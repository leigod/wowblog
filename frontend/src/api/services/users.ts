import { request } from '../http'

/**
 * 用户接口类型定义
 */
export interface User {
  id: number
  username: string
  full_name?: string
  email?: string
  mobile?: string
  role: 'Admin' | 'Editor' | 'Author' | 'Contributor' | 'User'
  status: 'normal' | 'disabled'
  profile_image?: string
  profile_bio?: string
  about?: string
  gender?: number
  articles_count?: number
  comments_count?: number
  created_at: number
  updated_at?: number
}

export interface UserListResponse {
  users: User[]
  total: number
  page: number
  page_size: number
}

export interface UpdateUserStatusRequest {
  status: 'normal' | 'disabled'
}

export interface UpdateUserRoleRequest {
  role: 'Admin' | 'Editor' | 'Author' | 'Contributor' | 'User'
}

export interface SendUserMessageRequest {
  type: 'system' | 'reminder'
  title: string
  content: string
}

/**
 * 获取用户列表
 */
export const getUserList = (params?: {
  page?: number
  page_size?: number
  status?: string
  keyword?: string
}) => {
  return request<{ code: number; msg?: string; data: UserListResponse }>({
    url: '/admin/users',
    method: 'GET',
    params
  })
}

/**
 * 获取用户详情
 */
export const getUserDetail = (userId: number) => {
  return request<{ code: number; msg?: string; data: User }>({
    url: `/admin/users/${userId}`,
    method: 'GET'
  })
}

/**
 * 更新用户状态
 */
export const updateUserStatus = (userId: number, data: UpdateUserStatusRequest) => {
  return request<{ code: number; msg?: string }>({
    url: `/admin/users/${userId}/status`,
    method: 'PUT',
    data
  })
}

/**
 * 更新用户角色
 */
export const updateUserRole = (userId: number, data: UpdateUserRoleRequest) => {
  return request<{ code: number; msg?: string }>({
    url: `/admin/users/${userId}/role`,
    method: 'PUT',
    data
  })
}

/**
 * 重置用户密码
 */
export const resetUserPassword = (userId: number) => {
  return request<{ code: number; msg?: string; data?: { new_password?: string } }>({
    url: `/admin/users/${userId}/reset-password`,
    method: 'POST'
  })
}

/**
 * 删除用户
 */
export const deleteUser = (userId: number) => {
  return request<{ code: number; msg?: string }>({
    url: `/admin/users/${userId}`,
    method: 'DELETE'
  })
}

/**
 * 发送用户消息
 */
export const sendUserMessage = (userId: number, data: SendUserMessageRequest) => {
  return request<{ code: number; msg?: string }>({
    url: `/admin/users/${userId}/message`,
    method: 'POST',
    data
  })
}

// 默认导出
export default {
  getUserList,
  getUserDetail,
  updateUserStatus,
  updateUserRole,
  resetUserPassword,
  deleteUser,
  sendUserMessage
}
