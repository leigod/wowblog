<template>
  <div class="docbook-management">
    <div class="page-header">
      <h1>{{ t('admin.docbook.title') }}</h1>
      <p>{{ t('admin.docbook.title_info') }}</p>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <el-input v-model="searchKeyword" :placeholder="t('admin.docbook.search_placeholder')" prefix-icon="Search"
        class="search-input" @input="handleSearch" />
      <el-button type="primary" icon="Plus" @click="handleCreate">
        {{ t('admin.docbook.btn_create') }}
      </el-button>
    </div>

    <!-- 文档书列表 -->
    <!-- 桌面端表格 -->
    <el-table v-if="!isMobile" :data="docbooks" class="docbooks-table"
      :header-cell-style="{ backgroundColor: '#fafafa', fontWeight: 600 }" v-loading="loading">
      <template #empty>
        <div class="empty-state">
          <el-icon class="empty-icon">
            <FolderOpened />
          </el-icon>
          <h3>{{ t('admin.docbook.empty.title') }}</h3>
          <p>{{ t('admin.docbook.empty.description') }}</p>
        </div>
      </template>

      <el-table-column :label="t('admin.docbook.table.cover')" width="80">
        <template #default="scope">
          <div v-if="scope.row.cover" class="cover-thumb">
            <img :src="scope.row.cover" :alt="scope.row.name" />
          </div>
          <div v-else class="cover-placeholder">
            <span>{{ scope.row.icon || '?' }}</span>
          </div>
        </template>
      </el-table-column>

      <el-table-column prop="name" :label="t('admin.docbook.table.name')" min-width="200">
        <template #default="scope">
          <div class="name-cell">
            <div class="name-text">{{ scope.row.name }}</div>
            <div class="slug-text">/{{ scope.row.slug }}</div>
          </div>
        </template>
      </el-table-column>

      <el-table-column prop="doc_count" :label="t('admin.docbook.table.doc_count')" width="80" align="center">
        <template #default="scope">
          <el-tag>{{ scope.row.doc_count }}</el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="is_public" :label="t('admin.docbook.table.visibility')" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.is_public ? 'success' : 'info'">
            {{ scope.row.is_public ? t('admin.docbook.visibility.public') : t('admin.docbook.visibility.private') }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="sort_order" :label="t('admin.docbook.table.sort_order')" width="80" align="center">
        <template #default="scope">
          <span>{{ scope.row.sort_order }}</span>
        </template>
      </el-table-column>

      <el-table-column prop="updatetime" :label="t('admin.docbook.table.update_time')" width="160">
        <template #default="scope">
          {{ formatDateTime(scope.row.updatetime) }}
        </template>
      </el-table-column>

      <el-table-column :label="t('admin.docbook.table.actions')" width="180" fixed="right">
        <template #default="scope">
          <el-tooltip placement="bottom" :content="t('admin.docbook.actions.manage_docs')">
            <el-button circle type="default" @click="handleViewDocs(scope.row)">
              <el-icon>
                <FolderOpened />
              </el-icon>
            </el-button>
          </el-tooltip>

          <el-tooltip placement="bottom" :content="t('admin.docbook.actions.edit')">
            <el-button circle type="default" @click="handleEdit(scope.row)">
              <el-icon>
                <Edit />
              </el-icon>
            </el-button>
          </el-tooltip>

          <el-tooltip placement="bottom" :content="t('admin.docbook.actions.delete')">
            <el-button circle type="default" @click="handleDelete(scope.row)">
              <el-icon>
                <Delete />
              </el-icon>
            </el-button>
          </el-tooltip>
        </template>
      </el-table-column>
    </el-table>

    <!-- 移动端卡片布局 -->
    <div v-else class="docbooks-cards" v-loading="loading">
      <div v-if="docbooks.length === 0" class="empty-state">
        <el-icon class="empty-icon">
          <FolderOpened />
        </el-icon>
        <h3>{{ t('admin.docbook.empty.title') }}</h3>
        <p>{{ t('admin.docbook.empty.description') }}</p>
      </div>
      <el-card v-for="docbook in docbooks" :key="docbook.id" class="docbook-card" shadow="hover">
        <div class="card-header">
          <div v-if="docbook.cover" class="card-cover">
            <img :src="docbook.cover" :alt="docbook.name" />
          </div>
          <div v-else class="card-cover-placeholder">
            <span>{{ docbook.icon || '?' }}</span>
          </div>
          <div class="card-title">
            <div class="name-text">{{ docbook.name }}</div>
            <div class="slug-text">/{{ docbook.slug }}</div>
          </div>
        </div>
        <div class="card-body">
          <div class="card-info-row">
            <span class="label">{{ t('admin.docbook.table.doc_count') }}:</span>
            <el-tag size="small">{{ docbook.doc_count }}</el-tag>
          </div>
          <div class="card-info-row">
            <span class="label">{{ t('admin.docbook.table.visibility') }}:</span>
            <el-tag :type="docbook.is_public ? 'success' : 'info'" size="small">
              {{ docbook.is_public ? t('admin.docbook.visibility.public') : t('admin.docbook.visibility.private') }}
            </el-tag>
          </div>
          <div class="card-info-row">
            <span class="label">{{ t('admin.docbook.table.sort_order') }}:</span>
            <span>{{ docbook.sort_order }}</span>
          </div>
          <div class="card-info-row">
            <span class="label">{{ t('admin.docbook.table.update_time') }}:</span>
            <span class="time-text">{{ formatDateTime(docbook.updatetime) }}</span>
          </div>
        </div>
        <div class="card-footer">
          <el-button size="small" @click="handleViewDocs(docbook)">
            {{ t('admin.docbook.actions.manage_docs') }}
          </el-button>
          <el-button size="small" type="primary" @click="handleEdit(docbook)">
            {{ t('admin.docbook.actions.edit') }}
          </el-button>
          <el-button size="small" type="danger" @click="handleDelete(docbook)">
            {{ t('admin.docbook.actions.delete') }}
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrapper">
      <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total"
        :page-sizes="[10, 20, 50, 100]" layout="total, sizes, prev, pager, next, jumper" @current-change="loadData"
        @size-change="loadData" />
    </div>

    <!-- 创建/编辑对话框 -->
    <el-dialog v-model="showEditDialog"
      :title="editingDocBook ? t('admin.docbook.dialog.edit_title') : t('admin.docbook.dialog.create_title')"
      :width="isMobile ? '95%' : '600px'" :close-on-click-modal="false">
      <el-form ref="formRef" :model="formData" :rules="formRules" :label-width="isMobile ? 'auto' : '100px'"
        :label-position="isMobile ? 'top' : 'right'">
        <el-form-item :label="t('admin.docbook.dialog.form.name')" prop="name">
          <el-input v-model="formData.name" :placeholder="t('admin.docbook.dialog.form.name_placeholder')" />
        </el-form-item>

        <el-form-item :label="t('admin.docbook.dialog.form.slug')" prop="slug">
          <el-input v-model="formData.slug" :placeholder="t('admin.docbook.dialog.form.slug_placeholder')"
            :disabled="!!editingDocBook">
            <template #prepend>{{ t('admin.docbook.dialog.form.slug_prefix') }}</template>
          </el-input>
        </el-form-item>

        <el-form-item :label="t('admin.docbook.dialog.form.description')" prop="description">
          <el-input v-model="formData.description" type="textarea" :rows="3"
            :placeholder="t('admin.docbook.dialog.form.description_placeholder')" />
        </el-form-item>

        <el-form-item :label="t('admin.docbook.dialog.form.cover')">
          <el-upload class="cover-uploader" :http-request="handleCustomUpload" :show-file-list="false"
            :before-upload="beforeCoverUpload" :disabled="isUploading">
            <div v-if="isUploading" class="upload-loading">
              <el-icon class="is-loading">
                <Loading />
              </el-icon>
              <span>{{ t('admin.docbook.dialog.cover_upload.uploading') }}</span>
            </div>
            <img v-else-if="formData.cover" :src="formData.cover" class="cover-preview" />
            <div v-else class="cover-placeholder">
              <el-icon>
                <Plus />
              </el-icon>
              <div>{{ t('admin.docbook.dialog.cover_upload.click_to_upload') }}</div>
              <div class="upload-tip">{{ t('admin.docbook.dialog.cover_upload.upload_tip') }}</div>
            </div>
          </el-upload>
          <div v-if="formData.cover && !isUploading" class="cover-actions">
            <el-button size="small" @click="formData.cover = ''">{{ t('admin.docbook.dialog.cover_upload.remove_cover')
            }}</el-button>
          </div>
        </el-form-item>

        <el-form-item :label="t('admin.docbook.dialog.form.icon')">
          <el-input v-model="formData.icon" :placeholder="t('admin.docbook.dialog.form.icon_placeholder')" />
        </el-form-item>

        <el-divider>{{ t('admin.docbook.dialog.form.settings') }}</el-divider>

        <el-form-item :label="t('admin.docbook.dialog.form.visibility')">
          <el-switch v-model="formData.is_public" :active-text="t('admin.docbook.dialog.form.visibility_public')"
            :inactive-text="t('admin.docbook.dialog.form.visibility_private')" />
        </el-form-item>

        <el-form-item :label="t('admin.docbook.dialog.form.show_sidebar')">
          <el-switch v-model="formData.show_sidebar" />
        </el-form-item>

        <el-form-item :label="t('admin.docbook.dialog.form.allow_comment')">
          <el-switch v-model="formData.allow_comment" />
        </el-form-item>

        <el-form-item :label="t('admin.docbook.dialog.form.allow_search')">
          <el-switch v-model="formData.allow_search" />
        </el-form-item>

        <el-form-item :label="t('admin.docbook.dialog.form.theme')">
          <el-select v-model="formData.theme" :placeholder="t('admin.docbook.dialog.form.theme_placeholder')">
            <el-option :label="t('admin.docbook.theme.default')" value="default" />
            <el-option :label="t('admin.docbook.theme.minimal')" value="minimal" />
            <el-option :label="t('admin.docbook.theme.dark')" value="dark" />
          </el-select>
        </el-form-item>

        <el-form-item :label="t('admin.docbook.dialog.form.sort_order')">
          <el-input-number v-model="formData.sort_order" :min="0" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showEditDialog = false">{{ t('admin.docbook.dialog.btn_cancel') }}</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ t('admin.docbook.dialog.btn_confirm') }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules, type UploadProps } from 'element-plus'
import { FolderOpened, Plus, Loading, Document } from '@element-plus/icons-vue'
import { docBookApi, type DocBook, type DocBookCreate, type DocBookUpdate } from '@/api'
import { uploadFile } from '@/api/services/common'
import { useMobileDetection } from '@/composables/useMobileDetection'
import TrashIcon from '@/components/tiptap-icons/trash-icon.vue'

const router = useRouter()
const { t } = useI18n()
const { isMobile } = useMobileDetection()

// 上传状态
const isUploading = ref(false)

// 封面上传处理
const handleCustomUpload = async (options: any) => {
  isUploading.value = true
  try {
    const res = await uploadFile({
      file: options.file,
      onProgress: (progressEvent) => {
        if (progressEvent.total > 0) {
          const percent = Math.round((progressEvent.loaded / progressEvent.total) * 100)
          options.onProgress({ percent })
        }
      }
    })

    if (res.code === 1) {
      formData.cover = res.data.full_url
      options.onSuccess(res.data)
      ElMessage.success(t('admin.docbook.message.upload_success'))
    } else {
      options.onError(new Error(res.msg || t('admin.docbook.message.upload_failed')))
      ElMessage.error(res.msg || t('admin.docbook.message.upload_failed'))
    }
  } catch (error) {
    options.onError(error)
    ElMessage.error(t('admin.docbook.message.upload_failed'))
  } finally {
    isUploading.value = false
  }
}

const beforeCoverUpload: UploadProps['beforeUpload'] = (rawFile) => {
  const isImage = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp'].includes(rawFile.type)
  const isLt2M = rawFile.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error(t('admin.docbook.message.image_format_error'))
    return false
  }
  if (!isLt2M) {
    ElMessage.error(t('admin.docbook.message.image_size_error'))
    return false
  }
  return true
}

