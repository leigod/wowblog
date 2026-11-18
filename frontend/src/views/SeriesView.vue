<template>
  <TaxonomyPage
    :kicker="t('taxonomy.kicker_series')"
    :title="seriesDetail.name || ''"
    :desc="seriesDetail.series_desc || ''"
    :cover="seriesDetail.image || ''"
    :total="total"
    :crumbs="crumbs"
    :articles="seriesArticlesList"
    :loading="loading"
    :has-more="hasMore"
    numbered
    :list-title="t('taxonomy.list_title_series')"
    :cta-text="t('taxonomy.read_first')"
    :start-to="startTo"
    @load-more="loadMore"
  />
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { getSeriesDetailApi, getSeriesArticlesList } from '@/api/services/blog'
import { ElMessage } from 'element-plus'
import TaxonomyPage from '@/components/collection/TaxonomyPage.vue'
import type { TaxonomyCrumb } from '@/components/collection/types'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const appStore = useAppStore()

const seriesDetail = ref<any>({})
const seriesArticlesList = ref<any[]>([])

// 分页相关状态
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const loading = ref(false)
const hasMore = ref(true)

const crumbs = computed<TaxonomyCrumb[]>(() => [
  { label: t('taxonomy.home'), to: '/' },
  { label: t('taxonomy.index_series'), to: '/series' },
  { label: seriesDetail.value.name || '' }
])

// 系列是线性阅读的，给一个「从第 1 篇开始」的入口
const startTo = computed(() => {
  const first = seriesArticlesList.value[0]
  return first?.slug ? `/article/${first.slug}` : ''
})

const fetchArticles = async (page: number, size: number, append: boolean = false) => {
  const seriesSlug = route.params.seriesSlug as string
  loading.value = true

  try {
    const articlesRes = await getSeriesArticlesList(seriesSlug, page, size)

    if (articlesRes.code === 1) {
      const newArticles = articlesRes.data.list || []

      if (append) {
        seriesArticlesList.value = [...seriesArticlesList.value, ...newArticles]
      } else {
        seriesArticlesList.value = newArticles
      }

      total.value = articlesRes.data.total || 0

      if (seriesArticlesList.value.length >= total.value || newArticles.length < size) {
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

const setPageSEO = (detail: any) => {
  if (!detail?.name) return
  const title = detail.name
  const description = detail.series_desc || ''
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

const loadDetail = async () => {
  const seriesSlug = route.params.seriesSlug as string
  try {
    const res = await getSeriesDetailApi(seriesSlug)
    if (res.code === 1) {
      seriesDetail.value = res.data
      setPageSEO(res.data)
      return true
    }
    ElMessage.error(t('taxonomy.load_failed'))
    router.push({ name: 'empty' })
    return false
  } catch (error) {
    console.error('加载系列内容出错:', error)
    ElMessage.error(t('taxonomy.load_failed'))
    router.push({ name: 'empty' })
    return false
  }
}

onMounted(async () => {
  const ok = await loadDetail()
  if (ok) await initArticles()
})

watch(
  () => route.params.seriesSlug,
  async (newSlug, oldSlug) => {
    if (newSlug === oldSlug) return
    const ok = await loadDetail()
    if (ok) await initArticles()
  }
)

defineOptions({ name: 'SeriesView' })
</script>
