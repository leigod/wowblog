<template>
  <div class="notifications-page">
    <div class="page-header">
      <h1>{{ t('notification.title') }}</h1>
    </div>

    <!-- 搜索和筛选栏 -->
    <div class="notifications-toolbar">
      <div class="search-wrapper">
        <el-input
          v-model="searchQuery"
          :placeholder="t('notification.search_placeholder')"
          :prefix-icon="Search"
          clearable
          class="search-input"
        />
      </div>

      <div class="filter-tabs-wrapper">
        <el-tabs v-model="activeFilter" class="filter-tabs">
          <el-tab-pane :label="t('notification.tab_all')" name="all" />
          <el-tab-pane :label="t('notification.tab_unread')" name="unread" />
          <el-tab-pane :label="t('notification.tab_comment')" name="comment" />
          <el-tab-pane :label="t('notification.tab_like_bookmark')" name="like_bookmark" />
          <el-tab-pane :label="t('notification.tab_mention')" name="mention" />
          <el-tab-pane :label="t('notification.tab_system')" name="system" />
        </el-tabs>
      </div>

      <div class="header-actions">
        <el-button v-if="unreadCount > 0" type="primary" @click="handleMarkAllRead">
          {{ t('notification.mark_all_read') }}
        </el-button>
      </div>
    </div>

    <!-- 通知列表 -->
    <div v-loading="loading" class="notifications-list">
      <!-- 批量操作栏 -->
      <div v-if="selectedIds.length > 0" class="batch-actions">
        <span class="selected-count">{{
          t('notification.selected_count', { n: selectedIds.length })
        }}</span>
        <el-button text @click="handleMarkSelectedRead">{{
          t('notification.mark_selected_read')
        }}</el-button>
        <el-button text type="danger" @click="handleDeleteSelected">{{
          t('notification.delete_selected')
        }}</el-button>
        <el-button text @click="clearSelection">{{ t('notification.cancel_selection') }}</el-button>
      </div>

      <!-- 空状态 -->
      <div v-if="filteredNotifications.length === 0" class="empty-state">
        <el-icon :size="48">
          <Bell />
        </el-icon>
        <p>{{ t('notification.empty') }}</p>
      </div>

      <!-- 通知项列表（使用 checkbox-group 包裹） -->
      <el-checkbox-group v-model="selectedIds">
        <!-- 通知项 -->
        <div
          v-for="item in filteredNotifications"
          :key="item.id"
          class="notification-item"
          :class="{ unread: !item.is_read, important: item.is_important }"
        >
          <!-- 复选框 -->
          <el-checkbox :value="item.id" class="notification-checkbox" @click.stop />

          <!-- 重要性标记 -->
          <el-icon
            :class="['important-star', { active: item.is_important }]"
            @click.stop="toggleImportant(item)"
          >
            <StarFilled />
          </el-icon>

          <!-- 通知图标 -->
          <div :class="['notification-icon', `type-${item.type}`]">
            <el-icon :size="20">
              <component :is="getNotificationIcon(item.type)" />
            </el-icon>
          </div>

          <!-- 通知内容 -->
          <div class="notification-content" @click="handleNotificationClick(item)">
            <div class="notification-title">{{ item.title }}</div>
            <div class="notification-meta">
              <span class="notification-time">{{ formatTime(item.created_at) }}</span>
              <span v-if="item.content" class="notification-snippet">{{ item.content }}</span>
            </div>
          </div>

          <!-- 未读指示器 -->
          <div v-if="!item.is_read" class="unread-indicator"></div>

          <!-- 悬停操作按钮 -->
          <div class="notification-actions">
            <el-button
              v-if="!item.is_read"
              type="primary"
              link
              size="small"
              @click.stop="handleMarkAsRead(item.id)"
            >
              {{ t('notification.mark_as_read') }}
            </el-button>
            <el-dropdown trigger="click" @command="handleItemCommand(item)">
              <el-button :icon="MoreFilled" circle size="small" />
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="toggle-important">
                    <el-icon>
                      <StarFilled />
                    </el-icon>
                    {{
                      item.is_important
                        ? t('notification.unmark_important')
                        : t('notification.mark_important')
                    }}
                  </el-dropdown-item>
                  <el-dropdown-item command="delete" divided>
                    <el-icon>
                      <Delete />
                    </el-icon>
                    {{ t('notification.delete') }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-checkbox-group>
    </div>

    <!-- 分页 -->
    <div v-if="total > pageSize" class="pagination-wrapper">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="prev, pager, next"
        @size-change="loadNotifications"
        @current-change="loadNotifications"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Bell,
  StarFilled,
  Search,
  ChatDotRound,
  Promotion,
  Collection,
  InfoFilled,
  Warning,
  MoreFilled,
  Delete
} from '@element-plus/icons-vue'
import * as notificationApi from '@/api/services/notifications'

