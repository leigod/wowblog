"""
成员邀请 CRUD 操作
"""
import secrets
import hashlib
import time
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
import app.models.data.member_invitations as models
import app.models.data.users as user_models
from app.models.data.users import User


# 角色权限描述
ROLE_PERMISSIONS = {
    'Admin': {
        'zh-CN': '管理系统设置、发布文章、管理成员和评论',
        'en-US': 'manage system settings, publish articles, and manage members and comments'
    },
    'Editor': {
        'zh-CN': '发布和管理文章，管理分类标签',
        'en-US': 'publish and manage articles, manage categories and tags'
    },
    'Author': {
        'zh-CN': '创建和发布自己的文章',
        'en-US': 'create and publish own articles'
    },
    'Contributor': {
        'zh-CN': '创建草稿文章（需审核后发布）',
        'en-US': 'create draft articles (requires approval to publish)'
    }
}


def generate_token() -> str:
    """生成邀请令牌"""
    raw_token = secrets.token_urlsafe(32)
    return hashlib.sha256(raw_token.encode()).hexdigest()


def get_role_permissions(role: str, language: str = 'zh-CN') -> str:
    """获取角色权限描述"""
    if role in ROLE_PERMISSIONS:
        return ROLE_PERMISSIONS[role].get(language, ROLE_PERMISSIONS[role]['en-US'])
    return ''


async def check_existing_invitation(
    db: AsyncSession,
    email: str,
    role: str
) -> Optional[models.MemberInvitation]:
    """检查是否存在待处理的相同邀请"""
    result = await db.execute(
        select(models.MemberInvitation).where(
            and_(
                models.MemberInvitation.email == email,
                models.MemberInvitation.role == role,
                models.MemberInvitation.status == 'pending',
                models.MemberInvitation.expires_at > int(time.time())
            )
        )
    )
    return result.scalar_one_or_none()


async def check_user_exists(db: AsyncSession, email: str) -> Optional[User]:
    """检查用户是否已存在"""
    result = await db.execute(
        select(user_models.User).where(user_models.User.email == email)
    )
    return result.scalar_one_or_none()


async def create_invitation(
    db: AsyncSession,
    email: str,
    role: str,
    invited_by: int,
    blog_name: str,
    admin_name: str,
    language: str = 'zh-CN',
    expires_days: int = 7
) -> models.MemberInvitation:
    """创建邀请"""
    token = generate_token()
    expires_at = int(time.time()) + (expires_days * 24 * 60 * 60)

    invitation = models.MemberInvitation(
        token=token,
        email=email,
        role=role,
        invited_by=invited_by,
        blog_name=blog_name,
        admin_name=admin_name,
        language=language,
        expires_at=expires_at,
        status='pending'
    )

    db.add(invitation)
    await db.commit()
    await db.refresh(invitation)

    return invitation


async def get_invitation_by_token(db: AsyncSession, token: str) -> Optional[models.MemberInvitation]:
    """根据令牌获取邀请"""
    result = await db.execute(
        select(models.MemberInvitation).where(
            models.MemberInvitation.token == token
        )
    )
    return result.scalar_one_or_none()


async def get_invitation_by_id(db: AsyncSession, invitation_id: int) -> Optional[models.MemberInvitation]:
    """根据ID获取邀请"""
    result = await db.execute(
        select(models.MemberInvitation).where(
            models.MemberInvitation.id == invitation_id
        )
    )
    return result.scalar_one_or_none()


async def verify_invitation(db: AsyncSession, token: str) -> Tuple[bool, Optional[models.MemberInvitation], str]:
    """
    验证邀请令牌
    返回: (是否有效, 邀请对象, 消息)
    """
    invitation = await get_invitation_by_token(db, token)

    if not invitation:
        return False, None, '邀请不存在'

    current_time = int(time.time())

    if invitation.status == 'cancelled':
        return False, invitation, '邀请已失效'

    if invitation.status == 'accepted':
        return False, invitation, '您已加入团队'

    if invitation.status == 'expired':
        return False, invitation, '邀请已过期'

    if invitation.expires_at < current_time:
        # 更新状态为过期
        invitation.status = 'expired'
        await db.commit()
        return False, invitation, '邀请已过期'

    return True, invitation, '邀请有效'


async def accept_invitation(
    db: AsyncSession,
    token: str,
    user_id: int
) -> Tuple[bool, str]:
    """接受邀请"""
    invitation = await get_invitation_by_token(db, token)

    if not invitation:
        return False, '邀请不存在'

    if invitation.status != 'pending':
        return False, '邀请已被处理'

    # 更新用户角色
    result = await db.execute(
        select(user_models.User).where(user_models.User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        return False, '用户不存在'

    user.role = invitation.role
    invitation.status = 'accepted'
    invitation.accepted_at = int(time.time())

    await db.commit()
    return True, '成功加入团队'


async def get_invitation_list(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None
) -> Tuple[list, int]:
    """获取邀请列表"""
    query = select(models.MemberInvitation).order_by(
        models.MemberInvitation.created_at.desc()
    )

    if status:
        query = query.where(models.MemberInvitation.status == status)

    # 获取总数
    count_result = await db.execute(
        select(models.MemberInvitation.id).where(
            models.MemberInvitation.status == status if status else True
        )
    )
    total = len(count_result.all())

    # 分页
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    invitations = result.scalars().all()

    return list(invitations), total


async def cancel_invitation(db: AsyncSession, invitation_id: int) -> bool:
    """取消邀请"""
    invitation = await get_invitation_by_id(db, invitation_id)

    if not invitation or invitation.status != 'pending':
        return False

    invitation.status = 'cancelled'
    await db.commit()
    return True


async def get_pending_invitations_count(db: AsyncSession) -> int:
    """获取待处理邀请数量"""
    result = await db.execute(
        select(models.MemberInvitation.id).where(
            models.MemberInvitation.status == 'pending'
        )
    )
    return len(result.all())


# ==================== 邮件设置 CRUD ====================

async def get_active_email_settings(db: AsyncSession) -> Optional[models.EmailSettings]:
    """获取启用的邮件设置"""
    result = await db.execute(
        select(models.EmailSettings).where(
            models.EmailSettings.is_active == True
        )
    )
    return result.scalar_one_or_none()


async def get_all_email_settings(db: AsyncSession) -> list:
    """获取所有邮件设置"""
    result = await db.execute(
        select(models.EmailSettings)
    )
    return list(result.scalars().all())


async def update_email_settings(
    db: AsyncSession,
    settings_id: int,
    **kwargs
) -> Optional[models.EmailSettings]:
    """更新邮件设置"""
    result = await db.execute(
        select(models.EmailSettings).where(
            models.EmailSettings.id == settings_id
        )
    )
    settings = result.scalar_one_or_none()

    if not settings:
        return None

    for key, value in kwargs.items():
        if hasattr(settings, key):
            setattr(settings, key, value)

    await db.commit()
    await db.refresh(settings)
    return settings
