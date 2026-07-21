<template>
  <el-menu :default-active="activeIndex" class="el-menu-demo" mode="horizontal" :ellipsis="false"
    @select="handleSelect">
    <div class="wy-container hidden-xs-only">
      <el-menu-item index="0">
        <img style="width: 100px" :src="siteLogo" :alt="siteTitle" />
      </el-menu-item>
      <div class="flex-grow"></div>
      <!-- 动态渲染导航菜单 -->
      <template v-for="item in displayNavData" :key="item.id">
        <!-- 无子菜单的导航项 -->
        <el-menu-item v-if="!item.children || item.children.length === 0" :index="item.id.toString()">
          <router-link :to="item.url || '/'" class="wy-nav-link">
            {{ item.label }}
          </router-link>
        </el-menu-item>
        <!-- 有子菜单的导航项 -->
        <el-sub-menu v-else :index="`nav-${item.id}`">
          <template #title>{{ item.label }}</template>
          <el-menu-item-group>
            <!-- 第二级菜单 -->
            <template v-for="child in item.children" :key="`child-${child.id}`">
              <el-menu-item v-if="!child.children || child.children.length === 0"
                :index="`nav-${item.id}-sub-${child.id}`">
                <router-link :to="child.url || `/${child.slug || child.value || ''}`" class="wy-nav-link">
                  {{ child.label || child.name }}
                </router-link>
              </el-menu-item>
              <el-sub-menu v-else :index="`nav-${item.id}-sub-${child.id}`">
                <template #title>{{ child.label || child.name }}</template>
                <el-menu-item-group>
                  <!-- 第三级菜单 -->
                  <template v-for="grandChild in child.children" :key="`grandchild-${grandChild.id}`">
                    <el-menu-item v-if="!grandChild.children || grandChild.children.length === 0"
                      :index="`nav-${item.id}-sub-${child.id}-item-${grandChild.id}`">
                      <router-link :to="grandChild.url || `/${grandChild.slug || grandChild.value || ''}`"
                        class="wy-nav-link">
                        {{ grandChild.label || grandChild.name }}
                      </router-link>
                    </el-menu-item>
                    <el-sub-menu v-else :index="`nav-${item.id}-sub-${child.id}-item-${grandChild.id}`">
                      <template #title>{{ grandChild.label || grandChild.name }}</template>
                      <el-menu-item-group>
                        <!-- 第四级菜单 -->
                        <el-menu-item v-for="greatGrandChild in grandChild.children"
                          :key="`greatgrandchild-${greatGrandChild.id}`"
                          :index="`nav-${item.id}-sub-${child.id}-item-${grandChild.id}-child-${greatGrandChild.id}`">
                          <router-link :to="greatGrandChild.url ||
                            `/${greatGrandChild.slug || greatGrandChild.value || ''}`
                            " class="wy-nav-link">
                            {{ greatGrandChild.label || greatGrandChild.name }}
                          </router-link>
                        </el-menu-item>
                      </el-menu-item-group>
                    </el-sub-menu>
                  </template>
                </el-menu-item-group>
              </el-sub-menu>
            </template>
          </el-menu-item-group>
        </el-sub-menu>
      </template>
      <div class="flex-grow2">
        <div class="right-item">
          <el-button :icon="Search" circle @click="dialogVisible = true" />

        </div>
        <!-- 通知图标 -->
        <div class="right-item" v-if="isAuthenticated">
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
        </div>
        <div class="right-item">
          <el-tooltip class="box-item" effect="dark" :content="darkTip" placement="bottom"><el-switch v-model="darkMode"
              :active-action-icon="Moon" :inactive-action-icon="Sunny"
              @change="handleChangeDark"></el-switch></el-tooltip>
        </div>
        <div class="right-item">
          <el-dropdown :hide-on-click="false" @command="handleChange">
            <span class="el-dropdown-link">
              <IconifyIcon icon="heroicons:language" style="font-size: 24px"
                :color="darkMode ? '#FFFFFFFF' : 'currentColor'" :stroke="darkMode ? '#FFFFFFFF' : 'currentColor'" />
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item v-for="item in options" :key="item.value" :command="item.value">{{
                  item.label
                  }}</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
        <div class="right-item" v-if="isAuthenticated && appStore.userInfo.username">
          <el-popover :width="300"
            popper-style="box-shadow: rgb(14 18 22 / 35%) 0px 10px 38px -10px, rgb(14 18 22 / 20%) 0px 10px 20px -15px; padding: 5px;"
            placement="bottom-end">
            <template #reference>
              <el-avatar :src="appStore.userInfo.profile_image || defaultAvatar" />
            </template>
            <template #default>
              <div class="wy-menu-wrapper">
                <div class="wy-menu-item">
                  <el-avatar :size="50" :src="appStore.userInfo.profile_image || defaultAvatar" style="margin: 5px" />
                  <div style="flex: 1">
                    <p class="demo-rich-content__name" style="margin: 0; font-weight: 500">
                      {{ appStore.userInfo.full_name || appStore.userInfo.username }}
                      <el-tag v-if="appStore.userRole" size="small" style="margin-left: 8px">{{
                        getRoleDisplayName(appStore.userRole) }}</el-tag>
                    </p>
                    <p class="demo-rich-content__mention"
                      style="margin: 0; font-size: 14px; color: var(--el-color-info)">
                      @{{ appStore.userInfo.username }}
                    </p>
                  </div>
                </div>
                <div class="wy-menu-divider"></div>
                <div class="wy-menu-item" @click="navigateToBookmarks">
                  <IconifyIcon icon="material-symbols-light:bookmarks-outline"
                    style="font-size: 20px; margin-top: 5px; margin-left: 5px" />
                  <p style="margin: 0; font-size: 14px">{{ $t('navbar.usercenter.bookmarks') }}</p>
                </div>
                <div class="wy-menu-item" @click="navigateToHistory">
                  <IconifyIcon icon="material-symbols-light:history"
                    style="font-size: 20px; margin-top: 5px; margin-left: 5px" />
                  <p style="margin: 0; font-size: 14px">{{ $t('navbar.usercenter.history') }}</p>
                </div>
                <div class="wy-menu-item" @click="navigateToProfile">
                  <IconifyIcon icon="hugeicons:account-setting-03"
                    style="font-size: 20px; margin-top: 5px; margin-left: 5px" />
                  <p style="margin: 0; font-size: 14px">{{ $t('navbar.usercenter.profile') }}</p>
                </div>
                <div class="wy-menu-item" @click="navigateToMyArticles"
                  v-if="appStore.userRole == 'Author' || appStore.userRole == 'Contributor'">
                  <IconifyIcon icon="material-symbols-light:edit-square-outline"
                    style="font-size: 20px; margin-top: 5px; margin-left: 5px" />
                  <p style="margin: 0; font-size: 14px">{{ $t('navbar.usercenter.write') }}</p>
                </div>
                <div class="wy-menu-item" @click="navigateToBackend" v-if="appStore.userRole == 'Admin'">
                  <IconifyIcon icon="carbon:cloud-service-management" width="20" height="20"
                    style="font-size: 20px; margin-top: 5px; margin-left: 5px" />
                  <p style="margin: 0; font-size: 14px">{{ $t('navbar.usercenter.dashboard') }}</p>
                </div>
                <div class="wy-menu-divider"></div>
                <div class="wy-menu-item" @click="handleLogout">
                  <IconifyIcon icon="material-symbols-light:logout-rounded"
                    style="font-size: 20px; margin-top: 5px; margin-left: 5px" />
                  <p style="margin: 0; font-size: 14px">{{ $t('navbar.usercenter.logout') }}</p>
                </div>
              </div>
            </template>
          </el-popover>
        </div>
        <div class="right-item" v-else>
          <el-button v-if="appStore.enable_register" type="default" text @click="handleRegister($event)">{{
            $t('navbar.item.register')
            }}</el-button>
          <el-button type="primary" text @click="handleLogin($event)">{{
            $t('navbar.item.login')
            }}</el-button>
        </div>
      </div>
    </div>

    <!--移动端导航菜单-->
    <div class="wy-container hidden-sm-and-up">
      <el-menu-item index="0" @click="navigateToHome">
        <img style="width: 120px" :src="siteLogo" :alt="siteTitle" />
      </el-menu-item>

      <!--移动端导航菜单 - 紧跟在logo后面-->
      <el-dropdown trigger="click" placement="bottom-start" @command="handleNavMenuClick">
        <span class="mobile-nav-trigger">
          <iconify-icon icon="material-symbols-light:menu" :size="24" />
          <el-icon>
            <ArrowDown></ArrowDown>
          </el-icon>
        </span>

        <template #dropdown>
          <el-dropdown-menu class="mobile-nav-dropdown">
            <!--使用自定义多级菜单组件-->
            <MobileNavMenu :nav-items="displayNavData" @item-click="handleNavItemClick" />

            <!-- <el-dropdown-item divided @click="openSearch">
              <el-icon>
                <Search />
              </el-icon>
              {{ $t('navbar.search.btn.text') }}
            </el-dropdown-item> -->
          </el-dropdown-menu>
        </template>
      </el-dropdown>

      <div class="flex-grow"></div>

      <!--移动端右侧操作按钮组-->
      <div class="mobile-right-actions">
        <!--搜索按钮-->
        <el-button :icon="Search" circle @click="openSearch" />

        <!--更多按钮（包含深色模式、语言、通知）-->
        <el-dropdown trigger="click" @command="handleMoreMenuClick">
          <el-button :icon="More" circle />
          <template #dropdown>
            <el-dropdown-menu>
              <!--深色模式切换-->
              <el-dropdown-item :command="'toggle-dark'">
                <el-icon>
                  <component :is="darkMode ? Moon : Sunny" />
                </el-icon>
                {{ darkMode ? $t('navbar.light.tip') : $t('navbar.dark.tip') }}
              </el-dropdown-item>

              <!--语言切换-->
              <el-dropdown-item :command="'language'">
                <span class="language-icon">
                  <IconifyIcon icon="heroicons:language" :width="16" :height="16"
                    :color="darkMode ? '#FFFFFFFF' : 'currentColor'" />
                </span>
                {{ $t('navbar.item.language') || 'Language' }}
              </el-dropdown-item>

              <!--消息通知-->
              <el-dropdown-item :command="'notifications'" v-if="isAuthenticated">
                <div style="display: flex; align-items: center; justify-content: space-between; width: 100%;">
                  <span style="display: flex; align-items: center;">
                    <el-icon>
                      <Bell />
                    </el-icon>
                    {{ $t('navbar.item.notifications') || 'Notifications' }}
                  </span>
                  <el-badge is-dot :hidden="!hasNotificationDot" />
                </div>
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <!--用户头像下拉菜单（简化版，只包含用户相关操作）-->
        <el-dropdown trigger="click" @command="handleUserMenuClick" v-if="isAuthenticated">
          <el-avatar :size="40" :src="appStore.userInfo.profile_image || defaultAvatar" />
          <template #dropdown>
            <el-dropdown-menu>
              <!--用户信息头部-->
              <el-dropdown-item disabled style="opacity: 1; cursor: default; padding: 12px 20px">
                <div style="display: flex; align-items: center; gap: 10px">
                  <el-avatar :size="40" :src="appStore.userInfo.profile_image || defaultAvatar" />
                  <div>
                    <div style="font-weight: 500">{{ appStore.userInfo.full_name || appStore.userInfo.username }}</div>
                    <div style="font-size: 12px; color: var(--el-color-info)">@{{ appStore.userInfo.username }}</div>
                  </div>
                </div>
              </el-dropdown-item>
              <el-dropdown-item divided :command="'bookmarks'">
                <IconifyIcon icon="material-symbols-light:bookmarks-outline"
                  style="font-size: 18px; margin-right: 8px" />
                {{ $t('navbar.usercenter.bookmarks') }}
              </el-dropdown-item>
              <el-dropdown-item :command="'history'">
                <IconifyIcon icon="material-symbols-light:history" style="font-size: 18px; margin-right: 8px" />
                {{ $t('navbar.usercenter.history') }}
              </el-dropdown-item>
              <el-dropdown-item :command="'profile'">
                <IconifyIcon icon="hugeicons:account-setting-03" style="font-size: 18px; margin-right: 8px" />
                {{ $t('navbar.usercenter.profile') }}
              </el-dropdown-item>
              <el-dropdown-item v-if="appStore.userRole == 'Author' || appStore.userRole == 'Contributor'"
                :command="'my-articles'">
                <IconifyIcon icon="material-symbols-light:edit-square-outline"
                  style="font-size: 18px; margin-right: 8px" />
                {{ $t('navbar.usercenter.write') }}
              </el-dropdown-item>
              <el-dropdown-item v-if="appStore.userRole == 'Admin'" :command="'backend'">
                <IconifyIcon icon="carbon:cloud-service-management" style="font-size: 18px; margin-right: 8px" />
                {{ $t('navbar.usercenter.dashboard') }}
              </el-dropdown-item>
              <el-dropdown-item divided :command="'logout'">
                <IconifyIcon icon="material-symbols-light:logout-rounded" style="font-size: 18px; margin-right: 8px" />
                {{ $t('navbar.usercenter.logout') }}
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <!--未登录状态显示登录按钮-->
        <el-button v-else type="primary" size="small" @click="handleLogin">
          {{ $t('navbar.item.login') }}
        </el-button>
      </div>
    </div>

    <el-dialog v-model="dialogVisible" fullscreen center :show-close="false" class="search-dialog">
      <el-button class="search-close-btn" :icon="Close" circle @click="dialogVisible = false" />
      <div class="wy-search-input-wrap">
        <el-input v-model="keywords" class="wy-search-input" :placeholder="$t('navbar.search.input.placeholder')"
          clearable size="large" @keyup.enter="handleSearch" ref="searchInputRef" />
      </div>
      <template #footer>
        <div class="wy-dialog-footer">
          <el-button :icon="Search" size="large" round @click="handleSearch">
            {{ $t('navbar.search.btn.text') }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </el-menu>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ArrowDown, Sunny, Moon, Search, Bell, Close, More } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { ElMessage } from 'element-plus'
