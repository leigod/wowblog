<template>
  <el-container class="admin-layout">
    <el-header class="admin-header-wrap">
      <div v-if="isMobile" class="mobile-admin-header">
        <div>
          <span style="margin-right: 10px; font-weight: 600">{{ siteTitle }}</span>
          <el-dropdown trigger="click" @command="handleMenuClick">
            <span style="display: flex; align-items: center">
              <iconify-icon icon="material-symbols-light:menu" /><el-icon
                class="el-icon--right"><arrow-down /></el-icon>
            </span>

            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item v-for="item in filteredMenuItems" :key="item.index" :index="item.index"
                  :command="item.route"><el-icon>
                    <component :is="item.icon" />
                  </el-icon>
                  {{ item.title }}</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
        <div>
          <el-dropdown trigger="click" @command="handleUserMenuCommand">
            <span class="el-dropdown-link">
              {{ appStore.userInfo.full_name
              }}<el-icon class="el-icon--right"><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="create">
                  <el-icon>
                    <EditPen />
                  </el-icon>
                  {{ $t('admin.general.top.create') }}
                </el-dropdown-item>
                <el-dropdown-item command="home">
                  <el-icon>
                    <House />
                  </el-icon>
                  {{ $t('admin.general.top.home') }}
                </el-dropdown-item>
                <el-dropdown-item command="toggle-theme">
                  <el-icon v-if="!isAdminDark">
                    <Moon />
                  </el-icon>
                  <el-icon v-else>
                    <Sunny />
                  </el-icon>
                  {{ $t('admin.general.top.darkmode.' + (isAdminDark ? 'light' : 'dark')) }}
                </el-dropdown-item>
                <el-dropdown-item command="toggle-language">
                  <span class="language-icon">
                    <IconifyIcon icon="heroicons:language" :width="16" :height="16"
                      :color="isAdminDark ? '#FFFFFFFF' : 'currentColor'" />
                  </span>
                  {{ $t('admin.general.top.switch_language') }}
                </el-dropdown-item>
                <el-dropdown-item command="notifications">
                  <el-icon>
                    <Bell />
                  </el-icon>
                  {{ $t('admin.general.top.notifications') }}
                </el-dropdown-item>
                <el-dropdown-item command="profile">
                  <el-icon>
                    <User />
                  </el-icon>
                  {{ $t('admin.general.top.profile') }}
                </el-dropdown-item>
                <el-dropdown-item command="change-password">
                  <el-icon>
                    <Lock />
                  </el-icon>
                  {{ $t('admin.general.top.change_password') }}
                </el-dropdown-item>
                <el-dropdown-item command="logout">
                  <el-icon>
                    <CircleClose />
                  </el-icon>
                  {{ $t('admin.general.top.logout') }}
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
      <div v-else class="admin-header">
        <!-- 管理后台头部 -->
        <div class="header-logo">
          <img style="width: 100px" :src="siteLogo" alt="logo" />
        </div>
        <div class="header-name">
          <span>{{ siteTitle }}</span>
        </div>
        <div class="flex-grow"></div>
        <div class="header-actions">
          <el-tooltip :content="$t('admin.general.top.create')">
            <el-button type="primary" :icon="EditPen" circle size="large" @click="navigateToCreateArticle" />
          </el-tooltip>
          <el-tooltip :content="$t('admin.general.top.home')">
            <div class="round-button" @click="handleNavigateToHome">
              <el-icon :size="22">
                <House />
              </el-icon>
            </div>
          </el-tooltip>
          <el-tooltip :content="$t('admin.general.top.darkmode.' + (isAdminDark ? 'light' : 'dark'))">
            <div v-if="!isAdminDark" class="round-button" @click="handleAdminDarkMode(true)">
              <el-icon :size="22">
                <Moon />
              </el-icon>
            </div>
            <div v-else class="round-button" @click="handleAdminDarkMode(false)">
              <el-icon :size="22">
                <Sunny />
              </el-icon>
            </div>
          </el-tooltip>
          <el-dropdown :hide-on-click="false" @command="handleChange">
            <span class="el-dropdown-link">
              <IconifyIcon icon="heroicons:language" style="font-size: 24px"
                :color="isAdminDark ? '#FFFFFFFF' : 'currentColor'"
                :stroke="isAdminDark ? '#FFFFFFFF' : 'currentColor'" />
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item v-for="item in options" :key="item.value" :command="item.value">{{
                  item.label
                }}</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <!--消息通知-->
          <el-popover :width="360" placement="bottom-end" trigger="click"
            popper-style="box-shadow: rgb(14 18 22 / 35%) 0px 10px 38px -10px, rgb(14 18 22 / 20%) 0px 10px 20px -15px; padding: 5px;">
            <template #reference>
              <div class="notification-icon-wrapper" @click="handleNotificationIconClick">
                <el-icon :size="22" class="notification-bell">
                  <Bell />
                </el-icon>
                <el-badge is-dot :hidden="!hasNotificationDot" class="notification-badge-dot" />
              </div>
            </template>
            <template #default>
              <notification-panel @close="closeNotification" ref="notificationPanelRef" />
            </template>
          </el-popover>
          <!--个人资料-->
          <el-popover :width="300"
            popper-style="box-shadow: rgb(14 18 22 / 35%) 0px 10px 38px -10px, rgb(14 18 22 / 20%) 0px 10px 20px -15px; padding: 20px;"
            placement="bottom-end">
            <template #reference>
              <el-avatar :src="appStore.userInfo.profile_image || defaultAvatar" />
            </template>
            <template #default>
              <div class="demo-rich-conent" style="
                  display: flex;
                  gap: 16px;
                  flex-direction: column;
                  justify-content: center;
                  align-items: center;
                ">
                <el-avatar :size="80" :src="appStore.userInfo.profile_image || defaultAvatar"
                  style="margin-bottom: 8px" />
                <div>
                  <p class="demo-rich-content__name" style="margin: 0; font-weight: 500; text-align: center">
                    {{ appStore.userInfo.full_name }}
                  </p>
                  <p class="demo-rich-content__mention" style="
                      margin: 0;
                      font-size: 14px;
                      color: var(--el-color-info);
                      text-align: center;
                    ">
                    @{{ appStore.userInfo.username
                    }}<span style="font-size: 12px; margin-left: 10px">
                      <el-tag :class="`role-tag role-${userRole.toLowerCase()}`">
                        {{ userRole }}
                      </el-tag>
                    </span>
                  </p>
                </div>
                <el-divider />
                <div style="width: 100%; display: flex; justify-content: space-between">
                  <el-button type="default" size="small" style="margin-bottom: 10px" @click="navigateToProfile">
                    {{ $t('admin.general.top.profile') }}
                  </el-button>
                  <el-button type="default" size="small" style="margin-bottom: 10px" @click="navigateToChangePassword">
                    {{ $t('admin.general.top.change_password') }}
                  </el-button>
                  <el-button type="danger" size="small" style="margin-bottom: 10px" @click="handleLogout">
                    {{ $t('admin.general.top.logout') }}
                  </el-button>
                </div>
              </div>
            </template>
          </el-popover>
        </div>
      </div>
    </el-header>

    <el-container class="admin-container">
      <!-- 管理后台侧边栏 -->

      <el-menu v-if="!isMobile" default-active="1" class="el-menu-vertical-demo" :collapse="isCollapse"
        @open="handleOpen" @close="handleClose" @select="handleSelect" :router="enableRouter">
        <el-menu-item v-for="item in filteredMenuItems" :key="item.index" :index="item.index" :route="item.route">
          <el-icon>
            <component :is="item.icon" />
          </el-icon>
          <template #title>{{ item.title }}</template>
        </el-menu-item>
        <el-divider />
        <div v-if="!isCollapse" style="text-align: right; padding-right: 20px" @click="handleClose1">
          <el-tooltip content="收起菜单">
            <el-icon>
              <DArrowLeft />
            </el-icon>
          </el-tooltip>
        </div>
        <div v-else style="text-align: right; padding-right: 20px" @click="handleOpen1">
          <el-tooltip content="展开菜单">
            <el-icon>
              <DArrowRight />
            </el-icon>
          </el-tooltip>
        </div>
      </el-menu>

      <!-- <el-container class="admin-content"> -->
      <el-main class="admin-main">
        <div class="admin-breadcrumb">
          <el-breadcrumb :separator-icon="ArrowRight">
            <el-breadcrumb-item :to="{ path: '/admin/dashboard' }">{{ $t('admin.general.breadcrumb.title')
            }}</el-breadcrumb-item>
            <el-breadcrumb-item v-for="item in filteredBreadcrumbItems" :key="item.index">
              {{ item.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <!-- 管理后台内容区 -->
        <div class="admin-content">
          <router-view />
        </div>
      </el-main>
      <!-- </el-container> -->
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useMobileDetection } from '@/composables/useMobileDetection'
import {
  EditPen,
  Moon,
  Sunny,
  PieChart as Dashboard,
  TrendCharts as Analytics,
  Setting,
  ElementPlus,
  Guide,
  Document,
  Folder,
  Collection,
  CollectionTag,
  ChatDotSquare,
  User,
  ArrowRight,
  CircleClose,
  Bell,
  OfficeBuilding,
  Notebook,
  Lock
} from '@element-plus/icons-vue'
import IconifyIcon from '@/components/IconIfy.vue'
import NotificationPanel from '@/components/NotificationPanel.vue'
import * as notificationApi from '@/api/services/notifications'

const route = useRoute()
const router = useRouter()

const appStore = useAppStore()
const isCollapse = ref(false)

// 通知相关
const hasNotificationDot = ref(false)
const notificationPanelRef = ref()
let notificationPollingTimer: ReturnType<typeof setInterval> | null = null
let wsNotificationHandler: ((data: any) => void) | null = null

// 加载通知状态（是否有未读通知）
const loadNotificationStatus = async () => {
  if (!appStore.token) return
  try {
    const res = await notificationApi.getUnreadCount()
    if (res.code === 1) {
      const count = res.data || 0
      // 只有在有未读通知时才显示红点
      if (hasNotificationDot.value !== (count > 0)) {
        hasNotificationDot.value = count > 0
      }
    }
  } catch (error) {
    console.debug('获取未读数量失败:', error)
  }
}

// 点击通知图标时隐藏红点
const handleNotificationIconClick = () => {
  hasNotificationDot.value = false
}

// 关闭通知面板
const closeNotification = () => {
  hasNotificationDot.value = false
}

// 启动通知轮询（仅在轮询模式下）
const startNotificationPolling = () => {
  // 检查是否使用 WebSocket 模式
  const pushMethod = appStore.messagePushMethod
  if (pushMethod === 'websocket') {
    console.log('[AdminLayout] WebSocket 模式，不启动轮询')
    return
  }

  if (notificationPollingTimer) {
    clearInterval(notificationPollingTimer)
  }
  // 每60秒检查一次是否有未读通知
  notificationPollingTimer = setInterval(() => {
    // 只在页面可见时才轮询
    if (!document.hidden) {
      loadNotificationStatus()
    }
  }, 60000)
  console.log('[AdminLayout] 轮询模式已启动')
}

// 停止通知轮询
const stopNotificationPolling = () => {
  if (notificationPollingTimer) {
    clearInterval(notificationPollingTimer)
    notificationPollingTimer = null
    console.log('[AdminLayout] 轮询已停止')
  }
}

// 监听页面可见性变化
const handleVisibilityChange = () => {
  if (!document.hidden) {
    // 页面变为可见时，立即加载一次最新状态
    // 但仅在轮询模式下
    const pushMethod = appStore.messagePushMethod
    if (pushMethod !== 'websocket') {
      loadNotificationStatus()
    }
  }
}
// 从 store 读取主题状态，而不是使用本地 ref
const isAdminDark = computed({
  get: () => appStore.isDark,
  set: (val) => {
    // 当设置新值时，调用 store 的方法
    if (val !== appStore.isDark) {
      appStore.toggleDarkMode()
    }
  }
})
const enableRouter = ref(true)
const currentNavKey = ref('1')

const defaultAvatar = '/avatar.png'
const defaultLogo = '/wow_blog_logo.svg'
const siteLogo = computed(() => appStore.site_logo || defaultLogo)
const siteTitle = computed(() => appStore.site_title || 'WOW Blog')
const userRole = computed(() => appStore.userRole || '')

const { t } = useI18n()
const language = computed(() => appStore.admin_language || 'zh-CN')
const options = ref([
  { label: '中文', value: 'zh-CN' },
  { label: 'English', value: 'en-US' }
])
const emits = defineEmits(['selectLanguage', 'changeDarkMode'])
const handleChange = (command: string | number | object) => {
  const newLanguage = command as string
  console.log('切换管理后台语言:', newLanguage)

  // 更新 appStore 中的 admin_language（管理后台专用，不影响前台）
  appStore.admin_language = newLanguage

  // 保存到 user_config 中（store 初始化时读取 admin_language）
  const userConfig = JSON.parse(localStorage.getItem('user_config') || '{}')
  userConfig.admin_language = newLanguage
  localStorage.setItem('user_config', JSON.stringify(userConfig))

  // 使用独立的 admin-locale 键（i18n 初始化时读取，只用于管理后台）
  localStorage.setItem('admin-locale', newLanguage)

  // 发出事件以便父组件也能响应
  emits('selectLanguage', newLanguage)

  // 重新加载页面以应用新语言
  location.reload()
}

// 定义菜单项及所需权限
const menuItems = computed(() => [
  {
    index: '1',
    route: '/admin/dashboard',
    icon: Dashboard,
    title: t('admin.general.side.menu.overview'),
    roles: ['Admin']
  },
  {
    index: '2',
    route: '/admin/analytics',
    icon: Analytics,
    title: t('admin.general.side.menu.analytics'),
    roles: ['Admin'],
    hideInSidebar: true  // 在侧边栏中隐藏，但保留用于面包屑导航
  },
  {
    index: '3',
    route: '/admin/settings',
    icon: Setting,
    title: t('admin.general.side.menu.setting'),
    roles: ['Admin']
  },
  {
    index: '4',
    route: '/admin/appearance',
    icon: ElementPlus,
    title: t('admin.general.side.menu.appearance'),
    roles: ['Admin']
  },
  {
    index: '5',
    route: '/admin/navbar',
    icon: Guide,
    title: t('admin.general.side.menu.navbar'),
    roles: ['Admin']
  },
  {
    index: '6',
    route: '/admin/articles',
    icon: Document,
    title: t('admin.general.side.menu.articles'),
    roles: ['Admin']
  },
  {
    index: '7',
    route: '/admin/categories',
    icon: Folder,
    title: t('admin.general.side.menu.categories'),
    roles: ['Admin']
  },
  {
    index: '8',
    route: '/admin/series',
    icon: Collection,
    title: t('admin.general.side.menu.series'),
    roles: ['Admin']
  },
  {
    index: '9',
    route: '/admin/pages',
    icon: Document,
    title: t('admin.general.side.menu.pages'),
    roles: ['Admin']
  },
  {
    index: '10',
    route: '/admin/tags',
    icon: CollectionTag,
    title: t('admin.general.side.menu.tags'),
    roles: ['Admin']
  },
  {
    index: '11',
    route: '/admin/comments',
    icon: ChatDotSquare,
    title: t('admin.general.side.menu.comments'),
    roles: ['Admin']
  },
  {
    index: '12',
    route: '/admin/members',
    icon: OfficeBuilding,
    title: t('admin.general.side.menu.members'),
    roles: ['Admin']
  },
  {
    index: '13',
    route: '/admin/users',
    icon: User,
    title: t('admin.general.side.menu.users'),
    roles: ['Admin']
  },
  {
    index: '14',
    route: '/admin/docbooks',
    icon: Notebook,
    title: t('admin.general.side.menu.docbooks'),
    roles: ['Admin']
  },
  // {
  //   index: '15',
  //   route: '/admin/logs',
  //   icon: Message,
  //   title: t('admin.general.side.menu.messages'),
  //   roles: ['Admin']
  // }
])

// 根据用户角色过滤菜单项（侧边栏显示，排除隐藏项）
const filteredMenuItems = computed(() => {
  return menuItems.value.filter((item) =>
    appStore.userRole &&
    item.roles.includes(appStore.userRole) &&
    !item.hideInSidebar
  )
})

const filteredBreadcrumbItems = computed(() => {
  return menuItems.value.filter((item) => item.index === currentNavKey.value)
})

const handleOpen = (key: string, keyPath: string[]) => {
  console.log(key, keyPath)
}
const handleClose = (key: string, keyPath: string[]) => {
  console.log(key, keyPath)
}
const handleClose1 = () => {
  isCollapse.value = true
}
const handleOpen1 = () => {
  isCollapse.value = false
}

const handleAdminDarkMode = (val: boolean) => {
  // 直接切换到目标状态
  if (val !== appStore.isDark) {
    // 如果需要切换到暗色模式
    if (val) {
      appStore.setDarkMode('dark')
    } else {
      appStore.setDarkMode('light')
    }
  }
}

const handleSelect = (key: string | number, keyPath: (string | number)[]): void => {
  console.log(key, keyPath)
  currentNavKey.value = key as string
}

const navigateToCreateArticle = () => {
  window.open('/admin/articles/create', '_blank')
}

const handleNavigateToHome = () => {
  router.push('/')
}

const navigateToProfile = () => {
  router.push(`/profile/${appStore.userInfo.username}`)
}

const navigateToChangePassword = () => {
  router.push('/change-password')
}

const handleLogout = () => {
  // 清除用户信息和token
  appStore.clearUserInfo()
  router.push('/login')
}

// 使用统一的移动端检测系统
const { isMobile } = useMobileDetection(768)

// 计算用户是否已认证
const isAuthenticated = computed(() => !!appStore.token)

onMounted(async () => {
  // 初始化通知功能 - 仅在用户已认证时启动
  if (isAuthenticated.value) {
    await loadNotificationStatus()
    startNotificationPolling()
  }
  document.addEventListener('visibilitychange', handleVisibilityChange)

  // 如果是 WebSocket 模式，监听通知消息
  // @ts-ignore
  if (appStore.messagePushMethod === 'websocket') {
    try {
      const { wsService } = await import('@/api/services/websocket')
      wsNotificationHandler = (data: any) => {
        console.log('[AdminLayout] 收到 WebSocket 通知:', data)
        hasNotificationDot.value = true
        // 通知 NotificationPanel 添加新消息
        if (notificationPanelRef.value?.addNotification) {
          notificationPanelRef.value.addNotification(data)
        }
      }
      wsService.on('notification', wsNotificationHandler)
      console.log('[AdminLayout] WebSocket 通知监听已注册')
    } catch (error) {
      console.error('[AdminLayout] WebSocket 服务加载失败:', error)
    }
  }
})

// 监听认证状态变化，动态启动/停止通知轮询
watch(isAuthenticated, (authenticated) => {
  if (authenticated) {
    // 用户已登录，启动通知功能
    loadNotificationStatus()
    startNotificationPolling()
  } else {
    // 用户已登出，停止通知轮询
    stopNotificationPolling()
    hasNotificationDot.value = false
  }
})

onUnmounted(() => {
  // 清理通知相关资源
  stopNotificationPolling()
  document.removeEventListener('visibilitychange', handleVisibilityChange)

  // 清理 WebSocket 监听器
  if (wsNotificationHandler) {
    import('@/api/services/websocket').then(({ wsService }) => {
      wsService.off('notification', wsNotificationHandler!)
      console.log('[AdminLayout] WebSocket 通知监听已清理')
    })
  }
})

const handleMenuClick = (command: string) => {
  // 在menuItems中查找command对应的index
  const item = menuItems.value.find((item) => item.route === command)
  if (item) {
    currentNavKey.value = item.index
  }
  router.push(command)
}

// 处理移动端用户下拉菜单命令
const handleUserMenuCommand = (command: string) => {
  switch (command) {
    case 'create':
      navigateToCreateArticle()
      break
    case 'home':
      handleNavigateToHome()
      break
    case 'toggle-theme':
      handleAdminDarkMode(!appStore.isDark)
      break
    case 'toggle-language':
      handleChange(language.value === 'zh-CN' ? 'en-US' : 'zh-CN')
      break
    case 'notifications':
      // 跳转到通知页面
      router.push('/notifications')
      break
    case 'profile':
      navigateToProfile()
      break
    case 'change-password':
      navigateToChangePassword()
      break
    case 'logout':
      handleLogout()
      break
  }
}

// 监听路由变化，更新当前导航key
watch(() => route.path, (newPath) => {
  const item = menuItems.value.find((item) => item.route === newPath)
  if (item) {
    currentNavKey.value = item.index
  }
}, { immediate: true })
</script>

<style scoped>
.flex-grow {
  flex-grow: 1;
}

.admin-layout {
  height: 100vh;
}

.admin-sidebar {
  background: #001529;
}

.el-menu-vertical-demo:not(.el-menu--collapse) {
  width: 200px;
  min-height: 400px;
}

.admin-header-wrap {
  width: 100%;
  padding: 0 20px;
  /* border-bottom: 1px solid #e8e8e8; */
  border-bottom: 1px solid var(--el-menu-border-color);
  background-image: radial-gradient(transparent 1px, var(--el-menu-bg-color) 1px);
  background-size: 4px 4px;
  backdrop-filter: saturate(50%) blur(4px);
}

.mobile-admin-header {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
}

.admin-header {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 10px;
}

.admin-container {
  height: calc(100% - 64px);
}

.admin-main {
  height: 100%;
}

.admin-breadcrumb {
  width: 100%;
  padding: 20px;
  height: 60px;
  background-color: var(--el-menu-bg-color);
}

.admin-content {
  overflow-y: auto;
  height: 100%;
  padding: 0 20px;
}

.header-name {
  font-size: 2rem;
  font-weight: bold;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  padding-right: 20px;
}

.round-button {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: transparent;
  display: flex;
  justify-content: center;
  align-items: center;
}

.round-button:hover {
  background: #f5f5f5;
  color: var(--el-color-primary);
}

.role-tag {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 12px;
}

.role-admin {
  background-color: #fef3c7;
  color: #d97706;
  border-color: #fef3c7;
}

.role-editor {
  background-color: #dffdee;
  color: #08a360;
  border-color: #c7fed9;
}

.language-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  margin-right: 5px;
}

