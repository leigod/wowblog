"""
前端用户认证路由
支持邮箱登录、注册、以及后续的OAuth社交登录
"""
from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel, EmailStr
from typing import Optional, Annotated
import os

from app.database import get_db
from app.models.response import ApiResponse
from app.utils.response import success, error
from app.utils.auth import get_password_hash, verify_password
from app.crud.users import get_user_in_db, create_user as crud_create_user
from app.crud.user_oauth import (
    get_oauth_by_provider,
    create_oauth_binding
)
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
        status='active',
        createtime=int(datetime.now().timestamp()),
        updatetime=int(datetime.now().timestamp())
    )

    db.add(new_user)
    await db.flush()

    # 创建用户统计数据
    from app.models.data.users import UserStatData
    user_stat = UserStatData(
        user_id=new_user.id,
        articles=0,
        comments=0,
        likes=0,
        followers=0,
        following=0
    )
    db.add(user_stat)
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

    if user.status == 'hidden':
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

from app.config.oauth import OAuthConfig
from app.utils.oauth_providers import GoogleOAuthProvider, GitHubOAuthProvider, AppleOAuthProvider

# OAuth 社交登录当前默认禁用：callback 把 access_token 拼进 URL 重定向存在泄露风险
# （浏览器历史 / Referer / 服务器日志），且尚未实现 httpOnly cookie 方案。
# 待 cookie 方案落地后，设环境变量 OAUTH_ENABLED=true 启用。
OAUTH_ENABLED = os.getenv("OAUTH_ENABLED", "false").lower() == "true"

# 允许的 OAuth 重定向地址前缀白名单（逗号分隔），防开放重定向；启用 OAuth 前必须配置
_OAUTH_REDIRECT_ALLOWED = [
    o.strip() for o in os.getenv("OAUTH_REDIRECT_ALLOWED", "").split(",") if o.strip()
]


def _is_allowed_redirect_uri(uri: Optional[str]) -> bool:
    """校验 redirect_uri 是否在白名单内"""
    if not uri:
        return False
    return any(uri.startswith(prefix) for prefix in _OAUTH_REDIRECT_ALLOWED)


def _safe_frontend_url(redirect_uri: Optional[str]) -> str:
    """返回安全的重定向地址：白名单内用传入值，否则回退默认登录页"""
    if redirect_uri and _is_allowed_redirect_uri(redirect_uri):
        return redirect_uri
    return f"{OAuthConfig.FRONTEND_URL}/login"


def get_oauth_provider(provider: str):
    """获取 OAuth provider 实例"""
    config = OAuthConfig()

    if provider == "google":
        return GoogleOAuthProvider(
            client_id=config.GOOGLE_CLIENT_ID,
            client_secret=config.GOOGLE_CLIENT_SECRET
        )
    elif provider == "github":
        return GitHubOAuthProvider(
            client_id=config.GITHUB_CLIENT_ID,
            client_secret=config.GITHUB_CLIENT_SECRET
        )
    elif provider == "apple":
        return AppleOAuthProvider(
            client_id=config.APPLE_CLIENT_ID,
            team_id=config.APPLE_TEAM_ID,
            key_id=config.APPLE_KEY_ID,
            private_key=config.APPLE_PRIVATE_KEY
        )
    else:
        return None


async def handle_oauth_user_login(
    db: AsyncSession,
    provider: str,
    provider_user_id: str,
    email: Optional[str],
    name: Optional[str],
    avatar_url: Optional[str]
):
    """
    处理 OAuth 用户登录/注册

    1. 检查是否已有该 OAuth 绑定
    2. 如果有，直接登录
    3. 如果没有，检查邮箱是否已注册
    4. 如果邮箱已注册，绑定账号并登录
    5. 如果邮箱未注册，创建新用户并登录
    """
    import secrets

    # 检查是否已有该 OAuth 绑定
    oauth_binding = await get_oauth_by_provider(db, provider, provider_user_id)

    if oauth_binding:
        # 已绑定，直接登录
        user_query = select(models_users.User).where(models_users.User.id == oauth_binding.user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()

        if user and user.status != 'hidden':
            return user

    # 检查邮箱是否已注册
    user = None
    if email:
        user = await get_user_by_email(db, email)

    if user:
        # 邮箱已注册，绑定 OAuth 账号
        await create_oauth_binding(
            db=db,
            user_id=user.id,
            provider=provider,
            provider_user_id=provider_user_id,
            avatar_url=avatar_url
        )
        await db.commit()
        return user
    else:
        # 创建新用户
        random_password = os.urandom(16).hex()  # 生成随机密码

        # 密码使用 bcrypt 哈希（OAuth 用户使用随机密码，salt 由 bcrypt 管理）
        hashed_password = get_password_hash(random_password)

        # 生成唯一用户名
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
            status='active',
            profile_image=avatar_url,
            createtime=int(datetime.now().timestamp()),
            updatetime=int(datetime.now().timestamp())
        )

        db.add(new_user)
        await db.flush()

        # 创建用户统计数据
        from app.models.data.users import UserStatData
        user_stat = UserStatData(
            user_id=new_user.id,
            articles=0,
            comments=0,
            likes=0,
            followers=0,
            following=0
        )
        db.add(user_stat)
        await db.flush()

        # 绑定 OAuth
        await create_oauth_binding(
            db=db,
            user_id=new_user.id,
            provider=provider,
            provider_user_id=provider_user_id,
            avatar_url=avatar_url
        )
        await db.commit()

        return new_user


