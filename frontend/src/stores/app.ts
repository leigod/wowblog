import { defineStore } from 'pinia'
import { getSystemConfig, getPublicConfig } from '@/api/services/common'
import { getTempToken } from '@/api/services/user'
import { wsService } from '@/api/services/websocket'

interface Userinfo {
  id: number
  username: string
  email: string | null
  mobile: string | null
  full_name: string | null
  profile_image: string | null
  status: string
  role: string
}

// 定义存储键名
const TEMP_TOKEN_KEY = 'temp_token'
const TEMP_TOKEN_EXPIRE_KEY = 'temp_token_expire'
const THEME_FOLLOW_SYSTEM_KEY = 'theme_follow_system'
const THEME_DEFAULT_MODE_KEY = 'theme_default_mode'
const SITE_CONFIG_KEY = 'site_config'
const USER_CONFIG_KEY = 'user_config'

export const useAppStore = defineStore('app', {
  state: () => {
    // 从本地存储加载用户配置
    const userConfig = JSON.parse(localStorage.getItem(USER_CONFIG_KEY) || '{}')

    return {
      // 初始化主题设置
      isDark: false,
      isThemeFollowSystem:
        userConfig.isThemeFollowSystem !== undefined ? userConfig.isThemeFollowSystem : true,
      language: userConfig.language || 'zh-CN',
      admin_language: userConfig.admin_language || 'zh-CN',
      // 用户认证状态
      isLoggedIn: localStorage.getItem('is_logged_in') === 'true',
      token: localStorage.getItem('access_token') || sessionStorage.getItem('access_token') || null,
      userRole: localStorage.getItem('userRole') || null,
      userInfo: JSON.parse(localStorage.getItem('userInfo') || '{}'),
      // 临时 token（用于未登录用户访问公共接口）
      tempToken: null as string | null,
      loading: false,
      site_logo: null,
      site_title: null,
      site_favicon: null,
      disable_comment: false,
      dark_mode: 'system', // system, dark, light
      enable_register: true, // 是否开启注册，默认开启
      // 消息推送配置
      websocketEnabled: true,
      pollingInterval: 30000,
      messagePushMethod: 'websocket'
    }
  },
  actions: {
    // 初始化站点配置和主题
    async initTheme() {
      try {
        // 1. 先尝试从本地存储加载站点配置（用于快速显示）
        const savedSiteConfig = localStorage.getItem(SITE_CONFIG_KEY)
        if (savedSiteConfig) {
          try {
            const config = JSON.parse(savedSiteConfig)
            this.applySiteConfig(config)
            console.log('使用本地存储的站点配置')
          } catch (e) {
            console.error('解析本地站点配置失败:', e)
            // 如果解析失败，继续获取新配置
          }
        }

        // 2. 初始化暗黑模式状态
        this.initDarkMode()

        // 3. 始终从 API 获取最新的站点配置（确保获取最新的 enable_register 等配置）
        await this.fetchSiteConfig()
      } catch (error) {
        console.error('初始化配置失败:', error)
        // 出错时使用默认设置
        this.initDarkMode()
      }
    },

    // 初始化暗黑模式
    initDarkMode() {
      // 从用户配置获取主题模式和跟随系统设置
      const userConfig = JSON.parse(localStorage.getItem(USER_CONFIG_KEY) || '{}')
      const themeMode = userConfig.themeMode || 'light'
      const followSystem = userConfig.followSystem !== undefined ? userConfig.followSystem : true

      this.isThemeFollowSystem = followSystem

      // 根据设置决定初始主题
      if (followSystem) {
        // 跟随系统设置
        const isSystemDark =
          window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
        this.isDark = isSystemDark
        console.log('跟随系统主题:', this.isDark ? 'dark' : 'light')
      } else {
        // 不跟随系统时，使用用户配置的主题模式
        this.isDark = themeMode === 'dark'
        console.log('使用用户配置的主题模式:', this.isDark ? 'dark' : 'light')
      }

      // 更新实际的DOM元素以应用暗黑模式
      document.documentElement.classList.toggle('dark', this.isDark)
    },

    // 获取临时token（有效期10分钟）
    // 注意：临时token只用于公共接口，不应该覆盖用户的access_token
    async getTempToken() {
      const savedToken = localStorage.getItem(TEMP_TOKEN_KEY)
      const expireTime = localStorage.getItem(TEMP_TOKEN_EXPIRE_KEY)
      const now = Date.now()

      // 检查是否有未过期的临时token
      if (savedToken && expireTime && parseInt(expireTime) > now) {
        console.log('使用缓存的临时token')
        this.tempToken = savedToken
        return savedToken
      }

      // 没有有效token时，请求新的临时token
      try {
        const tokenRes = await getTempToken()
        if (tokenRes && tokenRes.code === 1 && tokenRes.data) {
          const newToken = tokenRes.data.access_token
          this.tempToken = newToken
          // 保存临时token，有效期10分钟
          const newExpireTime = Date.now() + 10 * 60 * 1000 // 10分钟有效期
          localStorage.setItem(TEMP_TOKEN_KEY, newToken)
          localStorage.setItem(TEMP_TOKEN_EXPIRE_KEY, String(newExpireTime))
          console.log('获取新的临时token成功')
          return newToken
        }
      } catch (error) {
        console.error('获取临时token失败:', error)
      }

      return null
    },

    // 获取站点配置
    async fetchSiteConfig() {
      try {
        console.log('开始获取站点配置')

        // 如果没有用户token，获取临时token（仅用于公共接口）
        if (!this.token && !this.isLoggedIn) {
          console.log('未登录，获取临时token用于公共接口')
          await this.getTempToken()
        }

        // 然后获取配置信息
        const configRes = await getSystemConfig()
        console.log('获取系统配置结果:', configRes)

        if (configRes && configRes.code === 1 && configRes.data) {
          const config = configRes.data
          console.log('获取到的系统配置:', config)

          // 应用配置
          this.applySiteConfig(config)

          // 保存到本地存储
          localStorage.setItem(SITE_CONFIG_KEY, JSON.stringify(config))
          console.log('站点配置保存成功')
        }
      } catch (error) {
        console.error('获取系统配置失败:', error)
      }
    },

    // 应用站点配置
    applySiteConfig(config: any) {
      // 保存网站全局配置
      this.site_logo = config.site_logo || this.site_logo
      this.site_title = config.site_title || this.site_title
      this.site_favicon = config.site_favicon || this.site_favicon
      this.disable_comment = config.disable_comment || false
      this.dark_mode = config.dark_mode || 'system'
      this.enable_register = config.enable_register !== undefined ? config.enable_register === 1 : true

      // 动态更新 favicon
      const updateFavicon = (faviconUrl: string) => {
        const link = document.getElementById('dynamic-favicon') as HTMLLinkElement
        if (link) {
          link.href = faviconUrl || '/favicon.ico'
        }
      }
      updateFavicon(this.site_favicon || '')

      // 如果用户没有设置过语言，使用站点默认语言
      const userConfig = JSON.parse(localStorage.getItem(USER_CONFIG_KEY) || '{}')
      if (!userConfig.language && config.language) {
        this.language = config.language
      }
    },

    // 设置语言
    setLanguage(lang: string) {
      this.language = lang

      // 保存到用户配置
      const userConfig = JSON.parse(localStorage.getItem(USER_CONFIG_KEY) || '{}')
      userConfig.language = lang
      localStorage.setItem(USER_CONFIG_KEY, JSON.stringify(userConfig))
    },

    // 切换暗黑模式
    toggleDarkMode() {
      this.isDark = !this.isDark

      // 更新实际的DOM元素以应用暗黑模式
      document.documentElement.classList.toggle('dark', this.isDark)

      // 切换主题时，自动设置为不跟随系统
      this.isThemeFollowSystem = false

      // 保存到用户配置
      const userConfig = JSON.parse(localStorage.getItem(USER_CONFIG_KEY) || '{}')
      userConfig.followSystem = false
      userConfig.themeMode = this.isDark ? 'dark' : 'light'
      localStorage.setItem(USER_CONFIG_KEY, JSON.stringify(userConfig))

      console.log('切换主题模式:', this.isDark ? 'dark' : 'light')
    },

    // 设置暗黑模式
    setDarkMode(mode: 'system' | 'dark' | 'light') {
      if (mode === 'system') {
        this.isThemeFollowSystem = true
        const isSystemDark =
          window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
        this.isDark = isSystemDark
      } else {
        this.isThemeFollowSystem = false
        this.isDark = mode === 'dark'
      }

      // 更新实际的DOM元素以应用暗黑模式
      document.documentElement.classList.toggle('dark', this.isDark)

      // 保存到用户配置
      const userConfig = JSON.parse(localStorage.getItem(USER_CONFIG_KEY) || '{}')
      userConfig.followSystem = mode === 'system'
      userConfig.themeMode = mode === 'system' ? (this.isDark ? 'dark' : 'light') : mode
      localStorage.setItem(USER_CONFIG_KEY, JSON.stringify(userConfig))

      console.log('设置主题模式为:', mode)
    },
    // 设置用户角色
    setUserRole(role: string) {
      this.userRole = role
      localStorage.setItem('userRole', role)
    },
    // 设置用户信息
    setUserInfo(info: Userinfo) {
      this.userInfo = info
      localStorage.setItem('userInfo', JSON.stringify(info))
    },
    // 设置登录状态
    setLoggedInState(loggedIn: boolean) {
      this.isLoggedIn = loggedIn
      localStorage.setItem('is_logged_in', String(loggedIn))
    },

    // 设置全局加载状态
    setLoading(loading: boolean) {
      this.loading = loading
    },

    // 加载公共配置
    async loadPublicConfig() {
      try {
        const res = await getPublicConfig()
        if (res.code === 1 && res.data) {
          this.websocketEnabled = res.data.websocket_enabled ?? true
          this.pollingInterval = (res.data.polling_interval || 30) * 1000
          this.messagePushMethod = res.data.message_push_method || 'websocket'
          console.log('公共配置加载成功:', res.data)
        }
      } catch (error) {
        console.error('加载公共配置失败:', error)
      }
    },

    // 初始化消息推送
    initMessagePush() {
      // 断开现有连接
      wsService.disconnect()

      // 如果启用 WebSocket
      if (this.messagePushMethod === 'websocket' && this.token) {
        // 构建 WebSocket URL
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        const host = window.location.host
        const wsUrl = `${protocol}//${host}/ws/messages`

        console.log('初始化 WebSocket 推送:', wsUrl)
        wsService.connect(wsUrl, this.token)
      } else {
        console.log('使用轮询方式获取消息，间隔:', this.pollingInterval)
      }
    },

    // 清除用户信息（登出时使用）
    clearUserInfo() {
      this.token = null
      this.userRole = null
      this.isLoggedIn = false
      this.tempToken = null

      // 断开 WebSocket 连接
      wsService.disconnect()

      // 清除所有存储的用户信息
      localStorage.removeItem('access_token')
      localStorage.removeItem('userRole')
      localStorage.removeItem('userInfo')
      localStorage.removeItem('is_logged_in')
      sessionStorage.removeItem('access_token')
      // 清除临时token
      localStorage.removeItem('temp_token')
      localStorage.removeItem('temp_token_expire')
    }
  }
})
