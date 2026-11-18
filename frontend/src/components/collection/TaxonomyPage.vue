<template>
  <div class="taxonomy-page" :class="{ 'is-wide': wide }">
    <!-- 面包屑：让「分类 › 技术 › PHP」的层级可见，也给出回索引页的入口 -->
    <nav v-if="crumbs.length" class="tax-crumbs" aria-label="breadcrumb">
      <template v-for="(crumb, i) in crumbs" :key="crumb.label">
        <span v-if="i" class="sep">/</span>
        <router-link v-if="crumb.to" :to="crumb.to" class="crumb">{{ crumb.label }}</router-link>
        <span v-else class="crumb is-current">{{ crumb.label }}</span>
      </template>
    </nav>

    <header class="tax-hero">
      <div class="hero-cover" :class="{ 'has-image': !!cover }">
        <img v-if="cover" :src="cover" :alt="title" />
        <span v-else class="hero-letter">{{ (title || '?').trim().slice(0, 1).toUpperCase() }}</span>
      </div>

      <div class="hero-text">
        <p class="hero-kicker">{{ kicker }}</p>
        <h1 class="hero-title">{{ title }}</h1>
        <p v-if="desc" class="hero-desc">{{ desc }}</p>

        <!-- 自己没直收文章但有子分类时，不报「共 0 篇」：交给下面的子分类入口和空态文案说明 -->
        <div v-if="total > 0 || !children.length" class="hero-meta">
          <span>{{ t('taxonomy.articles_count', { count: total }) }}</span>
          <template v-if="updatedText">
            <span class="dot">·</span>
            <span>{{ t('doc.updated') }} {{ updatedText }}</span>
          </template>
        </div>

        <div v-if="startTo" class="hero-actions">
          <router-link :to="startTo" class="hero-cta">
            {{ ctaText }}
            <el-icon><ArrowRight /></el-icon>
          </router-link>
        </div>
      </div>
    </header>

    <div v-if="children.length" class="tax-children">
      <span class="tax-children-title">{{ t('taxonomy.children_title') }}</span>
      <router-link v-for="child in children" :key="child.to" :to="child.to" class="tax-child">
        {{ child.label }}
      </router-link>
    </div>

    <div v-if="articles.length || loading" class="tax-list-head">
      <h2 class="tax-list-title">{{ listTitle }}</h2>
      <span class="tax-list-count">{{ articles.length }} / {{ total }}</span>
    </div>

    <p v-if="loading && !articles.length" class="tax-state">{{ t('taxonomy.loading') }}</p>

    <!-- 行式：系列页用，线性阅读强调顺序 -->
    <div v-else-if="layout === 'row' && articles.length" class="tax-list">
      <router-link
        v-for="(item, index) in articles"
        :key="item.id"
        :to="`/article/${item.slug}`"
        class="tax-row"
      >
        <span v-if="numbered" class="row-index">{{ pad(index + 1) }}</span>

        <div class="row-main">
          <h3 class="row-title" :title="item.title">{{ item.title }}</h3>
          <p class="row-summary">{{ plainText(item.content) }}</p>
          <div class="row-meta">
            <span v-if="item.author_username">@{{ item.author_username }}</span>
            <span v-if="item.createtime" class="dot">·</span>
            <span v-if="item.createtime">{{ formatDate(item.createtime) }}</span>
            <span class="dot">·</span>
            <span>{{ item.views || 0 }} {{ t('home.list.reads') }}</span>
          </div>
        </div>

        <div v-if="item.cover" class="row-cover">
          <img :src="item.cover" :alt="item.title" loading="lazy" />
        </div>
      </router-link>
    </div>

    <!-- 纵向卡网格：分类页用，橱窗式浏览（封面 16:10 + 标题 + 摘要 + 元信息） -->
    <div v-else-if="articles.length" class="tax-grid">
      <router-link
        v-for="item in articles"
        :key="item.id"
        :to="`/article/${item.slug}`"
        class="grid-card"
      >
        <div class="grid-cover">
          <img v-if="item.cover" :src="item.cover" :alt="item.title" loading="lazy" />
          <div v-else class="grid-placeholder">
            <span class="grid-mark" aria-hidden="true">{{
              (item.title || '?').trim().charAt(0)
            }}</span>
          </div>
        </div>
        <h3 class="grid-title" :title="item.title">{{ item.title }}</h3>
        <p class="grid-summary">{{ plainText(item.content) }}</p>
        <div class="grid-meta">
          <span v-if="item.author_username">@{{ item.author_username }}</span>
          <span v-if="item.createtime" class="dot">·</span>
          <span v-if="item.createtime">{{ formatDate(item.createtime) }}</span>
          <span class="dot">·</span>
          <span>{{ item.views || 0 }} {{ t('home.list.reads') }}</span>
        </div>
      </router-link>
    </div>

    <p v-else class="tax-state">
      {{ children.length ? t('taxonomy.empty_with_children') : t('taxonomy.empty') }}
    </p>

    <div v-if="articles.length" class="tax-foot">
      <el-button v-if="hasMore" text :loading="loading" @click="emit('load-more')">
        {{ t('taxonomy.load_more') }}
      </el-button>
      <span v-else class="tax-foot-end">{{ t('taxonomy.no_more') }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { ArrowRight } from '@element-plus/icons-vue'
import type { TaxonomyChild, TaxonomyCrumb, TaxonomyArticle } from './types'

const props = withDefaults(
  defineProps<{
    kicker: string
    title: string
    desc?: string
    cover?: string
    total?: number
    crumbs?: TaxonomyCrumb[]
    /** 子分类入口：父分类自己没有直收文章时，给用户下一跳 */
    children?: TaxonomyChild[]
    articles: TaxonomyArticle[]
    loading?: boolean
    hasMore?: boolean
    /** 系列天然有序，给每行加序号 */
    numbered?: boolean
    /** 列表版式：row=行式（系列默认），grid=纵向卡网格（分类页橱窗式） */
    layout?: 'row' | 'grid'
    /** 网格版式需要更宽的容器（1200px），行式保持 880px 窄栏利于阅读 */
    wide?: boolean
    listTitle?: string
    ctaText?: string
    startTo?: string
  }>(),
  {
    desc: '',
    cover: '',
    total: 0,
    crumbs: () => [],
    children: () => [],
    loading: false,
    hasMore: false,
    numbered: false,
    layout: 'row',
    wide: false,
    listTitle: '',
    ctaText: '',
    startTo: ''
  }
)

const emit = defineEmits<{ 'load-more': [] }>()

const { t } = useI18n()

const pad = (n: number) => String(n).padStart(2, '0')

const formatDate = (value: number | string) => {
  const ts = typeof value === 'number' ? value : Number(value)
  if (!Number.isFinite(ts) || ts <= 0) return ''
  // 秒级时间戳统一按秒处理（接口返回的是秒）
  const d = new Date(ts * 1000)
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

// content 是 HTML，列表里只要纯文本摘要
const plainText = (content?: string) => {
  const text = (content || '').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim()
  return text.length > 140 ? `${text.slice(0, 140)}…` : text
}

const updatedText = computed(() => {
  const latest = props.articles.reduce((max, item) => {
    const ts = Number(item.createtime || 0)
    return ts > max ? ts : max
  }, 0)
  return latest ? formatDate(latest) : ''
})
</script>

<style scoped>
.taxonomy-page {
  width: 100%;
  max-width: 880px;
  box-sizing: border-box;
  margin: 0 auto;
  padding: 28px 24px 88px;
}

/* 网格（橱窗）版式需要更宽的画布，每列约 370px 才放得下封面 */
.taxonomy-page.is-wide {
  max-width: 1200px;
}

/* ---------- 面包屑 ---------- */
.tax-crumbs {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  margin-bottom: 18px;
  font-size: 13px;
  line-height: 1.5;
}

.crumb {
  color: var(--wy-text-tertiary);
  text-decoration: none;
  transition: color var(--wy-duration) var(--wy-easing);
}

a.crumb:hover {
  color: var(--wy-brand);
}

.crumb.is-current {
  color: var(--wy-text-primary);
  font-weight: 500;
}

.sep {
  color: var(--wy-text-placeholder);
}

/* ---------- 页头 ---------- */
.tax-hero {
  display: flex;
  gap: 22px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--wy-border-subtle);
}

.hero-cover {
  flex: none;
  width: 84px;
  height: 84px;
  border-radius: var(--wy-radius-md);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--wy-brand-soft);
  color: var(--wy-brand);
  font-size: 30px;
  font-weight: 700;
}