@router.get("/auth/oauth/{provider}")
async def oauth_login(
    provider: str,
    redirect_uri: Optional[str] = None
):
    """
    OAuth社交登录授权跳转
    支持的provider: google, github, apple
    """
    if not OAUTH_ENABLED:
        raise HTTPException(status_code=503, detail="OAuth 登录暂未启用")

    provider_instance = get_oauth_provider(provider)

    if not provider_instance:
        return error(f'不支持的登录方式: {provider}')

    # 使用默认回调地址或前端传递的地址
    if not redirect_uri:
        redirect_uri = f"{OAuthConfig.BACKEND_URL}/auth/callback/{provider}"

    # 生成 state 并存储到 session（这里简化处理，直接返回）
    state = provider_instance.generate_state()

    # 返回授权 URL
    auth_url = provider_instance.get_auth_url(redirect_uri, state)

    return success(data={
        "auth_url": auth_url,
        "state": state
    })


@router.get("/auth/callback/{provider}")
async def oauth_callback(
    provider: str,
    code: str,
    state: Optional[str] = None,
    id_token: Optional[str] = None,  # Apple 特有
    redirect_uri: Optional[str] = None,  # 前端回调地址
    db: AsyncSession = Depends(get_db)
):
    """
    OAuth回调处理
    处理完成后重定向回前端页面
    """
    if not OAUTH_ENABLED:
        raise HTTPException(status_code=503, detail="OAuth 登录暂未启用")

    provider_instance = get_oauth_provider(provider)

    if not provider_instance:
        # 重定向回前端并带上错误信息
        frontend_url = _safe_frontend_url(redirect_uri)
        return RedirectResponse(
            url=f"{frontend_url}?error=unsupported_provider&error_description={provider}",
            status_code=302
        )

    try:
        # 获取 access token
        backend_redirect = f"{OAuthConfig.BACKEND_URL}/api/auth/callback/{provider}"

        # Apple 特殊处理 - 使用 id_token
        if provider == "apple" and id_token:
            user_info = await provider_instance.verify_id_token(id_token)
        else:
            access_token = await provider_instance.get_access_token(code, backend_redirect)
            user_info = await provider_instance.get_user_info(access_token)

        # 处理用户登录/注册
        user = await handle_oauth_user_login(
            db=db,
            provider=provider,
            provider_user_id=user_info.provider_user_id,
            email=user_info.email,
            name=user_info.name,
            avatar_url=user_info.avatar_url
        )

        if not user:
            frontend_url = _safe_frontend_url(redirect_uri)
            return RedirectResponse(
                url=f"{frontend_url}?error=login_failed&error_description=用户创建失败",
                status_code=302
            )

        # 生成访问令牌
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires
        )

        # TODO(安全): token 拼进 URL 会泄露到浏览器历史 / Referer / 服务器日志。
        # 启用 OAuth（OAUTH_ENABLED=true）前必须改为 httpOnly cookie 方案传递 token。
        frontend_url = _safe_frontend_url(redirect_uri)
        redirect_url = f"{frontend_url}?access_token={access_token}"

        return RedirectResponse(
            url=redirect_url,
            status_code=302
        )

    except Exception as e:
        import logging
        logging.error(f"OAuth callback error for {provider}: {str(e)}")
        frontend_url = _safe_frontend_url(redirect_uri)
        return RedirectResponse(
            url=f"{frontend_url}?error=oauth_error&error_description={str(e)}",
            status_code=302
        )
