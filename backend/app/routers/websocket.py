"""
WebSocket 路由
处理 WebSocket 连接和消息推送
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.websocket.manager import manager
from app.dependencies.authentication import SECRET_KEY, ALGORITHM
import jwt
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()


async def verify_websocket_token(token: str, db: AsyncSession):
    """
    验证 WebSocket token 并返回用户ID

    Args:
        token: JWT token
        db: 数据库会话

    Returns:
        用户ID，验证失败返回 None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username:
            from app.crud.users import get_user
            user = await get_user(db, username=username)
            if user:
                return user.id
    except Exception as e:
        logger.error(f"Token 验证失败: {e}")
    return None


@router.websocket("/ws/messages")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT token"),
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket 消息推送端点

    Args:
        websocket: WebSocket 实例
        token: JWT 认证 token
        db: 数据库会话
    """
    # 验证 token
    user_id = await verify_websocket_token(token, db)
    if not user_id:
        await websocket.close(code=1008, reason="Invalid token")
        return

    # 生成唯一连接ID
    connection_id = str(uuid.uuid4())

    # 接受连接
    await manager.connect(websocket, user_id, connection_id)

    try:
        # 发送连接成功消息
        await websocket.send_json({
            "type": "connected",
            "connection_id": connection_id,
            "user_id": user_id,
            "message": "WebSocket 连接成功"
        })

        # 保持连接并处理客户端消息
        while True:
            data = await websocket.receive_json()

            # 处理心跳包
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})

            # 可以在这里处理其他类型的消息
            elif data.get("type") == "echo":
                # 回显消息（用于测试）
                await websocket.send_json({
                    "type": "echo_response",
                    "data": data.get("data")
                })

    except WebSocketDisconnect:
        logger.info(f"WebSocket 主动断开: user_id={user_id}, connection_id={connection_id}")
        await manager.disconnect(connection_id)

    except Exception as e:
        logger.error(f"WebSocket 错误: user_id={user_id}, connection_id={connection_id}, error={e}")
        await manager.disconnect(connection_id)


@router.get("/ws/status")
async def get_websocket_status():
    """
    获取 WebSocket 连接状态

    Returns:
        连接统计信息
    """
    total_connections = await manager.get_connection_count()
    connected_users = manager.get_connected_users()

    return {
        "total_connections": total_connections,
        "connected_users_count": len(connected_users),
        "connected_users": list(connected_users)
    }
