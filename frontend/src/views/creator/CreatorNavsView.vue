<template>
  <div class="creator-page">
    <div class="page-header">
      <div>
        <h1>{{ t('creator.navs.title') }}</h1>
        <p>{{ t('creator.navs.title_info') }}</p>
      </div>
      <el-button type="primary" @click="openCreateDialog">
        <el-icon><Plus /></el-icon>
        {{ t('creator.navs.add') }}
      </el-button>
    </div>

    <el-card class="list-card" v-loading="loading">
      <el-empty v-if="!loading && navs.length === 0" :description="t('creator.navs.empty_description')">
        <template #image>
          <el-icon :size="56" color="var(--el-text-color-placeholder)"><Guide /></el-icon>
        </template>
        <p class="empty-title">{{ t('creator.navs.empty') }}</p>
      </el-empty>

      <div v-else ref="listContainer" class="nav-list">
        <div v-for="item in navs" :key="item.id" class="list-row">
          <div class="drag-handle">
            <IconifyIcon icon="material-symbols:drag-indicator" />
          </div>
          <div class="row-main">
            <span class="row-name">
              {{ item.label }}
              <el-tag v-if="item.status === 0" size="small" type="info">
                {{ t('creator.navs.status_hidden') }}
              </el-tag>
            </span>
            <span class="row-slug">
              {{ typeLabel(item.type) }} · {{ displayValue(item) }}
            </span>
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
      :title="editingId ? t('creator.navs.edit_title') : t('creator.navs.add')"
      width="520px"
      @closed="resetForm"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item :label="t('creator.navs.label')" prop="label">
          <el-input
            v-model="form.label"
            :placeholder="t('creator.navs.label_placeholder')"
            maxlength="50"
          />
        </el-form-item>
        <el-form-item :label="t('creator.navs.type')" prop="type">
          <el-radio-group v-model="form.type">
            <el-radio-button value="link">{{ t('creator.navs.type_link') }}</el-radio-button>
            <el-radio-button value="category">{{ t('creator.navs.type_category') }}</el-radio-button>
            <el-radio-button value="series">{{ t('creator.navs.type_series') }}</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="form.type === 'link'" :label="t('creator.navs.value_link')" prop="value">
          <el-input
            v-model="form.value"
            :placeholder="t('creator.navs.value_link_placeholder')"
          />
        </el-form-item>
        <el-form-item v-else-if="form.type === 'category'" :label="t('creator.navs.value_category')" prop="value">
          <el-select v-model="form.value" :placeholder="t('creator.navs.value_category_placeholder')" style="width: 100%">
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="cat.name"
              :value="String(cat.id)"
            />
          </el-select>
          <p v-if="!loadingDeps && categories.length === 0" class="dep-hint">
            {{ t('creator.navs.need_category') }}
          </p>
        </el-form-item>
        <el-form-item v-else :label="t('creator.navs.value_series')" prop="value">
          <el-select v-model="form.value" :placeholder="t('creator.navs.value_series_placeholder')" style="width: 100%">
            <el-option
              v-for="s in seriesList"
              :key="s.id"
              :label="s.name"
              :value="String(s.id)"
            />
          </el-select>
          <p v-if="!loadingDeps && seriesList.length === 0" class="dep-hint">
            {{ t('creator.navs.need_series') }}
          </p>
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
import { Plus, Edit, Delete, Guide } from '@element-plus/icons-vue'
import IconifyIcon from '@/components/IconIfy.vue'
import {
  getUserNavs,
  createUserNav,
  updateUserNav,
  deleteUserNav,
  sortUserNavs,
  getUserCategories,
  getUserSeriesList,
  type UserBlogNav
} from '@/api/services/creator'
import { useSortableList } from '@/composables/useSortableList'

const { t } = useI18n()

const loading = ref(false)
const saving = ref(false)
const loadingDeps = ref(false)
const navs = ref<UserBlogNav[]>([])
const categories = ref<{ id: number; name: string }[]>([])
const seriesList = ref<{ id: number; name: string }[]>([])
const listContainer = ref<HTMLElement | null>(null)
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const formRef = ref<FormInstance>()

const form = reactive<{
  label: string
  type: 'link' | 'category' | 'series'
  value: string
}>({
  label: '',
  type: 'link',
  value: ''
})

