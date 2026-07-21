<template>
  <div class="search-result-container">
    <!-- 顶部搜索栏 -->
    <div class="search-header">
      <div class="search-header-content">
        <div class="search-bar-wrapper">
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
    </div>

    <!-- 搜索统计信息 -->
    <div v-if="searchKeyword && !loading" class="search-stats">
      <span v-html="t('search.results_found', { total: total })"></span>
      <span class="search-time" v-html="t('search.results_time', { time: Math.floor(Math.random() * 50) + 20 })"></span>
    </div>

    <!-- 搜索结果列表 -->
    <div class="search-content-wrapper">
      <div v-loading="loading" class="search-content">
      <template v-if="!loading && searchResults.length > 0">
        <div
          v-for="article in searchResults"
          :key="article.id"
          class="search-result-item"
        >
          <!-- URL链接 -->
          <div class="result-url">
            <a :href="`/article/${article.slug}`" @click.prevent="navigateToArticle(article.slug)">
              {{ siteUrl }}/article/{{ article.slug }}
            </a>
          </div>
          <!-- 标题 -->
          <h3 class="result-title">
            <a :href="`/article/${article.slug}`" @click.prevent="navigateToArticle(article.slug)" v-html="highlightKeyword(article.title)">
            </a>
          </h3>
          <!-- 摘要 -->
          <p class="result-excerpt" v-html="highlightKeyword(getExcerpt(article.content))">
          </p>
          <!-- 元信息 -->
          <div class="result-meta">
            <span class="meta-info">
              {{ formatDate(article.pub_time || article.createtime) }} -
            </span>
            <span class="meta-author">
              <el-avatar :size="20" :src="article.author_profile_image">
                {{ article.author_full_name?.charAt(0) || '?' }}
              </el-avatar>
              {{ article.author_full_name }}
            </span>
              <span class="meta-views" v-if="article.reads">
              - {{ t('search.reads', { reads: article.reads }) }}
            </span>
          </div>
        </div>
      </template>

      <!-- 无结果 -->
      <div v-else-if="!loading && searchKeyword && searchResults.length === 0" class="no-results">
        <p class="no-results-text" v-html="t('search.no_results', { keyword: searchKeyword })">
        </p>
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
          <el-icon :size="80"><Search /></el-icon>
        </div>
        <p class="initial-text">{{ t('search.initial_state') }}</p>
      </div>
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
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { searchArticles, type SearchResultArticle } from '@/api/services/articles'
import { formatDateTime } from '@/utils/dateUtils'

const { t } = useI18n()

console.log('[SearchResult] Component script loaded')

const router = useRouter()
const route = useRoute()

