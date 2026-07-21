<template>
  <div class="content-editor-container">
    <div class="editor-header">
      <el-button link type="primary" @click="handleBack">
        <el-icon>
          <ArrowLeft />
        </el-icon> Back
      </el-button>
      <h1>Content Editor</h1>
      <el-button type="primary" @click="handleSave"> Save Content </el-button>
    </div>

    <div class="editor-wrapper">
      <TiptapEditor v-model="content" placeholder="Add page content here" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElButton, ElIcon, ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import TiptapEditor from '@/components/TiptapEditor.vue'

const router = useRouter()
const route = useRoute()

// Get content from route query or default to empty string
const content = ref((route.query.content as string) || '')
// Store the page ID or slug if editing existing page
const pageId = ref((route.query.pageId as string) || '')
const mode = ref((route.query.mode as string) || 'create')

onMounted(() => {
  // Initialization logic if needed
})

const handleSave = () => {
  // Save content to localStorage or sessionStorage temporarily
  // In a real app, you might want to call an API here
  localStorage.setItem('tempEditorContent', content.value)

  ElMessage.success('Content saved temporarily!')

  // Navigate back to the create page view with the saved content
  if (mode.value === 'create') {
    router.push({
      path: '/admin/pages/create',
      query: {
        content: content.value,
        pageId: pageId.value
      }
    })
  } else {
    router.push({
      path: '/admin/pages/edit/' + pageId.value,
      query: {
        content: content.value,
        pageId: pageId.value
      }
    })
  }
}

const handleBack = () => {
  // Ask for confirmation if there are unsaved changes
  if (content.value !== ((route.query.content as string) || '')) {
    if (confirm('You have unsaved changes. Are you sure you want to leave?')) {
      // 即使用户选择离开，也保存当前内容
      localStorage.setItem('tempEditorContent', content.value)
      router.push({
        path: '/admin/pages/create',
        query: {
          content: content.value,
          pageId: pageId.value
        }
      })
    }
  } else {
    router.push('/admin/pages/create')
  }
}
</script>

<style scoped>
.content-editor-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.editor-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e4e7ed;
}

.editor-header h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
}

.editor-wrapper {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

@media (max-width: 768px) {
  .content-editor-container {
    padding: 12px;
    max-width: 100%;
    width: 100%;
  }

  .editor-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
    padding-bottom: 12px;
  }

  .editor-header h1 {
    align-self: center;
    font-size: 18px;
    margin: 0;
  }

  .editor-header .el-button {
    width: 100%;
    justify-content: center;
  }

  .editor-wrapper {
    padding: 12px;
    border-radius: 8px;
  }
}

@media (max-width: 480px) {
  .content-editor-container {
    padding: 8px;
  }

  .editor-header h1 {
    font-size: 16px;
  }

  .editor-wrapper {
    padding: 8px;
  }
}
</style>
