<template>
  <div class="front-login-container">
    <!-- 背景装饰 -->
    <div class="login-background">
      <div class="bg-circle circle-1"></div>
      <div class="bg-circle circle-2"></div>
      <div class="bg-circle circle-3"></div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-card-wrapper">
      <el-card class="login-card" shadow="always">
        <!-- Logo / 网站名称 -->
        <div class="login-header">
          <h1 class="site-title">{{ appStore.site_title || $t('login.title') }}</h1>
          <p class="site-subtitle">{{ $t('login.subtitle') }}</p>
        </div>

        <!-- 登录表单 -->
        <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" class="login-form"
          @submit.prevent="handleLogin">
          <el-form-item prop="username">
            <el-input v-model="loginForm.username" :placeholder="$t('login.username_placeholder')" prefix-icon="User"
              size="large" clearable />
          </el-form-item>

          <el-form-item prop="password">
            <el-input v-model="loginForm.password" type="password" :placeholder="$t('login.password_placeholder')"
              prefix-icon="Lock" show-password size="large" @keyup.enter="handleLogin" />
          </el-form-item>

          <el-form-item class="form-options">
            <div style="width: 100%; display:flex; justify-content: space-between;">
              <el-checkbox v-model="loginForm.remember">{{ $t('login.remember_me') }}</el-checkbox>
              <el-link type="primary" underline="never" @click="handleForgotPassword">
                {{ $t('login.forgot_password') }}
              </el-link>
            </div>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" class="login-btn" :loading="loading" @click="handleLogin" size="large">
              {{ $t('login.login_button') }}
            </el-button>
          </el-form-item>
        </el-form>

        <!-- 分割线 + 社交登录按钮（仅在后台启用社交登录且有可用 provider 时显示） -->
        <template v-if="appStore.oauth_enabled && appStore.enabled_oauth_providers.length">
          <div class="divider">
            <span>{{ $t('login.or_social') }}</span>
          </div>

          <div class="social-login">
            <div class="social-icons">
              <el-tooltip v-if="appStore.enabled_oauth_providers.includes('google')" content="Google" placement="top">
                <button class="social-icon-btn" @click="handleSocialLogin('google')">
                  <Icon icon="basil:google-solid" />
                </button>
              </el-tooltip>
              <el-tooltip v-if="appStore.enabled_oauth_providers.includes('github')" content="GitHub" placement="top">
                <button class="social-icon-btn" @click="handleSocialLogin('github')">
                  <Icon icon="mdi:github" />
                </button>
              </el-tooltip>
              <el-tooltip v-if="appStore.enabled_oauth_providers.includes('gitee')" content="Gitee" placement="top">
                <button class="social-icon-btn" @click="handleSocialLogin('gitee')">
                  <Icon icon="simple-icons:gitee" />
                </button>
              </el-tooltip>
              <el-tooltip v-if="appStore.enabled_oauth_providers.includes('apple')" content="Apple" placement="top">
                <button class="social-icon-btn" @click="handleSocialLogin('apple')">
                  <Icon icon="ic:baseline-apple" />
                </button>
              </el-tooltip>
              <el-tooltip v-if="appStore.enabled_oauth_providers.includes('wechat')" content="微信" placement="top">
                <button class="social-icon-btn" @click="handleSocialLogin('wechat')">
                  <Icon icon="ri:wechat-fill" />
                </button>
              </el-tooltip>
              <el-tooltip v-if="appStore.enabled_oauth_providers.includes('qq')" content="QQ" placement="top">
                <button class="social-icon-btn" @click="handleSocialLogin('qq')">
                  <Icon icon="ri:qq-fill" />
                </button>
              </el-tooltip>
              <el-tooltip v-if="appStore.enabled_oauth_providers.includes('alipay')" content="支付宝" placement="top">
                <button class="social-icon-btn" @click="handleSocialLogin('alipay')">
                  <Icon icon="ant-design:alipay-outlined" />
                </button>
              </el-tooltip>
            </div>
          </div>
        </template>

        <!-- 注册提示 -->
        <div class="register-tip">
          {{ $t('login.no_account') }}
          <el-link type="primary" underline="never" @click="handleGoRegister">
            {{ $t('login.register_now') }}
          </el-link>
        </div>
      </el-card>

      <!-- 后台登录入口 -->
      <div class="admin-login-link">
        <el-link type="info" underline="never" href="/admin/login">
          {{ $t('login.admin_login') }}
        </el-link>
      </div>
    </div>

    <!-- 忘记密码对话框 -->
    <ForgetPasswordDialog v-model="showForgetPasswordDialog" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAppStore } from '@/stores/app'
