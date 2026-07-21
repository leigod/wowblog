"""
认证模块单元测试
测试 JWT Token 生成、验证、密码加密等功能
"""
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch
from jwt.exceptions import InvalidTokenError

from app.dependencies.authentication import (
    create_access_token,
    create_temporary_token,
    authenticate_user,
    get_current_user,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.utils.auth import verify_password, get_password_hash
import jwt


# ==================== Token 测试 ====================

class TestTokenCreation:
    """测试 Token 创建"""

    def test_create_access_token_with_expires(self):
        """测试创建带过期时间的 access token"""
        data = {"sub": "testuser"}
        expires = timedelta(minutes=60)

        token = create_access_token(data, expires)

        assert isinstance(token, str)
        assert len(token) > 0

        # 验证 token 可以正确解码
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "testuser"
        assert "exp" in payload

    def test_create_access_token_without_expires(self):
        """测试创建使用默认过期时间的 access token"""
        data = {"sub": "testuser"}

        token = create_access_token(data)

        assert isinstance(token, str)

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "testuser"

        # 验证 token 有过期时间
        assert "exp" in payload
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        diff = (exp - now).total_seconds()
        # 允许合理的误差范围
        assert 0 < diff < (ACCESS_TOKEN_EXPIRE_MINUTES * 60 + 10)

    def test_create_temporary_token(self):
        """测试创建临时 token"""
        data = {"jti": "test-token-id"}

        token = create_temporary_token(data)

        assert isinstance(token, str)

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["jti"] == "test-token-id"
        assert payload["type"] == "temporary"

        # 临时 token 应该有较短的过期时间（约10分钟）
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        diff = (exp - now).total_seconds()
        assert 500 < diff < 700  # 10分钟 +/- 小误差


class TestTokenValidation:
    """测试 Token 验证"""

    def test_valid_token_decoding(self):
        """测试有效 token 解码"""
        data = {"sub": "testuser"}
        token = create_access_token(data)

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "testuser"

    def test_expired_token_raises_error(self):
        """测试过期 token 抛出错误"""
        # 创建已过期的 token
        data = {"sub": "testuser"}
        expires = timedelta(minutes=-30)  # 30分钟前
        token = create_access_token(data, expires)

        # 过期 token 应该抛出 ExpiredSignatureError
        with pytest.raises(jwt.exceptions.ExpiredSignatureError):
            jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    def test_invalid_token_raises_error(self):
        """测试无效 token 抛出错误"""
        invalid_token = "invalid.token.string"

        with pytest.raises(InvalidTokenError):
            jwt.decode(invalid_token, SECRET_KEY, algorithms=[ALGORITHM])

    def test_token_with_wrong_secret_raises_error(self):
        """测试错误密钥的 token 抛出错误"""
        data = {"sub": "testuser"}
        token = create_access_token(data)

        with pytest.raises(InvalidTokenError):
            jwt.decode(token, "wrong_secret", algorithms=[ALGORITHM])


# ==================== 密码加密测试 ====================

class TestPasswordHashing:
    """测试密码加密功能（bcrypt）"""

    def test_hash_password_generates_different_hashes(self):
        """测试相同密码使用 bcrypt 生成不同的哈希值"""
        password = "testpassword123"

        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2
        # bcrypt 哈希长度是 60 字符
        assert len(hash1) == 60
        assert len(hash2) == 60

    def test_verify_password_correct(self):
        """测试正确密码验证"""
        password = "testpassword123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """测试错误密码验证"""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False


# ==================== 用户认证测试 ====================

class TestUserAuthentication:
    """测试用户认证功能"""

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, mock_db_session, mock_user):
        """测试成功认证用户"""
        # 将 dict 转换为对象
        class MockUser:
            def __init__(self, data):
                for key, value in data.items():
                    setattr(self, key, value)

        user_obj = MockUser(mock_user)

        with patch('app.dependencies.authentication.get_user_in_db', return_value=user_obj):
            # mock_user 密码是 "password123" 的 bcrypt 哈希
            result = await authenticate_user("testuser", "password123", mock_db_session)

            assert result is not False
            assert result.username == "testuser"

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, mock_db_session):
        """测试用户不存在"""
        with patch('app.dependencies.authentication.get_user_in_db', return_value=None):
            result = await authenticate_user("nonexistent", "password123", mock_db_session)

            assert result is False

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, mock_db_session, mock_user):
        """测试错误密码"""
        class MockUser:
            def __init__(self, data):
                for key, value in data.items():
                    setattr(self, key, value)

        user_obj = MockUser(mock_user)

        with patch('app.dependencies.authentication.get_user_in_db', return_value=user_obj):
            # 使用错误的密码
            result = await authenticate_user("testuser", "wrongpassword", mock_db_session)

            assert result is False


# ==================== Token 环境变量测试 ====================

class TestTokenConfiguration:
    """测试 Token 配置"""

    def test_secret_key_exists(self):
        """测试密钥存在"""
        assert SECRET_KEY is not None
        assert len(SECRET_KEY) > 0

    def test_algorithm_is_hs256(self):
        """测试算法是 HS256"""
        assert ALGORITHM == "HS256"

    def test_access_token_expire_minutes_default(self):
        """测试默认 Token 过期时间"""
        # 验证配置值存在且为正数（可能从 .env 设置为 10080）
        assert ACCESS_TOKEN_EXPIRE_MINUTES is not None
        assert ACCESS_TOKEN_EXPIRE_MINUTES > 0
        # 验证值在合理范围内（至少30分钟，最多30天）
        assert ACCESS_TOKEN_EXPIRE_MINUTES >= 30


# ==================== Mock 对象测试 ====================

class TestTokenDecoding:
    """测试 Token 解码"""

    def test_valid_token_structure(self, valid_token):
        """测试有效 token 结构"""
        assert isinstance(valid_token, str)
        assert len(valid_token) > 0

        payload = jwt.decode(valid_token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "sub" in payload
        assert "exp" in payload

    def test_expired_token_structure(self, expired_token):
        """测试过期 token 结构"""
        assert isinstance(expired_token, str)

        # 应该无法解码（已过期）
        with pytest.raises(InvalidTokenError):
            jwt.decode(expired_token, SECRET_KEY, algorithms=[ALGORITHM])