import IconifyIcon from '../components/IconIfy.vue'
import NotificationPanel from './NotificationPanel.vue'
import MobileNavMenu from './MobileNavMenu.vue'
import 'element-plus/theme-chalk/display.css'
import { getSiteNavList } from '@/api/services/nav'
import * as notificationApi from '@/api/services/notifications'
import { docBookApi } from '@/api/services/doc'

const router = useRouter()
const appStore = useAppStore()
const { t } = useI18n()
const dialogVisible = ref(false)
const keywords = ref('')
const searchInputRef = ref()
const defaultAvatar = '/src/assets/avatar.png'
const defaultLogo = '/src/assets/wow_blog_logo.svg'
const siteLogo = computed(() => appStore.site_logo || defaultLogo)
const siteTitle = computed(() => appStore.site_title || 'WOW Blog')
const language = computed(() => appStore.language || 'zh-CN')

// 定义导航项类型
interface NavItem {
  id: number
  label?: string
  name?: string
  nav_type?: 'sys' | 'user'
  type?: string
  value?: string
  slug?: string
  url?: string
  sort?: number
  status: number
  children?: NavItem[]
}


// 导航数据
const navList = ref<NavItem[]>([])

// 文档书列表
const docBooks = ref<any[]>([])

// 过滤后的显示导航数据
const displayNavData = computed(() => {
  const filtered = navList.value
    .filter((item) => item.status === 1)
    .sort((a, b) => (a.sort || 0) - (b.sort || 0))

  // 处理导航数据，添加文档书子菜单和URL
  return filtered.map(item => processNavItem(item))
})

