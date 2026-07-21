import router from './index'
import { useAppStore } from '@/stores/app'
import type { RouteMeta } from 'vue-router'

interface CustomRouteMeta extends RouteMeta {
  roles?: string[]
  requiresAuth?: boolean
  layout?: string
}

router.beforeEach((to, from, next) => {
  // 创建appStore实例
  const appStore = useAppStore()
  // 获取当前用户token和角色，同时检查两者作为认证状态
  const token = appStore.token
  const userRole = appStore.userRole
  const isAuthenticated = !!token && !!userRole

  // 记录路由守卫触发信息用于调试
  console.log('路由守卫触发:', {
    to: to.path,
    from: from.path,
    isAuthenticated,
    hasToken: !!token,
    hasRole: !!userRole
  })

  // 判断是否为管理后台路由
  const isAdminRoute = to.path.startsWith('/admin')

  // 处理前端登录页
  if (to.name === 'login') {
    if (isAuthenticated) {
      // 已登录用户根据角色跳转
      if (userRole === 'Admin') {
        return next('/admin/dashboard')
      }
      return next('/')
    }
    return next()
  }

  // 处理管理后台登录页
  if (to.name === 'admin-login') {
    if (isAuthenticated && userRole === 'Admin') {
      return next('/admin/dashboard')
    }
    return next()
  }

  // 获取路由元数据中的角色信息
  const routeMeta = to.meta as CustomRouteMeta

  // 检查路由是否需要认证
  const requiresAuth = routeMeta.requiresAuth || false
  if (requiresAuth && !isAuthenticated) {
    // 根据当前路由判断跳转到哪个登录页
    if (isAdminRoute) {
      return next('/admin/login')
    }
    return next('/login?redirect=' + encodeURIComponent(to.fullPath))
  }

  // 不需要权限的路由直接放行
  if (!routeMeta.roles) {
    return next()
  }

  // 检查用户角色是否有权限访问该路由
  if (userRole && routeMeta.roles.includes(userRole)) {
    next()
  } else {
    // 无权限时重定向到403页面
    next('/403')
  }
})
