<template>
  <div class="docbook-page">
    <div v-if="loading" class="book-state">{{ t('doc.loading') }}</div>
    <!-- 文档书不存在：友好错误页 + 其他文档书建议 -->
    <div v-else-if="!docbook" class="error-state">
      <div class="error-icon">
        <el-icon :size="34"><Collection /></el-icon>
      </div>
      <h2 class="error-title">{{ t('doc.docbook_not_found_title') }}</h2>
      <p class="error-desc">{{ t('doc.docbook_not_found') }}</p>
      <div class="error-actions">
        <el-button @click="router.push('/')">{{ t('doc.error_back_home') }}</el-button>
      </div>
      <div v-if="otherBooks.length" class="error-suggestions">
        <p class="suggestions-label">{{ t('doc.error_try_books') }}</p>
        <div class="suggestions-list">
          <router-link v-for="b in otherBooks" :key="b.id"
            :to="`/docs/${b.slug}`" class="suggestion-link">
            {{ b.name }}
          </router-link>
        </div>
      </div>
    </div>

    <template v-else>
      <!-- 书籍封面区：封面 + 书名 + 简介 + 元信息 + 入口 -->
      <header class="book-hero">
        <div class="book-cover">
          <img v-if="docbook.cover" :src="docbook.cover" :alt="docbook.name" />
          <div v-else class="book-cover-fallback">
            <span>{{ coverLetter }}</span>
          </div>
        </div>

        <div class="book-intro">
          <p class="book-kicker">{{ t('doc.book_label') }}</p>
          <h1 class="book-title">{{ docbook.name }}</h1>
          <p v-if="docbook.description" class="book-desc">{{ docbook.description }}</p>

          <div class="book-meta">
            <span>{{ docbook.doc_count }} {{ t('doc.articles_count') }}</span>
            <template v-if="docbook.author_name">
              <span class="dot">·</span>
              <span>{{ docbook.author_name }}</span>
            </template>
            <template v-if="updatedText">
              <span class="dot">·</span>
              <span>{{ t('doc.updated') }} {{ updatedText }}</span>
            </template>
          </div>

          <div v-if="startDocSlug" class="book-actions">
            <router-link :to="`/docs/${docbookSlug}/${startDocSlug}`" class="book-cta">
              {{ t('doc.start_reading') }}
              <el-icon><ArrowRight /></el-icon>
            </router-link>
          </div>
        </div>
      </header>

      <!-- 书内搜索 -->
      <div v-if="docbook.allow_search" class="book-search">
        <el-input
          v-model="searchKeyword"
          :placeholder="t('doc.search_placeholder')"
          :prefix-icon="Search"
          size="large"
          clearable
          @input="onSearchInput"
          @clear="clearSearch"
        />
      </div>

      <!-- 搜索结果 -->
      <section v-if="isSearching" class="book-section">
        <div class="section-head">
          <h2 class="section-title">{{ t('doc.search_results') }}</h2>
          <span v-if="searchResults.length" class="section-count">
            {{ searchResults.length }}
          </span>
        </div>

        <div v-if="searchResults.length" class="search-list">
          <router-link
            v-for="item in searchResults"
            :key="item.id"
            :to="`/docs/${docbookSlug}/${item.slug}`"
            class="search-row"
          >
            <span class="search-row-title">{{ item.title }}</span>
            <p v-if="item.excerpt" class="search-row-excerpt">{{ item.excerpt }}</p>
          </router-link>
        </div>
        <p v-else class="book-empty">{{ t('doc.search_empty') }}</p>
      </section>

      <!-- 章节目录 -->
      <section v-else class="book-section">
        <div class="section-head">
          <h2 class="section-title">{{ t('doc.doc_index') }}</h2>
          <span class="section-count">{{ docbook.doc_count }} {{ t('doc.articles_count') }}</span>
        </div>

        <div v-if="sections.length" class="chapter-grid">
          <article v-for="(section, index) in sections" :key="section.id" class="chapter-card">
            <div class="chapter-head">
              <span class="chapter-index">{{ pad(index + 1) }}</span>
              <router-link
                :to="`/docs/${docbookSlug}/${section.slug}`"
                class="chapter-title"
                :title="section.title"
              >
                {{ section.title }}
              </router-link>
            </div>

            <ul v-if="section.children.length" class="chapter-links">
              <li v-for="child in section.children.slice(0, MAX_LINKS)" :key="child.id">
                <router-link
                  :to="`/docs/${docbookSlug}/${child.slug}`"
                  :title="child.title"
                >
                  {{ child.title }}
                </router-link>
              </li>
              <li v-if="section.children.length > MAX_LINKS" class="chapter-more">
                +{{ section.children.length - MAX_LINKS }}
              </li>
            </ul>

            <router-link
              v-else
              :to="`/docs/${docbookSlug}/${section.slug}`"
              class="chapter-read"
            >
              {{ t('doc.read') }}
              <el-icon><ArrowRight /></el-icon>
            </router-link>
          </article>
        </div>

        <p v-else class="book-empty">{{ t('doc.no_docs') }}</p>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ArrowRight, Search, Collection } from '@element-plus/icons-vue'
