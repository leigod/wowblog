<template>
  <div class="creator-page">
    <div class="page-header">
      <div>
        <h1>{{ t('creator.appearance.title') }}</h1>
        <p>{{ t('creator.appearance.title_info') }}</p>
      </div>
      <el-button type="primary" plain :icon="View" @click="viewMyBlog">
        {{ t('creator.appearance.view_blog') }}
      </el-button>
    </div>

    <el-card class="settings-card" v-loading="loading">
      <el-form label-position="top" class="settings-form">
        <!-- Blog Logo -->
        <el-form-item :label="t('creator.appearance.logo')">
          <div class="upload-row">
            <div class="preview-box logo-preview">
              <img v-if="form.logo" :src="form.logo" alt="logo" />
              <el-icon v-else :size="28"><Picture /></el-icon>
            </div>
            <div class="upload-actions">
              <el-upload
                :show-file-list="false"
                accept="image/png"
                :before-upload="(f: File) => beforePngUpload(f, 'logo')"
                :http-request="(opt: any) => doUpload(opt, 'logo')"
              >
                <el-button type="primary" plain>{{ t('creator.appearance.upload_logo') }}</el-button>
              </el-upload>
              <el-button v-if="form.logo" text type="danger" @click="form.logo = null">
                {{ t('creator.appearance.remove') }}
              </el-button>
              <p class="upload-hint">{{ t('creator.appearance.logo_hint') }}</p>
            </div>
          </div>
        </el-form-item>

        <!-- Favicon -->
        <el-form-item :label="t('creator.appearance.favicon')">
          <div class="upload-row">
            <div class="preview-box favicon-preview">
              <img v-if="form.favicon" :src="form.favicon" alt="favicon" />
              <el-icon v-else :size="28"><Picture /></el-icon>
            </div>
            <div class="upload-actions">
              <el-upload
                :show-file-list="false"
                accept="image/png"
                :before-upload="(f: File) => beforePngUpload(f, 'favicon')"
                :http-request="(opt: any) => doUpload(opt, 'favicon')"
              >
                <el-button type="primary" plain>{{ t('creator.appearance.upload_favicon') }}</el-button>
              </el-upload>
              <el-button v-if="form.favicon" text type="danger" @click="form.favicon = null">
                {{ t('creator.appearance.remove') }}
              </el-button>
              <p class="upload-hint">{{ t('creator.appearance.favicon_hint') }}</p>
            </div>
          </div>
        </el-form-item>

        <!-- 首页布局 -->
        <el-form-item :label="t('creator.appearance.layout')">
          <div class="layout-options">
            <div
              v-for="opt in layoutOptions"
              :key="opt.value"
              class="layout-option"
              :class="{ active: form.homepage_layout === opt.value }"
              @click="selectLayout(opt.value)"
            >
              <div class="layout-thumb">
                <template v-if="opt.value === 'magazine'">
                  <span class="lt-hero"></span>
                  <span class="lt-cell"></span><span class="lt-cell"></span><span class="lt-cell"></span>
                </template>
                <template v-else-if="opt.value === 'stacked'">
                  <span class="lt-row" v-for="i in 3" :key="i"></span>
                </template>
                <template v-else>
                  <span class="lt-cell" v-for="i in 6" :key="i"></span>
                </template>
              </div>
              <p class="layout-name">{{ t('creator.appearance.layout_' + opt.value) }}</p>
              <p class="layout-desc">{{ t('creator.appearance.layout_' + opt.value + '_desc') }}</p>
            </div>
          </div>
          <p class="upload-hint">{{ t('creator.appearance.layout_hint') }}</p>
        </el-form-item>

        <!-- 图片水印 -->
        <el-form-item :label="t('creator.appearance.watermark')">
          <div class="watermark-settings">
            <el-radio-group v-model="form.watermark_enabled">
              <el-radio :value="null">{{ t('creator.appearance.watermark_follow_site') }}</el-radio>
              <el-radio :value="1">{{ t('creator.appearance.watermark_on') }}</el-radio>
              <el-radio :value="0">{{ t('creator.appearance.watermark_off') }}</el-radio>
            </el-radio-group>
            <template v-if="form.watermark_enabled === 1">
              <el-radio-group v-model="form.watermark_mode" size="small">
                <el-radio-button value="corner">{{ t('creator.appearance.watermark_corner') }}</el-radio-button>
                <el-radio-button value="tile">{{ t('creator.appearance.watermark_tile') }}</el-radio-button>
              </el-radio-group>
            </template>
            <p class="upload-hint">{{ t('creator.appearance.watermark_hint') }}</p>
          </div>
        </el-form-item>

        <!-- 社媒账号 -->
        <el-form-item :label="t('creator.appearance.social_links')">
          <div class="social-list">
            <div v-for="(link, index) in socialLinks" :key="index" class="social-row">
              <el-input
                v-model="link.platform"
                :placeholder="t('creator.appearance.social_platform_placeholder')"
                class="social-platform"
                maxlength="30"
              />
              <el-input
                v-model="link.url"
                :placeholder="t('creator.appearance.social_url_placeholder')"
                class="social-url"
              />
              <el-button text type="danger" @click="socialLinks.splice(index, 1)">
                {{ t('creator.appearance.remove_social') }}
              </el-button>
            </div>
            <el-button
              v-if="socialLinks.length < 8"
              text
              type="primary"
              @click="socialLinks.push({ platform: '', url: '' })"
            >
              + {{ t('creator.appearance.add_social') }}
            </el-button>
            <p class="upload-hint">{{ t('creator.appearance.social_links_hint') }}</p>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="saving" @click="handleSave">
            {{ t('creator.settings.save') }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Picture, View } from '@element-plus/icons-vue'
