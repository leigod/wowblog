<template>
  <div class="creator-articles">
    <div class="page-header">
      <h1>{{ t('creator.menu.articles') }}</h1>
      <p>{{ t('my_articles.subtitle') }}</p>
    </div>

    <!-- 操作按钮 -->
    <div class="page-actions">
      <el-button type="primary" :icon="EditPen" @click="handleCreateArticle">
        {{ t('my_articles.create_article') }}
      </el-button>
    </div>

    <!-- Status tabs - 空 tab，只负责切换状态 -->
    <el-tabs v-model="activeStatus" class="status-tabs" @tab-click="handleStatusChange">
      <el-tab-pane :label="publishedTabLabel" name="published" />
      <el-tab-pane :label="draftTabLabel" name="drafts" />
    </el-tabs>

    <!-- 文章列表 - 在 tabs 之外 -->
    <div class="articles-list" v-loading="loading">
      <div v-if="articlesList.length === 0 && !loading" class="empty-state">
        <el-empty :description="t('my_articles.empty_description')">
          <el-button type="primary" :icon="EditPen" @click="handleCreateArticle">
            {{ t('my_articles.create_first_article') }}
          </el-button>
        </el-empty>
      </div>

      <div v-else class="article-items">
        <div v-for="article in articlesList" :key="article.id" class="article-item">
          <div class="article-cover" v-if="article.cover">
            <img :src="article.cover" :alt="article.title" />
          </div>
          <div class="article-info">
            <h3 class="article-title">{{ article.title }}</h3>
            <p class="article-meta">
              <span class="article-date">{{ formatDate(article.pub_time || article.createtime) }}</span>
              <el-tag :type="getStatusTagType(article.status)" size="small">
                {{ getStatusText(article.status) }}
              </el-tag>
              <span class="article-views" :title="t('creator.articles.views')">
                <el-icon><View /></el-icon>{{ article.reads || 0 }}
              </span>
            </p>
            <div class="article-actions">
              <el-tag v-if="article.blog_top" type="warning" size="small" effect="plain">
                {{ t('creator.articles.pinned') }}
              </el-tag>
              <span v-if="article.blog_sort" class="sort-badge">#{{ article.blog_sort }}</span>
              <el-button size="small" :icon="Top" :type="article.blog_top ? 'warning' : 'default'"
                @click="handleToggleBlogTop(article)">
                {{ article.blog_top ? t('creator.articles.unpin') : t('creator.articles.pin') }}
              </el-button>
              <el-button size="small" @click="handleEditBlogSort(article)">
                {{ t('creator.articles.sort') }}
              </el-button>
              <el-button size="small" :icon="Edit" @click="handleEditArticle(article.id)">
                {{ t('my_articles.edit') }}
              </el-button>
              <el-button v-if="article.status === 'draft' && isAuthor" size="small" type="primary"
                @click="handlePublishArticle(article.id)">
                {{ t('my_articles.publish') }}
              </el-button>
              <el-button v-if="article.status === 'published'" size="small" type="warning"
                @click="handleUnpublishArticle(article.id)">
                {{ t('my_articles.unpublish') }}
              </el-button>
              <el-button size="small" type="danger" :icon="Delete" @click="handleDeleteArticle(article)">
                {{ t('my_articles.delete') }}
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Author 专属的文章管理（Creator 工作台）。
// 从 MyArticlesView 派生：跳转指向 /creator/articles/*，
// 发布/编辑走 creator 模式（可选 Blog 分类/系列）；/my-articles 留给 Contributor。
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Edit, EditPen, Delete, Top, View } from '@element-plus/icons-vue'
import { useAppStore } from '@/stores/app'
import { getUserArticles, getUserArticleCount, updateMyArticle, updateMyArticleStatus, updateMyArticleBlogMeta, deleteMyArticle } from '@/api/services/articles'

const router = useRouter()
const { t } = useI18n()
const appStore = useAppStore()

// 用户角色（Admin 预览工作台时不显示发布按钮，与原行为一致）
const isAuthor = computed(() => appStore.userRole === 'Author')