.hero-cover.has-image {
  background: var(--wy-bg-muted);
}

.hero-cover img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-text {
  flex: 1;
  min-width: 0;
}

.hero-kicker {
  margin: 0 0 6px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--wy-brand);
}

.hero-title {
  margin: 0 0 8px;
  font-size: 27px;
  line-height: 1.3;
  font-weight: 700;
  color: var(--wy-text-primary);
}

.hero-desc {
  margin: 0 0 12px;
  font-size: 14px;
  line-height: 1.7;
  color: var(--wy-text-secondary);
  white-space: pre-line;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  overflow: hidden;
}

.hero-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 7px;
  font-size: 13px;
  color: var(--wy-text-tertiary);
}

.dot {
  color: var(--wy-text-placeholder);
}

.hero-actions {
  margin-top: 16px;
}

.hero-cta {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 34px;
  padding: 0 15px;
  border-radius: var(--wy-radius-md);
  background: var(--wy-brand);
  color: var(--wy-on-brand);
  font-size: 13px;
  font-weight: 500;
  text-decoration: none;
  transition: background-color var(--wy-duration) var(--wy-easing);
}

.hero-cta:hover {
  background: var(--wy-brand-hover);
}

/* ---------- 子分类入口 ---------- */
.tax-children {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-top: 18px;
}

.tax-children-title {
  margin-right: 2px;
  font-size: 12px;
  font-weight: 600;
  color: var(--wy-text-tertiary);
}

