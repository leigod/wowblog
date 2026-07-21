"""
WebSocket 连接管理器
管理客户端 WebSocket 连接，支持消息推送和广播
"""
from typing import Dict, Set, Optional
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        # 活跃连接: {user_id: {connection_id: WebSocket}}
        self.active_connections: Dict[int, Dict[str, WebSocket]] = {}
        # 连接ID到用户ID的映射: {connection_id: user_id}
        self.connection_to_user: Dict[str, int] = {}

    async def connect(self, websocket: WebSocket, user_id: int, connection_id: str):
        """
        接受新的 WebSocket 连接

        Args:
            websocket: WebSocket 实例
            user_id: 用户ID
            connection_id: 连接ID（唯一标识）
        """
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = {}

        self.active_connections[user_id][connection_id] = websocket
        self.connection_to_user[connection_id] = user_id

        logger.info(f"WebSocket 连接建立: user_id={user_id}, connection_id={connection_id}")

    async def disconnect(self, connection_id: str):
        """
        断开 WebSocket 连接

        Args:
            connection_id: 连接ID
        """
        user_id = self.connection_to_user.pop(connection_id, None)

        if user_id and user_id in self.active_connections:
            self.active_connections[user_id].pop(connection_id, None)

            # 如果该用户没有其他连接，移除用户条目
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

        logger.info(f"WebSocket 连接断开: connection_id={connection_id}, user_id={user_id}")

    async def send_personal_message(self, message: dict, user_id: int):
        """
        向指定用户发送消息

        Args:
            message: 消息内容（字典）
            user_id: 目标用户ID
        """
        if user_id not in self.active_connections:
            logger.warning(f"用户 {user_id} 没有活跃连接")
            return

        # 向该用户的所有连接发送消息
        disconnected = []
        for conn_id, connection in self.active_connections[user_id].items():
            try:
                await connection.send_json(message)
                logger.debug(f"消息已发送给用户 {user_id}, 连接 {conn_id}")
            except Exception as e:
                logger.error(f"发送消息失败: conn_id={conn_id}, error={e}")
                disconnected.append(conn_id)

        # 清理断开的连接
        for conn_id in disconnected:
            await self.disconnect(conn_id)

    async def broadcast_to_all(self, message: dict, exclude_user_id: Optional[int] = None):
        """
        向所有连接广播消息

        Args:
            message: 消息内容（字典）
            exclude_user_id: 要排除的用户ID（不发送给该用户）
        """
        for user_id, connections in self.active_connections.items():
            # 跳过排除的用户
            if exclude_user_id and user_id == exclude_user_id:
                continue

            disconnected = []
            for conn_id, connection in connections.items():
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"广播消息失败: user_id={user_id}, conn_id={conn_id}, error={e}")
                    disconnected.append(conn_id)

            # 清理断开的连接
            for conn_id in disconnected:
                await self.disconnect(conn_id)

    async def get_connection_count(self, user_id: Optional[int] = None) -> int:
        """
        获取连接数

        Args:
            user_id: 指定用户ID时返回该用户的连接数，否则返回总连接数

        Returns:
            连接数
        """
        if user_id:
            return len(self.active_connections.get(user_id, {}))

        return sum(len(conns) for conns in self.active_connections.values())

    def get_connected_users(self) -> Set[int]:
        """
        获取所有在线用户的ID集合

        Returns:
            在线用户ID集合
        """
        return set(self.active_connections.keys())


# 全局连接管理器实例
manager = ConnectionManager()