const rules = computed(
  (): FormRules => ({
    label: [
      { required: true, message: t('creator.navs.label_required'), trigger: 'blur' },
      { max: 50, message: t('creator.navs.label_length'), trigger: 'blur' }
    ],
    value: [
      {
        required: true,
        validator: (_rule, value: string, callback) => {
          if (!value) {
            callback(new Error(t('creator.navs.value_required')))
            return
          }
          if (form.type === 'link' && !/^https?:\/\//.test(value)) {
            callback(new Error(t('creator.navs.url_invalid')))
            return
          }
          callback()
        },
        trigger: ['blur', 'change']
      }
    ]
  })
)

const typeLabel = (type: string) => {
  const map: Record<string, string> = {
    link: t('creator.navs.type_link'),
    category: t('creator.navs.type_category'),
    series: t('creator.navs.type_series')
  }
  return map[type] || type
}

const displayValue = (item: UserBlogNav) => {
  if (item.type === 'category') {
    return categories.value.find((c) => String(c.id) === item.value)?.name || item.value
  }
  if (item.type === 'series') {
    return seriesList.value.find((s) => String(s.id) === item.value)?.name || item.value
  }
  return item.value
}

const loadDeps = async () => {
  loadingDeps.value = true
  try {
    const [catRes, seriesRes] = await Promise.all([getUserCategories(), getUserSeriesList()])
    if (catRes.code === 1 && catRes.data) categories.value = catRes.data
    if (seriesRes.code === 1 && seriesRes.data) seriesList.value = seriesRes.data
  } finally {
    loadingDeps.value = false
  }
}

const loadList = async () => {
  loading.value = true
  try {
    const res = await getUserNavs()
    if (res.code === 1 && res.data) {
      navs.value = res.data
    }
  } catch (error) {
    console.error('load navs failed:', error)
  } finally {
    loading.value = false
    await nextTick()
    initSortable()
  }
}

const handleReorder = async (ids: number[]) => {
  try {
    const res = await sortUserNavs(ids)
    if (res.code === 1) {
      ElMessage.success(t('creator.navs.sort_success'))
    } else {
      ElMessage.error(t('creator.navs.sort_error'))
      loadList()
    }
  } catch {
    ElMessage.error(t('creator.navs.sort_error'))
    loadList()
  }
}

const { init: initSortable } = useSortableList(listContainer, navs, handleReorder)

const openCreateDialog = () => {
  editingId.value = null
  loadDeps()
  dialogVisible.value = true
}

const openEditDialog = (item: UserBlogNav) => {
  editingId.value = item.id
  form.label = item.label
  form.type = item.type
  form.value = item.value
  loadDeps()
  dialogVisible.value = true
}

const resetForm = () => {
  editingId.value = null
  form.label = ''
  form.type = 'link'
  form.value = ''
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
    const payload = { label: form.label, type: form.type, value: form.value }
    const res = editingId.value
      ? await updateUserNav(editingId.value, payload)
      : await createUserNav(payload)
    if (res.code === 1) {
      ElMessage.success(editingId.value ? t('creator.navs.update_success') : t('creator.navs.create_success'))
      dialogVisible.value = false
      loadList()
    } else {
      ElMessage.error(res.msg || t('creator.navs.create_error'))
    }
  } catch (error) {
    console.error('save nav failed:', error)
    ElMessage.error(t('creator.navs.create_error'))
  } finally {
    saving.value = false
  }
}

const handleDelete = (item: UserBlogNav) => {
  ElMessageBox.confirm(t('creator.navs.delete_confirm'), t('creator.navs.title'), {
    confirmButtonText: t('admin.general.btn.delete'),
    cancelButtonText: t('admin.general.btn.cancel'),
    type: 'warning'
  })
    .then(async () => {
      try {
        const res = await deleteUserNav(item.id)
        if (res.code === 1) {
          ElMessage.success(t('creator.navs.delete_success'))
          loadList()
        } else {
          ElMessage.error(res.msg || t('creator.navs.delete_error'))
        }
      } catch {
        ElMessage.error(t('creator.navs.delete_error'))
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

.nav-list {
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
  display: flex;
  align-items: center;
  gap: 8px;
}

.row-slug {
  font-size: 12px;
  color: var(--el-text-color-secondary);
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

.dep-hint {
  margin: 4px 0 0;
  font-size: 12px;
  color: var(--el-color-warning);
}

.empty-title {
  margin: 12px 0 0;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}
</style>
