<template>
  <div class="admin-settings">
    <h1>{{ t('admin.settings.title') }}</h1>
    <el-card class="settings-card">
      <el-tabs v-model="activeTab">
        <!-- 基础设置 -->
        <el-tab-pane :label="t('admin.settings.tabs.basic')" name="basic">
          <el-form ref="formRef" :model="formState" :label-width="formLabelConfig.labelWidth"
            :label-position="formLabelConfig.labelPosition" class="settings-form">
            <el-form-item :label="t('admin.settings.basic.site_title')">
              <el-input v-model="formState.siteTitle" :placeholder="t('admin.settings.basic.site_title_placeholder')" />
            </el-form-item>
            <el-form-item :label="t('admin.settings.basic.site_logo')">
              <el-upload class="upload-wrapper" drag :http-request="handleSiteLogoUpload"
                :before-upload="beforeLogoUpload" :show-file-list="false"
                accept="image/png,image/jpeg,image/svg+xml,image/vnd.microsoft.icon,image/x-icon">
                <template v-if="!isUploading && !formState.siteLogo">
                  <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                  <div class="el-upload__text" v-html="t('admin.settings.upload.drop_text')"></div>
                </template>
                <template v-if="isUploading">
                  <div style="text-align: center; padding: 20px 0">
                    <el-progress :percentage="uploadProgress" :stroke-width="2"
                      style="width: 200px; margin: 0 auto 10px"></el-progress>
                    <span>{{ uploadProgress }}%</span>
                  </div>
                </template>
                <template v-if="formState.siteLogo">
                  <div class="cover-image-wrapper">
                    <img :src="formState.siteLogo" alt="Site Logo" class="cover-image" />
                    <el-button :icon="Delete" class="delete-cover-btn" @click="removeImage('siteLogo')" />
                  </div>
                </template>
                <template #tip>
                  <div class="el-upload__tip">{{ t('admin.settings.basic.upload_logo_tip') }}</div>
                </template>
              </el-upload>
            </el-form-item>
            <el-form-item :label="t('admin.settings.basic.favicon')">
              <el-upload class="upload-wrapper" drag :http-request="handleFaviconUpload"
                :before-upload="beforeFaviconUpload" :show-file-list="false"
                accept="image/x-icon,image/vnd.microsoft.icon,image/png,image/svg+xml">
                <template v-if="!isUploading && !formState.favicon">
                  <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                  <div class="el-upload__text" v-html="t('admin.settings.upload.drop_text')"></div>
                </template>
                <template v-if="isUploading">
                  <div style="text-align: center; padding: 20px 0">
                    <el-progress :percentage="uploadProgress" :stroke-width="2"
                      style="width: 200px; margin: 0 auto 10px"></el-progress>
                    <span>{{ uploadProgress }}%</span>
                  </div>
                </template>
                <template v-if="formState.favicon">
                  <div class="cover-image-wrapper">
                    <img :src="formState.favicon" alt="favicon" class="cover-image" />
                    <el-button :icon="Delete" class="delete-cover-btn" @click="removeImage('favicon')" />
                  </div>
                </template>
                <template #tip>
                  <div class="el-upload__tip">{{ t('admin.settings.basic.upload_favicon_tip') }}</div>
                </template>
              </el-upload>
            </el-form-item>
            <!-- <el-form-item label="每页显示数量">
          <el-input-number v-model="formState.pageSize" :min="10" :max="100" :step="5" />
        </el-form-item> -->
            <el-form-item :label="t('admin.settings.basic.disable_comments')">
              <div class="form-item">
                <el-switch v-model="formState.disableComments" />
                <p class="form-hint">{{ t('admin.settings.basic.disable_comments_hint') }}</p>
              </div>
            </el-form-item>
            <el-form-item :label="t('admin.settings.basic.disable_doc_comments')">
              <div class="form-item">
                <el-switch v-model="formState.disableDocComments" />
                <p class="form-hint">{{ t('admin.settings.basic.disable_doc_comments_hint') }}</p>
              </div>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSubmit">{{ t('admin.settings.basic.save') }}</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 消息推送配置 -->
        <el-tab-pane :label="t('admin.settings.tabs.message')" name="message">
          <el-form ref="messageFormRef" :model="messageFormState" :label-width="messageFormLabelConfig.labelWidth"
            :label-position="messageFormLabelConfig.labelPosition" class="settings-form">
            <el-form-item :label="t('admin.settings.message.push_method')">
              <el-radio-group v-model="messageFormState.pushMethod">
                <el-radio value="websocket">
                  <div class="radio-option">
                    <span class="option-title">{{ t('admin.settings.message.method_websocket') }}</span>
                    <p class="option-desc">{{ t('admin.settings.message.method_websocket_desc') }}</p>
                  </div>
                </el-radio>
                <el-radio value="polling">
                  <div class="radio-option">
                    <span class="option-title">{{ t('admin.settings.message.method_polling') }}</span>
                    <p class="option-desc">{{ t('admin.settings.message.method_polling_desc') }}</p>
                  </div>
                </el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item v-if="messageFormState.pushMethod === 'polling'"
              :label="t('admin.settings.message.polling_interval')">
              <el-input-number v-model="messageFormState.pollingInterval" :min="10" :max="300" :step="10"
                controls-position="right" />
              <span class="unit-text">{{ t('admin.settings.message.polling_interval_unit') }}</span>
              <p class="form-hint">{{ t('admin.settings.message.polling_interval_hint') }}</p>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="handleMessageSubmit">{{ t('admin.settings.message.save_message')
                }}</el-button>
              <el-button v-if="messageFormState.pushMethod === 'websocket'" @click="testWebSocketConnection"
                :loading="isTesting">
                {{ t('admin.settings.message.test_connection') }}
              </el-button>
              <el-button v-if="isConnected && messageFormState.pushMethod === 'websocket'" @click="sendTestMessage"
                type="success">
                {{ t('admin.settings.message.send_test_message') }}
              </el-button>
            </el-form-item>

            <el-divider />

            <div class="connection-status">
              <h4>{{ t('admin.settings.message.connection_status') }}</h4>
              <el-tag :type="isConnected ? 'success' : 'info'">
                {{ isConnected ? t('admin.settings.message.connected') : t('admin.settings.message.disconnected') }}
              </el-tag>
              <p class="form-hint" v-if="messageFormState.pushMethod === 'websocket'">
                {{ t('admin.settings.message.connection_hint') }}
              </p>
              <p class="form-hint" v-if="wsUrl">
                {{ t('admin.settings.message.ws_url_label') }} <code>{{ wsUrl }}</code>
              </p>
            </div>
          </el-form>
        </el-tab-pane>

        <!-- 文章审核通知配置 -->
        <el-tab-pane :label="t('admin.settings.tabs.notification')" name="notification">
          <div class="notification-config-section">
            <div class="section-header">
              <h3>{{ t('admin.settings.notification.section_title') }}</h3>
              <p class="section-desc">{{ t('admin.settings.notification.section_desc') }}</p>
            </div>

            <el-form ref="notificationFormRef" :model="notificationFormState"
              :label-width="notificationFormLabelConfig.labelWidth"
              :label-position="notificationFormLabelConfig.labelPosition" class="settings-form">
              <el-form-item :label="t('admin.settings.notification.enable_review')">
                <div class="form-item">
                  <el-switch v-model="notificationFormState.enableArticleReviewNotification" />
                  <p class="form-hint">{{ t('admin.settings.notification.enable_review_hint') }}</p>
                </div>
              </el-form-item>

              <el-form-item :label="t('admin.settings.notification.notify_roles')">
                <el-checkbox-group v-model="notificationFormState.notifyRoles">
                  <el-checkbox value="Admin">{{ t('admin.settings.notification.role_admin') }}</el-checkbox>
                  <el-checkbox value="Editor">{{ t('admin.settings.notification.role_editor') }}</el-checkbox>
                </el-checkbox-group>
                <p class="form-hint">{{ t('admin.settings.notification.notify_roles_hint') }}</p>
              </el-form-item>

              <el-form-item>
                <el-button type="primary" @click="handleNotificationSubmit">{{ t('admin.settings.notification.save')
                  }}</el-button>
              </el-form-item>
            </el-form>

            <el-divider />

            <div class="info-box">
              <h4>{{ t('admin.settings.notification.info_title') }}</h4>
              <p>{{ t('admin.settings.notification.info_content') }}</p>
            </div>
          </div>
        </el-tab-pane>

        <!-- 邮件配置 -->
        <el-tab-pane :label="t('admin.settings.tabs.email')" name="email">
          <div class="email-config-section">
            <div class="section-header">
              <h3>{{ t('admin.settings.email.section_title') }}</h3>
              <p class="section-desc">{{ t('admin.settings.email.section_desc') }}</p>
            </div>

            <!-- 桌面端表格 -->
            <el-table v-if="!isMobile" :data="emailSettingsList" border style="margin-top: 20px">
              <el-table-column prop="provider" :label="t('admin.settings.email.table.provider')" width="120">
                <template #default="{ row }">
                  <el-tag>{{ t('admin.settings.providers.' + row.provider.toLowerCase()) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="smtp_host" :label="t('admin.settings.email.table.smtp_host')" width="200" />
              <el-table-column prop="smtp_port" :label="t('admin.settings.email.table.port')" width="80" />
              <el-table-column prop="from_email" :label="t('admin.settings.email.table.from_email')" width="180" />
              <el-table-column prop="from_name" :label="t('admin.settings.email.table.from_name')" width="120" />
              <el-table-column prop="is_active" :label="t('admin.settings.email.table.status')" width="80">
                <template #default="{ row }">
                  <el-tag :type="row.is_active ? 'success' : 'info'">
                    {{ row.is_active ? t('admin.settings.email.table.enabled') :
                      t('admin.settings.email.table.disabled')
                    }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column :label="t('admin.settings.email.table.config_status')" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.has_password ? 'success' : 'warning'">
                    {{ row.has_password ? t('admin.settings.email.table.configured') :
                      t('admin.settings.email.table.not_configured') }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column :label="t('admin.settings.email.table.actions')" width="100">
                <template #default="{ row }">
                  <el-button size="small" type="primary" @click="handleEditEmailSettings(row)">
                    {{ row.has_password ? t('admin.settings.email.table.edit') :
                      t('admin.settings.email.table.configure')
                    }}
                  </el-button>
                </template>
              </el-table-column>
            </el-table>

            <!-- 移动端卡片 -->
            <div v-else class="email-settings-cards">
              <el-card v-for="row in emailSettingsList" :key="row.id" class="email-setting-card" shadow="hover">
                <div class="card-header">
                  <el-tag>{{ t('admin.settings.providers.' + row.provider.toLowerCase()) }}</el-tag>
                  <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
                    {{ row.is_active ? t('admin.settings.email.table.enabled') :
                      t('admin.settings.email.table.disabled')
                    }}
                  </el-tag>
                </div>
                <div class="card-body">
                  <div class="info-row">
                    <span class="label">{{ t('admin.settings.email.table.smtp_host') }}:</span>
                    <span class="value">{{ row.smtp_host }}</span>
                  </div>
                  <div class="info-row">
                    <span class="label">{{ t('admin.settings.email.table.port') }}:</span>
                    <span class="value">{{ row.smtp_port }}</span>
                  </div>
                  <div class="info-row">
                    <span class="label">{{ t('admin.settings.email.table.from_email') }}:</span>
                    <span class="value">{{ row.from_email }}</span>
                  </div>
                  <div class="info-row">
                    <span class="label">{{ t('admin.settings.email.table.from_name') }}:</span>
                    <span class="value">{{ row.from_name || '-' }}</span>
                  </div>
                  <div class="info-row">
                    <span class="label">{{ t('admin.settings.email.table.config_status') }}:</span>
                    <el-tag :type="row.has_password ? 'success' : 'warning'" size="small">
                      {{ row.has_password ? t('admin.settings.email.table.configured') :
                        t('admin.settings.email.table.not_configured') }}
                    </el-tag>
                  </div>
                </div>
                <div class="card-footer">
                  <el-button type="primary" size="small" @click="handleEditEmailSettings(row)">
                    {{ row.has_password ? t('admin.settings.email.table.edit') :
                      t('admin.settings.email.table.configure')
                    }}
                  </el-button>
                </div>
              </el-card>

              <el-empty v-if="!emailSettingsLoading && emailSettingsList.length === 0"
                :description="t('admin.settings.email.empty')" />
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 邮件配置表单对话框 -->
    <el-dialog v-model="emailFormVisible"
      :title="editingEmailSettings ? t('admin.settings.email.dialog.edit_title') : t('admin.settings.email.dialog.add_title')"
      :width="isMobile ? '95%' : '600px'">
      <el-form :model="emailForm" :label-width="emailFormLabelConfig.labelWidth"
        :label-position="emailFormLabelConfig.labelPosition">
        <el-form-item :label="t('admin.settings.email.dialog.provider')">
          <el-select v-model="emailForm.provider" @change="handleProviderChange">
            <el-option :label="t('admin.settings.providers.gmail')" value="gmail" />
            <el-option :label="t('admin.settings.providers.outlook')" value="outlook" />
            <el-option :label="t('admin.settings.providers.qq')" value="qq" />
            <el-option :label="t('admin.settings.providers.163')" value="163" />
            <el-option :label="t('admin.settings.providers.custom')" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('admin.settings.email.dialog.smtp_host')">
          <el-input v-model="emailForm.smtp_host"
            :placeholder="t('admin.settings.email.dialog.smtp_host_placeholder')" />
        </el-form-item>
        <el-form-item :label="t('admin.settings.email.dialog.port')">
          <el-input-number v-model="emailForm.smtp_port" :min="1" :max="65535" />
        </el-form-item>
        <el-form-item :label="t('admin.settings.email.dialog.smtp_user')">
          <el-input v-model="emailForm.smtp_user"
            :placeholder="t('admin.settings.email.dialog.smtp_user_placeholder')" />
        </el-form-item>
        <el-form-item :label="t('admin.settings.email.dialog.smtp_pass')">
          <el-input v-model="emailForm.smtp_pass" type="password"
            :placeholder="editingEmailSettings?.has_password ? t('admin.settings.email.dialog.smtp_pass_edit_placeholder') : t('admin.settings.email.dialog.smtp_pass_placeholder')"
            show-password />
          <p v-if="editingEmailSettings?.has_password" class="form-hint">{{
            t('admin.settings.email.dialog.smtp_pass_hint')
            }}</p>
        </el-form-item>
        <el-form-item :label="t('admin.settings.email.dialog.from_email')">
          <el-input v-model="emailForm.from_email"
            :placeholder="t('admin.settings.email.dialog.from_email_placeholder')" />
        </el-form-item>
        <el-form-item :label="t('admin.settings.email.dialog.from_name')">
          <el-input v-model="emailForm.from_name"
            :placeholder="t('admin.settings.email.dialog.from_name_placeholder')" />
        </el-form-item>
        <el-form-item :label="t('admin.settings.email.dialog.use_tls')">
          <el-switch v-model="emailForm.use_tls" />
        </el-form-item>
        <el-form-item :label="t('admin.settings.email.dialog.is_active')">
          <el-switch v-model="emailForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="emailFormVisible = false">{{ t('admin.settings.email.dialog.btn_cancel') }}</el-button>
        <el-button type="primary" @click="handleEmailFormSubmit">{{ t('admin.settings.email.dialog.btn_confirm')
          }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { FormInstance } from 'element-plus'
import { ElMessage } from 'element-plus'
import { uploadFile } from '@/api/services/common'
import { getSiteConfig, updateSiteConfig } from '@/api/services/siteconfig'
import { getEmailSettings, updateEmailSettings } from '@/api/services/memberInvitations'
import { Delete } from '@element-plus/icons-vue'
import { useAppStore } from '@/stores/app'
import { wsService } from '@/api/services/websocket'
import { useMobileDetection } from '@/composables/useMobileDetection'

const appStore = useAppStore()
const { t } = useI18n()

// 移动端检测
const { isMobile } = useMobileDetection()

// 响应式表单标签配置
const formLabelConfig = computed(() => ({
  labelWidth: isMobile.value ? 'auto' : '120px',
  labelPosition: isMobile.value ? 'top' : 'right'
}))

const messageFormLabelConfig = computed(() => ({
  labelWidth: isMobile.value ? 'auto' : '140px',
  labelPosition: isMobile.value ? 'top' : 'right'
}))

const notificationFormLabelConfig = computed(() => ({
  labelWidth: isMobile.value ? 'auto' : '160px',
  labelPosition: isMobile.value ? 'top' : 'right'
}))

const emailFormLabelConfig = computed(() => ({
  labelWidth: isMobile.value ? 'auto' : '120px',
  labelPosition: isMobile.value ? 'top' : 'right'
}))

const formRef = ref<FormInstance>()
const messageFormRef = ref<FormInstance>()
const notificationFormRef = ref<FormInstance>()
const formState = reactive({
  siteTitle: 'WOW Blog',
  siteLogo: '',
  favicon: '',
  pageSize: 20,
  disableComments: false,
  disableDocComments: false
})

// 消息推送配置状态
const messageFormState = reactive({
  pushMethod: 'websocket',
  pollingInterval: 30
})

// 文章审核通知配置状态
const notificationFormState = reactive({
  enableArticleReviewNotification: false,
  notifyRoles: [] as string[]
})

// WebSocket 连接状态 - 实际监听 WebSocket 服务
const isConnected = ref(false)
const isTesting = ref(false)
const wsUrl = ref('')

// WebSocket 连接状态处理器
const handleConnected = () => {
  isConnected.value = true
  console.log('[SettingsView] WebSocket 已连接')
  ElMessage.success(t('admin.settings.message_tip.ws_connect_success'))
}

const handleReconnecting = () => {
  isConnected.value = false
  console.log('[SettingsView] WebSocket 重连中')
}

const handleDisconnected = () => {
  isConnected.value = false
  console.log('[SettingsView] WebSocket 已断开')
}

// 测试 WebSocket 连接
const testWebSocketConnection = async () => {
  isTesting.value = true

  try {
    // 直接连接到后端地址（因为前端没有配置代理）
    // 假设后端运行在 localhost:8000
    const backendUrl = 'localhost:8000'
    wsUrl.value = `ws://${backendUrl}/api/ws/messages`

    console.log('[SettingsView] 测试 WebSocket 连接:', wsUrl.value)

    // 获取 token
    const token = appStore.token || localStorage.getItem('access_token')
    if (!token) {
      ElMessage.error(t('admin.settings.message_tip.token_not_found'))
      isTesting.value = false
      return
    }

    // 断开现有连接
    wsService.disconnect()

    // 等待一秒确保断开完成
    await new Promise(resolve => setTimeout(resolve, 500))

    // 注册事件监听（一次性）
    const onConnected = () => {
      isConnected.value = true
      isTesting.value = false
      ElMessage.success(t('admin.settings.message_tip.ws_connect_success'))
      wsService.off('connected', onConnected)
    }

    const onError = () => {
      isConnected.value = false
      isTesting.value = false
      ElMessage.error(t('admin.settings.message_tip.ws_connect_failed'))
      wsService.off('max_reconnect_reached', onError)
    }

    wsService.on('connected', onConnected)
    wsService.on('max_reconnect_reached', onError)

    // 连接
    wsService.connect(wsUrl.value, token)

    // 5秒后检查状态
    setTimeout(() => {
      if (isTesting.value) {
        isTesting.value = false
        if (!isConnected.value) {
          ElMessage.error(t('admin.settings.message_tip.ws_connect_timeout'))
        }
        wsService.off('connected', onConnected)
        wsService.off('max_reconnect_reached', onError)
      }
    }, 5000)
  } catch (error) {
    isTesting.value = false
    console.error('WebSocket 连接测试失败:', error)
    ElMessage.error(t('admin.settings.message_tip.ws_test_failed'))
  }
}

// 发送测试消息
const sendTestMessage = () => {
  try {
    wsService.send({
      type: 'echo',
      data: {
        message: '这是一条测试消息',
        timestamp: new Date().toISOString()
      }
    })
    ElMessage.success(t('admin.settings.message_tip.test_message_sent'))

    // 监听回显消息（一次性）
    const onEcho = (data: any) => {
      console.log('[SettingsView] 收到回显消息:', data)
      ElMessage.success(`收到回显: ${JSON.stringify(data)}`)
      wsService.off('echo_response', onEcho)
    }
    wsService.on('echo_response', onEcho)
  } catch (error) {
    console.error('发送测试消息失败:', error)
    ElMessage.error(t('admin.settings.message_tip.test_message_failed'))
  }
}

// 当前激活的 tab
const activeTab = ref('basic')

// 邮件配置相关状态
const emailSettingsList = ref<any[]>([])
const emailSettingsLoading = ref(false)
const emailFormVisible = ref(false)
const editingEmailSettings = ref<any>(null)
const emailForm = ref({
  provider: 'gmail',
  smtp_host: 'smtp.gmail.com',
  smtp_port: 587,
  smtp_user: '',
  smtp_pass: '',
  from_email: '',
  from_name: '',
  use_tls: true,
  is_active: true
})

// 初始化时获取网站配置
onMounted(async () => {
  try {
    const res = await getSiteConfig()
    if (res.code === 1) {
      formState.siteTitle = res.data.site_title
      formState.siteLogo = res.data.site_logo
      formState.favicon = res.data.site_favicon
      formState.disableComments = res.data.disable_comment
      // doc_comment: 0=禁用, 1=开启; 前端switch是"是否禁用"，需要反转
      formState.disableDocComments = res.data.doc_comment === 0

      // 加载消息推送配置
      if (res.data.message_push_method) {
        messageFormState.pushMethod = res.data.message_push_method
      }
      if (res.data.polling_interval) {
        messageFormState.pollingInterval = res.data.polling_interval
      }

      // 加载文章审核通知配置
      if (res.data.enable_article_review_notification !== undefined) {
        notificationFormState.enableArticleReviewNotification = res.data.enable_article_review_notification === 1
      }
      if (res.data.article_review_notification_roles) {
        try {
          notificationFormState.notifyRoles = JSON.parse(res.data.article_review_notification_roles)
        } catch (e) {
          notificationFormState.notifyRoles = []
        }
      }
    }
  } catch (error) {
    console.error('获取网站配置失败:', error)
  }

  // 注册 WebSocket 事件监听
  wsService.on('connected', handleConnected)
  wsService.on('reconnecting', handleReconnecting)
  wsService.on('max_reconnect_reached', handleDisconnected)

  // 更新初始连接状态
  isConnected.value = wsService.isConnected()
})

// 组件卸载时清理
onUnmounted(() => {
  wsService.off('connected', handleConnected)
  wsService.off('reconnecting', handleReconnecting)
  wsService.off('max_reconnect_reached', handleDisconnected)
})

const handleSubmit = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
    const data = {
      site_title: formState.siteTitle,
      site_logo: formState.siteLogo,
      site_favicon: formState.favicon,
      disable_comment: formState.disableComments,
      // doc_comment: 0=禁用, 1=开启; 前端switch是"是否禁用"，需要反转
      doc_comment: formState.disableDocComments ? 0 : 1
    }
    const res = await updateSiteConfig(data)
    if (res.code === 1) {
      ElMessage.success(t('admin.settings.message_tip.save_success'))
      // 刷新 appStore 中的站点配置
      await appStore.fetchSiteConfig()
    } else {
      ElMessage.error(res.msg || t('admin.settings.message_tip.save_failed'))
    }
  } catch (err) {
    console.error('保存失败:', err)
  }
}

// 保存消息推送设置
const handleMessageSubmit = async () => {
  try {
    const data = {
      message_push_method: messageFormState.pushMethod,
      polling_interval: messageFormState.pollingInterval
    }
    const res = await updateSiteConfig(data)
    if (res.code === 1) {
      ElMessage.success(t('admin.settings.message_tip.message_save_success'))
      ElMessage.info(t('admin.settings.message_tip.message_save_hint'))

      // 刷新 appStore 中的站点配置
      await appStore.fetchSiteConfig()
    } else {
      ElMessage.error(res.msg || t('admin.settings.message_tip.message_save_failed'))
    }
  } catch (err) {
    console.error('保存消息推送设置失败:', err)
    ElMessage.error(t('admin.settings.message_tip.message_save_failed'))
  }
}

// 保存文章审核通知设置
const handleNotificationSubmit = async () => {
  try {
    const data = {
      enable_article_review_notification: notificationFormState.enableArticleReviewNotification ? 1 : 0,
      article_review_notification_roles: JSON.stringify(notificationFormState.notifyRoles)
    }
    const res = await updateSiteConfig(data)
    if (res.code === 1) {
      ElMessage.success(t('admin.settings.notification.save_success'))
      // 刷新 appStore 中的站点配置
      await appStore.fetchSiteConfig()
    } else {
      ElMessage.error(res.msg || t('admin.settings.notification.save_failed'))
    }
  } catch (err) {
    console.error('保存文章审核通知设置失败:', err)
    ElMessage.error(t('admin.settings.notification.save_failed'))
  }
}

// 上传进度
const uploadProgress = ref(0)
const isUploading = ref(false)

// 上传前验证 - Logo（支持 SVG、ICO）
const beforeLogoUpload = (file: File) => {
  const validTypes = [
    'image/jpeg',
    'image/png',
    'image/svg+xml',
    'image/vnd.microsoft.icon',
    'image/x-icon'
  ]
  const isValidType = validTypes.includes(file.type)
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isValidType) {
    ElMessage.error(t('admin.settings.message_tip.logo_format_error'))
    return false
  }
  if (!isLt2M) {
    ElMessage.error(t('admin.settings.message_tip.logo_size_error'))
    return false
  }
  return true
}

// 上传前验证 - Favicon（主要是 ICO）
const beforeFaviconUpload = (file: File) => {
  const validTypes = [
    'image/x-icon',
    'image/vnd.microsoft.icon',
    'image/png',
    'image/svg+xml'
  ]
  const isValidType = validTypes.includes(file.type)
  const isLt1M = file.size / 1024 / 1024 < 1

  if (!isValidType) {
    ElMessage.error(t('admin.settings.message_tip.favicon_format_error'))
    return false
  }
  if (!isLt1M) {
    ElMessage.error(t('admin.settings.message_tip.favicon_size_error'))
    return false
  }
  return true
}

// 上传网站Logo
const handleSiteLogoUpload = async (options: any) => {
  isUploading.value = true
  uploadProgress.value = 0

  try {
    const res = await uploadFile({
      file: options.file,
      onProgress: (progressEvent) => {
        if (progressEvent.total > 0) {
          const percent = Math.round((progressEvent.loaded / progressEvent.total) * 100)
          uploadProgress.value = percent
          options.onProgress({ percent })
        }
      }
    })

    if (res.code === 1 && res.data) {
      formState.siteLogo = res.data.full_url || res.data.url || ''
      ElMessage.success(t('admin.settings.message_tip.logo_upload_success'))
    } else {
      ElMessage.error(res.msg || t('admin.settings.message_tip.upload_failed'))
    }
  } catch (error) {
    ElMessage.error(t('admin.settings.message_tip.upload_failed'))
  } finally {
    isUploading.value = false
  }
}

// 上传Favicon
const handleFaviconUpload = async (options: any) => {
  isUploading.value = true
  uploadProgress.value = 0

  try {
    const res = await uploadFile({
      file: options.file,
      onProgress: (progressEvent) => {
        if (progressEvent.total > 0) {
          const percent = Math.round((progressEvent.loaded / progressEvent.total) * 100)
          uploadProgress.value = percent
          options.onProgress({ percent })
        }
      }
    })

    if (res.code === 1 && res.data) {
      formState.favicon = res.data.full_url || res.data.url || ''
      ElMessage.success(t('admin.settings.message_tip.favicon_upload_success'))
    } else {
      ElMessage.error(res.msg || t('admin.settings.message_tip.upload_failed'))
    }
  } catch (error) {
    ElMessage.error(t('admin.settings.message_tip.upload_failed'))
  } finally {
    isUploading.value = false
  }
}

// 移除封面图片
const removeImage = (type: string) => {
  if (type in formState && type === 'siteLogo') {
    formState.siteLogo = ''
  } else if (type in formState && type === 'favicon') {
    formState.favicon = ''
  }
}

// 邮件配置相关方法
const loadEmailSettings = async () => {
  emailSettingsLoading.value = true
  try {
    const res = await getEmailSettings()
    if (res.code === 1) {
      emailSettingsList.value = res.data || []
    }
  } catch (error) {
    ElMessage.error(t('admin.settings.message_tip.email_load_failed'))
  } finally {
    emailSettingsLoading.value = false
  }
}

const handleEditEmailSettings = (settings: any) => {
  editingEmailSettings.value = settings
  emailForm.value = {
    provider: settings.provider,
    smtp_host: settings.smtp_host,
    smtp_port: settings.smtp_port,
    smtp_user: settings.smtp_user || settings.smtpUser || '', // 后端API可能不返回此字段
    smtp_pass: '', // 密码不回显，出于安全考虑
    from_email: settings.from_email,
    from_name: settings.from_name || '',
    use_tls: settings.use_tls,
    is_active: settings.is_active
  }
  emailFormVisible.value = true
}

const handleEmailFormSubmit = async () => {
  if (!editingEmailSettings.value) {
    ElMessage.error(t('admin.settings.message_tip.invalid_operation'))
    return
  }

  try {
    // 如果密码为空且原配置有密码，则不更新密码字段
    const { smtp_pass, ...submitDataBase } = emailForm.value
    const submitData = (!smtp_pass && editingEmailSettings.value.has_password)
      ? submitDataBase
      : { ...emailForm.value }

    const res = await updateEmailSettings(editingEmailSettings.value.id, submitData)
    if (res.code === 1) {
      ElMessage.success(t('admin.settings.message_tip.email_update_success'))
      emailFormVisible.value = false
      loadEmailSettings()
    } else {
      ElMessage.error(res.msg || t('admin.settings.message_tip.email_update_failed'))
    }
  } catch (error) {
    console.error('保存邮件配置失败:', error)
    ElMessage.error(t('admin.settings.message_tip.operation_failed'))
  }
}

const handleProviderChange = (provider: string) => {
  const presets: Record<string, any> = {
    gmail: { smtp_host: 'smtp.gmail.com', smtp_port: 587 },
    outlook: { smtp_host: 'smtp.office365.com', smtp_port: 587 },
    qq: { smtp_host: 'smtp.qq.com', smtp_port: 587 },
    '163': { smtp_host: 'smtp.163.com', smtp_port: 465 }
  }
  if (presets[provider]) {
    emailForm.value.smtp_host = presets[provider].smtp_host
    emailForm.value.smtp_port = presets[provider].smtp_port
  }
}

// 监听 tab 切换，加载邮件配置
import { watch } from 'vue'
watch(activeTab, (newTab) => {
  if (newTab === 'email') {
    loadEmailSettings()
  }
})
</script>

<style scoped>
.admin-settings {
  padding: 20px;
}

.settings-card {
  max-width: 100%;
}

.settings-form {
  padding: 20px;
}

.form-item {
  display: flex;
  flex-direction: column;
}

.form-hint {
  font-size: 14px;
  color: #999999;
}

.upload-wrapper {
  position: relative;
  width: 100%;
  margin-top: 1rem;
}

.cover-image-wrapper {
  position: relative;
  display: inline-block;
  margin-bottom: 15px;
  width: 100%;
}

.cover-image {
  width: 100%;
  max-height: 200px;
  object-fit: contain;
  border-radius: 8px;
}

.delete-cover-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
}

.delete-cover-btn:hover {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: rgba(0, 0, 0, 0.8);
  color: white;
}

.email-config-section {
  padding: 20px;
}

/* 邮件设置卡片样式 */
.email-settings-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 20px;
}

