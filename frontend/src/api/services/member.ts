/**
 * 成员管理相关API服务
 */
import { request } from '../http'

/**
 * 获取管理成员列表
 * @returns
 */
export const getManageMemberList = () => {
  return request({
    url: '/admin/members/list',
    method: 'GET'
  })
}

/**
 * 添加管理成员
 * @param data
 * @returns
 */
export const addManageMember = (data: any) => {
  return request({
    url: '/admin/members/add',
    method: 'POST',
    data
  })
}

/**
 * 更新成员显示状态
 * @param id 成员ID
 * @param status 状态
 * @returns
 */
export const updateMemberStatus = (id: string, status: string) => {
  const formData = new FormData()
  formData.append('status', status)
  return request({
    url: `/admin/members/status/${id}`,
    method: 'POST',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 更新成员对外公开状态
 * @param id 成员ID
 * @param visible 公开状态
 * @returns
 */
export const updateMemberVisible = (id: string, visible: string) => {
  const formData = new FormData()
  formData.append('visible', visible)
  return request({
    url: `/admin/members/visible/${id}`,
    method: 'POST',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 删除成员
 * @param id 成员ID
 * @returns
 */
export const deleteMember = (id: string) => {
  return request({
    url: `/admin/members/delete/${id}`,
    method: 'DELETE'
  })
}

/**
 * 更新成员
 * @param id 成员ID
 * @param data 成员数据 包含username,full_name,profile_image,gender,email,mobile,role
 * @returns
 */
export const updateMember = (id: string, data: any) => {
  return request({
    url: `/admin/members/update/${id}`,
    method: 'POST',
    data
  })
}

/**
 * 获取成员信息
 * @param id 成员ID
 * @returns
 */
export const getMemberInfo = (id: string) => {
  return request({
    url: `/admin/members/info/${id}`,
    method: 'GET'
  })
}

/**
 * 查询作者
 */
export const searchAuthors = (keyword: string, author_id: number) => {
  return request({
    url: `/admin/members/searchauthor/${author_id}/${keyword}`,
    method: 'GET'
  })
}

/**
 * 查询共同创作者
 */
export const searchCoAuthors = (keyword: string) => {
  return request({
    url: `/admin/members/searchcoauthor/${keyword}`,
    method: 'GET'
  })
}

/**
 * 搜索可提及的用户（用于编辑器 Mention 功能）
 * @param query 搜索关键词（用户名或全名）
 */
export const searchUsersForMention = (query: string) => {
  // 添加空值检查，避免发送空请求
  if (!query || query.trim().length === 0) {
    return Promise.resolve({ data: [] })
  }
  return request({
    url: `/users/search/${encodeURIComponent(query)}`,
    method: 'GET'
  })
}
