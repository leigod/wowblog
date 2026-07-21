<template>
  <svg
    width="24"
    height="24"
    :class="className"
    viewBox="0 0 20480 1024"
    fill="currentColor"
    xmlns="http://www.w3.org/2000/svg"
    v-bind="$attrs"
  >
    <path
      fill-rule="evenodd"
      clip-rule="evenodd"
      d="M0 0l20480 0 0 1024-20480 0 0-1024Z"
      fill="currentColor"
    />
  </svg>
</template>

<script setup>
import { defineProps } from 'vue'

const props = defineProps({ className: String })

defineExpose({})

// 保持和原组件相同的显示名称
</script>
