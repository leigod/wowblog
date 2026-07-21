"""OAuth Providers Package"""
from .base import BaseOAuthProvider, OAuthUserInfo
from .google import GoogleOAuthProvider
from .github import GitHubOAuthProvider
from .apple import AppleOAuthProvider

__all__ = [
    'BaseOAuthProvider',
    'OAuthUserInfo',
    'GoogleOAuthProvider',
    'GitHubOAuthProvider',
    'AppleOAuthProvider',
]
