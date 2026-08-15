/**
 * 管理员操作日志 API（审计中间件自动写入，此处只读查询）
 */
import { request } from '../http'
import type { ApiResponse } from '../types'

/** 一条管理员操作日志 */
export interface AdminLogItem {
  id: number
  user_id?: number
  username?: string
  role?: string
  action: string
  method: string
  path: string
  detail?: Record<string, unknown> | null
  status_code?: number
  ip?: string
  user_agent?: string
  createtime: number
}

export interface AdminLogListParams {
  page?: number
  page_size?: number
  username?: string
  action?: string
  start_time?: number
  end_time?: number
}

/** 查询管理员操作日志 */
export const getAdminLogs = (params: AdminLogListParams = {}) => {
  return request<ApiResponse<AdminLogItem[]> & { total: number }>({
    url: '/admin/logs/list',
    method: 'GET',
    params
  })
}
