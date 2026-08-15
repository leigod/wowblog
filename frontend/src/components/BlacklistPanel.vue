<template>
  <el-card class="blacklist-panel" shadow="never">
    <!-- 工具栏 -->
    <div class="toolbar">
      <el-select v-model="filterStatus" clearable style="width: 140px"
        :placeholder="t('admin.comment.blacklist.filter_status')" @change="handleSearch">
        <el-option :label="t('admin.comment.blacklist.status_active')" value="active" />
        <el-option :label="t('admin.comment.blacklist.status_inactive')" value="inactive" />
      </el-select>
      <el-input v-model="keyword" :placeholder="t('admin.comment.blacklist.search_placeholder')" clearable
        style="width: 200px" @keyup.enter="handleSearch" @clear="handleSearch" />
      <el-button type="primary" @click="handleSearch">{{ t('admin.comment.blacklist.search') }}</el-button>
    </div>

    <el-table v-loading="loading" :data="list" border>
      <el-table-column :label="t('admin.comment.blacklist.user')" min-width="140">
        <template #default="{ row }">{{ row.username || row.user_id }}</template>
      </el-table-column>
      <el-table-column :label="t('admin.comment.blacklist.reason_col')" min-width="180">
        <template #default="{ row }">{{ row.reason || '—' }}</template>
      </el-table-column>
      <el-table-column :label="t('admin.comment.blacklist.expire')" width="180">
        <template #default="{ row }">
          <template v-if="!row.expire_at">{{ t('admin.comment.blacklist.expire_forever') }}</template>
          <span v-else :class="{ expired: row.expire_at * 1000 < Date.now() }">
            {{ formatTime(row.expire_at) }}
          </span>
        </template>
      </el-table-column>
      <el-table-column :label="t('admin.comment.blacklist.status_col')" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'danger' : 'info'" size="small">
            {{ row.status === 'active' ? t('admin.comment.blacklist.status_active') : t('admin.comment.blacklist.status_inactive') }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('admin.comment.blacklist.created')" width="170">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column :label="t('admin.comment.blacklist.actions')" width="150" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" size="small" @click="openEditExpire(row)">
            {{ t('admin.comment.blacklist.edit_expire') }}
          </el-button>
          <el-popconfirm v-if="row.status === 'active'"
            :title="t('admin.comment.blacklist.unban_confirm')" @confirm="handleUnban(row)">
            <template #reference>
              <el-button link type="success" size="small">
                {{ t('admin.comment.blacklist.unban') }}
              </el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination class="pager" v-model:current-page="page" v-model:page-size="pageSize" :total="total"
      :page-sizes="[20, 50, 100]" layout="total, sizes, prev, pager, next"
      @current-change="load" @size-change="handleSizeChange" />

    <!-- 修改禁评时长 -->
    <el-dialog v-model="showEditExpire" :title="t('admin.comment.blacklist.edit_expire')" width="420px">
      <p class="edit-hint">
        {{ t('admin.comment.blacklist.user') }}: {{ editingRow?.username || editingRow?.user_id }}
      </p>
      <el-form label-width="80px">
        <el-form-item :label="t('admin.comment.ban.duration')">
          <el-select v-model="editDays" style="width: 100%">
            <el-option :label="t('admin.comment.ban.forever')" :value="0" />
            <el-option :label="t('admin.comment.ban.days7')" :value="7" />
            <el-option :label="t('admin.comment.ban.days30')" :value="30" />
            <el-option :label="t('admin.comment.ban.days90')" :value="90" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditExpire = false">{{ t('admin.comment.words.cancel') }}</el-button>
        <el-button type="primary" :loading="saving" @click="handleSaveExpire">
          {{ t('admin.comment.words.confirm') }}
        </el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import {
  getBlacklist,
  updateBlacklist,
  type BlacklistItem
} from '@/api/services/commentAdmin'

const { t } = useI18n()

const loading = ref(false)
const saving = ref(false)
const list = ref<BlacklistItem[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const filterStatus = ref('active')
const keyword = ref('')

const formatTime = (ts?: number) => {
  if (!ts) return '—'
  return new Date(ts * 1000).toLocaleString()
}

const load = async () => {
  loading.value = true
  try {
    const res = await getBlacklist({
      page: page.value,
      page_size: pageSize.value,
      type: 'comment',
      status: filterStatus.value || undefined,
      keyword: keyword.value.trim() || undefined
    })
    if (res && res.code === 1) {
      list.value = res.data ?? []
      total.value = res.total ?? 0
    }
  } catch {
    // 由拦截器提示
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

// ===== 解除禁评（置为 inactive，保留记录可追溯）=====
const handleUnban = async (row: BlacklistItem) => {
  try {
    const res = await updateBlacklist(row.id, { status: 'inactive' })
    if (res && res.code === 1) {
      ElMessage.success(t('admin.comment.blacklist.unban_success'))
      await load()
    } else {
      ElMessage.error(res?.msg || t('admin.comment.blacklist.unban_failed'))
    }
  } catch {
    ElMessage.error(t('admin.comment.blacklist.unban_failed'))
  }
}

// ===== 修改禁评时长 =====
const showEditExpire = ref(false)
const editingRow = ref<BlacklistItem | null>(null)
const editDays = ref(0)

const openEditExpire = (row: BlacklistItem) => {
  editingRow.value = row
  editDays.value = 0
  showEditExpire.value = true
}

const handleSaveExpire = async () => {
  if (!editingRow.value) return
  saving.value = true
  try {
    const expire_at = editDays.value > 0
      ? Math.floor(Date.now() / 1000) + editDays.value * 86400
      : 0 // 约定 0 = 改为永久（后端置 NULL）
    const res = await updateBlacklist(editingRow.value.id, { expire_at })
    if (res && res.code === 1) {
      ElMessage.success(t('admin.comment.blacklist.update_success'))
      showEditExpire.value = false
      await load()
    } else {
      ElMessage.error(res?.msg || t('admin.comment.blacklist.update_failed'))
    }
  } catch {
    ElMessage.error(t('admin.comment.blacklist.update_failed'))
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.blacklist-panel {
  margin-top: 16px;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 14px;
}

.pager {
  margin-top: 14px;
  justify-content: flex-end;
}

.expired {
  color: var(--el-color-info);
  text-decoration: line-through;
}

.edit-hint {
  margin: 0 0 12px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}
</style>
