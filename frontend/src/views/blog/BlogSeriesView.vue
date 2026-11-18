<template>
  <div class="bsv-page" v-loading="loading">
    <template v-if="!loading">
      <BlogTopbar
        :blog="site.blog"
        :navs="site.navs || []"
        :categories="site.categories || []"
        :blog-title="blogTitle"
        :site-favicon="appStore.site_favicon || '/favicon.ico'"
        :is-dark="appStore.isDark"
        :is-authenticated="!!appStore.token && !!appStore.userRole"
        :active-series-id="activeSeriesId"
        @nav-click="handleNavClick"
        @brand-click="goBlogHome"
        @toggle-dark="appStore.toggleDarkMode()"
        @go-write="goWrite"
        @search="(kw: string) => router.push({ path: '/search', query: { q: kw } })"
      />

      <main class="bsv-main">
        <!-- 系列头部 -->
        <header class="bsv-header">
          <div class="bsv-kicker">{{ t('blog.series.kicker') }}</div>
          <h1 class="bsv-title">{{ seriesDetail.name }}</h1>
          <p class="bsv-desc">{{ seriesDetail.description || '' }}</p>
        </header>

        <!-- 文章列表 -->
        <div class="bsv-list">
          <div
            v-for="(item, idx) in articles"
            :key="item.id"
            class="bsv-row"
            @click="goArticle(item.slug)"
          >
            <div class="bsv-row-date">{{ formatDate(item.pub_time) }}</div>
            <div class="bsv-row-main">
              <h2 class="bsv-row-title">{{ item.title }}</h2>
              <p class="bsv-row-summary">{{ item.summary || item.subtitle || '' }}</p>
              <div class="bsv-row-meta">
                {{ readMinutes(item) }} {{ t('blog.home.min') }} · {{ item.views || 0 }} {{ t('blog.home.views') }}
              </div>
            </div>
            <div v-if="item.cover" class="bsv-row-thumb">
              <img :src="item.cover" :alt="item.title" />
            </div>
          </div>
          <el-empty
            v-if="!loading && articles.length === 0"
            :description="t('blog.series.empty')"
          />
        </div>

        <!-- 加载更多 -->
        <div v-if="hasMore" class="bsv-load-more">
          <el-button :loading="loadingMore" round @click="loadMore">{{ t('home.list.loadmore') }}</el-button>
        </div>
      </main>

      <BlogFooter
        :impressum="site.blog?.impressum"
        :createtime="site.blog?.createtime"
        :blog-title="blogTitle"
        :site-favicon="appStore.site_favicon || '/favicon.ico'"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAppStore } from '@/stores/app'
import {
  getBlogSite,
  getPublicBlogSeries,
  getPublicBlogSeriesArticles
} from '@/api/services/creator'
import BlogTopbar from '@/components/blog/BlogTopbar.vue'
import BlogFooter from '@/components/blog/BlogFooter.vue'

interface SeriesArticle {
  id: number
  title: string
  slug: string
  cover: string | null
  subtitle: string | null
  summary?: string | null
  pub_time: number | null
  views: number
  content_len?: number
}

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const appStore = useAppStore()

