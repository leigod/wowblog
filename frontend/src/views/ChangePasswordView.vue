<template>
  <div class="change-password-container">
    <el-card class="change-password-card">
      <div class="page-header">
        <h1 class="page-title">{{ $t('change_password.title') }}</h1>
        <p class="page-subtitle">{{ $t('change_password.subtitle') }}</p>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        size="large"
        @submit.prevent
      >
        <el-form-item :label="$t('change_password.old_password')" prop="oldPassword">
          <el-input
            v-model="form.oldPassword"
            type="password"
            show-password
            prefix-icon="Lock"
            :placeholder="$t('change_password.old_password_placeholder')"
          />
        </el-form-item>

        <el-form-item :label="$t('change_password.new_password')" prop="newPassword">
          <el-input
            v-model="form.newPassword"
            type="password"
            show-password
            prefix-icon="Lock"
            :placeholder="$t('change_password.new_password_placeholder')"
          />
        </el-form-item>

        <el-form-item :label="$t('change_password.confirm_password')" prop="confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            type="password"
            show-password
            prefix-icon="Lock"
            :placeholder="$t('change_password.confirm_password_placeholder')"
            @keyup.enter="handleSubmit"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleSubmit">
            {{ $t('change_password.submit') }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'
import { changePassword } from '@/api/services/user'

const { t } = useI18n()
const router = useRouter()
const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const rules = reactive({
  oldPassword: [
    { required: true, message: t('change_password.old_password_required'), trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: t('change_password.new_password_required'), trigger: 'blur' },
    { min: 6, max: 20, message: t('change_password.password_length'), trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: t('change_password.confirm_password_required'), trigger: 'blur' },
    {
      validator: (_rule: any, value: string, callback: Function) => {
        if (value !== form.newPassword) {
          callback(new Error(t('change_password.password_mismatch')))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
})

const handleSubmit = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  loading.value = true
  try {
    const res = await changePassword({
      old_password: form.oldPassword,
      new_password: form.newPassword
    })
    if (res && res.code === 1) {
      ElMessage.success(t('change_password.success'))
      form.oldPassword = ''
      form.newPassword = ''
      form.confirmPassword = ''
      router.back()
    } else {
      ElMessage.error(res?.msg || t('change_password.failed'))
    }
  } catch (error) {
    console.error('修改密码失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.change-password-container {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  box-sizing: border-box;
}

.change-password-card {
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  margin: 0 0 8px;
  font-size: 22px;
}

.page-subtitle {
  margin: 0;
  font-size: 14px;
  color: #86909c;
}
</style>
