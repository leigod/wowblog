<template>
  <div class="comment-management">
    <div class="page-header">
      <h1>{{ $t('admin.comment.list.title') }}</h1>
      <p>{{ $t('admin.comment.list.subtitle') }}</p>
    </div>

    <!-- 统计卡片 -->
    <div class="statistics-cards">
      <div class="stat-card">
        <div class="stat-icon total">
          <IconifyIcon icon="lucide:message-square" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ statistics.total_comments }}</div>
          <div class="stat-label">{{ $t('admin.comment.stats.total') }}</div>
        </div>
      </div>
      <div class="stat-card" :class="{ warning: statistics.pending_audit > 0 }">
        <div class="stat-icon pending">
          <IconifyIcon icon="lucide:clock" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ statistics.pending_audit }}</div>
          <div class="stat-label">{{ $t('admin.comment.stats.pending') }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon today">
          <IconifyIcon icon="lucide:calendar" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ statistics.today_comments }}</div>
          <div class="stat-label">{{ $t('admin.comment.stats.today') }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon week">
          <IconifyIcon icon="lucide:trending-up" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ statistics.week_comments }}</div>
          <div class="stat-label">{{ $t('admin.comment.stats.week') }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon hidden">
          <IconifyIcon icon="lucide:eye-off" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ statistics.hidden_comments }}</div>
          <div class="stat-label">{{ $t('admin.comment.stats.hidden') }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon sensitive">
          <IconifyIcon icon="lucide:alert-triangle" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ statistics.sensitive_detected }}</div>
          <div class="stat-label">{{ $t('admin.comment.stats.sensitive') }}</div>
        </div>
      </div>
    </div>

    <!-- 状态标签页 -->
    <el-tabs v-model="activeStatus" class="status-tabs" @tab-click="handleStatusChange">
      <el-tab-pane :label="$t('admin.comment.tabs.all') + ` (${totalCount.all})`" name="all" />
      <el-tab-pane :label="$t('admin.comment.tabs.normal') + ` (${totalCount.normal})`" name="normal" />
      <el-tab-pane :label="$t('admin.comment.tabs.hidden') + ` (${totalCount.hidden})`" name="hidden" />
      <el-tab-pane :label="$t('admin.comment.tabs.pending') + ` (${totalCount.pending})`" name="pending" />
      <el-tab-pane :label="$t('admin.comment.tabs.approved') + ` (${totalCount.approved})`" name="approved" />
      <el-tab-pane :label="$t('admin.comment.tabs.rejected') + ` (${totalCount.rejected})`" name="rejected" />
    </el-tabs>

    <!-- 搜索和筛选 -->
    <div class="search-filter">
      <el-input v-model="searchKeyword" :placeholder="$t('admin.comment.list.search_placeholder')" prefix-icon="Search"
        class="search-input" @input="handleSearch" />
      <el-button icon="Filter" @click="showFilterDialog = true">
        {{ $t('admin.comment.list.filter') }}
      </el-button>
      <el-dropdown @command="handleBatchAction" v-if="selectedComments.length > 0">
        <el-button type="primary">
          {{ $t('admin.comment.list.batch_action') }} ({{ selectedComments.length }})
          <IconifyIcon icon="lucide:chevron-down" style="margin-left: 4px" />
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="approve">
              <IconifyIcon icon="lucide:check" /> {{ $t('admin.comment.actions.approve') }}
            </el-dropdown-item>
            <el-dropdown-item command="reject">
              <IconifyIcon icon="lucide:x" /> {{ $t('admin.comment.actions.reject') }}
            </el-dropdown-item>
            <el-dropdown-item command="show">
              <IconifyIcon icon="lucide:eye" /> {{ $t('admin.comment.actions.show') }}
            </el-dropdown-item>
            <el-dropdown-item command="hide">
              <IconifyIcon icon="lucide:eye-off" /> {{ $t('admin.comment.actions.hide') }}
            </el-dropdown-item>
            <el-dropdown-item command="delete" divided>
              <IconifyIcon icon="lucide:trash-2" /> {{ $t('admin.comment.actions.delete') }}
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <!-- 评论列表 -->
    <div class="comment-list" v-loading="loading">
      <el-empty v-if="commentList.length === 0 && !loading" :description="$t('admin.comment.list.empty')" />

      <div v-for="comment in commentList" :key="comment.id" class="comment-item">
        <div class="comment-checkbox">
          <el-checkbox v-model="selectedComments" :label="comment.id" />
        </div>

        <div class="comment-avatar">
          <el-avatar :src="comment.user_avatar" :size="40">
            {{ comment.username?.charAt(0)?.toUpperCase() }}
          </el-avatar>
        </div>

        <div class="comment-content-wrapper">
          <div class="comment-header">
            <span class="comment-username">{{ comment.username }}</span>
            <span class="comment-time">{{ formatTime(comment.created_at) }}</span>
            <el-tag v-if="comment.status === 'hidden'" type="info" size="small">
              {{ $t('admin.comment.status.hidden') }}
            </el-tag>
            <el-tag v-if="comment.audit_status === 'pending'" type="warning" size="small">
              {{ $t('admin.comment.status.pending') }}
            </el-tag>
            <el-tag v-if="comment.audit_status === 'rejected'" type="danger" size="small">
              {{ $t('admin.comment.status.rejected') }}
            </el-tag>
            <el-tag v-if="comment.sensitive_words" type="danger" size="small">
              {{ $t('admin.comment.status.sensitive') }}
            </el-tag>
          </div>

          <div class="comment-text" v-html="comment.comment"></div>

          <div class="comment-meta" v-if="comment.article_title">
            <router-link :to="`/article/${comment.article_slug}`" class="article-link" target="_blank">
              {{ $t('admin.comment.list.article') }}: {{ comment.article_title }}
            </router-link>
          </div>

          <div class="comment-stats">
            <span>
              <IconifyIcon icon="lucide:heart" size="14" /> {{ comment.likes }}
            </span>
            <span>
              <IconifyIcon icon="lucide:message-circle" size="14" /> {{ comment.replys }}
            </span>
            <span v-if="comment.ip">
              <IconifyIcon icon="lucide:globe" size="14" /> {{ comment.ip }}
            </span>
          </div>
        </div>

        <div class="comment-actions">
          <el-dropdown @command="onCommentAction(comment)">
            <el-button text>
              <IconifyIcon icon="lucide:more-horizontal" />
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="approve" v-if="comment.audit_status === 'pending'">
                  <IconifyIcon icon="lucide:check" /> {{ $t('admin.comment.actions.approve') }}
                </el-dropdown-item>
                <el-dropdown-item command="reject" v-if="comment.audit_status === 'pending'">
                  <IconifyIcon icon="lucide:x" /> {{ $t('admin.comment.actions.reject') }}
                </el-dropdown-item>
                <el-dropdown-item command="show" v-if="comment.status === 'hidden'">
                  <IconifyIcon icon="lucide:eye" /> {{ $t('admin.comment.actions.show') }}
                </el-dropdown-item>
                <el-dropdown-item command="hide" v-if="comment.status === 'normal'">
                  <IconifyIcon icon="lucide:eye-off" /> {{ $t('admin.comment.actions.hide') }}
                </el-dropdown-item>
                <el-dropdown-item command="delete" divided>
                  <IconifyIcon icon="lucide:trash-2" /> {{ $t('admin.comment.actions.delete') }}
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrapper" v-if="total > 0">
      <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total"
        :page-sizes="[10, 20, 50, 100]" layout="total, sizes, prev, pager, next, jumper"
        @current-change="handlePageChange" @size-change="handleSizeChange" />
    </div>

    <!-- 筛选对话框 -->
    <el-dialog v-model="showFilterDialog" :title="$t('admin.comment.list.filter_comments')"
      :width="isMobile ? '90%' : '500px'" :label-position="isMobile ? 'top' : 'right'">
      <el-form :label-width="isMobile ? '80px' : '100px'" :inline="false">
        <el-form-item :label="$t('admin.comment.filter.date_range')" :label-position="isMobile ? 'top' : 'left'">
          <el-date-picker v-model="filterDateRange" type="daterange" range-separator="to"
            popper-class="mobile_datepicker" :start-placeholder="$t('admin.comment.filter.start_date')"
            :end-placeholder="$t('admin.comment.filter.end_date')" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item :label="$t('admin.comment.filter.audit_status')" :label-position="isMobile ? 'top' : 'left'">
          <el-select v-model="filterAuditStatus" :placeholder="$t('admin.comment.filter.select_status')" clearable
            style="width: 100%">
            <el-option :label="$t('admin.comment.tabs.pending')" value="pending" />
            <el-option :label="$t('admin.comment.tabs.approved')" value="approved" />
            <el-option :label="$t('admin.comment.tabs.rejected')" value="rejected" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resetFilters">{{ $t('admin.general.btn.reset') }}</el-button>
        <el-button type="primary" @click="applyFilters">{{ $t('admin.general.btn.apply') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import IconifyIcon from '@/components/IconIfy.vue'
import { useMobileDetection } from '@/composables/useMobileDetection'
import {
  getCommentList,
  updateCommentStatus,
  updateCommentAudit,
  batchOperation,
  getCommentStatistics,
  type CommentListItem,
  type CommentStatisticsData,
  type CommentListResponse,
  type CommentStatisticsResponse
} from '@/api/services/commentAdmin'

// 移动端检测
const { isMobile } = useMobileDetection()

// 状态管理
const loading = ref(false)
const commentList = ref<CommentListItem[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const activeStatus = ref('all')
const searchKeyword = ref('')
const selectedComments = ref<number[]>([])
const showFilterDialog = ref(false)

// 筛选条件
const filterDateRange = ref<[string, string] | null>(null)
const filterAuditStatus = ref<string | null>(null)

// 统计数据
const statistics = ref<CommentStatisticsData>({
  total_comments: 0,
  pending_audit: 0,
  today_comments: 0,
  week_comments: 0,
  hidden_comments: 0,
  deleted_comments: 0,
  sensitive_detected: 0
})

// 各状态数量（用于显示在标签页上）
const totalCount = reactive({
  all: 0,
  normal: 0,
  hidden: 0,
  pending: 0,
  approved: 0,
  rejected: 0
})

// 加载评论列表
const loadComments = async () => {
  loading.value = true
  try {
    const params: any = {
      page: currentPage.value,
      page_size: pageSize.value,
      keyword: searchKeyword.value || undefined
    }

    // 根据当前标签页设置状态筛选
    if (activeStatus.value === 'normal') {
      params.status = 'normal'
    } else if (activeStatus.value === 'hidden') {
      params.status = 'hidden'
    } else if (activeStatus.value === 'pending' || activeStatus.value === 'approved' || activeStatus.value === 'rejected') {
      params.audit_status = activeStatus.value
    }

    // 应用筛选条件
    if (filterDateRange.value) {
      params.start_date = filterDateRange.value[0]
      params.end_date = filterDateRange.value[1]
    }
    if (filterAuditStatus.value) {
      params.audit_status = filterAuditStatus.value
    }

    const response = await getCommentList(params)
    if (response && response.code === 1) {
      commentList.value = response.list || []
      total.value = response.total || 0
    }
  } catch (error) {
    console.error('加载评论列表失败:', error)
    ElMessage.error('加载评论列表失败')
  } finally {
    loading.value = false
  }
}

// 加载统计数据
const loadStatistics = async () => {
  try {
    const response = await getCommentStatistics()
    if (response && response.code === 1) {
      // 统计数据可能在 data 字段中或直接在根级别
      const stats = response.data || response
      statistics.value = {
        total_comments: stats.total_comments || 0,
        pending_audit: stats.pending_audit || 0,
        today_comments: stats.today_comments || 0,
        week_comments: stats.week_comments || 0,
        hidden_comments: stats.hidden_comments || 0,
        deleted_comments: stats.deleted_comments || 0,
        sensitive_detected: stats.sensitive_detected || 0
      }
      // 更新标签页数量
      totalCount.all = statistics.value.total_comments
      totalCount.normal = statistics.value.total_comments - statistics.value.hidden_comments - statistics.value.deleted_comments
      totalCount.hidden = statistics.value.hidden_comments
      totalCount.pending = statistics.value.pending_audit
      totalCount.approved = statistics.value.total_comments - statistics.value.pending_audit // 简化计算
      totalCount.rejected = 0 // 需要从后端获取
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

// 处理状态切换
const handleStatusChange = () => {
  currentPage.value = 1
  selectedComments.value = []
  loadComments()
}

// 处理搜索（防抖）
let searchTimer: NodeJS.Timeout | null = null
const handleSearch = () => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    loadComments()
  }, 500)
}

// 处理分页变化
const handlePageChange = () => {
  loadComments()
}

const handleSizeChange = () => {
  currentPage.value = 1
  loadComments()
}

// 应用筛选
const applyFilters = () => {
  currentPage.value = 1
  showFilterDialog.value = false
  loadComments()
}

// 重置筛选
const resetFilters = () => {
  filterDateRange.value = null
  filterAuditStatus.value = null
}

// 处理单个评论操作
const handleCommentAction = async (action: string, comment: CommentListItem) => {
  try {
    if (action === 'approve') {
      await updateCommentAudit(comment.id, { audit_status: 'approved' })
      ElMessage.success('审核通过')
    } else if (action === 'reject') {
      await updateCommentAudit(comment.id, { audit_status: 'rejected' })
      ElMessage.success('已拒绝')
    } else if (action === 'show') {
      await updateCommentStatus(comment.id, { status: 'normal' })
      ElMessage.success('已显示')
    } else if (action === 'hide') {
      await updateCommentStatus(comment.id, { status: 'hidden' })
      ElMessage.success('已隐藏')
    } else if (action === 'delete') {
      await ElMessageBox.confirm('确认删除此评论？', '提示', {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      })
      await updateCommentStatus(comment.id, { status: 'deleted' })
      ElMessage.success('已删除')
    }

    await loadComments()
    await loadStatistics()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('操作失败:', error)
      ElMessage.error(error?.response?.data?.msg || '操作失败')
    }
  }
}

// 为模板中的下拉菜单事件创建包装函数
const onCommentAction = (comment: CommentListItem) => {
  return (cmd: string) => handleCommentAction(cmd, comment)
}

// 处理批量操作
const handleBatchAction = async (action: string) => {
  if (selectedComments.value.length === 0) {
    ElMessage.warning('请先选择评论')
    return
  }

  try {
    const actionMap: Record<string, string> = {
      approve: '通过',
      reject: '拒绝',
      show: '显示',
      hide: '隐藏',
      delete: '删除'
    }

    if (action === 'delete') {
      await ElMessageBox.confirm(`确认${actionMap[action]}选中的 ${selectedComments.value.length} 条评论？`, '提示', {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      })
    }

    await batchOperation({
      action,
      comment_ids: selectedComments.value
    })

    ElMessage.success(`已${actionMap[action]} ${selectedComments.value.length} 条评论`)
    selectedComments.value = []
    await loadComments()
    await loadStatistics()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('批量操作失败:', error)
      ElMessage.error(error?.response?.data?.msg || '操作失败')
    }
  }
}

// 格式化时间
const formatTime = (timestamp: number) => {
  const date = new Date(timestamp * 1000)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)} 天前`

  return date.toLocaleDateString()
}

// 初始化
onMounted(() => {
  loadComments()
  loadStatistics()
})
</script>

<style scoped>
.comment-management {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
}

.page-header p {
  color: #666;
  font-size: 14px;
}

/* 统计卡片 */
.statistics-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  transition: all 0.2s;
}

.stat-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stat-card.warning {
  border-color: #f59e0b;
  background: #fffbeb;
}

.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
}

.stat-icon :deep(svg) {
  width: 22px;
  height: 22px;
}

.stat-icon.total {
  background: #dbeafe;
  color: #3b82f6;
}

.stat-icon.pending {
  background: #fef3c7;
  color: #f59e0b;
}

.stat-icon.today {
  background: #d1fae5;
  color: #10b981;
}

.stat-icon.week {
  background: #e0e7ff;
  color: #6366f1;
}

.stat-icon.hidden {
  background: #f3f4f6;
  color: #6b7280;
}

.stat-icon.sensitive {
  background: #fee2e2;
  color: #ef4444;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  line-height: 1;
}

.stat-label {
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

/* 状态标签页 */
.status-tabs {
  margin-bottom: 16px;
}

/* 搜索和筛选 */
.search-filter {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.search-input {
  max-width: 300px;
}

/* 评论列表 */
.comment-list {
  min-height: 200px;
}

.comment-item {
  display: flex;
  align-items: flex-start;
  padding: 16px;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  margin-bottom: 12px;
  transition: all 0.2s;
}

.comment-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.comment-checkbox {
  margin-right: 12px;
  padding-top: 4px;
}

.comment-avatar {
  margin-right: 12px;
}

.comment-content-wrapper {
  flex: 1;
  min-width: 0;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.comment-username {
  font-weight: 600;
  color: #1f2937;
}

.comment-time {
  font-size: 12px;
  color: #9ca3af;
}

.comment-text {
  color: #374151;
  line-height: 1.6;
  margin-bottom: 8px;
  word-break: break-word;
}

.comment-text :deep(p) {
  margin: 0;
}

.comment-meta {
  margin-bottom: 8px;
}

.article-link {
  font-size: 13px;
  color: #6b7280;
  text-decoration: none;
}

.article-link:hover {
  color: #3b82f6;
}

.comment-stats {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #9ca3af;
}

.comment-stats span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.comment-actions {
  margin-left: 8px;
}

/* 分页 */
.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

/* 移动端适配 */
@media (max-width: 767px) {
  .statistics-cards {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .stat-card {
    padding: 16px;
  }

  .stat-icon {
    width: 36px;
    height: 36px;
  }

  .stat-value {
    font-size: 18px;
  }

  .stat-label {
    font-size: 12px;
  }

  .search-filter {
    flex-direction: column;
    gap: 8px;
  }

  .search-filter .search-input {
    width: 100%;
  }

  .search-filter .el-button {
    width: 100%;
  }

  /* 评论列表移动端优化 */
  .comment-item {
    padding: 12px;
  }

  .comment-avatar {
    width: 36px;
    height: 36px;
  }

  .comment-content-wrapper {
    margin-left: 12px;
  }

  .comment-header {
    flex-wrap: wrap;
    gap: 4px 8px;
  }

  .comment-username {
    font-size: 14px;
  }

  .comment-time {
    font-size: 12px;
  }

  .comment-text {
    font-size: 14px;
  }

  .comment-meta {
    font-size: 12px;
  }

  .comment-stats {
    flex-wrap: wrap;
    font-size: 12px;
    gap: 8px 12px;
  }

  .comment-actions {
    margin-left: 0;
    margin-top: 8px;
  }

  /* 标签页移动端优化 */
  .status-tabs :deep(.el-tabs__item) {
    font-size: 14px;
    padding: 0 12px;
  }

  /* 分页优化 */
  .pagination-wrapper :deep(.el-pagination__sizes),
  .pagination-wrapper :deep(.el-pagination__jump) {
    display: none;
  }

  /* 对话框宽度优化 */
  .el-dialog {
    width: 95% !important;
    margin: 5vh auto;
  }

  .el-dialog__body {
    padding: 15px;
  }

  /* 日期选择器移动端优化 */
  .el-date-editor {
    width: 100%;
  }

  .el-date-editor :deep(.el-input__wrapper) {
    width: 100% !important;
  }

  .el-date-editor :deep(.el-input__inner) {
    width: 100% !important;
  }

  /* 确保日期范围选择器的两个输入框都全宽 */
  .el-date-editor--range {
    width: 100%;
  }

  /* 移动端日期范围选择器折行显示 */
  .el-date-editor--range :deep(.el-date-editor__time-header) {
    display: flex;
    flex-wrap: wrap;
  }

  .el-date-editor--range :deep(.el-date-editor__time-wrap) {
    flex-basis: 100%;
    margin-bottom: 8px;
  }

  .el-date-editor--range :deep(.el-date-editor__time-wrap:last-child) {
    margin-bottom: 0;
  }

  /* 日期输入框容器折行 */
  .el-date-editor--range :deep(.el-date-editor__content) {
    flex-wrap: wrap;
  }

  /* 每个日期输入框单独一行 */
  .el-date-editor--range :deep(.el-range__content) {
    flex-wrap: wrap;
  }

  .el-date-editor--range :deep(.el-range-input) {
    width: 100%;
    min-width: 100%;
    margin-bottom: 8px;
  }

  .el-date-editor--range :deep(.el-range-input:last-of-type) {
    margin-bottom: 0;
  }

  /* 隐藏或调整分隔符 */
  .el-date-editor--range :deep(.el-range-separator) {
    display: none;
  }

  /* 日期选择器面板移动端优化 */
  .el-picker-popper {
    max-width: 100vw !important;
  }

  .el-picker__panel {
    max-width: 100vw;
  }

  /* 日期范围面板 - 两个日历垂直排列 */
  :deep(.el-date-range-picker) {
    width: auto !important;
  }

  :deep(.el-date-range-picker__content) {
    flex-direction: column;
    display: flex;
  }

  :deep(.el-date-range-picker__content .el-picker-panel__content) {
    width: 100%;
    margin-bottom: 10px;
  }

  :deep(.el-date-range-picker__content .el-picker-panel__content:last-child) {
    margin-bottom: 0;
  }

  :deep(.el-date-range-picker .el-picker-panel__body) {
    width: 100%;
    display: flex;
    flex-wrap: wrap;
  }

  :deep(.el-date-range-picker__content) {
    width: 75%;
  }

  .mobile_datepicker {
    font-size: 10px;
    padding: 0;
    margin: 0;
  }

  .el-date-table-cell {
    padding: 0;
    margin: 0;
  }

  .el-date-table-cell__text {
    padding: 0;
    margin: 0;
  }

  /* 下拉选择器移动端优化 */
  .el-select {
    width: 100%;
  }

  /* 表单项间距优化 */
  .el-form-item {
    margin-bottom: 18px;
  }

  /* 对话框底部按钮优化 */
  .el-dialog__footer {
    padding: 15px;
  }
}
</style>

<!-- 全局样式：用于影响挂载到 body 的弹出层 -->
<style>
/* 移动端日期范围选择器面板优化 - 两个日历垂直排列 */
@media (max-width: 767px) {
  .el-date-range-picker .el-date-range-picker__content {
    flex-direction: column !important;
    display: flex !important;
  }

  .el-date-range-picker .el-picker-panel__content {
    width: 100% !important;
    margin-bottom: 10px;
  }

  .el-date-range-picker .el-picker-panel__content:last-child {
    margin-bottom: 0;
  }

  /* 确保日期选择器面板在小屏幕上完整显示 */
  .el-picker__popper {
    max-width: 100vw !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
  }

  .el-picker-panel {
    max-width: 100vw;
  }

  /* 日期表格单元格在移动端的间距优化 */
  .el-date-table-cell {
    padding: 0;
    margin: 0;
  }

  .el-date-table-cell__text {
    padding: 0;
    margin: 0;
    font-size: 12px;
  }
}
</style>
