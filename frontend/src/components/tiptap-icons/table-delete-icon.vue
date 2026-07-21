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
      d="M776.464 753.136l90.496-90.512a32 32 0 0 1 45.264 45.264l-90.512 90.496 90.512 90.512a32 32 0 0 1-45.264 45.264l-90.496-90.512-90.512 90.512a32 32 0 1 1-45.264-45.264L731.2 798.4l-90.512-90.496a32 32 0 1 1 45.264-45.264l90.512 90.512zM608 512H400v144h96a32 32 0 0 1 0 64h-96v176h128a32 32 0 0 1 0 64H96a32 32 0 0 1-32-32V96a32 32 0 0 1 32-32h832a32 32 0 0 1 32 32v464a32 32 0 0 1-64 0v-48H672v48a32 32 0 1 1-64 0v-48zM128 256v192h208V256H128z m208 640V720H128v176h208z m0-240v-144H128v144h208z m64-400v192h208V256H400z m272 192h224V256H672v192z"
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
