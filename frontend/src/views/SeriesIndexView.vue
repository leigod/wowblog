<template>
  <CollectionPage
    :kicker="t('collection.series_kicker')"
    :title="t('collection.series_title')"
    :desc="t('collection.series_desc')"
    :stats="stats"
    :items="items"
    :loading="loading"
    :loading-text="t('collection.loading')"
    :empty-text="t('collection.empty_series')"
    :empty-search-text="t('collection.empty_search')"
    :unit="t('collection.series_unit')"
    searchable
    :search-placeholder="t('collection.series_search')"
  />
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import CollectionPage from '@/components/collection/CollectionPage.vue'
import type { CollectionItem } from '@/components/collection/types'
import { getSeriesList } from '@/api/services/series'
import { getSeriesArticlesList } from '@/api/services/blog'

interface RawSeries {
  id: number
  name: string
  slug: string
  series_desc?: string | null
  image?: string | null
  articles_order?: string | null
  sort?: number
}

const { t } = useI18n()

const seriesList = ref<RawSeries[]>([])
const counts = ref<Record<string, number>>({})
const loading = ref(true)

const items = computed<CollectionItem[]>(() =>
  seriesList.value.map((item) => {
    const meta: string[] = []
    const count = counts.value[item.slug]
    if (typeof count === 'number') meta.push(`${count} ${t('collection.article_count')}`)
    // 系列天然有序：提示阅读顺序，避免用户以为按时间倒序
    meta.push(item.articles_order === 'asc' ? t('collection.order_asc') : t('collection.order_desc'))

    return {
      key: item.id,
      title: item.name,
      desc: item.series_desc || '',
      cover: item.image || '',
      letter: (item.name || '?').trim().slice(0, 1).toUpperCase(),
      to: `/series/${item.slug}`,
      meta,
      searchText: item.slug
    }
  })
)

const stats = computed(() => [
  t('collection.stats_series', { count: seriesList.value.length })
])

const loadCounts = async () => {
  const results = await Promise.allSettled(
    seriesList.value.map((item) => getSeriesArticlesList(item.slug, 1, 1))
  )
  const next: Record<string, number> = {}
  results.forEach((result, index) => {
    const item = seriesList.value[index]
    if (!item) return
    if (result.status === 'fulfilled' && result.value?.code === 1) {
      next[item.slug] = result.value.data?.total || 0
    }
  })
  counts.value = next
}

const load = async () => {
  loading.value = true
  try {
    const response = await getSeriesList()
    const list = (response.data || []) as RawSeries[]
    seriesList.value = [...list].sort(
      (a, b) => (a.sort || 0) - (b.sort || 0) || a.name.localeCompare(b.name, 'zh-Hans-CN')
    )
  } catch (error) {
    console.error('加载系列列表失败:', error)
    seriesList.value = []
  } finally {
    loading.value = false
  }
  if (seriesList.value.length) void loadCounts()
}

onMounted(load)

defineOptions({ name: 'SeriesIndexView' })
</script>
