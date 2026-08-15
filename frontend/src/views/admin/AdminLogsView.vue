<template>
  <div class="admin-logs">
    <div class="page-header">
      <h1>{{ $t('admin.logs.title') }}</h1>
      <p>{{ $t('admin.logs.subtitle') }}</p>
    </div>

    <!-- 筛选 -->
    <el-card shadow="never" class="filter-card">
      <div class="toolbar">
        <el-input v-model="filterUsername" :placeholder="$t('admin.logs.filter_username')" clearable
          style="width: 180px" @keyup.enter="handleSearch" @clear="handleSearch" />
        <el-input v-model="filterAction" :placeholder="$t('admin.logs.filter_action')" clearable
          style="width: 180px" @keyup.enter="handleSearch" @clear="handleSearch" />
        <el-date-picker v-model="dateRange" type="datetimerange"
          :start-placeholder="$t('admin.logs.start_time')" :end-placeholder="$t('admin.logs.end_time')"
          value-format="x" style="width: 360px" />
        <el-button type="primary" @click="handleSearch">{{ $t('admin.logs.search') }}</el-button>
        <el-button @click="handleReset">{{ $t('admin.logs.reset') }}</el-button>
      </div>
    </el-card>

    <!-- 日志表格 -->
    <el-card shadow="never">
      <el-table v-loading="loading" :data="list" border>
        <el-table-column :label="$t('admin.logs.time')" width="170">
          <template #default="{ row }">{{ formatTime(row.createtime) }}</template>
        </el-table-column>
        <el-table-column :label="$t('admin.logs.user')" width="140">
          <template #default="{ row }">
            {{ row.username || '—' }}
            <el-tag v-if="row.role" size="small" type="info" style="margin-left: 4px">{{ row.role }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="action" :label="$t('admin.logs.action')" min-width="200" show-overflow-tooltip />
        <el-table-column prop="method" :label="$t('admin.logs.method')" width="80">
          <template #default="{ row }">
            <el-tag v-if="row.method" size="small" :type="methodTag(row.method)">{{ row.method }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status_code" :label="$t('admin.logs.status_code')" width="90">
          <template #default="{ row }">
            <el-tag v-if="row.status_code" size="small" :type="row.status_code < 400 ? 'success' : 'danger'">
              {{ row.status_code }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="ip" :label="$t('admin.logs.ip')" width="140" show-overflow-tooltip />
        <el-table-column :label="$t('admin.logs.actions')" width="90" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="showDetail(row)">
              {{ $t('admin.logs.detail') }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination class="pager" v-model:current-page="page" v-model:page-size="pageSize" :total="total"
        :page-sizes="[20, 50, 100]" layout="total, sizes, prev, pager, next"
        @current-change="load" @size-change="handleSizeChange" />
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" :title="$t('admin.logs.detail_title')" width="640px">
      <template v-if="detailRow">
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item :label="$t('admin.logs.time')">{{ formatTime(detailRow.createtime) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('admin.logs.user')">
            {{ detailRow.username || '—' }}（{{ detailRow.role || '—' }}）
          </el-descriptions-item>
          <el-descriptions-item :label="$t('admin.logs.action')" :span="2">{{ detailRow.action }}</el-descriptions-item>
          <el-descriptions-item :label="$t('admin.logs.method')">{{ detailRow.method }}</el-descriptions-item>
          <el-descriptions-item :label="$t('admin.logs.status_code')">{{ detailRow.status_code }}</el-descriptions-item>
          <el-descriptions-item :label="$t('admin.logs.ip')">{{ detailRow.ip || '—' }}</el-descriptions-item>
          <el-descriptions-item :label="$t('admin.logs.ua_short')">{{ detailRow.user_agent || '—' }}</el-descriptions-item>
        </el-descriptions>
        <div v-if="detailRow.detail" class="detail-json">
          <div class="detail-label">{{ $t('admin.logs.request_body') }}</div>
          <pre>{{ JSON.stringify(detailRow.detail, null, 2) }}</pre>
        </div>
        <div v-if="detailRow.user_agent" class="detail-ua">
          <div class="detail-label">User-Agent</div>
          <p>{{ detailRow.user_agent }}</p>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getAdminLogs, type AdminLogItem } from '@/api/services/adminLogs'

const loading = ref(false)
const list = ref<AdminLogItem[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

const filterUsername = ref('')
const filterAction = ref('')
const dateRange = ref<[string, string] | null>(null)

const detailVisible = ref(false)
const detailRow = ref<AdminLogItem | null>(null)

const formatTime = (ts?: number) => {
  if (!ts) return '—'
  return new Date(ts * 1000).toLocaleString()
}

const methodTag = (m: string): 'success' | 'warning' | 'danger' | 'info' => {
  if (m === 'GET') return 'success'
  if (m === 'POST') return 'warning'
  if (m === 'DELETE') return 'danger'
  return 'info'
}

const load = async () => {
  loading.value = true
  try {
    const params: Record<string, unknown> = {
      page: page.value,
      page_size: pageSize.value
    }
    if (filterUsername.value.trim()) params.username = filterUsername.value.trim()
    if (filterAction.value.trim()) params.action = filterAction.value.trim()
    if (dateRange.value) {
      // value-format="x" 给的是毫秒字符串，后端要秒级时间戳
      params.start_time = Math.floor(Number(dateRange.value[0]) / 1000)
      params.end_time = Math.floor(Number(dateRange.value[1]) / 1000)
    }
    const res = await getAdminLogs(params)
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

const handleReset = () => {
  filterUsername.value = ''
  filterAction.value = ''
  dateRange.value = null
  handleSearch()
}

const handleSizeChange = () => {
  page.value = 1
  load()
}

const showDetail = (row: AdminLogItem) => {
  detailRow.value = row
  detailVisible.value = true
}

onMounted(load)
</script>

<style scoped>
.admin-logs {
  padding: 20px;
}

.page-header {
  margin-bottom: 16px;
}

.page-header h1 {
  margin: 0 0 6px;
  font-size: 22px;
}

.page-header p {
  margin: 0;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.filter-card {
  margin-bottom: 16px;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.pager {
  margin-top: 14px;
  justify-content: flex-end;
}

.detail-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-bottom: 6px;
}

.detail-json {
  margin-top: 14px;
}

.detail-json pre {
  margin: 0;
  padding: 10px;
  background: var(--el-fill-color-light);
  border-radius: 6px;
  font-size: 12px;
  max-height: 300px;
  overflow: auto;
}

.detail-ua {
  margin-top: 14px;
}

.detail-ua p {
  margin: 0;
  font-size: 12px;
  word-break: break-all;
  color: var(--el-text-color-secondary);
}
</style>