// 处理导航项，添加文档书子菜单和URL
const processNavItem = (item: NavItem): NavItem => {
  // 处理系统文档导航：需要动态添加文档书列表作为子菜单
  if (item.nav_type === 'sys' && item.type === 'link' && item.value === 'doc') {
    return {
      ...item,
      children: docBooks.value.map(docBook => ({
        id: Number(`docbook-${docBook.id}`),
        label: docBook.name,
        name: docBook.name,
        slug: docBook.slug,
        url: `/docs/${docBook.slug}`,
        status: 1
      }))
    }
  }

  // 处理用户添加的文档导航
  if (item.nav_type === 'user' && item.type === 'doc' && item.value) {
    const docBook = docBooks.value.find(db => String(db.id) === String(item.value))
    if (docBook) {
      return {
        ...item,
        url: `/docs/${docBook.slug}`
      }
    }
  }

  // 处理子菜单
  if (item.children && item.children.length > 0) {
    return {
      ...item,
      children: item.children.map(child => processNavItem(child))
    }
  }

  return item
}

// 计算当前激活的菜单项
const activeIndex = computed(() => {
  const path = router.currentRoute.value.path
  // 查找匹配的导航项ID
  const findActiveNavId = (items: NavItem[]): string => {
    for (const item of items) {
      if (item.url === path || item.value === path || item.slug === path) {
        return item.id.toString()
      }
      if (item.children && item.children.length > 0) {
        const childResult = findActiveNavId(item.children)
        if (childResult) return childResult
      }
    }
    return '0' // 默认值
  }
  return findActiveNavId(navList.value) || '0'
})

