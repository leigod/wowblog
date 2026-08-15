"""authlib OAuth 客户端注册中心包。"""
from .registry import oauth, SUPPORTED_PROVIDERS, get_oauth_client

__all__ = ["oauth", "SUPPORTED_PROVIDERS", "get_oauth_client"]
