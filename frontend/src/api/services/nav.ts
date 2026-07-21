import { request } from '../http'

/**
 * 获取管理导航列表
 * @returns
 */
export const getManageNavList = () => {
  return request({
    url: '/admin/navs/list',
    method: 'GET'
  })
}

/**
 * 创新导航
 * @param data
 * @returns
 */
export const createNav = (data: { label: string; type: string; value: string }) => {
  const formData = new FormData()
  formData.append('label', data.label)
  formData.append('type', data.type)
  formData.append('value', data.value)

  return request({
    url: '/admin/navs/add',
    method: 'POST',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 更新导航
 * @param data
 * @returns
 */
export const updateNav = (data: { id: number; label: string; type: string; value: string }) => {
  const formData = new FormData()
  formData.append('label', data.label)
  formData.append('type', data.type)
  formData.append('value', data.value)

  return request({
    url: `/admin/navs/edit/${data.id}`,
    method: 'POST',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 更新导航排序
 * @param data 导航排序数据
 * @returns Promise<any>
 */
export const updateNavSort = (ids: string[]) => {
  const formData = new FormData()
  formData.append('nav_ids', ids.join(','))
  return request({
    url: `/admin/navs/sortbatch`,
    method: 'POST',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 删除导航
 * @param id 导航ID
 * @returns Promise<any>
 */
export const deleteNav = (id: number) => {
  return request({
    url: `/admin/navs/delete/${id}`,
    method: 'DELETE'
  })
}

/**
 * 获取站点导航
 * @returns Promise<any>
 */
export const getSiteNavList = () => {
  return request({
    url: '/blog/navs',
    method: 'GET'
  })
}
