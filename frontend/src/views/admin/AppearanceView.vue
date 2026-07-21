<template>
  <div class="admin-appearance">
    <h1>{{ t('admin.appearance.title') }}</h1>
    <el-card class="appearance-card">
      <el-tabs v-model="activeTab" class="appearance-tabs">
        <!-- 通用设置标签页 -->
        <el-tab-pane :label="t('admin.appearance.tabs.general')" name="general">
          <el-form ref="generalFormRef" :model="generalFormState" :label-width="formLabelConfig.labelWidth"
            :label-position="formLabelConfig.labelPosition" class="appearance-form">
            <!-- 默认语言 -->
            <el-form-item :label="t('admin.appearance.default_language')">
              <div class="form-item">
                <el-select v-model="generalFormState.defaultLang" :placeholder="t('admin.appearance.default_language')">
                  <el-option :label="t('admin.appearance.languages.zh-CN')" value="zh-CN" />
                  <el-option :label="t('admin.appearance.languages.en-US')" value="en-US" />
                </el-select>
                <p class="form-hint">
                  {{ t('admin.appearance.default_language_hint') }}
                </p>
              </div>
            </el-form-item>

            <!-- 深色模式 -->
            <el-form-item :label="t('admin.appearance.dark_mode')">
              <div class="form-item">
                <el-radio-group v-model="generalFormState.darkMode" size="large" fill="primary">
                  <el-radio-button :label="t('admin.appearance.dark_mode_system')" value="system" />
                  <el-radio-button :label="t('admin.appearance.dark_mode_dark')" value="dark" />
                  <el-radio-button :label="t('admin.appearance.dark_mode_light')" value="light" />
                </el-radio-group>
                <p class="form-hint">
                  {{ t('admin.appearance.dark_mode_hint') }}
                </p>
              </div>
            </el-form-item>

            <!-- 默认首页类型 -->
            <el-form-item :label="t('admin.appearance.default_homepage_type')">
              <div class="form-item">
                <el-radio-group v-model="generalFormState.defaultHomepage">
                  <el-radio-button :label="t('admin.appearance.homepage_type_blog')" value="blog" />
                  <el-radio-button :label="t('admin.appearance.homepage_type_doc')" value="doc" />
                </el-radio-group>
                <p class="form-hint">
                  {{ t('admin.appearance.default_homepage_hint') }}
                </p>
              </div>
            </el-form-item>

            <!-- 默认文档书 -->
            <el-form-item v-if="generalFormState.defaultHomepage === 'doc'"
              :label="t('admin.appearance.default_docbook')">
              <div class="form-item">
                <el-select v-model="generalFormState.defaultDocbookId"
                  :placeholder="t('admin.appearance.default_docbook')" :loading="loadingDocbooks">
                  <el-option v-for="docbook in docbookList" :key="docbook.id" :label="docbook.name"
                    :value="docbook.id" />
                  <template v-if="docbookList.length === 0" #empty>
                    <div style="padding: 10px; text-align: center; color: #999">
                      {{ t('admin.appearance.no_docbook_hint') }}
                    </div>
                  </template>
                </el-select>
                <p class="form-hint">
                  {{ t('admin.appearance.default_docbook_hint') }}
                </p>
              </div>
            </el-form-item>

            <!-- 文档模块子域名 -->
            <el-form-item :label="t('admin.appearance.doc_subdomain')">
              <div class="form-item">
                <el-input v-model="generalFormState.docSubdomain"
                  :placeholder="t('admin.appearance.doc_subdomain_placeholder')">
                  <template #prepend>https://</template>
                </el-input>
                <p class="form-hint">
                  {{ t('admin.appearance.doc_subdomain_hint') }}
                </p>
              </div>
            </el-form-item>

            <!-- 是否开启注册 -->
            <el-form-item :label="t('admin.appearance.enable_register')">
              <div class="form-item">
                <el-switch v-model="generalFormState.enableRegister" :active-value="1" :inactive-value="0" />
                <p class="form-hint">
                  {{ t('admin.appearance.enable_register_hint') }}
                </p>
              </div>
            </el-form-item>

            <!-- 用户注册默认角色 -->
            <el-form-item :label="t('admin.appearance.register_role')">
              <div class="form-item">
                <el-select v-model="generalFormState.registerRole"
                  :placeholder="t('admin.appearance.register_role_placeholder')">
                  <el-option :label="t('admin.appearance.roles.user')" value="User" />
                  <el-option :label="t('admin.appearance.roles.contributor')" value="Contributor" />
                  <el-option :label="t('admin.appearance.roles.author')" value="Author" />
                </el-select>
                <p class="form-hint">
                  {{ t('admin.appearance.register_role_hint') }}
                </p>
              </div>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="handleGeneralSubmit">{{ t('admin.appearance.save_button') }}</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- Footer 设置标签页 -->
        <el-tab-pane :label="t('admin.appearance.tabs.footer')" name="footer">
          <el-form ref="footerFormRef" :model="footerFormState" :label-width="formLabelConfig.labelWidth"
            :label-position="formLabelConfig.labelPosition" class="appearance-form">
            <!-- Logo 上传 -->
            <el-form-item :label="t('admin.appearance.footer.logo')">
              <div class="form-item">
                <el-upload class="logo-uploader" :http-request="handleLogoUpload" :before-upload="beforeLogoUpload"
                  :show-file-list="false" :disabled="logoUploading" accept="image/*">
                  <template v-if="footerFormState.logo_url">
                    <img :src="footerFormState.logo_url" class="logo-preview" />
                    <el-button :icon="Delete" class="delete-logo-btn" @click.prevent="removeLogo" />
                  </template>
                  <template v-else>
                    <el-icon class="logo-uploader-icon">
                      <UploadFilled />
                    </el-icon>
                    <div class="logo-upload-text">{{ t('admin.appearance.footer.upload_logo') }}</div>
                  </template>
                </el-upload>
                <p class="form-hint">
                  {{ t('admin.appearance.footer.logo_hint') }}
                </p>
              </div>
            </el-form-item>

            <!-- 网站描述 -->
            <el-form-item :label="t('admin.appearance.footer.site_description')">
              <div class="form-item">
                <el-input v-model="footerFormState.site_description" type="textarea" :rows="3"
                  :placeholder="t('admin.appearance.footer.site_description_placeholder')" />
                <p class="form-hint">
                  {{ t('admin.appearance.footer.site_description_hint') }}
                </p>
              </div>
            </el-form-item>

            <!-- 社交媒体 -->
            <el-form-item :label="t('admin.appearance.footer.social_media')">
              <div class="form-item">
                <div class="social-media-list">
                  <div v-for="(media, index) in footerFormState.social_media" :key="index" class="social-media-item">
                    <el-select v-model="media.icon" :placeholder="t('admin.appearance.footer.select_icon')"
                      style="width: 200px; margin-right: 10px">
                      <el-option label="微信 WeChat" value="ic:baseline-wechat" />
                      <el-option label="微博 Weibo" value="ri:weibo-fill" />
                      <el-option label="知乎 Zhihu" value="ant-design:zhihu-circle-filled" />
                      <el-option label="抖音 Douyin" value="mage:tiktok-circle" />
                      <el-option label="哔哩哔哩 Bilibili" value="streamline-ultimate:bilibili-logo-bold" />
                      <el-option label="小红书 Xiaohongshu" value="simple-icons:xiaohongshu" />
                      <el-option label="Gitee" value="simple-icons:gitee" />
                      <el-option label="GitHub" value="mdi:github" />
                      <el-option label="Twitter" value="mdi:twitter" />
                      <el-option label="LinkedIn" value="mdi:linkedin" />
                      <el-option label="Instagram" value="mingcute:instagram-fill" />
                      <el-option label="Dribbble" value="ant-design:dribbble-circle-filled" />
                      <el-option label="YouTube" value="mdi:youtube" />
                      <el-option label="Facebook" value="mdi:facebook" />
                      <el-option label="Discord" value="mdi:discord" />
                      <el-option label="Telegram" value="mdi:telegram" />
                      <el-option label="Email" value="mdi:email" />
                      <el-option label="Website" value="mdi:web" />
                      <el-option label="RSS" value="mdi:rss" />
                    </el-select>
                    <el-input v-model="media.url" :placeholder="t('admin.appearance.footer.url_placeholder')"
                      style="flex: 1; margin-right: 10px" />
                    <el-button type="danger" @click="removeSocialMedia(index)">{{ t('admin.appearance.footer.remove')
                      }}</el-button>
                  </div>
                </div>
                <el-button type="primary" plain style="width: 120px;" @click="addSocialMedia">{{
                  t('admin.appearance.footer.add_social') }}</el-button>
                <p class="form-hint">
                  {{ t('admin.appearance.footer.social_media_hint') }}
                </p>
              </div>
            </el-form-item>

            <!-- 导航分组 -->
            <el-form-item :label="t('admin.appearance.footer.nav_groups')">
              <div class="form-item">
                <div class="nav-groups-list">
                  <div v-for="(group, groupIndex) in footerFormState.nav_groups" :key="groupIndex"
                    class="nav-group-item">
                    <div class="group-header">
                      <el-input v-model="group.group_name"
                        :placeholder="t('admin.appearance.footer.group_name_placeholder')"
                        style="flex: 1; margin-right: 10px" />
                      <el-button type="danger" @click="removeNavGroup(groupIndex)">{{
                        t('admin.appearance.footer.remove')
                        }}</el-button>
                    </div>
                    <div class="group-links">
                      <div v-for="(link, linkIndex) in group.links" :key="linkIndex" class="link-item">
                        <el-input v-model="link.name" :placeholder="t('admin.appearance.footer.link_name_placeholder')"
                          style="width: 150px; margin-right: 10px" />
                        <el-input v-model="link.url" :placeholder="t('admin.appearance.footer.url_placeholder')"
                          style="flex: 1; margin-right: 10px" />
                        <el-button type="danger" size="small" @click="removeLink(groupIndex, linkIndex)">
                          <IconifyIcon icon="mdi:close" />
                        </el-button>
                      </div>
                      <el-button type="primary" plain size="small" style="width: 90px;" @click="addLink(groupIndex)">
                        <IconifyIcon icon="mdi:plus" style="margin-right: 5px" />
                        {{ t('admin.appearance.footer.add_link') }}
                      </el-button>
                    </div>
                  </div>
                </div>
                <el-button type="primary" plain style="width: 120px" @click="addNavGroup">{{
                  t('admin.appearance.footer.add_nav_group')
                }}</el-button>
                <p class="form-hint">
                  {{ t('admin.appearance.footer.nav_groups_hint') }}
                </p>
              </div>
            </el-form-item>

            <!-- 版权信息 -->
            <el-form-item :label="t('admin.appearance.footer.copyright')">
              <div class="form-item">
                <el-input v-model="footerFormState.copyright"
                  :placeholder="t('admin.appearance.footer.copyright_placeholder')" />
                <p class="form-hint">
                  {{ t('admin.appearance.footer.copyright_hint') }}
                </p>
              </div>
            </el-form-item>

            <!-- ICP 信息 -->
            <el-form-item :label="t('admin.appearance.footer.icp_info')">
              <div class="form-item">
                <div class="icp-list">
                  <div v-for="(icp, index) in footerFormState.icp_info" :key="index" class="icp-item">
                    <el-input v-model="icp.text" :placeholder="t('admin.appearance.footer.icp_text_placeholder')"
                      style="width: 200px; margin-right: 10px" />
                    <el-input v-model="icp.url" :placeholder="t('admin.appearance.footer.url_placeholder')"
                      style="flex: 1; margin-right: 10px" />
                    <el-button type="danger" @click="removeIcp(index)">{{ t('admin.appearance.footer.remove')
                      }}</el-button>
                  </div>
                </div>
                <el-button type="primary" plain style="width: 120px;" @click="addIcp">{{
                  t('admin.appearance.footer.add_icp')
                  }}</el-button>
                <p class="form-hint">
                  {{ t('admin.appearance.footer.icp_info_hint') }}
                </p>
              </div>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" :loading="footerSaving" @click="handleFooterSubmit">{{
                t('admin.appearance.save_button')
                }}</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { FormInstance } from 'element-plus'
