from pydantic import BaseModel, Field
from pydantic.config import ConfigDict
from typing import Optional, Literal
from datetime import datetime


class NotificationBase(BaseModel):
    user_id: int
    type: Literal['comment', 'reply', 'article_mention', 'comment_mention', 'like', 'bookmark', 'system']
    title: str
    content: Optional[str] = None
    actor_id: Optional[int] = None
    actor_name: Optional[str] = None
    actor_avatar: Optional[str] = None
    target_type: Optional[str] = None
    target_id: Optional[int] = None
    target_title: Optional[str] = None
    target_url: Optional[str] = None


class NotificationCreate(NotificationBase):
    """创建通知"""
    pass


class NotificationUpdate(BaseModel):
    """更新通知"""
    is_read: bool = False


class Notification(BaseModel):
    """通知响应"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    type: str
    title: str
    content: Optional[str] = None
    actor_id: Optional[int] = None
    actor_name: Optional[str] = None
    actor_avatar: Optional[str] = None
    target_type: Optional[str] = None
    target_id: Optional[int] = None
    target_title: Optional[str] = None
    target_url: Optional[str] = None
    is_read: bool
    created_at: int


class NotificationListItem(BaseModel):
    """通知列表项"""
    id: int
    type: str
    title: str
    content: Optional[str] = None
    actor_id: Optional[int] = None
    actor_name: Optional[str] = None
    actor_avatar: Optional[str] = None
    target_url: Optional[str] = None
    is_read: bool
    created_at: int


class SystemNotificationCreate(BaseModel):
    """系统通知创建"""
    title: str
    content: str
    target_users: Optional[list[int]] = None  # None 表示全员通知
