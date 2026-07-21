/**
 * API通用类型定义
 */

/**
 * 基础响应结构
 */
// 在TypeScript中，没有专门的integer类型，所有数字都使用number类型表示
// 虽然time字段类型是number，但在API响应中，它表示的是整数时间戳（秒或毫秒）
export interface ApiResponse<T = any> {
  code: number
  msg: string
  time: number // 整数时间戳（建议在使用时进行整数检查）
  data: T
}

// 可选：创建一个自定义类型别名，提高代码可读性
export type Timestamp = number // 表示整数时间戳的类型别名

/**
 * 分页响应结构
 */
export interface PaginationResponse<T = any> {
  list: T[]
  total: number
  page: number
  pageSize: number
}

/**
 * 分页结果（PageResult别名，兼容性）
 */
export type PageResult<T = any> = PaginationResponse<T>

/**
 * 分页请求参数
 */
export interface PaginationParams {
  page?: number
  pageSize?: number
  keyword?: string
  [key: string]: any
}

/**
 * 文件上传参数
 */
export interface UploadParams {
  file: File
  fileName?: string
  [key: string]: any
}

/**
 * API错误类型
 */
export interface ApiError {
  code?: number
  msg: string
  time: number
  [key: string]: any
}