import { docApi, docBookApi, type DocBook, type Doc, type DocTreeNode } from '@/api'

const { t } = useI18n()
const route = useRoute()

// 章节卡片里最多平铺几条子页，超出只显示计数，避免单卡过长
const MAX_LINKS = 4

const docbookSlug = computed(() => route.params.docbookSlug as string)
const router = useRouter()

// 错误页建议：拿不到当前书时，推荐其他文档书
const otherBooks = ref<DocBook[]>([])
const loadOtherBooks = async () => {
  try {
    const response = await docBookApi.list({ skip: 0, limit: 10 })
    otherBooks.value = (response.data || []).filter(b => b.slug !== docbookSlug.value).slice(0, 6)
  } catch {
    otherBooks.value = []
  }
}

const docbook = ref<DocBook | null>(null)
const docTree = ref<DocTreeNode[]>([])
const loading = ref(true)
const searchKeyword = ref('')
const searchResults = ref<Doc[]>([])

// 顶层节点即章节；有子页的展示子页清单，没有子页的作为单篇入口
const sections = computed(() => docTree.value)

const coverLetter = computed(() => (docbook.value?.name || '?').trim().slice(0, 1))

const pad = (n: number) => String(n).padStart(2, '0')

const updatedText = computed(() => {
  const ts = docbook.value?.updatetime
  if (!ts) return ''
  const d = new Date(ts * 1000)
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
})

const findSlugById = (nodes: DocTreeNode[], id: number): string | null => {
  for (const node of nodes) {
    if (node.id === id) return node.slug
    const hit = findSlugById(node.children || [], id)
    if (hit) return hit
  }
  return null
}

const firstLeafSlug = (nodes: DocTreeNode[]): string | null => {
  for (const node of nodes) {
    if (!node.children?.length) return node.slug
    const deep = firstLeafSlug(node.children)
    if (deep) return deep
  }
  return null
}

// 「开始阅读」优先落到后台配置的首页文档，没配就取第一篇叶子文档
const startDocSlug = computed(() => {
  const homeId = docbook.value?.home_doc_id
  if (homeId) {
    const slug = findSlugById(docTree.value, homeId)
    if (slug) return slug
  }
  return firstLeafSlug(docTree.value)
})

// 输入即搜，加 300ms 防抖，避免逐字触发请求
let searchTimer: ReturnType<typeof setTimeout> | null = null
const isSearching = computed(() => searchKeyword.value.trim().length > 0)

const onSearchInput = () => {
  if (searchTimer) clearTimeout(searchTimer)
  if (!isSearching.value) {
    searchResults.value = []
    return
  }
  searchTimer = setTimeout(() => {
    void runSearch()
  }, 300)
}

const runSearch = async () => {
  if (!docbook.value) return
  try {
    const response = await docApi.search(docbook.value.id, searchKeyword.value.trim())
    searchResults.value = response.data || []
  } catch (error) {
    console.error('搜索失败:', error)
    searchResults.value = []
  }
}

const clearSearch = () => {
  searchKeyword.value = ''
  searchResults.value = []
}

const loadDocBook = async () => {
  try {
    const response = await docBookApi.getBySlug(docbookSlug.value)
    docbook.value = response.data || null
  } catch (error) {
    console.error('加载文档书失败:', error)
    docbook.value = null
  }
  if (!docbook.value) await loadOtherBooks()
}

