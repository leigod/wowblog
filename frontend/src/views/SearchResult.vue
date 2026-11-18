<template>
  <div class="search-result-container">
    <!-- 顶部搜索栏：吸顶 + 表面色，输入框收回 8px / 细描边（原为 24px 胶囊 + Google 阴影） -->
    <div class="search-header">
      <div class="search-header-content">
        <div class="search-bar">
          <el-input
            v-model="searchKeyword"
            class="search-input"
            :placeholder="t('search.placeholder')"
            clearable
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button type="primary" class="search-btn" @click="handleSearch">
            {{ t('search.button') }}
          </el-button>
        </div>
      </div>
    </div>

    <div class="search-body">
      <!-- 搜索统计信息 -->
      <div v-if="searchKeyword && !loading" class="search-stats">
        <span v-html="t('search.results_found', { total: total })"></span>
        <span class="search-time" v-html="t('search.results_time', { time: Math.floor(Math.random() * 50) + 20 })"></span>
      </div>

      <!-- 搜索结果列表：Google 式扁平排版 —— 元信息行在上、大标题、摘要，无卡片描边 -->
      <div v-loading="loading" class="search-content">
        <template v-if="!loading && searchResults.length > 0">
          <div
            v-for="article in searchResults"
            :key="article.id"
            class="search-result-item"
            @click="navigateToArticle(article.slug)"
          >
            <!-- 站点行：作者 · 日期 · 阅读数 -->
            <div class="result-meta">
              <span class="meta-author">
                <el-avatar :size="22" :src="article.author_profile_image">
                  {{ article.author_full_name?.charAt(0) || '?' }}
                </el-avatar>
                {{ article.author_full_name }}
              </span>
              <span class="meta-dot">·</span>
              <span class="meta-info">{{ formatDate(article.pub_time || article.createtime) }}</span>
              <template v-if="article.reads">
                <span class="meta-dot">·</span>
                <span class="meta-views">{{ t('search.reads', { reads: article.reads }) }}</span>
              </template>
            </div>
            <!-- 标题 -->
            <h3 class="result-title">
              <a :href="`/article/${article.slug}`" @click.prevent="navigateToArticle(article.slug)"
                v-html="highlightKeyword(article.title)">
              </a>
            </h3>
            <!-- 摘要 -->
            <p class="result-excerpt" v-html="highlightKeyword(getExcerpt(article.content))"></p>
          </div>
        </template>

        <!-- 无结果 -->
        <div v-else-if="!loading && searchKeyword && searchResults.length === 0" class="no-results">
          <p class="no-results-text" v-html="t('search.no_results', { keyword: searchKeyword })"></p>
          <p class="no-results-suggestion">{{ t('search.suggestions_title') }}</p>
          <ul class="suggestions">
            <li>{{ t('search.suggestion_check_input') }}</li>
            <li>{{ t('search.suggestion_try_other') }}</li>
            <li>{{ t('search.suggestion_try_general') }}</li>
          </ul>
        </div>

        <!-- 初始状态 -->
        <div v-else-if="!loading && !searchKeyword" class="initial-state">
          <div class="search-icon">
            <el-icon :size="56"><Search /></el-icon>
          </div>
          <p class="initial-text">{{ t('search.initial_state') }}</p>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="total > pageSize" class="pagination-wrap">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="prev, pager, next"
          @current-change="handlePageChange"
          small
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { searchArticles, type SearchResultArticle } from '@/api/services/articles'
import { formatDateTime } from '@/utils/dateUtils'

const { t } = useI18n()

const router = useRouter()
const route = useRoute()

