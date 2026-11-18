<template>
  <div class="creator-page">
    <div class="page-header">
      <div>
        <h1>{{ t('creator.series.title') }}</h1>
        <p>{{ t('creator.series.title_info') }}</p>
      </div>
      <el-button type="primary" @click="openCreateDialog">
        <el-icon><Plus /></el-icon>
        {{ t('creator.series.add') }}
      </el-button>
    </div>

    <el-card class="list-card" v-loading="loading">
      <el-empty v-if="!loading && seriesList.length === 0" :description="t('creator.series.empty_description')">
        <template #image>
          <el-icon :size="56" color="var(--el-text-color-placeholder)"><Collection /></el-icon>
        </template>
        <p class="empty-title">{{ t('creator.series.empty') }}</p>
      </el-empty>

      <div v-else ref="listContainer" class="series-list">
        <div v-for="item in seriesList" :key="item.id" class="list-row">
          <div class="drag-handle">
            <IconifyIcon icon="material-symbols:drag-indicator" />
          </div>
          <div class="row-main">
            <span class="row-name">{{ item.name }}</span>
            <span v-if="item.slug" class="row-slug">/series/{{ item.slug }}</span>
            <span v-if="item.description" class="row-desc">{{ item.description }}</span>
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
      :title="editingId ? t('creator.series.edit_title') : t('creator.series.add')"
      width="460px"
      @closed="resetForm"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item :label="t('creator.series.name')" prop="name">
          <el-input
            v-model="form.name"
            :placeholder="t('creator.series.name_placeholder')"
            maxlength="100"
          />
        </el-form-item>
        <el-form-item :label="t('creator.series.slug')" prop="slug">
          <el-input
            v-model="form.slug"
            :placeholder="t('creator.series.slug_placeholder')"
            maxlength="50"
          />
          <div class="form-tip">{{ t('creator.series.slug_tip') }}</div>
        </el-form-item>
        <el-form-item :label="t('creator.series.description')" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            :placeholder="t('creator.series.description_placeholder')"
            maxlength="300"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ t('admin.general.btn.cancel') }}</el-button>
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
import { Plus, Edit, Delete, Collection } from '@element-plus/icons-vue'
import IconifyIcon from '@/components/IconIfy.vue'
import {
  getUserSeriesList,
  createUserSeries,
  updateUserSeries,
  deleteUserSeries,
  sortUserSeries,
  type UserBlogSeries
} from '@/api/services/creator'
import { useSortableList } from '@/composables/useSortableList'

const { t } = useI18n()

const loading = ref(false)
const saving = ref(false)
const seriesList = ref<UserBlogSeries[]>([])
const listContainer = ref<HTMLElement | null>(null)
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const formRef = ref<FormInstance>()

const form = reactive({
  name: '',
  slug: '',
  description: ''
})

const rules = computed(
  (): FormRules => ({
    name: [
      { required: true, message: t('creator.series.name_required'), trigger: 'blur' },
      { max: 100, message: t('creator.series.name_length'), trigger: 'blur' }
    ],
    slug: [
      { pattern: /^[a-z0-9_-]*$/, message: t('creator.series.slug_invalid'), trigger: 'blur' },
      { max: 50, message: t('creator.series.slug_length'), trigger: 'blur' }
    ],
    description: [{ max: 300, message: t('creator.series.description_length'), trigger: 'blur' }]
  })
)

const loadList = async () => {
  loading.value = true
  try {
    const res = await getUserSeriesList()
    if (res.code === 1 && res.data) {
      seriesList.value = res.data
    }
  } catch (error) {
    console.error('load series failed:', error)
  } finally {
    loading.value = false
    await nextTick()
    initSortable()
  }
}

const handleReorder = async (ids: number[]) => {
  try {
    const res = await sortUserSeries(ids)
    if (res.code === 1) {
      ElMessage.success(t('creator.series.sort_success'))
    } else {
      ElMessage.error(t('creator.series.sort_error'))
      loadList()
    }
  } catch {
    ElMessage.error(t('creator.series.sort_error'))
    loadList()
  }
}

const { init: initSortable } = useSortableList(listContainer, seriesList, handleReorder)

const openCreateDialog = () => {
  editingId.value = null
  dialogVisible.value = true
}

const openEditDialog = (item: UserBlogSeries) => {
  editingId.value = item.id
  form.name = item.name
  form.slug = item.slug || ''
  form.description = item.description || ''
  dialogVisible.value = true
}

const resetForm = () => {
  editingId.value = null
  form.name = ''
  form.slug = ''
  form.description = ''
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
      ? await updateUserSeries(editingId.value, { name: form.name, slug: form.slug, description: form.description })
      : await createUserSeries({ name: form.name, slug: form.slug, description: form.description })
    if (res.code === 1) {
      ElMessage.success(
        editingId.value ? t('creator.series.update_success') : t('creator.series.create_success')
      )
      dialogVisible.value = false
      loadList()
    } else {
      ElMessage.error(res.msg || t('creator.series.create_error'))
    }
  } catch (error) {
    console.error('save series failed:', error)
    ElMessage.error(t('creator.series.create_error'))
  } finally {
    saving.value = false
  }
}

const handleDelete = (item: UserBlogSeries) => {
  ElMessageBox.confirm(t('creator.series.delete_confirm'), t('creator.series.title'), {
    confirmButtonText: t('admin.general.btn.delete'),
    cancelButtonText: t('admin.general.btn.cancel'),
    type: 'warning'
  })
    .then(async () => {
      try {
        const res = await deleteUserSeries(item.id)
        if (res.code === 1) {
          ElMessage.success(t('creator.series.delete_success'))
          loadList()
        } else {
          ElMessage.error(res.msg || t('creator.series.delete_error'))
        }
      } catch {
        ElMessage.error(t('creator.series.delete_error'))
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

.series-list {
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
}

.row-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.row-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.row-desc {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.row-slug {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.form-tip {
  font-size: 12px;
  color: var(--el-text-color-placeholder);
  line-height: 1.4;
  margin-top: 2px;
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
</style>
