<template>
  <div class="blog-home" v-loading="loading">
    <!-- 未开通引导 -->
    <div v-if="!loading && !site.blog?.opened" class="blog-not-opened">
      <h2>该用户尚未开通个人博客</h2>
      <p>仅 Author 角色开通后可展示，博主可从顶部头像菜单进入「Blog 工作台」开通。</p>
      <el-button type="primary" @click="$router.push('/')">返回首页</el-button>
    </div>

    <template v-if="!loading && site.blog?.opened">
      <!-- ① 顶栏：网站 logo（灰度，回站首页）+ 斜线 + blog logo / blog 名称（互斥展示） -->
      <BlogTopbar
        :blog="site.blog"
        :navs="site.navs || []"
        :categories="site.categories || []"
        :blog-title="blogTitle"
        :site-favicon="appStore.site_favicon || '/favicon.ico'"
        :is-dark="appStore.isDark"
        :is-authenticated="isAuthenticated"
        :active-cat-slug="activeCatSlug"
        :active-series-id="activeSeriesId"
        @nav-click="handleNavClick"
        @brand-click="resetFilter"
        @toggle-dark="appStore.toggleDarkMode()"
        @go-write="goWrite"
        @search="(kw: string) => { searchKeyword = kw; submitSearch() }"
      />

      <main class="bh-main" :class="`bh-main--${layout}`">
        <!-- 聚合标题（分类/系列过滤中） -->
        <div v-if="activeFilter" class="bh-filter-bar">
          <span>{{ activeFilterLabel }}</span>
          <el-button text size="small" @click="resetFilter">
            <el-icon><Close /></el-icon>
          </el-button>
        </div>

        <!-- ============ magazine 布局（默认，杂志风格）============ -->
        <template v-if="layout === 'magazine'">
        <!-- ② 焦点区：左焦点图 + 右副列 4 条（无文章时整体隐藏） -->
        <section v-if="articles.length > 0 && !activeFilter" class="bh-hero">
          <article v-if="heroArticle" class="bh-hero-main" @click="goArticle(heroArticle)">
            <div class="bh-hero-cover">
              <img v-if="heroArticle.cover" :src="heroArticle.cover" :alt="heroArticle.title" />
            </div>
            <div class="bh-hero-meta bh-meta">
              <span>{{ formatDate(heroArticle.pub_time || heroArticle.createtime) }}</span>
              <span>{{ readMinutes(heroArticle) }} {{ t('blog.home.min_read') }}</span>
              <span>{{ heroArticle.reads }} {{ t('blog.home.views') }}</span>
            </div>
            <h2 class="bh-hero-title">{{ heroArticle.title }}</h2>
            <p class="bh-hero-summary">{{ articleSummary(heroArticle) }}</p>
          </article>
          <aside class="bh-hero-side">
            <article
              v-for="a in sideArticles"
              :key="a.id"
              class="bh-hero-side-item"
              @click="goArticle(a)"
            >
              <div class="bh-side-info">
                <h3 class="bh-side-title">{{ a.title }}</h3>
                <div class="bh-meta">
                  <span>{{ formatDate(a.pub_time || a.createtime) }}</span>
                  <span>{{ readMinutes(a) }} {{ t('blog.home.min') }}</span>
                  <span>{{ a.reads }} {{ t('blog.home.views') }}</span>
                </div>
              </div>
              <div class="bh-side-thumb">
                <img v-if="a.cover" :src="a.cover" :alt="a.title" />
              </div>
            </article>
          </aside>
        </section>

        <!-- ③ 资料区：logo / 名称+文章数+简介 / 社媒（浅色背景卡片） -->
        <section class="bh-profile">
          <div class="bh-profile-inner">
            <div class="bh-profile-logo">
              <!-- 方形圆角：blog favicon → 用户头像 → blog 名首字母 -->
              <img v-if="site.blog.favicon" :src="site.blog.favicon" alt="logo" class="is-squared" />
              <img v-else-if="site.user?.profile_image" :src="site.user.profile_image" :alt="blogTitle" class="is-squared" />
              <span v-else class="bh-profile-letter">{{ blogTitle.charAt(0) }}</span>
            </div>
            <div class="bh-profile-info">
              <h2 class="bh-profile-name">
                {{ blogTitle }}
                <span class="bh-profile-count">{{ total }} 篇文章</span>
              </h2>
              <p class="bh-profile-desc">{{ site.blog.blog_description || '还没有写简介' }}</p>
            </div>
            <div class="bh-profile-social" v-if="socialLinks.length > 0">
              <component
                :is="isUrl(social.url) ? 'a' : 'span'"
                v-for="(social, i) in socialLinks"
                :key="i"
                :href="isUrl(social.url) ? social.url : undefined"
                :target="isUrl(social.url) ? '_blank' : undefined"
                :rel="isUrl(social.url) ? 'noopener noreferrer' : undefined"
                class="bh-social-item"
                :title="socialLabel(social.platform) + (isUrl(social.url) ? '' : '：' + social.url)"
              >
                <IconifyIcon :icon="socialIcon(social.platform)" width="18" height="18" />
              </component>
            </div>
          </div>
        </section>

        <!-- ④ 列表区：3 列 grid card + 加载更多 -->
        <section class="bh-list">
          <article v-for="a in listArticles" :key="a.id" class="bh-card" @click="goArticle(a)">
            <div class="bh-card-cover">
              <img v-if="a.cover" :src="a.cover" :alt="a.title" loading="lazy" />
              <div v-else class="bh-card-cover bh-card-cover-empty">
                <el-icon :size="28"><Picture /></el-icon>
              </div>
            </div>
            <h3 class="bh-card-title">{{ a.title }}</h3>
            <p class="bh-card-desc">{{ articleSummary(a) }}</p>
            <div class="bh-meta bh-card-meta">
              <span>{{ formatDate(a.pub_time || a.createtime) }}</span>
              <span>{{ readMinutes(a) }} {{ t('blog.home.min_read') }}</span>
              <span>{{ a.reads }} {{ t('blog.home.views') }}</span>
            </div>
          </article>

          <div v-if="articles.length === 0" class="bh-empty">
            <p>这里还没有已发布的文章</p>
          </div>

          <div v-if="hasMore" class="bh-more">
            <el-button :loading="loadingMore" round @click="loadMore">加载更多</el-button>
          </div>
        </section>
        </template>

        <!-- ============ stacked 布局：信息区置顶 + 通栏焦点区 + 单行列表 ============ -->
        <template v-else-if="layout === 'stacked'">
          <!-- 信息区：favicon 独占顶部一行，下方 name+简介（左）与社媒+文章数（右）同一行 -->
          <section class="bh-profile profile-top">
            <div class="pt-logo">
              <img v-if="site.blog.favicon" :src="site.blog.favicon" alt="logo" />
              <img v-else-if="site.user?.profile_image" :src="site.user.profile_image" :alt="blogTitle" />
              <span v-else class="pt-letter">{{ blogTitle.charAt(0) }}</span>
            </div>
            <div class="pt-body">
              <div class="pt-left">
                <h2 class="pt-name">{{ blogTitle }}</h2>
                <p class="pt-desc">{{ site.blog.blog_description || '还没有写简介' }}</p>
              </div>
              <div class="pt-right">
                <div class="pt-social" v-if="socialLinks.length > 0">
                  <component
                    :is="isUrl(social.url) ? 'a' : 'span'"
                    v-for="(social, i) in socialLinks"
                    :key="i"
                    :href="isUrl(social.url) ? social.url : undefined"
                    :target="isUrl(social.url) ? '_blank' : undefined"
                    :rel="isUrl(social.url) ? 'noopener noreferrer' : undefined"
                    class="bh-social-item"
                    :title="socialLabel(social.platform) + (isUrl(social.url) ? '' : '：' + social.url)"
                  >
                    <IconifyIcon :icon="socialIcon(social.platform)" width="18" height="18" />
                  </component>
                </div>
                <span class="pt-count">{{ total }} {{ t('blog.home.posts') }}</span>
              </div>
            </div>
          </section>

          <!-- 焦点区：通栏左图右文 -->
          <article
            v-if="heroArticle && !activeFilter"
            class="st-hero"
            @click="goArticle(heroArticle)"
          >
            <div class="st-hero-cover">
              <img v-if="heroArticle.cover" :src="heroArticle.cover" :alt="heroArticle.title" />
              <div v-else class="st-hero-cover-empty"><el-icon :size="48"><Picture /></el-icon></div>
            </div>
            <div class="st-hero-body">
              <h2 class="st-hero-title">{{ heroArticle.title }}</h2>
              <p class="st-hero-summary">{{ articleSummary(heroArticle) }}</p>
              <div class="bh-meta st-hero-meta">
                <span>{{ formatDate(heroArticle.pub_time || heroArticle.createtime) }}</span>
                <span>{{ readMinutes(heroArticle) }} {{ t('blog.home.min_read') }}</span>
                <span>{{ heroArticle.reads }} {{ t('blog.home.views') }}</span>
              </div>
            </div>
          </article>

          <!-- 列表区：每行 日期 | 标题+摘要+阅读时长 | 缩略图 -->
          <section class="st-list">
            <article v-for="a in listArticles" :key="a.id" class="st-row" @click="goArticle(a)">
              <div class="st-row-date">{{ formatDate(a.pub_time || a.createtime) }}</div>
              <div class="st-row-main">
                <h3 class="st-row-title">{{ a.title }}</h3>
                <p class="st-row-desc">{{ articleSummary(a) }}</p>
                <div class="bh-meta st-row-meta">
                  <span>{{ readMinutes(a) }} {{ t('blog.home.min_read') }}</span>
                  <span>{{ a.reads }} {{ t('blog.home.views') }}</span>
                </div>
              </div>
              <div class="st-row-thumb">
                <img v-if="a.cover" :src="a.cover" :alt="a.title" loading="lazy" />
              </div>
            </article>

            <div v-if="articles.length === 0" class="bh-empty">
              <p>这里还没有已发布的文章</p>
            </div>

            <div v-if="hasMore" class="bh-more">
              <el-button :loading="loadingMore" round @click="loadMore">显示更多</el-button>
            </div>
          </section>
        </template>

        <!-- ============ grid 布局：信息区置顶 + 焦点区与列表合并为卡片网格 ============ -->
        <template v-else>
          <!-- 信息区：与 stacked 一致 -->
          <section class="bh-profile profile-top">
            <div class="pt-logo">
              <img v-if="site.blog.favicon" :src="site.blog.favicon" alt="logo" />
              <img v-else-if="site.user?.profile_image" :src="site.user.profile_image" :alt="blogTitle" />
              <span v-else class="pt-letter">{{ blogTitle.charAt(0) }}</span>
            </div>
            <div class="pt-body">
              <div class="pt-left">
                <h2 class="pt-name">{{ blogTitle }}</h2>
                <p class="pt-desc">{{ site.blog.blog_description || '还没有写简介' }}</p>
              </div>
              <div class="pt-right">
                <div class="pt-social" v-if="socialLinks.length > 0">
                  <component
                    :is="isUrl(social.url) ? 'a' : 'span'"
                    v-for="(social, i) in socialLinks"
                    :key="i"
                    :href="isUrl(social.url) ? social.url : undefined"
                    :target="isUrl(social.url) ? '_blank' : undefined"
                    :rel="isUrl(social.url) ? 'noopener noreferrer' : undefined"
                    class="bh-social-item"
                    :title="socialLabel(social.platform) + (isUrl(social.url) ? '' : '：' + social.url)"
                  >
                    <IconifyIcon :icon="socialIcon(social.platform)" width="18" height="18" />
                  </component>
                </div>
                <span class="pt-count">{{ total }} {{ t('blog.home.posts') }}</span>
              </div>
            </div>
          </section>

          <!-- 卡片网格：按默认排序（置顶优先），无独立焦点区 -->
          <section class="gd-grid">
            <article v-for="a in listArticles" :key="a.id" class="gd-card" @click="goArticle(a)">
              <div class="gd-cover">
                <img v-if="a.cover" :src="a.cover" :alt="a.title" loading="lazy" />
                <div v-else class="gd-cover-empty"><el-icon :size="40"><Picture /></el-icon></div>
              </div>
              <div class="bh-meta gd-meta">
                <span>{{ formatDate(a.pub_time || a.createtime) }}</span>
                <span>{{ readMinutes(a) }} {{ t('blog.home.min_read') }}</span>
                <span>{{ a.reads }} {{ t('blog.home.views') }}</span>
              </div>
              <h3 class="gd-title">{{ a.title }}</h3>
              <p class="gd-desc">{{ articleSummary(a) }}</p>
            </article>

            <div v-if="articles.length === 0" class="bh-empty">
              <p>这里还没有已发布的文章</p>
            </div>

            <div v-if="hasMore" class="bh-more">
              <el-button :loading="loadingMore" round @click="loadMore">显示更多</el-button>
            </div>
          </section>
        </template>
      </main>

      <!-- ⑤ footer：法律声明块在上（左对齐灰色小字），版权/链接/Powered 行在下 -->
      <BlogFooter
        :impressum="site.blog.impressum"
        :createtime="site.blog.createtime"
        :blog-title="blogTitle"
        :site-favicon="appStore.site_favicon || '/favicon.ico'"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAppStore } from '@/stores/app'