// 状态
const loading = ref(false)
const docbooks = ref<DocBook[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const searchKeyword = ref('')

const showEditDialog = ref(false)
const editingDocBook = ref<DocBook | null>(null)
const submitting = ref(false)

const formRef = ref<FormInstance>()
const formData = reactive<DocBookCreate>({
  name: '',
  slug: '',
  description: '',
  cover: '',
  icon: '',
  is_public: true,
  show_sidebar: true,
  allow_comment: true,
  allow_search: true,
  theme: 'default',
  sort_order: 0
})

const formRules: FormRules = {
  name: [
    { required: true, message: t('admin.docbook.validation.name_required'), trigger: 'blur' },
    { max: 100, message: t('admin.docbook.validation.name_too_long'), trigger: 'blur' }
  ],
  slug: [
    { required: true, message: t('admin.docbook.validation.slug_required'), trigger: 'blur' },
    { max: 100, message: t('admin.docbook.validation.slug_too_long'), trigger: 'blur' },
    { pattern: /^[a-z0-9-]+$/, message: t('admin.docbook.validation.slug_invalid'), trigger: 'blur' }
  ]
}

// 格式化时间
const formatDateTime = (timestamp: number) => {
  const date = new Date(timestamp * 1000)
  return date.toLocaleString('zh-CN')
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const response = await docBookApi.list({
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
      keyword: searchKeyword.value
    })
    if (response.data) {
      docbooks.value = response.data
      // 获取总数
      const countRes = await docBookApi.count(searchKeyword.value)
      if (countRes.data) {
        total.value = countRes.data.total
      }
    }
  } catch (error) {
    ElMessage.error(t('admin.docbook.message.load_failed'))
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  loadData()
}

// 创建
const handleCreate = () => {
  editingDocBook.value = null
  Object.assign(formData, {
    name: '',
    slug: '',
    description: '',
    cover: '',
    icon: '',
    is_public: true,
    show_sidebar: true,
    allow_comment: true,
    allow_search: true,
    theme: 'default',
    sort_order: 0
  })
  showEditDialog.value = true
}

// 编辑
const handleEdit = (docbook: DocBook) => {
  editingDocBook.value = docbook
  Object.assign(formData, {
    name: docbook.name,
    slug: docbook.slug,
    description: docbook.description || '',
    cover: docbook.cover || '',
    icon: docbook.icon || '',
    is_public: docbook.is_public,
    show_sidebar: docbook.show_sidebar,
    allow_comment: docbook.allow_comment,
    allow_search: docbook.allow_search,
    theme: docbook.theme,
    sort_order: docbook.sort_order
  })
  showEditDialog.value = true
}

// 删除
const handleDelete = async (docbook: DocBook) => {
  try {
    await ElMessageBox.confirm(
      t('admin.docbook.confirm_delete.message', { name: docbook.name }),
      t('admin.docbook.confirm_delete.title'),
      {
        type: 'warning',
        confirmButtonText: t('admin.docbook.confirm_delete.confirm_btn'),
        cancelButtonText: t('admin.docbook.confirm_delete.cancel_btn')
      }
    )

    await docBookApi.delete(docbook.id)
    ElMessage.success(t('admin.docbook.message.delete_success'))
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(t('admin.docbook.message.delete_failed'))
    }
  }
}

