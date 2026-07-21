"""
WebSocket 连接测试脚本
用于测试 WebSocket 连接和消息推送功能
"""
import asyncio
import websockets
import json
import requests
from typing import Optional


class WebSocketTester:
    """WebSocket 测试客户端"""

    def __init__(self, base_url: str = "ws://localhost:8000"):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.connection_id: Optional[str] = None
        self.user_id: Optional[int] = None

    def login(self, username: str, password: str) -> bool:
        """
        登录获取 token

        Args:
            username: 用户名
            password: 密码

        Returns:
            是否登录成功
        """
        try:
            response = requests.post(
                f"{self.base_url.replace('ws://', 'http://')}/api/login",
                data={
                    "username": username,
                    "password": password
                }
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 1:
                    self.token = data["data"]["access_token"]
                    print(f"✓ 登录成功: {username}")
                    return True
            print(f"✗ 登录失败: {response.text}")
            return False
        except Exception as e:
            print(f"✗ 登录异常: {e}")
            return False

    async def connect(self) -> bool:
        """
        连接 WebSocket

        Returns:
            是否连接成功
        """
        if not self.token:
            print("✗ 请先登录")
            return False

        try:
            url = f"{self.base_url}/api/ws/messages?token={self.token}"
            self.ws = await websockets.connect(url)

            # 等待连接确认消息
            message = await self.ws.recv()
            data = json.loads(message)

            if data.get("type") == "connected":
                self.connection_id = data.get("connection_id")
                self.user_id = data.get("user_id")
                print(f"✓ WebSocket 连接成功")
                print(f"  连接ID: {self.connection_id}")
                print(f"  用户ID: {self.user_id}")
                return True

            print(f"✗ 连接失败: {data}")
            return False

        except Exception as e:
            print(f"✗ WebSocket 连接异常: {e}")
            return False

    async def listen(self, timeout: int = 30):
        """
        监听消息

        Args:
            timeout: 超时时间（秒）
        """
        print(f"\n开始监听消息 (超时: {timeout}秒)...")
        print("-" * 50)

        try:
            while timeout > 0:
                try:
                    message = await asyncio.wait_for(
                        self.ws.recv(),
                        timeout=1.0
                    )
                    data = json.loads(message)
                    print(f"\n📩 收到消息:")
                    print(f"  类型: {data.get('type')}")
                    print(f"  数据: {json.dumps(data.get('data'), indent=2, ensure_ascii=False)}")
                    print(f"  时间: {data.get('timestamp')}")

                except asyncio.TimeoutError:
                    timeout -= 1
                    # 每10秒发送一次心跳
                    if timeout % 10 == 0:
                        await self.send_ping()

        except KeyboardInterrupt:
            print("\n监听已中断")
        except Exception as e:
            print(f"\n✗ 监听异常: {e}")

    async def send_ping(self):
        """发送心跳包"""
        if self.ws:
            await self.ws.send(json.dumps({"type": "ping"}))
            print("💓 心跳已发送")

    async def send_echo(self, data: dict):
        """发送测试消息"""
        if self.ws:
            await self.ws.send(json.dumps({"type": "echo", "data": data}))
            print(f"📤 测试消息已发送: {data}")

    async def close(self):
        """关闭连接"""
        if self.ws:
            await self.ws.close()
            print("✓ WebSocket 连接已关闭")


async def test_websocket():
    """测试 WebSocket 功能"""
    print("=" * 50)
    print("WebSocket 功能测试")
    print("=" * 50)

    tester = WebSocketTester()

    # 1. 登录（默认使用 admin/123456，你可以修改这些值）
    print("\n1. 测试登录...")
    username = "admin"  # 修改为你的用户名
    password = "123456"  # 修改为你的密码
    if not tester.login(username, password):
        print(f"登录失败，请检查用户名和密码: {username}/{password}")
        return

    # 2. 连接 WebSocket
    print("\n2. 测试 WebSocket 连接...")
    if not await tester.connect():
        return

    # 3. 发送测试消息
    print("\n3. 测试消息发送...")
    await tester.send_echo({"test": "hello world"})

    # 4. 监听消息
    print("\n4. 测试消息接收...")
    await tester.listen(timeout=30)

    # 5. 关闭连接
    print("\n5. 关闭连接...")
    await tester.close()


def test_websocket_status():
    """测试 WebSocket 状态接口"""
    print("\n" + "=" * 50)
    print("WebSocket 状态查询")
    print("=" * 50)

    try:
        response = requests.get("http://localhost:8000/api/ws/status")
        if response.status_code == 200:
            data = response.json()
            print(f"\n✓ 状态查询成功:")
            print(f"  总连接数: {data.get('total_connections', 0)}")
            print(f"  在线用户数: {data.get('connected_users_count', 0)}")
            print(f"  在线用户ID: {data.get('connected_users', [])}")
        else:
            print(f"✗ 状态查询失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 状态查询异常: {e}")


if __name__ == "__main__":
    import sys

    print("\nWebSocket 测试工具")
    print("=" * 50)
    print("用法:")
    print("  python test_websocket.py status  - 查询 WebSocket 状态")
    print("  python test_websocket.py test    - 测试 WebSocket 连接")
    print("=" * 50)

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "status":
            test_websocket_status()
        elif command == "test":
            asyncio.run(test_websocket())
        else:
            print(f"未知命令: {command}")
    else:
        print("\n请指定命令: status 或 test")
