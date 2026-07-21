<template>
  <div class="create-category-container">
    <div class="page-header">
      <h1>{{ t('admin.category.page.edit.title') }}</h1>
      <p>{{ t('admin.category.page.edit.description') }}</p>
    </div>

    <el-form
      ref="categoryFormRef"
      :model="categoryForm"
      :rules="formRules"
      label-width="120px"
      class="category-form"
      label-position="top"
      size="large"
    >
      <el-form-item :label="t('admin.category.page.form.name')" prop="name">
        <el-input
          v-model="categoryForm.name"
          :placeholder="t('admin.category.page.form.name_placeholder')"
          maxlength="50"
          show-word-limit
        />
      </el-form-item>

      <el-form-item :label="t('admin.category.page.form.parent')" prop="parentId">
        <el-tree-select
          v-model="categoryForm.parentId"
          :data="categoryTreeData"
          :render-after-expand="false"
          :default-expand-all="true"
          :check-strictly="true"
          :props="{
            label: 'label',
            value: 'value',
            children: 'children'
          }"
          :placeholder="t('admin.category.page.form.parent_placeholder')"
        />
      </el-form-item>

      <el-form-item :label="t('admin.category.page.form.description')" prop="description">
        <el-input
          v-model="categoryForm.description"
          :placeholder="t('admin.category.page.form.description_placeholder')"
          type="textarea"
          :rows="4"
          maxlength="200"
          show-word-limit
        />
      </el-form-item>

      <el-form-item :label="t('admin.category.page.form.slug')" prop="slug">
        <el-input
          v-model="categoryForm.slug"
          :placeholder="t('admin.category.page.form.slug_placeholder')"
          maxlength="100"
          show-word-limit
        />
        <div class="form-hint">{{ t('admin.category.page.form.slug_helptip') }}</div>
      </el-form-item>

      <el-form-item :label="t('admin.category.page.form.cover')">
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
            <template v-if="!isUploading && !categoryForm.coverImage">
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                <span v-html="$t('admin.category.page.form.upload')"></span>
                <span>{{ t('admin.category.page.form.upload_helptip') }}</span>
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
            <template v-if="categoryForm.coverImage">
              <div class="cover-image-wrapper">
                <img :src="categoryForm.coverImage" alt="Category Cover" class="cover-image" />
                <el-button :icon="Delete" class="delete-cover-btn" @click="removeImage" />
              </div>
            </template>
          </el-upload>
        </div>
      </el-form-item>

      <el-form-item :label="t('admin.category.page.form.order')" prop="articleSort">
        <el-select
          v-model="categoryForm.articleSort"
          :placeholder="t('admin.category.page.form.order_placeholder')"
        >
          <el-option :label="t('admin.category.table.head.order_new')" value="newest"></el-option>
          <el-option :label="t('admin.category.table.head.order_hot')" value="hottest"></el-option>
          <el-option
            :label="t('admin.category.table.head.order_pubtime')"
            value="oldest"
          ></el-option>
        </el-select>
      </el-form-item>

      <el-form-item class="form-actions">
        <el-button type="default" @click="navigateBack">{{
          t('admin.general.btn.cancel')
        }}</el-button>
        <el-button type="primary" @click="handleSubmit">{{
          t('admin.category.page.edit.btn')
        }}</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import {
  ElForm,
  ElFormItem,
  ElInput,
  ElSelect,
  ElOption,
  ElUpload,
  ElButton,
  ElImage,
  ElMessage
} from 'element-plus'
import { Upload, Delete } from '@element-plus/icons-vue'
import type { FormInstance, UploadProps, UploadFile } from 'element-plus'
import { getManageCategoryList, updateCategory, getCategoryInfo } from '@/api/services/categories'
import { uploadFile } from '@/api/services/common'

// 定义表单数据接口
interface CategoryForm {
  name: string
  parentId: string
  description: string
  slug: string
  coverImage: string | null
  articleSort: 'newest' | 'hottest' | 'oldest'
}

// 定义父分类接口
interface ParentCategory {
  id: string
  name: string
}

const { t } = useI18n()

// 表单引用
const categoryFormRef = ref<FormInstance>()

// 表单数据
const categoryForm = reactive<CategoryForm>({
  name: '',
  parentId: '',
  description: '',
  slug: '',
  coverImage: null,
  articleSort: 'newest'
})

// 上传文件列表
const uploadFileList = ref<UploadFile[]>([])

// 父分类列表（模拟数据）
const parentCategories = ref<ParentCategory[]>([])

// 表单验证规则
const formRules = reactive<Record<string, any>>({
  name: [
    { required: true, message: t('admin.category.page.validate.name'), trigger: 'blur' },
    { min: 2, max: 50, message: t('admin.category.page.validate.name_length'), trigger: 'blur' }
  ],
  slug: [
    { required: true, message: t('admin.category.page.validate.slug'), trigger: 'blur' },
    {
      pattern: /^[a-zA-Z0-9_-]+$/,
      message: t('admin.category.page.validate.slug_format'),
      trigger: 'blur'
    },
    { min: 2, max: 100, message: t('admin.category.page.validate.slug_length'), trigger: 'blur' }
  ],
  articleSort: [
    { required: true, message: t('admin.category.page.validate.article_sort'), trigger: 'change' }
  ]
})

const router = useRouter()
const route = useRoute()

// 生命周期钩子
onMounted(() => {
  // 加载父分类数据（实际项目中应该从API获取）
  loadParentCategories()
  // 加载分类详情
  loadCategoryDetails()
})

// 树形选择器数据
const categoryTreeData = ref<any[]>([
  {
    value: '0',
    label: t('admin.category.page.form.parent_default')
  }
])

