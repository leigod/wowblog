<template>
  <div class="create-page-container">
    <div class="page-header">
      <h1>{{ t('admin.pages.page.edit.title') }}</h1>
      <p>{{ t('admin.pages.page.edit.description') }}</p>
    </div>

    <el-form
      ref="pageFormRef"
      :model="pageForm"
      :rules="formRules"
      label-position="top"
      size="large"
      class="page-form"
    >
      <!-- Title Field -->
      <el-form-item :label="t('admin.pages.page.form.title')" prop="title">
        <el-input
          v-model="pageForm.title"
          :placeholder="t('admin.pages.page.form.title_placeholder')"
        />
      </el-form-item>

      <!-- Page Content Editor -->
      <el-form-item :label="t('admin.pages.page.form.content')" prop="content" label-position="top">
        <div class="editor-container">
          <!-- <p class="editor-hint">
            Click to open the editor and add content via WYSIWYG.
          </p> -->
          <div class="readonly-textarea-wrapper" @click="openContentEditor">
            <el-input
              v-model="pageForm.content"
              type="textarea"
              :rows="8"
              :placeholder="t('admin.pages.page.form.content_placeholder')"
              readonly
              class="readonly-textarea"
            />
            <div class="textarea-overlay">
              <span class="click-hint">{{ t('admin.pages.page.form.content_edit') }}</span>
            </div>
          </div>
        </div>
      </el-form-item>

      <!-- Page Slug -->
      <el-form-item :label="t('admin.pages.page.form.slug')" prop="slug">
        <el-input
          v-model="pageForm.slug"
          :placeholder="t('admin.pages.page.form.slug_placeholder')"
        />
        <p class="form-hint">
          {{ t('admin.pages.page.form.slug_helptip') }}
        </p>
      </el-form-item>

      <!-- Social Media Image -->
      <el-form-item
        :label="t('admin.pages.page.form.cover')"
        label-position="top"
        prop="socialImage"
      >
        <template #label>
          <div class="label-content">
            <span>{{ t('admin.pages.page.form.cover') }}</span>
          </div>
        </template>
        <p class="form-hint">{{ t('admin.pages.page.form.cover_info') }}</p>
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
            <template v-if="!isUploading && !pageForm.socialImage">
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                <span v-html="$t('admin.pages.page.form.upload')"></span>
                <span>{{ $t('admin.pages.page.form.upload_helptip') }}</span>
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
            <template v-if="pageForm.socialImage">
              <div class="cover-image-wrapper">
                <img :src="pageForm.socialImage" alt="Page Cover" class="cover-image" />
                <el-button :icon="Delete" class="delete-cover-btn" @click="removeImage" />
              </div>
            </template>
          </el-upload>
          <p class="form-hint">
            {{ t('admin.pages.page.form.cover_helptip') }}
          </p>
        </div>
      </el-form-item>

      <!-- SEO Description -->
      <el-form-item :label="t('admin.pages.page.form.seodesc')" prop="seoDescription">
        <el-input
          v-model="pageForm.seoDescription"
          :placeholder="t('admin.pages.page.form.seodesc_placeholder')"
          type="textarea"
          :rows="2"
        />
        <p class="form-hint">
          {{ t('admin.pages.page.form.seodesc_helptip') }}
        </p>
      </el-form-item>

      <!-- Action Buttons -->
      <div class="form-actions">
        <el-button link class="back-button" @click="handleBack">
          <el-icon><ArrowLeft /></el-icon> {{ t('admin.general.btn.back') }}
        </el-button>
        <el-button type="primary" class="create-button" @click="handleSubmit">
          {{ t('admin.pages.page.edit.btn') }}
        </el-button>
      </div>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute, onBeforeRouteUpdate } from 'vue-router'
import { useI18n } from 'vue-i18n'
import {
  ElForm,
  ElFormItem,
  ElInput,
  ElButton,
  ElUpload,
  ElIcon,
  ElMessage,
  ElDialog
} from 'element-plus'
import { ArrowLeft, Delete, Upload, ZoomIn } from '@element-plus/icons-vue'
import { updatePage, getPageInfo } from '@/api/services/pages'
import { uploadFile } from '@/api/services/common'
// import { getUserMe } from '@/api/services/user'

