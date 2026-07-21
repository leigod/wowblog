<template>
  <div class="mention-list">
    <template v-if="items.length > 0">
      <div
        v-for="(item, index) in items"
        :key="item.id"
        class="mention-item"
        :class="{ 'is-selected': index === selectedIndex }"
        @click="selectItem(index)"
      >
        <img :src="item.avatar" class="mention-avatar" />
        <div class="mention-info">
          <span class="mention-full-name">{{ item.name }}</span>
          <span class="mention-username">@{{ item.username }}</span>
        </div>
      </div>
    </template>
    <div v-else class="mention-empty">
      没有找到用户
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  items: {
    type: Array,
    required: true
  },
  command: {
    type: Function,
    required: true
  }
})

const selectedIndex = ref(0)

const selectItem = (index) => {
  const item = props.items[index]
  if (item) {
    props.command(item)
  }
}

const onKeyDown = ({ event }) => {
  if (event.key === 'ArrowUp') {
    selectedIndex.value = (selectedIndex.value - 1 + props.items.length) % props.items.length
    return true
  }

  if (event.key === 'ArrowDown') {
    selectedIndex.value = (selectedIndex.value + 1) % props.items.length
    return true
  }

  if (event.key === 'Enter') {
    selectItem(selectedIndex.value)
    return true
  }

  return false
}

watch(() => props.items, () => {
  selectedIndex.value = 0
})

defineExpose({
  onKeyDown
})
</script>

<style scoped>
.mention-list {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  max-height: 250px;
  overflow-y: auto;
  padding: 4px 0;
}

.mention-item {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.mention-item:hover,
.mention-item.is-selected {
  background-color: var(--el-fill-color-light);
}

.mention-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  margin-right: 12px;
  object-fit: cover;
}

.mention-info {
  display: flex;
  flex-direction: column;
}

.mention-full-name {
  font-size: 14px;
  color: var(--el-text-color-primary);
  font-weight: 500;
}

.mention-username {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 2px;
}

.mention-empty {
  padding: 12px 16px;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}
</style>
