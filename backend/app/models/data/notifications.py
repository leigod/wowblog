from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Index
from app.database import Base
import time


class Notification(Base):
    __tablename__ = 'wb_notifications'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True, comment='接收用户ID')
    type = Column(String(20), nullable=False, comment='通知类型')
    title = Column(String(200), nullable=False, comment='通知标题')
    content = Column(Text, comment='通知内容摘要')
    actor_id = Column(Integer, comment='触发者用户ID')
    actor_name = Column(String(50), comment='触发者用户名')
    actor_avatar = Column(String(500), comment='触发者头像')
    target_type = Column(String(20), comment='关联对象类型')
    target_id = Column(Integer, comment='关联对象ID')
    target_title = Column(String(200), comment='关联对象标题')
    target_url = Column(String(500), comment='关联对象URL')
    is_read = Column(Boolean, default=False, comment='是否已读')
    created_at = Column(Integer, default=lambda: int(time.time()), comment='创建时间')

    __table_args__ = (
        Index('idx_user_read', 'user_id', 'is_read', 'created_at'),
        Index('idx_created', 'created_at'),
    )