const loadDocTree = async () => {
  if (!docbook.value) return
  try {
    const response = await docApi.getTree(docbook.value.id)
    docTree.value = response.data || []
  } catch (error) {
    console.error('加载文档树失败:', error)
    docTree.value = []
  }
}

const load = async () => {
  loading.value = true
  await loadDocBook()
  if (docbook.value) await loadDocTree()
  loading.value = false
}

watch(docbookSlug, () => {
  searchKeyword.value = ''
  searchResults.value = []
  void load()
})

onMounted(load)

onUnmounted(() => {
  if (searchTimer) clearTimeout(searchTimer)
})
</script>

<style scoped>
.docbook-page {
  /* .el-main 是 flex 容器，只写 max-width 会让本页按内容宽度收缩，
     章节网格被挤成 2 列；必须显式撑满再由 max-width 收口。 */
  width: 100%;
  max-width: 1120px;
  box-sizing: border-box;
  margin: 0 auto;
  padding: 32px 24px 80px;
}

.book-state {
  padding: 120px 0;
  text-align: center;
  color: var(--wy-text-tertiary);
}

/* ---------- 友好错误页（文档书不存在） ---------- */
.error-state {
  max-width: 560px;
  width: 100%;
  margin: 48px auto;
  padding: 48px 40px;
  text-align: center;
  background: var(--wy-bg-surface);
  border: 1px solid var(--wy-border-subtle);
  border-radius: var(--wy-radius-lg);
  box-shadow: var(--wy-shadow-card);
}

.error-icon {
  width: 76px;
  height: 76px;
  margin: 0 auto 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--wy-brand-soft);
  color: var(--wy-brand);
}

.error-title {
  margin: 0 0 8px;
  font-size: 20px;
  font-weight: 600;
  color: var(--wy-text-primary);
}

.error-desc {
  margin: 0 0 24px;
  font-size: 14px;
  line-height: 1.6;
  color: var(--wy-text-secondary);
}

.error-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}

.error-suggestions {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--wy-border-subtle);
}

.suggestions-label {
  margin: 0 0 12px;
  font-size: 13px;
  color: var(--wy-text-tertiary);
}

.suggestions-list {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
}

.suggestion-link {
  display: inline-flex;
  align-items: center;
  padding: 6px 14px;
  font-size: 13px;
  color: var(--wy-text-secondary);
  text-decoration: none;
  background: var(--wy-bg-muted);
  border-radius: var(--wy-radius-md);
  transition: color var(--wy-duration) var(--wy-easing),
    background-color var(--wy-duration) var(--wy-easing);
}

.suggestion-link:hover {
  color: var(--wy-brand);
  background: var(--wy-brand-soft);
}

/* ---------- 封面区 ---------- */
.book-hero {
  display: flex;
  gap: 28px;
  padding: 32px;
  background: var(--wy-bg-surface);
  border: 1px solid var(--wy-border-subtle);
  border-radius: var(--wy-radius-lg);
}

.book-cover {
  flex: none;
  width: 104px;
  height: 140px;
  border-radius: var(--wy-radius-md);
  overflow: hidden;
  box-shadow: var(--wy-shadow-card);
}

.book-cover img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.book-cover-fallback {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background: linear-gradient(150deg, var(--wy-brand) 0%, var(--wy-brand-hover) 100%);
  color: var(--wy-on-brand);
  font-size: 40px;
  font-weight: 700;
  letter-spacing: 2px;
}

.book-intro {
  flex: 1;
  min-width: 0;
}

.book-kicker {
  margin: 0 0 6px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--wy-text-tertiary);
}

.book-title {
  margin: 0 0 10px;
  font-size: 28px;
  line-height: 1.3;
  font-weight: 700;
  color: var(--wy-text-primary);
}

.book-desc {
  margin: 0 0 14px;
  font-size: 15px;
  line-height: 1.7;
  color: var(--wy-text-secondary);
}

.book-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--wy-text-tertiary);
}

.book-meta .dot {
  color: var(--wy-text-placeholder);
}

.book-actions {
  margin-top: 20px;
}