import { getBlogConfig, updateBlogConfig, type BlogLayout } from '@/api/services/creator'
import { uploadFile } from '@/api/services/common'
import { useAppStore } from '@/stores/app'

const { t } = useI18n()
const appStore = useAppStore()

// 新开标签页打开当前用户的 blog 首页
const viewMyBlog = () => {
  const username = appStore.userInfo?.username
  if (!username) return
  window.open(`/blog/${username}`, '_blank')
}

const loading = ref(false)
const saving = ref(false)

const form = reactive<{
  logo: string | null
  favicon: string | null
  homepage_layout: BlogLayout
  watermark_enabled: number | null
  watermark_mode: 'corner' | 'tile' | null
}>({
  logo: null,
  favicon: null,
  homepage_layout: 'magazine',
  watermark_enabled: null,
  watermark_mode: null
})

const socialLinks = ref<{ platform: string; url: string }[]>([])

const layoutOptions: { value: BlogLayout }[] = [
  { value: 'magazine' },
  { value: 'stacked' },
  { value: 'grid' }
]

const selectLayout = (value: BlogLayout) => {
  form.homepage_layout = value
}

// 水印开关联动：开启时样式默认右下角；非开启状态样式跟随全站
watch(() => form.watermark_enabled, (enabled) => {
  if (enabled === 1 && form.watermark_mode === null) {
    form.watermark_mode = 'corner'
  } else if (enabled !== 1) {
    form.watermark_mode = null
  }
})

const loadConfig = async () => {
  loading.value = true
  try {
    const res = await getBlogConfig()
    if (res.code === 1 && res.data) {
      form.logo = res.data.logo
      form.favicon = res.data.favicon
      form.homepage_layout = res.data.homepage_layout || 'magazine'
      form.watermark_enabled = res.data.watermark_enabled ?? null
      form.watermark_mode = res.data.watermark_mode ?? null
      socialLinks.value = Array.isArray(res.data.social_links) ? res.data.social_links : []
    }
  } catch (error) {
    console.error(t('creator.settings.load_error'), error)
    ElMessage.error(t('creator.settings.load_error'))
  } finally {
    loading.value = false
  }
}

const beforePngUpload = (file: File, target: 'logo' | 'favicon') => {
  if (file.type !== 'image/png') {
    ElMessage.error(t('creator.appearance.file_type_error'))
    return false
  }
  void target
  return true
}