import { ElMessage } from 'element-plus'
import { frontLoginApi, getCurrentUserInfo, exchangeOAuthToken, type FrontLoginRequest } from '@/api/services/auth'
import { getUserMe, login } from '@/api/services/user'
import { Icon } from '@iconify/vue'
import ForgetPasswordDialog from '@/components/ForgetPasswordDialog.vue'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()
const { t } = useI18n()

const loading = ref(false)
const loginFormRef = ref()
const showForgetPasswordDialog = ref(false)

const loginForm = reactive<FrontLoginRequest>({
  username: '',
  password: '',
  remember: false
})

const loginRules = {
  username: [
    { required: true, message: t('login.username_required'), trigger: 'blur' }
  ],
  password: [
    { required: true, message: t('login.password_required'), trigger: 'blur' },
    { min: 6, message: t('login.password_min_length'), trigger: 'blur' }
  ]
}

/**
 * 安全校验：登录后回跳目标必须是站内相对路径，防止开放重定向（如 //evil.com）。
 */
const isSafeRedirect = (target: string): boolean => {
  return !!target && target.startsWith('/') && !target.startsWith('//')
}

/**
 * 完整登录链：存 token → 设置登录态 → 拉取用户信息 → 加载公共配置 → 初始化消息推送。
 * 普通登录与 OAuth 登录共用此流程，确保登录态完整（修复 OAuth 登录后 store 半登录、
 * 被路由守卫踢出的 bug）。@returns 是否成功完成登录（成功后由调用方执行路由跳转）
 */
const completeLogin = async (token: string, remember = true): Promise<boolean> => {
  // 清旧 token，避免不同存储混用
  localStorage.removeItem('access_token')
  sessionStorage.removeItem('access_token')

  appStore.setLoggedInState(true)
  if (remember) {
    localStorage.setItem('access_token', token)
  } else {
    sessionStorage.setItem('access_token', token)
  }
  appStore.token = token

  try {
    const userRes = await getUserMe()
    if (userRes && userRes.code === 1 && userRes.data) {
      appStore.setUserInfo(userRes.data)
      appStore.setUserRole(userRes.data.role)
      await appStore.loadPublicConfig()
      appStore.initMessagePush()
      ElMessage.success(t('login.success'))
      return true
    }
    ElMessage.error(t('login.get_user_info_failed'))
    return false
  } catch (userError) {
    console.error('获取用户信息失败:', userError)
    ElMessage.error(t('login.get_user_info_retry'))
    return false
  }
}

const handleLogin = async () => {
  try {
    await loginFormRef.value?.validate()
    loading.value = true

    const loginRes = await login({
      username: loginForm.username,
      password: loginForm.password
    })

    if (loginRes && loginRes.code === 1) {
      const token = loginRes.access_token || loginRes.token || loginRes.data?.access_token || loginRes.data?.token
      if (!token) {
        ElMessage.error(t('login.success_but_no_token'))
        return
      }
      const ok = await completeLogin(token, loginForm.remember)
      if (ok) {
        const redirect = (route.query.redirect as string) || '/'
        router.push(isSafeRedirect(redirect) ? redirect : '/')
      }
    } else {
      ElMessage.error(loginRes?.msg || t('login.failed'))
    }
  } catch (error: any) {
    console.error('登录错误:', error)
    if (error?.response?.data?.msg) {
      ElMessage.error(error.response.data.msg)
    } else {
      ElMessage.error(t('login.login_failed_retry'))
    }
  } finally {
    loading.value = false
  }
}

const handleForgotPassword = () => {
  showForgetPasswordDialog.value = true
}

/**
 * 处理社交登录：跳转到后端 OAuth 授权端点。
 * 国内三家（微信/QQ/支付宝）在 P2 阶段实现，暂提示即将上线。
 */