import { getBlogSite, getBlogArticles } from '@/api/services/creator'
import IconifyIcon from '@/components/IconIfy.vue'
import BlogTopbar from '@/components/blog/BlogTopbar.vue'
import BlogFooter from '@/components/blog/BlogFooter.vue'
import { Search, Sunny, Moon, EditPen, Close, Picture, ArrowDown, Menu } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const appStore = useAppStore()

interface BlogArticleItem {
  id: number
  title: string
  slug: string
  subtitle: string | null
  cover: string | null
  pub_time: number | null
  createtime: number | null
  content_len: number
  content_preview?: string
  reads?: number
}

const loading = ref(false)
const loadingMore = ref(false)
// 全屏搜索弹层（交互与站点首页一致：回车/按钮 → /search?q=）
const searchVisible = ref(false)
const searchKeyword = ref('')
const site = ref<any>({ blog: null, navs: [], categories: [], series: [], user: {} })
const articles = ref<BlogArticleItem[]>([])
const total = ref(0)

// 首页布局：magazine（默认）/ stacked / grid，由外观设置页下发
type BlogLayout = 'magazine' | 'stacked' | 'grid'
const layout = computed<BlogLayout>(() => {
  const v = site.value.blog?.homepage_layout
  return v === 'stacked' || v === 'grid' ? v : 'magazine'
})