// 初始化i18n
const { t } = useI18n()

// 直接使用reactive对象而不是ref包装的对象
const pageForm = reactive<{
  title: string
  content: string
  slug: string
  socialImage: string | null
  seoDescription: string | null
}>({
  title: '',
  content: '',
  slug: '',
  socialImage: null,
  seoDescription: null
})

// Form validation rules
const formRules = {
  title: [
    { required: true, message: t('admin.pages.page.validate.title'), trigger: 'blur' },
    { max: 100, message: t('admin.pages.page.validate.title_length'), trigger: 'blur' }
  ],
  content: [{ required: true, message: t('admin.pages.page.validate.content'), trigger: 'change' }],
  slug: [
    { required: true, message: t('admin.pages.page.validate.slug'), trigger: 'blur' },
    {
      pattern: /^[a-z0-9-]+$/,
      message: t('admin.pages.page.validate.slug_format'),
      trigger: 'blur'
    },
    { max: 100, message: t('admin.pages.page.validate.slug_length'), trigger: 'blur' }
  ],
  seoDescription: [
    { max: 500, message: t('admin.pages.page.validate.seodesc_length'), trigger: 'blur' }
  ]
}

// Refs
const pageFormRef = ref<InstanceType<typeof ElForm>>()
const previewDialog = ref(false)
const previewImage = ref('')
const router = useRouter()
const route = useRoute()

// 处理表单提交
const handleSubmit = async () => {
  if (!pageFormRef.value) return

  try {
    const valid = await pageFormRef.value.validate()
    if (valid) {
      const reqData = {
        title: pageForm.title,
        content: pageForm.content,
        slug: pageForm.slug,
        image: pageForm.socialImage,
        seo_desc: pageForm.seoDescription
      }

      console.log('Submitting form with data:', reqData)

      const res = await updatePage(route.params.id as string, reqData)
      console.log('API response:', res)
      if (res.code === 1) {
        ElMessage.success(t('admin.pages.page.edit.success'))
        localStorage.removeItem('tempEditorContent')
        localStorage.removeItem('tempPageTitle')
        localStorage.removeItem('tempPageSlug')
        localStorage.removeItem('tempPageCover')
        localStorage.removeItem('tempPageDescription')
        router.push('/admin/pages')
      } else {
        ElMessage.error(t('admin.pages.page.edit.error'))
      }
    }
  } catch (error) {
    ElMessage.error(t('admin.pages.page.form.validate'))
  }
}

// 打开内容编辑器
const openContentEditor = () => {
  // 保存当前内容到localStorage
  localStorage.setItem('tempPageTitle', pageForm.title)
  localStorage.setItem('tempPageSlug', pageForm.slug)
  localStorage.setItem('tempPageCover', pageForm.socialImage || '')
  localStorage.setItem('tempPageDescription', pageForm.seoDescription || '')
  router.push({
    path: '/admin/content-editor',
    query: {
      content: pageForm.content,
      pageId: route.params.id,
      mode: 'edit'
    }
  })
}

// 返回上一页
const handleBack = () => {
  router.push('/admin/pages')
}

// 预览上传的图片
const handlePreview = (file: any) => {
  previewImage.value = file.url || file.preview
  previewDialog.value = true
}

// 上传前验证
const beforeUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error(t('admin.pages.page.form.uploaderror.format'))
    return false
  }

  const fileSize = file.size / 1024 / 1024 < 2
  if (!fileSize) {
    ElMessage.error(t('admin.pages.page.form.uploaderror.size'))
    return false
  }

  return true
}

// 加载内容（从路由参数或localStorage）
const loadContent = () => {
  // 优先从路由参数获取内容
  if (route.query.content) {
    pageForm.content = route.query.content as string
    localStorage.setItem('tempEditorContent', pageForm.content)
  } else {
    // 如果路由参数中没有，则尝试从localStorage获取
    const savedContent = localStorage.getItem('tempEditorContent')
    if (savedContent) {
      pageForm.content = savedContent
    }
  }
  if (route.query.content) {
    // 从localStorage获取其他字段
    const savedTitle = localStorage.getItem('tempPageTitle')
    const savedSlug = localStorage.getItem('tempPageSlug')
    const savedCover = localStorage.getItem('tempPageCover')
    const savedDescription = localStorage.getItem('tempPageDescription')

    if (savedTitle) {
      pageForm.title = savedTitle
    }
    if (savedSlug) {
      pageForm.slug = savedSlug
    }
    if (savedCover) {
      pageForm.socialImage = savedCover
    }
    if (savedDescription) {
      pageForm.seoDescription = savedDescription
    }
  }
}

