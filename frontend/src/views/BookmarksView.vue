<template>
  <div class="wy-container">
    <el-container>
      <el-main>
        <el-row :gutter="30">
          <el-col :xs="24" :sm="24" :md="16">
            <div style="display: flex; align-items: center; margin-bottom: 20px">
              <h2 style="margin: 0; font-size: 24px; font-weight: 800">{{ t('bookmarks.title') }}</h2>
              <span style="margin-left: 15px; color: #909399; font-size: 14px">{{ t('bookmarks.count', {
                count:
                  totalCount
              }) }}</span>
            </div>

            <!-- 收藏列表 -->
            <el-card v-for="item in articleList" :key="item.id" shadow="hover" class="wy-card wy-card-radius"
              @click="handleDetail(item)">
              <div class="wy-card-header">
                <div class="left">
                  <div class="block">
                    <el-avatar :size="50" :src="item.author_profile_image || default_avatar"
                      @click.stop="handleProfile(item.author_username)" />
                  </div>
                  <div class="block">
                    <div class="author">{{ item.author_full_name }}</div>
                    <div class="info">
                      @{{ item.author_username }} ·
                      {{ formatDateTime(item.createtime, 'YYYY-MM-DD') }}
                    </div>
                  </div>
                </div>
                <div class="right">
                  <el-button type="warning" size="small" plain round @click.stop="handleUnbookmark(item.id, $event)">
                    <IconifyIcon icon="material-symbols-light:bookmark-star" width="16" height="16"></IconifyIcon>
                    <span style="margin-left: 5px">{{ t('list.view.bookmark.delete') }}</span>
                  </el-button>
                </div>
              </div>
              <div class="wy-card-body">
                <div class="content">
                  <div class="left">
                    <div class="title">
                      {{ item.title }}
                    </div>
                    <div class="summary">
                      {{ stripHtml(item.content) }}
                    </div>
                  </div>
                  <div class="right" v-if="item.cover">
                    <el-image :src="item.cover" fit="cover" class="wy-card-radius wy-card-image" />
                  </div>
                </div>
                <div class="info">
                  <div class="left">
                    <span>
                      <el-icon>
                        <ChatLineRound />
                      </el-icon> {{ t('home.list.discuss') }}
                    </span>
                    · <span>{{ item.stats?.likes || 0 }} {{ t('home.list.likes') }}</span> ·
                    <span>{{ item.stats?.views || 0 }} {{ t('home.list.reads') }}</span>
                  </div>
                  <div class="right">
                    <el-button type="info" size="small" plain round style="border: 1px solid #e4e7ed; font-weight: 400"
                      @click.stop="handleLabel(tag)" v-for="tag in item.displayTags" :key="tag.id">{{ tag.name
                      }}</el-button>
                  </div>
                </div>
              </div>
            </el-card>

            <!-- 空状态 -->
            <div v-if="articleList.length === 0 && !loading" class="wy-empty-state">
              <IconifyIcon icon="material-symbols-light:bookmark-star-outline" width="64" height="64" color="#dcdfe6">
              </IconifyIcon>
              <p style="margin-top: 15px; color: #909399; font-size: 16px">{{ t('bookmarks.empty') }}</p>
              <el-button type="primary" round style="margin-top: 15px" @click="goHome">{{ t('list.view.browse')
              }}</el-button>
            </div>

            <!-- 加载更多 -->
            <div v-if="articleList.length > 0" class="wy-load-more">
              <el-button v-if="hasMoreData" type="primary" text @click="handleLoadMore" :loading="loading">
                {{ t('list.view.loadmore') }}
              </el-button>
              <div v-else class="wy-no-more-data">-- {{ t('list.view.nomore') }} --</div>
            </div>
          </el-col>

          <el-col :xs="24" :sm="24" :md="8">
            <el-card shadow="never" class="wy-recommend-articles" style="margin-bottom: 30px">
              <div class="wy-card-title">{{ t('home.list.trending') }}</div>
              <div class="wy-card-body">
                <div class="article-item" v-for="item in trendingArticleList" :key="item.title"
                  @click="handleDetail(item)">
                  <div class="item-title">{{ item.title }}</div>
                  <div class="item-info">
                    <span class="author">{{ item.full_name }}</span><span> · </span><span>{{ item.views }} {{
                      t('home.list.reads') }}</span>
                  </div>
                </div>
              </div>
            </el-card>

            <el-card shadow="never" style="margin-bottom: 30px">
              <div class="wy-card-title">{{ t('home.list.hottag') }}</div>
              <div class="wy-card-body">
                <div class="wy-hot-tags">
                  <el-tag v-for="item in tagItems" :key="item.id" type="primary" effect="light" round
                    @click="handleLabel(item)">
                    {{ item.name }}
                  </el-tag>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ChatLineRound } from '@element-plus/icons-vue'
