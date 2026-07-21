import { request } from '../http'

/**
 * 获取网站配置
 * @returns
 */
export const getSiteConfig = () => {
  return request({
    url: `/admin/setting`,
    method: 'GET'
  })
}

/**
 * 更新网站配置
 * @param data 配置数据
 * @returns
 */
export const updateSiteConfig = (data: any) => {
  return request({
    url: `/admin/setting/update`,
    method: 'POST',
    data
  })
}