import { ElMessage } from 'element-plus'
import { Delete, UploadFilled } from '@element-plus/icons-vue'
import IconifyIcon from '@/components/IconIfy.vue'
import { getSiteConfig, updateSiteConfig } from '@/api/services/siteconfig'
import { docBookApi } from '@/api/services/doc'
import { uploadFile } from '@/api/services/common'
import type { DocBook } from '@/api/services/doc'
import { useMobileDetection } from '@/composables/useMobileDetection'

const { t } = useI18n()

// 移动端检测
const { isMobile } = useMobileDetection()

// 响应式表单标签配置
const formLabelConfig = computed(() => ({
  labelWidth: isMobile.value ? 'auto' : '140px',
  labelPosition: isMobile.value ? 'top' : 'right'
}))

// 社交媒体类型
interface SocialMedia {
  icon: string
  url: string
}

// 导航链接
interface NavLink {
  name: string
  url: string
}

// 导航分组
interface NavGroup {
  group_name: string
  links: NavLink[]
}

// ICP 信息
interface IcpInfo {
  text: string
  url: string
}

// Footer 配置
interface FooterConfig {
  logo_url: string
  site_description: string
  social_media: SocialMedia[]
  nav_groups: NavGroup[]
  copyright: string
  icp_info: IcpInfo[]
}

