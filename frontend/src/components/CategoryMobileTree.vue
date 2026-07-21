<template>
  <el-card
    :class="['mobile-category-card', depth > 0 ? 'child-card' : '']"
    :style="{ marginLeft: depth > 0 ? (depth * 12) + 'px' : '0' }"
  >
    <div class="category-card-header">
      <div class="category-title">
        <el-image
          v-if="category.coverImage"
          :src="category.coverImage"
          alt="封面"
          class="category-cover"
          :preview-src-list="[category.coverImage]"
          preview-teleported
        />
        <div v-else class="category-cover-placeholder">
          <el-icon><Folder /></el-icon>
        </div>
        <div class="category-info">
          <h3>{{ category.name }}</h3>
          <p v-if="category.description">{{ category.description }}</p>
        </div>
      </div>
    </div>

    <div class="category-card-body">
      <div class="info-row">
        <span class="label">{{ $t('admin.category.table.head.slug') }}:</span>
        <span class="value">/{{ category.slug }}</span>
      </div>
      <div class="info-row">
        <span class="label">{{ $t('admin.category.table.head.parent') }}:</span>
        <span class="value">{{ category.parentName || $t('admin.category.table.no_parent') }}</span>
      </div>
      <div class="info-row">
        <span class="label">{{ $t('admin.category.table.head.order') }}:</span>
        <el-select v-model="localArticleSort" size="small" @change="handleSortChange">
          <el-option :label="$t('admin.category.table.head.order_new')" value="newest"></el-option>
          <el-option :label="$t('admin.category.table.head.order_hot')" value="hottest"></el-option>
          <el-option :label="$t('admin.category.table.head.order_pubtime')" value="oldest"></el-option>
        </el-select>
      </div>
      <div class="info-row">
        <span class="label">{{ $t('admin.category.table.head.weight') }}:</span>
        <span class="value">{{ category.sort }}</span>
      </div>
    </div>

    <template #footer>
      <div class="category-card-actions">
        <el-button @click="$emit('edit', category)" size="small">
          <el-icon><Edit /></el-icon>
        </el-button>
        <el-button @click="$emit('delete', category)" type="danger" size="small">
          <el-icon><Delete /></el-icon>
        </el-button>
      </div>
    </template>

    <!-- 递归渲染子分类 -->
    <template v-if="category.children && category.children.length > 0">
      <div class="children-container">
        <CategoryMobileTree
          v-for="child in category.children"
          :key="child.id"
          :category="child"
          :depth="depth + 1"
          @edit="$emit('edit', $event)"
          @delete="$emit('delete', $event)"
          @sort-change="$emit('sort-change', $event)"
        />
      </div>
    </template>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Folder, Edit, Delete } from '@element-plus/icons-vue'

// 定义分类数据接口
interface Category {
  id: number
  name: string
  parentId: number | null
  parentName?: string
  description: string
  slug: string
  coverImage: string | null
  articleSort: 'newest' | 'hottest' | 'oldest'
  sort: number
  children?: Category[]
}

// Props 定义
const props = defineProps<{
  category: Category
  depth: number
}>()

// Emits 定义
const emit = defineEmits<{
  edit: [category: Category]
  delete: [category: Category]
  'sort-change': [category: Category]
}>()

// 本地状态用于排序选择，避免直接修改 props
const localArticleSort = computed({
  get: () => props.category.articleSort,
  set: () => {
    // 触发排序变更事件，但不直接修改 props
  }
})

// 处理排序变更
const handleSortChange = () => {
  emit('sort-change', props.category)
}
</script>

<style scoped lang="scss">
.mobile-category-card {
  margin-bottom: 12px;
  border-radius: 8px;

  :deep(.el-card__body) {
    padding: 16px;
  }
}

.child-card {
  border-left: 3px solid var(--el-color-primary);
}

.category-card-header {
  margin-bottom: 16px;
}

.category-title {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.category-cover {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  object-fit: cover;
  flex-shrink: 0;
}

.category-cover-placeholder {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  background: var(--el-fill-color-light);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: var(--el-text-color-placeholder);
}

.category-info {
  flex: 1;
  min-width: 0;
}

.category-info h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.category-info p {
  margin: 0;
  font-size: 14px;
  color: var(--el-text-color-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.category-card-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
}

.info-row .label {
  color: var(--el-text-color-secondary);
  flex-shrink: 0;
  margin-right: 8px;
}

.info-row .value {
  color: var(--el-text-color-primary);
  text-align: right;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.info-row .el-select {
  width: auto;
  flex-shrink: 0;
}

.category-card-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.children-container {
  margin-top: 8px;
}
</style>
