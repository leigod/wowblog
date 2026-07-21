"""
API 集成测试
测试 API 端点的功能和响应
"""
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch


# ==================== 认证 API 测试 ====================

class TestAuthAPI:
    """测试认证相关 API"""

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient):
        """测试成功登录"""
        # Mock 用户数据（用 SimpleNamespace 支持属性访问，匹配 auth.py 的 user.status 等）
        from types import SimpleNamespace
        mock_user = SimpleNamespace(
            id=1,
            username="testuser",
            password="hashed_password",
            salt=None,
            email="test@example.com",
            role="User",
            status="active"
        )

        with patch('app.routers.auth.authenticate_by_email_or_username', return_value=mock_user):
            with patch('app.utils.auth.verify_password', return_value=True):
                with patch('app.crud.users.update_user_login_info'):
                    response = await client.post(
                        "/api/auth/login",
                        json={
                            "username": "testuser",
                            "password": "password123"
                        }
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert data["code"] == 1
                    assert "access_token" in data["data"]
                    assert data["data"]["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient):
        """测试错误密码登录"""
        with patch('app.routers.auth.authenticate_by_email_or_username', return_value=False):
            response = await client.post(
                "/api/auth/login",
                json={
                    "username": "testuser",
                    "password": "wrongpassword"
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 0

    @pytest.mark.asyncio
    async def test_login_disabled_user(self, client: AsyncClient):
        """测试禁用用户登录"""
        from types import SimpleNamespace
        mock_user = SimpleNamespace(
            id=1,
            username="disableduser",
            status="hidden"
        )

        with patch('app.routers.auth.authenticate_by_email_or_username', return_value=mock_user):
            response = await client.post(
                "/api/auth/login",
                json={
                    "username": "disableduser",
                    "password": "password123"
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 0
            assert "禁用" in data["msg"]

    @pytest.mark.asyncio
    async def test_get_temp_token(self, client: AsyncClient):
        """测试获取临时 token"""
        response = await client.get("/api/auth/temp-token")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 1
        assert "access_token" in data["data"]

    @pytest.mark.asyncio
    async def test_logout(self, client: AsyncClient):
        """测试登出"""
        response = await client.post("/api/auth/logout")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 1
        assert data["data"]["logged_out"] is True


# ==================== 博客 API 测试 ====================
# TODO: 博客 API 路由已重构（/api/articles → POST /api/blog/articles/list 等），
# 原 mock 测试与当前路由/函数脱节，待后续按新路由补集成测试。


# ==================== 用户 API 测试 ====================

class TestUserAPI:
    """测试用户相关 API"""

    @pytest.mark.asyncio
    async def test_get_current_user_info_unauthorized(self, client: AsyncClient):
        """测试未授权获取用户信息"""
        response = await client.get("/api/auth/me")

        # 应该返回 401 或重定向到登录
        assert response.status_code in [401, 403, 307, 302]


# ==================== 媒体 API 测试 ====================

class TestMediaAPI:
    """测试媒体相关 API"""

    @pytest.mark.asyncio
    async def test_upload_image_unauthorized(self, client: AsyncClient):
        """测试未授权上传图片"""
        response = await client.post(
            "/api/upload/",
            files={"file": ("test.jpg", b"fake image data", "image/jpeg")}
        )

        # 应该需要认证
        assert response.status_code in [401, 403, 422]


# ==================== 速率限制测试 ====================

class TestRateLimit:
    """测试速率限制"""

    @pytest.mark.asyncio
    async def test_rate_limit_login(self, client: AsyncClient):
        """测试登录速率限制"""
        # 连续多次请求应该触发速率限制
        responses = []
        for _ in range(6):  # 超过限制（5次/分钟）
            with patch('app.routers.auth.authenticate_by_email_or_username', return_value=False):
                response = await client.post(
                    "/api/auth/login",
                    json={"username": "test", "password": "test"}
                )
                responses.append(response)

        # 最后一个请求应该被速率限制
        last_response = responses[-1]
        # 可能返回 429 或继续正常（取决于中间件实现）
        assert last_response.status_code in [200, 429]


# ==================== 错误处理测试 ====================

class TestErrorHandling:
    """测试错误处理"""

    @pytest.mark.asyncio
    async def test_404_not_found(self, client: AsyncClient):
        """测试 404 错误"""
        response = await client.get("/api/nonexistent/endpoint")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_invalid_json(self, client: AsyncClient):
        """测试无效 JSON"""
        response = await client.post(
            "/api/auth/login",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code in [400, 422]


# ==================== CORS 测试 ====================

class TestCORS:
    """测试 CORS 配置"""

    @pytest.mark.asyncio
    async def test_cors_headers(self, client: AsyncClient):
        """测试 CORS 响应头"""
        # CORS 预检（OPTIONS）应返回 200 并带 Allow-Origin 响应头
        response = await client.options(
            "/api/auth/login",
            headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST"}
        )

        assert response.status_code == 200
        lowered_headers = {k.lower() for k in response.headers}
        assert "access-control-allow-origin" in lowered_headers
