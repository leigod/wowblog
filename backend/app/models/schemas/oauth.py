"""
OAuth 相关的 Schema 定义
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any


class OAuthProvider(BaseModel):
    """OAuth提供商信息"""
    provider: str  # google, github, apple, wechat, qq, alipay
    provider_user_id: str
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None


class OAuthBindRequest(BaseModel):
    """绑定OAuth账号请求"""
    provider: str
    provider_user_id: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None


class OAuthUserInfo(BaseModel):
    """OAuth用户信息"""
    provider: str
    provider_user_id: str
    email: Optional[str] = None
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None


class OAuthCallbackRequest(BaseModel):
    """OAuth回调请求"""
    code: str
    state: Optional[str] = None