const searchKeyword = ref('')
const searchResults = ref<SearchResultArticle[]>([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const siteUrl = computed(() => window.location.origin)

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
  console.log('[Search] performSearch called with keyword:', keyword)
  console.log('[Search] currentPage:', currentPage.value, 'pageSize:', pageSize.value)

  if (!keyword) {
    searchResults.value = []
    total.value = 0
    return
  }

  loading.value = true
  try {
    console.log('[Search] Calling searchArticles API...')
    const response = await searchArticles(keyword, currentPage.value, pageSize.value)
    console.log('[Search] API response:', response)
    // 响应结构: { code: 1, data: { list: [], total: 0 } }
    searchResults.value = response.data?.list || []
    total.value = response.data?.total || 0
    console.log('[Search] Results count:', searchResults.value.length, 'Total:', total.value)
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
  // 滚动到顶部
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
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 20px 40px;
}

/* 顶部搜索栏 */
.search-header {
  position: sticky;
  top: 0;
  background: var(--el-bg-color);
  padding: 20px 0;
  border-bottom: 1px solid var(--el-border-color-light);
  z-index: 100;

  .search-header-content {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    align-items: center;
  }

  .search-bar-wrapper {
    flex: 1;
  }

  .search-bar {
    display: flex;
    gap: 10px;

    .search-input {
      flex: 1;

      :deep(.el-input__wrapper) {
        border-radius: 24px;
        box-shadow: 0 1px 6px rgba(32, 33, 36, 0.28);
        border-color: transparent;
        padding: 5px 15px;

        &:hover,
        &.is-focus {
          box-shadow: 0 1px 6px rgba(32, 33, 36, 0.28);
        }
      }
    }

    .search-btn {
      border-radius: 24px;
      padding: 12px 24px;
    }
  }
}

/* 搜索统计 */
.search-stats {
  padding: 15px 0;
  font-size: 14px;
  color: #70757a;
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;

  .search-time {
    color: #70757a;
  }

  strong {
    color: #202124;
  }
}

/* 搜索结果 */
.search-content-wrapper {
  width: 800px;
  margin: 0 auto;
}

.search-content {
  min-height: 400px;
  padding-bottom: 20px;
}

.search-result-item {
  padding: 16px 0;
  border-bottom: 1px solid var(--el-border-color-lighter);

  &:last-child {
    border-bottom: none;
  }

  .result-url {
    font-size: 12px;
    color: var(--el-text-color-secondary);
    margin-bottom: 4px;

    a {
      color: var(--el-text-color-secondary);
      text-decoration: none;

      &:hover {
        text-decoration: underline;
      }
    }
  }

  .result-title {
    font-size: 20px;
    margin: 0 0 4px 0;
    line-height: 1.3;

    a {
      color: var(--el-color-primary);
      text-decoration: none;

      &:hover {
        text-decoration: underline;
      }

      :deep(em) {
        font-style: normal;
        font-weight: bold;
      }
    }
  }

  .result-excerpt {
    font-size: 14px;
    line-height: 1.58;
    color: var(--el-text-color-regular);
    margin: 0 0 8px 0;

    :deep(em) {
      font-style: normal;
      font-weight: bold;
      color: var(--el-color-danger);  /* 红色高亮 */
    }
  }

  .result-meta {
    font-size: 12px;
    color: var(--el-text-color-secondary);
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;

    .meta-author {
      display: flex;
      align-items: center;
      gap: 4px;
      color: var(--el-text-color-primary);
    }
  }
}

/* 无结果状态 */
.no-results {
  padding: 40px 20px;
  text-align: left;

  .no-results-text {
    font-size: 16px;
    color: var(--el-text-color-primary);
    margin-bottom: 20px;
  }

  .no-results-suggestion {
    font-size: 14px;
    color: var(--el-text-color-secondary);
    margin-bottom: 10px;
  }

  .suggestions {
    list-style: none;
    padding: 0;
    margin: 0;

    li {
      font-size: 14px;
      color: var(--el-text-color-primary);
      padding: 4px 0;
      padding-left: 20px;
      position: relative;

      &:before {
        content: '•';
        position: absolute;
        left: 0;
        color: var(--el-text-color-secondary);
      }
    }
  }
}

/* 初始状态 */
.initial-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;

  .search-icon {
    color: var(--el-text-color-placeholder);
    margin-bottom: 20px;
  }

  .initial-text {
    font-size: 16px;
    color: var(--el-text-color-secondary);
    margin: 0;
  }
}

/* 分页 */
.pagination-wrap {
  display: flex;
  justify-content: center;
  padding: 30px 0;

  :deep(.el-pagination) {
    .btn-prev,
    .btn-next,
    .el-pager li {
      background: var(--el-fill-color-light);
      border-radius: 50%;
      width: 36px;
      height: 36px;
      line-height: 36px;
      margin: 0 4px;
      font-weight: 500;
      color: var(--el-text-color-primary);

      &:hover {
        background: var(--el-fill-color);
      }

      &.is-active {
        background: var(--el-color-primary);
        color: #fff;
      }
    }
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .search-result-container {
    padding: 15px 10px;
  }

  .search-header {
    padding: 15px 0;

    .search-header-content {
      flex-direction: column;
      gap: 15px;
    }

    .search-bar {
      flex-direction: column;
      gap: 8px;

      .search-input {
        width: 100%;

        :deep(.el-input__wrapper) {
          padding: 8px 12px;
        }
      }

      .search-btn {
        width: 100%;
        padding: 10px 20px;
      }
    }
  }

  .search-stats {
    font-size: 12px;
    padding: 10px 0;
    flex-direction: column;
    gap: 4px;
  }

  .search-content-wrapper {
    width: 100%;
  }

  .search-result-item {
    padding: 12px 0;

    .result-url {
      font-size: 11px;
      word-break: break-all;
    }

    .result-title {
      font-size: 16px;
      line-height: 1.4;

      a {
        word-break: break-word;
      }
    }

    .result-excerpt {
      font-size: 13px;
      line-height: 1.6;
    }

    .result-meta {
      font-size: 11px;
      flex-wrap: wrap;

      .meta-author {
        font-size: 11px;
      }
    }
  }

  .no-results {
    padding: 30px 15px;

    .no-results-text {
      font-size: 14px;
    }

    .no-results-suggestion {
      font-size: 13px;
    }

    .suggestions li {
      font-size: 13px;
      padding: 3px 0;
    }
  }

  .initial-state {
    padding: 60px 20px;

    .search-icon {
      :deep(.el-icon) {
        font-size: 60px !important;
      }
    }

    .initial-text {
      font-size: 14px;
    }
  }

  .pagination-wrap {
    padding: 20px 0;

    :deep(.el-pagination) {
      .btn-prev,
      .btn-next,
      .el-pager li {
        width: 32px;
        height: 32px;
        line-height: 32px;
        font-size: 13px;
        margin: 0 2px;
      }
    }
  }
}

/* 超小屏幕优化 */
@media (max-width: 480px) {
  .search-result-container {
    padding: 10px 8px;
  }

  .search-header {
    padding: 10px 0;
  }

  .search-result-item {
    .result-title {
      font-size: 15px;
    }

    .result-excerpt {
      font-size: 12px;
    }
  }

  .result-meta .meta-author {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 150px;
  }
}
</style>
