<template>
  <div class="analytics-container">
    <div class="page-header">
      <h1>{{ t('admin.analytics.title') }}</h1>
      <p>{{ t('admin.analytics.subtitle') }}</p>
    </div>

    <!-- API Warning -->
    <el-alert v-if="showApiWarning" type="warning" :closable="false" class="api-warning">
      <template #default>
        <div class="warning-content">
          <el-icon>
            <WarningFilled />
          </el-icon>
          <span>{{ t('admin.analytics.api_not_implemented') }}</span>
        </div>
      </template>
    </el-alert>

    <!-- Stats Cards -->
    <section class="stats-section" :class="{ 'api-unavailable': !statisticsApiAvailable }">
      <h2 class="section-title">{{ t('admin.analytics.stats.title') }}</h2>
      <div class="stats-grid">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon articles">
            <el-icon>
              <Document />
            </el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ statistics.total_articles || 0 }}</div>
            <div class="stat-label">{{ t('admin.analytics.stats.total_articles') }}</div>
          </div>
        </el-card>
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon views">
            <el-icon>
              <View />
            </el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ formatNumber(statistics.total_views || 0) }}</div>
            <div class="stat-label">{{ t('admin.analytics.stats.total_views') }}</div>
          </div>
        </el-card>
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon likes">
            <el-icon>
              <StarFilled />
            </el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ formatNumber(statistics.total_likes || 0) }}</div>
            <div class="stat-label">{{ t('admin.analytics.stats.total_likes') }}</div>
          </div>
        </el-card>
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon comments">
            <el-icon>
              <ChatDotRound />
            </el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ formatNumber(statistics.total_comments || 0) }}</div>
            <div class="stat-label">{{ t('admin.analytics.stats.total_comments') }}</div>
          </div>
        </el-card>
      </div>
    </section>

    <!-- View Trend Chart -->
    <section class="trend-section">
      <div class="section-header">
        <h2 class="section-title">{{ t('admin.analytics.trend.title') }}</h2>
        <div class="section-controls">
          <el-radio-group v-model="trendDays" @change="handleTrendDaysChange" class="trend-radio-group">
            <el-radio-button :value="7">{{ t('admin.analytics.time_range.week') }}</el-radio-button>
            <el-radio-button :value="30">{{ t('admin.analytics.time_range.month') }}</el-radio-button>
            <el-radio-button :value="90">{{ t('admin.analytics.time_range.quarter') }}</el-radio-button>
          </el-radio-group>
        </div>
      </div>
      <el-card class="chart-card" shadow="never">
        <div ref="chartRef" class="chart-container" :style="{ height: chartHeight }"></div>
        <el-empty v-if="!trendApiAvailable && !loadingTrend" :description="t('admin.analytics.api_not_implemented')"
          class="chart-empty" />
      </el-card>
    </section>

    <!-- Top Articles Table -->
    <section class="top-articles-section">
      <div class="section-header">
        <h2 class="section-title">{{ t('admin.analytics.top_articles.title') }}</h2>
        <div class="section-controls">
          <el-select v-model="topType" @change="handleTypeChange" class="type-select">
            <el-option :label="t('admin.analytics.top_articles.type_views')" value="views" />
            <el-option :label="t('admin.analytics.top_articles.type_likes')" value="likes" />
            <el-option :label="t('admin.analytics.top_articles.type_comments')" value="comments" />
          </el-select>
        </div>
      </div>

      <el-card class="table-card" shadow="never">
        <el-table :data="topArticles" v-loading="loading" class="top-articles-table" :header-cell-style="{
          backgroundColor: '#fafafa',
          fontWeight: 600,
          fontSize: '14px',
          padding: '12px 14px'
        }">
          <el-table-column :label="t('admin.analytics.top_articles.rank')" width="80" align="center">
            <template #default="{ $index }">
              <div class="rank-badge" :class="`rank-${$index + 1}`">
                {{ $index + 1 }}
              </div>
            </template>
          </el-table-column>
          <el-table-column :label="t('admin.analytics.top_articles.title')" min-width="200">
            <template #default="{ row }">
              <div class="article-title-cell">
                <el-link type="primary" :href="`/article/${row.slug}`" target="_blank" :underline="false"
                  class="article-link">
                  {{ row.title }}
                </el-link>
                <div class="article-meta">
                  <span class="meta-item">
                    <el-icon>
                      <Calendar />
                    </el-icon>
                    {{ formatDate(row.pub_time) }}
                  </span>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column :label="t('admin.analytics.top_articles.author')" width="120">
            <template #default="{ row }">
              <div class="author-cell">
                <el-avatar v-if="row.author_profile_image" :src="row.author_profile_image" :size="32"
                  class="author-avatar" />
                <el-avatar v-else :size="32" class="author-avatar">
                  <el-icon>
                    <User />
                  </el-icon>
                </el-avatar>
                <span class="author-name">{{ row.author_full_name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column :label="t('admin.analytics.top_articles.views')" width="100" align="center">
            <template #default="{ row }">
              <el-statistic :value="row.reads || 0" />
            </template>
          </el-table-column>
          <el-table-column :label="t('admin.analytics.top_articles.likes')" width="100" align="center">
            <template #default="{ row }">
              <el-statistic :value="row.likes || 0" />
            </template>
          </el-table-column>
          <el-table-column :label="t('admin.analytics.top_articles.comments')" width="100" align="center">
            <template #default="{ row }">
              <el-statistic :value="row.comments || 0" />
            </template>
          </el-table-column>
        </el-table>

        <el-empty v-if="!loading && topArticles.length === 0"
          :description="t('admin.analytics.top_articles.no_data')" />
      </el-card>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import * as echarts from 'echarts/core'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent
} from 'echarts/components'
import { LineChart } from 'echarts/charts'
import { CanvasRenderer } from 'echarts/renderers'
import type { EChartsOption } from 'echarts'
import {
  ElCard,
  ElTable,
  ElTableColumn,
  ElIcon,
  ElStatistic,
  ElSelect,
  ElOption,
  ElLink,
  ElAvatar,
  ElEmpty,
  ElMessage,
  ElAlert,
  ElRadioButton,
  ElRadioGroup
} from 'element-plus'
import {
  Document,
  View,
  StarFilled,
  ChatDotRound,
  Calendar,
  User,
  WarningFilled
} from '@element-plus/icons-vue'
import { getStatistics, getTopArticles, getViewTrend } from '@/api/services/articles'

// 注册 echarts 组件
echarts.use([GridComponent, TooltipComponent, LegendComponent, LineChart, CanvasRenderer])

interface Statistics {
  total_articles: number
  total_views: number
  total_likes: number
  total_comments: number
}

interface TopArticle {
  id: number
  title: string
  slug: string
  author_full_name: string
  author_username: string
  author_profile_image: string | null
  pub_time: number
  reads: number
  likes: number
  comments: number
}

interface TrendData {
  date: string
  views: number
}

const { t } = useI18n()

const loading = ref(false)
const loadingTrend = ref(false)
const statistics = ref<Statistics>({
  total_articles: 0,
  total_views: 0,
  total_likes: 0,
  total_comments: 0
})
const topArticles = ref<TopArticle[]>([])
const topType = ref<'views' | 'likes' | 'comments'>('views')
const trendDays = ref<7 | 30 | 90>(7)
const trendData = ref<TrendData[]>([])
const statisticsApiAvailable = ref(true)
const topArticlesApiAvailable = ref(true)
const trendApiAvailable = ref(true)

// 图表相关
const chartRef = ref<HTMLDivElement>()
const chartInstance = ref<echarts.ECharts>()
const chartHeight = ref('350px')

// 是否显示 API 未实现提示
const showApiWarning = computed(() => {
  return !statisticsApiAvailable.value || !topArticlesApiAvailable.value
})

// Format large numbers with K suffix
const formatNumber = (num: number): string => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

// Format timestamp to readable date
const formatDate = (timestamp: number): string => {
  const date = new Date(timestamp * 1000)
  const now = new Date()
  const diffInDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24))

  if (diffInDays === 0) {
    return t('admin.general.time.today')
  } else if (diffInDays === 1) {
    return t('admin.general.time.yesterday')
  } else if (diffInDays < 7) {
    return t('admin.general.time.days_ago', { days: diffInDays })
  } else if (diffInDays < 30) {
    return t('admin.general.time.weeks_ago', { weeks: Math.floor(diffInDays / 7) })
  } else if (diffInDays < 365) {
    return t('admin.general.time.months_ago', { months: Math.floor(diffInDays / 30) })
  } else {
    return date.toLocaleDateString()
  }
}

