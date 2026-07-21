<template>
  <div class="notification-panel">
    <!-- 头部 -->
    <div class="notification-header">
      <div class="header-left">
        <h3>{{ t('notification.title') }}</h3>
        <el-badge v-if="unreadCount > 0" :value="unreadCount" class="unread-badge" />
      </div>
      <el-button v-if="unreadCount > 0" type="primary" link size="small" @click="handleMarkAllRead">
        {{ t('notification.mark_all_read') }}
      </el-button>
    </div>

    <!-- 标签筛选 -->
    <div class="notification-tabs">
      <div class="tab-item" :class="{ active: activeTab === 'all' }" @click="activeTab = 'all'">
        {{ t('notification.tab_all') }}
      </div>
      <div class="tab-item" :class="{ active: activeTab === 'unread' }" @click="activeTab = 'unread'">
        {{ t('notification.tab_unread') }}
        <el-badge v-if="unreadCount > 0" :value="unreadCount" />
      </div>
      <div class="tab-item" :class="{ active: activeTab === 'mention' }" @click="activeTab = 'mention'">
        {{ t('notification.tab_mention') }}
      </div>
    </div>

    <!-- 通知列表 -->
    <div class="notification-list">
      <div v-if="notifications.length === 0" class="empty-state">
        <el-icon size="40">
          <Bell />
        </el-icon>
        <p>{{ t('notification.empty') }}</p>
      </div>

      <div v-for="item in notifications" :key="item.id" class="notification-item" :class="{ unread: !item.is_read }"
        @click="handleNotificationClick(item)">
        <!-- 触发者头像 -->
        <el-avatar :size="40" :src="item.actor_avatar || '/src/assets/avatar.png'" class="actor-avatar" />

        <!-- 通知内容 -->
        <div class="notification-content">
          <div class="notification-title">{{ item.title }}</div>
          <div v-if="item.content" class="notification-text">
            {{ item.content }}
          </div>
          <div class="notification-time">{{ formatTime(item.created_at) }}</div>
        </div>

        <!-- 未读标识 -->
        <div v-if="!item.is_read" class="unread-dot"></div>
      </div>
    </div>

    <!-- 底部 -->
    <div class="notification-footer">
      <a @click="handleViewAll" class="view-all-link">
        {{ t('notification.view_all') }}
      </a>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Bell } from '@element-plus/icons-vue'
import * as notificationApi from '@/api/services/notifications'

const { t } = useI18n()

const emit = defineEmits(['close'])

const router = useRouter()
const notifications = ref<notificationApi.NotificationListItem[]>([])
const unreadCount = ref(0)
const activeTab = ref('all')

