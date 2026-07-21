<template>
  <div class="tag-management-container">
    <div class="page-header">
      <h1>{{ $t('admin.tags.title') }}</h1>
      <p>{{ $t('admin.tags.title_info') }}</p>
    </div>

    <div class="table-actions">
      <el-input
        v-model="searchName"
        :placeholder="$t('admin.tags.action.search.placeholder')"
        clearable
        style="width: 40%"
        @input="handleSearch"
      ></el-input>
      <el-button type="primary" size="default" class="create-tag-btn" @click="openCreateDrawer">
        <el-icon><Plus /></el-icon> {{ $t('admin.tags.btn.add') }}
      </el-button>
    </div>

    <!-- 移动端卡片布局 -->
    <template v-if="isMobile">
      <div v-loading="loading" class="mobile-tags-container">
        <el-card v-for="tag in tagList" :key="tag.id" class="mobile-tag-card">
          <div class="tag-card-header">
            <div class="tag-title">
              <el-image
                v-if="tag.image"
                :src="tag.image"
                alt="封面"
                class="tag-cover"
                :preview-src-list="[tag.image]"
                preview-teleported
              />
              <div v-else class="tag-cover-placeholder">
                <el-icon><PriceTag /></el-icon>
              </div>
              <div class="tag-info">
                <h3>{{ tag.name }}</h3>
                <p v-if="tag.description">{{ tag.description }}</p>
              </div>
            </div>
          </div>

          <div class="tag-card-body">
            <div class="info-row">
              <span class="label">{{ $t('admin.tags.table.slug') }}:</span>
              <span class="value">/{{ tag.slug }}</span>
            </div>
            <div class="info-row">
              <span class="label">{{ $t('admin.tags.table.visibility') }}:</span>
              <el-switch v-model="tag.visible" @change="handleStatusChange(tag)" />
            </div>
          </div>

          <template #footer>
            <div class="tag-card-actions">
              <el-button @click="openEditDrawer(tag)" size="small">
                <el-icon><Edit /></el-icon>
              </el-button>
              <el-button @click="handleDelete(tag)" type="danger" size="small">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </template>
        </el-card>
      </div>
    </template>

    <!-- 桌面端表格布局 -->
    <el-table
      v-else
      v-loading="loading"
      :data="tagList"
      row-key="id"
      class="tag-table"
      :header-cell-style="{
        backgroundColor: '#fafafa',
        fontWeight: 800,
        fontSize: '1rem',
        padding: '12px 14px'
      }"
    >
      <el-table-column
        prop="name"
        :label="$t('admin.tags.table.name')"
        width="200"
      ></el-table-column>
      <el-table-column
        prop="description"
        :label="$t('admin.tags.table.description')"
        show-overflow-tooltip
      ></el-table-column>
      <el-table-column
        prop="slug"
        :label="$t('admin.tags.table.slug')"
        width="180"
        show-overflow-tooltip
      ></el-table-column>
      <el-table-column :label="$t('admin.tags.table.cover')" width="120">
        <template #default="{ row }">
          <el-image
            v-if="row.image"
            :src="row.image"
            alt="封面"
            style="width: 40px; height: 40px; object-fit: fill; z-index: 1"
            :preview-src-list="[row.image]"
            preview-teleported
          />
          <span v-else class="no-image">{{ $t('admin.tags.table.no_cover') }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="$t('admin.tags.table.visibility')" width="120">
        <template #default="{ row }">
          <el-switch v-model="row.visible" @change="handleStatusChange(row)" />
        </template>
      </el-table-column>
      <el-table-column :label="$t('admin.tags.table.actions')" width="180" fixed="right">
        <template #default="{ row }">
          <div class="operation-buttons">
            <el-button type="default" circle @click="openEditDrawer(row)"
              ><el-icon><Edit /></el-icon
            ></el-button>
            <el-button type="default" circle class="text-danger" @click="handleDelete(row)"
              ><el-icon><Delete /></el-icon
            ></el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :page-sizes="[10, 20, 30, 50]"
      size="default"
      :disabled="false"
      :background="true"
      layout="total, sizes, prev, pager, next, jumper"
      :total="totalTags"
      :hide-on-single-page="true"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
      style="margin-top: 20px"
    />
    <!-- 创建/编辑标签抽屉 -->
    <el-drawer
      v-model="drawerVisible"
      :title="
        isEditMode ? $t('admin.tags.drawer.edit.title') : $t('admin.tags.drawer.create.title')
      "
      :size="isMobile ? '100%' : '30%'"
      footer-class="drawer-footer-wrapper"
    >
      <el-form
        ref="tagFormRef"
        :model="tagForm"
        :rules="formRules"
        label-width="120px"
        class="tag-form"
        label-position="top"
        size="large"
      >
        <el-form-item :label="$t('admin.tags.drawer.form.name')" prop="name">
          <el-input
            v-model="tagForm.name"
            :placeholder="$t('admin.tags.drawer.form.name_placeholder')"
            maxlength="30"
            show-word-limit
          />
        </el-form-item>
        <el-form-item :label="$t('admin.tags.drawer.form.type')" prop="type">
          <el-select
            v-model="tagForm.type"
            :placeholder="$t('admin.tags.drawer.form.type_placeholder')"
          >
            <el-option :label="$t('admin.tags.drawer.form.type_sys')" value="sys"></el-option>
            <el-option :label="$t('admin.tags.drawer.form.type_user')" value="user"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('admin.tags.drawer.form.slug')" prop="slug">
          <el-input
            v-model="tagForm.slug"
            :placeholder="$t('admin.tags.drawer.form.slug_placeholder')"
            maxlength="30"
            show-word-limit
          />
          <p class="form-hint">
            {{ $t('admin.tags.drawer.form.slug_helptip') }}
          </p>
        </el-form-item>
        <el-form-item :label="$t('admin.tags.drawer.form.description')" prop="description">
          <el-input
            v-model="tagForm.description"
            :placeholder="$t('admin.tags.drawer.form.description_placeholder')"
            type="textarea"
            :rows="4"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>

        <el-form-item :label="$t('admin.tags.drawer.form.status')">
          <el-switch
            v-model="tagForm.visible"
            :active-text="$t('admin.tags.drawer.form.status_visible')"
            :inactive-text="$t('admin.tags.drawer.form.status_hidden')"
          />
        </el-form-item>

        <el-form-item :label="$t('admin.tags.drawer.form.cover')" class="form-label">
          <div class="form-tip">{{ $t('admin.tags.drawer.form.cover_info') }}</div>
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
            <template v-if="!isUploading && !tagForm.image">
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                <span v-html="$t('admin.tags.drawer.form.upload')"></span>
                <span>{{ $t('admin.tags.drawer.form.upload_helptip') }}</span>
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
            <template v-if="tagForm.image">
              <div class="cover-image-wrapper">
                <img :src="tagForm.image" alt="Article Cover" class="cover-image" />
                <el-button :icon="Delete" class="delete-cover-btn" @click="removeImage" />
              </div>
            </template>
          </el-upload>
        </el-form-item>

        <!-- <el-form-item class="form-actions">
          <el-button type="default" @click="closeDrawer">取消</el-button>
          <el-button type="primary" @click="handleSubmit">保存</el-button>
        </el-form-item> -->
      </el-form>
      <template #footer>
        <div class="drawer-footer">
          <el-button type="default" @click="closeDrawer">
            {{ $t('admin.general.btn.cancel') }}
          </el-button>
          <el-button type="primary" @click="handleSubmit">
            {{ $t('admin.general.btn.save') }}
          </el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  ElTable,
  ElTableColumn,
  ElButton,
  ElDrawer,
  ElForm,
  ElFormItem,
  ElInput,
  ElSwitch,
  ElMessage,
  ElMessageBox
} from 'element-plus'
import { Plus, Delete, Edit, PriceTag } from '@element-plus/icons-vue'
import { useMobileDetection } from '@/composables/useMobileDetection'
import type { FormInstance } from 'element-plus'
import {
  createTag,
  updateTag,
  deleteTag,
  getTagList,
  updateTagStatus,
  getTagInfo
} from '@/api/services/tags'
import { uploadFile } from '@/api/services/common'

