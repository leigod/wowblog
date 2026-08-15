/**
 * 管理后台评论管理相关API服务
 */
import { request } from '../http'

// ==================== 类型定义 ====================

/**
 * 评论列表项
 */
export interface CommentListItem {
  id: number
  user_id: number
  username: string
  user_avatar?: string
  article_id?: number
  article_title?: string
  article_slug?: string
  comment: string
  status: 'normal' | 'hidden' | 'deleted'
  audit_status: 'pending' | 'approved' | 'rejected'
  ip?: string
  created_at: number
  updated_at?: number
  replys: number
  likes: number
  parent_id?: number
  sensitive_words?: string
}

/**
 * 评论列表请求参数
 */
export interface CommentListRequest {
  page?: number
  page_size?: number
  status?: string
  audit_status?: string
  user_id?: number
  article_id?: number
  keyword?: string
  start_date?: string
  end_date?: string
}

/**
 * 评论列表响应
 */
export interface CommentListResponse {
  code: number
  msg?: string
  list: CommentListItem[]
  total: number
  page: number
  page_size: number
}

/**
 * 评论统计数据
 */
export interface CommentStatisticsData {
  total_comments: number
  pending_audit: number
  today_comments: number
  week_comments: number
  hidden_comments: number
  deleted_comments: number
  sensitive_detected: number
}

/**
 * 评论统计响应
 */
export interface CommentStatisticsResponse {
  code: number
  msg?: string
  data: CommentStatisticsData
}

/**
 * 敏感词信息
 */
export interface SensitiveWord {
  id: number
  word: string
  type: 'banned' | 'review' | 'replace'
  replacement?: string
  category?: string
  status: 'active' | 'inactive'
  created_at: number
  created_by?: number
}

/**
 * 黑名单信息
 */
export interface BlacklistItem {
  id: number
  user_id: number
  username?: string
  user_avatar?: string
  type: string
  reason?: string
  note?: string
  expire_at?: number
  status: string
  created_at: number
  admin_name?: string
}

// ==================== 评论管理 ====================

/**
 * 获取评论列表
 */
export const getCommentList = (params: CommentListRequest = {}) => {
  return request<CommentListResponse>({
    url: '/admin/comments/list',
    method: 'GET',
    params
  })
}

/**
 * 更新评论状态
 */
export const updateCommentStatus = (commentId: number, data: { status: string; reason?: string }) => {
  return request({
    url: `/admin/comments/${commentId}/status`,
    method: 'POST',
    data
  })
}

/**
 * 更新评论审核状态
 */
export const updateCommentAudit = (commentId: number, data: { audit_status: string; reason?: string }) => {
  return request({
    url: `/admin/comments/${commentId}/audit`,
    method: 'POST',
    data
  })
}

/**
 * 批量操作评论
 */
export const batchOperation = (data: { action: string; comment_ids: number[]; reason?: string }) => {
  return request({
    url: '/admin/comments/batch',
    method: 'POST',
    data
  })
}

/**
 * 获取评论统计数据
 */
export const getCommentStatistics = () => {
  return request<CommentStatisticsResponse>({
    url: '/admin/comments/statistics',
    method: 'GET'
  })
}

// ==================== 敏感词管理 ====================

/**
 * 获取敏感词列表
 */
export const getSensitiveWords = (params: { page?: number; page_size?: number; keyword?: string; type?: string; status?: string } = {}) => {
  return request({
    url: '/admin/comments/sensitive-words/list',
    method: 'GET',
    params
  })
}

/**
 * 创建敏感词
 */
export const createSensitiveWord = (data: { word: string; type?: string; replacement?: string; category?: string }) => {
  return request({
    url: '/admin/comments/sensitive-words/create',
    method: 'POST',
    data
  })
}

/**
 * 更新敏感词
 */
export const updateSensitiveWord = (wordId: number, data: Partial<SensitiveWord>) => {
  return request({
    url: `/admin/comments/sensitive-words/${wordId}/update`,
    method: 'POST',
    data
  })
}

/**
 * 删除敏感词
 */
export const deleteSensitiveWord = (wordId: number) => {
  return request({
    url: `/admin/comments/sensitive-words/${wordId}/delete`,
    method: 'DELETE'
  })
}

// ==================== 黑名单管理 ====================

/**
 * 获取黑名单列表
 */
export const getBlacklist = (params: { page?: number; page_size?: number; type?: string; status?: string; keyword?: string } = {}) => {
  return request({
    url: '/admin/comments/blacklist/list',
    method: 'GET',
    params
  })
}

/**
 * 创建黑名单
 */
export const createBlacklist = (data: { user_id: number; type?: string; reason?: string; note?: string; expire_at?: number }) => {
  return request({
    url: '/admin/comments/blacklist/create',
    method: 'POST',
    data
  })
}

/**
 * 更新黑名单
 */
export const updateBlacklist = (blacklistId: number, data: { status?: string; expire_at?: number; note?: string }) => {
  return request({
    url: `/admin/comments/blacklist/${blacklistId}/update`,
    method: 'POST',
    data
  })
}

/**
 * 删除黑名单
 */
export const deleteBlacklist = (blacklistId: number) => {
  return request({
    url: `/admin/comments/blacklist/${blacklistId}/delete`,
    method: 'DELETE'
  })
}

// ==================== 系统设置 ====================

// 注：getCommentSettings / updateSystemSetting 已删除——wb_system_settings 与 wb_config 重复，后端端点已移除。

/**
 * 批量导入敏感词（纯文本，一行一条：词 / 词=>替换词 / 词@@review）
 */
export const importSensitiveWords = (content: string, category?: string) => {
  return request({
    url: '/admin/comments/sensitive-words/import',
    method: 'POST',
    data: { content, category }
  })
}

/**
 * 导出全部敏感词（返回纯文本）。
 * 用 fetch 而非统一 http 实例：导出是 text/plain 响应、无 code 信封，
 * 走 axios 响应拦截器会被当作业务错误。
 */
export const exportSensitiveWords = async (): Promise<string> => {
  const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token')
  const base = import.meta.env.VITE_API_BASE_URL || '/api'
  const resp = await fetch(`${base}/admin/comments/sensitive-words/export`, {
    headers: token ? { Authorization: `Bearer ${token}` } : undefined
  })
  if (!resp.ok) {
    throw new Error(`export failed: ${resp.status}`)
  }
  return resp.text()
}