const handleSocialLogin = (provider: string) => {
  // 微信/QQ 已上线；支付宝（非标准 OAuth2）待后续
  const phase3Providers = ['alipay']
  if (phase3Providers.includes(provider)) {
    ElMessage.info(t('login.oauth_login_coming'))
    return
  }

  ElMessage.info(t('login.oauth_redirecting'))
  const apiBase = import.meta.env.VITE_API_BASE_URL || '/api'
  // 把登录后目标页透传给后端（后端存 session，回调成功后带回前端）
  const redirect = (route.query.redirect as string) || '/'
  const authUrl = `${apiBase}/auth/oauth/${provider}?redirect=${encodeURIComponent(redirect)}`
  window.location.href = authUrl
}

/**
 * 处理 OAuth 回调
 * 后端回调成功后 302 回本页并带 ?oauth=success&redirect=...；前端用 httpOnly cookie
 * 调 /auth/oauth/session 换取 access_token，再走完整登录链。
 */
const checkOAuthCallback = async () => {
  const status = route.query.oauth as string | undefined
  if (!status) return

  // 先读取 redirect 再清 query（修复旧实现清了 query 才读 redirect 导致来源丢失的 bug）
  const redirect = (route.query.redirect as string) || '/'

  if (status === 'success') {
    loading.value = true
    try {
      const res = await exchangeOAuthToken()
      // 清掉 oauth 相关 query，避免刷新重复触发
      router.replace({ query: {} })
      if (res && res.code === 1 && res.data?.access_token) {
        const ok = await completeLogin(res.data.access_token, true)
        if (ok) {
          router.push(isSafeRedirect(redirect) ? redirect : '/')
        }
      } else {
        ElMessage.error(t('login.oauth_failed'))
      }
    } catch (error) {
      console.error('OAuth 换取 token 失败:', error)
      ElMessage.error(t('login.oauth_failed'))
    } finally {
      loading.value = false
    }
    return
  }

  if (status === 'error') {
    const desc = route.query.desc as string
    router.replace({ query: {} })
    ElMessage.error(desc || t('login.oauth_failed'))
  }
}

const handleGoRegister = () => {
  router.push('/register')
}

onMounted(() => {
  // 登录页面不需要调用 initTheme，避免不必要的 API 调用
  // appStore.initTheme()

  // 检查是否有 OAuth 回调的 token
  checkOAuthCallback()
})
</script>

<style scoped>
.front-login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* 背景装饰 */
.login-background {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 0;
}

.bg-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 6s ease-in-out infinite;
}

.circle-1 {
  width: 300px;
  height: 300px;
  top: -100px;
  left: -100px;
  animation-delay: 0s;
}

.circle-2 {
  width: 200px;
  height: 200px;
  bottom: -50px;
  right: -50px;
  animation-delay: 2s;
}

.circle-3 {
  width: 150px;
  height: 150px;
  top: 50%;
  right: 10%;
  animation-delay: 4s;
}

@keyframes float {

  0%,
  100% {
    transform: translateY(0) rotate(0deg);
  }

  50% {
    transform: translateY(-20px) rotate(10deg);
  }
}

/* 登录卡片 */
.login-card-wrapper {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 420px;
  padding: 20px;
}

.login-card {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  border: none;
}

:deep(.el-card__body) {
  padding: 40px;
}

/* 头部 */
.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.site-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px 0;
  color: var(--el-text-color-primary);
}

.site-subtitle {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  margin: 0;
}

/* 表单 */
.login-form {
  margin-top: 24px;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 8px;
}

/* 分割线 */
.divider {
  display: flex;
  align-items: center;
  text-align: center;
  margin: 24px 0;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid var(--el-border-color);
}

.divider span {
  padding: 0 12px;
}

/* 社交登录按钮 */
.social-login {
  margin-bottom: 24px;
}

.social-icons {
  display: flex;
  justify-content: center;
  gap: 20px;
  align-items: center;
}

.social-icon-btn {
  width: 40px;
  height: 40px;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  transition: all 0.2s ease;
  color: #999;
}

.social-icon-btn:hover {
  color: #666;
  transform: scale(1.1);
}

.social-icon-btn :deep(.iconify) {
  width: 24px;
  height: 24px;
}

/* 注册提示 */
.register-tip {
  text-align: center;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

/* 后台登录链接 */
.admin-login-link {
  text-align: center;
  margin-top: 16px;
}

/* 响应式 */
@media (max-width: 480px) {
  :deep(.el-card__body) {
    padding: 24px;
  }

  .site-title {
    font-size: 24px;
  }

  .social-icons {
    gap: 16px;
  }

  .social-icon-btn {
    width: 36px;
    height: 36px;
  }
}
</style>
