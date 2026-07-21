"""
消息通知API路由
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.models.response import ApiResponse
from app.models.schemas.notifications import (
    NotificationListItem,
    SystemNotificationCreate
)
from app.dependencies.authentication import get_current_user, get_current_user_id
from app.utils.response import success
from app.crud import notifications as crud_notifications
from app.crud.users import get_user_by_id
from app.services import notification_service

router = APIRouter(prefix="/notifications", tags=["通知"])


@router.get("", response_model=ApiResponse[List[NotificationListItem]])
async def get_notifications(
    unread_only: bool = Query(False, description="只获取未读通知"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取通知列表"""
    notifications = await crud_notifications.get_notification_list(
        db,
        user_id=user_id,
        unread_only=unread_only,
        page=page,
        page_size=page_size
    )
    return success(data=notifications)


@router.get("/unread-count", response_model=ApiResponse[int])
async def get_unread_count(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取未读通知数量"""
    count = await crud_notifications.get_unread_count(db, user_id)
    return success(data=count)


@router.post("/{notification_id}/read", response_model=ApiResponse)
async def mark_notification_as_read(
    notification_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """标记单条通知为已读"""
    result = await crud_notifications.mark_as_read(db, notification_id, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="通知不存在")
    return success(msg="已标记为已读")


@router.post("/read-all", response_model=ApiResponse)
async def mark_all_notifications_as_read(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """标记所有通知为已读"""
    count = await crud_notifications.mark_all_as_read(db, user_id)
    return success(msg=f"已标记 {count} 条通知为已读")


@router.delete("/{notification_id}", response_model=ApiResponse)
async def delete_notification(
    notification_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """删除通知"""
    result = await crud_notifications.delete_notification(db, notification_id, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="通知不存在")
    return success(msg="通知已删除")


# 管理员路由：发送系统通知
@router.post("/admin/system", response_model=ApiResponse)
async def send_system_notification(
    notification: SystemNotificationCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """发送系统通知（仅管理员）"""
    # 检查是否是管理员
    if current_user.role != 'Admin':
        raise HTTPException(status_code=403, detail="无权限")

    from app.crud.users import get_all_users

    notifications = []

    if notification.target_users is None:
        # 全员通知
        users = await get_all_users(db)
        for user in users:
            notifications.append({
                'user_id': user.id,
                'type': 'system',
                'title': notification.title,
                'content': notification.content,
                'target_url': notification.content  # 简单处理，可以优化
            })
    else:
        # 指定用户通知
        for user_id in notification.target_users:
            notifications.append({
                'user_id': user_id,
                'type': 'system',
                'title': notification.title,
                'content': notification.content,
                'target_url': notification.content
            })

    if notifications:
        # 批量创建
        from app.models.schemas.notifications import NotificationCreate
        notification_creates = [NotificationCreate(**n) for n in notifications]
        await crud_notifications.create_notifications_batch(db, notification_creates)

    return success(msg=f"已发送 {len(notifications)} 条系统通知")