// 组件挂载时
onMounted(() => {
  loadPageInfo()
  setTimeout(() => {
    loadContent()
  }, 100)

  // 仅用于调试，实际项目中可以移除
  // getUserMe().then((res) => {
  //   console.log(res)
  // })
})

// 监听路由参数变化
onBeforeRouteUpdate((to) => {
  if (to.query.content) {
    pageForm.content = to.query.content as string
    localStorage.setItem('tempEditorContent', pageForm.content)
  }
})

const loadPageInfo = async () => {
  try {
    const res = await getPageInfo(route.params.id as string)
    console.log(res)
    if (res.code === 1) {
      pageForm.title = res.data.title
      pageForm.slug = res.data.slug
      pageForm.content = res.data.content
      pageForm.socialImage = res.data.image
      pageForm.seoDescription = res.data.seo_desc
    }
  } catch (error) {
    console.error('加载页面信息失败:', error)
    // 将错误向上传播，确保全局错误处理能够正常工作
    throw error
  }
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
      options.onError(new Error(res.msg || t('admin.pages.page.form.uploaderror.default')))
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
  pageForm.socialImage = response.full_url
  ElMessage.success(t('admin.pages.page.form.uploadsuccess'))
}

// 上传失败处理
const handleUploadError = (error: any) => {
  ElMessage.error(t('admin.pages.page.form.uploaderror.default'))
  isUploading.value = false
}

// 移除封面图片
const removeImage = () => {
  pageForm.socialImage = ''
}
</script>

<style scoped>
.create-page-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
  margin-bottom: 50px;
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

.page-form {
  background-color: #fff;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.editor-container {
  margin-top: 10px;
  width: 100%;
}

.editor-hint {
  color: #606266;
  margin-bottom: 10px;
  font-size: 14px;
}

.readonly-textarea-wrapper {
  position: relative;
  cursor: pointer;
}

.readonly-textarea {
  /* background-color: #f5f7fa; */
  /* border: 1px dashed #dcdfe6; */
  min-height: 200px;
  resize: vertical;
  width: 100%;
}

.textarea-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(255, 255, 255, 0.8);
  border-radius: 4px;
  opacity: 0;
  transition: opacity 0.3s;
}

.readonly-textarea-wrapper:hover .textarea-overlay {
  opacity: 1;
}

.click-hint {
  background-color: #409eff;
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  pointer-events: none;
}

.form-hint {
  color: #909399;
  font-size: 12px;
  margin-top: 4px;
  line-height: 1.5;
}

.upload-container {
  margin-top: 20px;
  width: 100%;
}

.upload-area {
  /* border: 1px dashed #dcdfe6; */
  border-radius: 4px;
  width: 100%;
  height: 150px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: border-color 0.3s;
}

.upload-area:hover {
  border-color: #409eff;
}

.upload-icon {
  font-size: 28px;
  color: #c0c4cc;
  margin-bottom: 10px;
}

.upload-text {
  text-align: center;
  color: #909399;
}

.upload-hint {
  font-size: 12px;
  margin-top: 4px;
}

.uploaded-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.form-actions {
  margin-top: 30px;
  display: flex;
  justify-content: space-between;
}

.back-button {
  display: flex;
  align-items: center;
}

.create-button {
  min-width: 120px;
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

@media (max-width: 768px) {
  .create-page-container {
    padding: 15px;
  }

  .page-form {
    padding: 16px;
  }

  .form-actions {
    flex-direction: column-reverse;
    gap: 10px;
  }

  .back-button {
    width: 100%;
    justify-content: center;
  }

  .create-button {
    width: 100%;
  }
}
</style>
