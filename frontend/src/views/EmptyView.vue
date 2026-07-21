<template>
  <el-empty>
    <el-button type="primary" @click="handleClick">{{ t('error.404.home') }}</el-button>
    <template #description>
      <div>{{ t('error.404.description') }}</div>
      <div class="style404">404</div>
    </template>
  </el-empty>
</template>
<script lang="ts" setup>
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const router = useRouter()
const handleClick = () => {
  router.push('/')
}
</script>
<style>
.style404 {
  width: 100%;
  min-height: 400px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 10rem;
  font-weight: 800;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: darkgrey;
}
</style>
