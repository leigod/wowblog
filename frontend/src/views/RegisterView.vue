<template>
  <div class="register-container">
    <el-card class="register-card">
      <div class="register-header">
        <h2>{{ $t('register.title') }}</h2>
        <p>{{ $t('register.subtitle') }}</p>
      </div>
      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        class="register-form"
      >
        <el-form-item prop="username">
          <el-input
            v-model="registerForm.username"
            :placeholder="$t('register.username_placeholder')"
            prefix-icon="User"
            size="large"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            :placeholder="$t('register.password_placeholder')"
            prefix-icon="Lock"
            show-password
            size="large"
          />
        </el-form-item>

        <el-form-item prop="full_name">
          <el-input
            v-model="registerForm.full_name"
            :placeholder="$t('register.full_name_placeholder')"
            prefix-icon="Avatar"
            size="large"
          />
        </el-form-item>

        <el-form-item prop="email">
          <el-input
            v-model="registerForm.email"
            type="email"
            :placeholder="$t('register.email_placeholder')"
            prefix-icon="Message"
            size="large"
          />
        </el-form-item>

        <el-form-item prop="mobile">
          <el-input
            v-model="registerForm.mobile"
            :placeholder="$t('register.mobile_placeholder')"
            prefix-icon="Phone"
            size="large"
          />
        </el-form-item>

        <el-form-item :label="$t('register.gender_label')">
          <el-radio-group v-model="registerForm.gender">
            <el-radio value="0">{{ $t('register.gender_female') }}</el-radio>
            <el-radio value="1">{{ $t('register.gender_male') }}</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- <el-form-item label="头像">
          <el-upload
            class="avatar-uploader"
            action="/api/upload/"
            :show-file-list="false"
            :on-success="handleAvatarSuccess"
            :before-upload="beforeAvatarUpload"
          >
            <div class="el-upload">
              <img
                v-if="registerForm.profile_image"
                :src="registerForm.profile_image"
                class="avatar"
              />
              <el-icon v-else class="el-icon-plus avatar-uploader-icon"><UploadFilled /></el-icon>
            </div>
          </el-upload>
          <div class="avatar-hint">支持 JPG、PNG 格式，文件大小不超过 2MB</div>
        </el-form-item> -->

        <el-form-item>
          <el-button type="primary" class="register-btn" @click="handleRegister" :loading="loading">
            {{ $t('register.register_button') }}
          </el-button>
        </el-form-item>

        <div class="register-footer">
          <span>{{ $t('register.has_account') }}</span>
          <el-link type="primary" underline="never" @click="navigateToLogin">{{ $t('register.login_now') }}</el-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAppStore } from '@/stores/app'
import { ElMessage } from 'element-plus'
import { register, getTempToken } from '@/api/services/user'

const router = useRouter()
const appStore = useAppStore()
const { t } = useI18n()
const loading = ref(false)
const registerFormRef = ref()

// 注册表单数据
const registerForm = reactive({
  username: '',
  password: '',
  full_name: '',
  email: '',
  mobile: '',
  profile_image: '',
  gender: 0 // 默认为女性
})

