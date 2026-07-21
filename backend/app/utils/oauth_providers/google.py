"""
Google OAuth Provider 实现
"""
import httpx
from typing import Dict, Any
from .base import BaseOAuthProvider, OAuthUserInfo


class GoogleOAuthProvider(BaseOAuthProvider):
    """Google OAuth 提供商"""

    def __init__(self, client_id: str, client_secret: str):
        super().__init__(client_id, client_secret)
        self.auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        self.scope = "https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile"

    def get_auth_url(self, redirect_uri: str, state: str) -> str:
        """获取 Google 授权 URL"""
        from urllib.parse import urlencode

        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": self.scope,
            "response_type": "code",
            "state": state,
            "access_type": "offline",
            "prompt": "consent"
        }
        return f"{self.auth_url}?{urlencode(params)}"

    async def get_access_token(self, code: str, redirect_uri: str) -> str:
        """用授权码换取访问令牌"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    "code": code,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code"
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("access_token")

    async def get_user_info(self, access_token: str) -> OAuthUserInfo:
        """获取 Google 用户信息"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.userinfo_url,
                headers={
                    "Authorization": f"Bearer {access_token}"
                }
            )
            response.raise_for_status()
            data: Dict[str, Any] = response.json()

            return OAuthUserInfo(
                provider="google",
                provider_user_id=str(data.get("id")),
                email=data.get("email"),
                name=data.get("name"),
                avatar_url=data.get("picture"),
                raw_data=data
            )