const activeTab = ref('general')
const generalFormRef = ref<FormInstance>()
const footerFormRef = ref<FormInstance>()

const generalFormState = reactive({
  defaultLang: 'zh-CN',
  darkMode: 'system',
  defaultHomepage: 'blog',
  defaultDocbookId: null as number | null,
  docSubdomain: '',
  enableRegister: 1,
  registerRole: 'User'
})

const footerFormState = reactive<FooterConfig>({
  logo_url: '',
  site_description: '',
  social_media: [],
  nav_groups: [],
  copyright: '',
  icp_info: []
})

const docbookList = ref<DocBook[]>([])
const loadingDocbooks = ref(false)
const footerSaving = ref(false)

// 获取文档书列表
const fetchDocbooks = async () => {
  loadingDocbooks.value = true
  try {
    const res = await docBookApi.list({ limit: 100 })
    if (res.code === 1 && res.data) {
      docbookList.value = res.data
    }
  } catch (error) {
    console.error('获取文档书列表失败:', error)
  } finally {
    loadingDocbooks.value = false
  }
}

// 社交媒体操作
const addSocialMedia = () => {
  footerFormState.social_media.push({ icon: '', url: '' })
}

const removeSocialMedia = (index: number) => {
  footerFormState.social_media.splice(index, 1)
}

