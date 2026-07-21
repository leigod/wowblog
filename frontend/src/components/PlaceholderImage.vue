<template>
  <div class="placeholder-image" :style="{ width: width, height: height, backgroundColor: bgColor }">
    <svg viewBox="0 0 800 460" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
      <rect width="800" height="460" :fill="bgColor" />
      <g opacity="0.3">
        <rect x="200" y="100" width="400" height="260" :fill="strokeColor" rx="8" />
        <circle cx="400" cy="190" r="50" :fill="bgColor" />
        <rect x="250" y="260" width="300" height="20" :fill="bgColor" rx="4" />
        <rect x="280" y="290" width="240" height="20" :fill="bgColor" rx="4" />
        <rect x="300" y="320" width="200" height="20" :fill="bgColor" rx="4" />
      </g>
      <text x="400" y="400" font-family="Arial, sans-serif" font-size="24" :fill="textColor" text-anchor="middle">
        {{ text }}
      </text>
    </svg>
  </div>
</template>

<script setup lang="ts">
interface Props {
  width?: string
  height?: string
  text?: string
  bgColor?: string
  strokeColor?: string
  textColor?: string
}

withDefaults(defineProps<Props>(), {
  width: '100%',
  height: '230px',
  text: '暂无封面',
  bgColor: '#f5f5f5',
  strokeColor: '#d0d0d0',
  textColor: '#999999'
})

defineOptions({
  name: 'PlaceholderImage'
})
</script>

<style scoped>
.placeholder-image {
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.placeholder-image svg {
  width: 100%;
  height: 100%;
}
</style>
