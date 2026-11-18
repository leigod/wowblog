<template>
  <div class="collection-page">
    <!-- 页头：分类/系列/文档三种目录共用同一套排版 -->
    <header class="collection-hero">
      <p class="collection-kicker">{{ kicker }}</p>
      <h1 class="collection-title">{{ title }}</h1>
      <p v-if="desc" class="collection-desc">{{ desc }}</p>
      <div v-if="stats.length" class="collection-stats">
        <template v-for="(s, i) in stats" :key="s">
          <span v-if="i" class="dot">·</span>
          <span>{{ s }}</span>
        </template>
      </div>
    </header>

    <div v-if="searchable" class="collection-toolbar">
      <el-input
        v-model="keyword"
        :prefix-icon="Search"
        :placeholder="searchPlaceholder"
        clearable
        class="collection-search"
      />
      <span class="collection-count">{{ filtered.length }} {{ unit }}</span>
    </div>

    <p v-if="loading" class="collection-state">{{ loadingText }}</p>

    <template v-else>
      <div v-if="filtered.length" class="collection-grid">
        <div
          v-for="item in filtered"
          :key="item.key"
          class="collection-card"
          role="link"
          tabindex="0"
          @click="open(item.to)"
          @keydown.enter="open(item.to)"
          @keydown.space.prevent="open(item.to)"
        >
          <div class="card-cover" :class="{ 'has-image': item.cover }">
            <img v-if="item.cover" :src="item.cover" :alt="item.title" loading="lazy" />
            <span v-else class="card-letter">{{ item.letter }}</span>
          </div>

          <div class="card-body">
            <h2 class="card-title" :title="item.title">{{ item.title }}</h2>
            <p v-if="item.desc" class="card-desc">{{ item.desc }}</p>
            <div v-if="item.meta && item.meta.length" class="card-meta">
              <template v-for="(m, i) in item.meta" :key="m">
                <span v-if="i" class="dot">·</span>
                <span>{{ m }}</span>
              </template>
            </div>

            <div v-if="item.chips && item.chips.length" class="card-chips">
              <router-link
                v-for="chip in item.chips"
                :key="chip.key"
                :to="chip.to"
                class="chip"
                @click.stop
              >
                {{ chip.label }}
              </router-link>
            </div>
          </div>

          <el-icon class="card-arrow"><ArrowRight /></el-icon>
        </div>
      </div>

      <p v-else class="collection-state">{{ keyword ? emptySearchText : emptyText }}</p>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowRight, Search } from '@element-plus/icons-vue'
import type { CollectionItem } from './types'

const props = withDefaults(
  defineProps<{
    kicker: string
    title: string
    desc?: string
    stats?: string[]
    items: CollectionItem[]
    loading?: boolean
    loadingText?: string
    emptyText?: string
    emptySearchText?: string
    searchable?: boolean
    searchPlaceholder?: string
    unit?: string
  }>(),
  {
    desc: '',
    stats: () => [],
    loading: false,
    loadingText: '加载中...',
    emptyText: '这里还没有内容',
    emptySearchText: '没有匹配的结果',
    searchable: false,
    searchPlaceholder: '搜索',
    unit: '项'
  }
)

const router = useRouter()
const keyword = ref('')

const filtered = computed(() => {
  const kw = keyword.value.trim().toLowerCase()
  if (!kw) return props.items
  return props.items.filter((item) => {
    const haystack = [item.title, item.desc || '', item.searchText || '']
      .join(' ')
      .toLowerCase()
    return haystack.includes(kw)
  })
})

const open = (to: string) => {
  router.push(to)
}
</script>

<style scoped>
.collection-page {
  /* .el-main 是 flex 容器：不写 width:100% 会被内容宽度压缩 */
  width: 100%;
  max-width: 1120px;
  box-sizing: border-box;
  margin: 0 auto;
  padding: 36px 24px 88px;
}

/* ---------- 页头 ---------- */
.collection-hero {
  margin-bottom: 28px;
}

.collection-kicker {
  margin: 0 0 8px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--wy-brand);
}

.collection-title {
  margin: 0 0 10px;
  font-size: 30px;
  line-height: 1.25;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: var(--wy-text-primary);
}