.email-setting-card {
  margin: 0;
}

.email-setting-card .card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.email-setting-card .card-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.email-setting-card .info-row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 13px;
}

.email-setting-card .info-row .label {
  color: var(--el-text-color-secondary);
  min-width: 80px;
  flex-shrink: 0;
}

.email-setting-card .info-row .value {
  color: var(--el-text-color-regular);
  word-break: break-all;
  flex: 1;
}

.email-setting-card .card-footer {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--el-border-color-lighter);
  text-align: right;
}

.section-header {
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
}

.section-desc {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.notification-config-section {
  padding: 20px;
}

.info-box {
  padding: 16px;
  background-color: var(--el-color-info-light-9);
  border-left: 4px solid var(--el-color-info);
  border-radius: 4px;
}

.info-box h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.info-box p {
  margin: 0;
  font-size: 13px;
  color: var(--el-text-color-secondary);
  line-height: 1.6;
}

/* 消息推送配置样式 */
.settings-form :deep(.el-radio-group) {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
}

.settings-form :deep(.el-radio) {
  width: 100%;
  margin-right: 0;
  margin-bottom: 0 !important;
  display: flex;
  align-items: flex-start;
  min-height: 60px;
  padding: 8px 0;
}

.settings-form :deep(.el-radio__input) {
  margin-top: 2px;
}

.settings-form :deep(.el-radio__label) {
  width: 100%;
  padding-left: 8px;
}

.radio-option {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 100%;
}

.option-title {
  font-weight: 500;
  color: var(--el-text-color-regular);
}

.option-desc {
  margin: 0;
  font-size: 13px;
  color: var(--el-text-color-secondary);
  line-height: 1.4;
  word-break: break-word;
  overflow-wrap: break-word;
  hyphens: auto;
  max-width: 100%;
  width: 100%;
  white-space: normal;
  word-wrap: break-word;
}

.settings-form :deep(.el-radio__label) {
  width: 100%;
  padding-left: 8px;
  max-width: calc(100% - 24px);
  white-space: normal !important;
}

.settings-form :deep(.el-radio) {
  width: 100%;
  margin-right: 0;
  margin-bottom: 0 !important;
  display: flex;
  align-items: flex-start;
  min-height: auto;
  padding: 8px 0;
  white-space: normal !important;
  height: auto;
}

.settings-form :deep(.el-radio__input) {
  margin-top: 2px;
}

.unit-text {
  margin-left: 8px;
  color: var(--el-text-color-secondary);
}

.connection-status {
  padding: 16px;
  background-color: var(--el-fill-color-light);
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.connection-status h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-regular);
}