const { t } = useI18n()
const router = useRouter()

defineOptions({
  name: 'NotificationsView'
})

const loading = ref(false)
const notifications = ref<notificationApi.NotificationListItem[]>([])
const unreadCount = ref(0)
type FilterType = 'all' | 'unread' | 'comment' | 'like_bookmark' | 'mention' | 'system'
const activeFilter = ref<FilterType>('all')
const searchQuery = ref('')
const selectedIds = ref<number[]>([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 过滤后的通知列表
const filteredNotifications = computed(() => {
  let result = notifications.value

  // 按筛选条件过滤
  if (activeFilter.value === 'unread') {
    result = result.filter((item) => !item.is_read)
  } else if (activeFilter.value === 'comment') {
    result = result.filter((item) => item.type === 'comment' || item.type === 'reply')
  } else if (activeFilter.value === 'like_bookmark') {
    result = result.filter((item) => item.type === 'like' || item.type === 'bookmark')
  } else if (activeFilter.value === 'mention') {
    result = result.filter(
      (item) => item.type === 'article_mention' || item.type === 'comment_mention'
    )
  } else if (activeFilter.value === 'system') {
    result = result.filter((item) => item.type === 'system' || item.type === 'warning')
  }

  // 按搜索关键词过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter((item) => {
      return (
        item.title.toLowerCase().includes(query) ||
        (item.content && item.content.toLowerCase().includes(query))
      )
    })
  }

  return result
})

// 格式化时间
const formatTime = (timestamp: number) => {
  const date = new Date(timestamp * 1000)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (minutes < 1) return t('notification.time_just_now')
  if (minutes < 60) return t('notification.time_minutes_ago', { n: minutes })
  if (hours < 24) return t('notification.time_hours_ago', { n: hours })
  if (days < 7) return t('notification.time_days_ago', { n: days })
  return date.toLocaleDateString()
}

// 获取通知类型图标
const getNotificationIcon = (type: string) => {
  const iconMap: Record<string, any> = {
    comment: ChatDotRound,
    reply: ChatDotRound,
    article_mention: Promotion,
    comment_mention: Promotion,
    like: Collection,
    bookmark: Collection,
    system: InfoFilled,
    warning: Warning
  }
  return iconMap[type] || Bell
}

// 清除选择
const clearSelection = () => {
  selectedIds.value = []
}

// 切换重要性
const toggleImportant = async (item: notificationApi.NotificationListItem) => {
  // 这里需要调用后端API，暂时只在前端更新
  item.is_important = !item.is_important
  ElMessage.success(
    item.is_important ? t('notification.marked_important') : t('notification.unmarked_important')
  )
}

// 处理下拉菜单命令的包装函数
// el-dropdown 的 command 事件处理器：直接接收 (item, command) 双参数。
// 不要写成柯里化 —— 模板里 @command="fn(item)" 是 inline 表达式，
// 返回的内层函数会被丢弃，command 永远传不进来（表现为菜单项点击无反应）
const handleItemCommand = (item: notificationApi.NotificationListItem, command: string) => {
  handleCommand(command, item)
}

// 加载通知列表
const loadNotifications = async () => {
  loading.value = true
  try {
    const unreadOnly = activeFilter.value === 'unread'

    const res = await notificationApi.getNotifications({
      unread_only: unreadOnly,
      page: currentPage.value,
      page_size: pageSize.value
    })

    if (res.code === 1 && res.data) {
      // 模拟添加 is_important 字段
      notifications.value = res.data.map((item) => ({
        ...item,
        is_important: false
      }))
      total.value = res.data.length
    }
  } catch (error) {
    console.error('加载通知失败:', error)
    ElMessage.error(t('notification.load_failed'))
  } finally {
    loading.value = false
  }
}

// 加载未读数量
const loadUnreadCount = async () => {
  try {
    const res = await notificationApi.getUnreadCount()
    if (res.code === 1) {
      unreadCount.value = res.data || 0
    }
  } catch (error) {
    console.error('获取未读数量失败:', error)
  }
}

