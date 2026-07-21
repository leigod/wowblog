<template>
  <div class="forbidden-container">
    <div class="forbidden-content">
      <div class="error-code">403</div>
      <div class="error-title">{{ t('error.403.title') }}</div>
      <div class="error-description">
        {{ t('error.403.description') }}
      </div>
      <div class="error-actions">
        <el-button type="primary" @click="goBack">{{ t('error.403.back') }}</el-button>
        <el-button @click="goHome">{{ t('error.403.home') }}</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const router = useRouter()

const goBack = () => {
  router.back()
}

const goHome = () => {
  router.push('/')
}
</script>

<style scoped>
.forbidden-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  /* background-color: var(--el-bg-color-page); */
}

.forbidden-content {
  text-align: center;
  padding: 40px;
}

.error-code {
  font-size: 120px;
  font-weight: bold;
  color: var(--el-color-danger);
  line-height: 1;
  margin-bottom: 20px;
}

.error-title {
  font-size: 28px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 16px;
}

.error-description {
  font-size: 16px;
  color: var(--el-text-color-regular);
  margin-bottom: 32px;
}

.error-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}
</style>
