<template>
  <div class="user-management-container">
    <div class="page-header">
      <h1>{{ t('admin.user.title') }}</h1>
      <p>{{ t('admin.user.title_info') }}</p>
    </div>

    <el-divider></el-divider>

    <div class="manage-users-section">
      <div class="section-header">
        <h2 class="section-title">{{ t('admin.user.section_title') }}</h2>
        <div class="header-actions">
          <el-input v-model="searchKeyword" :placeholder="t('admin.user.search_placeholder')" clearable class="search-input" style="width: 300px">
            <template #prefix>
              <el-icon>
                <Search />
              </el-icon>
            </template>
          </el-input>
          <el-select v-model="statusFilter" :placeholder="t('admin.user.table.status')" clearable style="width: 150px" @change="loadUserList">
            <el-option :label="t('admin.user.status_filter.all')" value="" />
            <el-option :label="t('admin.user.status_filter.normal')" value="normal" />
            <el-option :label="t('admin.user.status_filter.disabled')" value="disabled" />
          </el-select>
        </div>
      </div>

      <div class="users-table-container">
        <!-- 移动端卡片布局 -->
        <template v-if="isMobile">
          <div v-loading="loading" class="mobile-users-container">
            <el-card v-for="user in filteredUsers" :key="user.id" class="mobile-user-card">
              <div class="user-card-header">
                <div class="user-info-main">
                  <el-avatar :src="user.profile_image || defaultAvatar" :size="50" />
                  <div class="user-details-main">
                    <div class="user-name-main">{{ user.full_name || user.username }}</div>
                    <div class="user-email-main">@{{ user.username }}</div>
                  </div>
                </div>
                <el-tag :class="`role-tag role-${user.role?.toLowerCase() || 'user'}`" size="small">
                  {{ getRoleName(user.role) }}
                </el-tag>
              </div>

              <div class="user-card-body">
                <div class="user-card-row">
                  <span class="row-label">{{ t('admin.user.table.email') }}:</span>
                  <span class="row-value">{{ user.email || '-' }}</span>
                </div>
                <div class="user-card-row">
                  <span class="row-label">{{ t('admin.user.table.status') }}:</span>
                  <el-select v-model="user.status" size="small" @change="handleStatusChange(user)">
                    <el-option :label="t('admin.user.status.normal')" value="normal"></el-option>
                    <el-option :label="t('admin.user.status.disabled')" value="disabled"></el-option>
                  </el-select>
                </div>
                <div class="user-card-row">
                  <span class="row-label">{{ t('admin.user.table.articles_count') }}:</span>
                  <span class="row-value">{{ user.articles_count || 0 }}</span>
                </div>
                <div class="user-card-row">
                  <span class="row-label">{{ t('admin.user.table.comments_count') }}:</span>
                  <span class="row-value">{{ user.comments_count || 0 }}</span>
                </div>
              </div>

              <template #footer>
                <div class="user-card-actions">
                  <el-button @click="handleViewUser(user)" size="small">
                    <IconifyIcon icon="pepicons-pencil:open" width="16" height="16" />
                  </el-button>
                  <el-button @click="handleSendMessage(user)" size="small">
                    <IconifyIcon icon="streamline-plump:mail-send-email-message" width="16" height="16" />
                  </el-button>
                  <el-dropdown trigger="click" @command="onDropdownCommand(user)">
                    <el-button size="small">
                      <el-icon><More /></el-icon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item command="editRole" v-if="user.id !== currentUserId">
                          <el-icon><Edit /></el-icon>
                          {{ t('admin.user.actions.edit_role') }}
                        </el-dropdown-item>
                        <el-dropdown-item command="resetPassword" v-if="user.id !== currentUserId">
                          <el-icon><Refresh /></el-icon>
                          {{ t('admin.user.actions.reset_password') }}
                        </el-dropdown-item>
                        <el-dropdown-item command="deleteUser" v-if="user.id !== currentUserId || user.id != 1" divided>
                          <el-icon><Delete /></el-icon>
                          {{ t('admin.user.actions.delete_user') }}
                        </el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </div>
              </template>
            </el-card>
          </div>
        </template>

        <!-- 桌面端表格布局 -->
        <el-table v-else :data="filteredUsers" v-loading="loading" class="users-table" border>
          <el-table-column prop="username" :label="t('admin.user.table.user')" width="280">
            <template #default="{ row }">
              <div class="user-info">
                <el-avatar :src="row.profile_image || defaultAvatar" :size="50" />
                <div class="user-details">
                  <div class="user-name">{{ row.full_name || row.username }}</div>
                  <div class="user-email">@{{ row.username }}</div>
                  <div class="user-register-time">{{ formatDate(row.created_at) }}</div>
                </div>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="email" :label="t('admin.user.table.email')" width="200">
            <template #default="{ row }">
              {{ row.email || '-' }}
            </template>
          </el-table-column>

          <el-table-column prop="role" :label="t('admin.user.table.role')" width="120">
            <template #default="{ row }">
              <el-tag :class="`role-tag role-${row.role?.toLowerCase() || 'user'}`">
                {{ getRoleName(row.role) }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="status" :label="t('admin.user.table.status')" width="120">
            <template #default="{ row }">
              <el-select v-model="row.status" size="small" @change="handleStatusChange(row)">
                <el-option :label="t('admin.user.status.normal')" value="normal"></el-option>
                <el-option :label="t('admin.user.status.disabled')" value="disabled"></el-option>
              </el-select>
            </template>
          </el-table-column>

          <el-table-column prop="articles_count" :label="t('admin.user.table.articles_count')" width="100">
            <template #default="{ row }">
              {{ row.articles_count || 0 }}
            </template>
          </el-table-column>

          <el-table-column prop="comments_count" :label="t('admin.user.table.comments_count')" width="100">
            <template #default="{ row }">
              {{ row.comments_count || 0 }}
            </template>
          </el-table-column>

          <el-table-column :label="t('admin.user.table.actions')" width="200" fixed="right">
            <template #default="{ row }">
              <el-button circle @click="handleViewUser(row)">
                <IconifyIcon icon="pepicons-pencil:open" color="#999999" />
              </el-button>
              <el-button circle type="default" @click="handleSendMessage(row)">
                <IconifyIcon icon="streamline-plump:mail-send-email-message" color="#000000" width="16" height="16" />
              </el-button>
              <el-dropdown trigger="click" @command="onDropdownCommand(row)">
                <el-button round text type="default" size="small">
                  <el-icon>
                    <More />
                  </el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="editRole" v-if="row.id !== currentUserId">
                      <el-icon>
                        <Edit />
                      </el-icon>
                      {{ t('admin.user.actions.edit_role') }}
                    </el-dropdown-item>
                    <el-dropdown-item command="resetPassword" v-if="row.id !== currentUserId">
                      <el-icon>
                        <Refresh />
                      </el-icon>
                      {{ t('admin.user.actions.reset_password') }}
                    </el-dropdown-item>
                    <el-dropdown-item command="deleteUser" v-if="row.id !== currentUserId || row.id != 1" divided>
                      <el-icon>
                        <Delete />
                      </el-icon>
                      {{ t('admin.user.actions.delete_user') }}
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-container">
          <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total"
            :page-sizes="[10, 20, 50, 100]" layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange" @current-change="handlePageChange" />
        </div>
      </div>
    </div>

    <!-- 用户详情抽屉 -->
    <el-drawer v-model="detailDrawerVisible" size="35%" placement="right" :title="t('admin.user.drawer.title')">
      <div v-if="selectedUser" class="user-detail-content">
        <div class="user-avatar-large">
          <el-avatar :src="selectedUser.profile_image || defaultAvatar" :size="100" />
        </div>
        <h3 class="user-name-large">{{ selectedUser.full_name || selectedUser.username }}</h3>
        <p class="user-username-large">@{{ selectedUser.username }}</p>

        <!-- 个人资料页链接 -->
        <div class="profile-link-section">
          <el-button type="primary" @click="openProfilePage(selectedUser.username)" link>
            <el-icon>
              <User />
            </el-icon>
            {{ t('admin.user.actions.view_profile') }}
          </el-button>
        </div>

        <el-divider />

        <div class="detail-section">
          <h4>{{ t('admin.user.detail_section.basic_info') }}</h4>
          <div class="info-row">
            <span class="info-label">{{ t('admin.user.detail_section.email') }}：</span>
            <span class="info-value">{{ selectedUser.email || '-' }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">{{ t('admin.user.detail_section.mobile') }}：</span>
            <span class="info-value">{{ selectedUser.mobile || '-' }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">{{ t('admin.user.detail_section.gender') }}：</span>
            <span class="info-value">{{ getGenderText(selectedUser.gender) }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">{{ t('admin.user.detail_section.register_time') }}：</span>
            <span class="info-value">{{ formatDate(selectedUser.created_at) }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">{{ t('admin.user.detail_section.status') }}：</span>
            <el-tag :type="selectedUser.status === 'normal' ? 'success' : 'danger'">
              {{ selectedUser.status === 'normal' ? t('admin.user.status.normal') : t('admin.user.status.disabled') }}
            </el-tag>
          </div>
        </div>

        <div class="detail-section">
          <h4>{{ t('admin.user.detail_section.statistics') }}</h4>
          <div class="info-row">
            <span class="info-label">{{ t('admin.user.detail_section.articles_count') }}：</span>
            <span class="info-value">{{ selectedUser.articles_count || 0 }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">{{ t('admin.user.detail_section.comments_count') }}：</span>
            <span class="info-value">{{ selectedUser.comments_count || 0 }}</span>
          </div>
        </div>

        <div class="detail-section">
          <h4>{{ t('admin.user.detail_section.bio') }}</h4>
          <p class="user-bio">{{ selectedUser.profile_bio || selectedUser.about || '-' }}</p>
        </div>
      </div>
    </el-drawer>

    <!-- 发送消息对话框 -->
    <el-dialog v-model="messageDialogVisible" :title="t('admin.user.message_dialog.title')" width="500px">
      <el-form :model="messageForm" label-width="80px">
        <el-form-item :label="t('admin.user.message_dialog.recipient')">
          <el-input :value="messageTargetUser?.full_name || messageTargetUser?.username" disabled />
        </el-form-item>
        <el-form-item :label="t('admin.user.message_dialog.message_type')">
          <el-select v-model="messageForm.type" style="width: 100%">
            <el-option :label="t('admin.user.message_dialog.type_system')" value="system" />
            <el-option :label="t('admin.user.message_dialog.type_reminder')" value="reminder" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('admin.user.message_dialog.title')">
          <el-input v-model="messageForm.title" :placeholder="t('admin.user.message_dialog.title_placeholder')" />
        </el-form-item>
        <el-form-item :label="t('admin.user.message_dialog.content')">
          <el-input v-model="messageForm.content" type="textarea" :rows="4" :placeholder="t('admin.user.message_dialog.content_placeholder')" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="messageDialogVisible = false">{{ t('admin.user.message_dialog.cancel') }}</el-button>
        <el-button type="primary" @click="handleSendMessageSubmit" :loading="sendingMessage">{{ t('admin.user.message_dialog.send') }}</el-button>
      </template>
    </el-dialog>

    <!-- 修改角色对话框 -->
    <el-dialog v-model="roleDialogVisible" :title="t('admin.user.role_dialog.title')" width="400px">
      <el-form label-width="80px">
        <el-form-item :label="t('admin.user.role_dialog.user')">
          <el-input :value="roleTargetUser?.full_name || roleTargetUser?.username" disabled />
        </el-form-item>
        <el-form-item :label="t('admin.user.role_dialog.role')">
          <el-select v-model="newRole" style="width: 100%">
            <el-option :label="t('admin.user.roles.Admin') + ' (Admin)'" value="Admin" />
            <el-option :label="t('admin.user.roles.Editor') + ' (Editor)'" value="Editor" />
            <el-option :label="t('admin.user.roles.Author') + ' (Author)'" value="Author" />
            <el-option :label="t('admin.user.roles.Contributor') + ' (Contributor)'" value="Contributor" />
            <el-option :label="t('admin.user.roles.User') + ' (User)'" value="User" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="roleDialogVisible = false">{{ t('admin.user.role_dialog.cancel') }}</el-button>
        <el-button type="primary" @click="handleRoleChangeSubmit">{{ t('admin.user.role_dialog.confirm') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  ArrowDown,
  Edit,
  Delete,
  Refresh,
  User,
  More
} from '@element-plus/icons-vue'
import IconifyIcon from '@/components/IconIfy.vue'
import { useAppStore } from '@/stores/app'
import { useMobileDetection } from '@/composables/useMobileDetection'
import * as userApi from '@/api/services/users'

const { t } = useI18n()
const appStore = useAppStore()

// 移动端检测
const { isMobile } = useMobileDetection()

// 数据状态
const users = ref<any[]>([])
const loading = ref(false)
const searchKeyword = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 抽屉和对话框状态
const detailDrawerVisible = ref(false)
const messageDialogVisible = ref(false)
const roleDialogVisible = ref(false)

// 选中的用户
const selectedUser = ref<any>(null)
const messageTargetUser = ref<any>(null)
const roleTargetUser = ref<any>(null)

// 表单数据
const messageForm = ref<{
  type: 'system' | 'reminder'
  title: string
  content: string
}>({
  type: 'system',
  title: '',
  content: ''
})
const newRole = ref<'Admin' | 'Editor' | 'Author' | 'Contributor' | 'User'>('User')
const sendingMessage = ref(false)

const defaultAvatar = '/src/assets/avatar.png'
const currentUserId = computed(() => appStore.userInfo?.id)

// 角色名称映射
const getRoleName = (role: string) => {
  const translated = t(`user.roles.${role}`)
  // 如果翻译结果和key相同（即找不到翻译），则返回原role
  return translated !== `user.roles.${role}` ? translated : role || 'User'
}

// 性别文本映射
const getGenderText = (gender: number | undefined) => {
  if (gender === 1) return t('admin.user.detail_section.gender_male')
  if (gender === 0) return t('admin.user.detail_section.gender_female')
  return t('admin.user.detail_section.gender_unknown')
}

// 状态文本映射
const getStatusText = (status: string) => {
  return status === 'normal' ? t('admin.user.status.normal') : t('admin.user.status.disabled')
}

// 过滤后的用户列表
const filteredUsers = computed(() => {
  let result = users.value

  // 状态筛选
  if (statusFilter.value) {
    result = result.filter(u => u.status === statusFilter.value)
  }

  // 关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(u =>
      u.username?.toLowerCase().includes(keyword) ||
      u.full_name?.toLowerCase().includes(keyword) ||
      u.email?.toLowerCase().includes(keyword)
    )
  }

  return result
})

// 加载用户列表
const loadUserList = async () => {
  loading.value = true
  try {
    const res = await userApi.getUserList({
      page: currentPage.value,
      page_size: pageSize.value
    })

    if (res.code === 1) {
      users.value = res.data.users || []
      total.value = res.data.total || 0
    } else {
      ElMessage.error(res.msg || t('admin.user.message.load_failed'))
    }
  } catch (error) {
    console.error('加载用户列表失败:', error)
    ElMessage.error(t('admin.user.message.load_failed'))
  } finally {
    loading.value = false
  }
}

// 格式化日期
const formatDate = (timestamp: any) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp * 1000)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

// 查看用户详情
const handleViewUser = (user: any) => {
  selectedUser.value = user
  detailDrawerVisible.value = true
}

// 打开个人资料页
const openProfilePage = (username: string) => {
  const baseUrl = window.location.origin
  window.open(`${baseUrl}/profile/${username}`, '_blank')
}

// 发送消息
const handleSendMessage = (user: any) => {
  messageTargetUser.value = user
  messageForm.value = {
    type: 'system',
    title: '',
    content: ''
  }
  messageDialogVisible.value = true
}

// 提交发送消息
const handleSendMessageSubmit = async () => {
  if (!messageForm.value.title || !messageForm.value.content) {
    ElMessage.warning(t('admin.user.message_dialog.warning'))
    return
  }

  sendingMessage.value = true
  try {
    const res = await userApi.sendUserMessage(messageTargetUser.value.id, {
      type: messageForm.value.type,
      title: messageForm.value.title,
      content: messageForm.value.content
    })

    if (res.code === 1) {
      ElMessage.success(t('admin.user.message.send_success'))
      messageDialogVisible.value = false
    } else {
      ElMessage.error(res.msg || t('admin.user.message.send_failed'))
    }
  } catch (error) {
    console.error('发送消息失败:', error)
    ElMessage.error(t('admin.user.message.send_failed'))
  } finally {
    sendingMessage.value = false
  }
}

// 修改状态
const handleStatusChange = async (user: any) => {
  try {
    const res = await userApi.updateUserStatus(user.id, {
      status: user.status
    })

    if (res.code === 1) {
      const statusText = getStatusText(user.status)
      ElMessage.success(t('admin.user.message.status_update_success', { username: user.username, status: statusText }))
    } else {
      // 恢复原状态
      user.status = user.status === 'normal' ? 'disabled' : 'normal'
      ElMessage.error(res.msg || t('admin.user.message.status_update_failed'))
    }
  } catch (error) {
    // 恢复原状态
    user.status = user.status === 'normal' ? 'disabled' : 'normal'
    console.error('状态更新失败:', error)
    ElMessage.error(t('admin.user.message.status_update_failed'))
  }
}

// 下拉菜单命令处理
const handleDropdownCommand = (user: any, command: string) => {
  switch (command) {
    case 'editRole':
      roleTargetUser.value = user
      newRole.value = user.role || 'User'
      roleDialogVisible.value = true
      break
    case 'resetPassword':
      handleResetPassword(user)
      break
    case 'deleteUser':
      handleDeleteUser(user)
      break
  }
}

// 为模板中的下拉菜单事件创建包装函数（不带类型注解用于模板）
const onDropdownCommand = (user: any) => {
  return (cmd: string) => handleDropdownCommand(user, cmd)
}

// 修改角色提交
const handleRoleChangeSubmit = async () => {
  try {
    const res = await userApi.updateUserRole(roleTargetUser.value.id, {
      role: newRole.value
    })

    if (res.code === 1) {
      ElMessage.success(t('admin.user.message.role_update_success'))
      // 更新本地数据
      const index = users.value.findIndex(u => u.id === roleTargetUser.value.id)
      if (index !== -1) {
        ; (users.value[index] as any).role = newRole.value
      }
      roleDialogVisible.value = false
    } else {
      ElMessage.error(res.msg || t('admin.user.message.role_update_failed'))
    }
  } catch (error) {
    console.error('角色修改失败:', error)
    ElMessage.error(t('admin.user.message.role_update_failed'))
  }
}

// 重置密码
const handleResetPassword = async (user: any) => {
  const userName = user.full_name || user.username
  ElMessageBox.confirm(
    t('admin.user.reset_password_confirm.message', { name: userName }),
    t('admin.user.reset_password_confirm.title'),
    {
      confirmButtonText: t('admin.user.reset_password_confirm.confirm'),
      cancelButtonText: t('admin.user.reset_password_confirm.cancel'),
      type: 'warning'
    }
  ).then(async () => {
    try {
      const res = await userApi.resetUserPassword(user.id)
      if (res.code === 1) {
        ElMessage.success(t('admin.user.message.password_reset_success'))
      } else {
        ElMessage.error(res.msg || t('admin.user.message.password_reset_failed'))
      }
    } catch (error) {
      console.error('密码重置失败:', error)
      ElMessage.error(t('admin.user.message.password_reset_failed'))
    }
  }).catch(() => {
    // 用户取消
  })
}

// 删除用户
const handleDeleteUser = async (user: any) => {
  const userName = user.full_name || user.username
  ElMessageBox.confirm(
    t('admin.user.delete_user_confirm.message', { name: userName }),
    t('admin.user.delete_user_confirm.title'),
    {
      confirmButtonText: t('admin.user.delete_user_confirm.confirm'),
      cancelButtonText: t('admin.user.delete_user_confirm.cancel'),
      type: 'warning'
    }
  ).then(async () => {
    try {
      const res = await userApi.deleteUser(user.id)
      if (res.code === 1) {
        ElMessage.success(t('admin.user.message.delete_success'))
        // 从列表中移除
        users.value = users.value.filter(u => u.id !== user.id)
        total.value--
      } else {
        ElMessage.error(res.msg || t('admin.user.message.delete_failed'))
      }
    } catch (error) {
      console.error('用户删除失败:', error)
      ElMessage.error(t('admin.user.message.delete_failed'))
    }
  }).catch(() => {
    // 用户取消
  })
}

// 分页处理
const handlePageChange = (page: number) => {
  currentPage.value = page
  loadUserList()
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  loadUserList()
}

// 初始化
onMounted(() => {
  loadUserList()
})
</script>

<style scoped>
.user-management-container {
  padding: 24px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 2rem;
  font-weight: 600;
  color: var(--wy-section-title-color);
}

.page-header p {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
}

.manage-users-section {
  margin-top: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--wy-section-title-color);
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.users-table-container {
  background-color: #fff;
  border-radius: 8px;
  overflow: hidden;
}

.users-table {
  width: 100%;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-name {
  font-weight: 500;
  color: #333;
}

.user-email {
  font-size: 12px;
  color: #666;
}

.user-register-time {
  font-size: 11px;
  color: #999;
}

.role-tag {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 12px;
}

.role-admin {
  background-color: #fef3c7;
  color: #d97706;
  border-color: #fef3c7;
}

.role-editor {
  background-color: #dbeafe;
  color: #2563eb;
  border-color: #bfdbfe;
}

.role-author {
  background-color: #f3e8ff;
  color: #7c3aed;
  border-color: #ddd6fe;
}

.role-contributor {
  background-color: #e0e7ff;
  color: #4f46e5;
  border-color: #c7d2fe;
}

.role-user {
  background-color: #f3f4f6;
  color: #6b7280;
  border-color: #e5e7eb;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  padding: 16px;
  background-color: #fff;
  border-top: 1px solid #e5e7eb;
}

/* 用户详情抽屉样式 */
.user-detail-content {
  padding: 20px;
}

.user-avatar-large {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.user-name-large {
  text-align: center;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.user-username-large {
  text-align: center;
  color: #666;
  margin-bottom: 12px;
}

.profile-link-section {
  text-align: center;
  margin-bottom: 20px;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section h4 {
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 12px 0;
  color: #333;
}

.info-row {
  display: flex;
  margin-bottom: 12px;
}

.info-label {
  width: 80px;
  color: #666;
}

.info-value {
  flex: 1;
  color: #333;
}

.user-bio {
  color: #666;
  line-height: 1.6;
  margin: 0;
}

/* 移动端适配 */
@media (max-width: 767px) {
  .section-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .header-actions .search-input,
  .header-actions .el-select {
    width: 100% !important;
  }

  /* 移动端用户卡片 */
  .mobile-users-container {
    padding: 0;
  }

  .mobile-user-card {
    margin-bottom: 12px;
    border-radius: 8px;
  }

  .mobile-user-card :deep(.el-card__body) {
    padding: 16px;
  }

  .user-card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--el-border-color-lighter);
  }

  .user-info-main {
    display: flex;
    gap: 12px;
    align-items: center;
  }

  .user-details-main {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .user-name-main {
    font-size: 16px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .user-email-main {
    font-size: 14px;
    color: var(--el-text-color-secondary);
  }

  .user-card-body {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .user-card-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 14px;
  }

  .user-card-row .row-label {
    color: var(--el-text-color-secondary);
    flex-shrink: 0;
  }

  .user-card-row .row-value {
    color: var(--el-text-color-primary);
    text-align: right;
  }

  .user-card-actions {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
  }

  /* 抽屉宽度优化 */
  .el-drawer {
    width: 100% !important;
  }

  /* 对话框宽度优化 */
  .el-dialog {
    width: 95% !important;
  }

  /* 分页优化 */
  .pagination-container :deep(.el-pagination__sizes),
  .pagination-container :deep(.el-pagination__jump) {
    display: none;
  }
}
</style>
