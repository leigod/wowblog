<template>
  <el-config-provider :locale="elementPlusLocale">
    <div v-loading="appStore.loading" :element-loading-background="'rgba(0, 0, 0, 0.5)'">
      <component :is="currentLayout">
        <!-- 使用 keep-alive 缓存文档详情页 -->
        <router-view v-slot="{ Component, route }">
          <keep-alive :include="cacheableViews">
            <component :is="Component" :key="route.path" />
          </keep-alive>
        </router-view>
      </component>
    </div>
  </el-config-provider>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElConfigProvider } from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import en from 'element-plus/es/locale/lang/en'
import DefaultLayout from '@/components/layouts/DefaultLayout.vue'
import AdminLayout from '@/components/layouts/AdminLayout.vue'
import BlankLayout from '@/components/layouts/BlankLayout.vue'
import ArticleEditorLayout from '@/components/layouts/ArticleEditorLayout.vue'
import { useAppStore } from '@/stores/app'
import { useI18n } from 'vue-i18n'

// 配置需要缓存的视图组件名称
const cacheableViews = ref(['DocView', 'ArticleView', 'DocBookView'])

const appStore = useAppStore()
const route = useRoute()
const { locale } = useI18n()

// 响应式的Element Plus语言配置，与i18n的locale同步
const elementPlusLocale = computed(() => {
  return locale.value === 'zh-CN' ? zhCn : en
})

const currentLayout = computed(() => {
  const layout = route.meta.layout
  switch (layout) {
    case 'blank':
      return BlankLayout
    case 'admin':
      return AdminLayout
    case 'articleEditor':
      return ArticleEditorLayout
    default:
      return DefaultLayout
  }
})
// const locale = computed(() => {
//   switch (currentLocale.value) {
//     case 'zh-CN':
//       return zhCN
//     case 'en-US':
//       return enUS
//     default:
//       return zhCN
//   }
// })

// const handleSelectLanguage = (data: string) => {
//   changeLocale(data)
// }

// const handleDarkMode = (val: boolean) => {
//   console.log('触发了黑暗模式')
//   console.log(val)
//   toggleDark(val)
// }
</script>

<style>
body {
  margin: 0;
}

.wy-header {
  padding: 0;
}

.wy-main,
.wy-footer {
  display: flex;
  justify-content: center;
}

.wy-footer {
  background: black;
  min-height: 200px;
  color: white;
}

/* 通知弹窗样式 */
.notification-popover {
  padding: 0 !important;
  overflow: hidden !important;
}

.notification-popover .el-popover__body {
  padding: 0 !important;
}
</style>
