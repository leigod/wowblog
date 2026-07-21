<template>
  <div class="article-editor-layout" ref="rootElement">
    <!-- 顶部导航栏 -->
    <header class="editor-header">
      <div class="logo">
        <img src="@/assets/logo.svg" alt="Logo" class="logo-img" />
        <h1 class="site-title">{{ t('article_editor.title') }}</h1>
      </div>
      <div class="header-actions">
        <el-button type="default" round size="large" @click="handlePreview">{{ t('article_editor.preview')
          }}</el-button>
        <el-button type="primary" round size="large" @click="openPublishDrawer">{{ t('article_editor.publish')
          }}</el-button>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="editor-content">
      <!--文章操作按钮区  -->
      <div class="top-actions">
        <el-button v-if="showAddCoverBtn" type="default" color="#FFFFFF" :icon="Picture" round
          @click="handleAddCover">{{ t('article_editor.add_cover') }}</el-button>
        <el-button v-if="showSubtitleBtn" type="default" color="#FFFFFF" :icon="Postcard" round
          @click="toggleSubtitle">{{ t('article_editor.add_subtitle') }}</el-button>
      </div>
      <!-- 封面上传区域 -->
      <div class="cover-upload-area">
        <template v-if="coverImageUrl">
          <div class="cover-image-wrapper">
            <img :src="coverImageUrl" :alt="t('article_editor.cover_image')" class="cover-image" />
            <el-button :icon="Delete" class="delete-cover-btn" @click="removeCoverImage" />
          </div>
        </template>
      </div>
      <!-- 标题和副标题区域 -->
      <div class="article-title-area">
        <textarea maxlength="150" v-model="articleTitle" :placeholder="t('article_editor.title_placeholder')"
          class="article-title-input" rows="1" style="height: 60px !important"></textarea>
      </div>
      <div v-if="showSubtitle" class="subtitle-container">
        <textarea v-model="articleSubtitle" :placeholder="t('article_editor.subtitle_placeholder')"
          class="article-subtitle-input" maxlength="150" style="height: 53px !important"></textarea>
        <el-button :icon="Close" class="delete-subtitle-btn" @click="toggleSubtitle"></el-button>
      </div>

      <!-- 目录区域 -->
      <div v-if="showArticleTOC" class="table-of-contents" v-html="tableOfContents"></div>

      <!-- 富媒体编辑器区域 -->
      <div class="editor-container">
        <!-- <TiptapEditor
          v-model="articleContent"
          placeholder="Type '/' for commands..."
          class="editor"
        /> -->
        <SlashEditor v-model="articleContent" :placeholder="t('article_editor.content_placeholder')" />
      </div>

      <!-- 发布抽屉组件 -->
      <el-drawer v-model="publishDrawerVisible" :title="t('article_editor.publish_drawer_title')" :size="drawerSize"
        :before-close="handleClosePublishDrawer" @click="handleDrawerClick">
        <template #header>
          <div class="drawer-header" style="border-bottom: 1px solid #e4e7ed">
            <h2 class="drawer-title">{{ t('article_editor.publish_drawer_title') }}</h2>
          </div>
        </template>
        <el-form ref="publishFormRef" :model="publishForm" :rules="publishFormRules" label-width="100px"
          label-position="top" size="large">
          <el-form-item :label="t('article_editor.category')" class="form-label" prop="category">
            <el-tree-select v-model="publishForm.category" :data="categoryTreeData" :render-after-expand="false"
              :default-expand-all="true" :check-strictly="true" :props="{
                label: 'label',
                value: 'value',
                children: 'children'
              }" :placeholder="t('article_editor.select_category')" />
          </el-form-item>
          <el-form-item :label="t('article_editor.series')" class="form-label" v-if="seriesList.length > 0">
            <el-select v-model="publishForm.series" :placeholder="t('article_editor.select_series')">
              <el-option v-for="item in seriesList" :key="item.id" :label="item.name" :value="item.id" />
            </el-select>
          </el-form-item>
          <el-form-item :label="t('article_editor.author')" class="form-label" prop="author">
            <template #label>
              <span>{{ t('article_editor.author') }} </span>
              <el-tooltip placement="top">
                <template #content>
                  {{ t('article_editor.change_author_note') }}
                </template>
                <el-icon>
                  <QuestionFilled />
                </el-icon>
              </el-tooltip>
            </template>
            <template #default>
              <div style="
                  display: flex;
                  width: 100%;
                  border: 1px solid #dcdfe6;
                  border-radius: 15px;
                  height: auto;
                  align-items: center;
                  padding: 0 0 0 20px;
                ">
                <div style="display: flex; align-items: center; width: 50px; border-radius: 50%">
                  <img :src="authorInfo.profile_image ? authorInfo.profile_image : '/src/assets/avatar.png'
                    " :alt="t('article_editor.author_avatar')" class="author-avatar"
                    style="width: 51px; height: 51px; border-radius: 50%" />
                </div>
                <div style="
                    margin-left: 20px;
                    display: flex;
                    width: 100%;
                    justify-content: space-between;
                  ">
                  <div style="display: flex; flex-direction: column; padding-bottom: 10px">
                    <div style="font-size: 16px; font-weight: 500; flex: 1">
                      {{ authorInfo.full_name }}
                    </div>
                    <el-tag type="primary" round size="small">{{ t('article_editor.owner') }}</el-tag>
                  </div>
                  <div style="
                      width: 120px;
                      display: flex;
                      justify-content: flex-end;
                      align-items: center;
                    ">
                    <el-button round size="large" link @click.stop="handleChangeAuthor">{{
                      t('article_editor.change_author') }}</el-button>
                  </div>
                </div>
              </div>
              <el-card style="width: 100%; min-height: 120px; margin-top: 10px" v-if="changeAuthorCardShow" @click.stop>
                <el-input v-model="searchAuthorInput" :placeholder="t('article_editor.search_authors')"
                  :prefix-icon="Search" size="large" :autofocus="true" @input="handleSearchAuthors(searchAuthorInput)"
                  @click.stop />
                <div style="width: 100%; padding: 10px">
                  <span v-if="searchAuthorResults.length === 0 && !showSearchAuthorLoading">{{
                    t('article_editor.no_results') }}</span>
                  <span v-if="showSearchAuthorLoading">{{ t('article_editor.loading') }}</span>
                  <div v-else @click.stop>
                    <div v-for="item in searchAuthorResults" :key="item.id" class="author-item"
                      @click.stop="handleSelectAuthor(item)">
                      <div style="display: flex; align-items: center; width: 40px; border-radius: 50%">
                        <img :src="item.profile_image ? item.profile_image : '/src/assets/avatar.png'"
                          :alt="t('article_editor.author_avatar')" class="author-avatar"
                          style="width: 40px; height: 40px; border-radius: 50%" />
                      </div>
                      <div style="
                          margin-left: 10px;
                          display: flex;
                          flex-direction: column;
                          justify-content: center;
                        ">
                        <div style="font-size: 16px; font-weight: 500; line-height: 20px">
                          {{ item.full_name }}
                        </div>
                        <div style="font-size: 14px; color: #909399; line-height: 18px">
                          @{{ item.username }}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </el-card>
            </template>

            <!-- <el-select v-model="publishForm.author" placeholder="请选择作者">
              <el-option label="作者1" value="1" />
              <el-option label="作者2" value="2" />
            </el-select> -->
          </el-form-item>
          <el-form-item :label="t('article_editor.co_authors')" class="form-label">
            <template #label>
              <div>
                <span>{{ t('article_editor.co_authors') }} </span>
                <el-tooltip placement="top">
                  <template #content>
                    {{ t('article_editor.co_authors_note') }}
                  </template>
                  <el-icon>
                    <QuestionFilled />
                  </el-icon>
                </el-tooltip>
              </div>
            </template>

            <template #default>
              <el-button size="large" round :icon="CirclePlus" @click.stop="showCoAuthorCard = true">{{
                t('article_editor.add_co_author') }}</el-button>
              <div v-for="author in coAuthorsList" :key="author.id" style="
                  display: flex;
                  width: 100%;
                  border: 1px solid #dcdfe6;
                  border-radius: 15px;
                  height: auto;
                  align-items: center;
                  padding: 10px;
                  margin-top: 10px;
                ">
                <div style="display: flex; align-items: center; width: 40px; border-radius: 50%">
                  <img :src="author.profile_image ? author.profile_image : '/src/assets/avatar.png'"
                    :alt="t('article_editor.author_avatar')" class="author-avatar"
                    style="width: 40px; height: 40px; border-radius: 50%" />
                </div>
                <div style="
                    margin-left: 20px;
                    display: flex;
                    width: 100%;
                    justify-content: space-between;
                  ">
                  <div style="display: flex; flex-direction: column; justify-content: center">
                    <div style="font-size: 16px; font-weight: 500; line-height: 20px">
                      {{ author.full_name }}
                    </div>
                    <div style="font-size: 14px; color: #909399; line-height: 18px">
                      @{{ author.username }}
                    </div>
                  </div>
                  <div style="
                      width: 120px;
                      display: flex;
                      justify-content: flex-end;
                      align-items: center;
                    ">
                    <el-button circle link :icon="Delete" @click.stop="handleRemoveCoAuthor(author)"></el-button>
                  </div>
                </div>
              </div>
              <el-card style="width: 100%; min-height: 120px; margin-top: 10px" v-if="showCoAuthorCard" @click.stop>
                <el-input v-model="searchAuthorInput" :placeholder="t('article_editor.search_authors')"
                  :prefix-icon="Search" size="large" :autofocus="true" @input="handleSearchCoAuthors(searchAuthorInput)"
                  @click.stop />
                <div style="width: 100%; padding: 10px">
                  <span v-if="searchAuthorResults.length === 0 && !showSearchAuthorLoading">{{
                    t('article_editor.no_results') }}</span>
                  <span v-if="showSearchAuthorLoading">{{ t('article_editor.loading') }}</span>
                  <div v-else @click.stop>
                    <div v-for="item in searchAuthorResults" :key="item.id" class="author-item"
                      @click.stop="handleSelectCoAuthor(item)">
                      <div style="display: flex; align-items: center; width: 40px; border-radius: 50%">
                        <img :src="item.profile_image ? item.profile_image : '/src/assets/avatar.png'"
                          :alt="t('article_editor.author_avatar')" class="author-avatar"
                          style="width: 40px; height: 40px; border-radius: 50%" />
                      </div>
                      <div style="
                          margin-left: 10px;
                          display: flex;
                          flex-direction: column;
                          justify-content: center;
                        ">
                        <div style="font-size: 16px; font-weight: 500; line-height: 20px">
                          {{ item.full_name }}
                        </div>
                        <div style="font-size: 14px; color: #909399; line-height: 18px">
                          @{{ item.username }}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </el-card>
            </template>
          </el-form-item>
          <el-form-item :label="t('article_editor.status')" class="form-label">
            <el-radio-group v-model="publishForm.status">
              <el-radio label="draft" value="draft">{{ t('article_editor.status.draft') }}</el-radio>
              <el-radio v-if="!isContributor" label="published" value="published">{{
                t('article_editor.status.published')
                }}</el-radio>
              <el-radio v-if="!isContributor" label="scheduled" value="scheduled">{{
                t('article_editor.status.scheduled')
                }}</el-radio>
            </el-radio-group>
            <div v-if="isContributor" style="color: #909399; font-size: 12px; margin-top: 4px;">
              {{ t('article_editor.contributor_draft_only') }}
            </div>
          </el-form-item>
          <el-form-item v-if="publishForm.status === 'scheduled'" :label="t('article_editor.publish_date')"
            class="form-label">
            <el-date-picker v-model="publishForm.publishDate" type="datetime"
              :placeholder="t('article_editor.select_datetime')" />
          </el-form-item>
          <el-form-item :label="t('article_editor.article_slug')" class="form-label">
            <el-input v-model="publishForm.slug" :placeholder="t('article_editor.slug_placeholder')" />
          </el-form-item>
          <el-form-item :label="t('article_editor.tags')" class="form-label">
            <el-input-tag v-model="publishForm.tags" :placeholder="t('article_editor.add_tags')"
              @input="handleTagInput" />
            <el-card v-if="showTagsCard" style="
                width: 100%;
                min-height: 120px;
                max-height: 300px;
                overflow-y: auto;
                font-weight: 400;
                padding: 0;
              " body-style="padding: 10px 0 10px 0" shadow="always">
              <div v-if="showTagsCardLoading"
                style="display: flex; justify-content: center; align-items: center; height: 120px">
                <svg class="circular" viewBox="0 0 50 50">
                  <circle class="path" cx="25" cy="25" r="20" fill="none" />
                </svg>
              </div>
              <div v-for="tag in tagSuggestionsList" :key="tag.id"
                @click="handleSelectTag(tag.name, currentTagInputKey)" class="tag-list-item">
                {{ tag.name }}
              </div>
            </el-card>
          </el-form-item>
          <el-form-item :label="t('article_editor.seo_title')" class="form-label">
            <el-input v-model="publishForm.seoTitle" :placeholder="t('article_editor.seo_title_placeholder')" />
          </el-form-item>
          <el-form-item :label="t('article_editor.seo_description')" class="form-label">
            <el-input v-model="publishForm.seoDescription" type="textarea" :autosize="{ minRows: 2, maxRows: 4 }"
              :placeholder="t('article_editor.seo_description_placeholder')" />
          </el-form-item>
          <el-form-item :label="t('article_editor.custom_og_image')" class="form-label">
            <div class="form-tip">
              {{ t('article_editor.og_image_note') }}
            </div>
            <el-upload class="upload-wrapper" drag :http-request="handleCustomUpload" :before-upload="beforeUpload"
              :on-success="handleUploadSuccess" :on-error="handleUploadError" :show-file-list="false" accept="image/*">
              <template v-if="!isUploading && !publishForm.customOGImage">
                <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                <div class="el-upload__text">{{ t('article_editor.drop_file_here') }} <em>{{
                  t('article_editor.click_to_upload') }}</em></div>
              </template>
              <template v-if="isUploading">
                <div style="text-align: center; padding: 20px 0">
                  <el-progress :percentage="uploadProgress" :stroke-width="2"
                    style="width: 200px; margin: 0 auto 10px"></el-progress>
                  <span>{{ uploadProgress }}%</span>
                </div>
              </template>
              <template v-if="publishForm.customOGImage">
                <div class="cover-image-wrapper">
                  <img :src="publishForm.customOGImage" :alt="t('article_editor.cover_image')" class="cover-OGimage" />
                  <el-button :icon="Delete" class="delete-cover-btn" @click="removeOGImage" />
                </div>
              </template>
              <template #tip>
                <div class="el-upload__tip">
                  {{ t('article_editor.og_image_tip') }}
                </div>
              </template>
            </el-upload>
          </el-form-item>
          <el-form-item :label="t('article_editor.table_of_contents')" class="form-label">
            <div class="switch-item">
              <div class="form-tip">{{ t('article_editor.toc_note') }}</div>
              <el-switch v-model="publishForm.tableOfContentsEnabled" active-text="" inactive-text=""
                @change="handleTableOfContentsChange" />
            </div>
          </el-form-item>
          <el-form-item :label="t('article_editor.disable_comments')" class="form-label">
            <div class="switch-item">
              <div class="form-tip">{{ t('article_editor.disable_comments_note') }}</div>
              <el-switch v-model="publishForm.disableComments" active-text="" inactive-text="" />
            </div>
          </el-form-item>
        </el-form>
        <template #footer>
          <div class="drawer-actions">
            <el-button @click="publishDrawerVisible = false">{{ t('article_editor.cancel') }}</el-button>
            <el-button type="primary" @click="handlePublishArticle">{{ t('article_editor.publish') }}</el-button>
          </div>
        </template>
      </el-drawer>

      <!-- 上传图片对话框 -->
      <el-dialog
        v-model="dialogUploadImageFormVisible"
        :title="t('article_editor.add_cover')"
        :width="dialogWidth"
        :fullscreen="isMobile">
        <el-upload class="upload-demo" drag ref="coverUploadRef" :http-request="handleCustomHttpRequest"
          :before-upload="beforeUpload" :on-success="handleCoverUploadSuccess" :on-error="handleCoverUploadError"
          :show-file-list="false" accept="image/*">
          <template v-if="!isUploading">
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">{{ t('article_editor.drop_file_here') }} <em>{{
              t('article_editor.click_to_upload') }}</em></div>
          </template>
          <template v-else>
            <div style="text-align: center; padding: 20px 0">
              <el-progress :percentage="uploadProgress" :stroke-width="2"
                style="width: 200px; margin: 0 auto 10px"></el-progress>
              <span>{{ uploadProgress }}%</span>
            </div>
          </template>
          <template #tip>
            <div class="el-upload__tip">jpg/png files with a size less than 500kb</div>
          </template>
        </el-upload>
      </el-dialog>
    </main>

    <!-- 页脚 -->
    <!-- <footer class="editor-footer">
      <p>© {{ new Date().getFullYear() }} Article Management System</p>
    </footer> -->
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'