// 获取导航数据
const fetchNavList = async () => {
  try {
    const response = await getSiteNavList()
    if (response.code === 1 && response.data) {
      navList.value = response.data
    }
  } catch (error) {
    console.error('获取导航数据失败:', error)
  }
}

// 获取文档书列表
const fetchDocBooks = async () => {
  try {
    const response = await docBookApi.list({ skip: 0, limit: 100 })
    if (response.code === 1 && response.data) {
      docBooks.value = response.data
    }
  } catch (error) {
    console.error('获取文档书列表失败:', error)
  }
}

const handleSelect = (key: string, keyPath: string[]) => {
  console.log(key, keyPath)
}
const props = defineProps({
  isDark: {
    type: Boolean,
    required: false
  }
})
// 确保darkMode与props.isDark保持同步
const darkMode = ref(props.isDark || false)
const darkTip = ref(t('navbar.dark.tip'))

// 监听props.isDark变化，确保同步
watch(
  () => props.isDark,
  (newVal) => {
    darkMode.value = newVal || false
    if (darkMode.value) {
      darkTip.value = t('navbar.light.tip')
    } else {
      darkTip.value = t('navbar.dark.tip')
    }
  }
)

const options = ref([
  { label: '中文', value: 'zh-CN' },
  { label: 'English', value: 'en-US' }
])
const emits = defineEmits(['selectLanguage', 'changeDarkMode'])
const currentLanguage = ref(language.value)

