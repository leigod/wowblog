<template>
  <div class="login-container">
    <el-card class="login-card">
      <div class="login-header">
        <h2>{{ $t('login.admin_login') }}</h2>
        <p>{{ $t('login.subtitle') }}</p>
      </div>
      <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" class="login-form">
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            :placeholder="$t('login.username_placeholder')"
            prefix-icon="User"
            size="large"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            :placeholder="$t('login.password_placeholder')"
            prefix-icon="Lock"
            show-password
            size="large"
          />
        </el-form-item>
        <el-form-item class="remember-me">
          <el-checkbox v-model="loginForm.remember">{{ $t('login.remember_me') }}</el-checkbox>
          <el-link type="primary" underline="never" class="forgot-password" @click="showForgetPasswordDialog = true">
            {{ $t('login.forgot_password') }}
          </el-link>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" class="login-btn" @click="handleLogin" :loading="loading"
            >{{ $t('login.login_button') }}</el-button
          >
        </el-form-item>
      </el-form>
    </el-card>

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
import { login, getUserMe } from '@/api/services/user'
import ForgetPasswordDialog from '@/components/ForgetPasswordDialog.vue'

const router = useRouter()
const route = useRoute()
const redirect = (route.query.redirect as string) || '/'

const appStore = useAppStore()
const { t } = useI18n()
const loading = ref(false)
const showForgetPasswordDialog = ref(false)
const loginForm = reactive({
  username: '',
  password: '',
  remember: false
})

const loginRules = {
  username: [{ required: true, message: t('login.username_required'), trigger: 'blur' }],
  password: [
    { required: true, message: t('login.password_required'), trigger: 'blur' },
    { min: 6, message: t('login.password_min_length'), trigger: 'blur' }
  ]
}

const loginFormRef = ref()

const handleLogin = async () => {
  try {
    loading.value = true
    // 表单验证
    await loginFormRef.value.validate()

    // 真实登录请求
    try {
      // 移除模拟延时，使用真实API调用
      console.log('开始执行login请求...')
      const loginRes = await login({
        username: loginForm.username,
        password: loginForm.password
      })

      // 详细输出login响应，帮助调试
      console.log('login请求返回完整数据:', loginRes)
      console.log('login响应类型:', typeof loginRes)
      console.log('login响应结构:', Object.keys(loginRes || {}))

      // 容错处理，确保即使响应格式不是预期的对象也能继续
      if (!loginRes || typeof loginRes !== 'object') {
        console.error('login响应格式错误，不是有效的对象:', loginRes)
        ElMessage.error(t('login.login_failed_retry'))
        return
      }

      // 检查登录是否成功（考虑不同的成功状态码）
      const isLoginSuccess = loginRes.code === 1

      if (isLoginSuccess) {
        // 保存token到本地存储（尝试从多个可能的字段获取token）
        const token =
          loginRes.access_token ||
          loginRes.token ||
          loginRes.data?.access_token ||
          loginRes.data?.token

        if (token) {
          // 立即保存token到本地存储，不使用延迟
          if (loginForm.remember) {
            localStorage.setItem('access_token', token)
          } else {
            sessionStorage.setItem('access_token', token)
          }

          // 同时更新appStore中的token状态，确保路由守卫能立即识别登录状态
          appStore.token = token

          // 直接使用then/catch链式调用，避免await可能导致的阻塞
          getUserMe()
            .then(async (userRes) => {
              console.log('getUserMe请求返回完整数据:', userRes)
              console.log('getUserMe响应code:', userRes?.code)
              console.log('getUserMe响应data:', userRes?.data)

              if (userRes && userRes.code === 1 && userRes.data) {
                const userRole = userRes.data.role
                console.log('提取到的用户角色:', userRole)
                console.log('用户角色类型:', typeof userRole)

                appStore.setUserRole(userRole)
                appStore.setUserInfo(userRes.data)

                console.log('appStore.userRole已设置为:', appStore.userRole)
                console.log('localStorage中的userRole:', localStorage.getItem('userRole'))

                // 加载公共配置并初始化消息推送
                await appStore.loadPublicConfig()
                appStore.initMessagePush()

                ElMessage.success(t('login.success'))

                // 根据用户角色跳转到不同页面
                if (userRole === 'Admin') {
                  console.log('跳转到管理后台')
                  router.push('/admin/dashboard')
                } else {
                  console.log('跳转到首页:', redirect)
                  router.push(redirect)
                }
              } else {
                console.error('getUserMe响应格式不正确:', userRes)
                console.error('响应code:', userRes?.code, '期望: 1')
                console.error('响应data:', userRes?.data)
                ElMessage.error((userRes?.msg || t('login.get_user_info_failed')) + '（响应格式问题）')
              }
            })
            .catch((error) => {
              console.error('获取用户信息请求异常:', error)
              console.error('错误详情:', error.response?.data)
              ElMessage.error(t('login.get_user_info_retry'))

              // 获取用户信息失败，停留在登录页
              loading.value = false
            })
            .finally(() => {
              loading.value = false
            })
            .finally(() => {
              console.log('getUserMe请求处理完成')
            })
        } else {
          console.error('登录成功但未获取到token，响应数据:', loginRes)
          ElMessage.error(t('login.success_but_no_token'))
        }
      } else {
        const errorMsg = loginRes.msg || loginRes.message || t('login.failed')
        console.error('登录失败:', errorMsg)
        ElMessage.error(errorMsg)
      }
    } catch (error) {
      console.error('登录请求失败:', error)
      ElMessage.error(t('login.login_failed_retry'))
    } finally {
      loading.value = false
    }
  } catch (error) {
    loading.value = false
    console.error('登录表单验证失败:', error)
  }
}

// 使用appStore中的主题设置
onMounted(() => {
  // 初始化主题
  appStore.initTheme()
})
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--el-bg-color);
}

.login-card {
  width: 400px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 24px;
}

.login-header h2 {
  margin-bottom: 8px;
  color: #1d2129;
}

.login-header p {
  color: #86909c;
  font-size: 14px;
}

.login-form {
  margin-top: 20px;
}

.remember-me {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.forgot-password {
  font-size: 14px;
}

.login-btn {
  width: 100%;
  height: 40px;
  font-size: 16px;
}
</style>
