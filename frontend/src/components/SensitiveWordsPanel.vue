<template>
  <el-card class="words-panel" shadow="never">
    <!-- 工具栏 -->
    <div class="toolbar">
      <el-input v-model="keyword" :placeholder="t('admin.comment.words.search_placeholder')" clearable
        style="width: 200px" @keyup.enter="handleSearch" @clear="handleSearch" />
      <el-select v-model="filterType" clearable style="width: 140px"
        :placeholder="t('admin.comment.words.filter_type')">
        <el-option v-for="opt in TYPE_OPTIONS" :key="opt.value" :label="t(opt.label)" :value="opt.value" />
      </el-select>
      <el-select v-model="filterStatus" clearable style="width: 130px"
        :placeholder="t('admin.comment.words.filter_status')">
        <el-option :label="t('admin.comment.words.status_active')" value="active" />
        <el-option :label="t('admin.comment.words.status_inactive')" value="inactive" />
      </el-select>
      <el-button type="primary" @click="handleSearch">{{ t('admin.comment.words.search') }}</el-button>
      <div class="spacer" />
      <el-button @click="openImport">{{ t('admin.comment.words.import') }}</el-button>
      <el-button :loading="exporting" @click="handleExport">{{ t('admin.comment.words.export') }}</el-button>
      <el-button type="primary" @click="openCreate">{{ t('admin.comment.words.create') }}</el-button>
    </div>

    <!-- 词库表格 -->
    <el-table v-loading="loading" :data="list" border>
      <el-table-column prop="word" :label="t('admin.comment.words.word')" min-width="140" show-overflow-tooltip />
      <el-table-column :label="t('admin.comment.words.type')" width="110">
        <template #default="{ row }">
          <el-tag :type="typeTag(row.type)" size="small">{{ typeLabel(row.type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('admin.comment.words.replacement')" min-width="120">
        <template #default="{ row }">{{ row.replacement || '—' }}</template>
      </el-table-column>
      <el-table-column :label="t('admin.comment.words.category')" width="100">
        <template #default="{ row }">{{ row.category || '—' }}</template>
      </el-table-column>
      <el-table-column :label="t('admin.comment.words.status_col')" width="90">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
            {{ row.status === 'active' ? t('admin.comment.words.status_active') : t('admin.comment.words.status_inactive') }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('admin.comment.words.created_at')" width="170">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column :label="t('admin.comment.words.actions')" width="140" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" size="small" @click="openEdit(row)">
            {{ t('admin.comment.words.edit') }}
          </el-button>
          <el-popconfirm :title="t('admin.comment.words.delete_confirm')" @confirm="handleDelete(row)">
            <template #reference>
              <el-button link type="danger" size="small">{{ t('admin.comment.words.delete') }}</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination class="pager" v-model:current-page="page" v-model:page-size="pageSize" :total="total"
      :page-sizes="[20, 50, 100]" layout="total, sizes, prev, pager, next" @current-change="load"
      @size-change="handleSizeChange" />

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="showEdit" destroy-on-close
      :title="editingId ? t('admin.comment.words.edit') : t('admin.comment.words.create')" width="480px">
      <el-form :model="editForm" label-width="90px">
        <el-form-item :label="t('admin.comment.words.word')">
          <el-input v-model="editForm.word" maxlength="100" show-word-limit />
        </el-form-item>
        <el-form-item :label="t('admin.comment.words.type')">
          <el-select v-model="editForm.type" style="width: 100%">
            <el-option v-for="opt in TYPE_OPTIONS" :key="opt.value" :label="t(opt.label)" :value="opt.value" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="editForm.type === 'replace'" :label="t('admin.comment.words.replacement')">
          <el-input v-model="editForm.replacement" maxlength="100"
            :placeholder="t('admin.comment.words.replacement_placeholder')" />
        </el-form-item>
        <el-form-item :label="t('admin.comment.words.category')">
          <el-input v-model="editForm.category" maxlength="50"
            :placeholder="t('admin.comment.words.category_placeholder')" />
        </el-form-item>
        <el-form-item v-if="editingId" :label="t('admin.comment.words.status_col')">
          <el-switch v-model="editForm.statusActive" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEdit = false">{{ t('admin.comment.words.cancel') }}</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">{{ t('admin.comment.words.confirm') }}</el-button>
      </template>
    </el-dialog>

    <!-- 批量导入对话框 -->
    <el-dialog v-model="showImport" :title="t('admin.comment.words.import')" width="620px">
      <p class="import-hint">{{ t('admin.comment.words.import_hint') }}</p>
      <pre class="import-example">违禁词
违禁词=>和谐词
需审核词@@review
# 注释行</pre>
      <el-form label-width="90px">
        <el-form-item :label="t('admin.comment.words.category')">
          <el-input v-model="importCategory" maxlength="50" style="width: 200px"
            :placeholder="t('admin.comment.words.category_placeholder')" />
        </el-form-item>
        <el-form-item :label="t('admin.comment.words.import_file')">
          <input type="file" accept=".txt" @change="handleFileChange" />
        </el-form-item>
        <el-form-item :label="t('admin.comment.words.import_content')">
          <el-input v-model="importContent" type="textarea" :rows="10" monospace
            :placeholder="t('admin.comment.words.import_content_placeholder')" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showImport = false">{{ t('admin.comment.words.cancel') }}</el-button>
        <el-button type="primary" :loading="importing" :disabled="!importContent.trim()"
          @click="handleImport">{{ t('admin.comment.words.import_start') }}</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import {
  getSensitiveWords,
  createSensitiveWord,
  updateSensitiveWord,
  deleteSensitiveWord,
  importSensitiveWords,
  exportSensitiveWords,
  type SensitiveWord
} from '@/api/services/commentAdmin'

const { t } = useI18n()

const loading = ref(false)
const saving = ref(false)
const exporting = ref(false)
const importing = ref(false)

const list = ref<SensitiveWord[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const keyword = ref('')
const filterType = ref('')
const filterStatus = ref('')

/** 三档动作元数据 */
const TYPE_OPTIONS = [
  { value: 'banned', label: 'admin.comment.words.type_banned' },
  { value: 'review', label: 'admin.comment.words.type_review' },
  { value: 'replace', label: 'admin.comment.words.type_replace' }
] as const

const typeLabel = (type: string) => {
  const opt = TYPE_OPTIONS.find(o => o.value === type)
  return opt ? t(opt.label) : type
}
const typeTag = (type: string): 'danger' | 'warning' | 'primary' => {
  if (type === 'banned') return 'danger'
  if (type === 'review') return 'warning'
  return 'primary'
}

const formatTime = (ts?: number) => {
  if (!ts) return '—'
  return new Date(ts * 1000).toLocaleString()
}

const load = async () => {
  loading.value = true
  try {
    const res = await getSensitiveWords({
      page: page.value,
      page_size: pageSize.value,
      keyword: keyword.value || undefined,
      type: filterType.value || undefined,
      status: filterStatus.value || undefined
    })
    if (res && res.code === 1) {
      list.value = res.data ?? []
      total.value = res.total ?? 0
    }
  } catch {
    // 列表加载失败静默，由拦截器提示
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  page.value = 1
  load()
}

const handleSizeChange = () => {
  page.value = 1
  load()
}

// ===== 新增 / 编辑 =====
const showEdit = ref(false)
const editingId = ref<number | null>(null)
const editForm = reactive({
  word: '',
  type: 'banned' as 'banned' | 'review' | 'replace',
  replacement: '',
  category: '',
  statusActive: true
})

const openCreate = () => {
  editingId.value = null
  editForm.word = ''
  editForm.type = 'banned'
  editForm.replacement = ''
  editForm.category = ''
  editForm.statusActive = true
  showEdit.value = true
}

const openEdit = (row: SensitiveWord) => {
  editingId.value = row.id
  editForm.word = row.word
  editForm.type = row.type
  editForm.replacement = row.replacement ?? ''
  editForm.category = row.category ?? ''
  editForm.statusActive = row.status === 'active'
  showEdit.value = true
}

const handleSave = async () => {
  const word = editForm.word.trim()
  if (!word) {
    ElMessage.warning(t('admin.comment.words.word_required'))
    return
  }
  saving.value = true
  try {
    const payload: Record<string, unknown> = {
      word,
      type: editForm.type,
      category: editForm.category.trim() || undefined
    }
    if (editForm.type === 'replace' && editForm.replacement.trim()) {
      payload.replacement = editForm.replacement.trim()
    }
    if (editingId.value) {
      payload.status = editForm.statusActive ? 'active' : 'inactive'
    }
    const res = editingId.value
      ? await updateSensitiveWord(editingId.value, payload as Partial<SensitiveWord>)
      : await createSensitiveWord(payload as { word: string; type?: string })
    if (res && res.code === 1) {
      ElMessage.success(t('admin.comment.words.save_success'))
      showEdit.value = false
      await load()
    } else {
      ElMessage.error(res?.msg || t('admin.comment.words.save_failed'))
    }
  } catch (error: any) {
    // 409 = 词已存在，后端 detail 在 error.response.data.detail
    const detail = error?.response?.data?.detail
    ElMessage.error(detail || error?.response?.data?.msg || t('admin.comment.words.save_failed'))
  } finally {
    saving.value = false
  }
}

const handleDelete = async (row: SensitiveWord) => {
  try {
    const res = await deleteSensitiveWord(row.id)
    if (res && res.code === 1) {
      ElMessage.success(t('admin.comment.words.delete_success'))
      await load()
    } else {
      ElMessage.error(res?.msg || t('admin.comment.words.delete_failed'))
    }
  } catch {
    ElMessage.error(t('admin.comment.words.delete_failed'))
  }
}

// ===== 批量导入 / 导出 =====
const showImport = ref(false)
const importContent = ref('')
const importCategory = ref('')

const openImport = () => {
  importContent.value = ''
  importCategory.value = ''
  showImport.value = true
}

/** 选择 txt 文件后读入文本框（也可直接粘贴） */
const handleFileChange = (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => {
    importContent.value = String(reader.result ?? '')
  }
  reader.readAsText(file, 'utf-8')
  // 允许重复选择同一文件
  input.value = ''
}

const handleImport = async () => {
  importing.value = true
  try {
    const res = await importSensitiveWords(importContent.value, importCategory.value.trim() || undefined)
    if (res && res.code === 1) {
      ElMessage.success(
        t('admin.comment.words.import_done', {
          added: res.data?.added ?? 0,
          skipped: res.data?.skipped ?? 0
        })
      )
      showImport.value = false
      page.value = 1
      await load()
    } else {
      ElMessage.error(res?.msg || t('admin.comment.words.import_failed'))
    }
  } catch {
    ElMessage.error(t('admin.comment.words.import_failed'))
  } finally {
    importing.value = false
  }
}

const handleExport = async () => {
  exporting.value = true
  try {
    const text = await exportSensitiveWords()
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'sensitive-words.txt'
    a.click()
    URL.revokeObjectURL(url)
  } catch {
    ElMessage.error(t('admin.comment.words.export_failed'))
  } finally {
    exporting.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.words-panel {
  margin-top: 16px;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 14px;
}

.spacer {
  flex: 1;
}

.pager {
  margin-top: 14px;
  justify-content: flex-end;
}

.import-hint {
  margin: 0 0 8px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.import-example {
  margin: 0 0 14px;
  padding: 10px;
  background: var(--el-fill-color-light);
  border-radius: 6px;
  font-size: 12px;
  color: var(--el-text-color-regular);
}
</style>
