"""
管理员操作审计中间件

自动记录（零侵入业务代码）：
  1. /api/admin/* 下的写操作（POST/PUT/PATCH/DELETE）——Admin/Editor 的后台数据变更
  2. 登录/登出（/api/login、/api/auth/login、/api/auth/logout）

不记录页面浏览（GET），只记"改"——与云平台操作审计（阿里云 ActionTrail 等）惯例一致。

设计要点：
  - 请求体中的敏感字段（password/secret/token/private_key 等）脱敏为 ***
  - 登录失败也记录（detail 含尝试的用户名，是安全审计重点）
  - 日志写入失败只 warning 不抛出，绝不影响主请求
  - multipart 文件上传不存原始 body（存字节数说明），避免二进制乱码入库
"""
import json
import logging
import time
from typing import Any, Optional, Tuple

import jwt as pyjwt
from starlette.requests import Request
from sqlalchemy import select

from app.dependencies.authentication import SECRET_KEY, ALGORITHM
from app.database import AsyncSessionLocal
import app.models.data.users as models_users
import app.models.data.admin_log as models_admin_log

logger = logging.getLogger(__name__)

# 需要记录的认证端点 (path, method) -> action 名
_AUTH_ENDPOINTS = {
    ('/api/login', 'POST'): 'login',
    ('/api/auth/login', 'POST'): 'login',
    ('/api/auth/logout', 'POST'): 'logout',
}

_WRITE_METHODS = ('POST', 'PUT', 'PATCH', 'DELETE')

# 请求体中需要脱敏的字段名（小写比较）
_SENSITIVE_KEYS = {
    'password', 'old_password', 'new_password', 'confirm_password',
    'secret', 'client_secret', 'token', 'access_token', 'refresh_token',
    'private_key', 'authorization',
}


def _sanitize(obj: Any) -> Any:
    """递归脱敏：把敏感键的值替换为 ***。"""
    if isinstance(obj, dict):
        return {
            k: ('***' if str(k).lower() in _SENSITIVE_KEYS else _sanitize(v))
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [_sanitize(i) for i in obj]
    return obj


def _user_from_token(request: Request) -> Optional[str]:
    """从 Authorization Bearer token 解出 username（不验 DB，快速失败）。"""
    auth = request.headers.get('authorization', '')
    if not auth.lower().startswith('bearer '):
        return None
    try:
        payload = pyjwt.decode(auth[7:], SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get('sub')
    except Exception:
        return None


async def _record(request: Request, response, detail_raw: bytes, action: str) -> None:
    """写一条操作日志（独立 DB 会话；异常由调用方吞掉）。"""
    username = _user_from_token(request)

    # 解析请求体
    content_type = request.headers.get('content-type', '')
    body: Any = None
    if detail_raw:
        if 'multipart/form-data' in content_type or 'application/octet-stream' in content_type:
            # 文件上传等二进制 body 不入库（乱码无意义），只记说明
            body = {'_note': f'{content_type}, {len(detail_raw)} bytes'}
        else:
            try:
                body = json.loads(detail_raw)
            except Exception:
                body = {'_raw': detail_raw[:2000].decode('utf-8', 'ignore')}

    # 登录请求没有 token，从请求体取尝试的用户名（失败尝试也记录）
    if username is None and isinstance(body, dict) and body.get('username'):
        username = str(body['username'])

    user_id: Optional[int] = None
    role: Optional[str] = None
    async with AsyncSessionLocal() as session:
        if username:
            row = await session.execute(
                select(models_users.User).where(models_users.User.username == username)
            )
            user = row.scalar_one_or_none()
            if user:
                user_id, role = user.id, user.role
        session.add(models_admin_log.AdminLog(
            user_id=user_id,
            username=username,
            role=role,
            action=action,
            method=request.method.upper(),
            path=request.url.path,
            detail=json.dumps(_sanitize(body), ensure_ascii=False) if body is not None else None,
            status_code=response.status_code,
            ip=request.client.host if request.client else None,
            user_agent=(request.headers.get('user-agent') or '')[:500],
            createtime=int(time.time()),
        ))
        await session.commit()


async def admin_audit_middleware(request: Request, call_next):
    """判定 + 记录。不满足记录条件直接放行（零开销路径）。"""
    path = request.url.path
    method = request.method.upper()

    auth_action = _AUTH_ENDPOINTS.get((path, method))
    is_admin_write = path.startswith('/api/admin') and method in _WRITE_METHODS
    if not auth_action and not is_admin_write:
        return await call_next(request)

    # 预读 body（Starlette Request 会缓存 _body，后续路由仍可正常读取）
    detail_raw = await request.body()
    response = await call_next(request)

    action = auth_action or f'{method}:{path}'
    try:
        await _record(request, response, detail_raw, action)
    except Exception as e:
        # 审计写入失败绝不影响主请求
        logger.warning('admin audit log write failed (%s %s): %s', method, path, e)
    return response