// 分页参数按布局区分：
// - magazine：焦点区占 5 条（hero 1 + 副列 4），列表区每页 6 条
// - stacked：焦点区通栏 1 条，列表区每页 10 条
// - grid：无独立焦点区（焦点区与列表合并），列表区每页 10 条
const pageSize = computed(() => (layout.value === 'magazine' ? 6 : 10))
const HERO_COUNT = computed(() => (layout.value === 'magazine' ? 5 : layout.value === 'stacked' ? 1 : 0))

// 聚合过滤（?cat=slug / ?series=id）
const activeCatSlug = ref<string | null>(null)
const activeSeriesId = ref<number | null>(null)

const isAuthenticated = computed(() => !!appStore.token && !!appStore.userRole)
const blogTitle = computed(() => site.value.blog?.blog_name || site.value.user?.full_name || String(route.params.username))
const socialLinks = computed(() => {
  const links = site.value.blog?.social_links
  return Array.isArray(links) ? links.filter((l: any) => l?.platform && l?.url) : []
})
const heroArticle = computed(() => (articles.value.length > 0 ? articles.value[0] : null))
const sideArticles = computed(() => articles.value.slice(1, 5))
// magazine 焦点区消费前 HERO_COUNT 条；stacked 焦点区消费第 1 条；
// grid 无独立焦点区（全部进列表）；聚合视图一律无焦点区。焦点区与列表不重不漏。
const listArticles = computed(() =>
  activeFilter.value || HERO_COUNT.value === 0 ? articles.value : articles.value.slice(HERO_COUNT.value)
)
const hasMore = computed(() => articles.value.length < total.value)
const activeFilter = computed(() => activeCatSlug.value || activeSeriesId.value)
const activeFilterLabel = computed(() => {
  if (activeCatSlug.value) {
    const c = site.value.categories?.find((x: any) => x.slug === activeCatSlug.value)
    return c?.name || activeCatSlug.value
  }
  if (activeSeriesId.value) {
    const s = site.value.series?.find((x: any) => x.id === activeSeriesId.value)
    return s?.name || ''
  }
  return ''
})