// Load statistics data
const loadStatistics = async () => {
  try {
    const response = await getStatistics()
    if (response.code === 1) {
      statistics.value = response.data
      statisticsApiAvailable.value = true
    }
  } catch (error: any) {
    console.error('Failed to load statistics:', error)
    if (error.response?.status === 404) {
      statisticsApiAvailable.value = false
    }
  }
}

// Load top articles
const loadTopArticles = async () => {
  loading.value = true
  try {
    const response = await getTopArticles(topType.value, 10)
    if (response.code === 1) {
      topArticles.value = response.data || []
      topArticlesApiAvailable.value = true
    }
  } catch (error: any) {
    console.error('Failed to load top articles:', error)
    if (error.response?.status === 404) {
      topArticlesApiAvailable.value = false
    } else {
      ElMessage.error(t('admin.general.action.load_failed'))
    }
  } finally {
    loading.value = false
  }
}

// Handle type change
const handleTypeChange = () => {
  if (topArticlesApiAvailable.value) {
    loadTopArticles()
  }
}

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return

  chartInstance.value = echarts.init(chartRef.value)
  updateChart()

  // 监听窗口大小变化
  window.addEventListener('resize', handleChartResize)
}

// 更新图表
const updateChart = () => {
  if (!chartInstance.value) return

  const dates = trendData.value.map((item) => item.date)
  const views = trendData.value.map((item) => item.views)

  const option: EChartsOption = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: 'transparent',
      textStyle: {
        color: '#fff'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates,
      axisLine: {
        lineStyle: {
          color: 'var(--el-border-color)'
        }
      },
      axisLabel: {
        color: 'var(--el-text-color-regular)',
        fontSize: 12
      }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        show: false
      },
      axisLabel: {
        color: 'var(--el-text-color-regular)',
        fontSize: 12
      },
      splitLine: {
        lineStyle: {
          color: 'var(--el-border-color-darker)',
          type: 'dashed'
        }
      }
    },
    series: [
      {
        name: t('admin.analytics.trend.views'),
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        data: views,
        itemStyle: {
          color: '#6366f1'
        },
        lineStyle: {
          width: 2,
          color: '#6366f1'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(99, 102, 241, 0.3)' },
              { offset: 1, color: 'rgba(99, 102, 241, 0)' }
            ]
          }
        }
      }
    ]
  }

  chartInstance.value.setOption(option)
}

