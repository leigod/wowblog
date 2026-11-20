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
  // 跨域携带 cookie：OAuth 回调后通过 httpOnly cookie 中转 access_token，
  // 前端调 /auth/oauth/session 取 token 时必须带凭证。不影响现有 Bearer header 认证。
  withCredentials: true,
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

    // 上传 FormData 时必须移除实例默认的 application/json，
    // 否则后端按 JSON 解析 multipart 请求体 -> 422。
    // 删掉后浏览器会自动补带 boundary 的 multipart/form-data。
    if (typeof FormData !== 'undefined' && config.data instanceof FormData) {
      delete config.headers['Content-Type']
    }

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
// 需要管理员权限的API列表：仅在"未登录"分支用于跳过临时token重试。
// 已登录用户 token 过期一律走登出，不再因命中此列表而静默放过（旧逻辑会让坏 token 残留 sessionStorage）
const ADMIN_APIs = ['/admin/', '/user/', '/users/']
// 前端认证相关API，401 时直接失败、绝不触发登出
// （否则登录页输错一次密码就会把已登录态清掉）
const AUTH_APIs = ['/auth/', '/login', '/notifications/unread-count']

// 401 登出防抖锁：一旦开始登出流程，同批并发的其它 401 不再重复清理/跳转
let isRedirectingToLogin = false

// 无条件清理两端所有认证态（store + localStorage + sessionStorage）
const clearAllAuthState = (appStore: any) => {
  appStore.clearUserInfo()
  // 兜底：即便 store 的清理逻辑变动，也确保两端 token 不残留
  const keys = ['access_token', 'userRole', 'userInfo', 'is_logged_in', 'temp_token', 'temp_token_expire']
  keys.forEach(k => {
    localStorage.removeItem(k)
    sessionStorage.removeItem(k)
  })
}

http.interceptors.response.use(
  (response: AxiosResponse) => {
    const appStore = useAppStore()
    appStore.setLoading(false)

    const res = response.data

    // 处理业务错误（注意 res.data 可能为空数组/对象，必须可选链，
    // 否则 res.data[0].msg 在 data 为空时抛 TypeError，导致后端 msg 无法展示）
    if (res.code !== 1) {
      const errMsg = res.data?.[0]?.msg || res.msg || '请求失败'
      ElMessage.error(errMsg)
      return Promise.reject(new Error(errMsg))
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
          // 1) 获取临时token的请求本身返回401，直接失败，避免递归
          if (originalRequest.url?.includes(TEMP_TOKEN_URL)) {
            console.error('获取临时token失败，API返回401')
            return Promise.reject(error)
          }

          // 2) 认证相关接口（登录/注册等）返回401 = 账号密码错误，不是会话过期。
          //    绝不能触发登出，否则在登录页输错密码会把刚建立的登录态清掉。
          const isAuthAPI = AUTH_APIs.some(api => originalRequest.url?.includes(api))
          if (isAuthAPI) {
            return Promise.reject(error)
          }

          // 3) 登出防抖：本轮 401 已经开始走登出流程，后续并发请求一律静默拒绝。
          //    这是"重新登录后又被踢回、必须关页"的核心——晚到的旧 401 会看到
          //    is_logged_in 已被新登录置回 true，若不拦截就会再次 clearUserInfo。
          if (isRedirectingToLogin) {
            return Promise.reject(error)
          }

          // 4) 判断是否已登录（独立的登录状态标志）
          const isLoggedIn = localStorage.getItem('is_logged_in') === 'true'

          if (isLoggedIn) {
            // 已登录用户 token 过期：清理 + 跳转。
            // 注意这里不再按 ADMIN_APIs 分流——头像上传(/user/avatar)、
            // 取用户信息(/users/me)等接口过期时必须同样清理，否则坏 token 残留 sessionStorage。
            isRedirectingToLogin = true
            ElMessage.error('登录已过期，请重新登录')
            clearAllAuthState(appStore)

            // 等待重试队列中的请求全部拒绝，避免旧请求在跳登录后用临时token重试产生连锁
            retryRequests.forEach(({ reject }) => {
              try { reject(error) } catch (e) { console.error('重试请求失败:', e) }
            })
            retryRequests = []
            isGettingTempToken = false

            // 解锁时机：跳到登录页后再放开。用 replace 防止回退到需授权页面。
            setTimeout(() => {
              router.replace('/login').catch((err) => {
                console.log('路由跳转错误:', err)
                if (window.location.pathname !== '/login') {
                  window.location.href = '/login'
                }
              }).finally(() => {
                // 给一点缓冲再解锁，确保本轮并发 401 都已到达并被上面的锁拦掉
                setTimeout(() => { isRedirectingToLogin = false }, 300)
              })
            }, 0)
            return Promise.reject(error)
          }

          // 5) 未登录用户：管理类接口不做临时token重试（无意义），直接拒绝
          const isAdminAPI = ADMIN_APIs.some(api => originalRequest.url?.includes(api))
          if (isAdminAPI) {
            console.log('未登录且为管理员API，不使用临时token重试:', originalRequest.url)
            return Promise.reject(error)
          }

          // 6) 未登录用户访问公共接口，尝试临时token（原逻辑保留）
          if (!isGettingTempToken) {
            isGettingTempToken = true

            try {
              const tempToken = await appStore.getTempToken()
              isGettingTempToken = false

              if (tempToken) {
                console.log('获取临时token成功，重试请求:', originalRequest.url)

                retryRequests.forEach(({ resolve }) => resolve(tempToken))
                retryRequests = []

                originalRequest.headers = originalRequest.headers || {}
                originalRequest.headers['Authorization'] = `Bearer ${tempToken}`
                return http(originalRequest)
              }
            } catch (tokenError) {
              console.error('获取临时token失败:', tokenError)
              isGettingTempToken = false

              retryRequests.forEach(({ reject }) => {
                try { reject(tokenError) } catch (e) { console.error('重试请求失败:', e) }
              })
              retryRequests = []
              // 未登录用户获取临时token失败时直接拒绝，不跳转登录页
              return Promise.reject(tokenError)
            }
          } else {
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
