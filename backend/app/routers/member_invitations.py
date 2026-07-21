"""
成员邀请 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import os

from app.database import get_db
from app.dependencies.authentication import get_current_user, get_current_user_optional
from app.models.data.users import User
import app.crud.member_invitations as crud
import app.crud.siteconfig as crud_siteconfig
import app.models.schemas.member_invitations as schemas
from app.services.email_service import (
    EmailConfig,
    send_invitation_email,
    SMTP_PRESETS
)

router = APIRouter(prefix='/member-invitations', tags=['成员邀请'])


def success(msg: str = "操作成功", **kwargs):
    """统一成功响应"""
    return {
        "code": 1,
        "msg": msg,
        **kwargs
    }


def error(msg: str = "操作失败", code: int = 0):
    """统一错误响应"""
    return {
        "code": code,
        "msg": msg
    }


# ==================== 邀请管理 ====================

@router.post('/admin/invite')
async def create_invitation(
    invitation_data: schemas.InvitationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    创建邀请并发送邮件

    权限: Admin
    """
    # 检查权限
    if current_user.role != 'Admin':
        raise HTTPException(status_code=403, detail='仅管理员可邀请成员')

    # 检查是否存在待处理的相同邀请
    existing = await crud.check_existing_invitation(
        db=db,
        email=invitation_data.email,
        role=invitation_data.role
    )
    if existing:
        raise HTTPException(status_code=400, detail='该用户已被邀请此角色，请勿重复邀请')

    # 获取系统配置中的博客名称
    site_config = await crud_siteconfig.get_site_config(db)
    blog_name = site_config.site_title if site_config else 'My Blog'

    # 创建邀请
    invitation = await crud.create_invitation(
        db=db,
        email=invitation_data.email,
        role=invitation_data.role,
        invited_by=current_user.id,
        blog_name=blog_name,
        admin_name=current_user.full_name or current_user.username,
        language=invitation_data.language
    )

    # 获取邮件配置
    email_settings = await crud.get_active_email_settings(db)
    if not email_settings:
        # 邮件未配置，返回邀请创建成功但未发送邮件
        return success(
            msg='邀请已创建（邮件服务未配置，未发送邮件）',
            invitation_id=invitation.id,
            email_sent=False
        )

    # 构建接受链接
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
    accept_url = f"{frontend_url}/invite/accept/{invitation.token}"

    # 获取角色权限描述
    permissions = crud.get_role_permissions(
        role=invitation_data.role,
        language=invitation_data.language
    )

    # 发送邮件
    email_config = EmailConfig(
        smtp_host=email_settings.smtp_host,
        smtp_port=email_settings.smtp_port,
        smtp_user=email_settings.smtp_user,
        smtp_pass=email_settings.smtp_pass,
        from_email=email_settings.from_email,
        from_name=email_settings.from_name,
        use_tls=email_settings.use_tls
    )

    email_sent, error_msg = send_invitation_email(
        email_config=email_config,
        to_email=invitation_data.email,
        blog_name=invitation.blog_name,
        admin_name=invitation.admin_name,
        role=invitation_data.role,
        permissions=permissions,
        accept_url=accept_url,
        language=invitation_data.language
    )

    if not email_sent:
        raise HTTPException(status_code=500, detail=f'邮件发送失败：{error_msg}')

    return success(
        msg='邀请已创建并发送邮件',
        invitation_id=invitation.id,
        email_sent=True
    )


