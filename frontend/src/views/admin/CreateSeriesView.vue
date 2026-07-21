<template>
  <div class="create-series-container">
    <div class="page-header">
      <h1>{{ $t('admin.series.page.create.title') }}</h1>
      <p>{{ $t('admin.series.page.create.description') }}</p>
    </div>

    <el-form
      ref="seriesFormRef"
      :model="seriesForm"
      :rules="formRules"
      label-position="top"
      size="large"
      class="series-form"
    >
      <!-- Series Name -->
      <el-form-item :label="$t('admin.series.page.form.name')" prop="name">
        <el-input
          v-model="seriesForm.name"
          :placeholder="$t('admin.series.page.form.name_placeholder')"
          class="form-input"
        />
      </el-form-item>

      <!-- Series Slug -->
      <el-form-item :label="$t('admin.series.page.form.slug')" prop="slug">
        <el-input
          v-model="seriesForm.slug"
          :placeholder="$t('admin.series.page.form.slug_placeholder')"
          class="form-input"
        />
        <p class="form-hint">
          {{ $t('admin.series.page.form.slug_helptip') }}
        </p>
      </el-form-item>

      <!-- Series Description -->
      <el-form-item :label="$t('admin.series.page.form.description')" prop="description">
        <el-input
          v-model="seriesForm.description"
          type="textarea"
          :rows="4"
          :placeholder="$t('admin.series.page.form.description_placeholder')"
          class="form-textarea"
        />
      </el-form-item>

      <!-- Series Cover -->
      <el-form-item :label="$t('admin.series.page.form.cover')" prop="coverImage">
        <template #label>
          <div class="label-content">
            <span>{{ $t('admin.series.page.form.cover') }}</span>
          </div>
        </template>
        <p class="form-hint">
          {{ $t('admin.series.page.form.cover_helptip') }}
        </p>
        <div class="upload-container">
          <el-upload
            class="upload-wrapper"
            drag
            :http-request="handleCustomUpload"
            :before-upload="beforeUpload"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :show-file-list="false"
            accept="image/*"
          >
            <template v-if="!isUploading && !seriesForm.coverImage">
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                <span v-html="$t('admin.series.page.form.upload')"></span>
                <span>{{ $t('admin.series.page.form.upload_helptip') }}</span>
              </div>
            </template>
            <template v-if="isUploading">
              <div style="text-align: center; padding: 20px 0">
                <el-progress
                  :percentage="uploadProgress"
                  :stroke-width="2"
                  style="width: 200px; margin: 0 auto 10px"
                ></el-progress>
                <span>{{ uploadProgress }}%</span>
              </div>
            </template>
            <template v-if="seriesForm.coverImage">
              <div class="cover-image-wrapper">
                <img :src="seriesForm.coverImage" alt="Series Cover" class="cover-image" />
                <el-button :icon="Delete" class="delete-cover-btn" @click="removeImage" />
              </div>
            </template>
          </el-upload>
        </div>
      </el-form-item>

      <!-- Sort Articles -->
      <el-form-item :label="$t('admin.series.page.form.order')" prop="sortOrder">
        <el-select v-model="seriesForm.sortOrder" class="form-select">
          <el-option :label="$t('admin.series.page.form.order_oldest')" value="oldest" />
          <el-option :label="$t('admin.series.page.form.order_newest')" value="newest" />
        </el-select>
        <p class="form-hint">
          {{ $t('admin.series.page.form.order_helptip') }}
        </p>
      </el-form-item>
    </el-form>

    <!-- Action Buttons -->
    <div class="action-buttons">
      <el-button type="text" class="back-button" @click="navigateBack">
        <el-icon><ArrowLeft /></el-icon> {{ $t('admin.general.btn.back') }}
      </el-button>
      <el-button type="primary" class="create-button" @click="handleSubmit">
        {{ $t('admin.series.page.create.btn') }}
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import {
  ElForm,
  ElFormItem,
  ElInput,
  ElSelect,
  ElOption,
  ElUpload,
  ElButton,
  ElIcon,
  ElMessage
} from 'element-plus'
import { Upload, ArrowLeft, Delete } from '@element-plus/icons-vue'
import { createSeries } from '@/api/services/series'
import { uploadFile } from '@/api/services/common'

// i18n
const { t } = useI18n()

// Form state
const seriesForm = reactive<{
  name: string
  slug: string
  description: string
  coverImage: string | null
  sortOrder: string
}>({
  name: '',
  slug: '',
  description: '',
  coverImage: null,
  sortOrder: 'newest'
})

// Form validation rules
const formRules = {
  name: [
    { required: true, message: t('admin.series.page.validate.name'), trigger: 'blur' },
    { max: 100, message: t('admin.series.page.validate.name_length'), trigger: 'blur' }
  ],
  slug: [
    { required: true, message: t('admin.series.page.validate.slug'), trigger: 'blur' },
    {
      pattern: /^[a-z0-9-]+$/,
      message: t('admin.series.page.validate.slug_format'),
      trigger: 'blur'
    },
    { max: 100, message: t('admin.series.page.validate.slug_length'), trigger: 'blur' }
  ],
  description: [{ max: 500, message: t('admin.series.page.validate.description'), trigger: 'blur' }]
}