// 导航分组操作
const addNavGroup = () => {
  footerFormState.nav_groups.push({ group_name: '', links: [] })
}

const removeNavGroup = (groupIndex: number) => {
  footerFormState.nav_groups.splice(groupIndex, 1)
}

const addLink = (groupIndex: number) => {
  footerFormState.nav_groups[groupIndex].links.push({ name: '', url: '' })
}

const removeLink = (groupIndex: number, linkIndex: number) => {
  footerFormState.nav_groups[groupIndex].links.splice(linkIndex, 1)
}

// ICP 操作
const addIcp = () => {
  footerFormState.icp_info.push({ text: '', url: '' })
}

const removeIcp = (index: number) => {
  footerFormState.icp_info.splice(index, 1)
}

// Logo 上传相关
const logoUploading = ref(false)

// 上传前验证
const beforeLogoUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error(t('admin.appearance.footer.logo_image_only'))
    return false
  }
  if (!isLt2M) {
    ElMessage.error(t('admin.appearance.footer.logo_size_limit'))
    return false
  }
  return true
}

// 处理 Logo 上传
const handleLogoUpload = async (options: any) => {
  const { file } = options
  logoUploading.value = true

  try {
    const res = await uploadFile({ file })
    if (res.code === 1 && res.data) {
      footerFormState.logo_url = res.data.url || res.data.file_path || ''
      ElMessage.success(t('admin.appearance.footer.upload_success'))
    } else {
      ElMessage.error(res.msg || t('admin.appearance.footer.upload_failed'))
    }
  } catch (error) {
    console.error('Logo 上传失败:', error)
    ElMessage.error(t('admin.appearance.footer.upload_failed'))
  } finally {
    logoUploading.value = false
  }
}

// 移除 Logo
const removeLogo = () => {
  footerFormState.logo_url = ''
  ElMessage.success(t('admin.appearance.footer.logo_removed'))
}

// 初始化时获取网站配置
onMounted(async () => {
  try {
    const res = await getSiteConfig()
    if (res.code === 1 && res.data) {
      // 通用设置
      generalFormState.defaultLang = res.data.language || 'zh-CN'
      generalFormState.darkMode = res.data.dark_mode || 'system'
      generalFormState.defaultHomepage = res.data.default_homepage || 'blog'
      generalFormState.defaultDocbookId = res.data.default_docbook_id || null
      generalFormState.docSubdomain = res.data.doc_subdomain || ''
      generalFormState.enableRegister = res.data.enable_register ?? 1
      generalFormState.registerRole = res.data.register_role || 'User'

      // Footer 设置
      if (res.data.footer_config) {
        const footer = res.data.footer_config
        footerFormState.logo_url = footer.logo_url || ''
        footerFormState.site_description = footer.site_description || ''
        footerFormState.social_media = footer.social_media || []
        footerFormState.nav_groups = footer.nav_groups || []
        footerFormState.copyright = footer.copyright || ''
        footerFormState.icp_info = footer.icp_info || []
      }
    }
  } catch (error) {
    console.error('获取网站配置失败:', error)
  }

  // 获取文档书列表
  await fetchDocbooks()
})

