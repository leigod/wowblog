"""
Apple Sign In Provider 实现
"""
import httpx
import json
import time
from typing import Dict, Any, Optional
from jwt import PyJWKClient
import jwt
from .base import BaseOAuthProvider, OAuthUserInfo


class AppleOAuthProvider(BaseOAuthProvider):
    """Apple Sign In 提供商"""

    def __init__(
        self,
        client_id: str,
        team_id: str,
        key_id: str,
        private_key: str
    ):
        # Apple 不使用 client_secret，而是使用其他参数
        super().__init__(client_id, "")
        self.team_id = team_id
        self.key_id = key_id
        self.private_key = private_key
        self.auth_url = "https://appleid.apple.com/auth/authorize"
        self.token_url = "https://appleid.apple.com/auth/token"
        self.scope = "name email"

    def get_auth_url(self, redirect_uri: str, state: str) -> str:
        """获取 Apple 授权 URL"""
        from urllib.parse import urlencode

        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": self.scope,
            "response_type": "code",
            "state": state,
            "response_mode": "form_post"
        }
        return f"{self.auth_url}?{urlencode(params)}"

    async def get_access_token(self, code: str, redirect_uri: str) -> str:
        """用授权码换取访问令牌"""
        # 生成客户端密钥
        client_secret = self._generate_client_secret()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    "code": code,
                    "client_id": self.client_id,
                    "client_secret": client_secret,
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

    def _generate_client_secret(self) -> str:
        """生成 Apple 客户端密钥（JWT）"""
        headers = {
            "alg": "ES256",
            "kid": self.key_id
        }

        payload = {
            "iss": self.team_id,
            "iat": int(time.time()),
            "exp": int(time.time()) + 15777000,  # 6个月
            "aud": "https://appleid.apple.com",
            "sub": self.client_id
        }

        return jwt.encode(
            payload,
            self.private_key,
            algorithm="ES256",
            headers=headers
        )

    async def get_user_info(self, access_token: str) -> OAuthUserInfo:
        """获取 Apple 用户信息"""
        # Apple 的用户信息在授权回调中直接返回
        # 这里使用 access_token 验证并获取基本信息
        try:
            # 解码 id_token（如果有的话）
            # Apple 的 access_token 本身不包含用户信息
            # 用户信息需要在回调时从 'user' 参数中获取
            # 这里返回一个基础信息
            return OAuthUserInfo(
                provider="apple",
                provider_user_id="",  # 需要从 id_token 中获取
                email=None,
                name=None,
                avatar_url=None,
                raw_data={}
            )
        except Exception as e:
            # 如果验证失败，返回基本信息
            return OAuthUserInfo(
                provider="apple",
                provider_user_id="",
                email=None,
                name=None,
                avatar_url=None,
                raw_data={"error": str(e)}
            )

    async def verify_id_token(self, id_token: str) -> OAuthUserInfo:
        """
        验证 Apple id_token 并获取用户信息

        Apple 的用户信息主要通过 id_token 传递
        """
        try:
            # 获取 Apple 的公钥
            jwks_client = PyJWKClient("https://appleid.apple.com/auth/keys")
            signing_key = jwks_client.get_signing_key_from_jwt(id_token)

            # 解码并验证
            data = jwt.decode(
                id_token,
                key=signing_key.key,
                algorithms=["ES256"],
                audience=self.client_id,
                issuer="https://appleid.apple.com"
            )

            return OAuthUserInfo(
                provider="apple",
                provider_user_id=data.get("sub"),  # Apple 的唯一用户ID
                email=data.get("email"),
                name=None,  # Apple 只在首次授权时返回 name
                avatar_url=None,
                raw_data=data
            )
        except Exception as e:
            raise Exception(f"Failed to verify Apple id_token: {str(e)}")
