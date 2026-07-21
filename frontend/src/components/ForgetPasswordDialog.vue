<template>
  <el-dialog
    v-model="visible"
    :title="$t('login.reset_password_title')"
    width="400px"
    @close="handleClose"
  >
    <p class="dialog-subtitle">{{ $t('login.reset_password_subtitle') }}</p>

    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="80px"
      @submit.prevent="handleSubmit"
    >
      <el-form-item :label="$t('login.reset_password_username')" prop="username">
        <el-input
          v-model="formData.username"
          :placeholder="$t('login.reset_password_username_placeholder')"
          clearable
          @keyup.enter="handleSubmit"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">{{ $t('login.reset_password_cancel') }}</el-button>
        <el-button type="primary" :loading="loading" @click="handleSubmit">
          {{ $t('login.reset_password_button') }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { resetPassword, type ResetPasswordRequest } from '@/api/services/user'

interface Props {
  modelValue: boolean
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const { t, locale } = useI18n()
const visible = ref(props.modelValue)
const loading = ref(false)
const formRef = ref()

const formData = reactive({
  username: ''
})

const formRules = {
  username: [{ required: true, message: t('login.reset_password_username_required'), trigger: 'blur' }]
}

watch(
  () => props.modelValue,
  (newVal) => {
    visible.value = newVal
    if (!newVal) {
      // 对话框关闭时重置表单
      formData.username = ''
      formRef.value?.clearValidate()
    }
  }
)

watch(visible, (newVal) => {
  emit('update:modelValue', newVal)
})

const handleClose = () => {
  visible.value = false
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    loading.value = true

    const request: ResetPasswordRequest = {
      username: formData.username,
      language: locale.value
    }

    const response = await resetPassword(request)

    if (response && response.code === 1) {
      ElMessage.success(t('login.reset_password_success'))
      handleClose()
    } else {
      // 根据错误消息显示相应的提示
      const msg = response?.msg || t('login.reset_password_failed')

      // 检查是否是特定的错误情况
      if (msg.includes('未关联邮箱') || msg.includes('no associated email')) {
        ElMessage.warning(t('login.reset_password_no_email'))
      } else if (msg.includes('邮件服务未配置') || msg.includes('email service is not configured')) {
        ElMessage.warning(t('login.reset_password_email_not_configured'))
      } else if (msg.includes('邮件发送失败') || msg.includes('email sending failed')) {
        ElMessage.warning(t('login.reset_password_email_failed'))
      } else if (msg.includes('用户不存在') || msg.includes('User not found')) {
        ElMessage.error(t('login.reset_password_user_not_found'))
      } else {
        ElMessage.error(msg)
      }
    }
  } catch (error: any) {
    console.error('重置密码错误:', error)
    const errorMessage = error?.response?.data?.msg || t('login.reset_password_failed')
    ElMessage.error(errorMessage)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.dialog-subtitle {
  color: var(--el-text-color-secondary);
  font-size: 14px;
  margin: 0 0 20px 0;
  line-height: 1.5;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
