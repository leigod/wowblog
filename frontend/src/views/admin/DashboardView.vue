<template>
  <div class="admin-dashboard">
    <div class="dashboard-header">
      <div class="header-content">
        <div class="header-title">{{ t('admin.dashboard.title') }}</div>
        <div class="welcome-badge">
          <svg fill="none" viewBox="0 0 16 16" width="16" height="16">
            <path
              stroke="currentColor"
              d="M6.833 2C6.368 4.356 6.365 4.356 4 4.833M6.833 2c.47 2.363.473 2.366 2.834 2.833M6.833 2v5.667m2.834-2.834c-2.36.468-2.36.472-2.834 2.834m2.834-2.834H4m2.833 2.834C6.365 5.3 6.358 5.3 4 4.833m0 4.834c-.328 1.663-.33 1.663-2 2m2-2c.332 1.668.334 1.67 2 2m-2-2v4m2-2c-1.666.33-1.666.332-2 2m2-2H2m2 2c-.33-1.67-.336-1.67-2-2m9.667-4.334c-.383 1.94-.386 1.94-2.334 2.334m2.334-2.334c.386 1.946.39 1.949 2.333 2.334m-2.333-2.334V12M14 9.667c-1.944.385-1.944.388-2.333 2.333M14 9.667H9.333M11.667 12c-.386-1.948-.392-1.948-2.334-2.333"
              stroke-linecap="round"
              stroke-linejoin="round"
            ></path>
          </svg>
          <span>Welcome!</span>
        </div>
      </div>
      <p class="header-subtitle">{{ t('admin.dashboard.title_info') }}</p>
    </div>

    <el-divider></el-divider>

    <section class="stats-section">
      <div class="stats-header">
        <h2 class="section-title">{{ t('admin.dashboard.stats.title') }}</h2>
        <el-link type="primary" class="analytics-link" @click="navigateToAnalytics"
          >{{ t('admin.dashboard.stats.link') }} →</el-link
        >
      </div>
      <div class="stats-cards">
        <el-card class="stat-card">
          <div class="stat-value">{{ formatNumber(statsData.sevenDayViews) }}</div>
          <div class="stat-label">{{ t('admin.dashboard.stats.item1') }}</div>
        </el-card>
        <el-card class="stat-card">
          <div class="stat-value">{{ formatNumber(statsData.thirtyDayViews) }}</div>
          <div class="stat-label">{{ t('admin.dashboard.stats.item2') }}</div>
        </el-card>
        <el-card class="stat-card">
          <div class="stat-value">{{ formatNumber(statsData.totalViews) }}</div>
          <div class="stat-label">{{ t('admin.dashboard.stats.item3') }}</div>
        </el-card>
      </div>
    </section>

    <section class="quick-links-section">
      <h2 class="section-title">{{ t('admin.dashboard.quicklinks.title') }}</h2>
      <div class="quick-links-grid">
        <el-card class="quick-link-card" hoverable @click="navigateToCreateArticle">
          <div class="link-icon purple">
            <el-icon><EditPen /></el-icon>
          </div>
          <h3>{{ t('admin.dashboard.quicklinks.item1') }}</h3>
          <p>{{ t('admin.dashboard.quicklinks.item1_info') }}</p>
        </el-card>
        <el-card class="quick-link-card" hoverable @click="navigateToSeries">
          <div class="link-icon blue">
            <el-icon><FolderAdd /></el-icon>
          </div>
          <h3>{{ t('admin.dashboard.quicklinks.item2') }}</h3>
          <p>{{ t('admin.dashboard.quicklinks.item2_info') }}</p>
        </el-card>
        <el-card class="quick-link-card" hoverable @click="navigateToCategories">
          <div class="link-icon pink">
            <el-icon><Setting /></el-icon>
          </div>
          <h3>{{ t('admin.dashboard.quicklinks.item3') }}</h3>
          <p>{{ t('admin.dashboard.quicklinks.item3_info') }}</p>
        </el-card>
        <el-card class="quick-link-card" hoverable @click="navigateToPages">
          <div class="link-icon orange">
            <el-icon><DocumentAdd /></el-icon>
          </div>
          <h3>{{ t('admin.dashboard.quicklinks.item5') }}</h3>
          <p>{{ t('admin.dashboard.quicklinks.item5_info') }}</p>
        </el-card>
        <el-card class="quick-link-card" hoverable @click="navigateToMembers">
          <div class="link-icon purple">
            <el-icon><User /></el-icon>
          </div>
          <h3>{{ t('admin.dashboard.quicklinks.item6') }}</h3>
          <p>{{ t('admin.dashboard.quicklinks.item6_info') }}</p>
        </el-card>
      </div>
    </section>

    <section class="publication-section">
      <h2 class="section-title">{{ t('admin.dashboard.publish.title') }}</h2>
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="publication-card">
            <div class="publication-icon">
              <el-icon><House /></el-icon>
            </div>
            <h3 class="publication-name">{{ blogName }}</h3>
            <div class="publication-metrics">
              <div class="metric-item">
                <div class="metric-value">{{ publicationData.articleCount }}</div>
                <div class="metric-label">{{ t('admin.dashboard.publish.article') }}</div>
              </div>
              <div class="metric-item">
                <div class="metric-value">{{ publicationData.followerCount }}</div>
                <div class="metric-label">{{ t('admin.dashboard.publish.Follower') }}</div>
              </div>
            </div>
            <el-button class="edit-button" size="large" round @click="navigateToSettings">{{
              t('admin.dashboard.publish.editblog')
            }}</el-button>
          </el-card>
        </el-col>
        <el-col :span="18">
          <el-card class="articles-card">
            <div class="articles-header">
              <h3>{{ t('admin.dashboard.publish.articles') }}</h3>
              <div class="header-divider"></div>
              <span class="views-label">{{ t('admin.dashboard.publish.views') }}</span>
            </div>
            <div class="articles-list">
              <div
                v-for="article in recentArticles"
                :key="article.id"
                class="article-item"
                @click="navigateToArticleDetail(article)"
              >
                <div class="article-info">
                  <h4 class="article-title">{{ article.title }}</h4>
                  <div class="article-meta">{{ formatReadTime(article.content || '') }} · {{ formatDate(article.pub_time || article.createtime) }}</div>
                </div>
                <div class="article-views">{{ article.reads || 0 }}</div>
              </div>
              <div v-if="recentArticles.length === 0" class="empty-state">
                <p>{{ t('admin.dashboard.publish.no_articles') }}</p>
              </div>
            </div>
            <el-button class="see-all-link" type="default" size="large" round @click="navigateToArticles">{{
              t('admin.dashboard.publish.seeall')
            }}</el-button>
          </el-card>
        </el-col>
      </el-row>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { EditPen, FolderAdd, Setting, DocumentAdd, User, House } from '@element-plus/icons-vue'
