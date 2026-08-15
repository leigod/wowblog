"""
前端用户认证路由
支持邮箱登录、注册、以及后续的OAuth社交登录
"""
from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel, EmailStr
from typing import Optional, Annotated, List, Dict, Any
import os

from app.database import get_db
from app.models.response import ApiResponse
from app.utils.response import success, error
from app.utils.auth import get_password_hash, verify_password
from app.crud.users import get_user_in_db, create_user as crud_create_user
from app.crud.user_oauth import (
    get_oauth_by_provider,
    create_oauth_binding,
    get_user_oauth_bindings,
    unlink_provider_from_user
)
from app.crud.siteconfig import get_site_config
from app.dependencies.authentication import (
    create_access_token,
    get_current_user_id,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_temporary_token,
    require_temporary_token
)
from app.middleware import rate_limit_middleware
from datetime import timedelta, datetime
import app.models.data.users as models_users
import app.models.schemas.users as schemas_users

router = APIRouter()


# 速率限制依赖
async def rate_limit_login(request: Request):
    """登录速率限制：5次/分钟"""
    await rate_limit_middleware(request, "login")


async def rate_limit_register(request: Request):
    """注册速率限制：3次/5分钟"""
    await rate_limit_middleware(request, "register")


# ==================== Schema 定义 ====================

class FrontLoginRequest(BaseModel):
    """前端登录请求"""
    username: str  # 可以是邮箱或用户名
    password: str
    remember: Optional[bool] = False


class FrontRegisterRequest(BaseModel):
    """前端注册请求"""
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None