import {
  getUserBookmarks,
  getHotTagsList,
  getHotArticlesList
} from '@/api/services/blog'
import {
  getBlogTagsList,
  getBlogStats,
  unbookmarkArticleApi
} from '@/api/services/blog'
import { formatDateTime } from '@/utils/dateUtils'
import IconifyIcon from '@/components/IconIfy.vue'

const { t } = useI18n()
const router = useRouter()

const default_avatar = 'src/assets/avatar.png'
const articleList = ref<any[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const totalCount = ref(0)
const hasMoreData = ref(true)
const loading = ref(false)

const trendingArticleList = ref<any[]>([])
type Item = { id: number; type: string; name: string; slug: string; counts: number }
const tagItems = ref<Array<Item>>([])

onMounted(() => {
  loadBookmarks()
  loadHotTags()
  loadHotArticles()
})

// 获取收藏列表
const loadBookmarks = async () => {
  loading.value = true
  try {
    const res = await getUserBookmarks(currentPage.value, pageSize.value)
    if (res.code === 1) {
      const newArticles = res.data.list || []
      if (currentPage.value === 1) {
        articleList.value = newArticles
      } else {
        articleList.value = [...articleList.value, ...newArticles]
      }
      totalCount.value = res.data.total || 0
      pageSize.value = res.data.pageSize || 10

      // 判断是否还有更多数据
      hasMoreData.value = articleList.value.length < totalCount.value

      // 异步加载标签
      await loadArticlesTags()
      // 异步加载统计数据
      await loadArticleStats()
    }
  } catch (error) {
    console.error('加载收藏列表失败:', error)
    ElMessage.error('加载失败，请重试')
  } finally {
    loading.value = false
  }
}

// 异步加载所有文章的标签
const loadArticlesTags = async () => {
  articleList.value.forEach((article) => {
    article.displayTags = []
  })

  const allTagIds = new Set<string>()
  articleList.value.forEach((article) => {
    if (article.tags && typeof article.tags === 'string') {
      const tagIds = article.tags
        .split(',')
        .map((id: string) => id.trim())
        .filter((id: string) => id)
      tagIds.forEach((tagId: string) => allTagIds.add(tagId))
    }
  })

  if (allTagIds.size > 0) {
    const res = await getBlogTagsList(Array.from(allTagIds))
    if (res.code === 1) {
      const tagsMap = new Map<string, any>()
      res.data.forEach((tag: any) => {
        tagsMap.set(tag.id.toString(), tag)
      })

      articleList.value.forEach((article) => {
        if (article.tags && typeof article.tags === 'string') {
          const tagIds = article.tags
            .split(',')
            .map((id: string) => id.trim())
            .filter((id: string) => id)
          article.displayTags = tagIds
            .map((tagId: string) => tagsMap.get(tagId.toString()))
            .filter((tag: any) => tag !== undefined)
            .sort((a: any, b: any) => (b.counts || 0) - (a.counts || 0))
            .slice(0, 3)
        }
      })
    }
  }
}

// 异步加载文章统计数据
const loadArticleStats = async () => {
  try {
    if (articleList.value.length === 0) return

    const articleIds = articleList.value.map((article) => String(article.id))
    const res = await getBlogStats(articleIds)

    if (res.code === 1 && res.data) {
      const statsMap = new Map<string, any>()

      if (Array.isArray(res.data)) {
        res.data.forEach((stat: any) => {
          const articleId = stat.article_id ? String(stat.article_id) : null
          if (articleId) {
            statsMap.set(articleId, {
              likes: stat.likes || stat.like_count || 0,
              views: stat.views || stat.view_count || 0
            })
          }
        })
      }

      articleList.value.forEach((article) => {
        const articleIdStr = String(article.id)
        article.stats = statsMap.get(articleIdStr) || {
          likes: 0,
          views: 0
        }
      })
    }
  } catch (error) {
    console.error('Error loading article stats:', error)
  }
}

// 获取热门标签
const loadHotTags = async () => {
  const res = await getHotTagsList()
  if (res.code === 1) {
    tagItems.value = res.data || []
  }
}

// 获取热门文章
const loadHotArticles = async (limit: number = 5, days: number = 7) => {
  const res = await getHotArticlesList(limit, days)
  if (res.code === 1) {
    trendingArticleList.value = res.data || []
  }
}

// 加载更多
const handleLoadMore = () => {
  currentPage.value++
  loadBookmarks()
}

// 取消收藏
const handleUnbookmark = async (article_id: number, event: Event) => {
  event.stopPropagation()

  const article = articleList.value.find((article) => article.id === article_id)
  if (!article) return

  try {
    const res = await unbookmarkArticleApi(article_id)
    if (res.code === 1) {
      ElMessage.success('取消收藏成功')
      // 从列表中移除该文章
      articleList.value = articleList.value.filter((a) => a.id !== article_id)
      totalCount.value--
    }
  } catch (error) {
    console.error('取消收藏失败:', error)
    ElMessage.error('操作失败，请重试')
  }
}

const handleDetail = (item: any) => {
  const articleName = item.slug
  router.push(`/article/${articleName}`)
}

const handleLabel = (tag: any) => {
  if (tag && tag.slug) {
    router.push(`/tag/${tag.slug}`)
  }
}

const handleProfile = (username: string) => {
  router.push(`/profile/${username}`)
}

const goHome = () => {
  router.push('/')
}

// 移除HTML标签的辅助函数
const stripHtml = (html: string) => {
  if (!html) return ''
  return html.replace(/<[^>]*>/g, '').slice(0, 150)
}

defineOptions({ name: 'BookmarksView' })
</script>

<style scoped>
.wy-container {
  display: flex;
  width: 1200px;
  margin: 0 auto;
  padding: 30px 0;
}

.wy-card-radius {
  border-radius: 8px;
}

.wy-card:hover {
  cursor: pointer;
}

.wy-card:not(:first-of-type) {
  margin-top: 30px;
}

.wy-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.wy-card-header .left {
  display: flex;
}

.wy-card-header .left .block {
  margin-right: 10px;
}

.wy-card-header .author {
  font-weight: 800;
  font-size: 14px;
  line-height: 28px;
}

.wy-card-header .info {
  color: #909399;
}

.wy-card-body {
  display: flex;
  flex-direction: column;
}

.wy-card-body .content,
.wy-card-body .info {
  display: flex;
  justify-content: space-between;
  padding-top: 15px;
}

.wy-card-body .info .right {
  display: flex;
  align-items: center;
}

.wy-card-body .content .right {
  width: 179px;
  height: 108px;
  border-radius: 8px;
}

.wy-card-body .content .left {
  display: flex;
  flex-direction: column;
  flex: 1;
  margin-right: 10px;
}

.wy-card-body .title {
  font-weight: 800;
  font-size: 24px;
  line-height: 30px;
  padding-bottom: 10px;
}

.wy-card-body .summary {
  font-size: 18px;
  color: #909399;
  line-height: 28px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  line-clamp: 2;
  -webkit-line-clamp: 2;
}

.wy-card-image {
  width: 179px;
  height: 108px;
}

.wy-card-title {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--el-text-color-regular);
  margin-bottom: 1rem;
}

.wy-card-body .article-item .item-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--el-text-color-regular);
  cursor: pointer;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  margin-bottom: 0.5rem;
}

.wy-card-body .article-item .item-title:hover {
  text-decoration: underline;
  color: var(--el-color-primary);
}

.wy-card-body .article-item .item-info {
  display: flex;
  justify-content: flex-start;
  color: var(--el-text-color-secondary);
}

.wy-card-body .article-item .item-info span {
  margin-right: 8px;
}

.wy-hot-tags {
  display: flex;
  flex-wrap: wrap;
}

.wy-hot-tags span {
  cursor: pointer;
  margin: 5px;
}

.wy-hot-tags span:hover {
  cursor: pointer;
  margin: 5px;
  background-color: var(--el-color-primary);
  color: var(--el-color-white);
}

.wy-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  background: var(--el-bg-color);
  border-radius: 8px;
}

.wy-load-more {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 30px;
}

.wy-no-more-data {
  text-align: center;
  color: #909399;
  font-size: 14px;
  padding: 20px 0;
}

@media only screen and (max-width: 767px) {
  .wy-container {
    width: 100%;
  }

  .wy-card-image {
    width: 144px;
    height: 86px;
  }
}
</style>
