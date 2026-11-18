<template>
  <footer class="bh-footer">
    <div v-if="impressum" class="bh-footer-impressum">
      <pre class="bh-impressum-text">{{ impressum }}</pre>
    </div>
    <div class="bh-footer-inner">
      <span class="bh-footer-copy">© {{ copyrightYears }} {{ blogTitle }}</span>
      <span class="bh-footer-links">
        <a href="javascript:;" @click="$router.push('/page/privacy-policy')">隐私政策</a>
        <a href="javascript:;" @click="$router.push('/page/terms-of-service')">服务协议</a>
      </span>
      <span class="bh-footer-powered" @click="$router.push('/')">
        <img :src="siteFavicon || '/favicon.ico'" alt="site" class="bh-footer-favicon" />
        Powered by WOW Blog
      </span>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  impressum?: string | null
  createtime?: number | null
  blogTitle: string
  siteFavicon: string
}
const props = withDefaults(defineProps<Props>(), {
  impressum: null,
  createtime: null
})
const copyrightYears = computed(() => {
  const start = props.createtime
    ? new Date(props.createtime * 1000).getFullYear()
    : new Date().getFullYear()
  const now = new Date().getFullYear()
  return start === now ? String(now) : `${start} - ${now}`
})
</script>

<style scoped>
.bh-footer { border-top: 1px solid var(--el-border-color-lighter); background: var(--el-bg-color); }
.bh-footer-inner {
  max-width: 1200px; margin: 0 auto; padding: 20px 24px; display: flex; align-items: center;
  justify-content: space-between; gap: 16px; font-size: 13px;
  color: var(--el-text-color-secondary); flex-wrap: wrap;
}
.bh-footer-links { display: flex; gap: 18px; }
.bh-footer-links a { color: var(--el-text-color-secondary); text-decoration: none; }
.bh-footer-links a:hover { color: var(--el-color-primary); }
.bh-footer-powered { display: flex; align-items: center; gap: 6px; cursor: pointer; }
.bh-footer-favicon { width: 16px; height: 16px; border-radius: 3px; }
.bh-footer-impressum { max-width: 1200px; margin: 0 auto; padding: 28px 24px 0; }
.bh-impressum-text {
  margin: 0 0 36px; font-family: inherit; font-size: 13px; line-height: 1.9;
  color: var(--el-text-color-secondary); white-space: pre-wrap; word-break: break-word;
}
</style>