// 定义标签接口
interface Tag {
  id: string
  name: string
  type: string
  slug: string
  image: string
  description: string
  visible: boolean
}

// 定义表单数据接口
interface TagForm {
  id?: string
  name: string
  description: string
  visible: boolean
  type: string
  slug: string
  image: string
}

const { t } = useI18n()

// 移动端检测
const { isMobile } = useMobileDetection()

// 状态定义
const tagList = ref<Tag[]>([])
const loading = ref(true)
const drawerVisible = ref(false)
const isEditMode = ref(false)
const tagFormRef = ref<FormInstance>()

// 分页定义
const currentPage = ref(1)
const pageSize = ref(10)
const totalTags = ref(0)

// 搜索定义
const searchName = ref('')

// 表单数据
const tagForm = reactive<TagForm>({
  name: '',
  type: '',
  slug: '',
  image: '',
  description: '',
  visible: true
})

// 表单验证规则接口
interface FormRules {
  name: Array<{
    required?: boolean
    message?: string
    trigger?: string
    min?: number
    max?: number
  }>
  type: Array<{
    required?: boolean
    message?: string
    trigger?: string
  }>
  slug: Array<{
    required?: boolean
    message?: string
    trigger?: string
    min?: number
    max?: number
    pattern?: RegExp
  }>
}

