"""
OAuth 配置文件
用于配置各社交登录平台的 Client ID 和 Secret
"""
import os
from dotenv import load_dotenv

load_dotenv()


class OAuthConfig:
    """OAuth 配置类"""

    # 前端 URL（用于回调）
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
    BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000/api')

    # Google OAuth
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
    GOOGLE_AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
    GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token'
    GOOGLE_API_URL = 'https://www.googleapis.com/oauth2/v2/userinfo'
    GOOGLE_SCOPE = 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile'

    # GitHub OAuth
    GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID', '')
    GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET', '')
    GITHUB_AUTH_URL = 'https://github.com/login/oauth/authorize'
    GITHUB_TOKEN_URL = 'https://github.com/login/oauth/access_token'
    GITHUB_API_URL = 'https://api.github.com/user'
    GITHUB_SCOPE = 'user:email'

    # Apple Sign In
    APPLE_CLIENT_ID = os.getenv('APPLE_CLIENT_ID', '')
    APPLE_TEAM_ID = os.getenv('APPLE_TEAM_ID', '')
    APPLE_KEY_ID = os.getenv('APPLE_KEY_ID', '')
    APPLE_PRIVATE_KEY = os.getenv('APPLE_PRIVATE_KEY', '')
    APPLE_AUTH_URL = 'https://appleid.apple.com/auth/authorize'
    APPLE_TOKEN_URL = 'https://appleid.apple.com/auth/token'
    APPLE_SCOPE = 'name email'


# 验证必需的配置
def validate_oauth_config(provider: str) -> bool:
    """验证指定平台的 OAuth 配置是否完整"""
    config = OAuthConfig()

    if provider == 'google':
        return bool(config.GOOGLE_CLIENT_ID and config.GOOGLE_CLIENT_SECRET)
    elif provider == 'github':
        return bool(config.GITHUB_CLIENT_ID and config.GITHUB_CLIENT_SECRET)
    elif provider == 'apple':
        return bool(config.APPLE_CLIENT_ID and config.APPLE_TEAM_ID and config.APPLE_KEY_ID)
    return False