// 标记单条为已读
const handleMarkAsRead = async (id: number) => {
  try {
    const res = await notificationApi.markAsRead(id)
    if (res.code === 1) {
      const item = notifications.value.find((n) => n.id === id)
      if (item) {
        item.is_read = true
      }
      await loadUnreadCount()
      ElMessage.success(t('notification.marked_as_read'))
    }
  } catch (error) {
    console.error('标记失败:', error)
    ElMessage.error(t('notification.mark_failed'))
  }
}

// 标记全部为已读
const handleMarkAllRead = async () => {
  try {
    const res = await notificationApi.markAllAsRead()
    if (res.code === 1) {
      notifications.value.forEach((item) => {
        item.is_read = true
      })
      await loadUnreadCount()
      ElMessage.success(t('notification.marked_all_read'))
    }
  } catch (error) {
    console.error('标记失败:', error)
    ElMessage.error(t('notification.mark_failed'))
  }
}

// 标记选中项为已读
const handleMarkSelectedRead = async () => {
  try {
    await Promise.all(selectedIds.value.map((id) => notificationApi.markAsRead(id)))
    notifications.value.forEach((item) => {
      if (selectedIds.value.includes(item.id)) {
        item.is_read = true
      }
    })
    await loadUnreadCount()
    clearSelection()
    ElMessage.success(t('notification.marked_selected_read_success'))
  } catch (error) {
    console.error('标记失败:', error)
    ElMessage.error(t('notification.mark_failed'))
  }
}

// 删除通知
const handleDelete = async (id: number) => {
  try {
    const res = await notificationApi.deleteNotification(id)
    if (res.code === 1) {
      notifications.value = notifications.value.filter((n) => n.id !== id)
      await loadUnreadCount()
      ElMessage.success(t('notification.delete_success'))
    }
  } catch (error) {
    console.error('删除失败:', error)
    ElMessage.error(t('notification.delete_failed'))
  }
}

// 删除选中项
const handleDeleteSelected = async () => {
  try {
    await Promise.all(selectedIds.value.map((id) => notificationApi.deleteNotification(id)))
    notifications.value = notifications.value.filter((n) => !selectedIds.value.includes(n.id))
    await loadUnreadCount()
    clearSelection()
    ElMessage.success(t('notification.delete_selected_success'))
  } catch (error) {
    console.error('删除失败:', error)
    ElMessage.error(t('notification.delete_failed'))
  }
}

// 处理下拉菜单命令
const handleCommand = (command: string, item: notificationApi.NotificationListItem) => {
  if (command === 'toggle-important') {
    toggleImportant(item)
  } else if (command === 'delete') {
    ElMessageBox.confirm(t('notification.delete_confirm'), t('notification.delete_confirm_title'), {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
      type: 'warning'
    })
      .then(() => {
        handleDelete(item.id)
      })
      .catch(() => {
        // 取消删除
      })
  }
}

// 点击通知
const handleNotificationClick = async (item: notificationApi.NotificationListItem) => {
  // 标记为已读
  if (!item.is_read) {
    await handleMarkAsRead(item.id)
  }

  // 跳转到目标页面
  if (item.target_url) {
    router.push(item.target_url)
  }
}

// 监听筛选条件变化
watch(activeFilter, () => {
  currentPage.value = 1
  loadNotifications()
})

watch(searchQuery, () => {
  // 搜索是在前端过滤，不需要重新加载
})

onMounted(() => {
  loadNotifications()
  loadUnreadCount()
})
</script>

<style scoped>
.notifications-page {
  width: 100%;
  max-width: 960px;
  margin: 0 auto;
  padding: 28px 24px 64px;
  box-sizing: border-box;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0;
  font-size: 26px;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: var(--el-text-color-primary);
}

/* 工具栏：搜索独占一行（320 宽），第二行「胶囊筛选 + 全部已读」左右分置 */
.notifications-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px 16px;
  margin-bottom: 20px;
  width: 100%;
}

.search-wrapper {
  flex: 1 1 100%;
  max-width: 320px;
}

.search-input {
  width: 100%;
}

.filter-tabs-wrapper {
  flex: 1 1 auto;
  min-width: 0;
}

.filter-tabs {
  width: 100%;
  overflow-x: auto;
  scrollbar-width: none;

  &::-webkit-scrollbar {
    display: none;
  }
}

/* el-tabs → 胶囊组：去掉底部长线与滑动条，逐项独立胶囊 */
.filter-tabs :deep(.el-tabs__header) {
  margin: 0;
}