// 表单验证规则
const formRules = reactive<FormRules>({
  name: [
    { required: true, message: t('admin.tags.drawer.validate.name'), trigger: 'blur' },
    { min: 1, max: 30, message: t('admin.tags.drawer.validate.name_length'), trigger: 'blur' }
  ],
  type: [{ required: true, message: t('admin.tags.drawer.validate.type'), trigger: 'change' }],
  slug: [
    { required: true, message: t('admin.tags.drawer.validate.slug'), trigger: 'blur' },
    { min: 1, max: 30, message: t('admin.tags.drawer.validate.slug_length'), trigger: 'blur' },
    {
      pattern: /^[a-z0-9-]+$/,
      message: t('admin.tags.drawer.validate.slug_format'),
      trigger: 'blur'
    }
  ]
})

// 生命周期钩子
onMounted(() => {
  // 加载标签数据
  loadTagList()
})

// 加载标签列表（模拟API）
const loadTagList = async () => {
  loading.value = true
  // 模拟API请求延迟
  try {
    const tempTagList: Tag[] = []
    const res = await getTagList(currentPage.value, pageSize.value, searchName.value)
    if (res.code === 1) {
      totalTags.value = res.data.total
      pageSize.value = res.data.pageSize
      currentPage.value = res.data.page

      res.data.list.forEach((item: any) => {
        tempTagList.push({
          id: item.id,
          name: item.name,
          type: item.type,
          slug: item.slug,
          image: item.image,
          description: item.tag_desc,
          visible: item.status === 'normal' ? true : false
        })
      })
      tagList.value = tempTagList
      loading.value = false
    }
  } catch (error) {
    console.error('获取标签列表失败:', error)
  }
}

// 打开创建抽屉
const openCreateDrawer = () => {
  isEditMode.value = false
  // 重置表单
  tagForm.id = undefined
  tagForm.name = ''
  tagForm.type = 'sys'
  tagForm.slug = ''
  tagForm.image = ''
  tagForm.description = ''
  tagForm.visible = true
  drawerVisible.value = true
}

