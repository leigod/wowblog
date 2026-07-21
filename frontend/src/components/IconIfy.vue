<template>
  <div>
    <Icon :icon="icon" :width="width ? width : '24'" :height="height ? height : '24'" :inline="inline ? true : false"
      :color="color ? color : ''" :style="size ? { fontSize: size + 'px' } : {}"
      :stroke-width="strokeWidth ? strokeWidth : '0.5'" :stroke="stroke ? stroke : 'currentColor'" />
  </div>
</template>

<script setup lang="ts">
import { Icon } from '@iconify/vue'

interface Props {
  icon: string
  width?: string | number
  height?: string | number
  inline?: boolean
  color?: string
  size?: string | number
  strokeWidth?: string | number
  stroke?: string
}

defineProps<Props>()

// 添加组件名称
defineOptions({
  name: 'IconifyIcon'
})
</script>