const currentCatId = computed(() => {
  if (!activeCatSlug.value) return undefined
  return site.value.categories?.find((c: any) => c.slug === activeCatSlug.value)?.id
})

const loadArticles = async (offset = 0) => {
  const username = String(route.params.username)
  // 首屏无聚合过滤：一次请求多取焦点区占用的 HERO_COUNT 条，articles 从 offset=0
  // 连续存储，前 HERO_COUNT 条由焦点区消费，其余进列表区；聚合视图无焦点区，按 pageSize 取。
  const firstPage = offset === 0 && !activeFilter.value
  const res = await getBlogArticles(username, {
    limit: firstPage ? HERO_COUNT.value + pageSize.value : pageSize.value,
    offset,
    blogCat: currentCatId.value,
    blogSeries: activeSeriesId.value || undefined
  })
  if (res.code === 1 && res.data) {
    articles.value = res.data.list || []
    total.value = res.data.total || 0
  }
}

const loadMore = async () => {
  loadingMore.value = true
  try {
    // articles 现在从 offset=0 连续存储（含焦点区条目），下一页偏移即已加载条数
    const serverOffset = articles.value.length
    const username = String(route.params.username)
    const res = await getBlogArticles(username, {
      limit: pageSize.value,
      offset: serverOffset,
      blogCat: currentCatId.value,
      blogSeries: activeSeriesId.value || undefined
    })
    if (res.code === 1 && res.data) {
      articles.value = [...articles.value, ...(res.data.list || [])]
      total.value = res.data.total || 0
    }
  } finally {
    loadingMore.value = false
  }
}

const loadSite = async () => {
  loading.value = true
  try {
    const username = String(route.params.username)
    const siteRes = await getBlogSite(username)
    if (siteRes.code === 1 && siteRes.data) {
      site.value = siteRes.data
      document.title = `${site.value.blog?.blog_name || site.value.user?.full_name || username} - WOW Blog`
      // blog favicon 在浏览器标签页真实生效（复用全局动态 favicon link，离开本页恢复站点图标）
      applyBlogFavicon()
      if (site.value.blog?.opened) {
        await loadArticles(0)
      }
      // 站点数据（含导航）渲染后测量导航宽度，决定可见项与 More 收纳
      await nextTick()
      layoutNav()
    }
  } catch (error) {
    console.error('加载博客配置失败:', error)
  } finally {
    loading.value = false
  }
}

const FAVICON_LINK_ID = 'dynamic-favicon'

const applyBlogFavicon = () => {
  const link = document.getElementById(FAVICON_LINK_ID) as HTMLLinkElement | null
  if (link && site.value.blog?.favicon) {
    link.href = site.value.blog.favicon
  }
}

const restoreSiteFavicon = () => {
  const link = document.getElementById(FAVICON_LINK_ID) as HTMLLinkElement | null
  if (link) {
    link.href = appStore.site_favicon || '/favicon.ico'
  }
}

onBeforeUnmount(() => {
  restoreSiteFavicon()
  window.removeEventListener('resize', onViewportResize)
  navResizeObserver?.disconnect()
  navResizeObserver = null
})

// 导航点击：link 外链直跳；category/series 跳该博客的专属列表页（按 slug）
// （分类/系列导航的 value 存的是各自 id，需从 site 配置映射到 slug）
const resolveNavValue = (nav: any) => {
  if (nav.type === 'category') {
    const byId = site.value.categories?.find((c: any) => String(c.id) === nav.value)
    return byId?.slug || nav.value
  }
  return nav.value
}

const navToSlug = (nav: any) => {
  if (nav.type === 'category') {
    return site.value.categories?.find((c: any) => String(c.id) === nav.value)?.slug || nav.value
  }
  return site.value.series?.find((s: any) => String(s.id) === nav.value)?.slug || nav.value
}

const handleNavClick = (nav: any) => {
  if (!nav) return
  if (nav.type === 'link') {
    if (nav.value) window.open(nav.value, '_blank')
    return
  }
  const username = String(route.params.username)
  const slug = navToSlug(nav)
  if (nav.type === 'series') {
    router.push(`/blog/${username}/series/${slug}`)
  } else {
    router.push(`/blog/${username}/category/${slug}`)
  }
}

const isNavActive = (nav: any) => {
  if (nav.type === 'category') return activeCatSlug.value === resolveNavValue(nav)
  if (nav.type === 'series') return activeSeriesId.value === Number(nav.value)
  return false
}

const resetFilter = () => {
  activeCatSlug.value = null
  activeSeriesId.value = null
}

