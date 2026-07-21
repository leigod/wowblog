<template>
  <div class="invite-accept-container">
    <!-- 验证中 -->
    <div v-if="status === 'verifying'" class="invite-card">
      <el-icon class="loading-icon" :size="48"><Loading /></el-icon>
      <h2>{{ t('invite.verifying') }}</h2>
    </div>

    <!-- 邀请有效 -->
    <div v-else-if="status === 'valid' && invitation" class="invite-card">
      <div class="success-icon-wrapper">
        <el-icon class="success-icon" :size="64"><CircleCheck /></el-icon>
      </div>
      <h1>{{ t('invite.valid.title') }}</h1>
      <p class="invite-description">
        {{ t('invite.valid.description', {
          adminName: invitation.admin_name || 'Admin',
          blogName: invitation.blog_name || 'Blog',
          role: getRoleName(invitation.role)
        }) }}
      </p>

      <div class="permissions-section">
        <h3>{{ t('invite.valid.permissions', { role: getRoleName(invitation.role) }) }}</h3>
        <ul class="permissions-list">
          <li v-for="permission in getRolePermissions(invitation.role)" :key="permission">
            <el-icon><Check /></el-icon>
            {{ permission }}
          </li>
        </ul>
      </div>

      <div class="action-buttons">
        <template v-if="isLoggedIn">
          <el-button
            v-if="canAccept"
            type="primary"
            size="large"
            @click="handleAccept"
            :loading="accepting"
          >
            {{ t('invite.valid.button') }}
          </el-button>
          <el-alert
            v-else
            type="error"
            :title="t('invite.error.email_mismatch')"
            :closable="false"
            show-icon
          />
        </template>
        <template v-else>
          <el-button type="primary" size="large" @click="goToLogin">
            {{ t('invite.valid.login_button') }}
          </el-button>
          <el-button size="large" @click="goToRegister">
            {{ t('invite.valid.register_button') }}
          </el-button>
        </template>
      </div>
    </div>

    <!-- 邀请无效/过期/已接受 -->
    <div v-else-if="status === 'invalid'" class="invite-card">
      <div class="error-icon-wrapper">
        <el-icon class="error-icon" :size="64"><CircleClose /></el-icon>
      </div>
      <h1>{{ t('invite.invalid.title') }}</h1>
      <p class="error-message">{{ invalidMessage }}</p>
      <el-button type="primary" @click="goToHome">
        {{ t('invite.invalid.back_to_home') }}
      </el-button>
    </div>

    <!-- 接受成功 -->
    <div v-else-if="status === 'success'" class="invite-card">
      <div class="success-icon-wrapper">
        <el-icon class="success-icon" :size="64"><CircleCheck /></el-icon>
      </div>
      <h1>{{ t('invite.success.title') }}</h1>
      <p class="success-message">
        {{ t('invite.success.message', { blogName: invitation?.blog_name || 'Blog' }) }}
      </p>
      <el-button type="primary" @click="goToDashboard">
        {{ t('invite.success.continue') }}
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Loading, CircleCheck, CircleClose, Check } from '@element-plus/icons-vue'
import { verifyInvitation, acceptInvitation } from '@/api/services/memberInvitations'
import { useAppStore } from '@/stores/app'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const appStore = useAppStore()

type InviteStatus = 'verifying' | 'valid' | 'invalid' | 'success'

const status = ref<InviteStatus>('verifying')
const invitation = ref<any>(null)
const accepting = ref(false)
const invalidMessage = ref('')

// 当前登录用户
const isLoggedIn = computed(() => !!appStore.token)

// 是否可以接受邀请（邮箱匹配）
const canAccept = computed(() => {
  if (!invitation.value || !appStore.userInfo) return false
  return appStore.userInfo.email === invitation.value.email
})

// 获取角色名称
const getRoleName = (role: string) => {
  const roleNames: Record<string, string> = {
    Admin: t('admin.members.roles.admin.name'),
    Editor: t('admin.members.roles.editor.name'),
    Contributor: t('admin.members.roles.contributor.name')
  }
  return roleNames[role] || role
}