.tax-child {
  display: inline-flex;
  align-items: center;
  height: 28px;
  padding: 0 11px;
  border: 1px solid var(--wy-border-subtle);
  border-radius: 999px;
  background: var(--wy-bg-surface);
  color: var(--wy-text-secondary);
  font-size: 13px;
  line-height: 1;
  text-decoration: none;
  transition:
    color var(--wy-duration) var(--wy-easing),
    border-color var(--wy-duration) var(--wy-easing),
    background-color var(--wy-duration) var(--wy-easing);
}

.tax-child:hover {
  border-color: var(--wy-brand);
  background: var(--wy-brand-soft);
  color: var(--wy-brand);
}

/* ---------- 列表 ---------- */
.tax-list-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  margin: 24px 0 6px;
}

.tax-list-title {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--wy-text-primary);
}

.tax-list-count {
  font-size: 12px;
  font-variant-numeric: tabular-nums;
  color: var(--wy-text-placeholder);
}

.tax-list {
  display: flex;
  flex-direction: column;
}

.tax-row {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 18px 4px;
  border-bottom: 1px solid var(--wy-border-subtle);
  text-decoration: none;
  transition: background-color var(--wy-duration) var(--wy-easing);
}

.tax-row:last-child {
  border-bottom: none;
}

.tax-row:hover {
  background: var(--wy-bg-muted);
}

.row-index {
  flex: none;
  width: 26px;
  padding-top: 3px;
  font-family: var(--wy-font-mono);
  font-size: 12px;
  color: var(--wy-text-placeholder);
}

.row-main {
  flex: 1;
  min-width: 0;
}

.row-title {
  margin: 0 0 6px;
  font-size: 17px;
  line-height: 1.45;
  font-weight: 600;
  color: var(--wy-text-primary);
  transition: color var(--wy-duration) var(--wy-easing);
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  overflow: hidden;
}

.tax-row:hover .row-title {
  color: var(--wy-brand);
}

.row-summary {
  margin: 0 0 8px;
  font-size: 13px;
  line-height: 1.6;
  color: var(--wy-text-tertiary);
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  overflow: hidden;
}

.row-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--wy-text-placeholder);
}

.row-cover {
  flex: none;
  width: 132px;
  height: 82px;
  border-radius: var(--wy-radius-sm);
  overflow: hidden;
  background: var(--wy-bg-muted);
}

.row-cover img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.tax-state {
  margin: 0;
  padding: 56px 0;
  text-align: center;
  font-size: 14px;
  color: var(--wy-text-tertiary);
}

/* ---------- 纵向卡网格（分类页） ---------- */
/* auto-fill + minmax：加载更多追加时自动补位，窄屏自然降到 2/1 列 */
.tax-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 32px 24px;
}

.grid-card {
  display: flex;
  flex-direction: column;
  text-decoration: none;
}

.grid-cover {
  border-radius: var(--wy-radius-md);
  overflow: hidden;
  background: var(--wy-bg-muted);
  aspect-ratio: 16 / 10;
  margin-bottom: 12px;
}

.grid-cover img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--wy-duration-slow, 0.3s) var(--wy-easing);
}

.grid-card:hover .grid-cover img {
  transform: scale(1.03);
}

.grid-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--wy-brand-soft) 0%, var(--wy-bg-muted) 100%);
}

.grid-mark {
  font-size: 44px;
  font-weight: 700;
  line-height: 1;
  color: var(--wy-brand);
  opacity: 0.35;
}

.grid-title {
  margin: 0 0 6px;
  font-size: 17px;
  line-height: 1.45;
  font-weight: 600;
  color: var(--wy-text-primary);
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  overflow: hidden;
  transition: color var(--wy-duration) var(--wy-easing);
}

.grid-card:hover .grid-title {
  color: var(--wy-brand);
}

.grid-summary {
  margin: 0 0 8px;
  font-size: 13px;
  line-height: 1.6;
  color: var(--wy-text-tertiary);
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  overflow: hidden;
}

.grid-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  margin-top: auto;
  font-size: 12px;
  color: var(--wy-text-placeholder);
}

.tax-foot {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 24px;
}

.tax-foot-end {
  font-size: 12px;
  color: var(--wy-text-placeholder);
}

/* ---------- 响应式 ---------- */
@media (max-width: 1024px) {
  .tax-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .taxonomy-page {
    padding: 20px 16px 56px;
  }

  .tax-hero {
    gap: 14px;
    padding-bottom: 20px;
  }

  .hero-cover {
    width: 62px;
    height: 62px;
    font-size: 22px;
  }

  .hero-title {
    font-size: 21px;
  }

  .row-title {
    font-size: 15px;
  }

  .row-cover {
    width: 92px;
    height: 58px;
  }

  .tax-row {
    padding: 14px 0;
  }

  .tax-grid {
    grid-template-columns: 1fr;
    gap: 24px;
  }

  .grid-title {
    font-size: 15px;
  }
}
</style>
