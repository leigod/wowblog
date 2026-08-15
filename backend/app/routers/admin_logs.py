"""
管理员操作日志查询（审计中间件写入，此处只读）

挂载于 /api/admin 前缀下并要求 Admin 角色（见 main.py）。
注意：本模块自身的 GET 查询不会被审计中间件记录（只记写操作）。
"""
import json
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.authentication import get_current_active_admin_user
import app.models.data.admin_log as models


def success(msg: str = "操作成功", **kwargs):
    """统一成功响应（含分页等额外顶层字段）。

    与 admin_comments.py / member_invitations.py 的局部 success 同款：
    app.utils.response.success 只支持 msg/data，无法携带 total/page 等分页字段。
    返回裸 dict 且不挂 response_model（否则 extra 字段会被 pydantic 过滤掉）。
    """
    return {
        "code": 1,
        "msg": msg,
        **kwargs
    }


router = APIRouter(
    dependencies=[Depends(get_current_active_admin_user)],
    responses={404: {"description": "Not Found!"}},
)


@router.get('/logs/list')
async def list_admin_logs(
    page: int = 1,
    page_size: int = 20,
    username: Optional[str] = None,
    action: Optional[str] = None,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    查询管理员操作日志
    - username: 操作人（模糊）
    - action: 动作（模糊，如 login / POST:/api/admin/...）
    - start_time / end_time: 时间戳范围
    """
    conditions = []
    if username:
        conditions.append(models.AdminLog.username.like(f'%{username}%'))
    if action:
        conditions.append(models.AdminLog.action.like(f'%{action}%'))
    if start_time is not None:
        conditions.append(models.AdminLog.createtime >= start_time)
    if end_time is not None:
        conditions.append(models.AdminLog.createtime <= end_time)

    where = and_(*conditions) if conditions else None

    count_stmt = select(func.count()).select_from(models.AdminLog)
    list_stmt = select(models.AdminLog)
    if where is not None:
        count_stmt = count_stmt.where(where)
        list_stmt = list_stmt.where(where)

    total = (await db.execute(count_stmt)).scalar() or 0
    list_stmt = (
        list_stmt.order_by(models.AdminLog.createtime.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    rows = (await db.execute(list_stmt)).scalars().all()

    return success(
        data=[
            {
                'id': r.id,
                'user_id': r.user_id,
                'username': r.username,
                'role': r.role,
                'action': r.action,
                'method': r.method,
                'path': r.path,
                'detail': json.loads(r.detail) if r.detail else None,
                'status_code': r.status_code,
                'ip': r.ip,
                'user_agent': r.user_agent,
                'createtime': r.createtime,
            }
            for r in rows
        ],
        total=total,
        page=page,
        page_size=page_size,
    )
