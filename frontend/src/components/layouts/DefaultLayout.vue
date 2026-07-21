<template>
  <el-container class="layout-container">
    <el-header class="wy-header">
      <site-nav
        :is-dark="isDark"
        @select-language="handleSelectLanguage"
        @change-dark-mode="handleDarkMode"
      ></site-nav>
    </el-header>
    <el-main class="wy-main">
      <router-view></router-view>
    </el-main>
    <el-footer class="wy-footer">
      <site-footer />
    </el-footer>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterView } from 'vue-router'
import SiteNav from '../SiteNav.vue'
import SiteFooter from '../SiteFooter.vue'
import { useAppStore } from '@/stores/app'
import useLocale from '@/hooks/locale'
import zhCN from '@/locale/zh-CN'
import enUS from '@/locale/en-US'

const store = useAppStore()
const isDark = computed(() => store.isDark)
const { changeLocale } = useLocale()

const handleSelectLanguage = (lang: string) => {
  store.setLanguage(lang)
  changeLocale(lang)
}

const handleDarkMode = (val: boolean) => {
  store.toggleDarkMode()
}
</script>

<script lang="ts">
export default {
  component: 'DefaultLayout'
}
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.wy-header {
  padding: 0;
  height: auto;
  border-bottom: 1px solid var(--el-border-color-light);
}

.wy-main {
  flex: 1;
  padding: 0;
  overflow: visible;
}

.wy-footer {
  padding: 0;
  height: auto;
  border-top: none;
  background: transparent;
}
</style>
