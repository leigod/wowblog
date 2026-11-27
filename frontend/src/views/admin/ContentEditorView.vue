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
import { computed, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElButton, ElIcon, ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import TiptapEditor from '@/components/TiptapEditor.vue'
import {
  PAGE_DRAFT_QUERY_KEY,
  draftTokenFromQuery,
  getPageDraft,
  savePageDraft
} from '@/utils/pageDraft'

const router = useRouter()
const route = useRoute()

// 草稿由表单页在打开编辑器前写入：初始正文、以及“回到哪个表单”都以它为准
const draft = getPageDraft(draftTokenFromQuery(route.query[PAGE_DRAFT_QUERY_KEY]))
const content = ref(draft?.content ?? '')
// 进入编辑器时的正文，用于判断是否有未保存的修改
const initialContent = content.value

const returnPath = computed(() =>
  draft?.mode === 'edit' ? `/admin/pages/edit/${draft.pageId}` : '/admin/pages/create'
)

// 带着令牌回到表单：表单据此取回正文和之前填写的其它字段
const backToForm = () => {
  const token = draft?.token
  router.push({ path: returnPath.value, query: token ? { [PAGE_DRAFT_QUERY_KEY]: token } : {} })
}

const keepContent = () => {
  if (draft) savePageDraft({ ...draft, content: content.value })
}

const handleSave = () => {
  keepContent()
  ElMessage.success('Content saved temporarily!')
  backToForm()
}

const handleBack = () => {
  if (content.value === initialContent) {
    backToForm()
    return
  }
  if (confirm('You have unsaved changes. Are you sure you want to leave?')) {
    // 确认离开时保留已输入的内容并带回表单，不做丢弃
    keepContent()
    backToForm()
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