// 缓存不同标签的数据
const tabCache = ref<Record<string, notificationApi.NotificationListItem[]>>({
  all: [],
  unread: [],
  mention: []
})
const cacheValid = ref<Record<string, boolean>>({
  all: false,
  unread: false,
  mention: false
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
  return date.toLocaleDateString('zh-CN')
}

// 加载通知列表
const loadNotifications = async (forceReload = false) => {
  // 如果缓存有效且不强制重新加载，直接使用缓存
  if (!forceReload && cacheValid.value[activeTab.value]) {
    notifications.value = tabCache.value[activeTab.value] || []
    return
  }

  try {
    const unreadOnly = activeTab.value === 'unread'

    const res = await notificationApi.getNotifications({
      unread_only: unreadOnly,
      page: 1,
      page_size: 10
    })

    if (res.code === 1 && res.data) {
      let list = res.data

      // 如果是@我标签，过滤相关类型
      if (activeTab.value === 'mention') {
        list = list.filter(
          item => item.type === 'article_mention' || item.type === 'comment_mention'
        )
      }

      // 更新缓存
      tabCache.value[activeTab.value] = list
      cacheValid.value[activeTab.value] = true
      notifications.value = list
    }
  } catch (error) {
    console.error('加载通知失败:', error)
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

// 标记全部已读
const handleMarkAllRead = async () => {
  try {
    const res = await notificationApi.markAllAsRead()
    if (res.code === 1) {
      ElMessage.success(t('notification.marked_all_read'))
      // 使所有缓存失效
      cacheValid.value = { all: false, unread: false, mention: false }
      await loadNotifications(true)
      await loadUnreadCount()
    }
  } catch (error) {
    console.error('标记失败:', error)
  }
}

// 点击通知
const handleNotificationClick = async (item: notificationApi.NotificationListItem) => {
  // 标记为已读
  if (!item.is_read) {
    try {
      await notificationApi.markAsRead(item.id)
      // 更新本地数据，避免重新加载
      const targetItem = notifications.value.find(n => n.id === item.id)
      if (targetItem) {
        targetItem.is_read = true
        // 更新缓存
        tabCache.value[activeTab.value] = [...notifications.value]
      }
    } catch (error) {
      console.error('标记已读失败:', error)
    }
  }

  // 跳转到目标页面
  if (item.target_url) {
    emit('close')
    router.push(item.target_url)
  }
}

// 查看全部通知
const handleViewAll = () => {
  emit('close')
  router.push('/notifications')
}

// 监听标签变化
watch(activeTab, async () => {
  // 切换标签时，如果缓存有效则使用缓存，否则重新加载
  await loadNotifications(false)
})

// 添加新通知（用于 WebSocket 实时推送）
const addNotification = (data: any) => {
  // 构造通知项
  const newItem: notificationApi.NotificationListItem = {
    id: data.id,
    type: data.type,
    title: data.title,
    content: data.content,
    actor_id: data.actor_id,
    actor_name: data.actor_name,
    actor_avatar: data.actor_avatar,
    target_url: data.target_url,
    is_read: data.is_read,
    created_at: data.created_at
  }

  // 追加到各个标签的缓存和当前显示的列表
  const prependToList = (list: notificationApi.NotificationListItem[]) => {
    const newList = [newItem, ...list]
    return newList
  }

  // 更新全部标签的缓存
  if (tabCache.value.all) {
    tabCache.value.all = prependToList(tabCache.value.all)
  }
  // 更新未读标签的缓存（新消息肯定是未读的）
  if (tabCache.value.unread) {
    tabCache.value.unread = prependToList(tabCache.value.unread)
  }
  // 如果是@提及类型，也更新@我标签的缓存
  if (newItem.type === 'article_mention' || newItem.type === 'comment_mention') {
    if (tabCache.value.mention) {
      tabCache.value.mention = prependToList(tabCache.value.mention)
    }
  }

  // 更新当前显示的列表
  notifications.value = prependToList(notifications.value)

  // 更新未读数量
  unreadCount.value++
}

// 暴露方法供父组件调用
defineExpose({
  loadUnreadCount,
  loadNotifications,
  addNotification,
  // 刷新所有缓存
  refreshCache: () => {
    cacheValid.value = { all: false, unread: false, mention: false }
    loadNotifications(true)
  }
})

onMounted(() => {
  loadNotifications(true) // 初始加载时强制刷新
  loadUnreadCount()
})
</script>

<style scoped>
.notification-panel {
  width: 345px;
  max-height: 500px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--el-border-color);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-left h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.notification-tabs {
  display: flex;
  padding: 0 20px;
  border-bottom: 1px solid var(--el-border-color);
}

.tab-item {
  padding: 12px 16px;
  cursor: pointer;
  color: var(--el-text-color-secondary);
  position: relative;
  display: flex;
  align-items: center;
  gap: 4px;
}

.tab-item:hover {
  color: var(--el-color-primary);
}

.tab-item.active {
  color: var(--el-color-primary);
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--el-color-primary);
}

.notification-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: var(--el-text-color-secondary);
}

.empty-state p {
  margin: 12px 0 0 0;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 20px;
  cursor: pointer;
  transition: background 0.2s;
  position: relative;
}

.notification-item:hover {
  background: var(--el-fill-color-light);
}

.notification-item.unread {
  background: var(--el-fill-color-extra-light);
}

.actor-avatar {
  flex-shrink: 0;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
  line-height: 1.4;
}

.notification-text {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.notification-time {
  font-size: 12px;
  color: var(--el-text-color-placeholder);
}

.unread-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--el-color-danger);
  flex-shrink: 0;
  margin-top: 4px;
}

.notification-footer {
  padding: 12px 20px;
  border-top: 1px solid var(--el-border-color);
  text-align: center;
}

.view-all-link {
  color: var(--el-color-primary);
  text-decoration: none;
  font-size: 14px;
  cursor: pointer;
}

.view-all-link:hover {
  text-decoration: underline;
}
</style>
