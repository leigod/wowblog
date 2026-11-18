<template>
  <CollectionPage
    :kicker="t('collection.categories_kicker')"
    :title="t('collection.categories_title')"
    :desc="t('collection.categories_desc')"
    :stats="stats"
    :items="items"
    :loading="loading"
    :loading-text="t('collection.loading')"
    :empty-text="t('collection.empty_categories')"
    :empty-search-text="t('collection.empty_search')"
    :unit="t('collection.category_unit')"
    searchable
    :search-placeholder="t('collection.categories_search')"
  />
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import CollectionPage from '@/components/collection/CollectionPage.vue'
import type { CollectionChip, CollectionItem } from '@/components/collection/types'
import { getCategoryList } from '@/api/services/categories'
import { getCategoryArticlesList } from '@/api/services/blog'

interface RawCategory {
  id: number
  name: string
  slug: string
  pid: number
  cat_desc?: string | null
  image?: string | null
  sort?: number
}

const { t } = useI18n()

const categories = ref<RawCategory[]>([])
const counts = ref<Record<string, number>>({})
const loading = ref(true)

const MAX_CHIPS = 6

const childMap = computed(() => {
  const map = new Map<number, RawCategory[]>()
  for (const cat of categories.value) {
    const list = map.get(cat.pid) || []
    list.push(cat)
    map.set(cat.pid, list)
  }
  return map
})

// 有子分类的挂到父卡片上当入口；父级找不到的（脏数据）当一级处理
const roots = computed(() => {
  const ids = new Set(categories.value.map((c) => c.id))
  const top = categories.value.filter((c) => !c.pid || !ids.has(c.pid))
  const sortFn = (a: RawCategory, b: RawCategory) =>
    (a.sort || 0) - (b.sort || 0) || a.name.localeCompare(b.name, 'zh-Hans-CN')
  return [...top].sort(sortFn)
})

// 把父分类下的所有后代拍平成 chip（最多 6 个，超出只给计数）
const flattenDescendants = (parentId: number, acc: RawCategory[] = []): RawCategory[] => {
  const children = childMap.value.get(parentId) || []
  for (const child of children) {
    acc.push(child)
    flattenDescendants(child.id, acc)
  }
  return acc
}

// 含自身 + 全部后代的文章数。任一分类的计数还没回填就返回 null，避免报出假数字
const subtreeCount = (cat: RawCategory, descendants: RawCategory[]): number | null => {
  let sum = 0
  for (const node of [cat, ...descendants]) {
    const n = counts.value[node.slug]
    if (typeof n !== 'number') return null
    sum += n
  }
  return sum
}

const items = computed<CollectionItem[]>(() =>
  roots.value.map((cat) => {
    const descendants = flattenDescendants(cat.id)
    const chips: CollectionChip[] = descendants.slice(0, MAX_CHIPS).map((child) => ({
      key: child.id,
      label: child.name,
      to: `/category/${child.slug}`
    }))
    if (descendants.length > MAX_CHIPS) {
      chips.push({
        key: `more-${cat.id}`,
        label: `+${descendants.length - MAX_CHIPS}`,
        to: `/category/${cat.slug}`
      })
    }

    const meta: string[] = []
    const own = counts.value[cat.slug]
    if (typeof own === 'number') {
      if (own > 0) {
        // 自身有文章：报直收数，和点进去看到的列表一致
        meta.push(`${own} ${t('collection.article_count')}`)
      } else if (descendants.length) {
        // 自身没文章但子级有：报含子级总数，避免看起来像空分类
        const total = subtreeCount(cat, descendants)
        meta.push(
          typeof total === 'number' && total > 0
            ? t('collection.article_count_with_children', { count: total })
            : `${own} ${t('collection.article_count')}`
        )
      } else {
        meta.push(`${own} ${t('collection.article_count')}`)
      }
    }
    if (descendants.length) meta.push(`${descendants.length} ${t('collection.sub_count')}`)

    return {
      key: cat.id,
      title: cat.name,
      desc: cat.cat_desc || '',
      cover: cat.image || '',
      letter: (cat.name || '?').trim().slice(0, 1).toUpperCase(),
      to: `/category/${cat.slug}`,
      meta,
      chips,
      searchText: [cat.slug, ...descendants.map((d) => d.name)].join(' ')
    }
  })
)

const stats = computed(() => [
  t('collection.stats_categories', {
    total: categories.value.length,
    roots: roots.value.length
  })
])

// 单分类文章数：只取 1 条，读 total，用于卡片元信息
const loadCounts = async () => {
  const results = await Promise.allSettled(
    categories.value.map((cat) => getCategoryArticlesList(cat.slug, 1, 1))
  )
  const next: Record<string, number> = {}
  results.forEach((result, index) => {
    const cat = categories.value[index]
    if (!cat) return
    if (result.status === 'fulfilled' && result.value?.code === 1) {
      next[cat.slug] = result.value.data?.total || 0
    }
  })
  counts.value = next
}

const load = async () => {
  loading.value = true
  try {
    const response = await getCategoryList()
    categories.value = (response.data || []) as RawCategory[]
  } catch (error) {
    console.error('加载分类列表失败:', error)
    categories.value = []
  } finally {
    loading.value = false
  }
  if (categories.value.length) void loadCounts()
}

onMounted(load)

defineOptions({ name: 'CategoryIndexView' })
</script>