.book-cta {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 38px;
  padding: 0 18px;
  border-radius: var(--wy-radius-md);
  background: var(--wy-brand);
  color: var(--wy-on-brand);
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: background-color var(--wy-duration) var(--wy-easing),
    transform var(--wy-duration) var(--wy-easing);
}

.book-cta:hover {
  background: var(--wy-brand-hover);
  transform: translateY(-1px);
}

/* ---------- 搜索 ---------- */
.book-search {
  margin: 20px 0 8px;
}

/* ---------- 章节区 ---------- */
.book-section {
  margin-top: 32px;
}

.section-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.section-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--wy-text-primary);
}

.section-count {
  font-size: 13px;
  color: var(--wy-text-tertiary);
}

.chapter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(272px, 1fr));
  gap: 16px;
}

.chapter-card {
  display: flex;
  flex-direction: column;
  padding: 18px 20px;
  background: var(--wy-bg-surface);
  border: 1px solid var(--wy-border-subtle);
  border-radius: var(--wy-radius-md);
  transition: border-color var(--wy-duration) var(--wy-easing),
    box-shadow var(--wy-duration) var(--wy-easing),
    transform var(--wy-duration) var(--wy-easing);
}

.chapter-card:hover {
  border-color: var(--wy-border-strong);
  box-shadow: var(--wy-shadow-card-hover);
  transform: translateY(-2px);
}

.chapter-head {
  display: flex;
  align-items: baseline;
  gap: 10px;
  min-width: 0;
}

.chapter-index {
  flex: none;
  font-family: var(--wy-font-mono);
  font-size: 12px;
  color: var(--wy-text-placeholder);
}

.chapter-title {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  font-size: 15px;
  font-weight: 600;
  color: var(--wy-text-primary);
  text-decoration: none;
  transition: color var(--wy-duration) var(--wy-easing);
}

.chapter-title:hover {
  color: var(--wy-brand);
}

.chapter-links {
  list-style: none;
  margin: 12px 0 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.chapter-links li {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
  font-size: 13px;
  line-height: 1.5;
}

.chapter-links li::before {
  content: '';
  flex: none;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--wy-border-strong);
}

.chapter-links a {
  min-width: 0;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  color: var(--wy-text-secondary);
  text-decoration: none;
  transition: color var(--wy-duration) var(--wy-easing);
}

.chapter-links a:hover {
  color: var(--wy-brand);
}

.chapter-more {
  color: var(--wy-text-placeholder);
}

.chapter-read {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-top: auto;
  padding-top: 12px;
  font-size: 13px;
  color: var(--wy-text-tertiary);
  text-decoration: none;
  transition: color var(--wy-duration) var(--wy-easing);
}

.chapter-read:hover {
  color: var(--wy-brand);
}

/* ---------- 搜索结果 ---------- */
.search-list {
  display: flex;
  flex-direction: column;
  background: var(--wy-bg-surface);
  border: 1px solid var(--wy-border-subtle);
  border-radius: var(--wy-radius-md);
  overflow: hidden;
}

.search-row {
  display: block;
  padding: 14px 20px;
  text-decoration: none;
  border-bottom: 1px solid var(--wy-border-subtle);
  transition: background-color var(--wy-duration) var(--wy-easing);
}

.search-row:last-child {
  border-bottom: none;
}

.search-row:hover {
  background: var(--wy-bg-muted);
}

.search-row-title {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--wy-text-primary);
}

.search-row-excerpt {
  margin: 6px 0 0;
  font-size: 13px;
  line-height: 1.6;
  color: var(--wy-text-tertiary);
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  overflow: hidden;
}

.book-empty {
  margin: 0;
  padding: 48px 0;
  text-align: center;
  font-size: 14px;
  color: var(--wy-text-tertiary);
}

/* ---------- 响应式 ---------- */
@media (max-width: 768px) {
  .docbook-page {
    padding: 20px 16px 48px;
  }

  .book-hero {
    flex-direction: column;
    gap: 18px;
    padding: 22px;
  }

  .book-cover {
    width: 76px;
    height: 102px;
  }

  .book-cover-fallback {
    font-size: 30px;
  }

  .book-title {
    font-size: 22px;
  }

  .chapter-grid {
    grid-template-columns: 1fr;
  }
}
</style>