// 加载父分类数据
const loadParentCategories = async () => {
  try {
    // 实际项目中从API获取分类列表
    const res = await getManageCategoryList()
    if (res.code === 1) {
      // 服务端返回的字段：id, name, pid, cat_desc, slug, image, articles_order, sort

      // 将扁平数据转换为树形结构
      const categories = res.data

      // 创建分类映射表用于快速查找
      const categoryMap = new Map<string, any>()

      // 初始化顶级分类数组
      const rootCategories: any[] = []

      // 处理所有分类，创建映射并找出顶级分类
      categories.forEach((category: any) => {
        const { id, name, pid } = category
        const categoryNode = {
          value: id.toString(),
          label: name,
          children: []
        }
        categoryMap.set(id.toString(), categoryNode)

        // 顶级分类：pid为0或null或空
        if (!pid || pid === 0 || pid === '0') {
          rootCategories.push(categoryNode)
        }
      })

      // 构建树形结构
      categories.forEach((category: any) => {
        const { id, pid } = category
        const categoryNode = categoryMap.get(id.toString())

        // 非顶级分类需要找到其父分类并添加为子节点
        if (pid && pid !== 0 && pid !== '0') {
          const parentNode = categoryMap.get(pid.toString())
          if (parentNode) {
            parentNode.children.push(categoryNode)
          }
        }
      })

      // 更新树形数据，包含"无（顶级分类）"选项和所有层级分类
      categoryTreeData.value = [
        { value: '0', label: t('admin.category.page.form.parent_default') },
        ...rootCategories
      ]
    }
  } catch (error) {
    console.error('加载分类数据失败:', error)
    ElMessage.error(t('admin.category.page.load.error'))
  }
}

// 加载分类详情
const loadCategoryDetails = async () => {
  try {
    const res = await getCategoryInfo(route.params.id as string)
    if (res.code === 1) {
      const category = res.data
      categoryForm.name = category.name
      categoryForm.parentId = category.pid.toString()
      categoryForm.description = category.cat_desc
      categoryForm.slug = category.slug
      categoryForm.coverImage = category.image
      categoryForm.articleSort =
        category.articles_order === 'id desc'
          ? 'newest'
          : category.articles_order === 'pubtime asc'
            ? 'oldest'
            : 'hottest'
    }
  } catch (error) {
    console.error('加载分类详情失败:', error)
    ElMessage.error(t('admin.category.page.load.error'))
  }
}

// 文件变化时的处理
const handleFileChange = (uploadFile: UploadFile, uploadFiles: UploadFile[]) => {
  // 只保留最后一次上传的文件
  uploadFileList.value = [uploadFile]
  // 显示预览
  if (uploadFile.raw) {
    categoryForm.coverImage = URL.createObjectURL(uploadFile.raw)
  }
}

// 表单提交
const handleSubmit = async () => {
  if (!categoryFormRef.value) return

  try {
    // 表单验证
    const valid = await categoryFormRef.value.validate()

    if (valid) {
      const reqData = {
        name: categoryForm.name,
        cat_desc: categoryForm.description,
        slug: categoryForm.slug,
        image: categoryForm.coverImage,
        articles_order:
          categoryForm.articleSort === 'newest'
            ? 'id desc'
            : categoryForm.articleSort === 'oldest'
              ? 'pubtime asc'
              : 'views desc',
        pid: categoryForm.parentId === '0' ? 0 : categoryForm.parentId
      }
      const res = await updateCategory(route.params.id as string, reqData)
      console.log(res)
      if (res.code === 1) {
        ElMessage.success(t('admin.category.page.edit.success'))
        router.push('/admin/categories')
      } else {
        ElMessage.error(t('admin.category.page.edit.error'))
      }
    }

    // 模拟API提交
    console.log('提交分类数据:', categoryForm)
  } catch (error) {
    console.error('表单验证失败:', error)
    ElMessage.error(t('admin.category.page.form.validate'))
  }
}

// 取消并返回
const navigateBack = () => {
  router.push('/admin/categories')
}

// 上传前验证
const beforeUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error(t('admin.category.page.form.uploaderror.format'))
    return false
  }

  const fileSize = file.size / 1024 / 1024 < 2
  if (!fileSize) {
    ElMessage.error(t('admin.category.page.form.uploaderror.size'))
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
      options.onError(new Error(res.msg || t('admin.category.page.form.uploaderror.default')))
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
  categoryForm.coverImage = response.full_url
  ElMessage.success(t('admin.category.page.form.uploadsuccess'))
}

// 上传失败处理
const handleUploadError = (error: any) => {
  ElMessage.error(t('admin.category.page.form.uploaderror.default'))
  isUploading.value = false
}

// 移除封面图片
const removeImage = () => {
  categoryForm.coverImage = ''
}
</script>

<style scoped lang="scss">
.create-category-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 15px;

  h1 {
    margin: 0 0 5px 0;
    font-size: 24px;
    font-weight: 600;
  }

  p {
    margin: 0;
    color: #6b7280;
    font-size: 14px;
  }
}

.category-form {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.form-hint {
  color: #6b7280;
  font-size: 12px;
  margin-top: 4px;
  line-height: 1.5;
}

.upload-demo {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  padding: 20px;
  text-align: center;
}

.upload-icon {
  font-size: 28px;
  color: #409eff;
  margin-bottom: 16px;
}

.upload-text {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 8px;
}

.upload-hint {
  font-size: 12px;
  color: #9ca3af;
}

.image-preview {
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.remove-image-btn {
  color: #f56c6c;
  padding: 0;
  height: auto;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.upload-container {
  /* margin-top: 20px; */
  width: 100%;
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
