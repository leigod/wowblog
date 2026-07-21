import { request } from '../http'

/**
 * 获取管理导航列表
 * @returns
 */
export const getManagePageList = () => {
  return request({
    url: '/admin/page/list',
    method: 'GET'
  })
}

/**
 * 创建页面
 * @param data
 * @returns
 */
export const createPage = (data: any) => {
  return request({
    url: '/admin/page/add',
    method: 'POST',
    data
  })
}

/**
 * 编辑页面
 * @param id 页面ID
 * @param data 页面数据
 * @returns
 */
export const updatePage = (id: string, data: any) => {
  return request({
    url: `/admin/page/edit/${id}`,
    method: 'POST',
    data
  })
}

/**
 * 更新页面显示状态
 * @param id 页面ID
 * @param data 页面数据
 * @returns
 */
export const updatePageStatus = (id: string, status: string) => {
  const formData = new FormData()
  formData.append('status', status)
  return request({
    url: `/admin/page/status/${id}`,
    method: 'POST',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 删除页面
 * @param id 页面ID
 * @returns
 */
export const deletePage = (id: string) => {
  return request({
    url: `/admin/page/delete/${id}`,
    method: 'DELETE'
  })
}

/**
 * 获取页面详情
 * @param id 页面ID
 * @returns
 */
export const getPageInfo = (id: string) => {
  return request({
    url: `/admin/page/detail/${id}`,
    method: 'GET'
  })
}
