"""
消息推送工具函数
用于在系统中发送 WebSocket 通知
"""
import logging
from typing import Optional
from app.websocket.manager import manager

logger = logging.getLogger(__name__)


async def notify_user(user_id: int, message_type: str, data: dict):
    """
    向指定用户发送通知

    Args:
        user_id: 用户ID
        message_type: 消息类型（如 'new_message', 'notification' 等）
        data: 消息数据
    """
    try:
        await manager.send_personal_message({
            "type": message_type,
            "data": data,
            "timestamp": int(__import__('time').time() * 1000)
        }, user_id)
        logger.info(f"通知已发送: user_id={user_id}, type={message_type}")
    except Exception as e:
        logger.error(f"发送通知失败: user_id={user_id}, error={e}")


async def notify_all(message_type: str, data: dict, exclude_user_id: Optional[int] = None):
    """
    向所有在线用户广播通知

    Args:
        message_type: 消息类型
        data: 消息数据
        exclude_user_id: 要排除的用户ID
    """
    try:
        await manager.broadcast_to_all({
            "type": message_type,
            "data": data,
            "timestamp": int(__import__('time').time() * 1000)
        }, exclude_user_id=exclude_user_id)
        logger.info(f"广播已发送: type={message_type}, exclude={exclude_user_id}")
    except Exception as e:
        logger.error(f"广播失败: error={e}")


async def notify_new_message(sender_id: int, receiver_id: int, message_data: dict):
    """
    发送新消息通知

    Args:
        sender_id: 发送者ID
        receiver_id: 接收者ID
        message_data: 消息数据
    """
    await notify_user(receiver_id, 'new_message', {
        'sender_id': sender_id,
        **message_data
    })


async def notify_system_notification(user_id: int, title: str, content: str, link: Optional[str] = None):
    """
    发送系统通知

    Args:
        user_id: 用户ID
        title: 通知标题
        content: 通知内容
        link: 相关链接
    """
    await notify_user(user_id, 'system_notification', {
        'title': title,
        'content': content,
        'link': link
    })


async def notify_comment_mentioned(user_id: int, comment_data: dict):
    """
    发送评论提及通知

    Args:
        user_id: 被提及的用户ID
        comment_data: 评论数据
    """
    await notify_user(user_id, 'comment_mentioned', comment_data)


async def notify_new_like(user_id: int, content_data: dict):
    """
    发送新点赞通知

    Args:
        user_id: 被点赞内容的作者ID
        content_data: 内容数据
    """
    await notify_user(user_id, 'new_like', content_data)


def get_websocket_stats():
    """
    获取 WebSocket 连接统计

    Returns:
        统计信息字典
    """
    import asyncio

    async def _get_stats():
        total = asyncio.create_task(manager.get_connection_count())
        users = manager.get_connected_users()
        await total
        return {
            'total_connections': total.result(),
            'connected_users': len(users),
            'user_ids': list(users)
        }

    try:
        # 在同步上下文中运行
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 如果事件循环正在运行，使用 create_task
            task = asyncio.create_task(_get_stats())
            return task
        else:
            # 如果没有运行的事件循环，运行新循环
            return asyncio.run(_get_stats())
    except (asyncio.Error, RuntimeError) as e:
        # 回退到同步方法
        logger.warning(f"获取WebSocket统计信息失败，回退到空数据: {e}")
        return {
            'total_connections': 0,
            'connected_users': 0,
            'user_ids': []
        }
