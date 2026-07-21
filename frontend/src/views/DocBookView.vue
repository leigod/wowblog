<template>
  <div class="docbook-container">
    <!-- 文档书头部 -->
    <div v-if="docbook" class="docbook-header">
      <div class="cover-section">
        <img v-if="docbook.cover" :src="docbook.cover" :alt="docbook.name" class="docbook-cover" />
        <div v-else class="docbook-cover-placeholder">
          <span class="icon">{{ docbook.icon || '?' }}</span>
        </div>
      </div>
      <div class="info-section">
        <h1 class="docbook-title">{{ docbook.name }}</h1>
        <p v-if="docbook.description" class="docbook-description">{{ docbook.description }}</p>
        <div class="docbook-meta">
          <span class="meta-item">
            <i class="icon-file"></i> {{ docbook.doc_count }}{{ t('doc.articles_count') }}
          </span>
          <span v-if="docbook.author_name" class="meta-item">
            <i class="icon-user"></i> {{ docbook.author_name }}
          </span>
        </div>
      </div>
    </div>

    <!-- 搜索框 -->
    <div v-if="docbook?.allow_search" class="search-section">
      <input
        v-model="searchKeyword"
        type="text"
        :placeholder="t('doc.search_placeholder')"
        class="search-input"
        @input="handleSearch"
      />
    </div>

    <!-- 主内容区 -->
    <div class="docbook-content">
      <!-- 侧边栏 -->
      <aside v-if="docbook?.show_sidebar && docTree.length > 0" class="doc-sidebar">
        <div class="sidebar-header">
          <h3>{{ t('doc.toc') }}</h3>
        </div>
        <div class="sidebar-content">
          <DocTree :tree="docTree" :docbook-slug="docbookSlug" @select="handleSelectDoc" />
        </div>
      </aside>

      <!-- 主文档区 -->
      <main class="doc-main">
        <div v-if="searchResults.length > 0" class="search-results">
          <h3>{{ t('doc.search_results') }}</h3>
          <ul class="result-list">
            <li v-for="doc in searchResults" :key="doc.id" class="result-item">
              <router-link
                :to="`/docs/${docbookSlug}/${doc.slug}`"
                class="result-link"
                @click="clearSearch"
              >
                <h4>{{ doc.title }}</h4>
                <p v-if="doc.excerpt" class="result-excerpt">{{ doc.excerpt }}</p>
              </router-link>
            </li>
          </ul>
        </div>

        <div v-else-if="currentDoc" class="doc-content">
          <article class="doc-article">
            <h1 class="doc-title">{{ currentDoc.title }}</h1>
            <div class="doc-meta">
              <span class="meta-item">{{ t('doc.views') }} {{ currentDoc.view_count }}</span>
            </div>
            <div v-if="currentDoc.content" class="markdown-body" v-html="renderedContent"></div>
            <div v-else class="doc-empty">{{ t('doc.no_content') }}</div>
          </article>

          <!-- 文档导航 -->
          <nav v-if="navigation" class="doc-navigation">
            <router-link
              v-if="navigation.prev"
              :to="`/docs/${docbookSlug}/${navigation.prev.slug}`"
              class="nav-link prev"
            >
              <span class="nav-label">{{ t('doc.prev') }}</span>
              <span class="nav-title">{{ navigation.prev.title }}</span>
            </router-link>
            <router-link
              v-if="navigation.next"
              :to="`/docs/${docbookSlug}/${navigation.next.slug}`"
              class="nav-link next"
            >
              <span class="nav-label">{{ t('doc.next') }}</span>
              <span class="nav-title">{{ navigation.next.title }}</span>
            </router-link>
          </nav>

          <!-- 面包屑 -->
          <nav v-if="navigation?.breadcrumbs?.length" class="breadcrumbs">
            <router-link
              v-for="crumb in navigation.breadcrumbs"
              :key="crumb.id"
              :to="`/docs/${docbookSlug}/${crumb.slug}`"
              class="breadcrumb-link"
            >
              {{ crumb.title }}
            </router-link>
          </nav>
        </div>

        <div v-else-if="docbook?.home_doc_id" class="doc-loading">
          {{ t('doc.loading') }}
        </div>

        <div v-else class="doc-empty-state">
          <h2>{{ t('doc.welcome_title') }}</h2>
          <p>{{ t('doc.welcome_message') }}</p>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { docApi, docBookApi, type DocBook, type Doc, type DocTreeNode } from '@/api'

