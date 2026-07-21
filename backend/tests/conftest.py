"""
Pytest 配置和共享 fixtures
"""
import os
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.database import get_db, Base
from app.dependencies.authentication import SECRET_KEY, ALGORITHM


# 测试数据库配置
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# 创建测试引擎
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """创建测试数据库会话"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session
        await session.rollback()

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(mock_db_session) -> AsyncGenerator[AsyncClient, None]:
    """创建测试客户端（用 mock_db_session，避免 sqlite create_all 的索引名全局唯一冲突；
    test_api 测试本身用 patch mock 上层函数，不依赖真 DB 数据）"""

    async def override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def mock_user():
    """模拟用户数据"""
    from app.utils.auth import get_password_hash
    hashed = get_password_hash("password123")
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "role": "User",
        "status": "active",
        "password": hashed,
        "salt": None,  # 新格式不需要 salt
        "createtime": 1234567890,
        "updatetime": 1234567890
    }


@pytest.fixture
def mock_admin_user():
    """模拟管理员用户"""
    from app.utils.auth import get_password_hash
    hashed = get_password_hash("admin123")
    return {
        "id": 999,
        "username": "admin",
        "email": "admin@example.com",
        "full_name": "Admin User",
        "role": "Admin",
        "status": "active",
        "password": hashed,
        "salt": None,  # 新格式不需要 salt
        "createtime": 1234567890,
        "updatetime": 1234567890
    }


@pytest.fixture
def valid_token(mock_user):
    """生成有效的测试 token"""
    import jwt
    from datetime import datetime, timedelta, timezone

    payload = {
        "sub": mock_user["username"],
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@pytest.fixture
def expired_token(mock_user):
    """生成过期的测试 token"""
    import jwt
    from datetime import datetime, timedelta, timezone

    payload = {
        "sub": mock_user["username"],
        "exp": datetime.now(timezone.utc) - timedelta(minutes=30)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@pytest.fixture
def invalid_token():
    """生成无效的测试 token"""
    return "invalid.token.string"


@pytest.fixture
def mock_db_session():
    """模拟数据库会话"""
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.scalar = AsyncMock()
    session.scalars = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def mock_redis():
    """模拟 Redis 客户端"""
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock()
    redis.delete = AsyncMock()
    redis.exists = AsyncMock(return_value=False)
    redis.incr = AsyncMock(return_value=1)
    redis.expire = AsyncMock()
    return redis


# 测试标记配置
def pytest_configure(config):
    """配置 pytest 标记"""
    config.addinivalue_line("markers", "unit: 单元测试")
    config.addinivalue_line("markers", "integration: 集成测试")
    config.addinivalue_line("markers", "auth: 认证测试")
    config.addinivalue_line("markers", "api: API测试")
    config.addinivalue_line("markers", "websocket: WebSocket测试")
    config.addinivalue_line("markers", "slow: 慢速测试")


# 跳过标记
def pytest_collection_modifyitems(config, items):
    """修改测试项，自动添加标记"""
    for item in items:
        # 根据文件路径自动添加标记
        if "test_auth" in str(item.fspath):
            item.add_marker(pytest.mark.auth)
        elif "test_api" in str(item.fspath):
            item.add_marker(pytest.mark.api)
        elif "test_websocket" in str(item.fspath):
            item.add_marker(pytest.mark.websocket)
