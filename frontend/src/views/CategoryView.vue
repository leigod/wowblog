<template>
  <TaxonomyPage
    :kicker="t('taxonomy.kicker_category')"
    :title="categoryDetail.name || ''"
    :desc="categoryDetail.cat_desc || ''"
    :cover="categoryDetail.image || ''"
    :total="total"
    :crumbs="crumbs"
    :children="childCategories"
    :articles="categoryArticlesList"
    :loading="loading"
    :has-more="hasMore"
    layout="grid"
    wide
    :list-title="t('taxonomy.list_title_category')"
    @load-more="loadMore"
  />
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { getCategoryDetailApi, getCategoryArticlesList } from '@/api/services/blog'
import { getCategoryList } from '@/api/services/categories'
import { ElMessage } from 'element-plus'
import TaxonomyPage from '@/components/collection/TaxonomyPage.vue'
import type { TaxonomyChild, TaxonomyCrumb } from '@/components/collection/types'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const appStore = useAppStore()

const categoryDetail = ref<any>({})
const categoryArticlesList = ref<any[]>([])
const allCategories = ref<any[]>([])

// 分页相关状态
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const loading = ref(false)
const hasMore = ref(true)

// 面包屑：首页 / 分类 / 父级… / 当前（多级分类才看得出自己在哪一层）
const crumbs = computed<TaxonomyCrumb[]>(() => {
  const list: TaxonomyCrumb[] = [
    { label: t('taxonomy.home'), to: '/' },
    { label: t('taxonomy.index_category'), to: '/category' }
  ]

  const chain: any[] = []
  let node = allCategories.value.find((c) => c.slug === categoryDetail.value.slug)
  let guard = 0
  while (node && guard < 6) {
    chain.unshift(node)
    const pid = node.pid
    node = pid ? allCategories.value.find((c) => c.id === pid) : null
    guard += 1
  }

  if (chain.length > 1) {
    chain.slice(0, -1).forEach((c) => list.push({ label: c.name, to: `/category/${c.slug}` }))
  }
  list.push({ label: categoryDetail.value.name || '' })
  return list.filter((c) => c.label)
})

// 子分类入口：父分类自己可能没有直收文章（文章都挂在子级），给出下一跳
const childCategories = computed<TaxonomyChild[]>(() => {
  const id = Number(categoryDetail.value?.id || 0)
  if (!id) return []
  return allCategories.value
    .filter((c) => Number(c.pid) === id)
    .sort(
      (a, b) => (a.sort || 0) - (b.sort || 0) || String(a.name).localeCompare(String(b.name), 'zh-Hans-CN')
    )
    .map((c) => ({ label: c.name, to: `/category/${c.slug}` }))
})

const fetchArticles = async (page: number, size: number, append: boolean = false) => {  const categorySlug = route.params.categorySlug as string
  loading.value = true

  try {
    const articlesRes = await getCategoryArticlesList(categorySlug, page, size)

    if (articlesRes.code === 1) {
      const newArticles = articlesRes.data.list || []

      if (append) {
        categoryArticlesList.value = [...categoryArticlesList.value, ...newArticles]
      } else {
        categoryArticlesList.value = newArticles
      }

      total.value = articlesRes.data.total || 0

      if (categoryArticlesList.value.length >= total.value || newArticles.length < size) {
        hasMore.value = false
      } else {
        hasMore.value = true
      }
    } else {
      ElMessage.error(t('taxonomy.load_failed'))
    }
  } catch (error) {
    console.error('加载文章列表出错:', error)
    ElMessage.error(t('taxonomy.load_failed'))
  } finally {
    loading.value = false
  }
}

const loadMore = async () => {
  currentPage.value++
  await fetchArticles(currentPage.value, pageSize.value, true)
}

const initArticles = async () => {
  currentPage.value = 1
  await fetchArticles(currentPage.value, pageSize.value, false)
}

// 动态设置浏览器标题与分享标签
const setPageSEO = (detail: any) => {
  if (!detail?.name) return
  const title = detail.name
  const description = detail.cat_desc || ''
  const imageUrl = detail.image || ''

  document.title = title + ' - ' + appStore.site_title || '默认标题'

  const metaDesc = document.querySelector('meta[name="description"]')
  if (metaDesc) {
    metaDesc.setAttribute('content', description)
  } else {
    const newMetaDesc = document.createElement('meta')
    newMetaDesc.name = 'description'
    newMetaDesc.content = description
    document.head.appendChild(newMetaDesc)
  }

  document.querySelector('meta[property="og:title"]')?.setAttribute('content', title)
  document.querySelector('meta[property="og:description"]')?.setAttribute('content', description)
  if (imageUrl) {
    document.querySelector('meta[property="og:image"]')?.setAttribute('content', imageUrl)
  }

  document.querySelector('meta[name="twitter:title"]')?.setAttribute('content', title)
  document.querySelector('meta[name="twitter:description"]')?.setAttribute('content', description)
  if (imageUrl) {
    document.querySelector('meta[name="twitter:image"]')?.setAttribute('content', imageUrl)
  }
}

// 分类层级只在首次进入时取一次，供面包屑使用
const loadCategoryTree = async () => {
  try {
    const response = await getCategoryList()
    allCategories.value = response.data || []
  } catch {
    allCategories.value = []
  }
}

const loadDetail = async () => {
  const categorySlug = route.params.categorySlug as string
  try {
    const res = await getCategoryDetailApi(categorySlug)
    if (res.code === 1) {
      categoryDetail.value = res.data
      setPageSEO(res.data)
      return true
    }
    ElMessage.error(t('taxonomy.load_failed'))
    router.push({ name: 'empty' })
    return false
  } catch (error) {
    console.error('加载分类内容出错:', error)
    ElMessage.error(t('taxonomy.load_failed'))
    router.push({ name: 'empty' })
    return false
  }
}

onMounted(async () => {
  void loadCategoryTree()
  const ok = await loadDetail()
  if (ok) await initArticles()
})

watch(
  () => route.params.categorySlug,
  async (newSlug, oldSlug) => {
    if (newSlug === oldSlug) return
    await initArticles()
    await loadDetail()
  }
)

defineOptions({ name: 'CategoryView' })
</script>