// 监听默认首页类型变化
watch(() => generalFormState.defaultHomepage, (newVal) => {
  if (newVal === 'blog') {
    generalFormState.defaultDocbookId = null
  }
})

// 保存通用设置
const handleGeneralSubmit = async () => {
  if (!generalFormRef.value) return
  try {
    await generalFormRef.value.validate()
    const data = {
      language: generalFormState.defaultLang,
      dark_mode: generalFormState.darkMode,
      default_homepage: generalFormState.defaultHomepage,
      default_docbook_id: generalFormState.defaultDocbookId,
      doc_subdomain: generalFormState.docSubdomain || null,
      enable_register: generalFormState.enableRegister,
      register_role: generalFormState.registerRole
    }
    const res = await updateSiteConfig(data)
    if (res.code === 1) {
      ElMessage.success(t('admin.appearance.message.save_success'))
    } else {
      ElMessage.error(res.msg || t('admin.appearance.message.save_failed'))
    }
  } catch (err) {
    console.error('保存失败:', err)
  }
}

// 保存 Footer 设置
const handleFooterSubmit = async () => {
  if (!footerFormRef.value) return
  try {
    footerSaving.value = true
    const data = {
      footer_config: footerFormState
    }
    const res = await updateSiteConfig(data)
    if (res.code === 1) {
      ElMessage.success(t('admin.appearance.message.save_success'))
    } else {
      ElMessage.error(res.msg || t('admin.appearance.message.save_failed'))
    }
  } catch (err) {
    console.error('保存失败:', err)
  } finally {
    footerSaving.value = false
  }
}
</script>

<style scoped>
.admin-appearance {
  padding: 20px;
}

.appearance-card {
  max-width: 900px;
}

.appearance-form {
  padding: 20px;
}

.appearance-tabs {
  padding: 0 20px;
}

.form-item {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.form-hint {
  font-size: 14px;
  color: #999999;
  margin-top: 8px;
  margin-bottom: 0;
}

.social-media-list,
.nav-groups-list,
.icp-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 10px;
}

.social-media-item,
.icp-item {
  display: flex;
  align-items: center;
}

.nav-group-item {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 15px;
  background-color: #fafafa;
}

.group-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.group-links {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-left: 20px;
}

.link-item {
  display: flex;
  align-items: center;
}

/* Logo 上传组件样式 */
.logo-uploader {
  display: inline-block;
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
}

.logo-uploader:hover {
  border-color: var(--el-color-primary);
}

.logo-uploader:deep(.el-upload) {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  /* height: 120px; */
}

.logo-preview {
  width: 100%;
  /* height: 120px; */
  object-fit: cover;
  display: block;
}

.delete-logo-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  padding: 4px !important;
  background: rgba(0, 0, 0, 0.6);
  border: none;
  border-radius: 4px;
  color: #e4e7ed;
  width: 46px;
}

.delete-logo-btn:hover {
  background: rgba(0, 0, 0, 0.8);
  color: #fff !important;
}

.logo-uploader-icon {
  font-size: 32px;
  color: #8c939d;
  margin-bottom: 8px;
}

.logo-upload-text {
  font-size: 12px;
  color: #8c939d;
  text-align: center;
}

