import { createI18n } from 'vue-i18n'
import enUS from './en-US'
import cn from './zh-CN'

// 同步导入管理后台翻译模块
import adminModules from './admin/index'

// 导入邀请模块
import inviteModules from './invite/index'

// 定义语言选项
export const LOCALE_OPTIONS = [
  { label: '中文', value: 'zh-CN' },
  { label: 'English', value: 'en-US' }
]

// 语言存储键常量
const ADMIN_LOCALE_KEY = 'admin-locale'
const BLOG_LOCALE_KEY = 'blog-locale'

// 后台侧（管理后台 + Author 工作台）共用 admin-locale，前台用 blog-locale。
// 统一用同一个判定，避免 i18n 初始化、路由守卫、切换 hook 三处口径漂移。
export const isBackendPath = (path: string) => /^\/(admin|creator)(\/|$)/.test(path)

const isAdminPage = isBackendPath(window.location.pathname)
const defaultLocale = isAdminPage
  ? localStorage.getItem(ADMIN_LOCALE_KEY) || 'zh-CN'
  : localStorage.getItem(BLOG_LOCALE_KEY) || 'zh-CN'

// 构建管理后台翻译消息（按语言分组）
const buildAdminMessages = (locale: 'zh-CN' | 'en-US') => {
  return {
    admin: {
      general: adminModules.general[locale],
      analytics: adminModules.analytics[locale],
      article: adminModules.article[locale],
      category: adminModules.category[locale],
      comment: adminModules.comment[locale],
      dashboard: adminModules.dashboard[locale],
      navbar: adminModules.navbar[locale],
      series: adminModules.series[locale],
      pages: adminModules.pages[locale],
      tags: adminModules.tags[locale],
      members: adminModules.members[locale],
      user: adminModules.user[locale],
      docbook: adminModules.docbook[locale],
      doc: adminModules.doc[locale],
      settings: adminModules.settings[locale],
      appearance: adminModules.appearance[locale]
    }
  }
}

// 合并翻译消息
// 注意：admin 段按 buildAdminMessages 白名单合并，新增 admin 模块必须同步在此注册。
// creator（Author 工作台）注册为顶层段而非 admin 子段——组件 key 为 creator.*，
// 且 AdminLayout 顶栏菜单等非 admin 前缀的组件也会使用该段（与 invite 同模式）。
const messages = {
  'en-US': {
    ...enUS,
    ...buildAdminMessages('en-US'),
    creator: adminModules.creator['en-US'],
    invite: inviteModules['en-US']
  },
  'zh-CN': {
    ...cn,
    ...buildAdminMessages('zh-CN'),
    creator: adminModules.creator['zh-CN'],
    invite: inviteModules['zh-CN']
  }
}

// 创建i18n实例
const i18n = createI18n({
  locale: defaultLocale,
  fallbackLocale: 'en-US',
  legacy: false,
  allowComposition: true,
  messages: messages
})

// 导出语言存储键常量，方便其他地方使用
export { ADMIN_LOCALE_KEY, BLOG_LOCALE_KEY }

export default i18n