// 桌面端和移动端共用的语言切换函数
const handleChange = (command: string | number | object) => {
  const newLanguage = command as string
  console.log('切换前台语言:', newLanguage)

  // 更新本地状态
  currentLanguage.value = newLanguage

  // 更新 appStore 中的 language（前台专用）
  appStore.language = newLanguage

  // 保存到 localStorage（前台使用 blog-locale 键）
  localStorage.setItem('blog-locale', newLanguage)

  // 发出事件以便父组件也能响应
  emits('selectLanguage', newLanguage)

  // 重新加载页面以应用新语言
  location.reload()
}
const handleChangeDark = (val: any) => {
  console.log('切换暗黑模式:', val)
  // 先更新本地状态
  darkMode.value = val

  // 更新提示文本
  if (val) {
    darkTip.value = t('navbar.light.tip')
  } else {
    darkTip.value = t('navbar.dark.tip')
  }

  // 通知父组件更新store
  emits('changeDarkMode', val)
}

// 初始化提示文本
if (darkMode.value) {
  darkTip.value = t('navbar.light.tip')
}

const isAuthenticated = computed(() => {
  return !!appStore.token && !!appStore.userRole
})
console.log(isAuthenticated.value)
const handleLogin = (e?: Event) => {
  if (e) e.stopPropagation() // 阻止事件冒泡

  // 检查当前是否已登录
  if (isAuthenticated.value) {
    // 已登录状态，先清除认证信息再跳转到登录页
    // appStore.clearUserInfo()
    // 使用replace避免回退到已登录状态的页面
    //router.replace('/login')
    ElMessage({
      message: '您已经登录，无需重复登录！',
      type: 'success'
    })
  } else {
    // 未登录状态，直接跳转到登录页
    router.push('/login')
  }
}

const handleRegister = (e?: Event) => {
  if (e) e.stopPropagation()
  router.push('/register')
}

const navigateToProfile = () => {
  router.push(`/profile/${appStore.userInfo.username}`)
}

const navigateToBookmarks = () => {
  router.push('/bookmarks')
}

const navigateToBackend = () => {
  router.push('/admin/dashboard')
}

const navigateToHistory = () => {
  router.push('/history')
}

const navigateToMyArticles = () => {
  router.push('/my-articles')
}

// 点击搜索按钮，跳转到搜索结果页
const handleSearch = () => {
  if (keywords.value.trim()) {
    dialogVisible.value = false
    router.push({ path: '/search', query: { q: keywords.value.trim() } })
  }
}

const handleLogout = () => {
  appStore.clearUserInfo()
  router.push('/login')
}

// 移动端：点击Logo返回首页
const navigateToHome = () => {
  router.push('/')
}