const searchKeyword = ref('')
const searchResults = ref<SearchResultArticle[]>([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 从URL获取关键词
onMounted(() => {
  const keyword = route.query.q as string
  if (keyword) {
    searchKeyword.value = keyword
    performSearch()
  }
})

// 监听路由参数变化
watch(() => route.query.q, (newKeyword) => {
  if (newKeyword) {
    searchKeyword.value = newKeyword as string
    currentPage.value = 1
    performSearch()
  }
})

// 执行搜索
const performSearch = async () => {
  const keyword = searchKeyword.value.trim()
  if (!keyword) {
    searchResults.value = []
    total.value = 0
    return
  }

  loading.value = true
  try {
    const response = await searchArticles(keyword, currentPage.value, pageSize.value)
    // 响应结构: { code: 1, data: { list: [], total: 0 } }
    searchResults.value = response.data?.list || []
    total.value = response.data?.total || 0
  } catch (error) {
    console.error('[Search] API error:', error)
    ElMessage.error(t('search.failed'))
    searchResults.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 处理搜索按钮点击
const handleSearch = () => {
  if (!searchKeyword.value.trim()) {
    ElMessage.warning(t('search.no_keyword'))
    return
  }
  currentPage.value = 1
  // 更新URL参数
  router.push({ path: '/search', query: { q: searchKeyword.value.trim() } })
}

// 处理页码变化
const handlePageChange = (page: number) => {
  currentPage.value = page
  performSearch()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 导航到文章详情
const navigateToArticle = (slug: string) => {
  router.push(`/article/${slug}`)
}

// 高亮关键词
const highlightKeyword = (text: string): string => {
  if (!text || !searchKeyword.value.trim()) return text
  const keyword = searchKeyword.value.trim().toLowerCase()
  const regex = new RegExp(`(${escapeRegExp(keyword)})`, 'gi')
  return text.replace(regex, '<em>$1</em>')
}

// 转义正则表达式特殊字符
const escapeRegExp = (string: string): string => {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

// 获取文章摘要
const getExcerpt = (content: string, maxLength: number = 160): string => {
  if (!content) return ''
  // 移除HTML标签
  const text = content.replace(/<[^>]+>/g, '')
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

// 格式化日期
const formatDate = (timestamp: number): string => {
  return formatDateTime(timestamp, 'YYYY年MM月DD日')
}
</script>

<style scoped lang="scss">
.search-result-container {
  /* 外层布局是 flex 容器，根节点必须显式 width:100%，
     否则整列收缩为内容宽度（单条短摘要时整列变窄） */
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px 64px;
}

/* ---------- 顶部搜索栏：吸顶，表面色 + 细描边 ---------- */
.search-header {
  position: sticky;
  top: 0;
  z-index: 100;
  margin: 0 -20px 24px;
  padding: 16px 20px;
  background-color: var(--wy-bg-canvas, #fafafa);
  background: color-mix(in srgb, var(--wy-bg-canvas, #fafafa) 86%, transparent);
  backdrop-filter: saturate(180%) blur(12px);
  border-bottom: 1px solid var(--wy-border-subtle, #e4e4e7);
}

.search-header-content {
  width: 100%;
  max-width: 680px;
  margin: 0 auto;
}

.search-bar {
  display: flex;
  gap: 8px;

  .search-input {
    flex: 1;

    /* 胶囊 + Google 投影 → 规范输入框：8px、细描边、无阴影 */
    :deep(.el-input__wrapper) {
      border-radius: var(--wy-radius-md, 8px);
      box-shadow: 0 0 0 1px var(--wy-border-subtle, #e4e4e7) inset;
      padding: 2px 12px;
      background-color: var(--wy-bg-surface, #fff);

      &:hover {
        box-shadow: 0 0 0 1px var(--wy-border-strong, #d4d4d8) inset;
      }

      &.is-focus {
        box-shadow: 0 0 0 2px var(--wy-brand, #2f5fd0) inset;
      }
    }
  }

  .search-btn {
    border-radius: var(--wy-radius-md, 8px);
    padding: 8px 20px;
    font-weight: 500;
  }
}

/* ---------- 结果区：固定宽度内容列（Google 约 650px），左对齐、不随内容伸缩 ---------- */
.search-body {
  width: 100%;
  max-width: 680px;
  margin: 0 auto;
}

.search-stats {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 16px;
  font-size: 13px;
  color: var(--wy-text-tertiary, #71717a);

  .search-time {
    color: var(--wy-text-placeholder, #a1a1aa);
  }

  :deep(strong) {
    color: var(--wy-text-secondary, #52525b);
    font-weight: 600;
  }
}

.search-content {
  min-height: 360px;
}

/* 结果项：Google 式扁平排版 —— 无卡片描边，靠留白分隔；列宽固定，不随内容变化 */
.search-result-item {
  padding: 18px 0;
  cursor: pointer;

  .result-meta {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 8px;
    font-size: 13px;
    color: var(--wy-text-tertiary, #71717a);

    .meta-author {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      color: var(--wy-text-secondary, #52525b);
    }

    .meta-dot {
      color: var(--wy-text-placeholder, #a1a1aa);
    }
  }

  .result-title {
    margin: 0 0 6px;
    font-size: 20px;
    font-weight: 500;
    line-height: 1.4;

    a {
      color: var(--wy-brand, #2f5fd0);
      text-decoration: none;
      transition: color var(--wy-duration, 160ms) var(--wy-easing, ease);
    }

    &:hover a {
      text-decoration: underline;
      text-underline-offset: 3px;
    }

    :deep(em) {
      font-style: normal;
      font-weight: 600;
    }
  }

  .result-excerpt {
    margin: 0;
    font-size: 14px;
    line-height: 1.65;
    color: var(--wy-text-secondary, #52525b);
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    overflow: hidden;

    /* 关键词高亮：Google 式加粗深色，不铺底色 */
    :deep(em) {
      font-style: normal;
      font-weight: 600;
      color: var(--wy-text-primary, #18181b);
    }
  }
}

/* ---------- 无结果 ---------- */
.no-results {
  padding: 32px 4px;

  .no-results-text {
    margin: 0 0 12px;
    font-size: 16px;
    color: var(--wy-text-primary, #18181b);

    :deep(strong) {
      font-weight: 600;
    }
  }

  .no-results-suggestion {
    margin: 0 0 10px;
    font-size: 14px;
    color: var(--wy-text-secondary, #52525b);
  }

  .suggestions {
    margin: 0;
    padding: 0;
    list-style: none;

    li {
      position: relative;
      padding: 4px 0 4px 16px;
      font-size: 14px;
      color: var(--wy-text-secondary, #52525b);

      &:before {
        content: '';
        position: absolute;
        left: 2px;
        top: 13px;
        width: 4px;
        height: 4px;
        border-radius: 50%;
        background: var(--wy-text-placeholder, #a1a1aa);
      }
    }
  }
}

/* ---------- 初始状态 ---------- */
.initial-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;

  .search-icon {
    color: var(--wy-text-placeholder, #a1a1aa);
    margin-bottom: 16px;
  }

  .initial-text {
    margin: 0;
    font-size: 15px;
    color: var(--wy-text-tertiary, #71717a);
  }
}

/* ---------- 分页 ---------- */
.pagination-wrap {
  display: flex;
  justify-content: center;
  padding: 28px 0 8px;

  :deep(.el-pagination) {
    .btn-prev,
    .btn-next,
    .el-pager li {
      width: 34px;
      height: 34px;
      line-height: 34px;
      margin: 0 3px;
      border-radius: var(--wy-radius-md, 8px);
      background: var(--wy-bg-muted, #f5f5f5);
      color: var(--wy-text-secondary, #52525b);
      font-weight: 500;

      &:hover {
        background: var(--wy-brand-soft, #eef3fd);
        color: var(--wy-brand, #2f5fd0);
      }

      &.is-active {
        background: var(--wy-brand, #2f5fd0);
        color: var(--wy-on-brand, #fff);
      }
    }
  }
}

/* ---------- 移动端 ---------- */
@media (max-width: 767px) {
  .search-result-container {
    padding: 0 12px 48px;
  }

  .search-header {
    margin: 0 -12px 16px;
    padding: 12px;
  }

  .search-bar {
    gap: 8px;

    .search-btn {
      padding: 8px 14px;
    }
  }

  .search-stats {
    font-size: 12px;
    gap: 6px;
  }

  .search-result-item {
    padding: 14px 0;

    .result-title {
      font-size: 17px;
    }

    .result-excerpt {
      font-size: 13px;
    }

    .result-meta {
      font-size: 12px;
      gap: 6px;
    }
  }

  .initial-state {
    padding: 56px 16px;

    .initial-text {
      font-size: 14px;
    }
  }

  .pagination-wrap {
    padding: 20px 0 4px;

    :deep(.el-pagination) {
      .btn-prev,
      .btn-next,
      .el-pager li {
        width: 30px;
        height: 30px;
        line-height: 30px;
        margin: 0 2px;
        font-size: 13px;
      }
    }
  }
}
</style>