// 查看文档
const handleViewDocs = (docbook: DocBook) => {
  router.push({
    name: 'admin-docs',
    params: { docbookId: docbook.id },
    state: { docbook } as any
  })
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
  } catch {
    return
  }

  submitting.value = true
  try {
    if (editingDocBook.value) {
      await docBookApi.update(editingDocBook.value.id, formData as DocBookUpdate)
      ElMessage.success(t('admin.docbook.message.update_success'))
    } else {
      await docBookApi.create(formData)
      ElMessage.success(t('admin.docbook.message.create_success'))
    }
    showEditDialog.value = false
    loadData()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || t('admin.docbook.message.operation_failed'))
  } finally {
    submitting.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.docbook-management {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
}

.page-header p {
  margin: 0;
  color: var(--el-text-color-secondary);
}

.action-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.search-input {
  flex: 1;
  max-width: 300px;
}

.docbooks-table {
  margin-bottom: 20px;
}

.cover-thumb {
  width: 50px;
  height: 50px;
  border-radius: 4px;
  overflow: hidden;
}

.cover-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  width: 50px;
  height: 50px;
  background: var(--el-color-primary);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
}

/* 封面上传组件样式 */
.cover-uploader {
  display: inline-block;
}

.cover-uploader :deep(.el-upload) {
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
}

