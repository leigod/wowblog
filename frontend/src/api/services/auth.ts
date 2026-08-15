/**
 * 前端用户认证相关 API
 */
import { request } from '../http'
import type { ApiResponse } from '../types'

/**
 * 前端登录请求参数
 */
export interface FrontLoginRequest {
  username: string  // 可以是邮箱或用户名
  password: string
  remember?: boolean
}

/**
 * 前端注册请求参数
 */
export interface FrontRegisterRequest {
  email: string
  username: string
  password: string
  full_name?: string
}

/**
 * Token 响应
 */
export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
}

/**
 * 用户信息响应
 */
export interface UserInfo {
  id: number
  username: string
  email?: string
  full_name?: string
  profile_image?: string
  role: string
  status: string
}

/**
 * 前端用户登录
 */
export const frontLoginApi = (data: FrontLoginRequest) => {
  return request<ApiResponse<TokenResponse>>({
    url: '/auth/login',
    method: 'POST',
    data
  })
}

/**
 * 前端用户注册
 */
export const frontRegisterApi = (data: FrontRegisterRequest, tempToken: string) => {
  return request<ApiResponse<TokenResponse>>({
    url: '/auth/register',
    method: 'POST',
    data,
    headers: {
      Authorization: `Bearer ${tempToken}`
    }
  })
}

/**
 * 获取临时token（用于注册等操作）
 */
export const getTempTokenApi = () => {
  return request<ApiResponse<{ access_token: string; token_type: string }>>({
    url: '/auth/temp-token',
    method: 'GET'
  })
}

/**
 * 获取当前用户信息
 */
export const getCurrentUserInfo = () => {
  return request<ApiResponse<UserInfo>>({
    url: '/auth/me',
    method: 'GET'
  })
}

/**
 * 登出
 */
export const frontLogoutApi = () => {
  return request<ApiResponse<{ logged_out: boolean }>>({
    url: '/auth/logout',
    method: 'POST'
  })
}

/**
 * OAuth 回调后换取 access_token
 *
 * 后端在 OAuth 回调成功时把 access_token 写入 httpOnly 短期 cookie（oauth_token），
 * 前端调本接口（依赖 axios withCredentials 携带 cookie）一次性取出 token，后端随即删除 cookie。
 * 前端拿到后存入 localStorage，走与普通登录一致的后续流程。
 */
export const exchangeOAuthToken = () => {
  return request<ApiResponse<{ access_token: string; token_type: string }>>({
    url: '/auth/oauth/session',
    method: 'GET'
  })
}