// 移动端：导航菜单点击处理
const handleNavMenuClick = (command: string) => {
  // 处理简单命令（如 'search'）
  if (command === 'search') {
    dialogVisible.value = true
    // 聚焦搜索输入框
    setTimeout(() => {
      searchInputRef.value?.focus()
    }, 100)
    return
  }

  // 处理 JSON 格式命令（如导航）
  try {
    const data = JSON.parse(command)
    if (data.type === 'nav') {
      router.push(data.url)
    } else if (data.type === 'search') {
      dialogVisible.value = true
      setTimeout(() => {
        searchInputRef.value?.focus()
      }, 100)
    }
  } catch (error) {
    console.error('解析菜单命令失败:', error)
  }
}

// 移动端：用户菜单点击处理
const handleUserMenuClick = (command: string) => {
  switch (command) {
    case 'login':
      handleLogin()
      break
    case 'register':
      handleRegister()
      break
    case 'profile':
      navigateToProfile()
      break
    case 'bookmarks':
      navigateToBookmarks()
      break
    case 'history':
      navigateToHistory()
      break
    case 'my-articles':
      navigateToMyArticles()
      break
    case 'backend':
      navigateToBackend()
      break
    case 'logout':
      handleLogout()
      break
  }
}

// 移动端：导航项点击处理（来自 MobileNavMenu 组件）
const handleNavItemClick = (item: any) => {
  // 如果是首页或者 url 为空，跳转到首页
  if (!item.url || item.url === '' || item.url === '/') {
    router.push('/')
  } else if (item.url) {
    router.push(item.url)
  }
}

// 移动端：打开搜索对话框
const openSearch = () => {
  dialogVisible.value = true
  // 聚焦搜索输入框
  setTimeout(() => {
    searchInputRef.value?.focus()
  }, 100)
}

// 移动端：更多菜单点击处理
const handleMoreMenuClick = (command: string) => {
  switch (command) {
    case 'toggle-dark':
      toggleDarkMode()
      break
    case 'language': {
      // 直接切换到另一种语言（与管理后台行为一致）
      const newLanguage = currentLanguage.value === 'zh-CN' ? 'en-US' : 'zh-CN'
      handleChange(newLanguage)
      break
    }
    case 'notifications':
      openNotifications()
      break
  }
}

// 移动端：切换深色模式
const toggleDarkMode = () => {
  const newValue = !darkMode.value
  darkMode.value = newValue
  darkTip.value = newValue ? t('navbar.light.tip') : t('navbar.dark.tip')
  emits('changeDarkMode', newValue)
}

// 移动端：打开通知页面
const openNotifications = () => {
  // 跳转到通知页面
  router.push('/notifications')
}

// 角色名称映射
const getRoleDisplayName = (role: string): string => {
  const roleMap: Record<string, string> = {
    'Admin': '管理员',
    'Editor': '编辑',
    'Author': '作者',
    'Contributor': '投稿者',
    'User': '普通用户'
  }
  return roleMap[role] || role
}

// 通知相关
const hasNotificationDot = ref(false)
const notificationPanelRef = ref()
let notificationPollingTimer: ReturnType<typeof setInterval> | null = null
let wsNotificationHandler: ((data: any) => void) | null = null

// 加载通知状态（是否有未读通知）
const loadNotificationStatus = async () => {
  if (!isAuthenticated.value) return
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
    // 静默处理错误，避免频繁的错误提示
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
    console.log('[SiteNav] WebSocket 模式，不启动轮询')
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
  console.log('[SiteNav] 轮询模式已启动')
}