import { getViewTrend, getStatistics, getManageArticlesList, getUserArticleCount } from '@/api/services/articles'
import { useAppStore } from '@/stores/app'
import { useMobileDetection } from '@/composables/useMobileDetection'

const { t } = useI18n()
const router = useRouter()
const appStore = useAppStore()

// 移动端检测
const { isMobile } = useMobileDetection()

// 统计数据
const statsData = ref({
  sevenDayViews: 0,
  thirtyDayViews: 0,
  totalViews: 0
})

// 发布信息数据
const publicationData = ref({
  articleCount: 0,
  followerCount: '-'
})

// 最新文章列表
const recentArticles = ref<any[]>([])

// 博客名称
const blogName = computed(() => appStore.site_title || 'WOW Blog')

// 格式化数字
const formatNumber = (num: number | string): string => {
  const number = typeof num === 'string' ? parseInt(num) : num
  if (number >= 1000000) {
    return (number / 1000000).toFixed(1) + 'M'
  }
  if (number >= 1000) {
    return (number / 1000).toFixed(1) + 'K'
  }
  return number.toString()
}

// 加载统计数据
const loadStats = async () => {
  try {
    // 并行获取统计数据和趋势数据
    const [statsResponse, trend7Response, trend30Response] = await Promise.all([
      getStatistics(),
      getViewTrend(7),
      getViewTrend(30)
    ])

    // 处理总体统计数据
    if (statsResponse.code === 1) {
      statsData.value.totalViews = typeof statsResponse.data.total_views === 'string'
        ? parseInt(statsResponse.data.total_views)
        : statsResponse.data.total_views
    }

    // 处理7日趋势数据
    if (trend7Response.code === 1 && Array.isArray(trend7Response.data)) {
      statsData.value.sevenDayViews = trend7Response.data.reduce((sum: number, item: any) => sum + (item.views || 0), 0)
    }

    // 处理30日趋势数据
    if (trend30Response.code === 1 && Array.isArray(trend30Response.data)) {
      statsData.value.thirtyDayViews = trend30Response.data.reduce((sum: number, item: any) => sum + (item.views || 0), 0)
    }
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

// 加载发布信息
const loadPublicationInfo = async () => {
  try {
    // 并行获取文章数量和最新文章列表
    const [countResponse, articlesResponse] = await Promise.all([
      getUserArticleCount(appStore.userInfo.username || ''),
      getManageArticlesList(1, 4, { status: 'published' })
    ])

    // 处理文章数量
    if (countResponse.code === 1) {
      publicationData.value.articleCount = countResponse.data.total || 0
    }

    // 处理文章列表
    if (articlesResponse.code === 1 && articlesResponse.data) {
      recentArticles.value = articlesResponse.data.list || []
    }
  } catch (error) {
    console.error('Failed to load publication info:', error)
  }
}

// 跳转到数据分析页面
const navigateToAnalytics = () => {
  router.push('/admin/analytics')
}

// 快速开始卡片跳转函数
const navigateToCreateArticle = () => {
  window.open('/admin/articles/create', '_blank')
}

const navigateToSeries = () => {
  router.push('/admin/series')
}

const navigateToCategories = () => {
  router.push('/admin/categories')
}

const navigateToPages = () => {
  router.push('/admin/pages')
}

const navigateToMembers = () => {
  router.push('/admin/members')
}

const navigateToArticles = () => {
  router.push('/admin/articles')
}

// 跳转到设置页面
const navigateToSettings = () => {
  router.push('/admin/settings')
}

// 跳转到文章详情
const navigateToArticleDetail = (article: any) => {
  router.push(`/admin/articles/edit/${article.id}`)
}

// 格式化文章阅读时间
const formatReadTime = (content: string) => {
  // 假设每分钟阅读200字
  const wordCount = content?.length || 0
  const minutes = Math.max(1, Math.ceil(wordCount / 200))
  return `${minutes} min read`
}

// 格式化日期
const formatDate = (timestamp: number | string) => {
  const date = new Date(typeof timestamp === 'string' ? parseInt(timestamp) : timestamp)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

// 初始化时加载数据
onMounted(() => {
  loadStats()
  loadPublicationInfo()
})
</script>

<style scoped>
:global(:root) {
  --wy-section-title-color: #4b5563;
  --wy-button-bg-color: #ffffff;
  --wy-button-hover-bg-color: #f3f4f6;
}
:global(.dark) {
  --wy-section-title-color: #e5e7eb;
  --wy-button-bg-color: transparent;
  --wy-button-hover-bg-color: rgb(24.4, 33.8, 43.5);
}
.admin-dashboard {
  padding: 24px;
}
.dashboard-header {
  margin-bottom: 32px;
}
.header-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.header-title {
  font-size: 2rem;
  font-weight: 600;
  color: var(--wy-section-title-color);
}
.header-subtitle {
  font-size: 1rem;
  color: rgb(113 113 122);
}
.welcome-badge {
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 0.375rem;
  border-radius: 0.375rem;
  background-color: rgb(253 242 248 / 1);
  padding-top: 0.375rem;
  padding-bottom: 0.375rem;
  padding-right: 0.625rem;
  padding-left: 0.5rem;
  font-weight: 500;
  color: rgb(219 39 119);
}
.stats-section {
  margin-bottom: 32px;
}
.stats-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.analytics-link {
  font-size: 14px;
}
.section-title {
  font-size: 18px;
  margin-bottom: 16px;
  color: var(--wy-section-title-color);
}
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}
.stat-card {
  padding: 20px;
  text-align: center;
}
.stat-value {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 8px;
  /* color: #111827; */
}
.stat-label {
  color: #6b7280;
  font-size: 14px;
}
.quick-links-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}
.quick-link-card {
  padding: 24px;
  height: 100%;
  transition: transform 0.2s;
}
.quick-link-card:hover {
  transform: translateY(-4px);
}
.link-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  color: white;
  font-size: 20px;
}
.link-icon.purple {
  background-color: #8b5cf6;
}
.link-icon.blue {
  background-color: #3b82f6;
}
.link-icon.pink {
  background-color: #ec4899;
}
.link-icon.orange {
  background-color: #f97316;
}
.quick-link-card h3 {
  font-size: 16px;
  margin-bottom: 8px;
  color: var(--el-text-color-regular);
}
.quick-link-card p {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}
.publication-section {
  margin-top: 32px;
}
.publication-card {
  padding: 24px;
  text-align: center;
  min-height: 370px;
}
.publication-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: #3b82f6;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  font-size: 24px;
}
.publication-name {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 24px;
  color: var(--el-text-color-regular);
}
.publication-metrics {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-bottom: 24px;
}
.metric-item {
  text-align: center;
  margin-bottom: 20px;
}
.metric-value {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 4px;
  color: var(--el-text-color-regular);
}
.metric-label {
  font-size: 14px;
  color: #6b7280;
}
.edit-button {
  width: 100%;
  background-color: var(--wy-button-bg-color);
  color: #4b5563;
  border: 1px solid var(--el-border-color);
}
.edit-button:hover {
  background-color: var(--wy-button-hover-bg-color);
  color: #4b5563;
}
.articles-card {
  padding: 24px;
  min-height: 370px;
}
.articles-header {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
}
.articles-header h3 {
  font-size: 18px;
  margin: 0;
  color: var(--el-text-color-regular);
}
.header-divider {
  flex-grow: 1;
  height: 1px;
  background-color: #e5e7eb;
  margin: 0 16px;
}
.views-label {
  font-size: 14px;
  color: #6b7280;
}
.articles-list {
  max-height: 165px;
  overflow-y: auto;
}
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px 16px;
  color: #9ca3af;
  font-size: 14px;
}
.article-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  /* border-bottom: 1px solid #e5e7eb; */
  border-radius: 8px;

  &:hover {
    background-color: var(--wy-button-hover-bg-color);
    cursor: pointer;
  }
}
.article-title {
  font-size: 16px;
  margin: 0 0 4px 0;
  color: var(--el-text-color-regular);
}
.article-meta {
  font-size: 14px;
  color: #6b7280;
}
.article-views {
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-regular);
}
.see-all-link {
  display: block;
  text-align: center;
  margin-top: 24px;
  font-size: 14px;
  width: 100%;
  color: #4b5563;
  border: 1px solid var(--el-border-color);

  &:hover {
    background-color: var(--wy-button-hover-bg-color);
  }
}

