<template>
  <div class="doc-view-container">
    <div v-if="loading" class="loading">{{ t('doc.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <template v-else-if="doc && docbook">
      <!-- 文档头部面包屑 -->
      <nav class="breadcrumbs">
        <router-link to="/" class="breadcrumb-link">首页</router-link>
        <span class="separator">/</span>
        <router-link :to="`/docs/${docbookSlug}`" class="breadcrumb-link">
          {{ docbook.name }}
        </router-link>
        <span v-if="navigation?.breadcrumbs?.length" class="separator">/</span>
        <template v-if="navigation?.breadcrumbs?.length">
          <template v-for="crumb in navigation.breadcrumbs" :key="crumb.id">
            <router-link :to="`/docs/${docbookSlug}/${crumb.slug}`" class="breadcrumb-link">
              {{ crumb.title }}
            </router-link>
            <span class="separator">/</span>
          </template>
        </template>
        <span class="current">{{ doc.title }}</span>
      </nav>

      <!-- 侧边栏和主内容 -->
      <div class="doc-content-wrapper">
        <!-- 侧边栏 -->
        <aside class="doc-sidebar left-sidebar">
          <template v-if="docbook.show_sidebar && docTree.length > 0">
            <!-- 搜索框 -->
            <div class="sidebar-search">
              <el-input v-model="searchKeyword" :placeholder="t('doc.search_placeholder')" :prefix-icon="Search" clearable size="large"
                :loading="searching" />
            </div>
            <div class="sidebar-header">
              <h3>{{ docbook.name }}</h3>
              <!-- <router-link :to="`/docs/${docbookSlug}`" class="back-link">
                <el-icon :size="14" style="vertical-align: middle">
                  <ArrowLeft />
                </el-icon>
                <span>返回封面</span>
              </router-link> -->
            </div>

            <div class="sidebar-content">
              <el-tree-v2 :key="doc?.id" ref="treeRef" :data="filteredDocTree" :props="treeProps" :height="600"
                :item-size="32" :default-expand-all="false" :expand-on-click-node="false"
                :default-expanded-keys="expandedKeys" @node-click="handleNodeClick" class="doc-tree">
                <template #default="{ node, data }">
                  <router-link :to="`/docs/${docbookSlug}/${data.slug}`" class="tree-node-link"
                    :class="{ active: isCurrentDoc(data.slug) }">
                    <span class="node-label">{{ node.label }}</span>
                  </router-link>
                </template>
              </el-tree-v2>
            </div>
          </template>
        </aside>

        <!-- 主文档内容 -->
        <main class="doc-main">
          <article class="doc-article">
            <h1 class="doc-title">{{ doc.title }}</h1>

            <div class="doc-meta">
              <!-- <span v-if="doc.author_name" class="meta-item">
                <i class="icon-user"></i> {{ doc.author_name }}
              </span>
              <span class="meta-item">
                <i class="icon-eye"></i> {{ doc.view_count }} 次浏览
              </span> -->
              <span v-if="doc.pubtime" class="meta-item">
                <!-- <i class="icon-clock"></i> -->
                更新于: {{ formatDate(doc.pubtime) }} 文档著作权归开发者所有，未经许可，禁止转载、复制此文档的任何内容。
              </span>
            </div>

            <div v-if="doc.excerpt" class="doc-excerpt">
              {{ doc.excerpt }}
            </div>

            <div class="doc-content markdown-body">
              <div v-html="renderedContent"></div>
            </div>

            <!-- 子文档导航（内容为空时显示） -->
            <div v-if="showChildNav">
              <p>本文档没有内容，以下是该文档下的子页面：</p>
              <ul>
                <li v-for="child in childDocs" :key="child.id">
                  <router-link :to="`/docs/${docbookSlug}/${child.slug}`">
                    {{ child.title }}
                  </router-link>
                </li>
              </ul>
            </div>
          </article>


          <!-- 文档导航 -->
          <nav v-if="hasNavigation" class="doc-navigation">
            <router-link v-if="navigation.prev" :to="`/docs/${docbookSlug}/${navigation.prev.slug}`"
              class="nav-link prev">
              <el-icon class="nav-icon" :size="20">
                <ArrowLeft />
              </el-icon>
              <div class="nav-info">
                <span class="nav-label">{{ t('doc.prev') }}</span>
                <span class="nav-title">{{ navigation.prev.title }}</span>
              </div>
            </router-link>

            <router-link v-if="navigation.next" :to="`/docs/${docbookSlug}/${navigation.next.slug}`"
              class="nav-link next">
              <div class="nav-info">
                <span class="nav-label">{{ t('doc.next') }}</span>
                <span class="nav-title">{{ navigation.next.title }}</span>
              </div>
              <el-icon class="nav-icon" :size="20">
                <ArrowRight />
              </el-icon>
            </router-link>
          </nav>

          <!-- 评论区（如果允许评论） -->
          <div v-if="allowDocComment" class="doc-comments">
            <h3>{{ t('doc.comments') }} ({{ commentsList.length }})</h3>

            <!-- 评论表单 -->
            <div v-if="showCommentForm" class="comment-form">
              <div class="comment-user-info">
                <el-avatar :size="32" :src="appStore.userInfo?.profile_image || '/src/assets/avatar.png'" />
                <span>{{ appStore.userInfo?.username || 'Anonymous' }}</span>
              </div>
              <el-input
                v-model="commentInput"
                :rows="3"
                type="textarea"
                :placeholder="t('doc.comment_placeholder')"
                class="comment-input"
              />
              <div class="comment-actions">
                <el-button type="primary" size="small" @click="handleSubmitComment">{{ t('doc.submit_comment') }}</el-button>
              </div>
            </div>

            <!-- 未登录提示 -->
            <div v-else class="comment-login-tip">
              <p>{{ t('doc.login_to_comment') }}</p>
              <el-button type="primary" size="small" @click="router.push('/login')">{{ t('doc.login') }}</el-button>
            </div>

            <el-divider />

            <!-- 评论列表 -->
            <div v-if="commentsLoading" class="comments-loading">
              <el-skeleton :rows="3" animated />
            </div>

            <div v-else-if="commentsList.length === 0" class="comments-empty">
              <p>{{ t('doc.no_comments_yet') }}</p>
            </div>

            <div v-else class="comments-list">
              <!-- 排序选择 -->
              <div class="comments-header">
                <span>{{ t('doc.all_comments', { count: commentsList.length }) }}</span>
                <el-select v-model="commentList_order" size="small" style="width: 120px">
                  <el-option :label="t('doc.sort_by_hot')" value="top" />
                  <el-option :label="t('doc.sort_by_time')" value="new" />
                </el-select>
              </div>

              <!-- 评论项 -->
              <div v-for="item in commentsList" :key="item.id" class="comment-item">
                <el-avatar :size="40" :src="item.profile_image || '/src/assets/avatar.png'" class="comment-avatar" />
                <div class="comment-content">
                  <div class="comment-header">
                    <span class="comment-author">{{ item.full_name }}@{{ item.username }}</span>
                    <span class="comment-time">{{ formatCommentTime(item.createtime) }}</span>
                  </div>
                  <p class="comment-text">{{ item.comment }}</p>
                  <div class="comment-footer">
                    <span class="comment-location">{{ item.location || '未知' }}</span>
                    <div class="comment-stats">
                      <span class="stat-item">
                        <el-icon :size="14"><ChatDotRound /></el-icon>
                        {{ item.replys }}
                      </span>
                      <el-button
                        v-if="showCommentForm"
                        type="primary"
                        link
                        size="small"
                        @click="handleReplyTo(item.id)"
                      >
                        {{ t('doc.reply') }}
                      </el-button>
                    </div>
                  </div>

                  <!-- 回复表单 -->
                  <div v-if="replyToComment === item.id" class="reply-form">
                    <el-input
                      v-model="replyInput"
                      :rows="2"
                      type="textarea"
                      :placeholder="t('doc.reply_placeholder')"
                      size="small"
                      class="reply-input"
                    />
                    <div class="reply-actions">
                      <el-button size="small" @click="handleCancelReply">{{ t('common.cancel') }}</el-button>
                      <el-button type="primary" size="small" @click="handleSubmitReply(item.id)">
                        {{ t('doc.submit_comment') }}
                      </el-button>
                    </div>
                  </div>

                  <!-- 回复列表 -->
                  <div v-if="item.replys > 0" class="replies-section">
                    <el-button
                      v-if="!expandedRepliesIds.includes(item.id)"
                      type="primary"
                      link
                      size="small"
                      @click="toggleReplies(item.id)"
                    >
                      {{ t('doc.expand_replies', { replies: item.replys }) }}
                    </el-button>
                    <el-button
                      v-else
                      type="primary"
                      link
                      size="small"
                      @click="toggleReplies(item.id)"
                    >
                      {{ t('doc.collapse_replies') }}
                    </el-button>

                    <div v-if="expandedRepliesIds.includes(item.id)" class="replies-list">
                      <div v-for="reply in repliesList" :key="reply.id" class="reply-item">
                        <el-avatar :size="28" :src="reply.profile_image || '/src/assets/avatar.png'" />
                        <div class="reply-content">
                          <div class="reply-header">
                            <span class="reply-author">{{ reply.full_name }}@{{ reply.username }}</span>
                            <span class="reply-time">{{ formatCommentTime(reply.createtime) }}</span>
                          </div>
                          <p class="reply-text">{{ reply.comment }}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>

        <!-- 右侧目录 -->
        <aside class="doc-sidebar right-sidebar">
          <!-- 占位符，保持高度 -->
          <div v-show="isRightSidebarFixed" ref="rightSidebarPlaceholderRef" class="right-sidebar-placeholder"
            :style="{ height: sidebarHeight + 'px' }"></div>
          <!-- 实际内容 -->
          <div ref="rightSidebarRef" :class="{ 'is-fixed': isRightSidebarFixed }" class="right-sidebar-inner">
            <template v-if="tableOfContents.length > 0">
              <div class="toc-header">
                <h4>本文目录</h4>
              </div>
              <el-anchor :offset="80" :bounds="50" class="doc-anchor" @click="handleAnchorClick">
                <el-anchor-link v-for="item in tableOfContents" :key="item.id" :href="`#${item.id}`"
                  :class="`toc-level-${item.level}`">
                  {{ item.text }}
                </el-anchor-link>
              </el-anchor>
            </template>
          </div>
        </aside>

      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
// 定义组件名称，用于 keep-alive 缓存
defineOptions({
  name: 'DocView'
})

import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ArrowLeft, ArrowRight, Search, ChatDotRound } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { docApi, docBookApi, type DocBook, type Doc, type DocTreeNode } from '@/api/services/doc'
import docDefaultExport from '@/api/services/doc'
import { useAppStore } from '@/stores/app'
import { getSystemConfig } from '@/api/services/common'
import hljs from 'highlight.js/lib/common'
import 'highlight.js/styles/github-dark.css'

const { t } = useI18n()
const appStore = useAppStore()

// 类型定义
interface DocComment {
  doc_id: number
  type: 'subject' | 'reply'
  subject_id?: number
  comment: string
}

// 文档评论API
const docCommentApi = (docDefaultExport as any).docComment || {
  getList: (doc_id: number, type: 'subject' | 'reply' = 'subject', subject_id?: number, order: 'top' | 'new' = 'top', currentpage: number = 1, pagesize: number = 10) => {
    return fetch(`/api/docs/${doc_id}/comments?doc_id=${doc_id}&type=${type}&subject_id=${subject_id || 0}&order=${order}&currentpage=${currentpage}&pagesize=${pagesize}`)
  },
  create: (doc_id: number, comment: DocComment) => {
    return fetch(`/api/docs/${doc_id}/comments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(comment)
    })
  }
}

const route = useRoute()
const router = useRouter()

const docbookSlug = computed(() => route.params.docbookSlug as string)
const docSlug = computed(() => route.params.docSlug as string)

// 状态
const loading = ref(true)
const error = ref('')
const docbook = ref<DocBook | null>(null)
const doc = ref<Doc | null>(null)
const docTree = ref<DocTreeNode[]>([])
const navigation = ref<any>(null)
const searchKeyword = ref('')
const rightSidebarRef = ref<HTMLElement | null>(null)
const rightSidebarPlaceholderRef = ref<HTMLElement | null>(null)
const isRightSidebarFixed = ref(false)
const sidebarHeight = ref(0)
const isAnchorScrolling = ref(false) // 锚点滚动中标志
const searchResults = ref<Doc[]>([])
const searching = ref(false)
const loadingFromCache = ref(false) // 是否正在从缓存加载

// 缓存相关函数
const getCacheKey = () => `doc_cache_${docbookSlug.value}_${docSlug.value}`
const getCacheExpiry = () => `doc_cache_expiry_${docbookSlug.value}_${docSlug.value}`
const CACHE_DURATION = 30 * 60 * 1000 // 30分钟缓存有效期

// 保存数据到本地缓存
const saveToCache = (data: any) => {
  try {
    const cacheKey = getCacheKey()
    const expiryKey = getCacheExpiry()
    localStorage.setItem(cacheKey, JSON.stringify(data))
    localStorage.setItem(expiryKey, String(Date.now() + CACHE_DURATION))
  } catch (e) {
    console.warn('缓存保存失败:', e)
  }
}

// 从本地缓存读取数据
const loadFromCache = () => {
  try {
    const cacheKey = getCacheKey()
    const expiryKey = getCacheExpiry()
    const cachedData = localStorage.getItem(cacheKey)
    const expiry = localStorage.getItem(expiryKey)

    if (cachedData && expiry && Date.now() < parseInt(expiry)) {
      return JSON.parse(cachedData)
    }
    // 清除过期缓存
    if (cachedData) {
      localStorage.removeItem(cacheKey)
      localStorage.removeItem(expiryKey)
    }
  } catch (e) {
    console.warn('缓存读取失败:', e)
  }
  return null
}

// 清除缓存
const clearCache = () => {
  try {
    localStorage.removeItem(getCacheKey())
    localStorage.removeItem(getCacheExpiry())
  } catch (e) {
    console.warn('缓存清除失败:', e)
  }
}

// 评论相关状态
const commentsList = ref<any[]>([])
const commentsLoading = ref(false)
const commentInput = ref('')
const commentList_order = ref<'top' | 'new'>('top')
const expandedRepliesIds = ref<number[]>([])
const repliesList = ref<any[]>([])
const needLogin = computed(() => !appStore.token)
const showCommentForm = computed(() => !!appStore.token)
const replyToComment = ref<number | null>(null)  // 当前回复的评论ID
const replyInput = ref('')  // 回复输入内容
const siteConfig = ref<any>(null)  // 站点配置
const allowDocComment = computed(() => {
  // 全局设置和文档书设置都允许时才显示评论
  const globalEnabled = siteConfig.value?.doc_comment === 1
  const docbookEnabled = docbook.value?.allow_comment === true
  return globalEnabled && docbookEnabled
})

// 树形组件展开的节点
const expandedKeys = ref<number[]>([])

// 树形组件引用
const treeRef = ref()

// 树形组件配置
const treeProps = {
  value: 'id',
  label: 'title',
  children: 'children'
}

// 判断是否是当前文档
const isCurrentDoc = (slug: string) => {
  return route.params.docSlug === slug
}

// 通过遍历树找到节点路径
const findNodePath = (nodes: DocTreeNode[], targetId: number, path: number[] = []): number[] | null => {
  for (const node of nodes) {
    const currentPath = [...path, node.id]
    if (node.id === targetId) {
      return currentPath.slice(0, -1) // 返回父节点路径
    }
    if (node.children && node.children.length > 0) {
      const result = findNodePath(node.children, targetId, currentPath)
      if (result) return result
    }
  }
  return null
}

// 根据文档路径获取需要展开的父节点ID列表
const getExpandedKeys = (currentDoc: Doc, tree: DocTreeNode[]): number[] => {
  const keys: number[] = []

  console.log('=== getExpandedKeys ===')
  console.log('当前文档:', currentDoc.title, 'id:', currentDoc.id, 'path:', currentDoc.path)

  // 方法1：从文档的 path 字段解析
  if (currentDoc.path && currentDoc.path !== '0') {
    const pathIds = currentDoc.path.split('/').filter(Boolean).map(id => parseInt(id))
    console.log('path解析结果:', pathIds)
    // 不包含最后一个节点（当前节点自己）
    keys.push(...pathIds.slice(0, -1))
    console.log('从path解析的展开节点IDs:', keys)
  }

  // 方法2：通过遍历树查找（备用）
  const treePath = findNodePath(tree, currentDoc.id)
  console.log('从树遍历的展开节点IDs:', treePath)
  if (treePath) {
    if (keys.length === 0) {
      keys.push(...treePath)
    }
  }

  console.log('最终返回的keys:', keys)
  console.log('====================')
  return keys
}

// 树节点点击处理
const handleNodeClick = (data: any) => {
  router.push(`/docs/${docbookSlug.value}/${data.slug}`)
}

const hasNavigation = computed(() =>
  navigation.value?.prev || navigation.value?.next
)

// 获取当前文档的子文档列表
const childDocs = computed(() => {
  if (!doc.value || !docTree.value.length) return []

  // 递归查找当前文档的子节点
  const findChildren = (nodes: DocTreeNode[], targetId: number): DocTreeNode[] => {
    for (const node of nodes) {
      if (node.id === targetId) {
        return node.children || []
      }
      if (node.children && node.children.length > 0) {
        const result = findChildren(node.children, targetId)
        if (result.length > 0) return result
      }
    }
    return []
  }

  return findChildren(docTree.value, doc.value.id)
})

// 判断是否需要显示子文档导航（内容为空且有子文档）
const showChildNav = computed(() => {
  return !doc.value?.content && childDocs.value.length > 0
})

// 过滤文档树（根据搜索关键词）
const filteredDocTree = computed(() => {
  if (!searchKeyword.value.trim()) {
    return docTree.value
  }

  // 获取匹配文档的 ID 集合
  const matchedIds = new Set(searchResults.value.map(doc => doc.id))

  if (matchedIds.size === 0) {
    return []
  }

  // 递归过滤树，只显示匹配的节点及其父节点
  const filterTree = (nodes: DocTreeNode[]): DocTreeNode[] => {
    const result: DocTreeNode[] = []

    for (const node of nodes) {
      const isMatched = matchedIds.has(node.id)
      const hasMatchingChildren = node.children && node.children.length > 0

      if (isMatched) {
        // 该节点匹配，保留该节点及其所有子节点
        result.push(node)
      } else if (hasMatchingChildren) {
        // 该节点不匹配，检查子节点
        const filteredChildren = filterTree(node.children)
        if (filteredChildren.length > 0) {
          // 有子节点匹配，保留该节点但只显示匹配的子节点
          result.push({
            ...node,
            children: filteredChildren
          })
        }
      }
    }

    return result
  }

  return filterTree(docTree.value)
})

// 监听搜索关键词变化（带防抖）
let searchTimer: ReturnType<typeof setTimeout> | null = null

watch(searchKeyword, async (newKeyword) => {
  // 清除之前的定时器
  if (searchTimer) {
    clearTimeout(searchTimer)
  }

  if (!newKeyword.trim()) {
    searchResults.value = []
    return
  }

  if (!docbook.value) return

  // 设置新的定时器（300ms 防抖）
  searchTimer = setTimeout(async () => {
    try {
      searching.value = true
      const response = await docApi.search(docbook.value!.id, newKeyword, 100)
      if (response.data) {
        searchResults.value = response.data
      }
    } catch (error) {
      console.error('搜索失败:', error)
      searchResults.value = []
    } finally {
      searching.value = false
    }
  }, 300)
})

// 目录提取
const tableOfContents = computed(() => {
  if (!doc.value?.content) return []

  // 创建临时 DOM 来解析 HTML
  const tempDiv = document.createElement('div')
  tempDiv.innerHTML = doc.value.content

  const headings = tempDiv.querySelectorAll('h1, h2, h3, h4, h5, h6')
  const toc: Array<{ id: string; text: string; level: number }> = []

  headings.forEach((heading, index) => {
    const id = `heading-${index}`
    heading.id = id

    const level = parseInt(heading.tagName.substring(1))
    const text = heading.textContent || ''

    toc.push({ id, text, level })
  })

  return toc
})

// 内容渲染 - 编辑器已输出HTML，直接使用
const renderedContent = computed(() => {
  if (!doc.value?.content) return ''
  // 编辑器已经输出 HTML，直接返回
  return doc.value.content
})

const formatDate = (timestamp: number) => {
  const date = new Date(timestamp * 1000)
  return date.toLocaleDateString('zh-CN')
}

const formatCommentTime = (timestamp: number) => {
  const date = new Date(timestamp * 1000)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) {
    const hours = Math.floor(diff / (1000 * 60 * 60))
    if (hours === 0) {
      const minutes = Math.floor(diff / (1000 * 60))
      return minutes <= 0 ? '刚刚' : `${minutes}分钟前`
    }
    return `${hours}小时前`
  } else if (days < 7) {
    return `${days}天前`
  } else {
    return date.toLocaleDateString('zh-CN')
  }
}

// 初始化代码高亮和复制按钮
const initCodeHighlighting = () => {
  setTimeout(() => {
    const contentDiv = document.querySelector('.doc-content')
    if (contentDiv && doc.value?.content) {
      // 设置标题 ID
      const contentHeadings = contentDiv.querySelectorAll('h1, h2, h3, h4, h5, h6')
      contentHeadings.forEach((heading, index) => {
        heading.id = `heading-${index}`
      })

      // 代码高亮并添加复制按钮
      const codeBlocks = contentDiv.querySelectorAll('pre code')
      codeBlocks.forEach((block) => {
        hljs.highlightElement(block as HTMLElement)

        // 为代码块的父元素 pre 添加复制按钮
        const pre = block.parentElement as HTMLElement
        if (pre && !pre.querySelector('.code-copy-btn')) {
          addCopyButton(pre, block.textContent || '')
        }
      })
    }
  }, 100)
}

// 加载数据
const loadData = async (useCache = true) => {
  // 首先尝试从缓存加载
  if (useCache) {
    const cached = loadFromCache()
    if (cached) {
      loadingFromCache.value = true
      siteConfig.value = cached.siteConfig
      docbook.value = cached.docbook
      doc.value = cached.doc
      docTree.value = cached.docTree
      navigation.value = cached.navigation
      loading.value = false

      // 异步初始化代码高亮
      setTimeout(() => {
        initCodeHighlighting()
        if (doc.value) {
          expandedKeys.value = getExpandedKeys(doc.value, docTree.value)
        }
      }, 100)

      // 在后台加载最新数据
      loadData(false).catch(err => {
        console.warn('后台刷新失败，使用缓存数据:', err)
      })
      return
    }
  }

  loading.value = true
  loadingFromCache.value = false
  error.value = ''

  try {
    // 并行加载站点配置、文档书、文档和文档树
    const [configResponse, bookResponse] = await Promise.all([
      getSystemConfig(),
      docBookApi.getBySlug(docbookSlug.value)
    ])

    if (configResponse.code === 1) {
      siteConfig.value = configResponse.data
    }

    if (!bookResponse.data) {
      error.value = t('doc.docbook_not_found')
      return
    }

    docbook.value = bookResponse.data
    const docbookId = bookResponse.data.id

    // 并行加载文档和文档树
    const [docResponse, treeResponse] = await Promise.all([
      docApi.getBySlug(docSlug.value, docbookId),
      docApi.getTree(docbookId)
    ])

    if (!docResponse.data) {
      error.value = t('doc.not_found')
      return
    }

    doc.value = docResponse.data
    docTree.value = treeResponse.data || []

    // 更新树形组件展开的节点
    if (doc.value) {
      expandedKeys.value = getExpandedKeys(doc.value, docTree.value)
      console.log('最终设置的 expandedKeys:', expandedKeys.value)
      console.log('docTree 数据:', JSON.stringify(docTree.value, null, 2))
    }

    // 加载导航信息
    const navResponse = await docApi.getNavigation(doc.value.id)
    if (navResponse.data) {
      navigation.value = navResponse.data
    }

    // 保存到缓存
    saveToCache({
      siteConfig: siteConfig.value,
      docbook: docbook.value,
      doc: doc.value,
      docTree: docTree.value,
      navigation: navigation.value
    })

    // 数据加载完成后初始化代码高亮和复制按钮
    initCodeHighlighting()

    // 加载评论（检查全局设置和文档书设置）
    if (allowDocComment.value) {
      loadComments()
    }
  } catch (e: any) {
    console.error('加载文档失败:', e)
    // 如果有缓存数据，显示缓存数据而不是错误
    const cached = loadFromCache()
    if (cached) {
      ElMessage.warning('网络连接失败，显示缓存内容')
      siteConfig.value = cached.siteConfig
      docbook.value = cached.docbook
      doc.value = cached.doc
      docTree.value = cached.docTree
      navigation.value = cached.navigation
      if (doc.value) {
        expandedKeys.value = getExpandedKeys(doc.value, docTree.value)
      }
      initCodeHighlighting()
    } else {
      error.value = e.message || t('doc.load_failed')
    }
  } finally {
    loading.value = false
    loadingFromCache.value = false
  }
}

watch(() => route.params, () => loadData(true))

// 锚点点击处理
const handleAnchorClick = () => {
  // 设置锚点滚动中标志，阻止滚动监听改变吸顶状态
  isAnchorScrolling.value = true
}

// 检测用户手动滚动（区分锚点滚动和手动滚动）
let lastScrollTime = 0
let lastScrollTopForDir = 0 // 用于检测滚动方向

// 右侧边栏吸顶处理
const handleRightSidebarScroll = () => {
  if (!rightSidebarRef.value) return

  const rect = rightSidebarRef.value.getBoundingClientRect()
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop
  const offsetTop = 80 // 吸顶距离
  const now = Date.now()

  // 检测滚动方向
  const scrollDirection = scrollTop > lastScrollTopForDir ? 'down' : 'up'
  lastScrollTopForDir = scrollTop

  // 检测是否是用户手动滚动（滚动间隔超过 100ms）
  const timeDelta = now - lastScrollTime
  lastScrollTime = now

  // 如果正在锚点滚动中，只有当用户向下滚动且超过原始位置时才解锁
  if (isAnchorScrolling.value) {
    if (timeDelta > 100 && scrollDirection === 'down') {
      // 获取原始位置
      const originalTop = rightSidebarRef.value.dataset.originalTop
        ? parseFloat(rightSidebarRef.value.dataset.originalTop)
        : 0

      // 只有向下滚动超过原始位置才解锁
      if (scrollTop > originalTop - offsetTop) {
        isAnchorScrolling.value = false
      }
    }
    // 锚点滚动中，保持当前吸顶状态不变
    return
  }

  // 获取元素的原始位置（只在首次计算）
  const originalTop = rightSidebarRef.value.dataset.originalTop
    ? parseFloat(rightSidebarRef.value.dataset.originalTop)
    : rect.top + scrollTop

  // 保存原始位置
  if (!rightSidebarRef.value.dataset.originalTop) {
    rightSidebarRef.value.dataset.originalTop = originalTop.toString()
  }

  // 判断是否需要吸顶
  if (scrollTop > originalTop - offsetTop) {
    if (!isRightSidebarFixed.value) {
      // 即将变为固定状态
      sidebarHeight.value = rect.height
      isRightSidebarFixed.value = true
    }
  } else {
    if (isRightSidebarFixed.value) {
      isRightSidebarFixed.value = false
    }
  }
}

// 监听窗口大小变化，重新计算位置
const handleResize = () => {
  // 窗口大小变化时重新计算吸顶状态
  if (rightSidebarRef.value) {
    // 清除原始位置缓存，强制重新计算
    delete rightSidebarRef.value.dataset.originalTop
    handleRightSidebarScroll()
  }
}

// 评论相关功能
// 加载评论列表
const loadComments = async () => {
  if (!doc.value || !allowDocComment.value) return

  commentsLoading.value = true
  try {
    const res = await docCommentApi.getList(
      doc.value.id,
      'subject',
      undefined,
      commentList_order.value,
      1,
      20
    )
    if (res.code === 1 && res.data) {
      commentsList.value = res.data
    }
  } catch (error) {
    console.error('加载评论失败:', error)
  } finally {
    commentsLoading.value = false
  }
}

// 提交评论
const handleSubmitComment = async () => {
  if (!doc.value) return
  if (!commentInput.value.trim()) {
    ElMessage.warning(t('doc.comment_required'))
    return
  }

  try {
    const comment: DocComment = {
      doc_id: doc.value.id,
      type: 'subject',
      comment: commentInput.value.trim()
    }

    const res = await docCommentApi.create(doc.value.id, comment)
    if (res.code === 1) {
      ElMessage.success(t('doc.comment_success'))
      commentInput.value = ''
      // 重新加载评论列表
      await loadComments()
    } else {
      ElMessage.error(res.msg || t('doc.comment_failed'))
    }
  } catch (error) {
    console.error('发布评论失败:', error)
    ElMessage.error(t('doc.comment_failed'))
  }
}

// 切换回复展开状态
const toggleReplies = async (subjectId: number) => {
  if (!doc.value) return

  const index = expandedRepliesIds.value.indexOf(subjectId)
  if (index > -1) {
    // 收起
    expandedRepliesIds.value.splice(index, 1)
  } else {
    // 展开 - 加载回复列表
    try {
      const res = await docCommentApi.getList(
        doc.value.id,
        'reply',
        subjectId,
        'top',
        1,
        10
      )
      if (res.code === 1 && res.data) {
        repliesList.value = res.data
        expandedRepliesIds.value.push(subjectId)
      }
    } catch (error) {
      console.error('加载回复失败:', error)
    }
  }
}

// 开始回复
const handleReplyTo = (commentId: number) => {
  replyToComment.value = commentId
  replyInput.value = ''
}

// 取消回复
const handleCancelReply = () => {
  replyToComment.value = null
  replyInput.value = ''
}

// 提交回复
const handleSubmitReply = async (subjectId: number) => {
  if (!doc.value) return
  if (!replyInput.value.trim()) {
    ElMessage.warning(t('doc.reply_required'))
    return
  }

  try {
    const comment: DocComment = {
      doc_id: doc.value.id,
      type: 'reply',
      subject_id: subjectId,
      comment: replyInput.value.trim()
    }

    const res = await docCommentApi.create(doc.value.id, comment)
    if (res.code === 1) {
      ElMessage.success(t('doc.reply_success'))
      replyInput.value = ''
      replyToComment.value = null
      // 重新加载评论列表
      await loadComments()
      // 重新展开回复
      if (!expandedRepliesIds.value.includes(subjectId)) {
        expandedRepliesIds.value.push(subjectId)
      }
      const replyRes = await docCommentApi.getList(doc.value.id, 'reply', subjectId, 'top', 1, 10)
      if (replyRes.code === 1 && replyRes.data) {
        repliesList.value = replyRes.data
      }
    } else {
      ElMessage.error(res.msg || t('doc.reply_failed'))
    }
  } catch (error) {
    console.error('发布回复失败:', error)
    ElMessage.error(t('doc.reply_failed'))
  }
}

// 监听排序方式变化
watch(commentList_order, () => {
  loadComments()
})

onMounted(() => {
  loadData()
  // 添加滚动监听
  window.addEventListener('scroll', handleRightSidebarScroll, { passive: true })
  // 添加窗口大小变化监听
  window.addEventListener('resize', handleResize)
})

// lucide:copy 图标 SVG
const copyIconSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>`

// lucide:check 图标 SVG (复制成功后显示)
const checkIconSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`

// 添加复制按钮到代码块
const addCopyButton = (preElement: HTMLElement, code: string) => {
  // 创建包装容器
  const wrapper = document.createElement('div')
  wrapper.className = 'code-block-wrapper'

  // 将 pre 元素包装在 wrapper 中
  if (preElement.parentNode) {
    preElement.parentNode.insertBefore(wrapper, preElement)
    wrapper.appendChild(preElement)
  }

  // 创建复制按钮
  const button = document.createElement('button')
  button.className = 'code-copy-btn'
  button.innerHTML = `<span class="copy-icon">${copyIconSvg}</span><span class="copy-text">复制</span>`
  button.title = '复制代码'

  button.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(code)
      button.classList.add('copied')
      button.innerHTML = `<span class="copy-icon">${checkIconSvg}</span><span class="copy-text">已复制</span>`
      ElMessage.success('代码已复制到剪贴板')

      setTimeout(() => {
        button.classList.remove('copied')
        button.innerHTML = `<span class="copy-icon">${copyIconSvg}</span><span class="copy-text">复制</span>`
      }, 2000)
    } catch (err) {
      ElMessage.error('复制失败，请手动复制')
    }
  })

  wrapper.appendChild(button)
}

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleRightSidebarScroll)
  window.removeEventListener('resize', handleResize)
  // 清除搜索定时器
  if (searchTimer) {
    clearTimeout(searchTimer)
  }
})
</script>

<style scoped>
.doc-view-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.loading,
.error {
  text-align: center;
  padding: 60px 20px;
  font-size: 18px;
}

.error {
  color: var(--error-color, #f56c6c);
}

.breadcrumbs {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-bottom: 24px;
  padding: 12px 16px;
  background: var(--card-bg);
  border-radius: 8px;
  font-size: 14px;
}

.breadcrumb-link {
  color: var(--accent-color);
  text-decoration: none;
  transition: color 0.2s;
}

.breadcrumb-link:hover {
  color: var(--accent-hover);
}

.separator {
  color: var(--text-secondary);
}

.current {
  color: var(--text-secondary);
}

.doc-content-wrapper {
  display: grid;
  grid-template-columns: 280px 1fr 240px;
  gap: 24px;
  position: relative;
}

.doc-sidebar {
  background: var(--card-bg);
  border-radius: 8px;
  padding: 16px;
}

.left-sidebar {
  position: sticky;
  top: 20px;
  max-height: calc(100vh - 40px);
  overflow-y: auto;
  align-self: start;
}

.right-sidebar {
  width: 240px;
  position: relative;
}

.right-sidebar-placeholder {
  width: 100%;
}

.right-sidebar-inner {
  transition: transform 0.2s;
  /* border-left: 1px solid var(--el-border-color); */
}

.right-sidebar-inner.is-fixed {
  position: fixed;
  top: 80px;
  max-height: calc(100vh - 100px);
  overflow-y: auto;
  z-index: 100;
  /* 宽度和 right 通过内联样式设置 */
}

/* Affix 内部的目录容器样式 */
.right-sidebar .toc-header,
.right-sidebar .toc-content {
  background: var(--card-bg);
  border-radius: 8px;
  padding: 12px;
}

.right-sidebar .toc-header {
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 8px;
  padding-bottom: 8px;
}

.sidebar-header {
  /* margin-bottom: 16px;
  padding-bottom: 16px; */
  border-bottom: 1px solid var(--border-color);
}

.sidebar-header h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: var(--accent-color);
  text-decoration: none;
  font-size: 14px;
}

.sidebar-search {
  margin-bottom: 12px;
}

/* el-tree-v2 样式 */
.doc-tree {
  --el-tree-node-content-height: 32px;
}

.doc-tree :deep(.el-tree-v2__wrapper) {
  background: transparent;
}

.doc-tree :deep(.el-tree-v2__node) {
  padding-left: 0 !important;
}

.doc-tree :deep(.el-tree-v2__node-content) {
  padding-left: 0 !important;
}

.tree-node-link {
  display: block;
  width: 100%;
  padding: 6px 8px;
  color: #606266;
  text-decoration: none;
  border-radius: 4px;
  transition: all 0.2s;
}

.tree-node-link:hover {
  background: #ecf5ff;
  color: #409eff;
}

.tree-node-link.active {
  background: #ecf5ff;
  color: #409eff;
  font-weight: 500;
}

.node-label {
  font-size: 14px;
}

.doc-main {
  background: var(--card-bg);
  border-radius: 8px;
  padding: 40px;
  min-height: 500px;
}

.doc-article {
  max-width: 800px;
  margin: 0 auto;
}

.doc-title {
  font-size: 36px;
  margin: 0 0 16px 0;
  line-height: 1.3;
}

.doc-title-line {
  border: none;
  height: 1px;
  background-color: var(--gray-3);
}

.doc-line hr {
  border: none;
  height: 1px;
  background-color: var(--gray-3);
}

.doc-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  padding: 16px 0;
  border-bottom: 1px solid var(--gray-3);
  margin-bottom: 24px;
  color: var(--gray-4);
  font-size: 14px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.doc-excerpt {
  padding: 16px;
  background: var(--hover-bg);
  border-left: 4px solid var(--accent-color);
  border-radius: 4px;
  margin-bottom: 32px;
  font-size: 16px;
  line-height: 1.6;
}

.doc-content {
  font-size: 16px;
  line-height: 1.8;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4),
.markdown-body :deep(h5),
.markdown-body :deep(h6) {
  margin-top: 32px;
  margin-bottom: 16px;
  font-weight: 600;
  line-height: 1.4;
}

.markdown-body :deep(h1) {
  font-size: 28px;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 8px;
}

.markdown-body :deep(h2) {
  font-size: 24px;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 8px;
}

.markdown-body :deep(h3) {
  font-size: 20px;
}

.markdown-body :deep(h4) {
  font-size: 18px;
}

.markdown-body :deep(h5) {
  font-size: 16px;
}

.markdown-body :deep(h6) {
  font-size: 14px;
}

.markdown-body :deep(p) {
  margin-bottom: 16px;
  line-height: 1.8;
}

/* 行内代码样式 */
.markdown-body :deep(code) {
  padding: 3px 6px;
  background: #f4f4f5;
  border: 1px solid #e4e4e7;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
  font-size: 0.9em;
  color: #e83e8c;
}

/* 代码块样式 */
.markdown-body :deep(.code-block-wrapper) {
  position: relative;
  margin: 16px 0;
}

.markdown-body :deep(pre) {
  padding: 16px;
  padding-top: 16px;
  background: #1e1e1e;
  border-radius: 8px;
  overflow-x: auto;
  margin: 0;
}

.markdown-body :deep(pre code) {
  padding: 0;
  background: transparent;
  border: none;
  color: #d4d4d4;
  font-size: 0.875em;
  line-height: 1.6;
}

/* 复制按钮样式 - 使用 :deep() 确保样式应用到动态添加的元素 */
.markdown-body :deep(.code-copy-btn) {
  position: absolute;
  top: 6px;
  right: 6px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  z-index: 10;
  line-height: 1;
}

.markdown-body :deep(.code-copy-btn:hover) {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  color: white;
}

.markdown-body :deep(.code-copy-btn.copied) {
  background: #67c23a;
  border-color: #67c23a;
  color: white;
}

.markdown-body :deep(.copy-icon) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 14px;
  height: 14px;
  line-height: 1;
}

.markdown-body :deep(.copy-icon svg) {
  width: 100%;
  height: 100%;
}

.markdown-body :deep(.copy-text) {
  font-size: 11px;
  line-height: 1;
}

/* 图片样式 */
.markdown-body :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 16px 0;
  display: block;
}

/* 列表样式 */
.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  margin-bottom: 16px;
  padding-left: 2em;
}

.markdown-body :deep(li) {
  margin-bottom: 4px;
}

/* 引用样式 */
.markdown-body :deep(blockquote) {
  margin: 16px 0;
  padding: 12px 16px;
  border-left: 4px solid #409eff;
  background: #ecf5ff;
  color: #606266;
  border-radius: 4px;
}

.markdown-body :deep(blockquote p) {
  margin: 0;
  margin-bottom: 8px;
}

.markdown-body :deep(blockquote p:last-child) {
  margin-bottom: 0;
}

/* 链接样式 */
.markdown-body :deep(a) {
  color: var(--accent-color);
  text-decoration: none;
}

.markdown-body :deep(a:hover) {
  text-decoration: underline;
}

/* 表格样式 */
.markdown-body :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
}

.markdown-body :deep(th),
.markdown-body :deep(td) {
  border: 1px solid var(--border-color);
  padding: 8px 12px;
  text-align: left;
}

.markdown-body :deep(th) {
  background: var(--hover-bg);
  font-weight: 600;
}

.markdown-body :deep(tr:nth-child(even)) {
  background: var(--hover-bg);
}

/* 分割线 */
.markdown-body :deep(hr) {
  border: none;
  border-top: 2px solid var(--border-color);
  margin: 24px 0;
}

.doc-navigation {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-top: 48px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}

.nav-link {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: var(--hover-bg);
  border-radius: 8px;
  text-decoration: none;
  color: var(--text-primary);
  transition: all 0.2s;
  border: 1px solid transparent;
}

.nav-link:hover {
  background: #ecf5ff;
  border-color: #409eff;
  color: #409eff;
}

.nav-link.next {
  flex-direction: row;
  justify-content: flex-end;
  text-align: right;
}

.nav-link.next .nav-info {
  text-align: right;
}

.nav-info {
  flex: 1;
  min-width: 0;
}

.nav-label {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.nav-link:hover .nav-label {
  color: #409eff;
}

.nav-title {
  display: block;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.nav-icon {
  font-size: 20px;
  flex-shrink: 0;
  color: #909399;
}

.nav-link:hover .nav-icon {
  color: #409eff;
}

.doc-comments {
  margin-top: 48px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}

.doc-comments h3 {
  margin: 0 0 20px 0;
  font-size: 20px;
  font-weight: 600;
}

/* 评论表单 */
.comment-form {
  margin-bottom: 24px;
  padding: 16px;
  background: var(--hover-bg);
  border-radius: 8px;
}

.comment-user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 500;
}

.comment-input {
  margin-bottom: 12px;
}

.comment-actions {
  display: flex;
  justify-content: flex-end;
}

.comment-login-tip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  background: var(--hover-bg);
  border-radius: 8px;
  margin-bottom: 24px;
}

.comment-login-tip p {
  margin: 0;
  color: var(--text-secondary);
}

/* 评论列表 */
.comments-loading,
.comments-empty {
  padding: 40px 20px;
  text-align: center;
  color: var(--text-secondary);
}

.comments-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-size: 14px;
  color: var(--text-secondary);
}

.comment-item {
  display: flex;
  gap: 12px;
  padding: 16px 0;
  border-bottom: 1px solid var(--border-color);
}

.comment-item:last-child {
  border-bottom: none;
}

.comment-avatar {
  flex-shrink: 0;
}

.comment-content {
  flex: 1;
  min-width: 0;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.comment-author {
  font-weight: 500;
  color: var(--text-primary);
}

.comment-time {
  font-size: 12px;
  color: var(--text-secondary);
}

.comment-text {
  margin: 0 0 8px 0;
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-primary);
  word-break: break-word;
}

.comment-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: var(--text-secondary);
}

.comment-stats {
  display: flex;
  gap: 12px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 回复列表 */
.replies-section {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
}

.replies-list {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.reply-item {
  display: flex;
  gap: 8px;
}

.reply-content {
  flex: 1;
}

.reply-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.reply-author {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.reply-time {
  font-size: 11px;
  color: var(--text-secondary);
}

.reply-text {
  margin: 0;
  font-size: 13px;
  line-height: 1.5;
  color: var(--text-primary);
}

/* 回复表单样式 */
.reply-form {
  margin-top: 12px;
  padding: 12px;
  background: var(--hover-bg);
  border-radius: 8px;
}

.reply-input {
  margin-bottom: 8px;
}

.reply-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.comments-placeholder {
  color: var(--text-secondary);
  text-align: center;
  padding: 40px;
}

/* 目录样式 */
.toc-header {
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
}

.toc-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

/* el-anchor 样式覆盖 */
.doc-anchor {
  --el-anchor-bg-color: transparent;
  --el-anchor-padding-left: 0;
  --el-anchor-padding-right: 0;
}

.doc-anchor :deep(.el-anchor__list) {
  padding-left: 0;
}

.doc-anchor :deep(.el-anchor__item) {
  padding-left: 0;
}

.doc-anchor :deep(.el-anchor__link) {
  display: block;
  padding: 6px 12px;
  color: #606266;
  text-decoration: none;
  border-radius: 4px;
  font-size: 13px;
  line-height: 1.5;
  transition: all 0.2s;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.doc-anchor :deep(.el-anchor__link:hover) {
  background: #ecf5ff;
  color: #409eff;
}

.doc-anchor :deep(.el-anchor__link.is-active) {
  background: #ecf5ff;
  color: #409eff;
  font-weight: 500;
}

.doc-anchor :deep(.el-anchor__marker) {
  background-color: #409eff;
}

/* 目录层级缩进 */
.doc-anchor .toc-level-1 :deep(.el-anchor__link) {
  padding-left: 12px;
  font-weight: 600;
}

.doc-anchor .toc-level-2 :deep(.el-anchor__link) {
  padding-left: 24px;
}

.doc-anchor .toc-level-3 :deep(.el-anchor__link) {
  padding-left: 36px;
}

.doc-anchor .toc-level-4 :deep(.el-anchor__link) {
  padding-left: 48px;
}

.doc-anchor .toc-level-5 :deep(.el-anchor__link) {
  padding-left: 60px;
}

.doc-anchor .toc-level-6 :deep(.el-anchor__link) {
  padding-left: 72px;
}

@media (max-width: 768px) {
  .doc-content-wrapper {
    grid-template-columns: 1fr !important;
  }

  .doc-sidebar {
    position: static;
    max-height: 400px;
  }

  .right-sidebar {
    display: none;
  }

  .left-sidebar {
    order: 2;
  }

  .doc-main {
    padding: 24px 16px;
    order: 1;
  }

  .doc-title {
    font-size: 28px;
  }

  .doc-navigation {
    flex-direction: column;
  }

  .nav-link {
    max-width: 100%;
  }
}
</style>