@router.get('/admin/list')
async def get_invitation_list(
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取邀请列表

    权限: Admin
    """
    if current_user.role != 'Admin':
        raise HTTPException(status_code=403, detail='仅管理员可访问')

    invitations, total = await crud.get_invitation_list(
        db=db,
        page=page,
        page_size=page_size,
        status=status
    )

    return success(
        msg='获取成功',
        invitations=[{
            'id': inv.id,
            'email': inv.email,
            'role': inv.role,
            'status': inv.status,
            'language': inv.language,
            'created_at': inv.created_at,
            'expires_at': inv.expires_at,
            'accepted_at': inv.accepted_at,
            'invited_by': inv.invited_by,
            'admin_name': inv.admin_name,
            'blog_name': inv.blog_name,
        } for inv in invitations],
        total=total,
        page=page,
        page_size=page_size
    )


@router.post('/admin/{invitation_id}/resend')
async def resend_invitation_email(
    invitation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    重新发送邀请邮件

    权限: Admin
    """
    if current_user.role != 'Admin':
        raise HTTPException(status_code=403, detail='仅管理员可操作')

    invitation = await crud.get_invitation_by_id(db, invitation_id)
    if not invitation:
        raise HTTPException(status_code=404, detail='邀请不存在')

    if invitation.status != 'pending':
        raise HTTPException(status_code=400, detail='只能重新发送待处理的邀请')

    # 获取邮件配置
    email_settings = await crud.get_active_email_settings(db)
    if not email_settings:
        raise HTTPException(status_code=400, detail='请先配置邮件服务')

    # 构建接受链接
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
    accept_url = f"{frontend_url}/invite/accept/{invitation.token}"

    # 获取角色权限描述
    permissions = crud.get_role_permissions(
        role=invitation.role,
        language=invitation.language
    )

    # 发送邮件
    email_config = EmailConfig(
        smtp_host=email_settings.smtp_host,
        smtp_port=email_settings.smtp_port,
        smtp_user=email_settings.smtp_user,
        smtp_pass=email_settings.smtp_pass,
        from_email=email_settings.from_email,
        from_name=email_settings.from_name,
        use_tls=email_settings.use_tls
    )

    email_sent, error_msg = send_invitation_email(
        email_config=email_config,
        to_email=invitation.email,
        blog_name=invitation.blog_name,
        admin_name=invitation.admin_name,
        role=invitation.role,
        permissions=permissions,
        accept_url=accept_url,
        language=invitation.language
    )

    if not email_sent:
        raise HTTPException(status_code=500, detail=f'邮件发送失败：{error_msg}')

    return success(msg='邮件已重新发送')


@router.post('/admin/{invitation_id}/cancel')
async def cancel_invitation(
    invitation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    取消邀请

    权限: Admin
    """
    if current_user.role != 'Admin':
        raise HTTPException(status_code=403, detail='仅管理员可操作')

    cancelled = await crud.cancel_invitation(db, invitation_id)
    if not cancelled:
        raise HTTPException(status_code=400, detail='邀请不存在或已被处理')

    return success(msg='邀请已取消')


@router.get('/pending-count')
async def get_pending_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取待处理邀请数量"""
    if current_user.role != 'Admin':
        raise HTTPException(status_code=403, detail='仅管理员可访问')

    count = await crud.get_pending_invitations_count(db)
    return success(data={'count': count})


# ==================== 公开接口 ====================

@router.get('/verify/{token}')
async def verify_invitation(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """
    验证邀请令牌（公开接口）
    """
    is_valid, invitation, message = await crud.verify_invitation(db, token)

    response_data = {
        'valid': is_valid,
        'message': message
    }

    if is_valid and invitation:
        response_data.update({
            'email': invitation.email,
            'role': invitation.role,
            'blog_name': invitation.blog_name,
            'admin_name': invitation.admin_name
        })

    return response_data


@router.post('/accept/{token}')
async def accept_invitation(
    token: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    接受邀请（需要登录）

    注意: 如果用户未登录，需要先登录后再调用此接口
    """
    if not current_user:
        raise HTTPException(status_code=401, detail='请先登录')

    # 验证邀请
    is_valid, invitation, message = await crud.verify_invitation(db, token)
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)

    # 检查邮箱是否匹配
    if current_user.email != invitation.email:
        raise HTTPException(status_code=400, detail='此邀请不是发给您的')

    # 接受邀请
    success, message = await crud.accept_invitation(db, token, current_user.id)
    if not success:
        raise HTTPException(status_code=400, detail=message)

    return success(msg='恭喜您已成功加入团队！')


# ==================== 邮件设置 ====================

@router.get('/admin/email-settings')
async def get_email_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取邮件设置列表"""
    if current_user.role != 'Admin':
        raise HTTPException(status_code=403, detail='仅管理员可访问')

    settings = await crud.get_all_email_settings(db)

    return success(
        data=[{
            'id': s.id,
            'provider': s.provider,
            'smtp_host': s.smtp_host,
            'smtp_port': s.smtp_port,
            'smtp_user': s.smtp_user,  # 添加SMTP用户名
            'from_email': s.from_email,
            'from_name': s.from_name,
            'use_tls': s.use_tls,
            'is_active': s.is_active,
            'has_password': bool(s.smtp_pass)
        } for s in settings]
    )


@router.post('/admin/email-settings/{settings_id}/update')
async def update_email_settings(
    settings_id: int,
    data: schemas.EmailSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新邮件设置"""
    if current_user.role != 'Admin':
        raise HTTPException(status_code=403, detail='仅管理员可操作')

    settings = await crud.update_email_settings(
        db=db,
        settings_id=settings_id,
        **data.model_dump(exclude_none=True)
    )

    if not settings:
        raise HTTPException(status_code=404, detail='邮件设置不存在')

    return success(msg='邮件设置已更新')


@router.get('/admin/smtp-presets')
async def get_smtp_presets(
    current_user: User = Depends(get_current_user),
):
    """获取 SMTP 预设配置"""
    if current_user.role != 'Admin':
        raise HTTPException(status_code=403, detail='仅管理员可访问')

    return success(data=list(SMTP_PRESETS.keys()))