// 根元素引用
const rootElement = ref<HTMLElement | null>(null)
import {
  ElUpload,
  ElButton,
  ElDrawer,
  ElForm,
  ElFormItem,
  ElSelect,
  ElOption,
  ElInput,
  ElRadioGroup,
  ElRadio,
  ElDatePicker,
  ElMessage,
  ElTreeSelect,
  ElInputTag,
  ElProgress,
  ElAutocomplete
} from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  Picture,
  Delete,
  Close,
  Postcard,
  CirclePlus,
  QuestionFilled,
  Search
} from '@element-plus/icons-vue'
//import TiptapEditor from '@/components/TiptapEditor.vue'
import SlashEditor from '@/components/SlashEditor.vue'
import { getCategoryList } from '@/api/services/categories'
import { uploadFile } from '@/api/services/common'
import { getSeriesList } from '@/api/services/series'
import { getUserMe } from '@/api/services/user'
import { searchAuthors, searchCoAuthors } from '@/api/services/member'
import { searchTagsFrontend } from '@/api/services/tags'
import { addArticle, createArticle } from '@/api/services/articles'
import { useAppStore } from '@/stores/app'

// 封面图片相关
const coverImageUrl = ref('')
const coverUploadRef = ref<InstanceType<typeof ElUpload>>()
const dialogUploadImageFormVisible = ref(false)
const showAddCoverBtn = ref(true)

