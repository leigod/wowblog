<template>
  <div class="creator-page">
    <div class="page-header">
      <div>
        <h1>{{ t('creator.categories.title') }}</h1>
        <p>{{ t('creator.categories.title_info') }}</p>
      </div>
      <el-button type="primary" @click="openCreateDialog">
        <el-icon><Plus /></el-icon>
        {{ t('creator.categories.add') }}
      </el-button>
    </div>

    <el-card class="list-card" v-loading="loading">
      <el-empty
        v-if="!loading && categories.length === 0"
        :description="t('creator.categories.empty_description')"
      >
        <template #image>
          <el-icon :size="56" color="var(--el-text-color-placeholder)"><PriceTag /></el-icon>
        </template>
        <p class="empty-title">{{ t('creator.categories.empty') }}</p>
      </el-empty>

      <div v-else ref="listContainer" class="category-list">
        <div v-for="item in categories" :key="item.id" class="list-row">
          <div class="drag-handle" :title="t('creator.categories.title')">
            <IconifyIcon icon="material-symbols:drag-indicator" />
          </div>
          <div class="row-main">
            <span class="row-name">{{ item.name }}</span>
            <span class="row-slug">/{{ item.slug }}</span>
          </div>
          <div class="row-time">{{ formatTime(item.createtime) }}</div>
          <div class="row-actions">
            <el-button text circle @click="openEditDialog(item)">
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-button text circle type="danger" @click="handleDelete(item)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 新建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingId ? t('creator.categories.edit_title') : t('creator.categories.add')"
      width="460px"
      @closed="resetForm"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item :label="t('creator.categories.name')" prop="name">
          <el-input
            v-model="form.name"
            :placeholder="t('creator.categories.name_placeholder')"
            maxlength="100"
          />
        </el-form-item>
        <el-form-item label="Slug" prop="slug">
          <el-input v-model="form.slug" :placeholder="t('creator.categories.slug_placeholder')" maxlength="50">
            <template #prepend>/</template>
          </el-input>
          <div class="form-tip">{{ t('creator.categories.slug_tip') }}</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">
          {{ t('admin.general.btn.cancel') }}
        </el-button>
        <el-button type="primary" :loading="saving" @click="handleSubmit">
          {{ editingId ? t('admin.general.btn.update') : t('admin.general.btn.create') }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Plus, Edit, Delete, PriceTag } from '@element-plus/icons-vue'
import IconifyIcon from '@/components/IconIfy.vue'
import {
  getUserCategories,
  createUserCategory,
  updateUserCategory,
  deleteUserCategory,
  sortUserCategories,
  type UserBlogCategory
} from '@/api/services/creator'
import { useSortableList } from '@/composables/useSortableList'

const { t } = useI18n()

const loading = ref(false)
const saving = ref(false)
const categories = ref<UserBlogCategory[]>([])
const listContainer = ref<HTMLElement | null>(null)
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const formRef = ref<FormInstance>()

const form = reactive({
  name: '',
  slug: ''
})

const rules = computed(
  (): FormRules => ({
    name: [
      { required: true, message: t('creator.categories.name_required'), trigger: 'blur' },
      { max: 100, message: t('creator.categories.name_length'), trigger: 'blur' }
    ],
    slug: [
      { pattern: /^[a-z0-9_-]*$/, message: t('creator.categories.slug_invalid'), trigger: 'blur' },
      { max: 50, message: t('creator.categories.slug_length'), trigger: 'blur' }
    ]
  })
)

const loadList = async () => {
  loading.value = true
  try {
    const res = await getUserCategories()
    if (res.code === 1 && res.data) {
      categories.value = res.data
    }
  } catch (error) {
    console.error('load categories failed:', error)
  } finally {
    loading.value = false
    await nextTick()
    initSortable()
  }
}

const handleReorder = async (ids: number[]) => {
  try {
    const res = await sortUserCategories(ids)
    if (res.code === 1) {
      ElMessage.success(t('creator.categories.sort_success'))
    } else {
      ElMessage.error(t('creator.categories.sort_error'))
      loadList()
    }
  } catch {
    ElMessage.error(t('creator.categories.sort_error'))
    loadList()
  }
}

const { init: initSortable } = useSortableList(listContainer, categories, handleReorder)

const openCreateDialog = () => {
  editingId.value = null
  dialogVisible.value = true
}

const openEditDialog = (item: UserBlogCategory) => {
  editingId.value = item.id
  form.name = item.name
  form.slug = item.slug
  dialogVisible.value = true
}

const resetForm = () => {
  editingId.value = null
  form.name = ''
  form.slug = ''
  formRef.value?.resetFields()
}

const handleSubmit = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  saving.value = true
  try {
    const res = editingId.value
      ? await updateUserCategory(editingId.value, { name: form.name, slug: form.slug })
      : await createUserCategory({ name: form.name, slug: form.slug })
    if (res.code === 1) {
      ElMessage.success(
        editingId.value ? t('creator.categories.update_success') : t('creator.categories.create_success')
      )
      dialogVisible.value = false
      loadList()
    } else {
      ElMessage.error(res.msg || t('creator.categories.create_error'))
    }
  } catch (error) {
    console.error('save category failed:', error)
    ElMessage.error(t('creator.categories.create_error'))
  } finally {
    saving.value = false
  }
}

const handleDelete = (item: UserBlogCategory) => {
  ElMessageBox.confirm(t('creator.categories.delete_confirm'), t('creator.categories.title'), {
    confirmButtonText: t('admin.general.btn.delete'),
    cancelButtonText: t('admin.general.btn.cancel'),
    type: 'warning'
  })
    .then(async () => {
      try {
        const res = await deleteUserCategory(item.id)
        if (res.code === 1) {
          ElMessage.success(t('creator.categories.delete_success'))
          loadList()
        } else {
          ElMessage.error(res.msg || t('creator.categories.delete_error'))
        }
      } catch {
        ElMessage.error(t('creator.categories.delete_error'))
      }
    })
    .catch(() => {})
}

const formatTime = (timestamp: number) => {
  if (!timestamp) return '-'
  return new Date(timestamp * 1000).toLocaleDateString()
}

onMounted(loadList)
</script>

<style scoped>
/* 注：本样式块曾整体遗漏（模板靠类名引用但样式缺失），
   导致列表行退化为纵向堆叠——与 CreatorSeriesView 保持同款行式布局 */
.creator-page {
  padding: 20px;
  max-width: 900px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
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

.list-card {
  border-radius: 8px;
}

.category-list {
  display: flex;
  flex-direction: column;
}

.list-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 8px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.list-row:last-child {
  border-bottom: none;
}

.drag-handle {
  cursor: move;
  color: var(--el-text-color-placeholder);
  font-size: 18px;
  display: flex;
  flex-shrink: 0;
}

.row-main {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: baseline;
  gap: 8px;
  overflow: hidden;
}

.row-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.row-slug {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.row-time {
  flex-shrink: 0;
  font-size: 12px;
  color: var(--el-text-color-placeholder);
}

.row-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.empty-title {
  margin: 12px 0 0;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.form-tip {
  font-size: 12px;
  color: var(--el-text-color-placeholder);
  line-height: 1.4;
  margin-top: 2px;
}
</style>