// Refs
const seriesFormRef = ref<InstanceType<typeof ElForm>>()
const router = useRouter()

// Methods
const navigateBack = () => {
  router.push('/admin/series')
}

const handleSubmit = async () => {
  if (!seriesFormRef.value) return

  try {
    const valid = await seriesFormRef.value.validate()
    if (valid) {
      // In a real application, you would send the data to your API here
      const reqData = {
        name: seriesForm.name,
        slug: seriesForm.slug,
        series_desc: seriesForm.description,
        image: seriesForm.coverImage,
        articles_order: seriesForm.sortOrder === 'oldest' ? 'asc' : 'desc'
      }
      const res = await createSeries(reqData)
      if (res.code === 1) {
        // Clear the form after successful creation
        seriesForm.name = ''
        seriesForm.slug = ''
        seriesForm.description = ''
        seriesForm.coverImage = null
        seriesForm.sortOrder = 'oldest'
        console.log('Series data to submit:', seriesForm)
        // Show success message and redirect
        ElMessage.success(t('admin.series.page.create.success'))
        router.push('/admin/series')
      } else {
        ElMessage.error(res.msg)
      }
    }
  } catch (error) {
    // Validation failed
    console.error('Validation failed:', error)
  }
}

const handleCoverChange = (file: any) => {
  // Handle image preview
  seriesForm.coverImage = URL.createObjectURL(file.raw)
}

// 上传前验证
const beforeUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error(t('admin.series.page.form.uploaderror.format'))
    return false
  }

  const fileSize = file.size / 1024 / 1024 < 2
  if (!fileSize) {
    ElMessage.error(t('admin.series.page.form.uploaderror.size'))
    return false
  }

  return true
}

// 上传进度
const uploadProgress = ref(0)
const isUploading = ref(false)

// 上传OG图片文件
const handleCustomUpload = async (options: any) => {
  isUploading.value = true
  uploadProgress.value = 0

  try {
    const res = await uploadFile({
      file: options.file,
      onProgress: (progressEvent) => {
        if (progressEvent.total > 0) {
          const percent = Math.round((progressEvent.loaded / progressEvent.total) * 100)
          uploadProgress.value = percent
          options.onProgress({ percent })
        }
      }
    })

    if (res.code === 1) {
      options.onSuccess(res.data)
    } else {
      options.onError(new Error(res.msg || t('admin.series.page.form.uploaderror.default')))
    }
  } catch (error) {
    options.onError(error)
  } finally {
    isUploading.value = false
  }
}

// 发布文章上传OG图片成功处理
const handleUploadSuccess = (response: any, file: any) => {
  //publishForm.customOGImage = URL.createObjectURL(file.raw)
  seriesForm.coverImage = response.full_url
  ElMessage.success(t('admin.series.page.form.uploadsuccess'))
}

// 上传失败处理
const handleUploadError = (error: any) => {
  ElMessage.error(t('admin.series.page.form.uploaderror.default'))
  isUploading.value = false
}

// 移除封面图片
const removeImage = () => {
  seriesForm.coverImage = ''
}
</script>

<style scoped lang="scss">
.create-series-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
  h1 {
    font-size: 24px;
    font-weight: 600;
    margin: 0;
  }

  p {
    margin: 0;
    color: #6b7280;
    font-size: 14px;
  }
}

.series-form {
  margin-bottom: 40px;
}

.form-input,
.form-textarea,
.form-select {
  width: 100%;
}

.form-hint {
  margin-top: 5px;
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 20px;
}

.label-content {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 1rem;
  font-weight: 600;
  color: var(--el-text-color-regular);
}

.upload-container {
  width: 100%;
}

.upload-area {
  /* border: 1px dashed #d1d5db; */
  border-radius: 8px;
  padding: 20px 20px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s;

  &:hover {
    border-color: #3b82f6;
  }
}

.upload-icon {
  font-size: 24px;
  color: #9ca3af;
  margin-bottom: 10px;
}

.upload-text {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 5px;
}

.upload-hint {
  font-size: 12px;
  color: #6b7280;
}

.uploaded-image {
  width: 100%;
  height: auto;
  border-radius: 8px;
  object-fit: cover;
}

.action-buttons {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 5px;
}

.create-button {
  padding: 10px 24px;
}

.upload-wrapper {
  position: relative;
  width: 100%;
  margin-top: 1rem;
}
.cover-image-wrapper {
  position: relative;
  display: inline-block;
  margin-bottom: 15px;
  width: 100%;
}

.cover-image {
  width: 100%;
  max-height: 400px;
  object-fit: cover;
  border-radius: 8px;
}

.delete-cover-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
}

.delete-cover-btn:hover {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: rgba(0, 0, 0, 0.8);
  color: white;
}
</style>
