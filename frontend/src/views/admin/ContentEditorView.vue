<template>
  <div class="content-editor-container">
    <div class="editor-header">
      <el-button link type="primary" @click="handleBack">
        <el-icon>
          <ArrowLeft />
        </el-icon>
        {{ t('admin.pages.content_editor.back') }}
      </el-button>
      <h1>{{ t('admin.pages.content_editor.title') }}</h1>
      <el-button type="primary" @click="handleSave">
        {{ t('admin.pages.content_editor.save') }}
      </el-button>
    </div>

    <div class="editor-wrapper">
      <TiptapEditor v-model="content" :placeholder="t('admin.pages.content_editor.placeholder')" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElButton, ElIcon, ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import TiptapEditor from '@/components/TiptapEditor.vue'
import {
  PAGE_DRAFT_QUERY_KEY,
  draftTokenFromQuery,
  getPageDraft,
  savePageDraft
} from '@/utils/pageDraft'

const { t } = useI18n()
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
  ElMessage.success(t('admin.pages.content_editor.save_success'))
  backToForm()
}

const handleBack = async () => {
  if (content.value === initialContent) {
    backToForm()
    return
  }
  try {
    await ElMessageBox.confirm(
      t('admin.pages.content_editor.unsaved_message'),
      t('admin.pages.content_editor.unsaved_title'),
      {
        confirmButtonText: t('admin.pages.content_editor.unsaved_leave'),
        cancelButtonText: t('admin.pages.content_editor.unsaved_stay'),
        type: 'warning'
      }
    )
  } catch {
    // 用户选择“继续编辑”：留在编辑器，不做任何事
    return
  }
  // 确认离开时保留已输入的内容并带回表单，不做丢弃
  keepContent()
  backToForm()
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
