"""
OAuth Provider 基类
定义 OAuth 提供商需要实现的基础接口
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pydantic import BaseModel


class OAuthUserInfo(BaseModel):
    """统一的 OAuth 用户信息"""
    provider: str
    provider_user_id: str
    email: Optional[str] = None
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None


class BaseOAuthProvider(ABC):
    """OAuth 提供商基类"""

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

    @abstractmethod
    def get_auth_url(self, redirect_uri: str, state: str) -> str:
        """
        获取授权 URL

        Args:
            redirect_uri: 回调地址
            state: 状态参数，用于防止 CSRF 攻击

        Returns:
            授权 URL
        """
        pass

    @abstractmethod
    async def get_access_token(self, code: str, redirect_uri: str) -> str:
        """
        用授权码换取访问令牌

        Args:
            code: 授权码
            redirect_uri: 回调地址

        Returns:
            访问令牌
        """
        pass

    @abstractmethod
    async def get_user_info(self, access_token: str) -> OAuthUserInfo:
        """
        获取用户信息

        Args:
            access_token: 访问令牌

        Returns:
            用户信息
        """
        pass

    def generate_state(self) -> str:
        """生成随机 state 参数"""
        import secrets
        return secrets.token_urlsafe(16)
