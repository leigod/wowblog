import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { nextTick } from 'vue'
import { useAppStore } from '@/stores/app'
//import './styles/element/index.scss'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import '@fortawesome/fontawesome-free/css/all.css'
import VueSocialSharing from 'vue-social-sharing'
//import 'element-plus/theme-chalk/src/dark/var.scss'
//import './styles/dark/css-vars.css'

import './styles/_variables.scss'
import './styles/_keyframe-animations.scss'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import en from 'element-plus/es/locale/lang/en'
import i18n from './locale/index'

import App from './App.vue'
import router from './router'
import './router/permission'

const app = createApp(App)

// elementplus icon
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
	app.component(key, component)
}

app.use(i18n)
// 根据当前语言初始化Element Plus
const initialLocale = i18n.global.locale.value === 'zh-CN' ? zhCn : en
app.use(ElementPlus, {
	locale: initialLocale
})
app.use(VueSocialSharing)
// 创建pinia实例
const pinia = createPinia()
app.use(pinia)

// 初始化主题设置
const appStore = useAppStore()

// 动态设置 favicon
const updateFavicon = (faviconUrl: string) => {
	const link = document.getElementById('dynamic-favicon') as HTMLLinkElement
	if (link) {
		link.href = faviconUrl || '/favicon.ico'
	}
}

// 初始化主题和favicon（异步初始化）
const initApp = async () => {
	await appStore.initTheme()
	updateFavicon(appStore.site_favicon || '')
}

initApp()

app.use(router)

router.beforeEach((to, from, next) => {
	//document.title = to.meta.title == undefined ? '默认标题' : to.meta.title
	const title = typeof to.meta.title === 'string' ? to.meta.title : '默认标题'
	document.title = title

	// 根据路由切换前后台语言（完全独立，互不影响）
	const isAdminRoute = to.path.startsWith('/admin/')
	const ADMIN_LOCALE_KEY = 'admin-locale'
	const BLOG_LOCALE_KEY = 'blog-locale'

	const localeKey = isAdminRoute ? ADMIN_LOCALE_KEY : BLOG_LOCALE_KEY
	const targetLocale = (localStorage.getItem(localeKey) || 'zh-CN') as 'zh-CN' | 'en-US'

	// 更新 i18n 实例的 locale
	if (i18n.global.locale.value !== targetLocale) {
		i18n.global.locale.value = targetLocale
	}

	next()
})

app.mount('#app')