/* 移动端适配 */
@media (max-width: 767px) {
  .admin-appearance {
    padding: 0;
  }

  .admin-appearance h1 {
    font-size: 20px;
    margin-bottom: 16px;
  }

  .appearance-card {
    width: 100%;
    margin: 0;
    border-radius: 0;
  }

  /* 标签页优化 */
  .appearance-tabs :deep(.el-tabs__header) {
    margin: 0 0 16px 0;
  }

  .appearance-tabs :deep(.el-tabs__item) {
    font-size: 14px;
    padding: 0 12px;
  }

  .appearance-tabs :deep(.el-tabs__nav-wrap) {
    overflow-x: auto;
  }

  /* 表单优化 */
  .appearance-form :deep(.el-form-item__label) {
    width: 100% !important;
    text-align: left;
    margin-bottom: 8px;
    line-height: 1.5;
  }

  .appearance-form :deep(.el-form-item__content) {
    margin-left: 0 !important;
  }

  /* 单选按钮组优化 */
  /* :deep(.el-radio-group) {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  :deep(.el-radio-button) {
    flex: 1;
    min-width: calc(50% - 4px);
  }

  :deep(.el-radio-button__inner) {
    width: 100%;
  } */

  /* 选择器优化 */
  :deep(.el-select) {
    width: 100%;
  }

  /* 输入框优化 */
  :deep(.el-input) {
    width: 100%;
  }

  /* 开关组件优化 */
  :deep(.el-switch) {
    transform: scale(0.9);
  }

  /* 上传组件优化 */
  .upload-wrapper :deep(.el-upload-dragger) {
    padding: 20px;
  }

  .logo-uploader-icon {
    font-size: 24px;
  }

  .logo-upload-text {
    font-size: 11px;
  }

  /* Logo上传区域优化 */
  .logo-upload-wrapper {
    width: 100%;
  }

  .logo-preview-wrapper {
    max-width: 100%;
  }

  .logo-preview-image {
    max-width: 120px;
  }

  /* 社交媒体列表优化 */
  .social-media-list {
    padding: 0;
  }

  .social-media-item {
    flex-direction: column;
    gap: 12px;
    padding: 12px;
  }

  .social-media-inputs {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .social-media-inputs .el-input {
    width: 100%;
  }

  .social-media-actions {
    width: 100%;
    display: flex;
    justify-content: flex-end;
  }

  /* 导航分组优化 */
  .nav-groups-list {
    padding: 0;
  }

  .nav-group-item {
    padding: 12px;
  }

  .nav-group-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .nav-group-name {
    font-size: 14px;
  }

  .nav-group-actions {
    width: 100%;
    display: flex;
    justify-content: flex-end;
  }

  /* 导航链接列表优化 */
  .nav-links-list {
    padding: 0;
  }

  .nav-link-item {
    flex-direction: column;
    gap: 8px;
    padding: 12px;
  }

  .nav-link-inputs {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .nav-link-inputs .el-input {
    width: 100%;
  }

  /* ICP信息优化 */
  .icp-info-list {
    padding: 0;
  }

  .icp-info-item {
    flex-direction: column;
    gap: 8px;
    padding: 12px;
  }

  .icp-info-inputs {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .icp-info-inputs .el-input {
    width: 100%;
  }

  /* 按钮优化 */
  :deep(.el-button) {
    width: 100%;
    margin-bottom: 8px;
  }

  :deep(.el-button + .el-button) {
    margin-left: 0;
  }

  /* 卡片优化 */
  :deep(.el-card__body) {
    padding: 16px;
  }

  /* 分隔线优化 */
  :deep(.el-divider) {
    margin: 12px 0;
  }

  /* 空状态优化 */
  :deep(.el-empty) {
    padding: 20px;
  }

  /* 表单提示优化 */
  .form-hint {
    font-size: 12px;
    line-height: 1.4;
    margin-top: 4px;
  }

  /* 标签优化 */
  :deep(.el-tag) {
    font-size: 12px;
  }

  /* 输入框组优化 */
  :deep(.el-input-group) {
    flex-wrap: wrap;
  }

  :deep(.el-input-group__append) {
    border-left: 1px solid var(--el-border-color);
  }

  /* 社交媒体项优化 */
  .social-media-item {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
    padding: 12px;
  }

  .social-media-item .el-select,
  .social-media-item .el-input {
    width: 100% !important;
    margin-right: 0 !important;
  }

  .social-media-item .el-button {
    width: auto;
    padding: 8px 16px;
  }

  /* 导航分组优化 */
  .nav-group-item {
    padding: 12px;
  }

  .group-header {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .group-header .el-input {
    width: 100% !important;
    margin-right: 0 !important;
  }

  .group-header .el-button {
    width: auto;
    align-self: flex-end;
  }

  /* 导航链接项优化 */
  .link-item {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
    padding: 8px;
  }

  .link-item .el-input {
    width: 100% !important;
    margin-right: 0 !important;
  }

  .link-item .el-button {
    width: auto;
    align-self: flex-end;
    margin-top: 4px;
  }

  /* ICP项优化 */
  .icp-item {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
    padding: 12px;
  }

  .icp-item .el-input {
    width: 100% !important;
    margin-right: 0 !important;
  }

  .icp-item .el-button {
    width: auto;
    align-self: flex-end;
  }

  /* 添加按钮优化 */
  .form-item .el-button[style*="width"] {
    width: 100% !important;
  }
}
</style>