.language-icon svg {
  width: 16px !important;
  height: 16px !important;
}

.el-dropdown-link {
  cursor: pointer;
  color: var(--el-color-text);
  display: flex;
  align-items: center;
  border: none;
  outline: none;
}

.el-dropdown-link:hover {
  border: none;
  outline: none;
  color: var(--el-menu-hover-text-color);
}

/* 通知图标样式 */
.notification-icon-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.notification-icon-wrapper:hover {
  color: var(--el-color-primary);
  background: var(--el-fill-color-light);
}

.notification-bell {
  color: var(--el-text-color-regular);
}

.notification-badge-dot {
  position: absolute;
  top: 4px;
  right: 4px;
}

.notification-badge-dot :deep(.el-badge__content.is-dot) {
  width: 8px;
  height: 8px;
}

/* 管理后台移动端全局样式 */
@media (max-width: 767px) {
  .admin-content {
    overflow-y: auto;
    height: 100%;
    padding: 0 10px;
  }

  /* 优化所有对话框 */
  :deep(.el-dialog) {
    width: 95% !important;
    margin: 0 auto;
  }

  :deep(.el-dialog__header) {
    padding: 16px;
  }

  :deep(.el-dialog__body) {
    padding: 16px;
  }

  :deep(.el-dialog__footer) {
    padding: 12px 16px;
  }

  /* 优化所有抽屉 */
  :deep(.el-drawer) {
    width: 100% !important;
  }

  :deep(.el-drawer__header) {
    padding: 16px;
    margin-bottom: 0;
  }

  :deep(.el-drawer__body) {
    padding: 16px;
  }

  /* 优化所有表单 */
  :deep(.el-form-item__label) {
    width: 100% !important;
    text-align: left;
    margin-bottom: 8px;
    line-height: 1.5;
  }

  :deep(.el-form-item__content) {
    margin-left: 0 !important;
  }

  /* 优化所有卡片 */
  :deep(.el-card) {
    margin-bottom: 12px;
    border-radius: 8px;
  }

  :deep(.el-card__header) {
    padding: 12px 16px;
  }

  :deep(.el-card__body) {
    padding: 16px;
  }

  /* 优化按钮组 */
  :deep(.el-button-group) {
    display: flex;
    flex-wrap: wrap;
  }

  /* 优化分页 */
  :deep(.el-pagination__sizes),
  :deep(.el-pagination__jump) {
    display: none;
  }

  :deep(.btn-prev),
  :deep(.btn-next),
  :deep(.el-pager li) {
    min-width: 32px;
    height: 32px;
    line-height: 32px;
    font-size: 14px;
  }

  /* 优化标签页 */
  :deep(.el-tabs__header) {
    margin: 0 0 16px 0;
  }

  :deep(.el-tabs__item) {
    font-size: 14px;
    padding: 0 12px;
  }

  :deep(.el-tabs__nav-wrap::after) {
    height: 2px;
  }

  /* 优化面包屑 */
  :deep(.el-breadcrumb) {
    font-size: 12px;
  }

  :deep(.el-breadcrumb__item) {
    display: inline-flex;
    align-items: center;
  }

  /* 优化输入框防止iOS缩放 */
  :deep(.el-input__inner),
  :deep(.el-textarea__inner) {
    font-size: 16px;
  }

  /* 优化下拉菜单 */
  :deep(.el-dropdown-menu) {
    max-width: 280px;
  }

  /* 优化选择器 */
  :deep(.el-select) {
    width: 100%;
  }

  /* 优化日期选择器 */
  :deep(.el-date-editor) {
    width: 100%;
  }

  /* 优化上传组件 */
  :deep(.el-upload-dragger) {
    padding: 20px;
  }

  /* 优化开关 */
  :deep(.el-switch) {
    transform: scale(0.9);
  }

  /* 优化消息提示 */
  :deep(.el-message) {
    max-width: 90%;
  }

  /* 优化通知 */
  :deep(.el-notification) {
    max-width: 90%;
  }
}
</style>