const { t } = useI18n()

const route = useRoute()
const docbookSlug = computed(() => route.params.docbookSlug as string)
const docSlug = computed(() => route.params.docSlug as string | undefined)

// 状态
const docbook = ref<DocBook | null>(null)
const docTree = ref<DocTreeNode[]>([])
const currentDoc = ref<Doc | null>(null)
const navigation = ref<any>(null)
const searchKeyword = ref('')
const searchResults = ref<Doc[]>([])

// Markdown渲染 (简单实现，实际可使用markdown-it等库)
const renderedContent = computed(() => {
  if (!currentDoc.value?.content) return ''
  return currentDoc.value.content
    // 简单的markdown转换
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
    .replace(/\*(.*)\*/gim, '<em>$1</em>')
    .replace(/\n/gim, '<br>')
})

// 加载文档书
const loadDocBook = async () => {
  try {
    const response = await docBookApi.getBySlug(docbookSlug.value)
    if (response.data) {
      docbook.value = response.data
    }
  } catch (error) {
    console.error('加载文档书失败:', error)
  }
}

// 加载文档树
const loadDocTree = async () => {
  if (!docbook.value) return
  try {
    const response = await docApi.getTree(docbook.value.id)
    if (response.data) {
      docTree.value = response.data
    }
  } catch (error) {
    console.error('加载文档树失败:', error)
  }
}

// 加载文档
const loadDoc = async (slug: string) => {
  if (!docbook.value) return
  try {
    const [docRes, navRes] = await Promise.all([
      docApi.getBySlug(slug, docbook.value.id),
      docApi.getNavigation((currentDoc.value?.id || docbook.value.home_doc_id)!)
    ])
    if (docRes.data) {
      currentDoc.value = docRes.data
    }
    if (navRes.data) {
      navigation.value = navRes.data
    }
  } catch (error) {
    console.error('加载文档失败:', error)
  }
}

// 加载首页文档
const loadHomeDoc = async () => {
  if (!docbook.value?.home_doc_id) return
  try {
    const response = await docApi.getById(docbook.value.home_doc_id)
    if (response.data) {
      currentDoc.value = response.data
      loadNavigation(response.data.id)
    }
  } catch (error) {
    console.error('加载首页文档失败:', error)
  }
}

const loadNavigation = async (docId: number) => {
  try {
    const response = await docApi.getNavigation(docId)
    if (response.data) {
      navigation.value = response.data
    }
  } catch (error) {
    console.error('加载导航失败:', error)
  }
}

// 搜索
const handleSearch = async () => {
  if (!docbook.value || !searchKeyword.value.trim()) {
    searchResults.value = []
    return
  }
  try {
    const response = await docApi.search(docbook.value.id, searchKeyword.value)
    if (response.data) {
      searchResults.value = response.data
    }
  } catch (error) {
    console.error('搜索失败:', error)
  }
}

const clearSearch = () => {
  searchKeyword.value = ''
  searchResults.value = []
}

const handleSelectDoc = (doc: DocTreeNode) => {
  // 由路由导航处理
}

// 监听路由变化
watch(() => route.params, async (newParams) => {
  if (newParams.docSlug) {
    await loadDoc(newParams.docSlug as string)
  } else if (docbook.value?.home_doc_id) {
    await loadHomeDoc()
  }
})

onMounted(async () => {
  await loadDocBook()
  if (docbook.value) {
    await loadDocTree()
    if (docSlug.value) {
      await loadDoc(docSlug.value)
    } else if (docbook.value.home_doc_id) {
      await loadHomeDoc()
    }
  }
})
</script>

<script lang="ts">
// 文档树组件
import { defineComponent, h } from 'vue'
import type { PropType } from 'vue'
import { RouterLink } from 'vue-router'

const DocTree = defineComponent({
  name: 'DocTree',
  props: {
    tree: {
      type: Array as PropType<any[]>,
      required: true
    },
    docbookSlug: {
      type: String,
      required: true
    }
  },
  emits: ['select'],
  setup(props, { emit }) {
    const renderNode = (node: any, level: number = 0) => {
      const hasChildren = node.children && node.children.length > 0
      const className = 'tree-node level-' + level

      const children = [
        h(RouterLink, {
          to: '/docs/' + props.docbookSlug + '/' + node.slug,
          class: 'tree-node-link',
          onClick: () => emit('select', node)
        }, () => [
          h('span', { class: 'node-icon' }, hasChildren ? '?' : '-'),
          h('span', { class: 'node-title' }, node.title)
        ])
      ]

      if (hasChildren) {
        children.push(
          h('div', { class: 'tree-children' },
            node.children.map((child: any) => renderNode(child, level + 1))
          )
        )
      }

      return h('div', { class: className, key: node.id }, children)
    }

    return () => h('div', { class: 'doc-tree' },
      props.tree.map(node => renderNode(node))
    )
  }
})