.collection-desc {
  margin: 0 0 12px;
  max-width: 62ch;
  font-size: 15px;
  line-height: 1.7;
  color: var(--wy-text-secondary);
}

.collection-stats {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--wy-text-tertiary);
}

.dot {
  color: var(--wy-text-placeholder);
}

/* ---------- 工具条 ---------- */
.collection-toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--wy-border-subtle);
}

.collection-search {
  max-width: 320px;
}

.collection-count {
  margin-left: auto;
  font-size: 13px;
  color: var(--wy-text-tertiary);
  white-space: nowrap;
}

/* ---------- 卡片网格 ---------- */
.collection-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 16px;
}

.collection-card {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  min-height: 116px;
  padding: 18px;
  background: var(--wy-bg-surface);
  border: 1px solid var(--wy-border-subtle);
  border-radius: var(--wy-radius-md);
  cursor: pointer;
  transition: border-color var(--wy-duration) var(--wy-easing),
    box-shadow var(--wy-duration) var(--wy-easing),
    transform var(--wy-duration) var(--wy-easing);
}

.collection-card:hover,
.collection-card:focus-visible {
  border-color: var(--wy-border-strong);
  box-shadow: var(--wy-shadow-card-hover);
  transform: translateY(-2px);
  outline: none;
}

.card-cover {
  flex: none;
  width: 54px;
  height: 70px;
  border-radius: var(--wy-radius-sm);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--wy-brand-soft);
  color: var(--wy-brand);
  font-size: 22px;
  font-weight: 700;
}

.card-cover.has-image {
  background: var(--wy-bg-muted);
}

.card-cover img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-body {
  flex: 1;
  min-width: 0;
}

.card-title {
  margin: 0 0 6px;
  font-size: 16px;
  line-height: 1.4;
  font-weight: 600;
  color: var(--wy-text-primary);
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  transition: color var(--wy-duration) var(--wy-easing);
}

.collection-card:hover .card-title {
  color: var(--wy-brand);
}

.card-desc {
  margin: 0 0 10px;
  /* 两行等高：卡片高度不随简介长度跳动 */
  min-height: 3em;
  font-size: 13px;
  line-height: 1.5;
  color: var(--wy-text-tertiary);
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  overflow: hidden;
}

.card-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--wy-text-placeholder);
}

.card-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 10px;
}

.chip {
  display: inline-flex;
  align-items: center;
  max-width: 100%;
  padding: 2px 9px;
  font-size: 12px;
  color: var(--wy-text-secondary);
  text-decoration: none;
  background: var(--wy-bg-muted);
  border-radius: var(--wy-radius-pill);
  transition: color var(--wy-duration) var(--wy-easing),
    background-color var(--wy-duration) var(--wy-easing);
}

.chip:hover {
  color: var(--wy-brand);
  background: var(--wy-brand-soft);
}

.card-arrow {
  flex: none;
  margin-top: 2px;
  font-size: 16px;
  color: var(--wy-text-placeholder);
  opacity: 0;
  transform: translateX(-4px);
  transition: opacity var(--wy-duration) var(--wy-easing),
    transform var(--wy-duration) var(--wy-easing),
    color var(--wy-duration) var(--wy-easing);
}

.collection-card:hover .card-arrow {
  opacity: 1;
  transform: translateX(0);
  color: var(--wy-brand);
}

.collection-state {
  margin: 0;
  padding: 64px 0;
  text-align: center;
  font-size: 14px;
  color: var(--wy-text-tertiary);
}

/* ---------- 响应式 ---------- */
@media (max-width: 768px) {
  .collection-page {
    padding: 22px 16px 56px;
  }

  .collection-title {
    font-size: 23px;
  }

  .collection-grid {
    grid-template-columns: 1fr;
  }

  .collection-card {
    min-height: 0;
    padding: 14px;
    gap: 12px;
  }

  .card-cover {
    width: 44px;
    height: 58px;
    font-size: 18px;
  }

  .card-arrow {
    display: none;
  }

  .collection-toolbar {
    flex-wrap: wrap;
  }

  .collection-search {
    max-width: none;
    flex: 1 1 100%;
  }
}
</style>