// 响应式对话框宽度
const windowWidth = ref(window.innerWidth)

// 监听窗口大小变化
const handleResize = () => {
  windowWidth.value = window.innerWidth
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
  // 组件卸载时清理事件监听
  return () => {
    window.removeEventListener('resize', handleResize)
  }
})

// 判断是否为移动端
const isMobile = computed(() => windowWidth.value < 768)

// 对话框宽度
const dialogWidth = computed(() => {
  if (windowWidth.value < 768) {
    return '95%'
  } else if (windowWidth.value < 1024) {
    return '600px'
  } else {
    return '700px'
  }
})

// Drawer宽度
const drawerSize = computed(() => {
  if (windowWidth.value < 768) {
    return '100%'
  } else if (windowWidth.value < 1024) {
    return '50%'
  } else {
    return '30%'
  }
})

// 标题和副标题相关
const articleTitle = ref('')
const articleSubtitle = ref('')
const showSubtitle = ref(false)
const showSubtitleBtn = ref(true)

// 目录相关
const showArticleTOC = ref(false)
const tableOfContents = ref('')

// 文章内容
const articleContent = ref('')

// 发布抽屉相关
const publishDrawerVisible = ref(false)
// 树形选择器数据
const categoryTreeData = ref<any[]>([])
const changeAuthorCardShow = ref(false)
const showCoAuthorCard = ref(false)
const searchAuthorResults = ref<any[]>([])
const searchAuthorInput = ref('')
const seriesList = ref<any[]>([])
const authorInfo = ref<any>({})
const showSearchAuthorLoading = ref(false)
const tempCoAuthors = ref<string[]>([])
const coAuthorsList = ref<any[]>([])
const tagSuggestionsList = ref<any[]>([])
const showTagsCard = ref(false)
const currentTagInputKey = ref('')
const showTagsCardLoading = ref(false)