// 获取角色权限
const getRolePermissions = (role: string): string[] => {
  const permissions: Record<string, string[]> = {
    Admin: [
      t('admin.members.roles.admin.permissions1'),
      t('admin.members.roles.admin.permissions2'),
      t('admin.members.roles.admin.permissions3'),
      t('admin.members.roles.admin.permissions4')
    ],
    Editor: [
      t('admin.members.roles.editor.permissions1'),
      t('admin.members.roles.editor.permissions2'),
      t('admin.members.roles.editor.permissions3'),
      t('admin.members.roles.editor.permissions4')
    ],
    Contributor: [
      t('admin.members.roles.contributor.permissions1'),
      t('admin.members.roles.contributor.permissions2'),
      t('admin.members.roles.contributor.permissions3')
    ]
  }
  return permissions[role] || []
}

// 验证邀请
const verifyInvite = async () => {
  const token = route.params.token as string
  if (!token) {
    status.value = 'invalid'
    invalidMessage.value = t('invite.invalid.not_found')
    return
  }

  try {
    const res = await verifyInvitation(token)
    if (res.valid) {
      invitation.value = res
      status.value = 'valid'
    } else {
      status.value = 'invalid'
      // 根据错误消息设置对应的状态消息
      if (res.message?.includes('expired')) {
        invalidMessage.value = t('invite.invalid.expired')
      } else if (res.message?.includes('cancelled')) {
        invalidMessage.value = t('invite.invalid.cancelled')
      } else if (res.message?.includes('accepted')) {
        invalidMessage.value = t('invite.invalid.accepted')
      } else {
        invalidMessage.value = res.message || t('invite.invalid.not_found')
      }
    }
  } catch (error: any) {
    status.value = 'invalid'
    invalidMessage.value = error?.response?.data?.msg || t('invite.invalid.not_found')
  }
}

// 接受邀请
const handleAccept = async () => {
  if (!canAccept.value) {
    ElMessage.error(t('invite.error.email_mismatch'))
    return
  }

  const token = route.params.token as string
  accepting.value = true

  try {
    await acceptInvitation(token)
    status.value = 'success'
    ElMessage.success(t('invite.success.message', { blogName: invitation.value?.blog_name }))
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.msg || t('invite.error.failed'))
  } finally {
    accepting.value = false
  }
}

// 跳转到登录
const goToLogin = () => {
  router.push({
    name: 'login',
    query: { redirect: route.fullPath }
  })
}

// 跳转到注册
const goToRegister = () => {
  router.push({
    name: 'register',
    query: { redirect: route.fullPath }
  })
}

// 跳转到首页
const goToHome = () => {
  router.push({ name: 'home' })
}

// 跳转到管理后台
const goToDashboard = () => {
  router.push({ name: 'admin-dashboard' })
}

onMounted(() => {
  verifyInvite()
})
</script>

<style scoped>
.invite-accept-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.invite-card {
  background: white;
  border-radius: 16px;
  padding: 48px;
  max-width: 560px;
  width: 100%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  text-align: center;
}

.loading-icon {
  color: var(--el-color-primary);
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.invite-card h2 {
  margin-top: 20px;
  color: var(--el-text-color-primary);
}

.success-icon-wrapper,
.error-icon-wrapper {
  margin-bottom: 24px;
}

.success-icon {
  color: var(--el-color-success);
}

.error-icon {
  color: var(--el-color-danger);
}

.invite-card h1 {
  font-size: 28px;
  margin: 0 0 16px 0;
  color: var(--el-text-color-primary);
}

.invite-description {
  font-size: 16px;
  color: var(--el-text-color-regular);
  line-height: 1.6;
  margin-bottom: 32px;
}

.permissions-section {
  background: var(--el-fill-color-light);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 32px;
  text-align: left;
}

.permissions-section h3 {
  font-size: 16px;
  margin: 0 0 16px 0;
  color: var(--el-text-color-primary);
}

.permissions-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.permissions-list li {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  color: var(--el-text-color-regular);
}

.permissions-list li .el-icon {
  color: var(--el-color-success);
  flex-shrink: 0;
}

.action-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.error-message,
.success-message {
  font-size: 16px;
  color: var(--el-text-color-regular);
  margin-bottom: 24px;
}
</style>
