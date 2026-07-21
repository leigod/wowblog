/**
 * 通用API服务
 * 包含共用的API调用方法
 */
import { request } from '../http'
import type { UploadParams, PaginationParams, PaginationResponse } from '../types'

/**
 * 上传进度回调接口
 */
export interface UploadProgressCallback {
  (progressEvent: { percent: number; loaded: number; total: number }): void
}

/**
 * 文件上传服务
 * @param params 上传参数
 * @returns Promise<any>
 */
export const uploadFile = (
  params: UploadParams & { onProgress?: UploadProgressCallback }
): Promise<any> => {
  const formData = new FormData()
  formData.append('file', params.file)

  // 添加其他参数
  const { onProgress, ...otherParams } = params
  Object.keys(otherParams).forEach((key) => {
    if (key !== 'file') {
      formData.append(key, otherParams[key])
    }
  })

  // 处理上传进度回调
  const handleProgress = onProgress
    ? (progressEvent: any) => {
        const eventData = {
          percent:
            progressEvent.total > 0
              ? Math.round((progressEvent.loaded / progressEvent.total) * 100)
              : 0,
          loaded: progressEvent.loaded,
          total: progressEvent.total
        }
        onProgress(eventData)
      }
    : undefined

  return request({
    url: '/upload/',
    method: 'POST',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    onUploadProgress: handleProgress
  })
}

/**
 * 获取验证码
 * @returns Promise<any>
 */
export const getCaptcha = (): Promise<any> => {
  return request({
    url: '/captcha',
    method: 'GET'
  })
}

/**
 * 获取系统配置
 * @returns Promise<any>
 */
export const getSystemConfig = (): Promise<any> => {
  return request({
    url: '/blog/config',
    method: 'GET'
  })
}

/**
 * 获取公共配置（包含消息推送设置）
 * @returns Promise<any>
 */
export const getPublicConfig = (): Promise<any> => {
  return request({
    url: '/config/public',
    method: 'GET'
  })
}

/**
 * 获取字典数据
 * @param type 字典类型
 * @returns Promise<any>
 */
export const getDictionary = (type: string): Promise<any> => {
  return request({
    url: `/dictionary/${type}`,
    method: 'GET'
  })
}

/**
 * 分页获取数据的通用方法
 * @param url 请求URL
 * @param params 分页参数
 * @returns Promise<PaginationResponse<T>>
 */
export const getPagedList = <T = any>(
  url: string,
  params: PaginationParams
): Promise<PaginationResponse<T>> => {
  return request({
    url,
    method: 'GET',
    params: {
      page: params.page || 1,
      pageSize: params.pageSize || 10,
      ...params
    }
  })
}
