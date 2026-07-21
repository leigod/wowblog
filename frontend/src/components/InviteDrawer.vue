<template>
  <el-drawer
    v-model="visible"
    :title="$t('admin.members.drawer.invite_title')"
    direction="rtl"
    :size="isMobile ? '100%' : '450px'"
    @close="handleClose"
  >
    <div class="invite-drawer">
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        :label-position="isMobile ? 'top' : 'right'"
        :label-width="isMobile ? 'auto' : '100px'"
        @submit.prevent="handleSubmit"
      >
        <el-form-item :label="$t('admin.members.form.email')" prop="email">
          <el-input
            v-model="formData.email"
            :placeholder="$t('admin.members.invite.email_placeholder')"
            type="email"
          />
        </el-form-item>

        <el-form-item :label="$t('admin.members.form.role')" prop="role">
          <el-select
            v-model="formData.role"
            :placeholder="$t('admin.members.invite.role_placeholder')"
            style="width: 100%"
          >
            <el-option
              v-for="role in roleOptions"
              :key="role.value"
              :label="role.label"
              :value="role.value"
            >
              <div class="role-option">
                <span>{{ role.label }}</span>
                <span class="role-desc">{{ role.description }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item :label="$t('admin.members.form.language')" prop="language">
          <el-select
            v-model="formData.language"
            :placeholder="$t('admin.members.invite.language_placeholder')"
            style="width: 100%"
          >
            <el-option label="中文" value="zh-CN" />
            <el-option label="English" value="en-US" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <div class="invite-info">
            <el-icon class="info-icon"><InfoFilled /></el-icon>
            <span>{{ $t('admin.members.invite.description') }}</span>
          </div>
        </el-form-item>
      </el-form>
    </div>

    <template #footer>
      <div class="drawer-footer">
        <el-button @click="handleClose">{{ $t('admin.members.invite.cancel') }}</el-button>
        <el-button
          type="primary"
          @click="handleSubmit"
          :loading="submitting"
        >
          {{ $t('admin.members.invite.submit') }}
        </el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { InfoFilled } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import type { FormInstance, FormRules } from 'element-plus'
import { createInvitation } from '@/api/services/memberInvitations'
import { useMobileDetection } from '@/composables/useMobileDetection'

const { t } = useI18n()
const { isMobile } = useMobileDetection()

interface Props {
  modelValue: boolean
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'success'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const formRef = ref<FormInstance>()
const submitting = ref(false)

// 角色选项
const roleOptions = [
  {
    value: 'Admin',
    label: t('admin.members.roles.admin.name'),
    description: t('admin.members.roles.admin.description')
  },
  {
    value: 'Editor',
    label: t('admin.members.roles.editor.name'),
    description: t('admin.members.roles.editor.description')
  },
  {
    value: 'Author',
    label: t('admin.members.roles.author.name'),
    description: t('admin.members.roles.author.description')
  },
  {
    value: 'Contributor',
    label: t('admin.members.roles.contributor.name'),
    description: t('admin.members.roles.contributor.description')
  }
]

// 表单数据
const formData = reactive({
  email: '',
  role: 'Contributor',
  language: 'zh-CN'
})

// 表单验证规则
const rules: FormRules = {
  email: [
    { required: true, message: t('admin.members.validations.email_required'), trigger: 'blur' },
    { type: 'email', message: t('admin.members.validations.invalid_email'), trigger: 'blur' }
  ],
  role: [
    { required: true, message: t('admin.members.validations.select_role'), trigger: 'change' }
  ],
  language: [
    { required: true, message: t('admin.members.validations.language_required'), trigger: 'change' }
  ]
}

// 关闭抽屉
const handleClose = () => {
  visible.value = false
  formRef.value?.resetFields()
  formData.email = ''
  formData.role = 'Contributor'
  formData.language = 'zh-CN'
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    const valid = await formRef.value.validate()
    if (!valid) return

    submitting.value = true

    await createInvitation({
      email: formData.email,
      role: formData.role as any,
      language: formData.language as any
    })

    ElMessage.success(t('admin.members.message.invite_success'))
    emit('success')
    handleClose()
  } catch (error: any) {
    console.error('Failed to create invitation:', error)
    const message = error?.response?.data?.msg || t('admin.members.message.invite_error')
    ElMessage.error(message)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.invite-drawer {
  padding: 20px;
}

.role-option {
  display: flex;
  flex-direction: column;
}

.role-desc {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}

.invite-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: var(--el-color-info-light-9);
  border-radius: 4px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.info-icon {
  color: var(--el-color-info);
  flex-shrink: 0;
}

.drawer-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 0 20px 20px;
}

/* 移动端样式 */
@media (max-width: 767px) {
  .invite-drawer {
    padding: 16px;
  }

  .drawer-footer {
    padding: 0 16px 16px;
    flex-direction: column;
  }

  .drawer-footer .el-button {
    width: 100%;
  }

  .invite-info {
    font-size: 12px;
    padding: 10px;
  }
}
</style>