// 打开编辑抽屉
const openEditDrawer = (row: Tag) => {
  isEditMode.value = true
  // 填充表单数据
  tagForm.id = row.id
  tagForm.name = row.name
  tagForm.type = row.type
  tagForm.slug = row.slug
  tagForm.image = row.image
  tagForm.description = row.description
  tagForm.visible = row.visible
  drawerVisible.value = true
}

// 关闭抽屉
const closeDrawer = () => {
  drawerVisible.value = false
  // 重置表单验证
  if (tagFormRef.value) {
    tagFormRef.value.resetFields()
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!tagFormRef.value) return

  try {
    // 表单验证
    await tagFormRef.value.validate()
    const reqData = {
      name: tagForm.name,
      type: tagForm.type,
      slug: tagForm.slug,
      image: tagForm.image,
      tag_desc: tagForm.description,
      status: tagForm.visible ? 'normal' : 'hidden'
    }

    if (isEditMode.value) {
      // 编辑标签
      const res = await updateTag(tagForm.id as string, reqData)
      if (res.code === 1) {
        const index = tagList.value.findIndex((tag) => tag.id === tagForm.id)
        if (index !== -1) {
          tagList.value[index] = { ...(tagForm as Tag) }
          ElMessage.success(t('admin.tags.drawer.edit.success'))
        }
      }
    } else {
      // 创建新标签
      const res = await createTag(reqData)
      if (res.code === 1) {
        // 刷新标签列表
        loadTagList()
        // tagList.value.unshift(newTag)
        ElMessage.success(t('admin.tags.drawer.create.success'))
      }
    }

    // 关闭抽屉
    closeDrawer()
  } catch (error) {
    console.error('表单验证失败:', error)
    ElMessage.error(t('admin.tags.drawer.form.validate'))
  }
}

// 更改显示状态
const handleStatusChange = async (row: Tag) => {
  // console.log('变更前状态', row.visible)
  // row.visible = !row.visible
  // console.log('变更后状态', row.visible)
  const status = row.visible ? 'normal' : 'hidden'
  const res = await updateTagStatus(row.id as string, status)
  if (res.code === 1) {
    console.log(`标签 ${row.name} 显示状态变为:`, status)
    // 刷新标签列表
    loadTagList()

    ElMessage.success(
      t('admin.tags.action.toggle.success', {
        action: status === 'normal' ? t('admin.tags.action.show') : t('admin.tags.action.hide'),
        tagname: row.name
      })
    )
  } else {
    ElMessage.error(
      t('admin.tags.action.toggle.error', {
        action: status === 'normal' ? t('admin.tags.action.show') : t('admin.tags.action.hide'),
        tagname: row.name
      })
    )
  }
}

// 删除标签
const handleDelete = (row: Tag) => {
  ElMessageBox.confirm(
    t('admin.tags.action.delete.confirm', { tagname: row.name }),
    t('admin.tags.action.delete.title'),
    {
      confirmButtonText: t('admin.tags.action.delete.btn.confirm'),
      cancelButtonText: t('admin.tags.action.delete.btn.cancel'),
      type: 'warning'
    }
  )
    .then(async () => {
      // 执行删除
      const res = await deleteTag(row.id as string)
      if (res.code === 1) {
        tagList.value = tagList.value.filter((tag) => tag.id !== row.id)
        ElMessage.success(t('admin.tags.action.delete.success', { tagname: row.name }))
      } else {
        ElMessage.error(t('admin.tags.action.delete.error', { tagname: row.name }))
      }
    })
    .catch(() => {
      // 取消删除
      console.log('取消删除标签')
    })
}

// 上传进度
const uploadProgress = ref(0)
const isUploading = ref(false)

// 上传前验证
const beforeUpload = (file: File) => {
  const isJPG = file.type === 'image/jpeg' || file.type === 'image/png'
  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isJPG) {
    ElMessage.error(t('admin.tags.drawer.form.uploaderror.format'))
    return false
  }
  if (!isLt2M) {
    ElMessage.error(t('admin.tags.drawer.form.uploaderror.size'))
    return false
  }
  return true
}

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
      options.onError(new Error(res.msg || t('admin.tags.drawer.form.uploaderror.default')))
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
  tagForm.image = response.full_url
  ElMessage.success(t('admin.tags.drawer.form.uploadsuccess'))
}