const loading = ref(true)
const loadingMore = ref(false)
const site = ref<any>({ blog: null, navs: [], categories: [], series: [], user: {} })
const seriesDetail = ref<any>({})
const articles = ref<SeriesArticle[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = 10

const username = computed(() => String(route.params.username || ''))
const seriesSlug = computed(() => String(route.params.seriesSlug || ''))
const blogTitle = computed(() =>
  site.value.blog?.blog_name || site.value.user?.full_name || username.value
)
// 顶栏系列导航高亮：导航项 value 存系列 id，当前页按 slug 反查 id
const activeSeriesId = computed<number | null>(() => {
  const match = (site.value.series || []).find((s: any) => s.slug === seriesSlug.value)
  return match ? Number(match.id) : null
})

const hasMore = computed(() => articles.value.length < total.value)

const formatDate = (ts: number | null) => {
  if (!ts) return ''
  return new Date(ts * 1000).toLocaleDateString('zh-CN', {
    year: 'numeric', month: 'short', day: 'numeric'
  })
}
const readMinutes = (a: SeriesArticle) => Math.max(1, Math.ceil((a.content_len || 0) / 400))
const goArticle = (slug: string) => { if (slug) router.push(`/article/${slug}`) }
const goBlogHome = () => router.push(`/blog/${username.value}`)
const goWrite = () => {
  window.open(appStore.userRole === 'Author' ? '/creator/articles/create' : '/my-articles/create', '_blank')
}
// 顶栏导航：分类/系列跳各自列表页，外链新开窗口
const resolveNavSlug = (nav: any) => {
  if (nav.type === 'category') {
    return site.value.categories?.find((c: any) => String(c.id) === nav.value)?.slug || nav.value
  }
  return site.value.series?.find((s: any) => String(s.id) === nav.value)?.slug || nav.value
}
const handleNavClick = (nav: any) => {
  if (!nav) return
  if (nav.type === 'link') {
    if (nav.value) window.open(nav.value, '_blank')
  } else if (nav.type === 'series') {
    router.push(`/blog/${username.value}/series/${resolveNavSlug(nav)}`)
  } else {
    router.push(`/blog/${username.value}/category/${resolveNavSlug(nav)}`)
  }
}

const fetchArticles = async (page: number, append: boolean) => {
  const res = await getPublicBlogSeriesArticles(username.value, seriesSlug.value, {
    page, pageSize
  })
  if (res.code === 1 && res.data) {
    const list = (res.data.list || []) as SeriesArticle[]
    articles.value = append ? [...articles.value, ...list] : list
    total.value = res.data.total || 0
  }
}

const loadAll = async () => {
  loading.value = true
  currentPage.value = 1
  try {
    const siteRes = await getBlogSite(username.value)
    if (siteRes.code === 1 && siteRes.data) site.value = siteRes.data
    const detailRes = await getPublicBlogSeries(username.value, seriesSlug.value)
    if (detailRes.code === 1 && detailRes.data) {
      seriesDetail.value = detailRes.data
      document.title = `${detailRes.data.name} - ${blogTitle.value}`
    } else {
      router.push('/404')
      return
    }
    await fetchArticles(1, false)
  } catch (error) {
    console.error('加载 blog 系列页失败:', error)
    router.push('/404')
  } finally {
    loading.value = false
  }
}

const loadMore = async () => {
  loadingMore.value = true
  try {
    currentPage.value++
    await fetchArticles(currentPage.value, true)
  } finally {
    loadingMore.value = false
  }
}

/* ---------- 标签页 favicon 跟随当前 blog ---------- */
const FAVICON_LINK_ID = 'dynamic-favicon'
const applyBlogFavicon = () => {
  const link = document.getElementById(FAVICON_LINK_ID) as HTMLLinkElement | null
  const icon = site.value.blog?.favicon || site.value.user?.profile_image
  if (link && icon) link.href = icon
}
const restoreSiteFavicon = () => {
  const link = document.getElementById(FAVICON_LINK_ID) as HTMLLinkElement | null
  if (link) link.href = appStore.site_favicon || '/favicon.ico'
}
watch(() => [site.value.blog?.favicon, site.value.user?.profile_image], applyBlogFavicon)
onBeforeUnmount(restoreSiteFavicon)

onMounted(loadAll)
watch([username, seriesSlug], () => loadAll())
</script>

<style scoped>
.bsv-page {
  min-height: 100vh;
  background: var(--el-bg-color-page, #f7f8fa);
}
.bsv-main {
  max-width: 1100px;
  margin: 0 auto;
  padding: 40px 24px 64px;
}
.bsv-header {
  margin-bottom: 32px;
  padding-bottom: 28px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}
.bsv-kicker {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  margin-bottom: 8px;
}
.bsv-title {
  font-size: 40px;
  font-weight: 700;
  line-height: 1.2;
  margin: 0 0 12px;
  color: var(--el-text-color-primary);
}
.bsv-desc {
  font-size: 15px;
  line-height: 1.7;
  color: var(--el-text-color-secondary);
  margin: 0;
}
.bsv-list {
  display: flex;
  flex-direction: column;
}
.bsv-row {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 24px 0;
  border-bottom: 1px solid var(--el-border-color-lighter);
  cursor: pointer;
  transition: background 0.2s;
}
.bsv-row:hover {
  background: var(--el-fill-color-lighter);
}
.bsv-row-date {
  width: 110px;
  flex-shrink: 0;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}
.bsv-row-main {
  flex: 1;
  min-width: 0;
}
.bsv-row-title {
  font-size: 17px;
  font-weight: 600;
  line-height: 1.5;
  margin: 0 0 6px;
  color: var(--el-text-color-primary);
}
.bsv-row-summary {
  font-size: 14px;
  line-height: 1.6;
  color: var(--el-text-color-secondary);
  margin: 0 0 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.bsv-row-meta {
  font-size: 12px;
  color: var(--el-text-color-placeholder);
}
.bsv-row-thumb {
  width: 150px;
  height: 96px;
  flex-shrink: 0;
  border-radius: 8px;
  overflow: hidden;
  background: var(--el-fill-color-light);
}
.bsv-row-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.bsv-load-more {
  display: flex;
  justify-content: center;
  padding: 32px 0 0;
}
@media (max-width: 768px) {
  .bsv-title { font-size: 30px; }
  .bsv-row { gap: 14px; flex-wrap: wrap; }
  .bsv-row-date { width: auto; }
  .bsv-row-thumb { width: 100%; height: 160px; order: -1; }
}
</style>