// 状态管理
const loading = ref(false)
const activeStatus = ref('published')
const currentPage = ref(1)
const total = ref(0)
const articlesList = ref<any[]>([])

// 统计数据
const totalPublished = ref(0)
const totalDrafts = ref(0)

// Tab 标签
const publishedTabLabel = computed(() => t('my_articles.tab.published') + ` (${totalPublished.value})`)
const draftTabLabel = computed(() => t('my_articles.tab.draft') + ` (${totalDrafts.value})`)

// 获取文章列表
const fetchArticles = async () => {
  loading.value = true
  try {
    const username = appStore.userInfo?.username
    if (!username) {
      ElMessage.error('无法获取用户信息')
      return
    }

    // 根据 activeStatus 确定 API 参数
    let statusParam: string | null = null
    if (activeStatus.value === 'published') {
      statusParam = 'published'
    } else if (activeStatus.value === 'drafts') {
      statusParam = 'draft'
    }

    const res = await getUserArticles(username, 100, statusParam)
    if (res.code === 1 && res.data) {
      articlesList.value = res.data.list || []
      total.value = res.data.total || 0
    }
  } catch (error) {
    console.error('获取文章列表失败:', error)
    ElMessage.error('获取文章列表失败')
  } finally {
    loading.value = false
  }
}

// 获取文章统计
const fetchArticleCount = async () => {
  try {
    const username = appStore.userInfo?.username
    if (!username) return

    const res = await getUserArticleCount(username)
    if (res.code === 1 && res.data) {
      totalPublished.value = res.data.published || 0
      totalDrafts.value = res.data.draft || 0
    }
  } catch (error) {
    console.error('获取文章统计失败:', error)
  }
}

// 状态变更
const handleStatusChange = (tab: any) => {
  activeStatus.value = tab.paneName
  currentPage.value = 1
  fetchArticles()
}