.filter-tabs :deep(.el-tabs__nav-wrap) {
  padding: 0;
}

.filter-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.filter-tabs :deep(.el-tabs__active-bar) {
  display: none;
}

.filter-tabs :deep(.el-tabs__nav) {
  display: flex;
  gap: 6px;
  border-bottom: none;
}

.filter-tabs :deep(.el-tabs__item) {
  --filter-tab-pad-x: 14px;
  height: 30px;
  line-height: 30px;
  padding: 0 var(--filter-tab-pad-x);
  border-radius: var(--wy-radius-pill, 999px);
  border: 1px solid transparent;
  font-size: 13px;
  font-weight: 400;
  color: var(--wy-text-secondary, var(--el-text-color-secondary));
  background-color: var(--wy-bg-muted, var(--el-fill-color-light));
  transition:
    background-color var(--wy-duration, 160ms) var(--wy-easing, ease),
    color var(--wy-duration, 160ms) var(--wy-easing, ease),
    border-color var(--wy-duration, 160ms) var(--wy-easing, ease);
}

/* element-plus 默认将首/尾 tab 的 padding 清零
   (.el-tabs--top > .el-tabs__header .el-tabs__item:nth-child(2) / :last-child，
   nav 里 active-bar 占据首个子元素位置，故第一个 tab 是 nth-child(2))，
   其特异性 (0,4,0) 高于上方规则；胶囊样式需要首尾留白一致，此处提权还原 */
.filter-tabs :deep(.el-tabs__header .el-tabs__item:nth-child(2)),
.filter-tabs :deep(.el-tabs__header .el-tabs__item:first-child) {
  padding-left: var(--filter-tab-pad-x);
}

.filter-tabs :deep(.el-tabs__header .el-tabs__item:last-child) {
  padding-right: var(--filter-tab-pad-x);
}

.filter-tabs :deep(.el-tabs__item:hover) {
  background-color: var(--wy-brand-soft, var(--el-color-primary-light-9));
  color: var(--wy-brand, var(--el-color-primary));
}

.filter-tabs :deep(.el-tabs__item.is-active) {
  background-color: var(--wy-brand, var(--el-color-primary));
  border-color: var(--wy-brand, var(--el-color-primary));
  color: var(--wy-on-brand, #ffffff);
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 8px;
  margin-left: auto;
}

.notifications-list {
  min-height: 300px;
}

.batch-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 10px 16px;
  background: var(--wy-brand-soft, var(--el-color-primary-light-9));
  border: 1px solid var(--el-color-primary-light-8, var(--wy-border-subtle));
  border-radius: var(--wy-radius-md, 8px);
  margin-bottom: 12px;
}

.selected-count {
  font-size: 14px;
  color: var(--el-text-color-primary);
  font-weight: 500;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: var(--el-text-color-placeholder);
}

.empty-state p {
  margin: 12px 0 0 0;
  font-size: 16px;
}

/* 列表项：12px 圆角 + 组件自写描边 → 规范 8px + subtle 细描边、无阴影 */
.notification-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: var(--wy-bg-surface, var(--el-bg-color));
  border: 1px solid var(--wy-border-subtle, var(--el-border-color-light));
  border-radius: var(--wy-radius-md, 8px);
  margin-bottom: 8px;
  transition:
    border-color var(--wy-duration, 160ms) var(--wy-easing, ease),
    box-shadow var(--wy-duration, 160ms) var(--wy-easing, ease);
  position: relative;
}

.notification-item:hover {
  border-color: var(--wy-border-strong, var(--el-border-color));
  box-shadow: var(--wy-shadow-card, 0 2px 12px rgba(24, 24, 27, 0.06));
}

/* 未读：浅品牌底 + 左侧内阴影色条（不用 border-left，避免改变内容宽度） */
.notification-item.unread {
  background: var(--wy-brand-soft, var(--el-color-primary-light-9));
  border-color: var(--el-color-primary-light-8, var(--wy-border-subtle));
  box-shadow: inset 3px 0 0 var(--wy-brand, var(--el-color-primary));
}

/* 重要标记优先于未读：星标条目左侧统一走琥珀色 */
.notification-item.important {
  box-shadow: inset 3px 0 0 var(--el-color-warning);
}

.notification-checkbox {
  flex-shrink: 0;
}

.important-star {
  flex-shrink: 0;
  font-size: 17px;
  color: var(--wy-border-strong, var(--el-border-color));
  cursor: pointer;
  transition: color var(--wy-duration, 160ms) var(--wy-easing, ease);
}

