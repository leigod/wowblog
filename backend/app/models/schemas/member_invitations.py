"""
成员邀请相关 Schema
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime


# ==================== 邀请管理 ====================

class InvitationCreate(BaseModel):
    """创建邀请"""
    email: EmailStr = Field(..., description='被邀请者邮箱')
    role: str = Field(..., description='邀请角色: Admin/Editor/Author/Contributor')
    language: str = Field(default='zh-CN', description='邮件语言')


class InvitationUpdate(BaseModel):
    """更新邀请"""
    status: Optional[str] = Field(None, description='状态: pending/accepted/cancelled/expired')


class InvitationListItem(BaseModel):
    """邀请列表项"""
    id: int
    email: str
    role: str
    status: str
    language: str
    created_at: int
    expires_at: int
    accepted_at: Optional[int] = None
    invited_by: int
    admin_name: Optional[str] = None
    blog_name: Optional[str] = None

    class Config:
        from_attributes = True


class InvitationListResponse(BaseModel):
    """邀请列表响应"""
    invitations: List[InvitationListItem]
    total: int
    page: int
    page_size: int


class InvitationVerifyResponse(BaseModel):
    """邀请验证响应"""
    valid: bool
    status: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    blog_name: Optional[str] = None
    admin_name: Optional[str] = None
    message: str


class InvitationAcceptRequest(BaseModel):
    """接受邀请请求"""
    token: str = Field(..., description='邀请令牌')


class InvitationAcceptResponse(BaseModel):
    """接受邀请响应"""
    success: bool
    message: str
    user_id: Optional[int] = None


# ==================== 邮件设置 ====================

class EmailSettings(BaseModel):
    """邮件设置"""
    id: int
    provider: str
    smtp_host: str
    smtp_port: int
    from_email: str
    from_name: Optional[str] = None
    use_tls: bool
    is_active: bool

    class Config:
        from_attributes = True


class EmailSettingsUpdate(BaseModel):
    """更新邮件设置"""
    provider: str
    smtp_host: str
    smtp_port: int = Field(default=587)
    smtp_user: Optional[str] = None
    smtp_pass: Optional[str] = None
    from_email: str
    from_name: Optional[str] = None
    use_tls: bool = Field(default=True)
    is_active: bool = Field(default=True)


# ==================== 角色权限描述 ====================

class RolePermissions(BaseModel):
    """角色权限描述"""
    role: str
    permissions_zh: str
    permissions_en: str
