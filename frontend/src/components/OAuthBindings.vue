<template>
  <el-card class="oauth-bindings-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span class="card-title">{{ t('profile_edit.oauth_bindings') }}</span>
        <span class="card-hint">{{ t('profile_edit.oauth_bindings_hint') }}</span>
      </div>
    </template>

    <el-skeleton v-if="loading" :rows="2" animated />

    <div v-else-if="bindings.length === 0" class="empty-state">
      <Icon icon="mdi:link-variant-off" class="empty-icon" />
      <span>{{ t('profile_edit.oauth_no_bindings') }}</span>
    </div>

    <div v-else class="binding-list">
      <div v-for="b in bindings" :key="b.provider" class="binding-item">
        <div class="binding-info">
          <Icon :icon="meta(b.provider).icon" class="binding-icon" />
          <div class="binding-text">
            <div class="binding-name">{{ meta(b.provider).name }}</div>
            <div class="binding-email">{{ b.email || t('profile_edit.oauth_no_email') }}</div>
          </div>
        </div>
        <el-popconfirm
          :title="t('profile_edit.oauth_unlink_confirm')"
          :confirm-button-text="t('profile_edit.oauth_unlink')"
          :cancel-button-text="$t('common.cancel')"
          width="260"
          @confirm="handleUnlink(b.provider)"
        >
          <template #reference>
            <el-button type="danger" text :loading="unlinking === b.provider">
              {{ t('profile_edit.oauth_unlink') }}
            </el-button>
          </template>
        </el-popconfirm>
      </div>
    </div>

    <!-- 绑定新账号（后台已启用但尚未绑定的 provider） -->
    <div v-if="!loading && availableProviders.length" class="bind-section">
      <div class="bind-title">{{ t('profile_edit.oauth_bind_new') }}</div>
      <div class="bind-buttons">
        <el-button v-for="p in availableProviders" :key="p" :loading="binding === p"
          size="small" round @click="handleBind(p)">
          <Icon :icon="meta(p).icon" class="bind-icon" />
          <span>{{ meta(p).name }}</span>
        </el-button>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Icon } from '@iconify/vue'
import { getOAuthBindings, unlinkOAuth, initiateOAuthBind, type OAuthBinding } from '@/api/services/oauth'
import { useAppStore } from '@/stores/app'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const appStore = useAppStore()

const loading = ref(false)
const unlinking = ref<string | null>(null)
const binding = ref<string | null>(null)
const bindings = ref<OAuthBinding[]>([])

/** 支持的 provider 元数据（图标 + 展示名） */
const PROVIDER_META: Record<string, { icon: string; name: string }> = {
  google: { icon: 'basil:google-solid', name: 'Google' },
  github: { icon: 'mdi:github', name: 'GitHub' },
  gitee: { icon: 'simple-icons:gitee', name: 'Gitee' },
  apple: { icon: 'ic:baseline-apple', name: 'Apple' },
  wechat: { icon: 'ri:wechat-fill', name: 'WeChat' },
  qq: { icon: 'ri:qq-fill', name: 'QQ' }
}
const meta = (provider: string) => PROVIDER_META[provider] ?? { icon: 'mdi:account-circle', name: provider }

/** 已启用但尚未绑定的 provider（用于"绑定新账号"按钮） */
const availableProviders = computed(() => {
  const bound = new Set(bindings.value.map(b => b.provider))
  return (appStore.enabled_oauth_providers || []).filter(p => !bound.has(p))
})

const load = async () => {
  loading.value = true
  try {
    const res = await getOAuthBindings()
    if (res && res.code === 1) {
      bindings.value = res.data ?? []
    }
  } catch {
    // 静默失败：绑定面板不应阻塞资料编辑页
  } finally {
    loading.value = false
  }
}

const handleUnlink = async (provider: string) => {
  unlinking.value = provider
  try {
    const res = await unlinkOAuth(provider)
    if (res && res.code === 1) {
      ElMessage.success(t('profile_edit.oauth_unlinked'))
      await load()
    } else {
      ElMessage.error(res?.msg || t('profile_edit.oauth_unlink_failed'))
    }
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.msg || t('profile_edit.oauth_unlink_failed'))
  } finally {
    unlinking.value = null
  }
}

/** 主动绑定：先调后端设 session 意图（axios 带 token），再 window.location 跳授权 URL */
const handleBind = async (provider: string) => {
  binding.value = provider
  try {
    const res = await initiateOAuthBind(provider)
    if (res && res.code === 1 && res.data?.authorize_url) {
      window.location.href = res.data.authorize_url
    } else {
      ElMessage.error(res?.msg || t('profile_edit.oauth_bind_failed'))
    }
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.msg || t('profile_edit.oauth_bind_failed'))
  } finally {
    binding.value = null
  }
}

onMounted(async () => {
  // 处理主动绑定回调（/profile/edit?oauth_bind=success|error）
  const result = route.query.oauth_bind as string | undefined
  if (result) {
    if (result === 'success') {
      ElMessage.success(t('profile_edit.oauth_bind_success'))
    } else {
      ElMessage.error((route.query.desc as string) || t('profile_edit.oauth_bind_failed'))
    }
    router.replace({ query: {} }) // 清 query，避免刷新重复提示
  }
  await load()
})
</script>

<style scoped>
.oauth-bindings-card {
  margin-top: 20px;
  border-radius: 12px;
}

.card-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
  flex-wrap: wrap;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.card-hint {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 28px 0;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.empty-icon {
  font-size: 32px;
  opacity: 0.5;
}

.binding-list {
  display: flex;
  flex-direction: column;
}

.binding-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.binding-item:last-child {
  border-bottom: none;
}

.binding-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.binding-icon {
  font-size: 24px;
  color: var(--el-text-color-regular);
}

.binding-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.binding-email {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 2px;
}

.bind-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.bind-title {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  margin-bottom: 10px;
}

.bind-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.bind-icon {
  margin-right: 4px;
  font-size: 16px;
  vertical-align: middle;
}
</style>
