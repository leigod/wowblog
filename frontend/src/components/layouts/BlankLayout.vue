<template>
  <div class="blank-layout">
    <router-view />
  </div>
</template>

<script setup lang="ts">
// 空白布局组件，用于不需要导航栏和页脚的页面（如登录页）
</script>

<style scoped>
.blank-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
</style>