class TokenResponse(BaseModel):
    """Token响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # 过期时间（秒）


class UserInfoResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    profile_image: Optional[str] = None
    role: str
    status: str


# ==================== 辅助函数 ====================

async def get_user_by_email(db: AsyncSession, email: str):
    """根据邮箱获取用户"""
    query = select(models_users.User).where(models_users.User.email == email)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def authenticate_by_email_or_username(identifier: str, password: str, db: AsyncSession):
    """通过邮箱或用户名认证"""

    # 先尝试用户名
    user = await get_user_in_db(db, username=identifier)

    # 如果用户名不存在，尝试邮箱
    if not user:
        user = await get_user_by_email(db, email=identifier)

    if not user:
        return False

    if not verify_password(password, user.password):
        return False

    return user


async def create_new_user(
    db: AsyncSession,
    username: str,
    email: str,
    password: str,
    full_name: Optional[str] = None
) -> models_users.User:
    """创建新用户"""
    # 密码使用 bcrypt 哈希（salt 由 bcrypt 内部管理，user.salt 置空）
    hashed_password = get_password_hash(password)

    # 创建用户
    new_user = models_users.User(
        username=username,
        email=email,
        password=hashed_password,
        salt=None,
        full_name=full_name or username,
        role='User',
        status='normal',
        createtime=int(datetime.now().timestamp())
    )

    db.add(new_user)
    await db.flush()

    return new_user


# ==================== API 端点 ====================

@router.post("/auth/login", response_model=ApiResponse[TokenResponse])
async def front_login(
    request: FrontLoginRequest,
    req: Request,
    _rate_limit: None = Depends(rate_limit_login),
    db: AsyncSession = Depends(get_db)
):
    """
    前端用户登录
    支持邮箱或用户名登录
    """
    user = await authenticate_by_email_or_username(request.username, request.password, db)

    if not user:
        return error('用户名/邮箱或密码错误')

    if user.status == 'block':
        return error('账号已被禁用')

    # 生成访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    # 更新登录信息
    from app.crud.users import update_user_login_info
    await update_user_login_info(db, user.username, req)
    await db.commit()

    return success(data={
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    })


@router.post("/auth/register", response_model=ApiResponse[TokenResponse])
async def front_register(
    request: FrontRegisterRequest,
    req: Request,
    _rate_limit: None = Depends(rate_limit_register),
    temp_token=Depends(require_temporary_token),
    db: AsyncSession = Depends(get_db)
):
    """
    前端用户注册
    需要临时token（防止恶意注册）
    """
    # 检查用户名是否已存在
    existing_user = await get_user_in_db(db, username=request.username)
    if existing_user:
        return error('用户名已被使用')

    # 检查邮箱是否已存在
    existing_email = await get_user_by_email(db, email=request.email)
    if existing_email:
        return error('邮箱已被注册')

    # 创建新用户
    try:
        new_user = await create_new_user(
            db=db,
            username=request.username,
            email=request.email,
            password=request.password,
            full_name=request.full_name
        )

        # 生成访问令牌
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": new_user.username},
            expires_delta=access_token_expires
        )

        await db.commit()

        return success(data={
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }, msg='注册成功')

    except Exception as e:
        await db.rollback()
        return error(f'注册失败: {str(e)}')


@router.get("/auth/me", response_model=ApiResponse[UserInfoResponse])
async def get_current_user_info(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取当前登录用户信息"""
    query = select(models_users.User).where(models_users.User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        return error('用户不存在')

    return success(data={
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "profile_image": user.profile_image,
        "role": user.role,
        "status": user.status
    })


@router.post("/auth/logout", response_model=ApiResponse[dict])
async def front_logout():
    """
    前端用户登出
    实际上由前端删除token即可，这里主要用于记录日志等
    """
    return success(data={"logged_out": True}, msg='登出成功')


@router.get("/auth/temp-token", response_model=ApiResponse[dict])
async def get_temp_token_for_auth():
    """
    获取临时token
    用于注册等需要临时授权的操作
    """
    jti = os.urandom(16).hex()
    token = create_temporary_token({"jti": jti})
    return success(data={
        "access_token": token,
        "token_type": "bearer"
    })


# ==================== OAuth 社交登录端点 ====================
# 用 authlib 接管协议层（state/PKCE/nonce/id_token 验签），自家 token 复用 create_access_token。
# 回调不再把 access_token 拼进 URL，而是写入 httpOnly 短期 cookie，
# 前端通过 /auth/oauth/session 一次性取出后存入 localStorage（与普通登录一致）。

from app.config.oauth import OAuthConfig
from app.oauth.registry import get_oauth_client, SUPPORTED_PROVIDERS
from app.oauth.manual_providers import (
    MANUAL_PROVIDERS,
    issue_state,
    verify_state,
    build_manual_auth_url,
    fetch_manual_profile,
)
from urllib.parse import urlsplit, urlencode
import time
import logging

_oauth_logger = logging.getLogger(__name__)

# OAuth 总开关：回调已改为 httpOnly cookie 中转，消除 URL 泄露风险；
# 仍保留开关，部署侧未就绪（缺凭据/未建表）时可安全兜底。
OAUTH_ENABLED = os.getenv("OAUTH_ENABLED", "false").lower() == "true"

# OAuth 回跳前端地址白名单（逗号分隔），防开放重定向；启用 OAuth 前应配置
_OAUTH_REDIRECT_ALLOWED = [
    o.strip() for o in os.getenv("OAUTH_REDIRECT_ALLOWED", "").split(",") if o.strip()
]

# 是否生产环境（决定 cookie 的 Secure 标志）
_IS_OAUTH_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

# httpOnly 中转 cookie 的名字与存活时间
_OAUTH_TOKEN_COOKIE = "oauth_token"
_OAUTH_COOKIE_MAX_AGE = 60  # 秒，仅够前端发一次 session 请求


def _parse_redirect_key(uri: Optional[str]):
    """解析 URI 为 (scheme, host, port) 元组；非法（含端口不合法的 evil 子域）返回 None。"""
    if not uri:
        return None
    try:
        parsed = urlsplit(uri)
        # .port 在访问时才解析，对 "localhost:5173.evil.com" 这类会抛 ValueError
        port = parsed.port
    except ValueError:
        return None
    if not parsed.scheme or not parsed.hostname:
        return None
    return (parsed.scheme.lower(), parsed.hostname.lower(), port)


def _is_allowed_redirect_uri(uri: Optional[str]) -> bool:
    """
    校验 redirect_uri 是否在白名单内（严格比对 scheme+host+port）。

    旧实现用 str.startswith 会被同前缀子域绕过
    （如白名单 http://localhost:5173 命中 http://localhost:5173.evil.com），
    这里改为解析后精确比较，杜绝开放重定向。
    """
    target_key = _parse_redirect_key(uri)
    if target_key is None:
        return False
    return any(_parse_redirect_key(allowed) == target_key for allowed in _OAUTH_REDIRECT_ALLOWED)


def _safe_frontend_url(redirect_uri: Optional[str]) -> str:
    """返回安全的重定向地址：白名单内用传入值，否则回退默认登录页。"""
    if redirect_uri and _is_allowed_redirect_uri(redirect_uri):
        return redirect_uri
    return f"{OAuthConfig.FRONTEND_URL}/login"


def _build_frontend_callback(status: str, desc: str = "", redirect: Optional[str] = None) -> str:
    """
    构造回前端的 302 目标 URL。
    landing 固定为可信的前端登录页（由后端环境变量决定）；redirect 仅作 query 透传
    （前端自行 router.push），故后端侧不存在开放重定向风险。
    """
    landing = f"{OAuthConfig.FRONTEND_URL}/login"
    params: dict = {"oauth": status}
    if desc:
        params["desc"] = desc
    if redirect:
        params["redirect"] = redirect
    return f"{landing}?{urlencode(params)}"


def _build_bind_frontend_callback(status: str, desc: str = "") -> str:
    """构造主动绑定回前端的 302 目标（回个人资料编辑页）。"""
    landing = f"{OAuthConfig.FRONTEND_URL}/profile/edit"
    params: dict = {"oauth_bind": status}
    if desc:
        params["desc"] = desc
    return f"{landing}?{urlencode(params)}"


async def _is_provider_enabled(db: AsyncSession, provider: str) -> bool:
    """运营级开关：后台 oauth_enabled 总开关 + enabled_oauth_providers 列表共同决定。"""
    config = await get_site_config(db)
    if not config:
        return False
    return config.oauth_enabled == 1 and provider in (config.enabled_oauth_providers or [])


async def _execute_bind(db: AsyncSession, bind_user_id: Optional[int], provider: str, profile: dict) -> None:
    """
    执行主动绑定：会话校验 + 冲突检查 + 创建绑定。
    - 会话失效（无 bind_user_id）→ ValueError
    - 该第三方账号已绑别的用户 → ValueError
    - 已绑本用户 → 幂等（不重复创建）
    - 否则创建绑定。供 oauth_callback 的 bind 分支调用。
    """
    if not bind_user_id:
        raise ValueError("绑定会话已失效，请重新发起绑定")
    existing = await get_oauth_by_provider(db, provider, profile["provider_user_id"])
    if existing and existing.user_id != bind_user_id:
        raise ValueError("该第三方账号已绑定其他用户")
    if not existing:
        await create_oauth_binding(
            db=db, user_id=bind_user_id, provider=provider,
            provider_user_id=profile["provider_user_id"], email=profile["email"],
            avatar_url=profile["avatar_url"], access_token=profile["access_token"],
            refresh_token=profile["refresh_token"], raw_data=profile["raw_data"],
        )
        await db.commit()


async def handle_oauth_user_login(
    db: AsyncSession,
    provider: str,
    provider_user_id: str,
    email: Optional[str],
    name: Optional[str],
    avatar_url: Optional[str],
    access_token: Optional[str] = None,
    refresh_token: Optional[str] = None,
    raw_data: Optional[dict] = None,
):
    """
    处理 OAuth 用户登录/注册：
    1. 已有该 OAuth 绑定 → 直接登录
    2. 邮箱已注册 → 补绑 OAuth 并登录
    3. 都没有 → 创建新用户并绑定

    access_token/refresh_token/raw_data 持久化进 wb_user_oauth（旧实现丢弃了这些）。
    """
    # 1. 检查是否已有该 OAuth 绑定
    oauth_binding = await get_oauth_by_provider(db, provider, provider_user_id)

    if oauth_binding:
        user_query = select(models_users.User).where(models_users.User.id == oauth_binding.user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()
        if user and user.status != 'block':
            return user

    # 2. 检查邮箱是否已注册
    user = None
    if email:
        user = await get_user_by_email(db, email)

    if user:
        # 邮箱已注册，补绑 OAuth 账号（并持久化 provider token）
        await create_oauth_binding(
            db=db,
            user_id=user.id,
            provider=provider,
            provider_user_id=provider_user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            email=email,
            avatar_url=avatar_url,
            raw_data=raw_data,
        )
        await db.commit()
        return user

    # 3. 创建新用户（随机密码，OAuth 用户不会用密码登录）
    random_password = os.urandom(16).hex()
    hashed_password = get_password_hash(random_password)

    base_username = f"{provider}_{provider_user_id[:8]}"
    username = base_username
    counter = 1
    while await get_user_in_db(db, username=username):
        username = f"{base_username}{counter}"
        counter += 1

    new_user = models_users.User(
        username=username,
        email=email,
        password=hashed_password,
        salt=None,
        full_name=name or username,
        role='User',
        status='normal',
        profile_image=avatar_url,
        createtime=int(datetime.now().timestamp()),
    )

    db.add(new_user)
    await db.flush()

    # 绑定 OAuth（持久化 provider token）
    await create_oauth_binding(
        db=db,
        user_id=new_user.id,
        provider=provider,
        provider_user_id=provider_user_id,
        access_token=access_token,
        refresh_token=refresh_token,
        email=email,
        avatar_url=avatar_url,
        raw_data=raw_data,
    )
    await db.commit()

    return new_user


async def _extract_oauth_profile(provider: str, token: dict) -> dict:
    """
    从 authlib 返回的 token dict 提取统一 profile 与 provider token。
    - google/apple（OIDC）：userinfo 已由 authlib 验签，直接取
    - github（非 OIDC）：用 access_token 调 /user（及 /user/emails）取资料
    """
    access_token = token.get("access_token")
    refresh_token = token.get("refresh_token")

    if provider in ("google", "apple"):
        userinfo = token.get("userinfo") or {}
        return {
            "provider_user_id": str(userinfo.get("sub") or ""),
            "email": userinfo.get("email"),
            "name": userinfo.get("name"),
            "avatar_url": userinfo.get("picture"),
            "access_token": access_token,
            "refresh_token": refresh_token,
            "raw_data": userinfo,
        }

    if provider == "github":
        client = get_oauth_client("github")
        profile_resp = await client.get("user", token=token)
        profile = profile_resp.json()
        email = profile.get("email")
        # GitHub 用户常隐藏公开邮箱，需单独取主邮箱
        if not email:
            emails_resp = await client.get("user/emails", token=token)
            for item in emails_resp.json():
                if item.get("primary"):
                    email = item.get("email")
                    break
        return {
            "provider_user_id": str(profile.get("id") or ""),
            "email": email,
            "name": profile.get("name") or profile.get("login"),
            "avatar_url": profile.get("avatar_url"),
            "access_token": access_token,
            "refresh_token": refresh_token,
            "raw_data": profile,
        }

    if provider == "gitee":
        client = get_oauth_client("gitee")
        profile_resp = await client.get("user", token=token)
        profile = profile_resp.json()
        # Gitee /api/v5/user 返回 {id, login, name, avatar_url, email, ...}
        return {
            "provider_user_id": str(profile.get("id") or ""),
            "email": profile.get("email"),
            "name": profile.get("name") or profile.get("login"),
            "avatar_url": profile.get("avatar_url"),
            "access_token": access_token,
            "refresh_token": refresh_token,
            "raw_data": profile,
        }

    raise ValueError(f"不支持的 provider: {provider}")


@router.get("/auth/oauth/session")
async def oauth_session(request: Request):
    """
    一次性取出 OAuth 回调写入的 httpOnly cookie 中的 access_token。
    取出后立即删除 cookie；前端拿到后存入 localStorage，走与普通登录一致的后续流程。
    注意：此固定路径必须在 /auth/oauth/{provider} 之前声明，否则会被 {provider} 吞掉。
    """
    token = request.cookies.get(_OAUTH_TOKEN_COOKIE)
    if not token:
        return JSONResponse(
            {"code": 0, "msg": "OAuth 会话不存在或已过期", "time": int(time.time()), "data": []},
            status_code=401,
        )
    response = JSONResponse({
        "code": 1,
        "msg": "ok",
        "time": int(time.time()),
        "data": {"access_token": token, "token_type": "bearer"},
    })
    response.delete_cookie(_OAUTH_TOKEN_COOKIE, path="/api/auth")
    return response


@router.get("/auth/oauth/bindings", response_model=ApiResponse[List[Dict[str, Any]]])
async def list_oauth_bindings(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """列出当前登录用户已绑定的第三方账号（不含敏感字段）。"""
    bindings = await get_user_oauth_bindings(db, user_id)
    return success(data=[
        {
            "provider": b.provider,
            "email": b.email,
            "avatar_url": b.avatar_url,
            "createtime": b.createtime,
        }
        for b in bindings
    ])


@router.delete("/auth/oauth/bindings/{provider}", response_model=ApiResponse[dict])
async def unlink_oauth_binding(
    provider: str,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """解除当前用户与指定第三方账号的绑定。"""
    if provider not in SUPPORTED_PROVIDERS:
        return error(f"不支持的登录方式: {provider}")
    ok = await unlink_provider_from_user(db, user_id, provider)
    await db.commit()
    if not ok:
        return error(f"未绑定该账号或解绑失败: {provider}")
    return success(data={"unlinked": True}, msg="解绑成功")


@router.get("/auth/oauth/{provider}")
async def oauth_login(provider: str, request: Request, redirect: Optional[str] = None,
                      db: AsyncSession = Depends(get_db)):
    """
    OAuth 社交登录授权跳转（未登录用户用）。
    - google/github/gitee/apple：走 authlib；wechat/qq：手撸授权 URL。
    """
    if not OAUTH_ENABLED:
        raise HTTPException(status_code=503, detail="OAuth 登录暂未启用")
    if not await _is_provider_enabled(db, provider):
        return RedirectResponse(
            url=_build_frontend_callback("error", desc=f"该登录方式未启用: {provider}", redirect=redirect or None),
            status_code=302,
        )

    request.session["oauth_login_redirect"] = redirect or ""
    request.session["oauth_intent"] = "login"
    redirect_uri = f"{OAuthConfig.BACKEND_URL}/auth/callback/{provider}"

    if provider in SUPPORTED_PROVIDERS:
        client = get_oauth_client(provider)
        if client is None:
            return error(f"未配置该登录方式的凭据: {provider}")
        return await client.authorize_redirect(request, redirect_uri)

    if provider in MANUAL_PROVIDERS:
        state = issue_state(request, provider)
        auth_url = build_manual_auth_url(provider, redirect_uri, state)
        return RedirectResponse(url=auth_url, status_code=302)

    return error(f"不支持的登录方式: {provider}")


@router.post("/auth/oauth/bind/{provider}")
async def oauth_bind_initiate(
    provider: str,
    request: Request,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    主动绑定发起（已登录用户用）。
    window.location 跳转不带 Authorization header，故拆两步：前端先调本端点（axios 带
    token）验证身份并写 session 意图，返回授权 URL；前端再 window.location 跳该 URL。
    平台回调由 oauth_callback 按 session 里的 oauth_intent=bind 走绑定分支。
    """
    if not OAUTH_ENABLED:
        raise HTTPException(status_code=503, detail="OAuth 登录暂未启用")
    if not await _is_provider_enabled(db, provider):
        return error(f"该登录方式未启用: {provider}")
    if provider not in SUPPORTED_PROVIDERS and provider not in MANUAL_PROVIDERS:
        return error(f"不支持的登录方式: {provider}")

    request.session["oauth_intent"] = "bind"
    request.session["oauth_bind_user_id"] = user_id
    redirect_uri = f"{OAuthConfig.BACKEND_URL}/auth/callback/{provider}"

    if provider in SUPPORTED_PROVIDERS:
        client = get_oauth_client(provider)
        if client is None:
            return error(f"未配置该登录方式的凭据: {provider}")
        # 用 authlib 底层方法生成授权 URL + 存 state，不直接 302（要把 URL 交给前端跳）
        rv = await client.create_authorization_url(redirect_uri)
        await client.save_authorize_data(request, redirect_uri=redirect_uri, **rv)
        return success(data={"authorize_url": rv["url"]})

    # manual provider（wechat/qq）
    state = issue_state(request, provider)
    auth_url = build_manual_auth_url(provider, redirect_uri, state)
    return success(data={"authorize_url": auth_url})


# 拆成 GET/POST 两个入口调用同一实现：api_route 合并注册会导致 OpenAPI
# 出现重复 operation ID（oauth_callback 警告），拆分后各自有独立函数名
@router.get("/auth/callback/{provider}")
async def oauth_callback_get(provider: str, request: Request, db: AsyncSession = Depends(get_db)):
    """OAuth 回调（GET 通用入口）"""
    return await _oauth_callback_impl(provider, request, db)


@router.post("/auth/callback/{provider}")
async def oauth_callback_post(provider: str, request: Request, db: AsyncSession = Depends(get_db)):
    """OAuth 回调（POST 兼容 Apple form_post）"""
    return await _oauth_callback_impl(provider, request, db)


async def _oauth_callback_impl(provider: str, request: Request, db: AsyncSession = Depends(get_db)):
    """
    OAuth 回调处理（GET 通用，POST 兼容 Apple form_post）。
    按 session 中的 oauth_intent 分流：login（创建/匹配用户 + 发 token）或
    bind（关联到当前已登录用户，不发 token）。
    """
    if not OAUTH_ENABLED:
        raise HTTPException(status_code=503, detail="OAuth 登录暂未启用")

    intent = request.session.pop("oauth_intent", "login")
    bind_user_id = request.session.pop("oauth_bind_user_id", None) if intent == "bind" else None
    final_redirect = request.session.pop("oauth_login_redirect", "") or None

    try:
        if not await _is_provider_enabled(db, provider):
            raise ValueError(f"该登录方式未启用: {provider}")

        # 提取 profile（authlib 自动验 state/id_token；manual 手动验 state）
        if provider in SUPPORTED_PROVIDERS:
            client = get_oauth_client(provider)
            if client is None:
                raise ValueError(f"未配置该登录方式的凭据: {provider}")
            token = await client.authorize_access_token(request)
            profile = await _extract_oauth_profile(provider, token)
        elif provider in MANUAL_PROVIDERS:
            code = request.query_params.get("code")
            state = request.query_params.get("state")
            if not code or not verify_state(request, state):
                raise ValueError("授权参数缺失或 state 校验失败")
            redirect_uri = f"{OAuthConfig.BACKEND_URL}/auth/callback/{provider}"
            profile = await fetch_manual_profile(provider, code, redirect_uri)
        else:
            raise ValueError(f"不支持的登录方式: {provider}")

        if not profile["provider_user_id"]:
            raise ValueError("未能从第三方获取用户标识")

        # ===== 主动绑定分支 =====
        if intent == "bind":
            await _execute_bind(db, bind_user_id, provider, profile)
            # 绑定不发新 token（用户已登录），回个人资料编辑页
            return RedirectResponse(url=_build_bind_frontend_callback("success"), status_code=302)

        # ===== 登录分支（原有逻辑） =====
        user = await handle_oauth_user_login(db=db, provider=provider, **profile)
        if not user:
            return RedirectResponse(
                url=_build_frontend_callback("error", desc="用户创建失败", redirect=final_redirect),
                status_code=302,
            )

        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        response = RedirectResponse(
            url=_build_frontend_callback("success", redirect=final_redirect),
            status_code=302,
        )
        response.set_cookie(
            _OAUTH_TOKEN_COOKIE, access_token,
            max_age=_OAUTH_COOKIE_MAX_AGE, httponly=True,
            secure=_IS_OAUTH_PRODUCTION, samesite="lax", path="/api/auth",
        )
        return response

    except Exception as e:
        _oauth_logger.warning("OAuth callback error for %s (intent=%s): %s", provider, intent, e)
        if intent == "bind":
            return RedirectResponse(
                url=_build_bind_frontend_callback("error", desc=str(e) or "绑定失败"),
                status_code=302,
            )
        desc = (
            request.query_params.get("error_description")
            or request.query_params.get("error")
            or str(e)
            or "授权失败或已取消"
        )
        return RedirectResponse(
            url=_build_frontend_callback("error", desc=desc, redirect=final_redirect),
            status_code=302,
        )