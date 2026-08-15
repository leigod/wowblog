"""
authlib OAuth 客户端注册中心

用 authlib 的 Starlette 客户端统一管理各社交登录 Provider，
自动处理 state / PKCE / nonce / id_token 验签。
state 经由 SessionMiddleware 的签名 cookie 中转（无状态，多 worker 友好）。

支持的 Provider（仅在配置了对应凭据时才注册）：
  - google  : OIDC，authlib 自动验签 id_token，userinfo 直接可信
  - github  : 非 OIDC，拿到 access_token 后手动调 /user 取资料
  - apple   : OIDC + form_post + ES256 client_secret（需 Apple 凭据实测）

国内三家（wechat/qq/alipay）在 P2 阶段补齐，届时在此 register。
"""
import time
import jwt
from authlib.integrations.starlette_client import OAuth

from app.config.oauth import OAuthConfig

oauth = OAuth()

# 标识当前后端"认识"的 provider（与是否注册了凭据无关）。
# 用于路由层校验，避免任意 provider 字符串打到 authlib。
SUPPORTED_PROVIDERS = {"google", "github", "gitee", "apple"}


def get_oauth_client(provider: str):
    """
    返回已注册的 authlib 客户端实例；未注册（缺凭据或未知 provider）返回 None。
    """
    if provider not in SUPPORTED_PROVIDERS:
        return None
    return oauth.create_client(provider)


def _generate_apple_client_secret() -> str:
    """
    生成 Apple client_secret（ES256 签名的 JWT）。

    Apple 的 token endpoint 要求 client_secret 是由开发者私钥（ES256）签名的 JWT，
    有效期最长 6 个月。这里在应用启动注册时生成一次，随部署周期刷新即可。
    """
    headers = {"alg": "ES256", "kid": OAuthConfig.APPLE_KEY_ID}
    now = int(time.time())
    payload = {
        "iss": OAuthConfig.APPLE_TEAM_ID,
        "iat": now,
        "exp": now + 15777000,  # 约 6 个月
        "aud": "https://appleid.apple.com",
        "sub": OAuthConfig.APPLE_CLIENT_ID,
    }
    return jwt.encode(
        payload,
        OAuthConfig.APPLE_PRIVATE_KEY,
        algorithm="ES256",
        headers=headers,
    )


# ---------- Google（OIDC discovery，自动验签 id_token） ----------
if OAuthConfig.GOOGLE_CLIENT_ID:
    oauth.register(
        name="google",
        client_id=OAuthConfig.GOOGLE_CLIENT_ID,
        client_secret=OAuthConfig.GOOGLE_CLIENT_SECRET,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

# ---------- GitHub（非 OIDC，userinfo 需手动取） ----------
if OAuthConfig.GITHUB_CLIENT_ID:
    oauth.register(
        name="github",
        client_id=OAuthConfig.GITHUB_CLIENT_ID,
        client_secret=OAuthConfig.GITHUB_CLIENT_SECRET,
        access_token_url="https://github.com/login/oauth/access_token",
        authorize_url="https://github.com/login/oauth/authorize",
        api_base_url="https://api.github.com/",
        client_kwargs={"scope": "user:email"},
    )

# ---------- Gitee（国内代码托管，标准 OAuth2，免费 / 个人可申请） ----------
if OAuthConfig.GITEE_CLIENT_ID:
    oauth.register(
        name="gitee",
        client_id=OAuthConfig.GITEE_CLIENT_ID,
        client_secret=OAuthConfig.GITEE_CLIENT_SECRET,
        access_token_url="https://gitee.com/oauth/token",
        authorize_url="https://gitee.com/oauth/authorize",
        api_base_url="https://gitee.com/api/v5/",
        client_kwargs={"scope": "user_info"},
    )

# ---------- Apple（OIDC，form_post + ES256 client_secret） ----------
# 注意：Apple 流程需凭据实测；id_token 由 authlib 用 Apple 公钥自动验签。
if OAuthConfig.APPLE_CLIENT_ID and OAuthConfig.APPLE_PRIVATE_KEY:
    oauth.register(
        name="apple",
        client_id=OAuthConfig.APPLE_CLIENT_ID,
        client_secret=_generate_apple_client_secret(),
        authorize_url="https://appleid.apple.com/auth/authorize",
        access_token_url="https://appleid.apple.com/auth/token",
        jwks_url="https://appleid.apple.com/auth/keys",
        client_kwargs={"scope": "name email", "response_mode": "form_post"},
    )
