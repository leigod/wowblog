/**
 * 用户相关API服务
 */
import { request } from '../http'

/**
 * 用户信息接口定义
 */
export interface UserInfo {
  id: number
  username: string
  full_name?: string
  nickname?: string
  avatar?: string
  profile_image?: string
  email?: string
  phone?: string
  mobile?: string
  about?: string
  profile_bio?: string
  profile_tagline?: string
  techStack?: string[]
  tech_stack?: string[]
  services?: string[]
  available_for?: string
  location?: string
  gender?: number
  school?: string
  social?: {
    github?: string
    twitter?: string
    linkedin?: string
    instagram?: string
    dribbble?: string
    website?: string
  }
  social_profiles?: Record<string, any>
  followers_count?: number
  createdAt?: string
  createtime?: number
  updatedAt?: string
  updatetime?: number
  status?: string
  role?: string
  [key: string]: any
}

/**
 * 获取用户信息
 * @returns Promise<UserInfo>
 */
export const getUserInfo = (): Promise<UserInfo> => {
  return request({
    url: '/user/info',
    method: 'GET'
  })
}

/**
 * 更新用户信息
 * @param data 用户信息数据
 * @returns Promise<any>
 */
export const updateUserInfo = (data: Partial<UserInfo>): Promise<any> => {
  return request({
    url: '/users/profile/update',
    method: 'PUT',
    data
  })
}

/**
 * 更新用户头像
 * @param file 头像文件
 * @returns Promise<any>
 */
export const updateUserAvatar = (file: File): Promise<any> => {
  const formData = new FormData()
  formData.append('avatar', file)

  return request({
    url: '/user/avatar',
    method: 'POST',
    data: formData,
    headers: {
      // 删除 Content-Type，让浏览器自动设置 multipart/form-data boundary
      'Content-Type': undefined
    }
  })
}

/**
 * 修改密码
 * @param data 密码数据
 * @returns Promise<any>
 */
export const changePassword = (data: {
  old_password: string
  new_password: string
}): Promise<any> => {
  return request({
    url: '/users/change-password',
    method: 'POST',
    data
  })
}

/**
 * 用户登录
 * @param loginData
 * @returns
 */
export const login = (loginData: { username: string; password: string }): Promise<any> => {
  // 后端使用 OAuth2PasswordRequestForm，必须使用 form-data 格式
  const formData = new FormData()
  formData.append('username', loginData.username)
  formData.append('password', loginData.password)

  return request({
    url: '/login',
    method: 'POST',
    data: formData,
    headers: {
      // 删除 Content-Type，让浏览器自动设置 multipart/form-data boundary
      'Content-Type': undefined
    }
  })
}

/**
 * 获取当前登录用户信息
 * @returns
 */
export const getUserMe = (): Promise<UserInfo> => {
  return request({
    url: '/users/me',
    method: 'GET'
  })
}

/**
 * 用户注册
 * @param registerData 注册数据
 * @returns Promise<any>
 */
export const register = (registerData: {
  username: string
  password: string
  full_name: string
  email?: string
  mobile?: string
  profile_image?: string
  gender?: number
}): Promise<any> => {
  // 后端使用 Form()，必须使用 form-data 格式
  const formData = new FormData()
  formData.append('username', registerData.username)
  formData.append('password', registerData.password)
  formData.append('full_name', registerData.full_name)

  // 添加可选字段
  if (registerData.email) {
    formData.append('email', registerData.email)
  }
  if (registerData.mobile) {
    formData.append('mobile', registerData.mobile)
  }
  if (registerData.profile_image) {
    formData.append('profile_image', registerData.profile_image)
  }
  if (registerData.gender !== undefined) {
    formData.append('gender', registerData.gender.toString())
  }

  return request({
    url: '/users/register',
    method: 'POST',
    data: formData,
    headers: {
      // 删除 Content-Type，让浏览器自动设置 multipart/form-data boundary
      'Content-Type': undefined
    }
  })
}

/**
 * 获取临时token
 */
