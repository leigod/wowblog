"""
管理后台评论相关数据模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base


class SensitiveWord(Base):
    """敏感词表"""
    __tablename__ = 'wb_sensitive_words'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    word = Column(String(100), nullable=False, comment='敏感词')
    type = Column(String(20), default='banned', comment='类型: banned(禁止)/review(需审核)/replace(替换)')
    replacement = Column(String(100), comment='替换内容')
    category = Column(String(50), comment='分类: politics/porn/adult/spam/other')
    status = Column(String(20), default='active', comment='状态: active/inactive')
    created_at = Column(Integer, default=0, comment='创建时间')
    created_by = Column(Integer, comment='创建人ID')
    
    __table_args__ = (
        Index('idx_word', 'word'),
        Index('idx_type', 'type'),
        Index('idx_status', 'status'),
    )


class Blacklist(Base):
    """黑名单表"""
    __tablename__ = 'wb_blacklist'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, comment='用户ID')
    type = Column(String(20), default='comment', comment='限制类型: comment/post/login')
    reason = Column(String(200), comment='拉黑原因')
    admin_id = Column(Integer, comment='操作管理员ID')
    note = Column(Text, comment='备注')
    expire_at = Column(Integer, comment='过期时间，NULL表示永久')
    status = Column(String(20), default='active', comment='状态: active/inactive')
    created_at = Column(Integer, default=0, comment='创建时间')
    updated_at = Column(Integer, default=0, comment='更新时间')
    
    __table_args__ = (
        Index('idx_user_id', 'user_id'),
        Index('idx_type', 'type'),
        Index('idx_status', 'status'),
    )


class CommentAuditLog(Base):
    """评论审核日志表"""
    __tablename__ = 'wb_comment_audit_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    comment_id = Column(Integer, nullable=False, comment='评论ID')
    action = Column(String(50), comment='操作: approved/rejected/hidden/deleted')
    from_status = Column(String(20), comment='原状态')
    to_status = Column(String(20), comment='新状态')
    admin_id = Column(Integer, comment='操作管理员ID')
    reason = Column(Text, comment='操作原因')
    created_at = Column(Integer, default=0, comment='创建时间')
    
    __table_args__ = (
        Index('idx_comment_id', 'comment_id'),
        Index('idx_admin_id', 'admin_id'),
    )


class SystemSetting(Base):
    """系统设置表"""
    __tablename__ = 'wb_system_settings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False, comment='设置键')
    value = Column(Text, comment='设置值')
    type = Column(String(20), default='string', comment='类型: string/boolean/number/json')
    description = Column(String(200), comment='描述')
    updated_at = Column(Integer, default=0, comment='更新时间')
    updated_by = Column(Integer, comment='更新人ID')
    
    __table_args__ = (
        Index('idx_key', 'key'),
    )
