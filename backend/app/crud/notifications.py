from sqlalchemy.orm import Session
import app.models.data.notifications as models
import app.models.schemas.notifications as schemas
from sqlalchemy import and_, select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import time


async def get_notification_list(
    db: AsyncSession,
    user_id: int,
    unread_only: bool = False,
    page: int = 1,
    page_size: int = 20,
) -> List[schemas.NotificationListItem]:
    """获取通知列表"""
    offset = (page - 1) * page_size

    conditions = [models.Notification.user_id == user_id]
    if unread_only:
        conditions.append(models.Notification.is_read == False)

    stmt = select(models.Notification).where(
        and_(*conditions)
    ).order_by(
        models.Notification.created_at.desc()
    ).offset(offset).limit(page_size)

    result = await db.execute(stmt)
    notifications = result.scalars().all()

    return [
        schemas.NotificationListItem(
            id=n.id,
            type=n.type,
            title=n.title,
            content=n.content,
            actor_id=n.actor_id,
            actor_name=n.actor_name,
            actor_avatar=n.actor_avatar,
            target_url=n.target_url,
            is_read=n.is_read,
            created_at=n.created_at,
        )
        for n in notifications
    ]


async def get_unread_count(db: AsyncSession, user_id: int) -> int:
    """获取未读通知数量"""
    stmt = select(func.count(models.Notification.id)).where(
        and_(
            models.Notification.user_id == user_id,
            models.Notification.is_read == False
        )
    )
    result = await db.execute(stmt)
    return result.scalar() or 0


async def mark_as_read(db: AsyncSession, notification_id: int, user_id: int) -> bool:
    """标记单条通知为已读"""
    stmt = update(models.Notification).where(
        and_(
            models.Notification.id == notification_id,
            models.Notification.user_id == user_id
        )
    ).values(is_read=True)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


async def mark_all_as_read(db: AsyncSession, user_id: int) -> int:
    """标记所有通知为已读"""
    stmt = update(models.Notification).where(
        and_(
            models.Notification.user_id == user_id,
            models.Notification.is_read == False
        )
    ).values(is_read=True)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount


async def create_notification(
    db: AsyncSession,
    notification: schemas.NotificationCreate
) -> models.Notification:
    """创建通知并推送"""
    # 保存到数据库
    notification_entity = models.Notification(**notification.model_dump())
    db.add(notification_entity)
    await db.commit()
    await db.refresh(notification_entity)

    # 通过消息推送服务实时推送
    try:
        from app.services.message_push_service import MessagePushService
        await MessagePushService.push_notification(
            db,
            notification.user_id,
            'notification',
            {
                'id': notification_entity.id,
                'type': notification_entity.type,
                'title': notification_entity.title,
                'content': notification_entity.content,
                'actor_id': notification_entity.actor_id,
                'actor_name': notification_entity.actor_name,
                'actor_avatar': notification_entity.actor_avatar,
                'target_url': notification_entity.target_url,
                'is_read': notification_entity.is_read,
                'created_at': notification_entity.created_at
            }
        )
    except Exception as e:
        # 推送失败不影响通知创建
        import logging
        logging.error(f"推送通知失败: {e}")

    return notification_entity


async def create_notifications_batch(
    db: AsyncSession,
    notifications: List[schemas.NotificationCreate]
) -> int:
    """批量创建通知"""
    for notification in notifications:
        notification_entity = models.Notification(**notification.model_dump())
        db.add(notification_entity)
    await db.commit()
    return len(notifications)


async def delete_old_notifications(
    db: AsyncSession,
    days: int = 30
) -> int:
    """删除旧通知（超过指定天数）"""
    cutoff_time = int(time.time()) - (days * 24 * 60 * 60)
    stmt = delete(models.Notification).where(
        models.Notification.created_at < cutoff_time
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount


async def delete_notification(
    db: AsyncSession,
    notification_id: int,
    user_id: int
) -> bool:
    """删除通知"""
    stmt = delete(models.Notification).where(
        and_(
            models.Notification.id == notification_id,
            models.Notification.user_id == user_id
        )
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0
