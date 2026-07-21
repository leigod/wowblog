import { request } from '../http'

/**
 * 获取标签列表
 * @returns
 */
export const getTagList = (currentPage: number, pageSize: number, keyword: string) => {
  return request({
    url: `/admin/tag/list?currentpage=${currentPage}&pagesize=${pageSize}&keyword=${keyword}`,
    method: 'GET'
  })
}

/**
 * 创建标签
 * @param data
 * @returns
 */
export const createTag = (data: any) => {
  return request({
    url: '/admin/tag/add',
    method: 'POST',
    data
  })
}

/**
 * 编辑标签
 * @param id 标签ID
 * @param data 标签数据
 * @returns
 */
export const updateTag = (id: string, data: any) => {
  return request({
    url: `/admin/tag/edit/${id}`,
    method: 'POST',
    data
  })
}

/**
 * 更新标签状态
 * @param id 标签ID
 * @param status 标签状态
 * @returns
 */
export const updateTagStatus = (id: string, status: string) => {
  const formData = new FormData()
  formData.append('status', status)
  return request({
    url: `/admin/tag/status/${id}`,
    method: 'POST',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 删除标签
 * @param id 标签ID
 * @returns
 */
export const deleteTag = (id: string) => {
  return request({
    url: `/admin/tag/delete/${id}`,
    method: 'DELETE'
  })
}

/**
 * 获取标签详情
 * @param id 标签ID
 * @returns
 */
export const getTagInfo = (id: string) => {
  return request({
    url: `/admin/tag/detail/${id}`,
    method: 'GET'
  })
}

/**
 * 按关键字查询标签
 * @param keyword 标签名称
 * @returns
 */
export const searchTags = (keyword: string) => {
  return request({
    url: `/admin/tag/search/${keyword}`,
    method: 'GET'
  })
}

/**
 * 前端用户搜索标签（只返回正常状态的标签）
 * @param keyword 标签名称
 * @returns
 */
export const searchTagsFrontend = (keyword: string) => {
  return request({
    url: `/blog/tags/search/${keyword}`,
    method: 'GET'
  })
}
