<template>
  <div class="articles-management">
    <div class="page-header">
      <h1>{{ t('admin.article.list.title') }}</h1>
      <p>{{ t('admin.article.list.subtitle') }}</p>
    </div>

    <!-- Status tabs -->
    <el-tabs v-model="activeStatus" class="status-tabs" @tab-click="handleStatusChange">
      <el-tab-pane
        :label="t('admin.article.list.tab.published') + ` (${totalPublished})`"
        name="published"
      />
      <el-tab-pane :label="t('admin.article.list.tab.draft') + ` (${totalDrafts})`" name="drafts" />
      <el-tab-pane
        :label="t('admin.article.list.tab.scheduled') + ` (${totalScheduled})`"
        name="scheduled"
      />
      <el-tab-pane
        :label="t('admin.article.list.tab.deleted') + ` (${totalDeleted})`"
        name="deleted"
      />
    </el-tabs>

    <!-- Search and filter -->
    <div class="search-filter">
      <el-input
        v-model="inputSearch"
        :placeholder="t('admin.article.list.search_placeholder')"
        prefix-icon="Search"
        class="search-input"
        @input="handleSearch"
      />
      <el-button class="filter-button" icon="Filter" @click="handleShowFilterDialog">{{
        t('admin.article.list.filter')
      }}</el-button>

      <!-- Filter Dialog -->
      <el-dialog
        v-model="showFilterDialog"
        :title="t('admin.article.list.filter_articles')"
        width="400px"
        :close-on-click-modal="false"
      >
        <el-tabs v-model="activeFilterTab" class="filter-tabs" @tab-click="handleFilterTabClick">
          <el-tab-pane :label="t('admin.article.list.authors')" name="authors" />
          <el-tab-pane :label="t('admin.article.list.tags')" name="tags" />
          <el-tab-pane :label="t('admin.article.list.date.tab_title')" name="date" />
        </el-tabs>

        <div class="filter-content">
          <template v-if="activeFilterTab === 'authors'">
            <el-input
              v-model="authorSearchTerm"
              :placeholder="t('admin.article.list.author_search_placeholder')"
              prefix-icon="Search"
              class="author-search"
              @input="filterAuthors"
            />
            <el-checkbox-group v-model="selectedAuthors" class="authors-list">
              <el-checkbox
                v-for="author in authorsList"
                :key="author.id"
                :label="author.full_name"
                :avatar="author.profile_image"
                :value="author.id"
              />
            </el-checkbox-group>
          </template>

          <template v-if="activeFilterTab === 'tags'">
            <el-input
              v-model="tagSearchTerm"
              :placeholder="t('admin.article.list.tag_search_placeholder')"
              prefix-icon="Search"
              class="author-search"
              @input="filterTags"
            />
            <el-checkbox-group v-model="selectedTags" class="tags-list">
              <el-checkbox
                v-for="tag in tagsList"
                :key="tag.id"
                :label="tag.name"
                :value="tag.id"
              />
            </el-checkbox-group>
          </template>

          <template v-if="activeFilterTab === 'date'">
            <el-radio-group
              v-model="selectedDateRange"
              class="date-radio-group"
              @change="handleDateRangeChange"
            >
              <el-radio :label="t('admin.article.list.date.previous_day')" value="previousDay">
                {{ t('admin.article.list.date.previous_day') }}
              </el-radio>
              <el-radio :label="t('admin.article.list.date.past_3_day')" value="past3days">
                {{ t('admin.article.list.date.past_3_day') }}
              </el-radio>
              <el-radio :label="t('admin.article.list.date.past_week')" value="pastWeek">
                {{ t('admin.article.list.date.past_week') }}
              </el-radio>
              <el-radio :label="t('admin.article.list.date.past_month')" value="pastMonth">
                {{ t('admin.article.list.date.past_month') }}
              </el-radio>
              <el-radio :label="t('admin.article.list.date.custome_date')" value="customDate">
                {{ t('admin.article.list.date.custome_date') }}
              </el-radio>
              <el-radio
                :label="t('admin.article.list.date.custome_date_range')"
                value="customRange"
              >
                {{ t('admin.article.list.date.custome_date_range') }}
              </el-radio>
            </el-radio-group>

            <!-- Custom Date Picker -->
            <el-date-picker
              v-if="selectedDateRange === 'customDate' && (showDatePicker || customDate)"
              v-model="customDate"
              type="date"
              @change="handleDateConfirm"
              class="custom-date-picker"
            />

            <!-- Custom Range Picker -->
            <el-date-picker
              v-if="selectedDateRange === 'customRange' && (showDatePicker || customDateRange)"
              v-model="customDateRange"
              type="daterange"
              range-separator="to"
              :start-placeholder="t('admin.article.list.date.start_date')"
              :end-placeholder="t('admin.article.list.date.end_date')"
              @change="handleDateConfirm"
              class="custom-date-picker"
            />
          </template>
        </div>

        <template #footer>
          <div class="dialog-footer">
            <el-button @click="showFilterDialog = false">
              {{ t('admin.general.btn.cancel') }}
            </el-button>
            <el-button type="primary" @click="applyFilters">
              {{ t('admin.general.btn.apply') }}
            </el-button>
          </div>
        </template>
      </el-dialog>
    </div>

    <template v-if="isMobile">
      <el-card v-for="article in articles" :key="article.id" class="mobile-article-card">
        <div class="article-title">
          <div class="title-text">
            {{ article.title }}
            <el-tag v-if="article.is_featured" type="danger">
              {{ t('admin.article.list.table.head.featured') }}
            </el-tag>
            <el-tag v-if="article.is_recommend" type="warning">
              {{ t('admin.article.list.table.head.recommend') }}
            </el-tag>
            <el-tag v-if="article.is_pin" type="primary">
              {{ t('admin.article.list.table.head.top') }}
            </el-tag>
          </div>
          <div class="meta-info">
            <el-avatar
              :size="24"
              :src="
                article.author_profile_image
                  ? article.author_profile_image
                  : '/src/assets/avatar.png'
              "
              class="author-avatar"
            />
            <span class="author-name">{{ article.author_full_name }}</span> ·
            <span class="publish-date">{{ formatDateTime(article.createtime) }}</span>
          </div>
        </div>

        <template #footer>
          <div class="actions">
            <el-button
              icon="Edit"
              size="default"
              class="edit-button"
              @click="handleEdit(article)"
              circle
            />
            <el-dropdown
              @command="onArticleAction(article)"
            >
              <el-button icon="More" size="default" class="more-button" circle text />
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-if="activeStatus === 'published'" command="pin">
                    <el-icon><Coordinate /></el-icon>
                    {{
                      article.is_pin
                        ? t('admin.article.list.table.menu.unpin')
                        : t('admin.article.list.table.menu.pin_to_blog')
                    }}
                  </el-dropdown-item>
                  <el-dropdown-item v-if="activeStatus === 'published'" command="recommend">
                    <el-icon><Coordinate /></el-icon>
                    {{
                      article.is_recommend
                        ? t('admin.article.list.table.menu.un_recommend')
                        : t('admin.article.list.table.menu.recommend_to_home')
                    }}
                  </el-dropdown-item>
                  <el-dropdown-item v-if="activeStatus === 'published'" command="featured">
                    <el-icon><Coordinate /></el-icon>
                    {{
                      article.is_featured
                        ? t('admin.article.list.table.menu.un_featured')
                        : t('admin.article.list.table.menu.featured')
                    }}
                  </el-dropdown-item>
                  <el-dropdown-item v-if="activeStatus === 'drafts'" command="preview">
                    <el-icon><View /></el-icon> {{ t('admin.article.list.table.menu.preview') }}
                  </el-dropdown-item>
                  <el-dropdown-item v-if="activeStatus === 'scheduled'" command="cancel">
                    <el-icon><Close /></el-icon> {{ t('admin.article.list.table.menu.cancel') }}
                  </el-dropdown-item>
                  <el-dropdown-item v-if="activeStatus === 'deleted'" command="restore">
                    <el-icon><Refresh /></el-icon> {{ t('admin.article.list.table.menu.restore') }}
                  </el-dropdown-item>
                  <el-dropdown-item command="delete" :danger="activeStatus !== 'deleted'">
                    <el-icon><Delete /></el-icon>
                    {{
                      activeStatus === 'deleted'
                        ? t('admin.article.list.table.menu.permanently_delete')
                        : t('admin.article.list.table.menu.delete')
                    }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </template>
      </el-card>
    </template>
    <!-- Articles table -->
    <el-table
      v-else
      :data="articles"
      class="articles-table"
      :header-cell-style="{
        backgroundColor: '#fafafa',
        fontWeight: 800,
        fontSize: '1rem',
        padding: '12px 14px'
      }"
      :cell-style="{
        padding: '12px 14px'
      }"
    >
      <template #empty>
        <div class="empty-state">
          <el-icon class="empty-icon">
            <component :is="getEmptyStateIcon()" />
          </el-icon>
          <h3 class="empty-title">{{ getEmptyStateTitle() }}</h3>
          <p class="empty-description">{{ getEmptyStateDescription() }}</p>
        </div>
      </template>
      <el-table-column prop="title" :label="t('admin.article.list.table.head.title')">
        <template #default="scope">
          <div class="article-title">
            <div class="title-text">{{ scope.row.title }}</div>
            <div class="meta-info">
              <el-avatar
                :size="24"
                :src="
                  scope.row.author_profile_image
                    ? scope.row.author_profile_image
                    : '/src/assets/avatar.png'
                "
                class="author-avatar"
              />
              <span class="author-name">{{ scope.row.author_full_name }}</span> ·
              <span class="publish-date">{{ formatDateTime(scope.row.createtime) }}</span>
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="slug" :label="t('admin.article.list.table.head.slug')">
        <template #default="scope"> /{{ scope.row.slug }} </template>
      </el-table-column>
      <el-table-column prop="is_pin" :label="t('admin.article.list.table.head.top')" width="100">
        <template #default="scope">
          <el-tag v-if="scope.row.is_pin" type="success">Yes</el-tag>
          <el-tag v-else type="danger">No</el-tag>
        </template>
      </el-table-column>
      <el-table-column
        prop="is_featured"
        :label="t('admin.article.list.table.head.featured')"
        width="120"
      >
        <template #default="scope">
          <el-tag v-if="scope.row.is_featured" type="success">Yes</el-tag>
          <el-tag v-else type="danger">No</el-tag>
        </template>
      </el-table-column>
      <el-table-column
        prop="is_recommend"
        :label="t('admin.article.list.table.head.recommend')"
        width="150"
      >
        <template #default="scope">
          <el-tag v-if="scope.row.is_recommend" type="success">Yes</el-tag>
          <el-tag v-else type="danger">No</el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('admin.article.list.table.head.actions')" width="150">
        <template #default="scope">
          <div class="actions">
            <el-button
              icon="Edit"
              size="default"
              class="edit-button"
              @click="handleEdit(scope.row)"
              circle
            />
            <el-dropdown
              @command="onArticleAction(scope.row)"
            >
              <el-button icon="More" size="default" class="more-button" circle text />
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-if="activeStatus === 'published'" command="pin">
                    <el-icon><Coordinate /></el-icon>
                    {{
                      scope.row.is_pin
                        ? t('admin.article.list.table.menu.unpin')
                        : t('admin.article.list.table.menu.pin_to_blog')
                    }}
                  </el-dropdown-item>
                  <el-dropdown-item v-if="activeStatus === 'published'" command="recommend">
                    <el-icon><Coordinate /></el-icon>
                    {{
                      scope.row.is_recommend
                        ? t('admin.article.list.table.menu.un_recommend')
                        : t('admin.article.list.table.menu.recommend_to_home')
                    }}
                  </el-dropdown-item>
                  <el-dropdown-item v-if="activeStatus === 'published'" command="featured">
                    <el-icon><Coordinate /></el-icon>
                    {{
                      scope.row.is_featured
                        ? t('admin.article.list.table.menu.un_featured')
                        : t('admin.article.list.table.menu.featured')
                    }}
                  </el-dropdown-item>
                  <el-dropdown-item v-if="activeStatus === 'drafts'" command="preview">
                    <el-icon><View /></el-icon> {{ t('admin.article.list.table.menu.preview') }}
                  </el-dropdown-item>
                  <el-dropdown-item v-if="activeStatus === 'scheduled'" command="cancel">
                    <el-icon><Close /></el-icon> {{ t('admin.article.list.table.menu.cancel') }}
                  </el-dropdown-item>
                  <el-dropdown-item v-if="activeStatus === 'deleted'" command="restore">
                    <el-icon><Refresh /></el-icon> {{ t('admin.article.list.table.menu.restore') }}
                  </el-dropdown-item>
                  <el-dropdown-item command="delete" :danger="activeStatus !== 'deleted'">
                    <el-icon><Delete /></el-icon>
                    {{
                      activeStatus === 'deleted'
                        ? t('admin.article.list.table.menu.permanently_delete')
                        : t('admin.article.list.table.menu.delete')
                    }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :page-sizes="[10, 20, 30, 50]"
      size="default"
      :disabled="false"
      :background="true"
      layout="total, sizes, prev, pager, next, jumper"
      :total="totalArticles"
      :hide-on-single-page="true"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
      style="margin-top: 20px"
    />
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { formatDateTime } from '@/utils/dateUtils'

// Initialize router at the top level
const router = useRouter()
import {
  Coordinate,
  View,
  Close,
  Refresh,
  Delete,
  Search,
  Filter,
  Edit,
  More,
  Calendar,
  Document,
  DocumentDelete,
  DocumentChecked
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getManageArticlesList,
  getArticlesStatusCount,
  getArticleAuthorsList,
  getArticleTagsList,
  deleteArticle,
  updateArticleStatus,
  updateArticleOpStatus,
  previewDraftArticle
} from '@/api/services/articles'
import type { ArticleSearchParams, ArticleTimeSearchParams } from '@/api/services/articles'

interface Article {
  id: number
  title: string
  author: string
  authorAvatar: string
  date: string
  slug: string
  is_pin: number
  is_featured: number
  is_recommend: number
  author_full_name: string
  author_profile_image: string
  createtime: number
}

// Initialize i18n
const { t } = useI18n()

// Date filter state
const selectedDateRange = ref<string>('')
const customDate = ref<Date | null>(null)
const customDateRange = ref<[Date | null, Date | null]>([null, null])
const showDatePicker = ref<boolean>(false)
const hasDateFilter = ref<boolean>(true)

// Pagination state
const currentPage = ref(1)
const pageSize = ref(10)
const totalArticles = ref(0)
const articles = ref<Article[]>([])
const currentPage1 = ref(1)
const currentPage2 = ref(1)
const currentPage3 = ref(1)
const currentPage4 = ref(1)
const pageSize1 = ref(10)
const pageSize2 = ref(10)
const pageSize3 = ref(10)
const pageSize4 = ref(10)
const totalPublished = ref(0)
const totalDrafts = ref(0)
const totalScheduled = ref(0)
const totalDeleted = ref(0)
const inputSearch = ref('')

// Date filter methods
const handleDateRangeChange = (range: string) => {
  selectedDateRange.value = range
  showDatePicker.value = ['customDate', 'customRange'].includes(range)
}

// Empty state methods
const getEmptyStateIcon = () => {
  switch (activeStatus.value) {
    case 'published':
      return DocumentChecked
    case 'drafts':
      return Document
    case 'scheduled':
      return Calendar
    case 'deleted':
      return DocumentDelete
    default:
      return Document
  }
}

const handleDateConfirm = () => {
  hasDateFilter.value = true
  showDatePicker.value = false
}

const clearDateFilter = () => {
  selectedDateRange.value = 'past3days'
  customDate.value = null
  customDateRange.value = [null, null]
  showDatePicker.value = false
  hasDateFilter.value = false
}

const getEmptyStateTitle = () => {
  switch (activeStatus.value) {
    case 'published':
      return t('admin.article.list.empty.published.title')
    case 'drafts':
      return t('admin.article.list.empty.draft.title')
    case 'scheduled':
      return t('admin.article.list.empty.scheduled.title')
    case 'deleted':
      return t('admin.article.list.empty.deleted.title')
    default:
      return t('admin.article.list.empty.default.title')
  }
}

const getEmptyStateDescription = () => {
  switch (activeStatus.value) {
    case 'published':
      return t('admin.article.list.empty.published.description')
    case 'drafts':
      return t('admin.article.list.empty.draft.description')
    case 'scheduled':
      return t('admin.article.list.empty.scheduled.description')
    case 'deleted':
      return t('admin.article.list.empty.deleted.description')
    default:
      return t('admin.article.list.empty.default.description')
  }
}

// State
const activeStatus = ref('published')
const showFilterDialog = ref(false)
const activeFilterTab = ref('authors')
const selectedAuthors = ref<string[]>([])
const selectedTags = ref<string[]>([])
const authorsList = ref<any[]>([])
const tagsList = ref<any[]>([])
const authorSearchTerm = ref('')
const tagSearchTerm = ref('')

// Expose variables to template
defineExpose({
  selectedDateRange,
  customDate,
  customDateRange,
  showDatePicker,
  hasDateFilter,
  handleDateRangeChange,
  handleDateConfirm,
  clearDateFilter
})

// Mock data
// const articles = ref([
//   {
//     id: 1,
//     title: '第一篇blog',
//     author: 'Lucas Jee',
//     authorAvatar: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png',
//     date: '28 Jul, 2024',
//     slug: '/blog'
//   }
// ])

// Methods
const handleStatusChange = (tab: any) => {
  // In a real application, you would fetch articles based on the selected status
  console.log('Status changed to:', tab.paneName)
  activeStatus.value = tab.paneName
  loadArticles()
}

const handleEdit = (article: any) => {
  // Navigate to edit page
  console.log('Edit article:', article.id)
  window.open(`/admin/articles/edit/${article.id}`, '_blank')
  // router.push(`/admin/articles/edit/${article.id}`)
}

const applyFilters = () => {
  // Apply filter logic here
  console.log('Applied filters:', { authors: selectedAuthors.value, tags: selectedTags.value })
  loadArticles()
  showFilterDialog.value = false
}

const handleAction = (
  command: 'pin' | 'preview' | 'cancel' | 'restore' | 'delete' | 'recommend' | 'featured',
  article: any
) => {
  switch (command) {
    case 'pin':
      console.log('Pin article:', article.id)
      handleUpdateOpStatus(command, article)
      break
    case 'recommend':
      console.log('Recommend article:', article.id)
      handleUpdateOpStatus(command, article)
      break
    case 'featured':
      console.log('Featured article:', article.id)
      handleUpdateOpStatus(command, article)
      break
    case 'preview':
      console.log('Preview article:', article.id)
      handlePreviewArticle(article)
      break
    case 'cancel':
      console.log('Cancel scheduled article:', article.id)
      break
    case 'restore':
      console.log('Restore article:', article.id)
      // 恢复文章：将状态从 deleted 改回 draft
      ElMessageBox.confirm(
        t('admin.article.dialog.restore.description'),
        t('admin.article.dialog.restore.title'),
        {
          confirmButtonText: t('admin.article.dialog.restore.confirm'),
          cancelButtonText: t('admin.article.dialog.restore.cancel'),
          type: 'info'
        }
      ).then(async () => {
        try {
          await updateArticleStatus(article.id, 'draft')
          ElMessage.success(t('admin.article.dialog.restore.success'))
          loadArticles()
        } catch (error) {
          ElMessage.error(t('admin.article.dialog.restore.error'))
        }
      })
      break
    case 'delete':
      console.log('Delete article:', article.id)
      // 根据当前标签页判断是软删除还是物理删除
      if (activeStatus.value === 'deleted') {
        // 在deleted标签页：物理删除
        ElMessageBox.confirm(
          t('admin.article.dialog.permanent_delete.description'),
          t('admin.article.dialog.permanent_delete.title'),
          {
            confirmButtonText: t('admin.article.dialog.permanent_delete.confirm'),
            cancelButtonText: t('admin.article.dialog.permanent_delete.cancel'),
            type: 'error'
          }
        ).then(async () => {
          try {
            await deleteArticle(article.id)
            ElMessage.success(t('admin.article.dialog.permanent_delete.success'))
            loadArticles()
          } catch (error) {
            ElMessage.error(t('admin.article.dialog.permanent_delete.error'))
          }
        })
      } else {
        // 在其他标签页：软删除（将状态改为deleted）
        ElMessageBox.confirm(
          t('admin.article.dialog.soft_delete.description'),
          t('admin.article.dialog.soft_delete.title'),
          {
            confirmButtonText: t('admin.article.dialog.soft_delete.confirm'),
            cancelButtonText: t('admin.article.dialog.soft_delete.cancel'),
            type: 'warning'
          }
        ).then(async () => {
          try {
            await updateArticleStatus(article.id, 'deleted')
            ElMessage.success(t('admin.article.dialog.soft_delete.success'))
            loadArticles()
          } catch (error) {
            ElMessage.error(t('admin.article.dialog.soft_delete.error'))
          }
        })
      }
      break
  }
}

// 为模板中的下拉菜单事件创建包装函数
const onArticleAction = (article: any) => {
  return (command: 'pin' | 'preview' | 'cancel' | 'restore' | 'delete' | 'recommend' | 'featured') =>
    handleAction(command, article)
}

const isMobile = ref(false)
const handleResize = () => {
  const width = window.innerWidth
  if (width <= 991) {
    isMobile.value = true
  } else {
    isMobile.value = false
  }
}

const handleUpdateOpStatus = async (type: 'pin' | 'recommend' | 'featured', article: any) => {
  try {
    let reqData = {}
    if (type === 'pin') {
      reqData = {
        is_pin: article.is_pin ? 0 : 1
      }
    } else if (type === 'recommend') {
      reqData = {
        is_recommend: article.is_recommend ? 0 : 1
      }
    } else if (type === 'featured') {
      reqData = {
        is_featured: article.is_featured ? 0 : 1
      }
    }
    await updateArticleOpStatus(article.id, reqData)
    ElMessage.success(t('admin.article.dialog.update.status.success'))
    loadArticles()
  } catch (error) {
    ElMessage.error(t('admin.article.dialog.update.status.error'))
  }
}

// 处理草稿文章预览
const handlePreviewArticle = async (article: any) => {
  try {
    // 对于已发布文章，直接通过slug打开
    if (article.status === 'published' && article.slug) {
      window.open(`/article/${article.slug}`, '_blank')
      return
    }

    // 对于草稿文章，调用预览API获取文章详情
    const res = await previewDraftArticle(article.id.toString())
    if (res.code === 1 && res.data) {
      const previewData = res.data.article || res.data  // 兼容两种数据格式

      // 在新窗口中打开预览页面
      const previewWindow = window.open('', '_blank')
      if (previewWindow) {
        const coverImage = previewData.cover
          ? `<img src="${previewData.cover}" style="width:100%;max-height:400px;object-fit:cover;border-radius:8px;margin-bottom:20px;">`
          : ''
        const subtitle = previewData.subtitle
          ? `<h2 style="font-size:1.2rem;color:#666;margin-bottom:30px;">${previewData.subtitle}</h2>`
          : ''
        let content = previewData.content || '<p>No content yet.</p>'

        // 获取作者信息（优先使用响应中的作者信息）
        const authorName = res.data.full_name || res.data.author_full_name || previewData.author_full_name || 'Unknown Author'
        const authorAvatar = res.data.profile_image || res.data.author_profile_image || previewData.author_profile_image || '/src/assets/avatar.png'

        const html = `
          <!DOCTYPE html>
          <html>
          <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>${previewData.title || 'Untitled'} - Preview</title>
            <style>
              body { max-width: 1024px; margin: 0 auto; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
              .article-title { font-size: 2.5rem; font-weight: bold; margin-bottom: 10px; }
              .article-meta { display: flex; align-items: center; gap: 10px; margin-bottom: 20px; color: #666; font-size: 14px; }
              .author-avatar { width: 32px; height: 32px; border-radius: 50%; object-fit: cover; }
              .article-content { line-height: 1.8; font-size: 1.1rem; }
              .preview-notice { background: #fff3cd; border: 1px solid #ffc107; border-radius: 4px; padding: 10px 15px; margin-bottom: 20px; color: #856404; }
              .preview-notice::before { content: '⚠️ '; margin-right: 5px; }
              img { max-width: 100%; height: auto; }
              pre { background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }
              code { background: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }
              pre code { background: none; padding: 0; }
            </style>
          </head>
          <body>
            <div class="preview-notice">This is a draft preview. The article has not been published yet.</div>
            ${coverImage}
            <h1 class="article-title">${previewData.title || 'Untitled Article'}</h1>
            <div class="article-meta">
              <img src="${authorAvatar}" class="author-avatar" onerror="this.src='/src/assets/avatar.png'">
              <span>${authorName}</span>
              <span>•</span>
              <span>Draft</span>
            </div>
            ${subtitle}
            <div class="article-content">${content}</div>
          </body>
          </html>
        `
        previewWindow.document.write(html)
        previewWindow.document.close()
      }
    } else {
      ElMessage.error('Failed to load article preview')
    }
  } catch (error) {
    console.error('Preview error:', error)
    ElMessage.error('Failed to preview article')
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
  loadArticles()
  loadArticlesCount()
  handleResize()
})
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

// 格式化当前日期0点的时间戳
const today = new Date()
today.setHours(0, 0, 0, 0)
const todayTimestamp = today.getTime() / 1000
// 获取当前日期23:59:59的时间戳
const endOfDayTimestamp = ((today.getTime() + 24 * 60 * 60 * 1000) / 1000).toFixed(0)
console.log(todayTimestamp, endOfDayTimestamp)
const loadArticles = async () => {
  const params: ArticleSearchParams = {
    keyword: inputSearch.value || null,
    status: activeStatus.value as 'draft' | 'published' | 'scheduled' | 'deleted' | null,
    authors: null,
    tags: null,
    time: null
  }
  if (activeStatus.value === 'published') {
    params.status = 'published'
    currentPage.value = currentPage1.value
    pageSize.value = pageSize1.value
  } else if (activeStatus.value === 'drafts') {
    params.status = 'draft'
    currentPage.value = currentPage2.value
    pageSize.value = pageSize2.value
  } else if (activeStatus.value === 'scheduled') {
    params.status = 'scheduled'
    currentPage.value = currentPage3.value
    pageSize.value = pageSize3.value
  } else if (activeStatus.value === 'deleted') {
    params.status = 'deleted'
    currentPage.value = currentPage4.value
    pageSize.value = pageSize4.value
  }
  if (selectedAuthors.value.length > 0) {
    params.authors = selectedAuthors.value.join(',')
  }
  if (selectedTags.value.length > 0) {
    params.tags = selectedTags.value.join(',')
  }

  if (selectedDateRange.value == 'previousDay') {
    const startTime = todayTimestamp - 24 * 60 * 60
    params.time = {
      op: '>',
      value: [startTime]
    }
  } else if (selectedDateRange.value == 'past3days') {
    const startTime = todayTimestamp - 3 * 24 * 60 * 60
    params.time = {
      op: '>',
      value: [startTime]
    }
  } else if (selectedDateRange.value == 'pastWeek') {
    const startTime = todayTimestamp - 7 * 24 * 60 * 60
    params.time = {
      op: '>',
      value: [startTime]
    }
  } else if (selectedDateRange.value == 'pastMonth') {
    const startTime = todayTimestamp - 30 * 24 * 60 * 60
    params.time = {
      op: '>',
      value: [startTime]
    }
  } else if (selectedDateRange.value == 'customDate') {
    const customTime = (
      (customDate.value ? customDate.value.getTime() : Date.now()) / 1000
    ).toFixed(0)
    // 获取自定义日期的23:59:59时间戳
    const customTime_end = parseInt(customTime) + 24 * 60 * 60
    params.time = {
      op: 'between',
      value: [customTime, customTime_end]
    }
  } else if (selectedDateRange.value == 'customRange') {
    const startTime = customDateRange.value[0] ? customDateRange.value[0].getTime() : Date.now()
    const endTime = customDateRange.value[1] ? customDateRange.value[1].getTime() : Date.now()
    params.time = {
      op: 'between',
      value: [(startTime / 1000).toFixed(0), (endTime / 1000).toFixed(0)]
    }
  }

  const res = await getManageArticlesList(currentPage.value, pageSize.value, params)
  if (res.code == 1) {
    articles.value = res.data.list
    totalArticles.value = res.data.total
  }
}

const loadArticlesCount = async () => {
  const res = await getArticlesStatusCount()
  if (res.code == 1) {
    console.log(res.data)
    totalPublished.value = res.data.published
    totalDrafts.value = res.data.draft
    totalScheduled.value = res.data.scheduled
    totalDeleted.value = res.data.deleted
  }
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  if (activeStatus.value === 'published') {
    pageSize1.value = val
  } else if (activeStatus.value === 'drafts') {
    pageSize2.value = val
  } else if (activeStatus.value === 'scheduled') {
    pageSize3.value = val
  } else if (activeStatus.value === 'deleted') {
    pageSize4.value = val
  }
  loadArticles()
  console.log(`${val} items per page`)
}
const handleCurrentChange = (val: number) => {
  currentPage.value = val
  if (activeStatus.value === 'published') {
    currentPage1.value = val
  } else if (activeStatus.value === 'drafts') {
    currentPage2.value = val
  } else if (activeStatus.value === 'scheduled') {
    currentPage3.value = val
  } else if (activeStatus.value === 'deleted') {
    currentPage4.value = val
  }
  loadArticles()
  console.log(`current page: ${val}`)
}

const handleShowFilterDialog = () => {
  if (activeFilterTab.value === 'authors') {
    loadAuthorsList()
  } else if (activeFilterTab.value === 'tags') {
    loadTagsList()
  }
  showFilterDialog.value = true
}

const handleFilterTabClick = (tab: any) => {
  activeFilterTab.value = tab.paneName
  if (tab.paneName === 'authors') {
    loadAuthorsList()
  } else if (tab.paneName === 'tags') {
    loadTagsList()
  }
}

const filterAuthors = () => {
  if (authorSearchTerm.value && authorSearchTerm.value.length >= 1) {
    // selectedAuthors.value = authorsList.value
    //   .filter((author) => author.name.includes(authorSearchTerm.value))
    //   .map((author) => author.id)
    loadAuthorsList(authorSearchTerm.value)
  } else if (authorSearchTerm.value.length == 0) {
    loadAuthorsList()
  }
}

const filterTags = () => {
  if (tagSearchTerm.value && tagSearchTerm.value.length >= 1) {
    // selectedTags.value = tagsList.value
    //   .filter((tag) => tag.name.includes(tagSearchTerm.value))
    //   .map((tag) => tag.id)
    loadTagsList(tagSearchTerm.value)
  } else if (tagSearchTerm.value.length == 0) {
    loadTagsList()
  }
}

const loadAuthorsList = async (keyword?: string) => {
  const res = await getArticleAuthorsList(keyword)
  if (res.code == 1) {
    authorsList.value = res.data
  } else {
    authorsList.value = []
  }
}

const loadTagsList = async (keyword?: string) => {
  const res = await getArticleTagsList(keyword)
  if (res.code == 1) {
    tagsList.value = res.data
  } else {
    tagsList.value = []
  }
}

const handleSearch = async () => {
  const res = await loadArticles()
}
</script>

<style scoped lang="scss">
.articles-management {
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;

  h1 {
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 8px;
  }

  p {
    color: var(--el-text-color-secondary);
    font-size: 14px;
  }
}

.status-tabs {
  margin-bottom: 24px;
}

.search-filter {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;

  .search-input {
    flex: 1;
    max-width: 600px;
  }
}

/* Filter Dialog Styles */
.filter-tabs {
  margin-bottom: 16px;
}

.filter-content {
  padding: 8px 0;
  max-height: 300px;
  overflow-y: auto;
}

.author-search {
  margin-bottom: 16px;
}

.authors-list,
.tags-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.dot-indicator {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: var(--el-color-primary);
}

.check-icon {
  margin-left: 8px;
  color: var(--el-color-primary);
}

.placeholder-content {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: var(--el-text-color-secondary);
  background-color: var(--el-bg-color-soft);
  border-radius: var(--el-border-radius-base);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.mobile-article-card {
  margin-bottom: 20px;
}
.articles-table {
  margin-bottom: 20px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}
.articles-table,
.mobile-article-card {
  .article-title {
    .title-text {
      font-weight: 500;
      margin-bottom: 4px;
      font-size: 1.1rem;
    }

    .meta-info {
      display: flex;
      align-items: center;
      gap: 8px;
      color: var(--el-text-color-secondary);
      font-size: 12px;

      .author-avatar {
        margin-right: 4px;
      }
    }
  }

  .actions {
    display: flex;
    gap: 4px;

    .edit-button,
    .more-button {
      padding: 4px;
    }
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;

  .empty-icon {
    font-size: 48px;
    color: var(--el-text-color-placeholder);
    margin-bottom: 16px;
  }

  .empty-title {
    font-size: 16px;
    font-weight: 500;
    margin-bottom: 8px;
    color: var(--el-text-color-primary);
  }

  .empty-description {
    font-size: 14px;
    color: var(--el-text-color-secondary);
    max-width: 300px;
  }
}

.date-radio-group {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
}

@media screen and (max-width: 991px) {
  .articles-management {
    padding: 0;
  }
}
</style>