.cover-uploader :deep(.el-upload:hover) {
  border-color: var(--el-color-primary);
}

.cover-preview {
  width: 200px;
  height: 120px;
  display: block;
  object-fit: cover;
}

.cover-uploader .cover-placeholder {
  width: 200px;
  height: 120px;
  background: var(--el-fill-color-light);
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.cover-uploader .cover-placeholder .el-icon {
  font-size: 28px;
  margin-bottom: 8px;
}

.cover-actions {
  margin-top: 8px;
}

.upload-loading {
  width: 200px;
  height: 120px;
  background: var(--el-fill-color-light);
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--el-text-color-secondary);
  gap: 8px;
}

.upload-loading .el-icon {
  font-size: 24px;
}

.upload-tip {
  font-size: 12px;
  color: var(--el-text-color-placeholder);
  margin-top: 4px;
}

.name-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.name-text {
  font-weight: 500;
}

.slug-text {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  font-family: monospace;
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  color: var(--el-text-color-placeholder);
  margin-bottom: 16px;
}

.empty-state h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
}

.empty-state p {
  margin: 0;
  color: var(--el-text-color-secondary);
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
}

/* 移动端样式 */
@media (max-width: 767px) {
  .docbook-management {
    padding: 12px;
  }

  .page-header h1 {
    font-size: 18px;
  }

  .page-header p {
    font-size: 12px;
  }

  .action-bar {
    flex-direction: column;
    gap: 8px;
  }

  .search-input {
    max-width: 100%;
  }

  .action-bar .el-button {
    width: 100%;
  }

  /* 卡片布局样式 */
  .docbooks-cards {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .docbook-card {
    margin: 0;
  }

  .docbook-card .card-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--el-border-color-lighter);
  }

  .card-cover,
  .card-cover-placeholder {
    width: 48px;
    height: 48px;
    flex-shrink: 0;
    border-radius: 4px;
    overflow: hidden;
  }

  .card-cover img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .card-cover-placeholder {
    background: var(--el-color-primary);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 18px;
  }

  .card-title {
    flex: 1;
    overflow: hidden;
  }

  .card-title .name-text {
    font-weight: 500;
    font-size: 14px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .card-title .slug-text {
    font-size: 11px;
    color: var(--el-text-color-secondary);
    font-family: monospace;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .card-body {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 12px;
  }

  .card-info-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 13px;
  }

  .card-info-row .label {
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }

  .card-info-row .time-text {
    font-size: 11px;
    color: var(--el-text-color-placeholder);
  }

  .card-footer {
    display: flex;
    gap: 8px;
    padding-top: 12px;
    border-top: 1px solid var(--el-border-color-lighter);
  }

  .card-footer .el-button {
    flex: 1;
  }

  /* 分页优化 */
  .pagination-wrapper {
    flex-wrap: wrap;
  }

  .pagination-wrapper :deep(.el-pagination) {
    flex-wrap: wrap;
    justify-content: center;
  }

  /* 空状态优化 */
  .empty-state {
    padding: 40px 16px;
  }

  .empty-icon {
    font-size: 48px;
  }

  .empty-state h3 {
    font-size: 14px;
  }

  .empty-state p {
    font-size: 12px;
  }
}
</style>
