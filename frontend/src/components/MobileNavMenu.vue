<template>
  <div class="mobile-nav-menu">
    <div v-for="item in navItems" :key="item.id" class="nav-item"
      :class="{ 'has-children': item.children && item.children.length > 0 }">
      <!-- 一级菜单项 -->
      <div class="nav-item-header" :class="{ 'is-disabled': item.children && item.children.length > 0 }"
        @click="handleItemClick(item)">
        <span class="nav-icon" v-if="item.children && item.children.length > 0">
          <el-icon>
            <component :is="expandedItems[item.id] ? ArrowDown : ArrowRight" />
          </el-icon>
        </span>
        <span class="nav-label">{{ item.label || item.name || 'Untitled' }}</span>
      </div>

      <!-- 子菜单（递归） -->
      <transition name="expand">
        <div v-if="item.children && item.children.length > 0 && expandedItems[item.id]" class="nav-children">
          <MobileNavMenu :nav-items="item.children" :depth="depth + 1" @item-click="handleChildClick" />
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { ArrowRight, ArrowDown } from '@element-plus/icons-vue'

// 定义导航项类型
export interface NavItem {
  id: number | string
  label?: string
  name?: string
  url?: string
  slug?: string
  value?: string
  children?: NavItem[]
  [key: string]: any
}

// Props
withDefaults(defineProps<{
  navItems: NavItem[]
  depth?: number
}>(), {
  depth: 0
})

// Emits
const emit = defineEmits<{
  'item-click': [item: NavItem]
}>()

// 展开状态
const expandedItems = reactive<Record<string, boolean>>({})

// 处理项目点击
const handleItemClick = (item: NavItem) => {
  if (item.children && item.children.length > 0) {
    // 切换展开状态
    expandedItems[item.id] = !expandedItems[item.id]
  } else {
    // 发出点击事件
    emit('item-click', item)
  }
}

// 处理子菜单点击
const handleChildClick = (item: NavItem) => {
  emit('item-click', item)
}
</script>

<style scoped lang="scss">
.mobile-nav-menu {
  .nav-item {
    .nav-item-header {
      display: flex;
      align-items: center;
      padding: 12px 16px;
      cursor: pointer;
      transition: background-color 0.2s;
      user-select: none;

      &:hover {
        color: var(--el-color-primary);
        background-color: var(--el-menu-hover-bg-color);
      }

      &.is-disabled {
        opacity: 0.7;
        font-weight: 500;
      }

      .nav-icon {
        margin-right: 8px;
        color: var(--el-color-info);
      }

      .nav-label {
        flex: 1;
      }
    }

    .nav-children {
      margin-left: 0;
      background-color: var(--el-fill-color-lighter);
      border-radius: 4px;
      margin-top: 4px;
      margin-bottom: 4px;
      overflow: hidden;
    }

    &.has-children {
      .nav-item-header {
        .nav-icon {
          transition: transform 0.2s;
        }
      }
    }
  }
}

// 展开动画
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
  max-height: 1000px;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
}
</style>
