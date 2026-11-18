<template>
  <div class="creator-page">
    <div class="page-header">
      <div>
        <h1>{{ t('creator.settings.title') }}</h1>
        <p>{{ t('creator.settings.title_info') }}</p>
      </div>
    </div>

    <el-card class="settings-card" v-loading="loading">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="140px"
        label-position="top"
        class="settings-form"
      >
        <el-form-item :label="t('creator.settings.blog_name')" prop="blog_name">
          <el-input
            v-model="form.blog_name"
            :placeholder="t('creator.settings.blog_name_placeholder')"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>

        <el-form-item :label="t('creator.settings.blog_description')" prop="blog_description">
          <el-input
            v-model="form.blog_description"
            type="textarea"
            :rows="3"
            :placeholder="t('creator.settings.blog_description_placeholder')"
            maxlength="300"
            show-word-limit
          />
        </el-form-item>

        <el-form-item :label="t('creator.settings.impressum')" prop="impressum">
          <el-input
            v-model="form.impressum"
            type="textarea"
            :rows="6"
            :placeholder="t('creator.settings.impressum_placeholder')"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="saving" @click="handleSave">
            {{ t('creator.settings.save') }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getBlogConfig, updateBlogConfig } from '@/api/services/creator'

const { t } = useI18n()

const loading = ref(false)
const saving = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  blog_name: '',
  blog_description: '',
  impressum: ''
})

const rules: FormRules = {
  blog_name: [{ max: 100, message: t('creator.settings.blog_name_length'), trigger: 'blur' }],
  blog_description: [
    { max: 300, message: t('creator.settings.blog_description_length'), trigger: 'blur' }
  ]
}

const loadConfig = async () => {
  loading.value = true
  try {
    const res = await getBlogConfig()
    if (res.code === 1 && res.data) {
      form.blog_name = res.data.blog_name || ''
      form.blog_description = res.data.blog_description || ''
      form.impressum = res.data.impressum || ''
    }
  } catch (error) {
    console.error(t('creator.settings.load_error'), error)
    ElMessage.error(t('creator.settings.load_error'))
  } finally {
    loading.value = false
  }
}

const handleSave = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  saving.value = true
  try {
    const res = await updateBlogConfig({
      blog_name: form.blog_name || null,
      blog_description: form.blog_description || null,
      impressum: form.impressum || null
    })
    if (res.code === 1) {
      ElMessage.success(t('creator.settings.save_success'))
    } else {
      ElMessage.error(res.msg || t('creator.settings.save_error'))
    }
  } catch (error) {
    console.error(t('creator.settings.save_error'), error)
    ElMessage.error(t('creator.settings.save_error'))
  } finally {
    saving.value = false
  }
}

onMounted(loadConfig)
</script>

<style scoped>
.creator-page {
  padding: 20px;
  max-width: 900px;
}

.page-header {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.page-header h1 {
  margin: 0 0 5px;
  font-size: 24px;
  font-weight: 600;
}

.page-header p {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.settings-card {
  border-radius: 8px;
}

.settings-form {
  max-width: 640px;
}
</style>
