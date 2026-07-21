import axios, {
  type AxiosInstance,
  type AxiosRequestConfig,
  type AxiosResponse,
  type AxiosError
} from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'
import { useAppStore } from '../stores/app'
import type { ApiResponse } from './types'

// 创建 axios 实例
const http: AxiosInstance = axios.create({
  // API基础URL配置
  // 从环境变量VITE_API_BASE_URL获取，若未设置则使用默认值'/api'
  // 环境变量设置方法：
  // 1. 在项目根目录创建.env.local文件
  // 2. 添加配置：VITE_API_BASE_URL=http://your-api-server:port/api
  // Vite 会按以下优先级加载环境变量：
  // 1. .env.local - 本地开发环境配置，优先级最高
  // 2. .env.development / .env.production - 特定模式的环境配置
  // 3. .env - 通用环境配置
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

/**
 * 请求拦截器
 * 添加token、设置loading状态等
 */
http.interceptors.request.use(
  (config: import('axios').InternalAxiosRequestConfig) => {
    const appStore = useAppStore()
    // 显示全局加载状态
    appStore.setLoading(true)

    // 获取token：优先使用用户access_token，其次使用临时token
    let token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token')

    // 调试：打印token来源
    if (token && (config.url?.includes('/auth/me') || config.url?.includes('/users/me'))) {
      const source = localStorage.getItem('access_token') === token ? 'localStorage' : 'sessionStorage'
      console.log('获取到access_token，来源:', source)
    }

    // 如果没有用户token，尝试使用临时token（用于公共接口）
    if (!token) {
      const tempToken = localStorage.getItem('temp_token')
      if (tempToken) {
        token = tempToken
        console.log('没有access_token，使用临时token')
      }
    }

    if (token) {
      config.headers = config.headers || {}
      config.headers['Authorization'] = `Bearer ${token}`
    }

    return config
  },
  (error: AxiosError) => {
    const appStore = useAppStore()
    appStore.setLoading(false)
    return Promise.reject(error)
  }
)

/**
 * 响应拦截器
 * 处理响应数据、统一错误处理等
 */
// 用于标记是否正在获取临时token，防止重复请求
let isGettingTempToken = false
// 用于存储等待重试的请求
let retryRequests: Array<{ resolve: (token: string) => void; reject: (error: any) => void }> = []
// 临时token API端点，避免循环
const TEMP_TOKEN_URL = '/get_temp_token'
// 需要管理员权限的API列表，不使用临时token重试
const ADMIN_APIs = ['/admin/', '/user/', '/users/']
// 前端认证相关API，401时直接失败，不重试
const AUTH_APIs = ['/auth/', '/login', '/notifications/unread-count']

http.interceptors.response.use(
  (response: AxiosResponse) => {
    const appStore = useAppStore()
    appStore.setLoading(false)

    const res = response.data

    // 处理业务错误
    if (res.code !== 1) {
      ElMessage.error(res.data[0].msg || res.msg || '请求失败')
      return Promise.reject(new Error(res.data[0].msg || res.msg || 'Error'))
    }

    //return res.data || res
    return res
  },
  async (error: AxiosError) => {
    const appStore = useAppStore()
    appStore.setLoading(false)

    // 统一错误处理
    if (error.response) {
      console.log('error.response:', error.response)
      const originalRequest = error.config as any

      switch (error.response.status) {
        case 401: {
          // 如果是获取临时token的请求本身返回401，直接失败，避免循环
          if (originalRequest.url?.includes(TEMP_TOKEN_URL)) {
            console.error('获取临时token失败，API返回401')
            return Promise.reject(error)
          }

          // 检查是否是需要管理员权限的API
          const isAdminAPI = ADMIN_APIs.some(api => originalRequest.url?.includes(api))
          if (isAdminAPI) {
            console.log('管理员API，不使用临时token重试:', originalRequest.url)
            // 管理员API直接返回错误，不尝试获取临时token
            return Promise.reject(error)
          }

          // 检查是否是前端认证相关API
          const isAuthAPI = AUTH_APIs.some(api => originalRequest.url?.includes(api))
          if (isAuthAPI) {
            // 前端认证API直接返回错误，不尝试获取临时token
            return Promise.reject(error)
          }

          // 检查用户是否已登录（使用独立的登录状态标志）
          const isLoggedIn = localStorage.getItem('is_logged_in') === 'true'

          if (!isLoggedIn) {
            // 未登录用户，尝试获取临时token
            if (!isGettingTempToken) {
              isGettingTempToken = true

              try {
                const tempToken = await appStore.getTempToken()
                isGettingTempToken = false

                if (tempToken) {
                  console.log('获取临时token成功，重试请求:', originalRequest.url)

                  // 获取临时token成功，重试所有等待的请求
                  retryRequests.forEach(({ resolve }) => resolve(tempToken))
                  retryRequests = []

                  // 重试当前请求
                  originalRequest.headers = originalRequest.headers || {}
                  originalRequest.headers['Authorization'] = `Bearer ${tempToken}`
                  return http(originalRequest)
                }
              } catch (tokenError) {
                console.error('获取临时token失败:', tokenError)
                isGettingTempToken = false

                // 获取临时token失败，拒绝所有等待的请求
                retryRequests.forEach(({ reject }) => {
                  try {
                    reject(tokenError)
                  } catch (e) {
                    console.error('重试请求失败:', e)
                  }
                })
                retryRequests = []
                // 对于未登录用户，获取临时token失败时直接拒绝请求，不跳转登录页
                return Promise.reject(tokenError)
              }
            } else {
              // 如果正在获取临时token，将当前请求加入等待队列
              console.log('正在获取临时token，将当前请求加入等待队列')
              return new Promise((resolve, reject) => {
                const retryCallback = (token: string) => {
                  originalRequest.headers = originalRequest.headers || {}
                  originalRequest.headers['Authorization'] = `Bearer ${token}`
                  http(originalRequest).then(resolve).catch(reject)
                }
                const rejectCallback = (err: any) => {
                  reject(err)
                }
                retryRequests.push({ resolve: retryCallback, reject: rejectCallback })
              })
            }
          }

          // 已登录用户 token过期，跳转到登录页
          ElMessage.error('登录已过期，请重新登录')
          appStore.clearUserInfo()
          // 使用replace代替push，防止用户返回到需要授权的页面
          // 添加setTimeout确保在清除用户信息后执行跳转
          setTimeout(() => {
            // 强制刷新路由，确保页面正确更新
            router.replace('/login').catch((error) => {
              console.log('路由跳转错误:', error)
              // 极端情况下强制刷新页面
              if (window.location.pathname !== '/login') {
                window.location.href = '/login'
              }
            })
          }, 0)
          break
        }
        case 403:
          ElMessage.error('无权限访问')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default: {
          const errorData = error.response.data || {}
          ElMessage.error((errorData as { msg?: string }).msg || '请求失败')
        }
      }
    } else if (error.request) {
      ElMessage.error('网络错误，请检查网络连接')
    } else {
      ElMessage.error('请求配置错误')
    }

    return Promise.reject(error)
  }
)

/**
 * 封装请求方法
 * @param config axios请求配置
 * @returns Promise<T> 返回响应中的data部分或整个响应对象
 */
// 使用泛型确保类型安全，T表示最终返回的数据类型
const request = async <T = any>(config: AxiosRequestConfig): Promise<T> => {
  const response = await http(config)
  // 先转换为unknown，再转换为目标类型T，避免类型检查错误
  return response as unknown as T
}

/**
 * 类型安全的API响应请求方法
 * @param config axios请求配置
 * @returns Promise<ApiResponse<T>> 返回完整的API响应结构
 */
export const requestWithResponse = async <T = any>(
  config: AxiosRequestConfig
): Promise<ApiResponse<T>> => {
  const response = await http(config)
  // 先转换为unknown，再转换为ApiResponse<T>，避免类型检查错误
  return response as unknown as ApiResponse<T>
}

export { http, request }
