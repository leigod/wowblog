<template>
  <div class="bcv-page" v-loading="loading">
    <template v-if="!loading">
      <BlogTopbar
        :blog="site.blog"
        :navs="site.navs || []"
        :categories="site.categories || []"
        :blog-title="blogTitle"
        :site-favicon="appStore.site_favicon || '/favicon.ico'"
        :is-dark="appStore.isDark"
        :is-authenticated="!!appStore.token && !!appStore.userRole"
        :active-cat-slug="categorySlug"
        :active-series-id="null"
        @nav-click="handleNavClick"
        @brand-click="goBlogHome"
        @toggle-dark="appStore.toggleDarkMode()"
        @go-write="goWrite"
        @search="(kw: string) => router.push({ path: '/search', query: { q: kw } })"
      />

      <main class="bcv-main">
        <!-- 分类头部 -->
        <header class="bcv-header">
          <div class="bcv-kicker">{{ t('blog.category.kicker') }}</div>
          <h1 class="bcv-title">{{ categoryDetail.name }}</h1>
          <p class="bcv-desc">{{ categoryDetail.description || '' }}</p>
        </header>

        <!-- 文章列表 -->
        <div class="bcv-list">
          <div
            v-for="item in articles"
            :key="item.id"
            class="bcv-row"
            @click="goArticle(item.slug)"
          >
            <div class="bcv-row-date">{{ formatDate(item.pub_time) }}</div>
            <div class="bcv-row-main">
              <h2 class="bcv-row-title">{{ item.title }}</h2>
              <p class="bcv-row-summary">{{ item.summary || item.subtitle || '' }}</p>
              <div class="bcv-row-meta">
                {{ readMinutes(item) }} {{ t('blog.home.min') }} · {{ item.views || 0 }} {{ t('blog.home.views') }}
              </div>
            </div>
            <div v-if="item.cover" class="bcv-row-thumb">
              <img :src="item.cover" :alt="item.title" />
            </div>
          </div>
          <el-empty
            v-if="!loading && articles.length === 0"
            :description="t('blog.category.empty')"
          />
        </div>

        <!-- 加载更多 -->
        <div v-if="hasMore" class="bcv-load-more">
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
  getPublicBlogCategory,
  getPublicBlogCategoryArticles
} from '@/api/services/creator'
import BlogTopbar from '@/components/blog/BlogTopbar.vue'
import BlogFooter from '@/components/blog/BlogFooter.vue'

interface CategoryArticle {
  id: number
  title: string
  slug: string
  cover: string | null
  subtitle?: string | null
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
const categoryDetail = ref<any>({})
const articles = ref<CategoryArticle[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = 10

const username = computed(() => String(route.params.username || ''))
const categorySlug = computed(() => String(route.params.categorySlug || ''))
const blogTitle = computed(() =>
  site.value.blog?.blog_name || site.value.user?.full_name || username.value
)
const hasMore = computed(() => articles.value.length < total.value)

const formatDate = (ts: number | null) => {
  if (!ts) return ''
  return new Date(ts * 1000).toLocaleDateString('zh-CN', {
    year: 'numeric', month: 'short', day: 'numeric'
  })
}
const readMinutes = (a: CategoryArticle) => Math.max(1, Math.ceil((a.content_len || 0) / 400))
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
  const res = await getPublicBlogCategoryArticles(username.value, categorySlug.value, {
    page, pageSize
  })
  if (res.code === 1 && res.data) {
    const list = (res.data.list || []) as CategoryArticle[]
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
    const detailRes = await getPublicBlogCategory(username.value, categorySlug.value)
    if (detailRes.code === 1 && detailRes.data) {
      categoryDetail.value = detailRes.data
      document.title = `${detailRes.data.name} - ${blogTitle.value}`
    } else {
      router.push('/404')
      return
    }
    await fetchArticles(1, false)
  } catch (error) {
    console.error('加载 blog 分类页失败:', error)
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
watch([username, categorySlug], () => loadAll())
</script>

<style scoped>
.bcv-page {
  min-height: 100vh;
  background: var(--el-bg-color-page, #f7f8fa);
}
.bcv-main {
  max-width: 1100px;
  margin: 0 auto;
  padding: 40px 24px 64px;
}
.bcv-header {
  margin-bottom: 32px;
  padding-bottom: 28px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}
.bcv-kicker {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  margin-bottom: 8px;
}
.bcv-title {
  font-size: 40px;
  font-weight: 700;
  line-height: 1.2;
  margin: 0 0 12px;
  color: var(--el-text-color-primary);
}
.bcv-desc {
  font-size: 15px;
  line-height: 1.7;
  color: var(--el-text-color-secondary);
  margin: 0;
}
.bcv-list {
  display: flex;
  flex-direction: column;
}
.bcv-row {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 24px 0;
  border-bottom: 1px solid var(--el-border-color-lighter);
  cursor: pointer;
  transition: background 0.2s;
}
.bcv-row:hover {
  background: var(--el-fill-color-lighter);
}
.bcv-row-date {
  width: 110px;
  flex-shrink: 0;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}
.bcv-row-main {
  flex: 1;
  min-width: 0;
}
.bcv-row-title {
  font-size: 17px;
  font-weight: 600;
  line-height: 1.5;
  margin: 0 0 6px;
  color: var(--el-text-color-primary);
}
.bcv-row-summary {
  font-size: 14px;
  line-height: 1.6;
  color: var(--el-text-color-secondary);
  margin: 0 0 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.bcv-row-meta {
  font-size: 12px;
  color: var(--el-text-color-placeholder);
}
.bcv-row-thumb {
  width: 150px;
  height: 96px;
  flex-shrink: 0;
  border-radius: 8px;
  overflow: hidden;
  background: var(--el-fill-color-light);
}
.bcv-row-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.bcv-load-more {
  display: flex;
  justify-content: center;
  padding: 32px 0 0;
}
@media (max-width: 768px) {
  .bcv-title { font-size: 30px; }
  .bcv-row { gap: 14px; flex-wrap: wrap; }
  .bcv-row-date { width: auto; }
  .bcv-row-thumb { width: 100%; height: 160px; order: -1; }
}
</style>
