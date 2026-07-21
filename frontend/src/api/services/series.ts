import { request } from '../http'

/**
 * 获取管理系列列表
 * @returns
 */
export const getManageSeriesList = () => {
  return request({
    url: '/admin/series/list',
    method: 'GET'
  })
}

/**
 * 创建系列
 * @param data
 * @returns
 */
export const createSeries = (data: any) => {
  return request({
    url: '/admin/series/add',
    method: 'POST',
    data
  })
}

/**
 * 编辑系列
 * @param id 系列ID
 * @param data 系列数据
 * @returns
 */
export const updateSeries = (id: string, data: any) => {
  return request({
    url: `/admin/series/edit/${id}`,
    method: 'POST',
    data
  })
}

/**
 * 删除系列
 * @param id 系列ID
 * @returns
 */
export const deleteSeries = (id: string) => {
  return request({
    url: `/admin/series/delete/${id}`,
    method: 'DELETE'
  })
}

/**
 * 获取系列详情
 * @param id 系列ID
 * @returns
 */
export const getSeriesInfo = (id: string) => {
  return request({
    url: `/admin/series/detail/${id}`,
    method: 'GET'
  })
}

/**
 * 更新导航排序
 * @param data 导航排序数据
 * @returns Promise<any>
 */
export const updateSeriesSort = (ids: string[]) => {
  const formData = new FormData()
  formData.append('series_ids', ids.join(','))
  return request({
    url: `/admin/series/sortbatch`,
    method: 'POST',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 获取系列列表（公开接口，供作者和协作者使用）
 * @returns
 */
export const getSeriesList = () => {
  return request({
    url: '/blog/series/list',
    method: 'GET'
  })
}