// 表单验证规则
const registerRules = {
  username: [
    { required: true, message: t('register.username_required'), trigger: 'blur' },
    { min: 3, max: 20, message: t('register.username_length'), trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: t('register.username_pattern'), trigger: 'blur' }
  ],
  password: [
    { required: true, message: t('register.password_required'), trigger: 'blur' },
    { min: 6, max: 20, message: t('register.password_length'), trigger: 'blur' }
  ],
  full_name: [
    { required: true, message: t('register.full_name_required'), trigger: 'blur' },
    { min: 3, max: 20, message: t('register.full_name_length'), trigger: 'blur' },
    {
      validator: (rule: any, value: string, callback: Function) => {
        // 过滤SQL注入的特殊字符
        const sqlInjectionPattern = /[';"()*&|<>[\]{}]/
        if (sqlInjectionPattern.test(value)) {
          callback(new Error(t('register.full_name_invalid')))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  email: [{ type: 'email', message: t('register.email_invalid'), trigger: 'blur', required: false }],
  mobile: [
    { pattern: /^1[3-9]\d{9}$/, message: t('register.mobile_invalid'), trigger: 'blur', required: false }
  ]
}

// 处理注册表单提交
const handleRegister = async () => {
  try {
    loading.value = true
    // 表单验证
    await registerFormRef.value.validate()

    // 构造注册数据
    const registerData = {
      ...registerForm,
      gender: Number(registerForm.gender) // 确保gender是数字类型
    }

    // 调用注册API
    const res = await register(registerData)

    if (res && res.code === 1) {
      ElMessage.success(t('register.success'))
      appStore.clearUserInfo()
      // 注册成功后跳转到登录页面
      setTimeout(() => {
        router.push('/login')
      }, 1000)
    } else {
      const errorMsg = res?.data[0].msg || t('register.failed')
      ElMessage.error(errorMsg)
    }
  } catch (error) {
    console.error('注册失败:', error)
    // const errorMessage = (error as Error).message || '注册失败，请稍后重试'
    const errorMessage = (error as any).response?.data.data[0].msg || t('register.failed')
    ElMessage.error(errorMessage)
  } finally {
    loading.value = false
  }
}

// 获取临时token
const getUserTempToken = async () => {
  try {
    const res = await getTempToken()
    if (res && res.code === 1) {
      const token = res.data.access_token
      localStorage.setItem('access_token', token)
      appStore.token = token
    } else {
      const errorMsg = res?.data[0].msg || t('register.get_temp_token_failed')
      ElMessage.error(errorMsg)
      return null
    }
  } catch (error) {
    console.error('获取临时token失败:', error)
    const errorMessage =
      (error as any).response?.data.data[0].msg || t('register.get_temp_token_failed')
    ElMessage.error(errorMessage)
    return null
  }
}

// 处理头像上传成功
const handleAvatarSuccess = (response: any, file: any) => {
  if (response && response.code === 1) {
    registerForm.profile_image = response.data.url
  } else {
    ElMessage.error(t('register.avatar_upload_failed'))
  }
}

// 头像上传前的校验
const beforeAvatarUpload = (file: File) => {
  const isJPG = file.type === 'image/jpeg' || file.type === 'image/png'
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isJPG) {
    ElMessage.error(t('register.avatar_format_error'))
    return false
  }
  if (!isLt2M) {
    ElMessage.error(t('register.avatar_size_error'))
    return false
  }
  return true
}

onMounted(() => {
  getUserTempToken()
})

// 跳转到登录页面
const navigateToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--el-bg-color);
  padding: 20px;
}

.register-card {
  width: 500px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.register-header {
  text-align: center;
  margin-bottom: 24px;
}

.register-header h2 {
  margin-bottom: 8px;
  color: #1d2129;
}

.register-header p {
  color: #86909c;
  font-size: 14px;
}

.register-form {
  margin-top: 20px;
}

.register-btn {
  width: 100%;
  height: 40px;
  font-size: 16px;
}

.register-footer {
  text-align: center;
  margin-top: 16px;
  font-size: 14px;
  color: #86909c;
}

.avatar-uploader {
  display: flex;
  align-items: center;
  width: 100%;
}

.avatar-uploader .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  width: 100px;
  height: 100px;
}

.avatar-uploader .el-upload:hover {
  border-color: #409eff;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 100px;
  height: 100px;
  line-height: 100px;
  text-align: center;
}
.avatar-uploader-icon:hover {
  color: #409eff;
}

.avatar {
  width: 100px;
  height: 100px;
  display: block;
}

.avatar-hint {
  display: inline-block;
  margin-top: 10px;
  font-size: 12px;
  color: #86909c;
}
</style>