/* 移动端适配 */
@media (max-width: 767px) {
  .admin-settings {
    padding: 0;
  }

  .admin-settings h1 {
    font-size: 20px;
    margin-bottom: 16px;
  }

  .settings-card {
    width: 100%;
    margin: 0;
    border-radius: 0;
  }

  /* 标签页优化 */
  :deep(.el-tabs--border-card) {
    border-radius: 0;
  }

  :deep(.el-tabs__header) {
    margin: 0 0 16px 0;
  }

  :deep(.el-tabs__item) {
    font-size: 14px;
    padding: 0 12px;
  }

  :deep(.el-tabs__nav-wrap) {
    overflow-x: auto;
  }

  /* 表单优化 */
  .settings-form :deep(.el-form-item__label) {
    width: 100% !important;
    text-align: left;
    margin-bottom: 8px;
    line-height: 1.5;
  }

  .settings-form :deep(.el-form-item__content) {
    margin-left: 0 !important;
  }

  /* 上传组件优化 */
  .upload-wrapper :deep(.el-upload-dragger) {
    padding: 20px;
  }

  .upload-wrapper :deep(.el-icon--upload) {
    font-size: 32px;
  }

  .upload-wrapper :deep(.el-upload__text) {
    font-size: 12px;
  }

  /* 封面图片优化 */
  .cover-image-wrapper {
    margin: 0 auto;
  }

  .cover-image {
    max-width: 100%;
    height: auto;
  }

  /* 单选按钮组移动端优化 */
  .settings-form :deep(.el-radio) {
    padding: 12px;
    border: 1px solid var(--el-border-color);
    border-radius: 8px;
  }

  .settings-form :deep(.el-radio.is-checked) {
    border-color: var(--el-color-primary);
    background-color: var(--el-color-primary-light-9);
  }

  .option-title {
    font-size: 14px;
    line-height: 1.4;
  }

  .option-desc {
    font-size: 12px;
    line-height: 1.4;
  }

  /* 连接状态优化 */
  .connection-status {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .connection-status h4 {
    font-size: 14px;
  }

  .connection-status code {
    font-size: 11px;
    word-break: break-all;
  }

  /* 按钮优化 */
  .settings-form :deep(.el-button) {
    width: 100%;
    margin-bottom: 8px;
  }

  .settings-form :deep(.el-button + .el-button) {
    margin-left: 0;
  }

  /* 输入数字组件优化 */
  :deep(.el-input-number) {
    width: 100%;
  }

  /* 开关组件优化 */
  :deep(.el-switch) {
    transform: scale(0.9);
  }

  /* 分隔线优化 */
  :deep(.el-divider) {
    margin: 16px 0;
  }

  /* 卡片优化 */
  :deep(.el-card__body) {
    padding: 16px;
  }

  /* 网格布局优化 */
  :deep(.el-row) {
    flex-direction: column;
  }

  :deep(.el-col) {
    width: 100% !important;
    margin-bottom: 12px;
  }

  /* 通知配置优化 */
  .notification-config-section {
    padding: 0;
  }

  .section-header {
    padding: 16px;
  }

  .section-header h3 {
    font-size: 16px;
  }

  .section-desc {
    font-size: 12px;
  }
}
</style>
