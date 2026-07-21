"""
消息推送服务 - 根据系统配置选择 WebSocket 或轮询推送
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import logging

from app.models.data.siteconfig import SiteConfig
from app.websocket.manager import manager

logger = logging.getLogger(__name__)


class MessagePushService:
    """消息推送服务"""

    @staticmethod
    async def get_push_config(db: AsyncSession) -> dict:
        """
        获取推送配置

        Returns:
            包含 push_method 和 polling_interval 的字典
        """
        try:
            result = await db.execute(select(SiteConfig))
            config = result.scalar_one_or_none()
            if config:
                return {
                    'push_method': getattr(config, 'message_push_method', 'websocket'),
                    'polling_interval': getattr(config, 'polling_interval', 30)
                }
        except Exception as e:
            logger.error(f"获取推送配置失败: {e}")

        # 默认配置
        return {
            'push_method': 'websocket',
            'polling_interval': 30
        }

    @staticmethod
    async def push_notification(
        db: AsyncSession,
        user_id: int,
        notification_type: str,
        data: dict
    ):
        """
        推送通知给指定用户（根据配置自动选择推送方式）

        Args:
            db: 数据库会话
            user_id: 接收通知的用户ID
            notification_type: 通知类型（如 'notification', 'new_message' 等）
            data: 通知数据
        """
        try:
            config = await MessagePushService.get_push_config(db)
            push_method = config.get('push_method', 'websocket')

            if push_method == 'websocket':
                # 使用 WebSocket 实时推送
                await MessagePushService._push_via_websocket(
                    user_id, notification_type, data
                )
            else:
                # 使用轮询模式（通知已保存到数据库，前端会定期获取）
                logger.debug(f"使用轮询模式，通知已保存到数据库: user_id={user_id}")
        except Exception as e:
            logger.error(f"推送通知失败: user_id={user_id}, error={e}")

    @staticmethod
    async def _push_via_websocket(
        user_id: int,
        notification_type: str,
        data: dict
    ):
        """
        通过 WebSocket 推送消息

        Args:
            user_id: 接收通知的用户ID
            notification_type: 通知类型
            data: 通知数据
        """
        try:
            import time
            message_data = {
                'type': notification_type,
                'data': data,
                'timestamp': int(time.time() * 1000)
            }

            # 发送个人消息
            await manager.send_personal_message(message_data, user_id)
            logger.info(f"WebSocket 推送成功: user_id={user_id}, type={notification_type}")
        except Exception as e:
            logger.error(f"WebSocket 推送失败: user_id={user_id}, error={e}")

    @staticmethod
    async def push_system_notification(
        db: AsyncSession,
        title: str,
        content: str,
        target_url: Optional[str] = None
    ):
        """
        推送系统全局通知给所有在线用户

        Args:
            db: 数据库会话
            title: 通知标题
            content: 通知内容
            target_url: 相关链接
        """
        try:
            config = await MessagePushService.get_push_config(db)
            push_method = config.get('push_method', 'websocket')

            if push_method == 'websocket':
                # 使用 WebSocket 广播
                import time
                message_data = {
                    'type': 'system_notification',
                    'data': {
                        'title': title,
                        'content': content,
                        'target_url': target_url,
                        'timestamp': int(time.time() * 1000)
                    }
                }
                await manager.broadcast_to_all(message_data)
                logger.info(f"系统通知广播成功: title={title}")
            else:
                logger.debug(f"使用轮询模式，系统通知已保存到数据库")
        except Exception as e:
            logger.error(f"推送系统通知失败: error={e}")
