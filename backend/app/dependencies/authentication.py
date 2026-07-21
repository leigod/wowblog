from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional
import os
import secrets
import logging

import jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
# JWTError 已在 PyJWT 2.x 中弃用，使用 InvalidTokenError 代替
try:
    from jwt.exceptions import JWTError
except ImportError:
    # PyJWT 2.x+ 不再有 JWTError，使用 InvalidTokenError
    JWTError = InvalidTokenError
from pydantic import BaseModel
from app.crud.users import get_user, get_user_in_db
import app.models.data.users as models
import app.models.schemas.users as schemas
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.auth import verify_password
from app.utils.roles import (
    Permission,
    has_permission,
    has_any_permission,
    has_all_permissions,
    is_admin_or_editor,
    is_admin_editor_or_author,
    is_content_creator,
    can_manage_role
)

# 配置日志
logger = logging.getLogger(__name__)

# JWT配置
# 从环境变量读取密钥，如果不存在则生成警告（开发环境可使用固定值，生产环境必须设置）
SECRET_KEY = os.getenv('JWT_SECRET_KEY')
if not SECRET_KEY:
    if os.getenv('ENVIRONMENT') == 'production':
        raise ValueError(
            "JWT_SECRET_KEY environment variable not set in production. "
            "Please set it in your .env file or environment."
        )
    else:
        # 开发环境生成临时随机密钥(每次启动变化,仅用于本地开发,不含任何固定值)
        SECRET_KEY = secrets.token_hex(32)
        logger.warning("未配置 JWT_SECRET_KEY,已生成临时开发密钥;生产环境必须设置该环境变量")

ALGORITHM = "HS256"

# Token有效期：30分钟（生产环境推荐）
# 从环境变量读取，默认30分钟
try:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))
except ValueError:
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 登录用户的token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

# 非登录用户的临时token（如注册、评论等场景）
temporary_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/get_temp_token", auto_error=False)


async def authenticate_user(username: str, password: str, db: AsyncSession = Depends(get_db)):
    user = await get_user_in_db(db, username=username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 只记录必要信息，不记录敏感token内容和完整payload
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            logger.warning("Token验证失败：缺少sub字段")
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except InvalidTokenError as e:
        logger.warning(f"Token解码失败: {str(e)}")
        raise credentials_exception
    user = await get_user(db, username=token_data.username)
    if user is None:
        logger.warning(f"用户查找失败: {token_data.username}")
        raise credentials_exception
    logger.info(f"用户验证成功: {user.username}")
    return user


# 获取当前登录用户的ID
async def get_current_user_id(token: Annotated[str, Depends(oauth2_scheme)], db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = await get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user.id


# 添加一个新的依赖函数，不会在未登录时抛出异常
async def get_optional_user_id(token: Optional[str] = Depends(oauth2_scheme),db: AsyncSession = Depends(get_db)):
    try:
        if token:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username:
                user = await get_user(db, username=username)
                if user:
                    return user.id
    except Exception:
        pass
    return None

async def get_current_active_user(
        current_user: Annotated[schemas.User, Depends(get_current_user)],
):
    if current_user.status == "hidden":
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_active_admin_user(
        current_user: Annotated[schemas.User, Depends(get_current_user)],
):
    if current_user.status == "hidden":
        raise HTTPException(status_code=400, detail="Inactive user")
    if current_user.role != "Admin":
        raise HTTPException(status_code=400, detail="您没有权限访问！")
    return current_user


# 生成临时token
def create_temporary_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=10)  # 临时token有效期较短
    to_encode.update({"exp": expire, "type": "temporary"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# 获取可选的用户（用于公开接口，不要求登录）
async def get_current_user_optional(token: Optional[str] = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        if token:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username:
                user = await get_user(db, username=username)
                if user:
                    return user
    except Exception:
        pass
    return None


# 获取可选的临时token用户（用于不需要登录但需要限流的接口）
async def get_optional_temporary_user(token: Optional[str] = Depends(temporary_oauth2_scheme)):
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "temporary":
            return None
        # 可以添加更多验证逻辑
        return {"token_id": payload.get("jti")}  # 返回一个标识
    except (InvalidTokenError, JWTError):
        # Token无效，返回None
        return None


# 获取临时token的依赖函数
def require_temporary_token(temp_user = Depends(get_optional_temporary_user)):
    if not temp_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="需要临时token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return temp_user


# ==================== 基于角色的权限检查 ====================

async def get_current_admin_user(
    current_user: Annotated[schemas.User, Depends(get_current_user)],
):
    """获取管理员用户（仅 Admin 可访问）"""
    if current_user.status == "hidden":
        raise HTTPException(status_code=403, detail="用户已被禁用")
    if current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="仅管理员可访问")
    return current_user


async def get_current_editor_user(
    current_user: Annotated[schemas.User, Depends(get_current_user)],
):
    """获取编辑用户（Admin 和 Editor 可访问）"""
    if current_user.status == "hidden":
        raise HTTPException(status_code=403, detail="用户已被禁用")
    if not is_admin_or_editor(current_user.role):
        raise HTTPException(status_code=403, detail="仅编辑和管理员可访问")
    return current_user


async def get_current_author_user(
    current_user: Annotated[schemas.User, Depends(get_current_user)],
):
    """获取作者用户（Admin、Editor 和 Author 可访问）"""
    if current_user.status == "hidden":
        raise HTTPException(status_code=403, detail="用户已被禁用")
    if not is_admin_editor_or_author(current_user.role):
        raise HTTPException(status_code=403, detail="仅作者、编辑和管理员可访问")
    return current_user


async def get_current_content_creator(
    current_user: Annotated[schemas.User, Depends(get_current_user)],
):
    """获取内容创建者（Admin、Editor、Author 和 Contributor 可访问）"""
    if current_user.status == "hidden":
        raise HTTPException(status_code=403, detail="用户已被禁用")
    if not is_content_creator(current_user.role):
        raise HTTPException(status_code=403, detail="仅内容创建者可访问")
    return current_user


async def require_permission(permission: Permission):
    """检查用户是否拥有指定权限的依赖工厂函数"""
    async def permission_check(current_user: Annotated[schemas.User, Depends(get_current_user)]) -> schemas.User:
        if current_user.status == "hidden":
            raise HTTPException(status_code=403, detail="用户已被禁用")
        if not has_permission(current_user.role, permission):
            raise HTTPException(status_code=403, detail=f"需要 {permission.value} 权限")
        return current_user
    return permission_check


async def require_any_permission(*permissions: Permission):
    """检查用户是否拥有任一指定权限的依赖工厂函数"""
    async def permission_check(current_user: Annotated[schemas.User, Depends(get_current_user)]) -> schemas.User:
        if current_user.status == "hidden":
            raise HTTPException(status_code=403, detail="用户已被禁用")
        if not has_any_permission(current_user.role, list(permissions)):
            perm_names = [p.value for p in permissions]
            raise HTTPException(status_code=403, detail=f"需要以下权限之一: {', '.join(perm_names)}")
        return current_user
    return permission_check


# 兼容旧版函数（保持向后兼容）
get_current_active_admin_user = get_current_admin_user
