"""
GitHub OAuth Provider 实现
"""
import httpx
from typing import Dict, Any
from .base import BaseOAuthProvider, OAuthUserInfo


class GitHubOAuthProvider(BaseOAuthProvider):
    """GitHub OAuth 提供商"""

    def __init__(self, client_id: str, client_secret: str):
        super().__init__(client_id, client_secret)
        self.auth_url = "https://github.com/login/oauth/authorize"
        self.token_url = "https://github.com/login/oauth/access_token"
        self.userinfo_url = "https://api.github.com/user"
        self.useremail_url = "https://api.github.com/user/emails"
        self.scope = "user:email"

    def get_auth_url(self, redirect_uri: str, state: str) -> str:
        """获取 GitHub 授权 URL"""
        from urllib.parse import urlencode

        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": self.scope,
            "response_type": "code",
            "state": state
        }
        return f"{self.auth_url}?{urlencode(params)}"

    async def get_access_token(self, code: str, redirect_uri: str) -> str:
        """用授权码换取访问令牌"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                json={
                    "code": code,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uri": redirect_uri
                },
                headers={
                    "Accept": "application/json"
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("access_token")

    async def get_user_info(self, access_token: str) -> OAuthUserInfo:
        """获取 GitHub 用户信息"""
        async with httpx.AsyncClient() as client:
            # 获取用户基本信息
            response = await client.get(
                self.userinfo_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json"
                }
            )
            response.raise_for_status()
            data: Dict[str, Any] = response.json()

            # 获取用户邮箱（GitHub 需要单独请求）
            email = None
            email_response = await client.get(
                self.useremail_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json"
                }
            )
            if email_response.status_code == 200:
                emails = email_response.json()
                # 找到主邮箱
                for e in emails:
                    if e.get("primary") and e.get("verified"):
                        email = e.get("email")
                        break

            # GitHub 没有真实姓名，使用 username 作为 name
            return OAuthUserInfo(
                provider="github",
                provider_user_id=str(data.get("id")),
                email=email,
                name=data.get("name") or data.get("login"),
                avatar_url=data.get("avatar_url"),
                raw_data=data
            )