// 从HTML内容中提取标题并生成目录结构
interface TableOfContentItem {
  id: string
  text: string
  level: number
  children: TableOfContentItem[]
}

// 生成唯一ID
const generateId = (text: string, level: number, index: number) => {
  return `toc-${level}-${text
    .toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/[^a-z0-9-]/g, '')}-${index}`
}

// 提取目录
const extractTableOfContents = (
  html: string
): { items: TableOfContentItem[]; contentWithIds: string } => {
  const parser = new DOMParser()
  const doc = parser.parseFromString(html, 'text/html')
  const headings = Array.from(doc.querySelectorAll('h1, h2, h3, h4, h5, h6'))

  const items: TableOfContentItem[] = []
  const stack: TableOfContentItem[] = []
  const headingMap = new Map<string, string>() // 存储原始标题到新ID的映射

  headings.forEach((heading, index) => {
    const level = parseInt(heading.tagName.replace('H', ''))
    const text = heading.textContent || ''
    const id = generateId(text, level, index)

    headingMap.set(text, id)

    const item: TableOfContentItem = {
      id,
      text,
      level,
      children: []
    }

    // 维护目录层级结构
    while (stack.length > 0 && stack[stack.length - 1].level >= level) {
      stack.pop()
    }

    if (stack.length === 0) {
      items.push(item)
    } else {
      stack[stack.length - 1].children.push(item)
    }

    stack.push(item)
  })

  // 更新原始HTML中的标题ID
  let contentWithIds = html
  headingMap.forEach((id, text) => {
    // 简单的替换方式，在实际应用中可能需要更复杂的处理
    const headingRegex = new RegExp(`<h([1-6])([^>]*)>${escapeRegExp(text)}`, 'i')
    contentWithIds = contentWithIds.replace(headingRegex, `<h$1$2 id="${id}">${text}`)
  })

  return { items, contentWithIds }
}

