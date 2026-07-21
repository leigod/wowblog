<template>
  <router-view v-slot="{ Component, route }">
    <transition name="fade" mode="out-in" appear>
      <component :is="Component" v-if="route.meta.ignoreCache" :key="route.fullPath" />
      <keep-alive v-else :include="cacheList">
        <component :is="Component" :key="route.fullPath" />
      </keep-alive>
    </transition>
  </router-view>
</template>

<script setup>
import { ref } from 'vue'
const cacheList = ref([])
</script>
<script>
export default {
  name: 'PageLayout'
}
</script>
<style scoped></style>
