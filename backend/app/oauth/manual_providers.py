"""
非标准 OAuth provider（微信 / QQ）的手撸实现。

这两家不能直接用 authlib 的高层客户端（authorize_access_token）：
  - 微信: token 端点用 GET，appid/secret 放 query；redirect_uri 须拼 `#wechat_redirect`
  - QQ:   token 端点返回 application/x-www-form-urlencoded 文本（非 JSON）；
          /me 端点返回 `callback({...});` 形式的 JSONP，需剥外壳

因此 google/github/apple 继续走 authlib（registry.py），微信/QQ 走本模块的手撸流程。
state 经由 SessionMiddleware 的 session 校验，提供 CSRF 防护。
"""
import re
import json
import secrets
from typing import Optional
from urllib.parse import urlencode, parse_qs

import httpx

from app.config.oauth import OAuthConfig

MANUAL_PROVIDERS = {"wechat", "qq"}


# ==================== state 工具（session-based，CSRF 防护） ====================

_STATE_SESSION_KEY = "oauth_manual_state"


def issue_state(request, provider: str) -> str:
    """生成 state 并存入 session，与 provider 绑定。"""
    state = secrets.token_urlsafe(16)
    request.session[_STATE_SESSION_KEY] = {"provider": provider, "state": state}
    return state


def verify_state(request, state: Optional[str]) -> bool:
    """校验 query 中的 state 与 session 存储的是否一致（一次性，校验后即删）。"""
    saved = request.session.pop(_STATE_SESSION_KEY, None)
    if not saved or not state:
        return False
    return saved.get("state") == state and bool(saved.get("provider"))


# ==================== 微信（网站应用扫码登录） ====================

_WECHAT_AUTHORIZE = "https://open.weixin.qq.com/connect/qrconnect"
_WECHAT_TOKEN = "https://api.weixin.qq.com/sns/oauth2/access_token"
_WECHAT_USERINFO = "https://api.weixin.qq.com/sns/userinfo"


def _wechat_auth_url(redirect_uri: str, state: str) -> str:
    params = {
        "appid": OAuthConfig.WECHAT_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "snsapi_login",
        "state": state,
    }
    # 微信强制要求 redirect_uri 之后拼接 #wechat_redirect
    return f"{_WECHAT_AUTHORIZE}?{urlencode(params)}#wechat_redirect"


async def _wechat_token(code: str) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(_WECHAT_TOKEN, params={
            "appid": OAuthConfig.WECHAT_CLIENT_ID,
            "secret": OAuthConfig.WECHAT_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
        })
        resp.raise_for_status()
        data = resp.json()
    # 失败时微信返回 {"errcode": ..., "errmsg": ...}，成功时不含 errcode
    if "errcode" in data or "access_token" not in data:
        raise ValueError(f"微信换取 token 失败: {data}")
    return data  # {access_token, expires_in, refresh_token?, openid, unionid?, scope}


async def _wechat_userinfo(access_token: str, openid: str) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(_WECHAT_USERINFO, params={
            "access_token": access_token,
            "openid": openid,
        })
        resp.raise_for_status()
        data = resp.json()
    if "errcode" in data:
        raise ValueError(f"微信获取用户信息失败: {data}")
    return data  # {openid, nickname, headimgurl, unionid?, sex, province, ...}


# ==================== QQ（QQ 互联） ====================

_QQ_AUTHORIZE = "https://graph.qq.com/oauth2.0/authorize"
_QQ_TOKEN = "https://graph.qq.com/oauth2.0/token"
_QQ_ME = "https://graph.qq.com/oauth2.0/me"
_QQ_USERINFO = "https://graph.qq.com/user/get_user_info"


def _qq_auth_url(redirect_uri: str, state: str) -> str:
    params = {
        "client_id": OAuthConfig.QQ_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "get_user_info",
        "state": state,
    }
    return f"{_QQ_AUTHORIZE}?{urlencode(params)}"


async def _qq_token(code: str, redirect_uri: str) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(_QQ_TOKEN, data={
            "client_id": OAuthConfig.QQ_CLIENT_ID,
            "client_secret": OAuthConfig.QQ_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        })
        resp.raise_for_status()
        # QQ token 端点返回 urlencoded 文本（access_token=...&expires_in=...），非 JSON
        parsed = parse_qs(resp.text)
    access_token = parsed.get("access_token", [None])[0]
    if not access_token:
        raise ValueError(f"QQ 换取 token 失败: {resp.text}")
    return {
        "access_token": access_token,
        "refresh_token": parsed.get("refresh_token", [None])[0],
    }


async def _qq_userinfo(access_token: str) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        # 1. /me 返回 callback({...}); 形式的 JSONP，需剥外壳拿 openid
        me_resp = await client.get(_QQ_ME, params={"access_token": access_token})
        me_resp.raise_for_status()
        me = _parse_qq_callback(me_resp.text)
        openid = me.get("openid")
        if not openid:
            raise ValueError(f"QQ 获取 openid 失败: {me_resp.text}")

        # 2. 取用户资料
        info_resp = await client.get(_QQ_USERINFO, params={
            "access_token": access_token,
            "oauth_consumer_key": OAuthConfig.QQ_CLIENT_ID,
            "openid": openid,
        })
        info_resp.raise_for_status()
        info = info_resp.json()
    info["openid"] = openid
    return info  # {openid, nickname, figureurl_qq_1, ...}


def _parse_qq_callback(text: str) -> dict:
    """QQ 接口常返回 `callback( {...} );` 形式的 JSONP，剥成 dict。"""
    text = text.strip()
    m = re.match(r"^callback\s*\((.*)\)\s*;?\s*$", text, re.DOTALL)
    payload = m.group(1) if m else text
    return json.loads(payload)


# ==================== 统一入口 ====================

def build_manual_auth_url(provider: str, redirect_uri: str, state: str) -> str:
    """构造微信/QQ 的授权 URL。"""
    if provider == "wechat":
        return _wechat_auth_url(redirect_uri, state)
    if provider == "qq":
        return _qq_auth_url(redirect_uri, state)
    raise ValueError(f"未知的 manual provider: {provider}")


async def fetch_manual_profile(provider: str, code: str, redirect_uri: str) -> dict:
    """
    换取并归一化微信/QQ 的用户 profile。
    返回结构与 auth.py 的 _extract_oauth_profile 完全一致，便于复用 handle_oauth_user_login。
    """
    if provider == "wechat":
        token = await _wechat_token(code)
        access_token = token["access_token"]
        openid = token["openid"]
        info = await _wechat_userinfo(access_token, openid)
        return {
            # 优先用 unionid：同一开放平台主体下跨应用稳定；否则回退 openid
            "provider_user_id": token.get("unionid") or openid,
            "email": None,  # 微信不返回邮箱
            "name": info.get("nickname"),
            "avatar_url": info.get("headimgurl"),
            "access_token": access_token,
            "refresh_token": token.get("refresh_token"),
            "raw_data": {**token, "userinfo": info},
        }

    if provider == "qq":
        token = await _qq_token(code, redirect_uri)
        info = await _qq_userinfo(token["access_token"])
        return {
            "provider_user_id": info["openid"],
            "email": None,  # QQ 不返回邮箱
            "name": info.get("nickname"),
            "avatar_url": info.get("figureurl_qq_1") or info.get("figureurl"),
            "access_token": token["access_token"],
            "refresh_token": token.get("refresh_token"),
            "raw_data": info,
        }

    raise ValueError(f"未知的 manual provider: {provider}")
