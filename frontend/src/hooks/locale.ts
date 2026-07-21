import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { ADMIN_LOCALE_KEY, BLOG_LOCALE_KEY } from '@/locale/index'

export default function useLocale() {
  const i18 = useI18n()
  
  // 获取当前语言
  const currentLocale = computed(() => {
    return i18.locale.value
  })
  
  // 判断是否在管理后台页面
  const isAdminPage = () => {
    return window.location.pathname.startsWith('/admin/')
  }
  
  // 切换语言函数
  const changeLocale = (value: string) => {
    // 验证语言值是否有效
    if (!['en-US', 'zh-CN'].includes(value)) {
      console.error('Invalid locale value:', value)
      return
    }
    
    // 如果语言没有变化，不需要操作
    if (i18.locale.value === value) {
      return
    }
    
    // 更新i18n语言设置（这将触发main.ts中的watch监听）
    i18.locale.value = value
    
    // 根据当前页面路径选择正确的存储键
    const localeKey = isAdminPage() ? ADMIN_LOCALE_KEY : BLOG_LOCALE_KEY
    localStorage.setItem(localeKey, value)
    
    // 显示切换成功消息
    ElMessage({
      message: i18.t('navbar.action.locale'),
      type: 'success'
    })
  }
  
  return {
    currentLocale,
    changeLocale,
    isAdminPage
  }
}