// 格式化日期
const formatDate = (timestamp: number) => {
  const date = new Date(timestamp * 1000)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// 获取状态标签类型
const getStatusTagType = (status: string) => {
  switch (status) {
    case 'published':
      return 'success'
    case 'draft':
      return 'info'
    default:
      return 'info'
  }
}

// 获取状态文本
const getStatusText = (status: string) => {
  switch (status) {
    case 'published':
      return t('my_articles.status.published')
    case 'draft':
      return t('my_articles.status.draft')
    default:
      return status
  }
}

// 创建文章：新开页面（不替换当前文章管理界面）
const handleCreateArticle = () => {
  window.open('/creator/articles/create', '_blank')
}

// 个人 blog 置顶开关（仅影响 /blog/:username 的焦点区优先展示）
const handleToggleBlogTop = async (article: any) => {
  const next = article.blog_top ? 0 : 1
  try {
    const res = await updateMyArticleBlogMeta(article.id, { blog_top: next })
    if (res.code === 1) {
      article.blog_top = next
      ElMessage.success(next ? t('creator.articles.pin_success') : t('creator.articles.unpin_success'))
      fetchArticles()
    } else {
      ElMessage.error(res.msg || t('creator.articles.meta_error'))
    }
  } catch {
    ElMessage.error(t('creator.articles.meta_error'))
  }
}

// 编辑个人 blog 排序权重（大者靠前，与置顶组合生效）
const handleEditBlogSort = (article: any) => {
  ElMessageBox.prompt(
    t('creator.articles.sort_prompt'),
    t('creator.articles.sort'),
    {
      confirmButtonText: t('admin.general.btn.update'),
      cancelButtonText: t('admin.general.btn.cancel'),
      inputValue: String(article.blog_sort || 0),
      inputPattern: /^-?\d+$/,
      inputErrorMessage: t('creator.articles.sort_invalid')
    }
  )
    .then(async ({ value }) => {
      try {
        const res = await updateMyArticleBlogMeta(article.id, { blog_sort: parseInt(value, 10) })
        if (res.code === 1) {
          ElMessage.success(t('creator.articles.sort_success'))
          fetchArticles()
        } else {
          ElMessage.error(res.msg || t('creator.articles.meta_error'))
        }
      } catch {
        ElMessage.error(t('creator.articles.meta_error'))
      }
    })
    .catch(() => {})
}

// 编辑文章（新开窗口）
const handleEditArticle = (id: number) => {
  window.open(`/creator/articles/edit/${id}`, '_blank')
}

// 发布文章
const handlePublishArticle = async (id: number) => {
  try {
    await ElMessageBox.confirm(
      t('my_articles.confirm_publish'),
      t('my_articles.confirm_title'),
      {
        confirmButtonText: t('my_articles.confirm_yes'),
        cancelButtonText: t('my_articles.confirm_no'),
        type: 'warning'
      }
    )

    const res = await updateMyArticleStatus(String(id), 'published')
    if (res.code === 1) {
      ElMessage.success(t('my_articles.publish_success'))
      fetchArticles()
      fetchArticleCount()
    } else {
      ElMessage.error(res.msg || t('my_articles.publish_failed'))
    }
  } catch (error) {
    // 用户取消操作
  }
}

// 取消发布文章
const handleUnpublishArticle = async (id: number) => {
  try {
    await ElMessageBox.confirm(
      t('my_articles.confirm_unpublish'),
      t('my_articles.confirm_title'),
      {
        confirmButtonText: t('my_articles.confirm_yes'),
        cancelButtonText: t('my_articles.confirm_no'),
        type: 'warning'
      }
    )

    const res = await updateMyArticleStatus(String(id), 'draft')
    if (res.code === 1) {
      ElMessage.success(t('my_articles.unpublish_success'))
      fetchArticles()
      fetchArticleCount()
    } else {
      ElMessage.error(res.msg || t('my_articles.unpublish_failed'))
    }
  } catch (error) {
    // 用户取消操作
  }
}

// 删除文章
const handleDeleteArticle = async (article: any) => {
  try {
    await ElMessageBox.confirm(
      t('my_articles.confirm_delete', { title: article.title }),
      t('my_articles.confirm_title'),
      {
        confirmButtonText: t('my_articles.confirm_yes'),
        cancelButtonText: t('my_articles.confirm_no'),
        type: 'warning'
      }
    )

    const res = await deleteMyArticle(String(article.id))
    if (res.code === 1) {
      ElMessage.success(t('my_articles.delete_success'))
      fetchArticles()
      fetchArticleCount()
    } else {
      ElMessage.error(res.msg || t('my_articles.delete_failed'))
    }
  } catch (error) {
    // 用户取消操作
  }
}

// 初始化
onMounted(() => {
  fetchArticles()
  fetchArticleCount()
})
</script>

<style scoped>
.creator-articles {
  padding: 20px;
  max-width: 1200px;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.page-header p {
  color: var(--el-text-color-secondary);
  margin: 0;
}

.page-actions {
  margin-bottom: 20px;
}

.status-tabs {
  margin-bottom: 20px;
}

.empty-state {
  padding: 60px 0;
}

.articles-list {
  min-height: 400px;
}

.article-items {
  display: grid;
  gap: 20px;
}

.article-item {
  display: flex;
  gap: 20px;
  padding: 20px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  transition: all 0.3s;
}

.article-item:hover {
  box-shadow: var(--wy-shadow-card-hover);
}

.article-cover {
  width: 200px;
  height: 120px;
  flex-shrink: 0;
}

.article-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 4px;
}

.article-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.article-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 12px 0;
  line-height: 1.4;
}

.article-meta {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 12px;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.article-views {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: var(--el-text-color-secondary);
}

.article-actions {
  display: flex;
  gap: 8px;
  margin-top: auto;
  align-items: center;
  flex-wrap: wrap;
}

/* blog 排序权重角标 */
.sort-badge {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  background: var(--el-fill-color-light);
  border-radius: 4px;
  padding: 2px 6px;
}

@media (max-width: 768px) {
  .creator-articles {
    padding: 10px;
  }

  .article-item {
    flex-direction: column;
  }

  .article-cover {
    width: 100%;
    height: 200px;
  }

  .article-actions {
    flex-wrap: wrap;
  }
}
</style>