// 辅助函数：转义正则表达式特殊字符
const escapeRegExp = (string: string) => {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

// 渲染目录HTML
const renderTableOfContents = (items: TableOfContentItem[]): string => {
  if (items.length === 0) return ''

  let html = '<ul class="toc-list">'

  items.forEach((item) => {
    html += `<li class="toc-item toc-level-${item.level}">`
    html += `<a href="#${item.id}" class="toc-link">${item.text}</a>`

    if (item.children.length > 0) {
      html += renderTableOfContents(item.children)
    }

    html += '</li>'
  })

  html += '</ul>'
  return html
}

// 处理预览功能
const handlePreview = () => {
  // 在新窗口打开预览
  const previewWindow = window.open('', '_blank')
  if (previewWindow) {
    const coverImage = coverImageUrl.value
      ? `<img src="${coverImageUrl.value}" class="cover-image">`
      : ''
    const subtitle = articleSubtitle.value
      ? `<h2 class="article-subtitle">${articleSubtitle.value}</h2>`
      : ''
    let content = articleContent.value || `<p>${t('article_editor.no_content')}</p>`

    let tableOfContentsHtml = ''

    // 如果启用了目录功能，则提取目录
    if (publishForm.tableOfContentsEnabled) {
      const { items, contentWithIds } = extractTableOfContents(content)
      content = contentWithIds

      if (items.length > 0) {
        tableOfContentsHtml = `
          <div class="table-of-contents">
            <h3 class="toc-title">Table of Contents</h3>
            ${renderTableOfContents(items)}
          </div>
        `
      }
    }

    const html = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>Article Preview</title>
        <style>
          body { max-width: 1024px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif; }
          .cover-image { width: 100%; max-height: 400px; object-fit: cover; border-radius: 8px; margin-bottom: 20px; }
          .article-title { font-size: 2rem; font-weight: bold; margin-bottom: 10px; }
          .article-subtitle { font-size: 1.2rem; color: #666; margin-bottom: 30px; }
          .article-content { line-height: 1.6; font-size: 1rem; }

          /* 目录样式 */
          .table-of-contents {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
          }
          .toc-title {
            font-size: 1.25rem;
            margin-top: 0;
            margin-bottom: 15px;
            font-weight: 600;
          }
          .toc-list {
            list-style-type: none;
            padding-left: 0;
            margin: 0;
          }
          .toc-item {
            margin: 5px 0;
          }
          .toc-link {
            color: #495057;
            text-decoration: none;
            display: block;
            padding: 4px 0;
            border-radius: 4px;
            transition: all 0.2s ease;
          }
          .toc-link:hover {
            color: #007bff;
            background-color: #e9ecef;
            padding-left: 5px;
          }
          /* 目录层级缩进 */
          .toc-level-2 { padding-left: 20px; }
          .toc-level-3 { padding-left: 40px; }
          .toc-level-4 { padding-left: 60px; }
          .toc-level-5 { padding-left: 80px; }
          .toc-level-6 { padding-left: 100px; }
        </style>
      </head>
      <body>
        ${coverImage}
        <h1 class="article-title">${articleTitle.value || t('article_editor.untitled_article')}</h1>
        ${subtitle}
        ${tableOfContentsHtml}
        <div class="article-content">${content}</div>
      </body>
      </html>
    `

    previewWindow.document.write(html)
    previewWindow.document.close()
  }
}

// 处理目录功能切换
const handleTableOfContentsChange = (value: boolean) => {
  publishForm.tableOfContentsEnabled = value
  generateTableOfContents()
}
// 生成目录
const generateTableOfContents = () => {
  let content = articleContent.value || `<p>${t('article_editor.no_content')}</p>`

  let tableOfContentsHtml = ''

  // 如果启用了目录功能，则提取目录
  if (publishForm.tableOfContentsEnabled) {
    const { items, contentWithIds } = extractTableOfContents(content)
    content = contentWithIds

    if (items.length > 0) {
      tableOfContentsHtml = `
          <h3 class="toc-title">Table of Contents</h3>
            ${renderTableOfContents(items)}
        `
      articleContent.value = content
      showArticleTOC.value = true
      tableOfContents.value = tableOfContentsHtml
    }
  } else {
    // 如果禁用了目录功能，移除目录HTML
    showArticleTOC.value = false
    tableOfContents.value = ''
  }
}

// 打开发布抽屉
const openPublishDrawer = () => {
  publishDrawerVisible.value = true
}

// 处理添加封面
const handleAddCover = () => {
  dialogUploadImageFormVisible.value = true
}

// 处理封面上传点击
const handleCoverUploadClick = () => {
  coverUploadRef.value?.submit()
}

// 上传前验证
const beforeUpload = (file: File) => {
  const isJPG = file.type === 'image/jpeg' || file.type === 'image/png'
  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isJPG) {
    ElMessage.error('只能上传JPG/PNG格式的图片')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过2MB')
    return false
  }
  return true
}
//coverImageUrl.value = 'https://images.pexels.com/photos/196655/pexels-photo-196655.jpeg'
// 上传成功处理
const handleCoverUploadSuccess = (response: any) => {
  coverImageUrl.value = response.full_url // 假设后端返回图片URL
  dialogUploadImageFormVisible.value = false
  showAddCoverBtn.value = false
  ElMessage.success(t('article_editor.cover_image_uploaded'))
}

// 上传失败处理
const handleCoverUploadError = (error: any) => {
  ElMessage.error(t('article_editor.upload_failed'))
  isUploading.value = false
}

// 自定义HTTP请求处理
const handleCustomHttpRequest = async (options: any) => {
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

    if (res.code === 1) {
      options.onSuccess(res.data)
    } else {
      options.onError(new Error(res.msg || '上传失败'))
    }
  } catch (error) {
    options.onError(error)
  } finally {
    isUploading.value = false
  }
}

// 移除封面图片
const removeCoverImage = () => {
  coverImageUrl.value = ''
  showAddCoverBtn.value = true
}

// 切换副标题显示
const toggleSubtitle = () => {
  showSubtitle.value = !showSubtitle.value
  showSubtitleBtn.value = !showSubtitleBtn.value
  if (!showSubtitle.value) {
    articleSubtitle.value = ''
  }
}

// 处理发布抽屉关闭
const handleClosePublishDrawer = (done: () => void) => {
  done()
}

// 辅助函数：将逗号分隔的字符串转换为数组
const commaSeparatedStringToArray = (str: string): string[] => {
  if (!str || typeof str !== 'string') {
    return []
  }

  return str
    .split(',')
    .map((item) => item.trim())
    .filter((item) => item !== '')
}

const publishFormRef = ref<FormInstance>()
const appStore = useAppStore()
const { t } = useI18n()

// 用户角色检查
const isContributor = computed(() => appStore.userRole === 'Contributor')
const isAuthor = computed(() => appStore.userRole === 'Author')
const isAdmin = computed(() => appStore.userRole === 'Admin')

const publishForm = reactive({
  category: '',
  series: '',
  author: '',
  coAuthors: [] as string[],
  tags: [] as string[],
  status: 'draft',
  publishDate: new Date(),
  customOGImage: '',
  tableOfContentsEnabled: false,
  disableComments: false,
  slug: '',
  seoTitle: '',
  seoDescription: ''
})
// 发布表单验证规则
const publishFormRules = {
  category: [{ required: true, message: '请选择分类', trigger: 'blur' }],
  // series: [{ required: true, message: '请选择系列', trigger: 'blur' }],
  author: [{ required: true, message: '请选择作者', trigger: 'blur' }]
  // coAuthors: [{ required: true, message: '请选择协作者', trigger: 'blur' }],
  // tags: [{ required: true, message: '请选择标签', trigger: 'blur' }],
}
// 处理文章发布
const handlePublishArticle = async () => {
  if (!publishFormRef.value) {
    return
  }
  try {
    // 正确处理Element Plus表单验证
    await publishFormRef.value.validate()

    // 获取用户角色
    const userRole = appStore.userRole

    // Contributor 只能创建草稿
    let articleStatus = publishForm.status
    if (userRole === 'Contributor') {
      articleStatus = 'draft'
    }

    const articleData = {
      title: articleTitle.value.trim() ? articleTitle.value : 'Untitled',
      subtitle: articleSubtitle.value,
      content: articleContent.value,
      cover: coverImageUrl.value,
      category_id: Number(publishForm.category),
      series_id: publishForm.series ? Number(publishForm.series) : null,
      author: publishForm.author,
      co_authors: publishForm.coAuthors ? publishForm.coAuthors.join(',') : null,
      tags: publishForm.tags ? publishForm.tags.join(',') : null,
      status: articleStatus,
      pub_time: publishForm.publishDate
        ? (publishForm.publishDate.getTime() / 1000).toFixed(0)
        : null,
      og_image: publishForm.customOGImage,
      disable_comments: publishForm.disableComments,
      enable_table_content: publishForm.tableOfContentsEnabled,
      slug: publishForm.slug,
      seo_title: publishForm.seoTitle,
      seo_desc: publishForm.seoDescription
    }

    // 根据角色选择不同的API
    const apiCall = userRole === 'Admin' ? addArticle(articleData) : createArticle(articleData)

    await apiCall
      .then((res: any) => {
        if (res.code === 1) {
          ElMessage.success(t('article_editor.published_success'))
          publishDrawerVisible.value = false
        }
      })
      .catch((err: any) => {
        ElMessage.error(err.msg || t('article_editor.publish_failed'))
      })
  } catch (error) {
    // 验证失败时自动显示错误信息，这里可以添加额外的错误处理
    return
  }
}

// 生命周期钩子
onMounted(() => {
  // 应用主题设置
  applyTheme()

  // 加载父分类数据
  loadParentCategories()
  loadSeriesData()
  loadUserInfo()
})

// 应用主题设置
const applyTheme = () => {
  if (!rootElement.value) return

  // 从 user_config 中读取主题设置
  const userConfigStr = localStorage.getItem('user_config')
  if (userConfigStr) {
    try {
      const userConfig = JSON.parse(userConfigStr)
      const themeMode = userConfig.themeMode || 'light'
      const followSystem = userConfig.followSystem !== undefined ? userConfig.followSystem : true

      let isDark = false

      if (followSystem) {
        // 跟随系统设置
        isDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      } else {
        // 使用用户配置的主题模式
        isDark = themeMode === 'dark'
      }

      if (isDark) {
        rootElement.value.classList.add('dark')
      } else {
        rootElement.value.classList.remove('dark')
      }
    } catch (e) {
      console.error('解析用户配置失败:', e)
    }
  }
}

// 加载父分类数据
const loadParentCategories = async () => {
  try {
    // 实际项目中从API获取分类列表
    const res = await getCategoryList()
    if (res.code === 1) {
      // 将扁平数据转换为树形结构
      const categories = res.data

      // 创建分类映射表用于快速查找
      const categoryMap = new Map<string, any>()

      // 初始化顶级分类数组
      const rootCategories: any[] = []

      // 处理所有分类，创建映射并找出顶级分类
      categories.forEach((category: any) => {
        const { id, name, pid } = category
        const categoryNode = {
          value: id.toString(),
          label: name,
          children: []
        }
        categoryMap.set(id.toString(), categoryNode)

        // 顶级分类：pid为0或null或空
        if (!pid || pid === 0 || pid === '0') {
          rootCategories.push(categoryNode)
        }
      })

      // 构建树形结构
      categories.forEach((category: any) => {
        const { id, pid } = category
        const categoryNode = categoryMap.get(id.toString())

        // 非顶级分类需要找到其父分类并添加为子节点
        if (pid && pid !== 0 && pid !== '0') {
          const parentNode = categoryMap.get(pid.toString())
          if (parentNode) {
            parentNode.children.push(categoryNode)
          }
        }
      })

      // 更新树形数据，包含"无（顶级分类）"选项和所有层级分类
      categoryTreeData.value = [...rootCategories]
    }
  } catch (error) {
    console.error('加载分类数据失败:', error)
    ElMessage.error('加载分类数据失败，请稍后重试')
  }
}

// 加载文章系列数据
const loadSeriesData = async () => {
  try {
    const res = await getSeriesList()
    if (res.code === 1) {
      seriesList.value = res.data
    }
  } catch (error) {
    console.error('加载文章系列数据失败:', error)
    ElMessage.error('加载文章系列数据失败，请稍后重试')
  }
}

// 获取当前登录用户信息
const loadUserInfo = async () => {
  try {
    const res = await getUserMe()
    if (res.code === 1) {
      console.log(res)
      publishForm.author = res.data.id
      authorInfo.value = res.data
    }
  } catch (error) {
    console.error('加载用户信息失败:', error)
    ElMessage.error('加载用户信息失败，请稍后重试')
  }
}

// 处理作者改变
const handleChangeAuthor = () => {
  changeAuthorCardShow.value = true
}

// 处理抽屉点击事件，点击空白处隐藏作者搜索卡片
const handleDrawerClick = () => {
  // 延迟隐藏，确保点击事件先触发
  setTimeout(() => {
    changeAuthorCardShow.value = false
    showCoAuthorCard.value = false
  }, 0)
}

const handleSearchAuthors = async (keyword: string) => {
  showSearchAuthorLoading.value = true
  if (keyword.length < 3) {
    searchAuthorResults.value = []
    setTimeout(() => {
      showSearchAuthorLoading.value = false
    }, 1500)
    return
  }
  try {
    const res = await searchAuthors(keyword, Number(publishForm.author))
    if (res.code === 1) {
      console.log(res)
      searchAuthorResults.value = res.data
      showSearchAuthorLoading.value = false
    }
  } catch (error) {
    // console.error('搜索作者失败:', error)
    // ElMessage.error('搜索作者失败，请稍后重试')
    searchAuthorResults.value = []
    showSearchAuthorLoading.value = false
  }
}

const handleSearchCoAuthors = async (keyword: string) => {
  showSearchAuthorLoading.value = true
  if (keyword.length < 3) {
    searchAuthorResults.value = []
    setTimeout(() => {
      showSearchAuthorLoading.value = false
    }, 1500)
    return
  }
  try {
    const res = await searchCoAuthors(keyword)
    if (res.code === 1) {
      console.log(res)
      searchAuthorResults.value = res.data
      showSearchAuthorLoading.value = false
    }
  } catch (error) {
    // console.error('搜索作者失败:', error)
    // ElMessage.error('搜索作者失败，请稍后重试')
    searchAuthorResults.value = []
    showSearchAuthorLoading.value = false
  }
}

const handleSelectAuthor = (author: any) => {
  publishForm.author = author.id
  authorInfo.value = author
  changeAuthorCardShow.value = false
  searchAuthorResults.value = []
  searchAuthorInput.value = ''
}

const handleSelectCoAuthor = (author: any) => {
  // 检查作者是否已添加
  if (tempCoAuthors.value.includes(author.id)) {
    ElMessage.error(t('article_editor.author_exists'))
    return
  }
  if (tempCoAuthors.value.length >= 4) {
    ElMessage.error(t('article_editor.max_co_authors'))
    return
  }
  tempCoAuthors.value.push(author.id)
  coAuthorsList.value.push(author)

  publishForm.coAuthors = [...tempCoAuthors.value]

  showCoAuthorCard.value = false
  searchAuthorResults.value = []
  searchAuthorInput.value = ''

  ElMessage.success(t('article_editor.co_author_added'))
}

const handleRemoveCoAuthor = (author: any) => {
  tempCoAuthors.value = tempCoAuthors.value.filter((id: string) => id !== author.id)
  coAuthorsList.value = coAuthorsList.value.filter((item: any) => item.id !== author.id)
  publishForm.coAuthors = [...tempCoAuthors.value]
}

// 上传进度
const uploadProgress = ref(0)
const isUploading = ref(false)

// 上传OG图片文件
const handleCustomUpload = async (options: any) => {
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

    if (res.code === 1) {
      options.onSuccess(res.data)
    } else {
      options.onError(new Error(res.msg || '上传失败'))
    }
  } catch (error) {
    options.onError(error)
  } finally {
    isUploading.value = false
  }
}

// 发布文章上传OG图片成功处理
const handleUploadSuccess = (response: any, file: any) => {
  //publishForm.customOGImage = URL.createObjectURL(file.raw)
  publishForm.customOGImage = response.full_url
  ElMessage.success(t('article_editor.image_uploaded'))
}

// 上传失败处理
const handleUploadError = (error: any) => {
  ElMessage.error(t('article_editor.upload_failed'))
  isUploading.value = false
}

// 移除封面图片
const removeOGImage = () => {
  publishForm.customOGImage = ''
}

const handleTagInput = (input: string) => {
  if (input.length === 0) {
    tagSuggestionsList.value = []
    showTagsCard.value = false
    showTagsCardLoading.value = false
    return
  }
  showTagsCard.value = true
  showTagsCardLoading.value = true
  // if (input.length < 3) {
  //   tagSuggestionsList.value = []
  //   return
  // }
  getTagSuggestions(input)
  currentTagInputKey.value = input
  console.log(input)

  // const results = input
  //   ? tagOptions.filter((tag) => tag.toLowerCase().includes(input.toLowerCase()))
  //   : tagOptions
  // tagSuggestionsList.value = results
  // if (results.length === 0) {
  //   showTagsCard.value = false
  // }
}

const getTagSuggestions = async (input: string) => {
  try {
    const res = await searchTagsFrontend(input)
    if (res.code === 1) {
      showTagsCardLoading.value = false
      tagSuggestionsList.value = res.data
    }
  } catch (error) {
    console.error('获取标签建议失败:', error)
    // ElMessage.error('获取标签建议失败，请稍后重试')
    tagSuggestionsList.value = []
    showTagsCard.value = false
    showTagsCardLoading.value = false
  }
}

const handleSelectTag = (tag: string, input: string) => {
  publishForm.tags = publishForm.tags.filter((t: string) => t !== input)
  if (!publishForm.tags.includes(tag)) {
    publishForm.tags.push(tag)
  }
  tagSuggestionsList.value = []
  showTagsCard.value = false
}
</script>

<style scoped>
.article-editor-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.8rem 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border-bottom: 1px solid var(--el-menu-border-color);
  background-image: radial-gradient(transparent 1px, var(--el-menu-bg-color) 1px);
  background-size: 4px 4px;
  backdrop-filter: saturate(50%) blur(4px);
  color: var(--el-color-primary);
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.logo-img {
  height: 2.5rem;
}

.site-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.editor-content {
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
  overflow-y: auto;
}

.editor-footer {
  padding: 1rem 2rem;
  text-align: center;
  color: #64748b;
  font-size: 0.875rem;
  border-top: 1px solid #e5e7eb;
}

.top-actions {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  align-items: flex-end;
}

.cover-upload-area {
  text-align: left;
}

.subtitle-action {
  text-align: right;
}

.cover-image-wrapper {
  position: relative;
  display: inline-block;
  margin-bottom: 15px;
  width: 100%;
}

.cover-image {
  width: 100%;
  max-height: 400px;
  object-fit: cover;
  border-radius: 8px;
}

.cover-OGimage {
  width: 100%;
  max-height: 200px;
  object-fit: cover;
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

.add-cover-btn {
  margin-right: 15px;
}

.article-title-area {
  margin-bottom: 20px;
}

.article-title-input {
  width: 100%;
  font-size: 2.25rem;
  resize: none;
  border: none;
  padding: 10px 0;
  margin-bottom: 15px;
  appearance: none;
  overflow: hidden;
  background-color: transparent;
  font-family:
    'Suisse Intl',
    ui-sans-serif,
    system-ui,
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    Roboto,
    'Helvetica Neue',
    Arial,
    'Noto Sans',
    sans-serif,
    'Apple Color Emoji',
    'Segoe UI Emoji',
    'Segoe UI Symbol',
    'Noto Color Emoji';
  font-weight: 700;
  color: rgb(24 24 27 / 1);
  outline: transparent solid 2px;
  outline-offset: 2px;
  line-height: 1.375 !important;
}

.subtitle-container {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
  align-items: center;
}

.article-subtitle-input {
  flex-grow: 1;
  font-size: 1.5rem;
  font-weight: 500;
  color: #666;
  border: none;
  padding: 8px 0;
  margin-right: 10px;
  resize: none;
  appearance: none;
  background-color: transparent;
  font-family:
    'Suisse Intl',
    ui-sans-serif,
    system-ui,
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    Roboto,
    'Helvetica Neue',
    Arial,
    'Noto Sans',
    sans-serif,
    'Apple Color Emoji',
    'Segoe UI Emoji',
    'Segoe UI Symbol',
    'Noto Color Emoji';
  font-size: 1.5rem;
  font-weight: 500;
  color: rgb(63 63 70 / 1);
  outline: transparent solid 2px;
  outline-offset: 2px;
  line-height: 1.375 !important;
}

.delete-subtitle-btn {
  border: none;
  background: transparent;
}

.editor-container {
  margin-bottom: 20px;
  border-radius: 8px;
  /* 移除 overflow: hidden 以允许 bubbleMenu 正常显示 */
  /* overflow: hidden; */
  position: relative;
}

.drawer-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  gap: 10px;
}

.switch-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  width: 100%;
  color: var(--el-color-regular-text);
}

.form-tip {
  color: var(--el-color-regular-text);
  font-weight: 200;
  line-height: 1.375rem;
}

.form-label {
  font-weight: 600;
  color: var(--el-color-secondary-text);
}

.upload-wrapper {
  position: relative;
  width: 100%;
  margin-top: 1rem;
}

.author-item {
  display: flex;
  width: 100%;
  align-items: center;
  cursor: pointer;
  margin-top: 10px;
  padding: 10px;
}

.author-item:hover {
  background-color: #f5f7fa;
}

.tag-list-card {
  width: 100%;
  font-weight: 200;
  padding: 0;
}

.tag-list-item {
  width: 100%;
  padding-left: 20px;
}

.tag-list-item:hover {
  background-color: #f5f7fa;
  cursor: pointer;
}

.circular {
  display: inline;
  height: 30px;
  width: 30px;
  animation: loading-rotate 2s linear infinite;
}

.path {
  animation: loading-dash 1.5s ease-in-out infinite;
  stroke-dasharray: 90, 150;
  stroke-dashoffset: 0;
  stroke-width: 2;
  stroke: var(--el-color-primary);
  stroke-linecap: round;
}

/* 目录样式 - 使用深度选择器让样式应用到v-html内容 */
.table-of-contents {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
}

.table-of-contents>>>.toc-title {
  font-size: 1.25rem;
  margin-top: 0;
  margin-bottom: 15px;
  font-weight: 600;
}

.table-of-contents>>>.toc-list {
  list-style-type: none;
  padding-left: 0;
  margin: 0;
}

.table-of-contents>>>.toc-item {
  margin: 5px 0;
}

.table-of-contents>>>.toc-link {
  color: #495057;
  text-decoration: none;
  display: block;
  padding: 4px 0;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.table-of-contents>>>.toc-link:hover {
  color: #007bff;
  background-color: #e9ecef;
  padding-left: 5px;
}

/* 目录层级缩进 */
.table-of-contents>>>.toc-level-2 {
  padding-left: 20px;
}

.table-of-contents>>>.toc-level-3 {
  padding-left: 40px;
}

.table-of-contents>>>.toc-level-4 {
  padding-left: 60px;
}

.table-of-contents>>>.toc-level-5 {
  padding-left: 80px;
}

.table-of-contents>>>.toc-level-6 {
  padding-left: 100px;
}
</style>