// 处理图表大小变化
const handleChartResize = () => {
  if (chartInstance.value) {
    chartInstance.value.resize()
  }
}

// 加载趋势数据
const loadTrendData = async () => {
  loadingTrend.value = true
  try {
    const response = await getViewTrend(trendDays.value)
    if (response.code === 1) {
      trendData.value = response.data || []
      trendApiAvailable.value = true
      await nextTick()
      if (!chartInstance.value) {
        initChart()
      } else {
        updateChart()
      }
    }
  } catch (error: any) {
    console.error('Failed to load trend data:', error)
    if (error.response?.status === 404) {
      trendApiAvailable.value = false
    }
  } finally {
    loadingTrend.value = false
  }
}

// 处理趋势天数变化
const handleTrendDaysChange = () => {
  loadTrendData()
}

// Initialize
onMounted(() => {
  loadStatistics()
  loadTopArticles()
  loadTrendData()
})

// Cleanup
onUnmounted(() => {
  window.removeEventListener('resize', handleChartResize)
  if (chartInstance.value) {
    chartInstance.value.dispose()
  }
})
</script>

<style scoped lang="scss">
.analytics-container {
  padding: 24px;
}

.api-warning {
  margin-bottom: 24px;
}

.warning-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-header {
  margin-bottom: 32px;

  h1 {
    margin: 0 0 8px 0;
    font-size: 24px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  p {
    margin: 0;
    font-size: 14px;
    color: var(--el-text-color-secondary);
  }
}

.section-title {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.stats-section {
  margin-bottom: 32px;
  opacity: 1;
  transition: opacity 0.3s;

  &.api-unavailable {
    opacity: 0.5;
    pointer-events: none;
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  transition: transform 0.2s, box-shadow 0.2s;

  &:hover {
    transform: translateY(-2px);
  }
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
  flex-shrink: 0;
  margin-bottom: 8px;

  &.articles {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }

  &.views {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  }

  &.likes {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  }

  &.comments {
    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  }
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--el-text-color-primary);
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.trend-section {
  margin-bottom: 32px;
}

.chart-card {
  position: relative;
  min-height: 350px;
}

.chart-container {
  width: 100%;
  height: 100%;
}

.chart-empty {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.trend-radio-group {
  display: flex;
}

.top-articles-section {
  margin-bottom: 32px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.section-controls {
  display: flex;
  gap: 12px;
}

.type-select {
  width: 120px;
}

.table-card {
  overflow: hidden;
}

.top-articles-table {
  :deep(.el-table__empty-block) {
    display: none;
  }
}

.rank-badge {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  background: var(--el-fill-color-light);
  color: var(--el-text-color-regular);

  &.rank-1 {
    background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
    color: #9a7d0a;
  }

  &.rank-2 {
    background: linear-gradient(135deg, #c0c0c0 0%, #e8e8e8 100%);
    color: #666;
  }

  &.rank-3 {
    background: linear-gradient(135deg, #cd7f32 0%, #e5a35a 100%);
    color: #8b5a2b;
  }
}

.article-title-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.article-link {
  font-weight: 500;
  font-size: 14px;
  color: var(--el-color-primary);
}

.article-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.author-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.author-avatar {
  flex-shrink: 0;
}

.author-name {
  font-size: 14px;
  color: var(--el-text-color-regular);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 768px) {
  .analytics-container {
    padding: 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
