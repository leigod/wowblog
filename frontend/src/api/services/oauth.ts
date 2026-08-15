/**
 * OAuth 第三方账号绑定管理 API
 *
 * 注意：与登录用的 exchangeOAuthToken（在 auth.ts）区分：
 *   - 登录中转：auth.ts 的 exchangeOAuthToken
 *   - 已登录用户的绑定查询/解绑：本文件
 */
import { request } from '../http'
import type { ApiResponse } from '../types'

/** 一个已绑定的第三方账号（列表项，不含敏感字段） */
export interface OAuthBinding {
  provider: string
  email?: string
  avatar_url?: string
  createtime?: number
}

/** 获取当前用户已绑定的第三方账号列表 */
export const getOAuthBindings = () => {
  return request<ApiResponse<OAuthBinding[]>>({
    url: '/auth/oauth/bindings',
    method: 'GET'
  })
}

/** 解除当前用户与指定第三方账号的绑定 */
export const unlinkOAuth = (provider: string) => {
  return request<ApiResponse<{ unlinked: boolean }>>({
    url: `/auth/oauth/bindings/${provider}`,
    method: 'DELETE'
  })
}

/**
 * 发起主动绑定：后端验证当前用户 + 写 session 意图（oauth_intent=bind），返回授权 URL。
 * 前端拿到后再 window.location 跳该 URL（window.location 不带 Authorization header，
 * 故必须先用本接口带 token 设好 session 意图）。
 */
export const initiateOAuthBind = (provider: string) => {
  return request<ApiResponse<{ authorize_url: string }>>({
    url: `/auth/oauth/bind/${provider}`,
    method: 'POST'
  })
}