export const getTempToken = (): Promise<any> => {
  return request({
    url: '/get_temp_token',
    method: 'GET'
  })
}

/**
 * 根据用户名获取用户信息
 * @param username 用户名
 * @returns Promise<UserInfo>
 */
export const getUserByUsername = (username: string): Promise<UserInfo> => {
  return request({
    url: `/users/profile/${username}`,
    method: 'GET'
  })
}

/**
 * 用户活动数据接口定义
 */
export interface UserActivity {
  id: number
  type: string
  target_id: number
  status: number
  createtime: number
  updatetime: number
}

/**
 * 用户时间线活动接口定义
 */
export interface TimelineActivity {
  type: 'article' | 'like' | 'bookmark' | 'comment'
  id?: number
  article_id?: number
  title?: string
  slug?: string
  article_title?: string
  article_slug?: string
  comment_content?: string
  action: string
  time: number
}

/**
 * 用户时间线响应接口定义
 */
export interface TimelineResponse {
  activities: TimelineActivity[]
  total: number
  has_more: boolean
}

/**
 * 获取用户最近活动（时间线）
 * @param username 用户名
 * @param limit 返回数量限制
 * @param offset 偏移量
 * @returns Promise<TimelineResponse>
 */
export const getUserActivity = (
  username: string,
  limit: number = 10,
  offset: number = 0
): Promise<{ code: number; data: TimelineResponse }> => {
  return request({
    url: `/blog/users/${username}/activity?limit=${limit}&offset=${offset}`,
    method: 'GET'
  })
}

/**
 * 用户隐私设置接口定义
 */
export interface UserPrivacySettings {
  privacy_show_bookmarks: number
  privacy_show_likes: number
  privacy_show_comments: number
  privacy_show_views: number
}

/**
 * 获取用户隐私设置
 * @returns Promise<{code: number, data: UserPrivacySettings}>
 */
export const getUserPrivacy = (): Promise<{ code: number; data: UserPrivacySettings }> => {
  return request({
    url: '/blog/users/privacy',
    method: 'GET'
  })
}

/**
 * 更新用户隐私设置
 * @param data 隐私设置数据
 * @returns Promise<{code: number, data: UserPrivacySettings}>
 */
export const updateUserPrivacy = (
  data: Partial<UserPrivacySettings>
): Promise<{ code: number; data: UserPrivacySettings }> => {
  return request({
    url: '/blog/users/privacy',
    method: 'PUT',
    data
  })
}

/**
 * 检查用户关注状态
 * @param username 目标用户名
 * @returns Promise<{is_following: boolean}>
 */
export const checkUserFollowStatus = (username: string): Promise<any> => {
  return request({
    url: `/users/${username}/follow-status`,
    method: 'GET'
  })
}

/**
 * 关注/取消关注用户
 * @param username 目标用户名
 * @returns Promise<{is_following: boolean, message: string}>
 */
export const toggleUserFollow = (username: string): Promise<any> => {
  return request({
    url: `/users/${username}/follow`,
    method: 'POST'
  })
}

/**
 * @mention 用户搜索结果接口定义
 */
export interface MentionUser {
  id: number
  username: string
  full_name?: string
  profile_image?: string
}

/**
 * 搜索用户（用于 @mention）
 * @param query 搜索关键词
 * @returns Promise<{code: number, data: MentionUser[]}>
 */
export const searchUsersForMention = (query: string): Promise<{ code: number; data: MentionUser[] }> => {
  // 添加空值检查，避免发送空请求
  if (!query || query.trim().length === 0) {
    return Promise.resolve({ code: 1, data: [] })
  }
  return request({
    url: `/users/search/${encodeURIComponent(query)}`,
    method: 'GET'
  })
}

/**
 * 重置密码请求接口定义
 */
export interface ResetPasswordRequest {
  username: string
  language?: string
}

/**
 * 重置用户密码
 * @param data 重置密码请求数据
 * @returns Promise<any>
 */
export const resetPassword = (data: ResetPasswordRequest): Promise<any> => {
  return request({
    url: '/users/reset-password',
    method: 'POST',
    data
  })
}
