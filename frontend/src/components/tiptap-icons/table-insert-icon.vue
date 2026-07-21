<template>
  <svg
    width="24"
    height="24"
    :class="className"
    viewBox="0 0 1024 1024"
    fill="currentColor"
    xmlns="http://www.w3.org/2000/svg"
    v-bind="$attrs"
  >
    <path
      fill-rule="evenodd"
      clip-rule="evenodd"
      d="M928 64H96a32 32 0 0 0-32 32v832a32 32 0 0 0 32 32h432a32 32 0 0 0 0-64h-128V720h96a32 32 0 0 0 0-64h-96v-144h496v48a32 32 0 0 0 64 0V96a32 32 0 0 0-32-32zM128 256h208v192H128V256z m208 640H128V720h208v176z m0-240H128v-144h208v144z m64-400h208v192H400V256z m272 192V256h224v192H672z m256 272H653.28l73.44-73.44a32.016 32.016 0 0 0-45.28-45.28l-128 128a32 32 0 0 0-4 4.96s-0.8 1.6-1.28 2.4a18.72 18.72 0 0 0-2.72 6.4c0 0.96 0 1.76-0.8 2.72a32 32 0 0 0 0 12.48c0 0.96 0 1.92 0.8 2.72 0.496 2.288 1.424 4.448 2.72 6.4 0 0 0 1.6 1.28 2.4a32 32 0 0 0 4 4.96l128 128a32.016 32.016 0 0 0 45.28-45.28L653.28 784H928a32 32 0 0 0 0-64z"
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