/* ---------- 导航溢出：JS 测量真实宽度，超出收进 More / 移动端目录 ---------- */
const navRef = ref<HTMLElement | null>(null)
const navMeasureRef = ref<HTMLElement | null>(null)
const navItemWidths = ref<number[]>([])   // 每个导航项的真实渲染宽度（中英文自适应）
const visibleNavCount = ref(999)          // 当前可见项数，测量后收敛
const NAV_GAP = 22                        // 与 CSS .bh-nav 的 gap 保持一致
const MORE_BTN_RESERVE = 74               // More 按钮预留宽度（含 gap）
const MOBILE_BREAKPOINT = 768             // 移动端断点，与 CSS 媒体查询一致
const isMobileViewport = ref(false)

const visibleNavs = computed(() => (site.value.navs || []).slice(0, visibleNavCount.value))
const hiddenNavs = computed(() => (site.value.navs || []).slice(visibleNavCount.value))

// 测量所有导航项的自然宽度（隐藏容器内 span 用与可见项相同的 .bh-nav-item 样式）
const measureNavWidths = () => {
  const measureEl = navMeasureRef.value
  if (!measureEl) return
  const spans = measureEl.querySelectorAll('.bh-nav-item')
  navItemWidths.value = Array.from(spans).map((el) => (el as HTMLElement).getBoundingClientRect().width)
}

// 依据可用宽度重新计算可见项数
const layoutNav = () => {
  const navs = site.value.navs || []
  if (navs.length === 0) {
    visibleNavCount.value = 0
    return
  }
  // 移动端：全部收进目录按钮
  if (isMobileViewport.value) {
    visibleNavCount.value = 0
    return
  }
  const container = navRef.value
  if (!container) return
  measureNavWidths()
  const widths = navItemWidths.value
  const available = container.clientWidth
  // 预留一个 More 按钮宽度：仅当存在放不下的项时才真正显示 More，
  // 这里先按"可能需要"预留，若全部放得下则最后不做截断
  let used = 0
  let count = 0
  for (let i = 0; i < navs.length; i++) {
    const itemWidth = widths[i] || 0
    const need = (i > 0 ? NAV_GAP : 0) + itemWidth
    // 若该项之后还有项，需为 More 按钮预留空间（保证 More 有位置显示）
    const reserveMore = i < navs.length - 1 ? MORE_BTN_RESERVE : 0
    if (used + need + reserveMore > available) break
    used += need
    count++
  }
  // 至少显示 1 项（避免极端窄屏下桌面端全空，移动端有目录按钮兜底）
  visibleNavCount.value = Math.max(1, count)
}

const onMoreNavCommand = (nav: any) => {
  if (nav) handleNavClick(nav)
}

let navResizeObserver: ResizeObserver | null = null
const onViewportResize = () => {
  isMobileViewport.value = window.innerWidth <= MOBILE_BREAKPOINT
  // 等 DOM 跟随响应式样式更新后再测量
  nextTick(layoutNav)
}

watch([activeCatSlug, activeSeriesId], () => loadArticles(0))

const goArticle = (a: BlogArticleItem) => {
  router.push(`/article/${a.slug}`)
}

const goWrite = () => {
  const url = appStore.userRole === 'Author' ? '/creator/articles/create' : '/my-articles/create'
  window.open(url, '_blank')
}

const openSearch = () => {
  searchVisible.value = true
  setTimeout(() => {
    const input = document.querySelector('.bh-search-input input') as HTMLInputElement | null
    input?.focus()
  }, 120)
}

const submitSearch = () => {
  const q = searchKeyword.value.trim()
  if (!q) return
  searchVisible.value = false
  router.push({ path: '/search', query: { q } })
}

// 摘要：优先副标题，否则剥 HTML 标签取正文预览（行数钳制交给 CSS line-clamp）
const articleSummary = (a: BlogArticleItem) => {
  if (a.subtitle) return a.subtitle
  const text = (a.content_preview || '')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
  return text
}

// 社媒值是否为可点击链接（wechat 等纯文本账号走 title 展示）
const isUrl = (value: string) => /^https?:\/\//i.test(value || '')

const socialLabel = (platform: string) => String(platform || '').toUpperCase()

