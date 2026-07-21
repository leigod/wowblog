<template>
  <div class="my-articles">
    <div class="page-header">
      <h1>{{ t('my_articles.title') }}</h1>
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
            </p>
            <div class="article-actions">
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Edit, EditPen, Delete } from '@element-plus/icons-vue'
import { useAppStore } from '@/stores/app'
import { getUserArticles, getUserArticleCount, updateArticle, deleteArticle } from '@/api/services/articles'

const router = useRouter()
const { t } = useI18n()
const appStore = useAppStore()

// 用户角色
const isAuthor = computed(() => appStore.userRole === 'Author')
const isContributor = computed(() => appStore.userRole === 'Contributor')

// 状态管理
const loading = ref(false)
// 根据用户角色设置初始状态：Contributor 默认显示草稿，其他默认显示已发布
const activeStatus = ref(isContributor.value ? 'drafts' : 'published')
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

    console.log('当前 activeStatus:', activeStatus.value)

    // 根据 activeStatus 确定 API 参数
    let statusParam: string | null = null
    if (activeStatus.value === 'published') {
      statusParam = 'published'
    } else if (activeStatus.value === 'drafts') {
      statusParam = 'draft'
    }

    console.log('使用 status 参数:', statusParam)

    // 使用带 status 参数的 API
    const res = await getUserArticles(username, 100, statusParam)

    console.log('API 响应:', res)

    if (res.code === 1 && res.data) {
      articlesList.value = res.data.list || []
      total.value = res.data.total || 0
      console.log('文章列表:', articlesList.value)
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
    console.log('文章统计 API 响应:', res)

    if (res.code === 1 && res.data) {
      console.log('文章统计数据:', res.data)
      totalPublished.value = res.data.published || 0
      totalDrafts.value = res.data.draft || 0
    }
  } catch (error) {
    console.error('获取文章统计失败:', error)
  }
}

// 状态变更
const handleStatusChange = (tab: any) => {
  console.log('Status changed to:', tab.paneName)
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

// 创建文章
const handleCreateArticle = () => {
  router.push('/my-articles/create')
}

// 编辑文章
const handleEditArticle = (id: number) => {
  router.push(`/my-articles/edit/${id}`)
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

    const res = await updateArticle(String(id), { status: 'published' })
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

    const res = await updateArticle(String(id), { status: 'draft' })
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

    const res = await deleteArticle(String(article.id))
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
.my-articles {
  padding: 20px;
  width: 1200px;
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
  color: #666;
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
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  transition: all 0.3s;
}

.article-item:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
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
  color: #666;
  font-size: 14px;
}

.article-actions {
  display: flex;
  gap: 8px;
  margin-top: auto;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 40px;
}

@media (max-width: 768px) {
  .my-articles {
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