/* 移动端适配 */
@media (max-width: 767px) {
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .header-content {
    width: 100%;
  }

  .welcome-badge {
    font-size: 12px;
  }

  .stats-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .stats-cards {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .stat-card {
    padding: 16px;
  }

  .stat-value {
    font-size: 24px;
  }

  .stat-label {
    font-size: 12px;
  }

  .quick-links-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .quick-link-card {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px;
    text-align: left;
  }

  .quick-link-card .link-icon {
    width: 40px;
    height: 40px;
  }

  .quick-link-card h3 {
    font-size: 14px;
  }

  .quick-link-card p {
    font-size: 12px;
  }

  .publication-card {
    padding: 16px;
  }

  .article-title {
    font-size: 14px;
  }

  .article-meta {
    font-size: 12px;
  }
}

/* 小于1080px时发布信息区域改为一栏式 */
@media (max-width: 1079px) {
  .publication-section :deep(.el-row) {
    display: flex;
    flex-direction: column;
  }

  .publication-section :deep(.el-col) {
    width: 100% !important;
    flex: 0 0 100%;
    max-width: 100%;
  }

  .publication-section .publication-card,
  .publication-section .articles-card {
    min-height: auto;
  }

  .publication-card {
    margin-bottom: 20px;
  }
}
</style>