.important-star:hover,
.important-star.active {
  color: var(--el-color-warning);
}

/* 类型图标：原来 6 套独立渐变，各自一组色相；收敛为「浅色底 + 语义色图标」，
   底色由语义色混合得到，深色模式下自动跟着变，不需要第二套值。 */
.notification-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--wy-radius-md, 8px);
  flex-shrink: 0;
  background: var(--wy-bg-muted, var(--el-fill-color-light));
  color: var(--wy-text-tertiary, var(--el-text-color-secondary));
}

.notification-icon.type-comment,
.notification-icon.type-reply {
  background: var(--wy-brand-soft, #eef3fd);
  background: color-mix(in srgb, var(--el-color-primary) 12%, transparent);
  color: var(--el-color-primary);
}

.notification-icon.type-article_mention,
.notification-icon.type-comment_mention {
  background: var(--el-color-warning-light-9, #fbf5ec);
  background: color-mix(in srgb, var(--el-color-warning) 14%, transparent);
  color: var(--el-color-warning);
}

.notification-icon.type-like {
  background: var(--el-color-danger-light-9, #fdf1f0);
  background: color-mix(in srgb, var(--el-color-danger) 12%, transparent);
  color: var(--el-color-danger);
}

.notification-icon.type-bookmark {
  background: var(--el-color-success-light-9, #eef7f2);
  background: color-mix(in srgb, var(--el-color-success) 12%, transparent);
  color: var(--el-color-success);
}

.notification-icon.type-system {
  background: var(--wy-bg-muted, var(--el-fill-color-light));
  color: var(--el-color-info);
}

.notification-icon.type-warning {
  background: var(--el-color-danger-light-9, #fdf1f0);
  background: color-mix(in srgb, var(--el-color-danger) 14%, transparent);
  color: var(--el-color-danger);
}

.notification-content {
  flex: 1;
  min-width: 0;
  cursor: pointer;
}

/* 未读 / 已读的视觉差异：未读加粗 + 主文字色，已读降到正文级灰色。
   时间与摘要统一到 tertiary，避免和标题抢层级。 */
.notification-title {
  font-size: 14px;
  font-weight: 400;
  color: var(--wy-text-secondary, var(--el-text-color-regular));
  line-height: 1.45;
  margin-bottom: 4px;
}

.notification-item.unread .notification-title {
  font-weight: 600;
  color: var(--wy-text-primary, var(--el-text-color-primary));
}

.notification-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--wy-text-tertiary, var(--el-text-color-secondary));
}

.notification-time {
  flex-shrink: 0;
  color: var(--wy-text-tertiary, var(--el-text-color-secondary));
}

.notification-snippet {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--wy-text-tertiary, var(--el-text-color-secondary));
}

.unread-indicator {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--wy-brand, var(--el-color-primary));
  flex-shrink: 0;
}

.notification-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
  flex-shrink: 0;
}

.notification-item:hover .notification-actions {
  opacity: 1;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 24px;
  padding: 16px 0;
}

/* 移动端适配 */
@media (max-width: 767px) {
  .notifications-page {
    padding: 16px;
  }

  .page-header h1 {
    font-size: 24px;
  }

  .notifications-toolbar {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .search-wrapper {
    width: 100%;
  }

  .search-input {
    max-width: 100%;
  }

  /* 移动端筛选标签 - Element Plus tabs 自动支持横向滚动 */
  .filter-tabs :deep(.el-tabs__item) {
    --filter-tab-pad-x: 12px;
    height: 28px;
    line-height: 28px;
    font-size: 13px;
  }

  .header-actions {
    width: auto;
    margin-left: 0;
  }

  .header-actions .el-button {
    width: auto;
  }

  .notification-item {
    padding: 12px 16px;
    gap: 8px;
  }

  .notification-icon {
    width: 36px;
    height: 36px;
  }

  .notification-icon :deep(.el-icon) {
    font-size: 18px;
  }

  .notification-title {
    font-size: 14px;
  }

  .notification-meta {
    font-size: 12px;
  }

  .important-star {
    font-size: 16px;
  }

  .unread-indicator {
    width: 6px;
    height: 6px;
  }

  /* 移动端始终显示操作按钮 */
  .notification-actions {
    opacity: 1;
  }

  .batch-actions {
    flex-wrap: wrap;
    padding: 10px 12px;
  }

  .selected-count {
    width: 100%;
    margin-bottom: 8px;
  }
}
</style>
