"""
成员邀请数据模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.database import Base
import time


class MemberInvitation(Base):
    """成员邀请表"""
    __tablename__ = 'wb_member_invitations'

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(64), unique=True, nullable=False, index=True, comment='邀请令牌')
    email = Column(String(100), nullable=False, index=True, comment='被邀请者邮箱')
    role = Column(String(20), nullable=False, comment='邀请角色')
    invited_by = Column(Integer, nullable=False, index=True, comment='邀请人ID')
    blog_name = Column(String(100), default=None, comment='博客名称')
    admin_name = Column(String(50), default=None, comment='管理员名称')
    language = Column(String(10), default='zh-CN', comment='邮件语言')
    status = Column(String(20), default='pending', index=True, comment='邀请状态')
    expires_at = Column(Integer, nullable=False, comment='过期时间')
    created_at = Column(Integer, default=int(time.time()), comment='创建时间')
    updated_at = Column(Integer, default=int(time.time()), onupdate=int(time.time()), comment='更新时间')
    accepted_at = Column(Integer, default=None, comment='接受时间')


class EmailSettings(Base):
    """邮件设置表"""
    __tablename__ = 'wb_email_settings'

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(50), nullable=False, comment='邮件服务提供商')
    smtp_host = Column(String(255), nullable=False, comment='SMTP服务器')
    smtp_port = Column(Integer, default=587, comment='SMTP端口')
    smtp_user = Column(String(255), default=None, comment='SMTP用户名')
    smtp_pass = Column(String(255), default=None, comment='SMTP密码')
    from_email = Column(String(100), nullable=False, comment='发件人邮箱')
    from_name = Column(String(100), default=None, comment='发件人名称')
    use_tls = Column(Boolean, default=True, comment='使用TLS')
    is_active = Column(Boolean, default=True, comment='是否启用')
    created_at = Column(Integer, default=int(time.time()), comment='创建时间')
    updated_at = Column(Integer, default=int(time.time()), onupdate=int(time.time()), comment='更新时间')
