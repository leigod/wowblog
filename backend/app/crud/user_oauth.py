"""
用户OAuth绑定 CRUD 操作
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import Optional, List
import app.models.data.user_oauth as models
import app.models.data.users as models_users


async def get_oauth_by_provider(
    db: AsyncSession,
    provider: str,
    provider_user_id: str
) -> Optional[models.UserOAuth]:
    """根据提供商和用户ID获取OAuth绑定记录"""
    query = (
        select(models.UserOAuth)
        .where(
            and_(
                models.UserOAuth.provider == provider,
                models.UserOAuth.provider_user_id == provider_user_id
            )
        )
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_user_oauth_bindings(
    db: AsyncSession,
    user_id: int
) -> List[models.UserOAuth]:
    """获取用户的所有OAuth绑定"""
    query = (
        select(models.UserOAuth)
        .where(models.UserOAuth.user_id == user_id)
    )
    result = await db.execute(query)
    return result.scalars().all()


async def create_oauth_binding(
    db: AsyncSession,
    user_id: int,
    provider: str,
    provider_user_id: str,
    access_token: Optional[str] = None,
    refresh_token: Optional[str] = None,
    email: Optional[str] = None,
    avatar_url: Optional[str] = None,
    raw_data: Optional[dict] = None
) -> models.UserOAuth:
    """创建OAuth绑定记录"""
    oauth_binding = models.UserOAuth(
        user_id=user_id,
        provider=provider,
        provider_user_id=provider_user_id,
        access_token=access_token,
        refresh_token=refresh_token,
        email=email,
        avatar_url=avatar_url,
        raw_data=raw_data
    )
    db.add(oauth_binding)
    await db.flush()
    return oauth_binding


async def update_oauth_tokens(
    db: AsyncSession,
    oauth_id: int,
    access_token: Optional[str] = None,
    refresh_token: Optional[str] = None
) -> bool:
    """更新OAuth的access token和refresh token"""
    query = (
        select(models.UserOAuth)
        .where(models.UserOAuth.id == oauth_id)
    )
    result = await db.execute(query)
    oauth = result.scalar_one_or_none()

    if oauth:
        if access_token:
            oauth.access_token = access_token
        if refresh_token:
            oauth.refresh_token = refresh_token
        await db.flush()
        return True
    return False


async def delete_oauth_binding(
    db: AsyncSession,
    oauth_id: int,
    user_id: int
) -> bool:
    """删除OAuth绑定"""
    from sqlalchemy import delete

    query = (
        delete(models.UserOAuth)
        .where(
            and_(
                models.UserOAuth.id == oauth_id,
                models.UserOAuth.user_id == user_id
            )
        )
    )
    await db.execute(query)
    return True


async def unlink_provider_from_user(
    db: AsyncSession,
    user_id: int,
    provider: str
) -> bool:
    """解除用户与指定提供商的绑定"""
    from sqlalchemy import delete

    query = (
        delete(models.UserOAuth)
        .where(
            and_(
                models.UserOAuth.user_id == user_id,
                models.UserOAuth.provider == provider
            )
        )
    )
    result = await db.execute(query)
    return result.rowcount > 0
