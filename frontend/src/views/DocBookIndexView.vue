<template>
  <CollectionPage
    :kicker="t('collection.docs_kicker')"
    :title="t('collection.docs_title')"
    :desc="t('collection.docs_desc')"
    :stats="stats"
    :items="items"
    :loading="loading"
    :loading-text="t('collection.loading')"
    :empty-text="t('collection.empty_books')"
    :empty-search-text="t('collection.empty_search')"
    :unit="t('collection.book_unit')"
    searchable
    :search-placeholder="t('collection.docs_search')"
  />
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import CollectionPage from '@/components/collection/CollectionPage.vue'
import type { CollectionItem } from '@/components/collection/types'
import { docBookApi, type DocBook } from '@/api'

const { t } = useI18n()

const books = ref<DocBook[]>([])
const loading = ref(true)

const formatDate = (ts?: number) => {
  if (!ts) return ''
  const d = new Date(ts * 1000)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

const items = computed<CollectionItem[]>(() =>
  books.value.map((book) => {
    const meta = [`${book.doc_count || 0} ${t('doc.articles_count')}`]
    if (book.author_name) meta.push(book.author_name)
    const updated = formatDate(book.updatetime)
    if (updated) meta.push(`${t('doc.updated')} ${updated}`)

    return {
      key: book.id,
      title: book.name,
      desc: book.description || '',
      cover: book.cover || '',
      letter: (book.name || '?').trim().slice(0, 1).toUpperCase(),
      to: `/docs/${book.slug}`,
      meta,
      searchText: book.slug
    }
  })
)

const stats = computed(() => {
  const totalDocs = books.value.reduce((sum, b) => sum + (b.doc_count || 0), 0)
  return [t('collection.stats_books', { books: books.value.length, docs: totalDocs })]
})

const load = async () => {
  loading.value = true
  try {
    const response = await docBookApi.list({ skip: 0, limit: 100 })
    const list = response.data || []
    // 后台排序值优先，其次最近更新的靠前
    books.value = [...list].sort(
      (a, b) => (a.sort_order || 0) - (b.sort_order || 0) || (b.updatetime || 0) - (a.updatetime || 0)
    )
  } catch (error) {
    console.error('加载文档书列表失败:', error)
    books.value = []
  } finally {
    loading.value = false
  }
}

onMounted(load)

defineOptions({ name: 'DocBookIndexView' })
</script>
