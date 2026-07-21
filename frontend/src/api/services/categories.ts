import { request } from '../http'

/**
 * 获取管理分类列表
 * @returns
 */
export const getManageCategoryList = () => {
  return request({
    url: '/admin/category/list',
    method: 'GET'
  })
}

/**
 * 创建分类
 * @param data
 * @returns
 */
export const createCategory = (data: any) => {
  return request({
    url: '/admin/category/add',
    method: 'POST',
    data
  })
}

/**
 * 编辑分类
 * @param id 分类ID
 * @param data 分类数据
 * @returns
 */
export const updateCategory = (id: string, data: any) => {
  return request({
    url: `/admin/category/edit/${id}`,
    method: 'POST',
    data
  })
}

/**
 * 更新分类显示状态
 * @param id 分类ID
 * @param status 分类状态
 * @returns
 */
export const updateCategoryStatus = (id: string, status: string) => {
  const formData = new FormData()
  formData.append('status', status)
  return request({
    url: `/admin/category/status/${id}`,
    method: 'POST',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 更新分类排序
 * @param data 分类排序数据
 * @returns Promise<any>
 */
export const updateCategorySort = (data: any) => {
  const formData = new FormData()
  formData.append('pid', data.pid)
  formData.append('sort', data.sort)
  return request({
    url: `/admin/category/sort/${data.id}`,
    method: 'POST',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 更新分类文章排序
 * @param id 分类ID
 * @param data 分类排序数据 {articles_order: 'id desc'}
 * @returns Promise<any>
 */
export const updateCategoryArticleSort = (id: string, data: any) => {
  return request({
    url: `/admin/category/articles/sort/${id}`,
    method: 'POST',
    data
  })
}

/**
 * 删除分类
 * @param id 分类ID
 * @returns
 */
export const deleteCategory = (id: string) => {
  return request({
    url: `/admin/category/delete/${id}`,
    method: 'DELETE'
  })
}

/**
 * 获取页面详情
 * @param id 页面ID
 * @returns
 */
export const getCategoryInfo = (id: string) => {
  return request({
    url: `/admin/category/detail/${id}`,
    method: 'GET'
  })
}

/**
 * 获取分类列表（公开接口，供作者和协作者使用）
 * @returns
 */
export const getCategoryList = () => {
  return request({
    url: '/blog/category/list',
    method: 'GET'
  })
}
