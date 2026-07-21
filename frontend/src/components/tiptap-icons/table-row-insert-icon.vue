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
      d="M96 320h575.936c35.392 0 64-28.672 64-63.936V128.064c0-35.328-28.608-64-64-64H96c-35.392 0-64 28.672-64 64v128c0 35.264 28.608 63.936 64 63.936z m447.936-191.936h128v128H543.936V128.064z m-256 0h192v128H287.936V128.064z m-191.936 0h128v128H96V128.064z m575.936 383.936H96c-35.392 0-64 28.672-64 64v319.936c0 35.392 28.608 64 64 64h575.936c35.392 0 64-28.608 64-64V576c0-35.328-28.608-64-64-64z m-447.936 383.936H96v-128h128v128z m0-191.936H96V576h128v128z m255.936 191.936H287.936v-128h192v128z m0-191.936H287.936V576h192v128z m192 191.936H543.936v-128h128v128z m0-191.936H543.936V576h128v128z m251.776-440.576l-168.192 112.448c-27.712 18.624-27.712 61.76 0 80.384l168.192 112.512c29.696 19.84 68.288-2.816 68.288-40.192V303.552c0-37.312-38.656-59.968-68.288-40.128z"
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
