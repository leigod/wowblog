import { request } from '../http'

/**
 * 通知接口类型定义
 */
export interface Notification {
  id: number
  user_id: number
  type: 'comment' | 'reply' | 'article_mention' | 'comment_mention' | 'like' | 'bookmark' | 'system'
  title: string
  content?: string
  actor_id?: number
  actor_name?: string
  actor_avatar?: string
  target_type?: string
  target_id?: number
  target_title?: string
  target_url?: string
  is_read: boolean
  created_at: number
}

export interface NotificationListItem {
  id: number
  type: string
  title: string
  content?: string
  actor_id?: number
  actor_name?: string
  actor_avatar?: string
  target_url?: string
  is_read: boolean
  is_important?: boolean
  created_at: number
}

/**
 * 获取通知列表
 */
export const getNotifications = (params?: {
  unread_only?: boolean
  page?: number
  page_size?: number
}) => {
  return request<{ code: number; msg?: string; data: NotificationListItem[] }>({
    url: '/notifications',
    method: 'GET',
    params
  })
}

/**
 * 获取未读通知数量
 */
export const getUnreadCount = () => {
  return request<{ code: number; data: number }>({
    url: '/notifications/unread-count',
    method: 'GET'
  })
}

/**
 * 标记单条通知为已读
 */
export const markAsRead = (notificationId: number) => {
  return request<{ code: number; msg?: string }>({
    url: `/notifications/${notificationId}/read`,
    method: 'POST'
  })
}

/**
 * 标记所有通知为已读
 */
export const markAllAsRead = () => {
  return request<{ code: number; msg?: string }>({
    url: '/notifications/read-all',
    method: 'POST'
  })
}

/**
 * 删除通知
 */
export const deleteNotification = (notificationId: number) => {
  return request<{ code: number; msg?: string }>({
    url: `/notifications/${notificationId}`,
    method: 'DELETE'
  })
}

// 默认导出
export default {
  getNotifications,
  getUnreadCount,
  markAsRead,
  markAllAsRead,
  deleteNotification
}
