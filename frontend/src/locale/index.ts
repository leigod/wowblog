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

// 根据当前是否在管理后台页面选择不同的语言存储键（完全独立，无后备）
const isAdminPage = window.location.pathname.startsWith('/admin/')
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
const messages = {
  'en-US': {
    ...enUS,
    ...buildAdminMessages('en-US'),
    invite: inviteModules['en-US']
  },
  'zh-CN': {
    ...cn,
    ...buildAdminMessages('zh-CN'),
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