// 停止通知轮询
const stopNotificationPolling = () => {
  if (notificationPollingTimer) {
    clearInterval(notificationPollingTimer)
    notificationPollingTimer = null
    console.log('[SiteNav] 轮询已停止')
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

// 初始化
onMounted(async () => {
  fetchNavList()
  fetchDocBooks()
  await loadNotificationStatus()
  // 只在用户已认证时启动轮询
  if (isAuthenticated.value) {
    startNotificationPolling()
  }
  // 监听页面可见性变化
  document.addEventListener('visibilitychange', handleVisibilityChange)

  // 如果是 WebSocket 模式，监听通知消息
  if (appStore.messagePushMethod === 'websocket') {
    try {
      const { wsService } = await import('@/api/services/websocket')
      wsNotificationHandler = (data: any) => {
        console.log('[SiteNav] 收到 WebSocket 通知:', data)
        hasNotificationDot.value = true
        // 通知 NotificationPanel 添加新消息
        if (notificationPanelRef.value?.addNotification) {
          notificationPanelRef.value.addNotification(data)
        }
      }
      wsService.on('notification', wsNotificationHandler)
      console.log('[SiteNav] WebSocket 通知监听已注册')
    } catch (error) {
      console.error('[SiteNav] WebSocket 服务加载失败:', error)
    }
  }
})

// 监听认证状态变化
watch(isAuthenticated, (newValue, oldValue) => {
  console.log('[SiteNav] 认证状态变化:', oldValue, '->', newValue)
  if (newValue && !oldValue) {
    // 从未认证变为已认证，启动轮询
    console.log('[SiteNav] 用户已登录，启动轮询')
    loadNotificationStatus()
    startNotificationPolling()
  } else if (!newValue && oldValue) {
    // 从已认证变为未认证，停止轮询
    console.log('[SiteNav] 用户已登出，停止轮询')
    stopNotificationPolling()
  }
})

onUnmounted(() => {
  stopNotificationPolling()
  document.removeEventListener('visibilitychange', handleVisibilityChange)

  // 清理 WebSocket 监听器
  if (wsNotificationHandler) {
    import('@/api/services/websocket').then(({ wsService }) => {
      wsService.off('notification', wsNotificationHandler!)
      console.log('[SiteNav] WebSocket 通知监听已清理')
    })
  }
})

// 定义组件名称
defineOptions({ name: 'SiteNav' })
</script>

<style scoped>
.flex-grow {
  flex-grow: 1;
}

.flex-grow2 {
  flex-grow: 2;
  display: flex;
  justify-content: flex-end;
}

.el-dropdown-link {
  cursor: pointer;
  color: var(--el-color-black);
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

.right-item {
  height: 100%;
  margin-left: 20px;
  display: flex;
  align-items: center;
}

.el-menu-demo {
  display: flex;
  justify-content: center;
}

.wy-container {
  display: flex;
  width: 1200px;
}

.wy-search-input-wrap {
  width: 100%;
  height: 500px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.wy-search-input {
  width: 80%;
  height: 50px;
  border-radius: 50px;
  font-size: 20px;
}

.wy-dialog-footer {
  text-align: center;
}

.search-close-btn {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 9999;
  width: 40px;
  height: 40px;
  font-size: 20px;
}

.wy-nav-link {
  color: var(--el-menu-text-color);
  text-decoration: none;
}

.wy-nav-link:hover {
  color: var(--el-menu-active-color);
  cursor: pointer;
  text-decoration: none;
}

.wy-menu-wrapper {
  width: 100%;
  display: flex;
  gap: 5px;
  flex-direction: column;
  justify-content: flex-start;
  align-items: flex-start;
}

.wy-menu-item {
  width: 100%;
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 10px;
  border-radius: 2px;
}

.wy-menu-item:hover {
  color: var(--el-menu-active-color);
  cursor: pointer;
  background-color: var(--el-menu-hover-bg-color);
}

.wy-menu-divider {
  border-top: 1px var(--el-border-color) var(--el-border-style);
  display: block;
  height: 1px;
  margin: 5px 0;
  width: 100%;
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
  background-color: var(--el-fill-color-light);
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

@media (min-width: 768px) {
  .wy-hidden-small {}

  .wy-hidden-big {
    display: none;
  }
}

@media only screen and (max-width: 767px) {
  .wy-container {
    display: flex;
    width: 100%;
    align-items: center;
  }

  .wy-hidden-small {
    display: none;
  }

  .wy-hidden-big {
    display: flex;
  }

  /* 移动端下拉菜单样式 */
  .el-dropdown-menu {
    max-width: 280px;
  }

  .el-dropdown-menu__item {
    padding: 12px 20px;
    line-height: 1.5;
  }

  .el-dropdown-menu__item i {
    margin-right: 8px;
  }

  /* 移动端导航触发按钮 */
  .mobile-nav-trigger {
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    padding: 8px;
    margin-left: -12px;
    border-radius: 4px;
    transition: background-color 0.2s;
  }

  .mobile-nav-trigger:hover {
    color: var(--el-color-primary);
    background-color: var(--el-menu-hover-bg-color);
  }

  /* 移动端导航下拉菜单 */
  .mobile-nav-dropdown {
    max-width: 300px !important;
    min-width: 150px;
  }

  /* 移动端右侧操作按钮组 */
  .mobile-right-actions {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-right: 10px;
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
}
</style>
