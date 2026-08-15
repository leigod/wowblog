"""
OAuth 社交登录测试

覆盖核心逻辑（不依赖外部 OAuth 凭据 / 真 HTTP）：
  - redirect_uri 白名单：scheme+host+port 严格比对，防 startswith 子域绕过
  - 手撸 provider state：issue / verify / 一次性
  - QQ JSONP callback 解析
  - 微信/QQ 授权 URL 构造（含微信的 #wechat_redirect）
  - handle_oauth_user_login：新建 / 按 provider_user_id 命中 / 按 email 合并 + token 持久化
  - /auth/oauth/session：cookie 中转取 token
  - /auth/oauth/{provider}：OAUTH_ENABLED 关闭时 503
  - /auth/oauth/bindings：未登录 401
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

import app.routers.auth as auth_module
from app.routers.auth import (
    _is_allowed_redirect_uri,
    _build_frontend_callback,
    _build_bind_frontend_callback,
    handle_oauth_user_login,
    _is_provider_enabled,
    _execute_bind,
)
from app.oauth.manual_providers import (
    issue_state,
    verify_state,
    _parse_qq_callback,
    build_manual_auth_url,
)
from app.config.oauth import OAuthConfig


# ==================== redirect_uri 白名单（严格比对） ====================

class TestRedirectUriWhitelist:
    """旧实现用 str.startswith 会被同前缀子域绕过，这里验证已改为严格比对。"""

    def _set_allowed(self, monkeypatch, allowed):
        monkeypatch.setattr(auth_module, "_OAUTH_REDIRECT_ALLOWED", allowed)

    def test_exact_match_allowed(self, monkeypatch):
        self._set_allowed(monkeypatch, ["http://localhost:5173"])
        assert _is_allowed_redirect_uri("http://localhost:5173") is True
        assert _is_allowed_redirect_uri("http://localhost:5173/login") is True

    def test_evil_subdomain_rejected(self, monkeypatch):
        """关键安全点：同前缀子域不应命中（旧 startswith 实现的绕过点）"""
        self._set_allowed(monkeypatch, ["http://localhost:5173"])
        assert _is_allowed_redirect_uri("http://localhost:5173.evil.com/") is False
        assert _is_allowed_redirect_uri("http://localhost:5173evil.com/") is False

    def test_different_port_rejected(self, monkeypatch):
        self._set_allowed(monkeypatch, ["http://localhost:5173"])
        assert _is_allowed_redirect_uri("http://localhost:8080") is False

    def test_different_scheme_rejected(self, monkeypatch):
        self._set_allowed(monkeypatch, ["http://localhost:5173"])
        assert _is_allowed_redirect_uri("https://localhost:5173") is False

    def test_empty_or_none_rejected(self, monkeypatch):
        self._set_allowed(monkeypatch, ["http://localhost:5173"])
        assert _is_allowed_redirect_uri(None) is False
        assert _is_allowed_redirect_uri("") is False

    def test_empty_whitelist_rejects_all(self, monkeypatch):
        self._set_allowed(monkeypatch, [])
        assert _is_allowed_redirect_uri("http://localhost:5173") is False


# ==================== 手撸 provider state（CSRF） ====================

class TestManualState:
    def _req(self):
        req = MagicMock()
        req.session = {}
        return req

    def test_issue_and_verify_success(self):
        req = self._req()
        state = issue_state(req, "wechat")
        assert state
        assert req.session["oauth_manual_state"]["provider"] == "wechat"
        assert verify_state(req, state) is True

    def test_verify_deletes_state(self):
        """state 一次性：校验后从 session 删除"""
        req = self._req()
        state = issue_state(req, "qq")
        verify_state(req, state)
        assert "oauth_manual_state" not in req.session

    def test_verify_wrong_state(self):
        req = self._req()
        issue_state(req, "wechat")
        assert verify_state(req, "totally-wrong") is False

    def test_verify_missing_session(self):
        req = self._req()
        assert verify_state(req, "anything") is False
        assert verify_state(req, None) is False

    def test_verify_is_one_time(self):
        """同一 state 第二次校验失败（已被消费删除）"""
        req = self._req()
        state = issue_state(req, "wechat")
        assert verify_state(req, state) is True
        assert verify_state(req, state) is False


# ==================== QQ JSONP 解析 ====================

class TestQQCallbackParse:
    def test_parse_jsonp_wrapper(self):
        text = 'callback( {"client_id":"12345","openid":"ABCDEF"} );'
        data = _parse_qq_callback(text)
        assert data["openid"] == "ABCDEF"
        assert data["client_id"] == "12345"

    def test_parse_plain_json(self):
        text = '{"openid":"XYZ"}'
        data = _parse_qq_callback(text)
        assert data["openid"] == "XYZ"

    def test_parse_multiline_jsonp(self):
        text = 'callback(\n  {"openid":"M"}\n);'
        data = _parse_qq_callback(text)
        assert data["openid"] == "M"


# ==================== 微信/QQ 授权 URL 构造 ====================

class TestManualAuthUrl:
    def test_wechat_url_has_required_parts(self):
        with patch.object(OAuthConfig, "WECHAT_CLIENT_ID", "wxAPPID"):
            url = build_manual_auth_url(
                "wechat",
                "https://blog.example.com/api/auth/callback/wechat",
                "STATE123",
            )
        assert "open.weixin.qq.com/connect/qrconnect" in url
        assert "appid=wxAPPID" in url
        assert "scope=snsapi_login" in url
        assert "state=STATE123" in url
        # 关键：微信强制 redirect_uri 后拼 #wechat_redirect
        assert url.endswith("#wechat_redirect")

    def test_qq_url_has_required_parts(self):
        with patch.object(OAuthConfig, "QQ_CLIENT_ID", "QQAPPID"):
            url = build_manual_auth_url(
                "qq",
                "https://blog.example.com/api/auth/callback/qq",
                "ST",
            )
        assert "graph.qq.com/oauth2.0/authorize" in url
        assert "client_id=QQAPPID" in url
        assert "response_type=code" in url
        # QQ 不需要 #wechat_redirect
        assert "#wechat_redirect" not in url

    def test_unknown_provider_raises(self):
        with pytest.raises(ValueError):
            build_manual_auth_url("facebook", "https://x", "s")


# ==================== 前端回跳 URL 构造 ====================

class TestFrontendCallbackUrl:
    def test_success_with_redirect(self):
        url = _build_frontend_callback("success", redirect="/article/1")
        assert "oauth=success" in url
        assert "redirect=%2Farticle%2F1" in url

    def test_error_with_desc(self):
        url = _build_frontend_callback("error", desc="denied")
        assert "oauth=error" in url
        assert "desc=denied" in url

    def test_status_only(self):
        url = _build_frontend_callback("success")
        assert "oauth=success" in url
        assert "desc=" not in url


# ==================== handle_oauth_user_login（真 sqlite） ====================

@pytest.fixture
async def db_session():
    """只建 OAuth 测试所需的表，避开 sqlite 全局索引名冲突（项目 wb_blacklist 等多表共用 idx_type）。"""
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
    from app.database import Base
    import app.models.data.users as users_model
    import app.models.data.user_oauth as oauth_model

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(lambda c: Base.metadata.create_all(
            c,
            tables=[
                users_model.User.__table__,
                oauth_model.UserOAuth.__table__,
            ],
            checkfirst=True,
        ))
    Session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with Session() as session:
        yield session
    await engine.dispose()


class TestHandleOauthUserLogin:
    @pytest.mark.asyncio
    async def test_creates_new_user_and_binding(self, db_session):
        """全新 OAuth 用户：创建 wb_users + wb_user_oauth，且 provider token 持久化"""
        user = await handle_oauth_user_login(
            db=db_session, provider="github", provider_user_id="12345",
            email="new@example.com", name="New User", avatar_url="http://avatar",
            access_token="atk", refresh_token="rtk", raw_data={"id": 12345},
        )
        assert user is not None
        assert user.username.startswith("github_")
        assert user.email == "new@example.com"
        assert user.role == "User"
        assert user.profile_image == "http://avatar"

        from app.crud.user_oauth import get_oauth_by_provider
        binding = await get_oauth_by_provider(db_session, "github", "12345")
        assert binding is not None
        assert binding.user_id == user.id
        assert binding.access_token == "atk"
        assert binding.refresh_token == "rtk"

    @pytest.mark.asyncio
    async def test_existing_binding_logs_in_same_user(self, db_session):
        """同一 provider_user_id 再次登录 → 返回同一用户，不重复创建"""
        u1 = await handle_oauth_user_login(
            db=db_session, provider="github", provider_user_id="99999",
            email="a@b.com", name="A", avatar_url=None,
        )
        await db_session.commit()
        uid1 = u1.id

        u2 = await handle_oauth_user_login(
            db=db_session, provider="github", provider_user_id="99999",
            email="a@b.com", name="A", avatar_url=None,
        )
        assert u2.id == uid1

    @pytest.mark.asyncio
    async def test_email_match_binds_to_existing_user(self, db_session):
        """邮箱已存在 → OAuth 绑到该已有用户，不新建"""
        import app.models.data.users as users_model
        from app.utils.auth import get_password_hash
        from datetime import datetime
        ts = int(datetime.now().timestamp())
        existing = users_model.User(
            username="localuser", email="exist@example.com",
            password=get_password_hash("whatever"), salt=None,
            full_name="Local", role="User", status="active",
            createtime=ts,
        )
        db_session.add(existing)
        await db_session.flush()
        existing_id = existing.id

        user = await handle_oauth_user_login(
            db=db_session, provider="google", provider_user_id="g-1",
            email="exist@example.com", name="G", avatar_url=None,
        )
        assert user.id == existing_id  # 绑到已有用户，未新建

        from app.crud.user_oauth import get_oauth_by_provider
        b = await get_oauth_by_provider(db_session, "google", "g-1")
        assert b is not None and b.user_id == existing_id


# ==================== 端点：session 中转 / 守卫 ====================

class TestOauthEndpoints:
    @pytest.fixture(autouse=True)
    def _no_rate_limit(self, monkeypatch):
        """测试环境无 Redis，跳过限流中间件的 Redis 连接（否则 client 请求会挂死）"""
        from unittest.mock import AsyncMock
        import app.main as main_module
        monkeypatch.setattr(main_module, "check_rate_limit", AsyncMock(return_value=None))

    @pytest.mark.asyncio
    async def test_session_returns_token_from_cookie(self, client):
        """有效 cookie → 返回 token"""
        resp = await client.get("/api/auth/oauth/session", cookies={"oauth_token": "fake-jwt"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 1
        assert body["data"]["access_token"] == "fake-jwt"

    @pytest.mark.asyncio
    async def test_session_no_cookie_returns_401(self, client):
        resp = await client.get("/api/auth/oauth/session")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_login_disabled_returns_503(self, client):
        """OAUTH_ENABLED=false 时授权跳转返回 503（与运行环境 .env 解耦）"""
        with patch.object(auth_module, "OAUTH_ENABLED", False):
            resp = await client.get("/api/auth/oauth/github")
        assert resp.status_code == 503

    @pytest.mark.asyncio
    async def test_bindings_require_auth(self, client):
        """绑定列表未登录 → 401"""
        resp = await client.get("/api/auth/oauth/bindings")
        assert resp.status_code == 401


# ==================== provider 启用校验（后台开关 + 列表） ====================

class TestProviderEnabled:
    """oauth_enabled 总开关 + enabled_oauth_providers 列表共同决定可用性。"""

    @pytest.mark.asyncio
    async def test_enabled_when_in_list(self, mock_db_session):
        config = MagicMock(oauth_enabled=1, enabled_oauth_providers=["github", "gitee"])
        with patch("app.routers.auth.get_site_config", AsyncMock(return_value=config)):
            assert await _is_provider_enabled(mock_db_session, "github") is True
            assert await _is_provider_enabled(mock_db_session, "wechat") is False

    @pytest.mark.asyncio
    async def test_disabled_when_total_switch_off(self, mock_db_session):
        config = MagicMock(oauth_enabled=0, enabled_oauth_providers=["github"])
        with patch("app.routers.auth.get_site_config", AsyncMock(return_value=config)):
            assert await _is_provider_enabled(mock_db_session, "github") is False

    @pytest.mark.asyncio
    async def test_disabled_when_no_config(self, mock_db_session):
        with patch("app.routers.auth.get_site_config", AsyncMock(return_value=None)):
            assert await _is_provider_enabled(mock_db_session, "github") is False

    @pytest.mark.asyncio
    async def test_disabled_when_empty_list(self, mock_db_session):
        config = MagicMock(oauth_enabled=1, enabled_oauth_providers=[])
        with patch("app.routers.auth.get_site_config", AsyncMock(return_value=config)):
            assert await _is_provider_enabled(mock_db_session, "github") is False


# ==================== 主动绑定执行（_execute_bind） ====================

class TestExecuteBind:
    """绑定到当前已登录用户：新建 / 冲突拒绝 / 幂等 / 会话失效。"""

    @staticmethod
    def _profile(provider_user_id="g-1"):
        return {
            "provider_user_id": provider_user_id, "email": None, "name": "G",
            "avatar_url": None, "access_token": "atk", "refresh_token": None, "raw_data": {},
        }

    @staticmethod
    async def _make_user(db_session, username, email):
        import app.models.data.users as users_model
        from app.utils.auth import get_password_hash
        from datetime import datetime
        ts = int(datetime.now().timestamp())
        user = users_model.User(
            username=username, email=email, password=get_password_hash("x"),
            salt=None, full_name=username, role="User", status="normal", createtime=ts,
        )
        db_session.add(user)
        await db_session.flush()
        return user

    @pytest.mark.asyncio
    async def test_creates_binding(self, db_session):
        user = await self._make_user(db_session, "u1", "u1@e.com")
        await _execute_bind(db_session, user.id, "github", self._profile())
        from app.crud.user_oauth import get_oauth_by_provider
        b = await get_oauth_by_provider(db_session, "github", "g-1")
        assert b is not None and b.user_id == user.id and b.access_token == "atk"

    @pytest.mark.asyncio
    async def test_conflict_rejected(self, db_session):
        """同一第三方账号已绑别的用户 → 拒绝"""
        user_a = await self._make_user(db_session, "ua", "ua@e.com")
        user_b = await self._make_user(db_session, "ub", "ub@e.com")
        await _execute_bind(db_session, user_a.id, "github", self._profile())
        with pytest.raises(ValueError, match="其他用户"):
            await _execute_bind(db_session, user_b.id, "github", self._profile())

    @pytest.mark.asyncio
    async def test_idempotent_same_user(self, db_session):
        """同用户重复绑同一账号 → 幂等，不报错"""
        user = await self._make_user(db_session, "u", "u@e.com")
        await _execute_bind(db_session, user.id, "gitee", self._profile("gt-1"))
        await _execute_bind(db_session, user.id, "gitee", self._profile("gt-1"))

    @pytest.mark.asyncio
    async def test_no_session_user_raises(self, db_session):
        """会话失效（无 bind_user_id）→ ValueError"""
        with pytest.raises(ValueError, match="失效"):
            await _execute_bind(db_session, None, "github", self._profile())


# ==================== 主动绑定回跳 URL ====================

class TestBindCallbackUrl:
    def test_success_url(self):
        url = _build_bind_frontend_callback("success")
        assert "oauth_bind=success" in url
        assert "/profile/edit" in url

    def test_error_url_with_desc(self):
        url = _build_bind_frontend_callback("error", desc="已绑定其他用户")
        assert "oauth_bind=error" in url
        assert "desc=" in url