const formatDate = (timestamp: number | null) => {
  if (!timestamp) return ''
  return new Date(timestamp * 1000).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

// 预估阅读时长：中文 ~400 字/分钟（content_len 为字符数）
const readMinutes = (a: BlogArticleItem) => Math.max(1, Math.ceil((a.content_len || 0) / 400))

const copyrightYears = computed(() => {
  const start = site.value.blog?.createtime
    ? new Date(site.value.blog.createtime * 1000).getFullYear()
    : new Date().getFullYear()
  const now = new Date().getFullYear()
  return start === now ? String(now) : `${start} - ${now}`
})

const socialIcon = (platform: string) => {
  // 与个人资料 social_profiles 的字段同源（13 个平台 key）
  const map: Record<string, string> = {
    github: 'mdi:github',
    twitter: 'mdi:twitter',
    x: 'mdi:twitter',
    linkedin: 'mdi:linkedin',
    instagram: 'mdi:instagram',
    dribbble: 'mdi:basketball',
    website: 'mdi:web',
    weibo: 'mdi:sina-weibo',
    wechat: 'mdi:wechat',
    zhihu: 'mdi:alpha-z-circle',
    bilibili: 'mdi:bilibili',
    douyin: 'mdi:music-note',
    xiaohongshu: 'mdi:book-open-variant',
    gitee: 'mdi:git',
    email: 'mdi:email-outline',
    rss: 'mdi:rss'
  }
  return map[(platform || '').toLowerCase()] || 'mdi:link-variant'
}

onMounted(() => {
  isMobileViewport.value = window.innerWidth <= MOBILE_BREAKPOINT
  window.addEventListener('resize', onViewportResize)
  // 监听导航容器宽度变化（如侧栏展开/字体缩放），自动重算收纳
  if (typeof ResizeObserver !== 'undefined') {
    navResizeObserver = new ResizeObserver(() => layoutNav())
  }
  loadSite().then(() => {
    nextTick(() => {
      if (navRef.value && navResizeObserver) navResizeObserver.observe(navRef.value)
    })
  })
})
watch(() => route.params.username, () => {
  if (route.name === 'blog-home') loadSite()
})
</script>

<style scoped>
.blog-home {
  min-height: 100vh;
  background: var(--el-bg-color);
  color: var(--el-text-color-primary);
}

.blog-not-opened {
  min-height: 60vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.blog-not-opened h2 {
  margin: 0;
}

.blog-not-opened p {
  color: var(--el-text-color-secondary);
  margin: 0 0 12px;
}

/* ① 顶栏 */
.bh-topbar {
  position: sticky;
  top: 0;
  z-index: 20;
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.bh-topbar-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  height: 60px;
  display: flex;
  align-items: center;
  gap: 24px;
}

.bh-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

/* 网站 favicon：正方形小图标，灰度呈现（不抢 blog logo），悬浮加深，点击回站首页 */
.bh-brand-site-logo {
  width: 22px;
  height: 22px;
  border-radius: 5px;
  object-fit: cover;
  cursor: pointer;
  filter: grayscale(100%);
  opacity: 0.55;
  transition: filter 0.2s, opacity 0.2s;
}

.bh-brand-site-logo:hover {
  filter: grayscale(100%) brightness(0.35);
  opacity: 1;
}

/* 双 logo 的浅色斜线分隔 */
.bh-brand-divider {
  width: 1px;
  height: 18px;
  background: var(--el-border-color);
  transform: rotate(20deg);
  flex-shrink: 0;
}

/* blog logo 与 blog 名称互斥展示（logo 优先）：高度 48px，宽度由 object-fit 等比例缩放 */
.bh-brand-blog-logo {
  height: 48px;
  max-width: 240px;
  object-fit: contain;
  cursor: pointer;
}

.bh-brand-name {
  font-size: 17px;
  font-weight: 700;
  cursor: pointer;
}

/* 导航居中：占据 brand 与 actions 之间的剩余空间，内容水平居中 */
.bh-nav {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 22px;
  overflow: hidden;
}

.bh-nav-item {
  font-size: 14px;
  color: var(--el-text-color-regular);
  text-decoration: none;
  white-space: nowrap;
  padding: 4px 0;
  border-bottom: 2px solid transparent;
  flex-shrink: 0;
}

.bh-nav-item:hover,
.bh-nav-item.active {
  color: var(--el-color-primary);
}

.bh-nav-item.active {
  border-bottom-color: var(--el-color-primary);
}

/* 桌面端 More 按钮（胶囊描边，参考截图） */
.bh-nav-more-wrap {
  flex-shrink: 0;
  margin-left: -6px;
}

.bh-nav-more-btn {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  height: 30px;
  padding: 0 12px;
  border: 1px solid var(--el-border-color);
  border-radius: 15px;
  background: var(--el-bg-color);
  color: var(--el-text-color-regular);
  font-size: 14px;
  cursor: pointer;
  white-space: nowrap;
  transition: border-color 0.2s, color 0.2s;
}

.bh-nav-more-btn:hover {
  border-color: var(--el-color-primary);
  color: var(--el-color-primary);
}

/* 下拉中的激活项 */
.bh-nav-more-wrap .el-dropdown-menu__item.is-active-nav,
.bh-nav-catalog-wrap .el-dropdown-menu__item.is-active-nav {
  color: var(--el-color-primary);
  font-weight: 600;
}

/* 移动端目录按钮：默认隐藏，≤768px 显示；同时隐藏可见项与 More */
.bh-nav-catalog-wrap {
  display: none;
  flex-shrink: 0;
}

.bh-nav-catalog-btn {
  width: 34px;
  height: 34px;
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  background: var(--el-bg-color);
  color: var(--el-text-color-regular);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

/* 隐藏测量容器：绝对定位移出视口，不参与布局，仅用于读取真实宽度 */
.bh-nav-measure {
  position: absolute;
  visibility: hidden;
  pointer-events: none;
  width: max-content;
  display: flex;
  gap: 22px;
  left: -99999px;
  top: 0;
}

.bh-topbar-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.bh-icon-btn {
  width: 34px;
  height: 34px;
  border: none;
  border-radius: 50%;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--el-text-color-regular);
}

.bh-icon-btn:hover {
  background: var(--el-fill-color-light);
}

/* 主区 */
.bh-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 28px 24px 64px;
}

.bh-filter-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
  font-size: 15px;
  font-weight: 600;
}

/* ② 焦点区 */
.bh-hero {
  display: flex;
  gap: 45px;
  margin-bottom: 48px;
}

.bh-hero-main {
  flex: 0 0 650px;
  max-width: 650px;
  cursor: pointer;
}

.bh-hero-cover {
  width: 100%;
  aspect-ratio: 800 / 420;
  border-radius: 12px;
  overflow: hidden;
  background: var(--el-fill-color-light);
}

.bh-hero-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

/* 元信息置于标题上方（小字，参考杂志版式） */
.bh-hero-meta {
  margin-top: 14px;
  font-size: 13px;
}

