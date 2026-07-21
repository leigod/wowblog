/**
 * 成员邀请相关API服务
 */
import { request } from '../http'

// ==================== 类型定义 ====================

/**
 * 邀请创建请求
 */
export interface InvitationCreateRequest {
  email: string
  role: 'Admin' | 'Editor' | 'Contributor'
  language?: 'zh-CN' | 'en-US'
}

/**
 * 邀请列表项
 */
export interface InvitationListItem {
  id: number
  email: string
  role: string
  status: 'pending' | 'accepted' | 'cancelled' | 'expired'
  language: string
  created_at: number
  expires_at: number
  accepted_at?: number
  invited_by: number
  admin_name?: string
  blog_name?: string
}

/**
 * 邀请列表响应
 */
export interface InvitationListResponse {
  code: number
  msg?: string
  invitations: InvitationListItem[]
  total: number
  page: number
  page_size: number
}

/**
 * 邀请验证响应
 */
export interface InvitationVerifyResponse {
  valid: boolean
  message: string
  email?: string
  role?: string
  blog_name?: string
  admin_name?: string
}

/**
 * 邮件设置
 */
export interface EmailSettings {
  id: number
  provider: string
  smtp_host: string
  smtp_port: number
  smtp_user?: string
  from_email: string
  from_name?: string
  use_tls: boolean
  is_active: boolean
  has_password?: boolean
}

// ==================== 邀请管理 ====================

/**
 * 创建邀请并发送邮件
 */
export const createInvitation = (data: InvitationCreateRequest) => {
  return request({
    url: '/member-invitations/admin/invite',
    method: 'POST',
    data
  })
}

/**
 * 获取邀请列表
 */
export const getInvitationList = (params: {
  page?: number
  page_size?: number
  status?: string
} = {}) => {
  return request<InvitationListResponse>({
    url: '/member-invitations/admin/list',
    method: 'GET',
    params
  })
}

/**
 * 重新发送邀请邮件
 */
export const resendInvitationEmail = (invitationId: number) => {
  return request({
    url: `/member-invitations/admin/${invitationId}/resend`,
    method: 'POST'
  })
}

/**
 * 取消邀请
 */
export const cancelInvitation = (invitationId: number) => {
  return request({
    url: `/member-invitations/admin/${invitationId}/cancel`,
    method: 'POST'
  })
}

/**
 * 获取待处理邀请数量
 */
export const getPendingInvitationsCount = () => {
  return request({
    url: '/member-invitations/pending-count',
    method: 'GET'
  })
}

// ==================== 公开接口 ====================

/**
 * 验证邀请令牌
 */
export const verifyInvitation = (token: string) => {
  return request<InvitationVerifyResponse>({
    url: `/member-invitations/verify/${token}`,
    method: 'GET'
  })
}

/**
 * 接受邀请
 */
export const acceptInvitation = (token: string) => {
  return request({
    url: `/member-invitations/accept/${token}`,
    method: 'POST'
  })
}

// ==================== 邮件设置 ====================

/**
 * 获取邮件设置列表
 */
export const getEmailSettings = () => {
  return request({
    url: '/member-invitations/admin/email-settings',
    method: 'GET'
  })
}

/**
 * 更新邮件设置
 */
export const updateEmailSettings = (settingsId: number, data: {
  provider: string
  smtp_host: string
  smtp_port?: number
  smtp_user?: string
  smtp_pass?: string
  from_email: string
  from_name?: string
  use_tls?: boolean
  is_active?: boolean
}) => {
  return request({
    url: `/member-invitations/admin/email-settings/${settingsId}/update`,
    method: 'POST',
    data
  })
}

/**
 * 获取 SMTP 预设配置
 */
export const getSmtpPresets = () => {
  return request({
    url: '/member-invitations/admin/smtp-presets',
    method: 'GET'
  })
}