const doUpload = async (option: any, target: 'logo' | 'favicon') => {
  try {
    // logo/favicon 是水印素材本身，标记 material 跳过水印
    const res = await uploadFile({ file: option.file as File, purpose: 'material' })
    if (res.code === 1 && res.data) {
      // 上传接口返回 url（相对 /static/...）与 full_url（完整地址）。
      // 必须存 full_url：相对路径会被前端 dev server（5173）解析而 404
      // （与文章封面的处理一致）
      const url = typeof res.data === 'string' ? res.data : (res.data.full_url || res.data.url)
      if (target === 'logo') {
        form.logo = url
      } else {
        form.favicon = url
      }
      ElMessage.success(t('creator.appearance.upload_success'))
    } else {
      ElMessage.error(res.msg || t('creator.appearance.upload_error'))
    }
  } catch (error) {
    console.error(t('creator.appearance.upload_error'), error)
    ElMessage.error(t('creator.appearance.upload_error'))
  }
  option.onSuccess?.()
}

const handleSave = async () => {
  saving.value = true
  try {
    const links = socialLinks.value
      .filter((l) => l.platform.trim() && l.url.trim())
      .map((l) => ({ platform: l.platform.trim(), url: l.url.trim() }))
    const res = await updateBlogConfig({
      logo: form.logo,
      favicon: form.favicon,
      homepage_layout: form.homepage_layout,
      social_links: links,
      watermark_enabled: form.watermark_enabled,
      watermark_mode: form.watermark_mode
    })
    if (res.code === 1) {
      ElMessage.success(t('creator.appearance.save_success'))
    } else {
      ElMessage.error(res.msg || t('creator.appearance.save_error'))
    }
  } catch (error) {
    console.error(t('creator.appearance.save_error'), error)
    ElMessage.error(t('creator.appearance.save_error'))
  } finally {
    saving.value = false
  }
}

onMounted(loadConfig)
</script>

<style scoped>
.creator-page {
  padding: 20px;
  max-width: 900px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
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

.settings-card {
  border-radius: 8px;
}

.settings-form {
  max-width: 680px;
}

.upload-row {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.preview-box {
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--el-fill-color-light);
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  color: var(--el-text-color-placeholder);
  overflow: hidden;
  flex-shrink: 0;
}

.logo-preview {
  width: 200px;
  height: 50px;
}

.favicon-preview {
  width: 64px;
  height: 64px;
}

.preview-box img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.upload-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
}

.upload-hint {
  margin: 4px 0 0;
  font-size: 12px;
  color: var(--el-text-color-placeholder);
  line-height: 1.5;
}

.layout-options {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.layout-option {
  width: 160px;
  padding: 12px;
  border: 2px solid var(--el-border-color-lighter);
  border-radius: 8px;
  cursor: pointer;
  transition: border-color 0.2s;
}

.layout-option:hover {
  border-color: var(--el-color-primary-light-5);
}

.layout-option.active {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

.layout-option.disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.layout-thumb {
  display: grid;
  gap: 4px;
  height: 64px;
  padding: 6px;
  border-radius: 4px;
  background: var(--el-fill-color-light);
  overflow: hidden;
}

.layout-option:first-of-type .layout-thumb,
.layout-thumb {
  grid-template-columns: 2fr 1fr;
}

.layout-thumb .lt-hero {
  grid-row: span 3;
  border-radius: 3px;
  background: var(--el-color-primary-light-7);
}

.layout-thumb .lt-cell {
  border-radius: 3px;
  background: var(--el-fill-color-darker);
}

.layout-thumb .lt-row {
  grid-column: span 2;
  height: 14px;
  border-radius: 3px;
  background: var(--el-fill-color-darker);
}

.layout-name {
  margin: 8px 0 2px;
  font-size: 13px;
  font-weight: 600;
}

.layout-desc {
  margin: 0;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.social-list {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.social-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.social-platform {
  width: 180px;
  flex-shrink: 0;
}

.social-url {
  flex: 1;
}
</style>