// 上传失败处理
const handleUploadError = (error: any) => {
  ElMessage.error(t('admin.tags.drawer.form.uploaderror.default'))
  isUploading.value = false
}

// 移除封面图片
const removeImage = () => {
  tagForm.image = ''
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  loadTagList()
  console.log(`${val} items per page`)
}
const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadTagList()
  console.log(`current page: ${val}`)
}

// 搜索标签
const handleSearch = (val: string) => {
  // 重置到第一页
  currentPage.value = 1
  // 如果输入为空或长度大于等于2，则执行搜索
  if (val.length === 0 || val.length >= 2) {
    loadTagList()
  }
}
</script>

<style scoped lang="scss">
.tag-management-container {
  padding: 20px;
  min-height: 100vh;
  box-sizing: border-box;
}

.page-header {
  margin-bottom: 20px;
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

.table-actions {
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
}

.tag-table {
  width: 100%;
  margin-bottom: 20px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.operation-buttons {
  display: flex;
  gap: 10px;
}

.tag-form {
  padding-top: 20px;
}

.drawer-footer-wrapper {
  padding: 0;
  border-top: 1px solid #e5e7eb;
}

.drawer-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 30px;
  padding-top: 15px;
  border-top: 1px solid #e5e7eb;
}

.form-tip {
  color: var(--el-color-regular-text);
  font-weight: 200;
  line-height: 1.375rem;
}

.form-label {
  font-weight: 600;
  color: var(--el-color-secondary-text);
}

.form-hint {
  margin-top: 5px;
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 20px;
  line-height: 1.5;
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
  max-height: 200px;
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

.no-image {
  display: inline-block;
  width: 40px;
  height: 40px;
  line-height: 40px;
  text-align: center;
  background-color: #f3f4f6;
  border-radius: 4px;
  color: #9ca3af;
  font-size: 12px;
}

/* 移动端适配 */
@media (max-width: 767px) {
  .table-actions {
    flex-direction: column;
    gap: 8px;
    align-items: stretch;
  }

  .table-actions .el-input {
    width: 100% !important;
  }

  .create-tag-btn {
    width: 100%;
  }

  /* 移动端标签卡片 */
  .mobile-tags-container {
    padding: 0;
  }

  .mobile-tag-card {
    margin-bottom: 12px;
    border-radius: 8px;
  }

  .mobile-tag-card :deep(.el-card__body) {
    padding: 16px;
  }

  .tag-card-header {
    margin-bottom: 16px;
  }

  .tag-title {
    display: flex;
    gap: 12px;
    align-items: flex-start;
  }

  .tag-cover {
    width: 50px;
    height: 50px;
    border-radius: 8px;
    object-fit: cover;
    flex-shrink: 0;
  }

  .tag-cover-placeholder {
    width: 50px;
    height: 50px;
    border-radius: 8px;
    background: var(--el-fill-color-light);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    color: var(--el-text-color-placeholder);
  }

  .tag-info {
    flex: 1;
    min-width: 0;
  }

  .tag-info h3 {
    margin: 0 0 8px 0;
    font-size: 16px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .tag-info p {
    margin: 0;
    font-size: 14px;
    color: var(--el-text-color-secondary);
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
  }

  .tag-card-body {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .info-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 14px;
  }

  .info-row .label {
    color: var(--el-text-color-secondary);
    flex-shrink: 0;
    margin-right: 8px;
  }

  .info-row .value {
    color: var(--el-text-color-primary);
    text-align: right;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .tag-card-actions {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
  }

  /* 分页优化 */
  .el-pagination :deep(.el-pagination__sizes),
  .el-pagination :deep(.el-pagination__jump) {
    display: none;
  }
}
</style>