export { DocTree }
</script>

<style scoped>
.docbook-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.docbook-header {
  display: flex;
  gap: 24px;
  margin-bottom: 32px;
  padding: 24px;
  background: var(--card-bg);
  border-radius: 8px;
}

.cover-section {
  flex-shrink: 0;
}

.docbook-cover {
  width: 120px;
  height: 160px;
  object-fit: cover;
  border-radius: 8px;
}

.docbook-cover-placeholder {
  width: 120px;
  height: 160px;
  background: var(--accent-color);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  color: white;
}

.info-section {
  flex: 1;
}

.docbook-title {
  font-size: 28px;
  margin: 0 0 12px 0;
}

.docbook-description {
  color: var(--text-secondary);
  margin: 0 0 16px 0;
  line-height: 1.6;
}

.docbook-meta {
  display: flex;
  gap: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--text-secondary);
  font-size: 14px;
}

.search-section {
  margin-bottom: 24px;
}

.search-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 16px;
}

.docbook-content {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 24px;
  align-items: start;
}

.doc-sidebar {
  position: sticky;
  top: 20px;
  background: var(--card-bg);
  border-radius: 8px;
  padding: 16px;
  max-height: calc(100vh - 40px);
  overflow-y: auto;
}

.sidebar-header h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
}

.doc-tree {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tree-node {
  padding-left: 0;
}

.tree-node.level-1 { padding-left: 16px; }
.tree-node.level-2 { padding-left: 32px; }
.tree-node.level-3 { padding-left: 48px; }

.tree-node-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: 4px;
  color: var(--text-primary);
  text-decoration: none;
  transition: background 0.2s;
}

.tree-node-link:hover {
  background: var(--hover-bg);
}

.router-link-active .tree-node-link {
  background: var(--accent-color);
  color: white;
}

.doc-main {
  min-height: 500px;
}

.doc-content {
  background: var(--card-bg);
  border-radius: 8px;
  padding: 32px;
}

.doc-article {
  max-width: 800px;
  margin: 0 auto;
}

.doc-title {
  font-size: 32px;
  margin: 0 0 16px 0;
}

.doc-meta {
  padding: 12px 0;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 24px;
  color: var(--text-secondary);
}

.markdown-body {
  line-height: 1.8;
  font-size: 16px;
}

.doc-empty {
  text-align: center;
  padding: 60px 0;
  color: var(--text-secondary);
}

.doc-empty-state {
  text-align: center;
  padding: 80px 20px;
  background: var(--card-bg);
  border-radius: 8px;
}

.doc-navigation {
  display: flex;
  justify-content: space-between;
  margin-top: 48px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}

.nav-link {
  flex: 1;
  max-width: 45%;
  padding: 16px;
  background: var(--hover-bg);
  border-radius: 8px;
  text-decoration: none;
  color: var(--text-primary);
  transition: background 0.2s;
}

.nav-link:hover {
  background: var(--border-color);
}

.nav-link.next {
  text-align: right;
  margin-left: auto;
}

.nav-label {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.nav-title {
  display: block;
  font-weight: 500;
}

.breadcrumbs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.breadcrumb-link {
  color: var(--accent-color);
  text-decoration: none;
  font-size: 14px;
}

.breadcrumb-link:hover {
  text-decoration: underline;
}

.search-results {
  background: var(--card-bg);
  border-radius: 8px;
  padding: 24px;
}

.result-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.result-item {
  border-bottom: 1px solid var(--border-color);
  padding: 16px 0;
}

.result-item:last-child {
  border-bottom: none;
}

.result-link {
  display: block;
  text-decoration: none;
  color: var(--text-primary);
}

.result-link h4 {
  margin: 0 0 8px 0;
}

.result-excerpt {
  color: var(--text-secondary);
  font-size: 14px;
  margin: 0;
}

@media (max-width: 768px) {
  .docbook-content {
    grid-template-columns: 1fr;
  }

  .doc-sidebar {
    position: static;
    max-height: 400px;
  }
}
</style>
