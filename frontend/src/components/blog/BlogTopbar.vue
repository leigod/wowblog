<template>
  <!-- 顶栏：网站 logo（灰度，回站首页）+ 斜线 + blog logo / blog 名称（互斥展示） -->
  <header class="bh-topbar">
    <div class="bh-topbar-inner">
      <div class="bh-brand">
        <img
          :src="siteFavicon || '/favicon.ico'"
          class="bh-brand-site-logo"
          alt="WOW Blog"
          title="WOW Blog"
          @click="$router.push('/')"
        />
        <span class="bh-brand-divider" aria-hidden="true"></span>
        <template v-if="blog?.logo">
          <img :src="blog.logo" class="bh-brand-blog-logo" :alt="blogTitle" @click="emit('brandClick')" />
        </template>
        <template v-else>
          <span class="bh-brand-name" @click="emit('brandClick')">{{ blogTitle }}</span>
        </template>
      </div>

      <!-- 导航：桌面端按可用宽度自动把溢出项收进 More；移动端收进目录按钮 -->
      <nav class="bh-nav" ref="navRef">
        <a
          v-for="nav in visibleNavs"
          :key="nav.id"
          class="bh-nav-item"
          :class="{ active: isNavActive(nav) }"
          href="javascript:;"
          @click="emit('navClick', nav)"
        >{{ nav.label }}</a>

        <el-dropdown
          v-if="hiddenNavs.length > 0"
          class="bh-nav-more-wrap"
          trigger="click"
          @command="onMoreNavCommand"
        >
          <button class="bh-nav-more-btn">
            More <el-icon :size="13"><ArrowDown /></el-icon>
          </button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item
                v-for="nav in hiddenNavs"
                :key="nav.id"
                :command="nav"
                :class="{ 'is-active-nav': isNavActive(nav) }"
              >{{ nav.label }}</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <el-dropdown class="bh-nav-catalog-wrap" trigger="click" @command="onMoreNavCommand">
          <button class="bh-nav-catalog-btn" :aria-label="$t('blog.home.nav_catalog')">
            <el-icon :size="20"><Menu /></el-icon>
          </button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item
                v-for="nav in navs"
                :key="nav.id"
                :command="nav"
                :class="{ 'is-active-nav': isNavActive(nav) }"
              >{{ nav.label }}</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </nav>

      <div class="bh-nav-measure" ref="navMeasureRef" aria-hidden="true">
        <span v-for="nav in navs" :key="nav.id" class="bh-nav-item">{{ nav.label }}</span>
      </div>

      <div class="bh-topbar-actions">
        <el-tooltip :content="$t('navbar.action.search')" placement="bottom">
          <button class="bh-icon-btn" @click="openSearch">
            <el-icon :size="18"><Search /></el-icon>
          </button>
        </el-tooltip>
        <el-tooltip :content="isDark ? $t('navbar.action.light') : $t('navbar.action.dark')" placement="bottom">
          <button class="bh-icon-btn" @click="emit('toggleDark')">
            <el-icon :size="18"><Sunny v-if="isDark" /><Moon v-else /></el-icon>
          </button>
        </el-tooltip>
        <el-button v-if="isAuthenticated" type="primary" round size="small" class="bh-write-btn" @click="emit('goWrite')">
          <el-icon style="margin-right: 4px"><EditPen /></el-icon>
          {{ $t('navbar.usercenter.write') }}
        </el-button>
      </div>
    </div>
  </header>

  <!-- 全屏搜索弹层 -->
  <el-dialog v-model="searchVisible" fullscreen center :show-close="false" class="bh-search-dialog">
    <el-button class="bh-search-close" :icon="Close" circle @click="searchVisible = false" />
    <div class="bh-search-wrap">
      <el-input
        v-model="searchKeyword"
        class="bh-search-input"
        :placeholder="$t('navbar.search.input.placeholder')"
        clearable
        size="large"
        @keyup.enter="submitSearch"
      />
    </div>
    <template #footer>
      <el-button type="primary" :icon="Search" size="large" round @click="submitSearch">
        {{ $t('navbar.search.btn.text') }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { Search, Sunny, Moon, EditPen, Close, ArrowDown, Menu } from '@element-plus/icons-vue'

interface Props {
  blog: any
  navs: any[]
  categories: any[]
  blogTitle: string
  siteFavicon: string
  isDark: boolean
  isAuthenticated: boolean
  activeCatSlug?: string | null
  activeSeriesId?: number | null
}
const props = withDefaults(defineProps<Props>(), {
  activeCatSlug: null,
  activeSeriesId: null
})
const emit = defineEmits<{
  navClick: [nav: any]
  brandClick: []
  toggleDark: []
  goWrite: []
  search: [keyword: string]
}>()

const resolveNavValue = (nav: any) => {
  if (nav.type === 'category') {
    const byId = props.categories?.find((c: any) => String(c.id) === nav.value)
    return byId?.slug || nav.value
  }
  return nav.value
}
const isNavActive = (nav: any) => {
  if (nav.type === 'category') return props.activeCatSlug === resolveNavValue(nav)
  if (nav.type === 'series') return props.activeSeriesId === Number(nav.value)
  return false
}
const onMoreNavCommand = (nav: any) => { if (nav) emit('navClick', nav) }

/* ---------- 导航溢出：JS 测量真实宽度，超出收进 More / 移动端目录 ---------- */
const navRef = ref<HTMLElement | null>(null)
const navMeasureRef = ref<HTMLElement | null>(null)
const navItemWidths = ref<number[]>([])
const visibleNavCount = ref(999)
const NAV_GAP = 22
const MORE_BTN_RESERVE = 74
const MOBILE_BREAKPOINT = 768
const isMobileViewport = ref(false)

const visibleNavs = computed(() => (props.navs || []).slice(0, visibleNavCount.value))
const hiddenNavs = computed(() => (props.navs || []).slice(visibleNavCount.value))

const measureNavWidths = () => {
  const measureEl = navMeasureRef.value
  if (!measureEl) return
  const spans = measureEl.querySelectorAll('.bh-nav-item')
  navItemWidths.value = Array.from(spans).map((el) => (el as HTMLElement).getBoundingClientRect().width)
}

const layoutNav = () => {
  const navs = props.navs || []
  if (navs.length === 0) { visibleNavCount.value = 0; return }
  if (isMobileViewport.value) { visibleNavCount.value = 0; return }
  const container = navRef.value
  if (!container) return
  measureNavWidths()
  const widths = navItemWidths.value
  const available = container.clientWidth
  let used = 0
  let count = 0
  for (let i = 0; i < navs.length; i++) {
    const itemWidth = widths[i] || 0
    const need = (i > 0 ? NAV_GAP : 0) + itemWidth
    const reserveMore = i < navs.length - 1 ? MORE_BTN_RESERVE : 0
    if (used + need + reserveMore > available) break
    used += need
    count++
  }
  visibleNavCount.value = Math.max(1, count)
}

let navResizeObserver: ResizeObserver | null = null
const onViewportResize = () => {
  isMobileViewport.value = window.innerWidth <= MOBILE_BREAKPOINT
  nextTick(layoutNav)
}
watch(() => props.navs, () => nextTick(layoutNav))

/* ---------- 搜索弹层 ---------- */
const searchVisible = ref(false)
const searchKeyword = ref('')
const openSearch = () => {
  searchVisible.value = true
  setTimeout(() => {
    const input = document.querySelector('.bh-search-dialog .bh-search-input input') as HTMLInputElement | null
    input?.focus()
  }, 120)
}
const submitSearch = () => {
  const q = searchKeyword.value.trim()
  if (!q) return
  searchVisible.value = false
  emit('search', q)
}

onMounted(() => {
  isMobileViewport.value = window.innerWidth <= MOBILE_BREAKPOINT
  window.addEventListener('resize', onViewportResize)
  if (typeof ResizeObserver !== 'undefined') {
    navResizeObserver = new ResizeObserver(() => layoutNav())
  }
  nextTick(() => {
    if (navRef.value && navResizeObserver) navResizeObserver.observe(navRef.value)
  })
})
onBeforeUnmount(() => {
  window.removeEventListener('resize', onViewportResize)
  navResizeObserver?.disconnect()
  navResizeObserver = null
})
</script>

<style scoped>
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
.bh-brand { display: flex; align-items: center; gap: 12px; flex-shrink: 0; }
.bh-brand-site-logo {
  width: 22px; height: 22px; border-radius: 5px; object-fit: cover; cursor: pointer;
  filter: grayscale(100%); opacity: 0.55; transition: filter 0.2s, opacity 0.2s;
}
.bh-brand-site-logo:hover { filter: grayscale(100%) brightness(0.35); opacity: 1; }
.bh-brand-divider {
  width: 1px; height: 18px; background: var(--el-border-color);
  transform: rotate(20deg); flex-shrink: 0;
}
.bh-brand-blog-logo { height: 48px; max-width: 240px; object-fit: contain; cursor: pointer; }
.bh-brand-name { font-size: 17px; font-weight: 700; cursor: pointer; }
.bh-nav {
  flex: 1; min-width: 0; display: flex; align-items: center; justify-content: center;
  gap: 22px; overflow: hidden;
}
.bh-nav-item {
  font-size: 14px; color: var(--el-text-color-regular); text-decoration: none;
  white-space: nowrap; padding: 4px 0; border-bottom: 2px solid transparent; flex-shrink: 0;
}
.bh-nav-item:hover, .bh-nav-item.active { color: var(--el-color-primary); }
.bh-nav-item.active { border-bottom-color: var(--el-color-primary); }
.bh-nav-more-wrap { flex-shrink: 0; margin-left: -6px; }
.bh-nav-more-btn {
  display: inline-flex; align-items: center; gap: 3px; height: 30px; padding: 0 12px;
  border: 1px solid var(--el-border-color); border-radius: 15px;
  background: var(--el-bg-color); color: var(--el-text-color-regular);
  font-size: 14px; cursor: pointer; white-space: nowrap;
  transition: border-color 0.2s, color 0.2s;
}
.bh-nav-more-btn:hover { border-color: var(--el-color-primary); color: var(--el-color-primary); }
.bh-nav-more-wrap .el-dropdown-menu__item.is-active-nav,
.bh-nav-catalog-wrap .el-dropdown-menu__item.is-active-nav { color: var(--el-color-primary); font-weight: 600; }
.bh-nav-catalog-wrap { display: none; flex-shrink: 0; }
.bh-nav-catalog-btn {
  width: 34px; height: 34px; border: 1px solid var(--el-border-color); border-radius: 8px;
  background: var(--el-bg-color); color: var(--el-text-color-regular); cursor: pointer;
  display: inline-flex; align-items: center; justify-content: center;
}
.bh-nav-measure {
  position: absolute; visibility: hidden; pointer-events: none; width: max-content;
  display: flex; gap: 22px; left: -99999px; top: 0;
}
.bh-topbar-actions { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
.bh-icon-btn {
  width: 34px; height: 34px; border: none; border-radius: 50%; background: transparent;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  color: var(--el-text-color-regular);
}
.bh-icon-btn:hover { background: var(--el-fill-color-light); }
@media (max-width: 768px) {
  .bh-nav > .bh-nav-item, .bh-nav-more-wrap { display: none; }
  .bh-nav-catalog-wrap { display: inline-flex; }
}
@media (max-width: 640px) {
  .bh-topbar-inner { padding: 0 16px; gap: 12px; }
  .bh-brand-name { display: none; }
}
</style>