.bh-hero-title {
  margin: 8px 0 10px;
  font-size: 28px;
  font-weight: 700;
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.bh-hero-summary {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 15px;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.bh-hero-side {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}

.bh-hero-side-item {
  display: flex;
  gap: 16px;
  padding: 18px 0;
  border-bottom: 1px solid var(--el-border-color-lighter);
  cursor: pointer;
}

.bh-hero-side-item:first-child {
  padding-top: 0;
}

.bh-hero-side-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.bh-side-info {
  flex: 1;
  min-width: 0;
}

.bh-side-title {
  margin: 0 0 8px;
  font-size: 17px;
  font-weight: 600;
  line-height: 1.45;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 缩略图在标题右侧（文字左、图右，参考版式） */
.bh-side-thumb {
  order: 2;
  flex-shrink: 0;
  width: 130px;
  height: 85px;
  border-radius: 8px;
  overflow: hidden;
  background: var(--el-fill-color-light);
}

.bh-side-info {
  order: 1;
}

.bh-side-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.bh-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: var(--el-text-color-placeholder);
}

/* ③ 资料区（浅色背景卡片容器） */
.bh-profile {
  margin-bottom: 40px;
}

.bh-profile-inner {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 28px 32px;
  border-radius: 16px;
  background: var(--el-fill-color-light);
}

.bh-profile-logo {
  flex-shrink: 0;
  width: 72px;
  display: flex;
  justify-content: center;
}

/* 方形圆角：blog favicon / 用户头像 / 首字母占位统一形态 */
.bh-profile-logo img.is-squared {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  object-fit: cover;
}

/* 兜底首字母占位 */
.bh-profile-letter {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  font-weight: 600;
  color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

.bh-profile-info {
  flex: 1;
  min-width: 0;
}

.bh-profile-name {
  margin: 0 0 6px;
  font-size: 20px;
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.bh-profile-count {
  font-size: 13px;
  font-weight: 400;
  color: var(--el-text-color-secondary);
}

.bh-profile-desc {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.bh-profile-social {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
}

.bh-social-item {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--el-text-color-regular);
  background: var(--el-bg-color);
  cursor: pointer;
}

.bh-social-item:hover {
  color: var(--el-color-primary);
}

/* 搜索弹层 */
.bh-search-close {
  position: absolute;
  top: 24px;
  right: 24px;
}

.bh-search-wrap {
  width: min(640px, 90vw);
  margin: 0 auto;
}

.bh-search-input :deep(input) {
  font-size: 18px;
}

/* ④ 列表区 */
.bh-list {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 28px 24px;
}

.bh-card {
  cursor: pointer;
  border-radius: 10px;
  transition: transform 0.2s;
}

.bh-card:hover {
  transform: translateY(-3px);
}

.bh-card-cover {
  width: 100%;
  aspect-ratio: 16 / 10;
  border-radius: 10px;
  overflow: hidden;
  background: var(--el-fill-color-light);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--el-text-color-placeholder);
}

.bh-card-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.bh-card-title {
  margin: 12px 0 6px;
  font-size: 16px;
  line-height: 1.45;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.bh-card-desc {
  margin: 0 0 8px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.bh-card-meta {
  font-size: 12px;
}

.bh-empty {
  grid-column: 1 / -1;
  text-align: center;
  padding: 60px 0;
  color: var(--el-text-color-secondary);
}

.bh-more {
  grid-column: 1 / -1;
  text-align: center;
  margin-top: 12px;
}

/* ⑤ footer */
.bh-footer {
  border-top: 1px solid var(--el-border-color-lighter);
  background: var(--el-bg-color);
}

.bh-footer-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
  flex-wrap: wrap;
}

.bh-footer-links {
  display: flex;
  gap: 18px;
}

.bh-footer-links a {
  color: var(--el-text-color-secondary);
  text-decoration: none;
}

.bh-footer-links a:hover {
  color: var(--el-color-primary);
}

.bh-footer-powered {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}

.bh-footer-favicon {
  width: 16px;
  height: 16px;
  border-radius: 3px;
}

/* 法律声明块：置于底部导航行上方，左对齐灰色次级文字（参考版式） */
.bh-footer-impressum {
  max-width: 1200px;
  margin: 0 auto;
  padding: 28px 24px 0;
}

.bh-impressum-text {
  margin: 0 0 36px;
  font-family: inherit;
  font-size: 13px;
  line-height: 1.9;
  color: var(--el-text-color-secondary);
  white-space: pre-wrap;
  word-break: break-word;
}

/* ==================== stacked / grid 共用：置顶信息区 ==================== */
.bh-profile.profile-top {
  margin-bottom: 48px;
}

.profile-top {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0;
}

/* favicon 独占顶部一行 */
.pt-logo {
  width: 76px;
  height: 76px;
  margin-bottom: 22px;
}

/* name+简介（左）与社媒+文章数（右）同一水平行 */
.pt-body {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 32px;
  width: 100%;
}

.pt-left {
  min-width: 0;
}

.pt-logo img,
.pt-letter {
  width: 76px;
  height: 76px;
  border-radius: 16px;
  object-fit: cover;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pt-letter {
  font-size: 34px;
  font-weight: 600;
  color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

.pt-name {
  margin: 0 0 12px;
  font-size: 44px;
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: -0.5px;
}

.pt-desc {
  margin: 0;
  max-width: 640px;
  color: var(--el-text-color-secondary);
  font-size: 15px;
  line-height: 1.75;
  white-space: pre-line;
}

.pt-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 14px;
  flex-shrink: 0;
  padding-top: 4px;
}

.pt-social {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.pt-social .bh-social-item {
  width: 34px;
  height: 34px;
  border: 1px solid var(--el-border-color-lighter);
}

.pt-count {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

/* ==================== stacked 布局 ==================== */
.st-hero {
  display: flex;
  align-items: stretch;
  gap: 36px;
  margin-bottom: 44px;
  padding: 12px 12px 12px 0;
  border-bottom: 1px solid var(--el-border-color-lighter);
  padding-bottom: 44px;
  cursor: pointer;
}

.st-hero-cover {
  flex: 0 0 52%;
  aspect-ratio: 16 / 10;
  border-radius: 12px;
  overflow: hidden;
  background: var(--el-fill-color-light);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--el-text-color-placeholder);
}

.st-hero-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.st-hero-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.st-hero-title {
  margin: 0 0 16px;
  font-size: 30px;
  font-weight: 700;
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.st-hero-summary {
  margin: 0 0 18px;
  color: var(--el-text-color-secondary);
  font-size: 15px;
  line-height: 1.7;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.st-hero-meta {
  font-size: 13px;
}

.st-list {
  display: flex;
  flex-direction: column;
}

.st-row {
  display: grid;
  grid-template-columns: 118px 1fr 150px;
  gap: 24px;
  align-items: start;
  padding: 24px 0;
  border-bottom: 1px solid var(--el-border-color-lighter);
  cursor: pointer;
}

.st-row:first-child {
  padding-top: 0;
}

.st-row-date {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  padding-top: 3px;
}

.st-row-main {
  min-width: 0;
}

.st-row-title {
  margin: 0 0 8px;
  font-size: 17px;
  font-weight: 600;
  line-height: 1.45;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.st-row-desc {
  margin: 0 0 10px;
  color: var(--el-text-color-secondary);
  font-size: 14px;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.st-row-meta {
  font-size: 12px;
}

.st-row-thumb {
  width: 150px;
  height: 96px;
  border-radius: 8px;
  overflow: hidden;
  background: var(--el-fill-color-light);
}

.st-row-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.st-list .bh-more {
  margin-top: 28px;
}

/* ==================== grid 布局 ==================== */
.gd-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 44px 32px;
}

.gd-card {
  cursor: pointer;
}

.gd-cover {
  width: 100%;
  aspect-ratio: 16 / 9;
  border-radius: 12px;
  overflow: hidden;
  background: var(--el-fill-color-light);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--el-text-color-placeholder);
  margin-bottom: 18px;
}

.gd-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.gd-meta {
  font-size: 13px;
  margin-bottom: 10px;
}

.gd-title {
  margin: 0 0 10px;
  font-size: 22px;
  font-weight: 700;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.gd-desc {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 14px;
  line-height: 1.65;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 响应式 */
@media (max-width: 1024px) {
  .bh-hero {
    flex-direction: column;
    gap: 20px;
  }

  .bh-hero-main {
    flex: none;
    max-width: 100%;
  }

  .bh-list {
    grid-template-columns: repeat(2, 1fr);
  }

  /* stacked / grid 响应式 */
  .st-hero {
    flex-direction: column;
    gap: 24px;
  }

  .st-hero-cover {
    flex: none;
    width: 100%;
  }

  .gd-grid {
    gap: 32px 20px;
  }

  .st-row {
    grid-template-columns: 100px 1fr 110px;
    gap: 16px;
  }

  .st-row-thumb {
    width: 110px;
    height: 74px;
  }
}

/* 导航溢出：≤768px 只显示目录按钮，可见项与 More 全部收起 */
@media (max-width: 768px) {
  .bh-nav > .bh-nav-item,
  .bh-nav-more-wrap {
    display: none;
  }

  .bh-nav-catalog-wrap {
    display: inline-flex;
  }
}

@media (max-width: 640px) {
  .bh-topbar-inner {
    padding: 0 16px;
    gap: 12px;
  }

  .bh-brand-name {
    display: none;
  }

  .bh-main {
    padding: 20px 16px 48px;
  }

  .bh-list {
    grid-template-columns: 1fr;
  }

  .bh-profile-inner {
    flex-direction: column;
    text-align: center;
    padding: 20px 16px;
  }

  .bh-side-thumb {
    width: 96px;
    height: 64px;
  }

  .bh-profile-name {
    justify-content: center;
  }

  .bh-footer-inner {
    flex-direction: column;
  }

  /* stacked / grid 移动端 */
  .pt-body {
    flex-direction: column;
    gap: 20px;
  }

  .pt-name {
    font-size: 34px;
  }

  .pt-logo,
  .pt-logo img,
  .pt-letter {
    width: 64px;
    height: 64px;
  }

  .pt-right {
    align-items: flex-start;
  }

  .pt-social {
    justify-content: flex-start;
  }

  .st-hero-title {
    font-size: 24px;
  }

  .st-row {
    grid-template-columns: 1fr 84px;
    gap: 8px 14px;
  }

  .st-row-date {
    grid-column: 1 / -1;
    padding-top: 0;
  }

  .st-row-thumb {
    width: 84px;
    height: 60px;
  }

  .gd-grid {
    grid-template-columns: 1fr;
  }

  .gd-title {
    font-size: 19px;
  }
}
</style>
