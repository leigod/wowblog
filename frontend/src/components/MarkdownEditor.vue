<template>
  <div class="markdown-editor" v-if="editor" @click.stop>
    <!-- 工具栏 -->
    <div class="editor-toolbar" @click.stop>
      <button type="button" @click.stop.prevent="safeCommand('toggleBold')"
        :class="{ 'is-active': editor.isActive('bold') }" class="toolbar-btn" title="粗体 (Ctrl+B)">
        <strong>B</strong>
      </button>
      <button type="button" @click.stop.prevent="safeCommand('toggleItalic')"
        :class="{ 'is-active': editor.isActive('italic') }" class="toolbar-btn" title="斜体 (Ctrl+I)">
        <em>I</em>
      </button>
      <button type="button" @click.stop.prevent="safeCommand('toggleStrike')"
        :class="{ 'is-active': editor.isActive('strike') }" class="toolbar-btn" title="删除线">
        <s>S</s>
      </button>
      <button type="button" @click.stop.prevent="safeCommand('toggleCode')"
        :class="{ 'is-active': editor.isActive('code') }" class="toolbar-btn" title="行内代码">
        &lt;/&gt;
      </button>

      <div class="toolbar-divider"></div>

      <button type="button" @click.stop.prevent="safeCommand('toggleHeading', { level: 1 })"
        :class="{ 'is-active': editor.isActive('heading', { level: 1 }) }" class="toolbar-btn" title="标题 1">
        H1
      </button>
      <button type="button" @click.stop.prevent="safeCommand('toggleHeading', { level: 2 })"
        :class="{ 'is-active': editor.isActive('heading', { level: 2 }) }" class="toolbar-btn" title="标题 2">
        H2
      </button>
      <button type="button" @click.stop.prevent="safeCommand('toggleHeading', { level: 3 })"
        :class="{ 'is-active': editor.isActive('heading', { level: 3 }) }" class="toolbar-btn" title="标题 3">
        H3
      </button>

      <div class="toolbar-divider"></div>

      <button type="button" @click.stop.prevent="safeCommand('toggleBulletList')"
        :class="{ 'is-active': editor.isActive('bulletList') }" class="toolbar-btn" title="无序列表">
        <IconifyIcon icon="lucide:list" color="#606266" />
      </button>
      <button type="button" @click.stop.prevent="safeCommand('toggleOrderedList')"
        :class="{ 'is-active': editor.isActive('orderedList') }" class="toolbar-btn" title="有序列表">
        <IconifyIcon icon="lucide:list-ordered" color="#606266" />
      </button>
      <button type="button" @click.stop.prevent="safeCommand('toggleBlockquote')"
        :class="{ 'is-active': editor.isActive('blockquote') }" class="toolbar-btn" title="引用">
        <IconifyIcon icon="lucide:quote" color="#606266" />
      </button>
      <button type="button" @click.stop.prevent="safeCommand('toggleCodeBlock')"
        :class="{ 'is-active': editor.isActive('codeBlock') }" class="toolbar-btn" title="代码块">
        &lt;&gt;
      </button>

      <div class="toolbar-divider"></div>

      <button type="button" @click.stop.prevent="insertImage" class="toolbar-btn" title="从URL插入图片">
        <IconifyIcon icon="lucide:image" color="#606266" />
      </button>
      <button type="button" @click.stop.prevent="uploadImage" class="toolbar-btn" title="上传图片">
        <IconifyIcon icon="lucide:image-up" color="#606266" />
      </button>

      <div class="toolbar-divider"></div>

      <button type="button" @click.stop.prevent="safeCommand('setHorizontalRule')" class="toolbar-btn" title="分割线">
        ―
      </button>
      <button type="button" @click.stop.prevent="safeCommand('undo')" class="toolbar-btn" title="撤销 (Ctrl+Z)"
        :disabled="!editor.can().undo()">
        <IconifyIcon icon="lucide:undo" color="#606266" />
      </button>
      <button type="button" @click.stop.prevent="safeCommand('redo')" class="toolbar-btn" title="重做 (Ctrl+Shift+Z)"
        :disabled="!editor.can().redo()">
        <IconifyIcon icon="lucide:redo" color="#606266" />
      </button>
    </div>

    <!-- 编辑器内容 -->
    <editor-content :editor="editor" class="editor-content" />

    <!-- 提示 -->
    <div class="editor-hint">
      支持 Markdown 快捷键：# 标题、**粗体**、*斜体*、`代码`、> 引用、- 列表等
    </div>

    <!-- URL插入图片对话框 -->
    <el-dialog v-model="dialogInsertImageVisible" title="从URL插入图片" width="500">
      <el-form :model="insertImageForm">
        <el-form-item label="URL">
          <el-input v-model="insertImageForm.url" placeholder="请输入图片URL" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogInsertImageVisible = false">取消</el-button>
        <el-button type="primary" @click="onSubmitInsertImage">确认</el-button>
      </template>
    </el-dialog>

    <!-- 上传图片对话框 -->
    <el-dialog v-model="dialogUploadImageVisible" title="上传图片" width="500">
      <el-upload drag :auto-upload="false" :on-change="handleFileChange" :show-file-list="false"
        accept="image/jpeg,image/jpg,image/png,image/gif">
        <el-icon class="el-icon--upload">
          <UploadFilled />
        </el-icon>
        <div class="el-upload__text">
          拖拽文件到此处或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 JPG、PNG、GIF 格式，文件大小不超过 5MB
          </div>
        </template>
      </el-upload>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import Link from '@tiptap/extension-link'
import Image from '@tiptap/extension-image'
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight'
import { all, createLowlight } from 'lowlight'
import IconifyIcon from '@/components/IconIfy.vue'

// 创建 lowlight 实例
const lowlight = createLowlight(all)

interface Props {
  modelValue: string
  placeholder?: string
}

interface Emits {
  (e: 'update:modelValue', value: string): void
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '输入内容...（支持 Markdown 快捷键）'
})

const emit = defineEmits<Emits>()

// 图片对话框状态
const dialogInsertImageVisible = ref(false)
const dialogUploadImageVisible = ref(false)
const insertImageForm = reactive({
  url: ''
})

const editor = useEditor({
  content: props.modelValue || '',
  extensions: [
    StarterKit.configure({
      heading: {
        levels: [1, 2, 3, 4, 5, 6]
      },
      codeBlock: false // 禁用默认的 codeBlock，使用 CodeBlockLowlight
    }),
    CodeBlockLowlight.configure({
      lowlight
    }),
    Placeholder.configure({
      placeholder: props.placeholder,
      emptyEditorClass: 'is-editor-empty'
    }),
    Link.configure({
      openOnClick: false
    }),
    Image
  ],
  onUpdate: ({ editor }) => {
    try {
      const html = editor.getHTML()
      emit('update:modelValue', html)
    } catch (e) {
      console.error('Editor update error:', e)
    }
  },
  onCreate: () => {
    // 确保编辑器正确初始化
    console.log('Editor created')
  }
})

// 安全执行命令
const safeCommand = (command: string, ...args: any[]) => {
  if (!editor.value) {
    console.warn('Editor not initialized')
    return false
  }

  try {
    const chain = editor.value.chain().focus()

    switch (command) {
      case 'toggleBold':
        chain.toggleBold().run()
        break
      case 'toggleItalic':
        chain.toggleItalic().run()
        break
      case 'toggleStrike':
        chain.toggleStrike().run()
        break
      case 'toggleCode':
        chain.toggleCode().run()
        break
      case 'toggleHeading':
        chain.toggleHeading(args[0]).run()
        break
      case 'toggleBulletList':
        chain.toggleBulletList().run()
        break
      case 'toggleOrderedList':
        chain.toggleOrderedList().run()
        break
      case 'toggleBlockquote':
        chain.toggleBlockquote().run()
        break
      case 'toggleCodeBlock':
        chain.toggleCodeBlock().run()
        break
      case 'setHorizontalRule':
        chain.setHorizontalRule().run()
        break
      case 'undo':
        if (editor.value.can().undo()) {
          chain.undo().run()
        }
        break
      case 'redo':
        if (editor.value.can().redo()) {
          chain.redo().run()
        }
        break
    }
    return true
  } catch (e) {
    console.error(`Command error (${command}):`, e)
    return false
  }
}

// 从URL插入图片
const insertImage = () => {
  insertImageForm.url = ''
  dialogInsertImageVisible.value = true
}

// 确认URL插入
const onSubmitInsertImage = () => {
  if (!editor.value) return

  dialogInsertImageVisible.value = false

  if (!insertImageForm.url) {
    ElMessage.warning('请输入图片URL')
    return
  }

  editor.value.chain().focus().setImage({ src: insertImageForm.url }).run()
}

// 上传图片
const uploadImage = () => {
  dialogUploadImageVisible.value = true
}

// 处理文件选择 - 转换为 base64 并插入到编辑器
const handleFileChange = (file: any) => {
  const rawFile = file.raw

  // 验证文件类型
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
  if (!allowedTypes.includes(rawFile.type)) {
    ElMessage.error('只能上传 JPG、PNG、GIF 格式的图片！')
    return
  }

  // 验证文件大小
  if (rawFile.size / 1024 / 1024 > 5) {
    ElMessage.error('图片大小不能超过 5MB！')
    return
  }

  // 转换为 base64
  const reader = new FileReader()
  reader.onload = (e) => {
    const base64Url = e.target?.result as string
    if (editor.value) {
      editor.value.chain().focus().setImage({ src: base64Url }).run()
    }
    dialogUploadImageVisible.value = false
    ElMessage.success('图片上传成功！')
  }
  reader.onerror = () => {
    ElMessage.error('读取图片文件失败！')
  }
  reader.readAsDataURL(rawFile)
}

// 监听外部值变化
watch(() => props.modelValue, (newValue) => {
  if (editor.value && editor.value.getHTML() !== newValue) {
    try {
      editor.value.commands.setContent(newValue || '', false)
    } catch (e) {
      console.error('Set content error:', e)
    }
  }
})

onBeforeUnmount(() => {
  if (editor.value) {
    editor.value.destroy()
  }
})
</script>

<style scoped>
.markdown-editor {
  border: 1px solid var(--el-border-color, #dcdfe6);
  border-radius: 4px;
  overflow: hidden;
}

.editor-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
  padding: 8px;
  background: var(--el-fill-color-light, #f5f7fa);
  border-bottom: 1px solid var(--el-border-color, #dcdfe6);
}

.toolbar-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 32px;
  padding: 0 8px;
  border: 1px solid transparent;
  background: transparent;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  color: var(--el-text-color-regular, #606266);
}

.toolbar-btn:hover:not(:disabled) {
  background: var(--el-fill-color, #e4e7ed);
}

.toolbar-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.toolbar-btn.is-active {
  background: var(--el-color-primary, #409eff);
  color: white;
}

.toolbar-divider {
  width: 1px;
  height: 20px;
  margin: 0 4px;
  background: var(--el-border-color, #dcdfe6);
}

.editor-content {
  min-height: 300px;
  max-height: 600px;
  overflow-y: auto;
  padding: 16px;
}

.editor-hint {
  padding: 8px 16px;
  font-size: 12px;
  color: var(--el-text-color-secondary, #909399);
  background: var(--el-fill-color-light, #f5f7fa);
  border-top: 1px solid var(--el-border-color, #dcdfe6);
}

/* Tipt 编辑器内容样式 */
:deep(.ProseMirror) {
  outline: none;
}

:deep(.ProseMirror p.is-editor-empty:first-child::before) {
  color: var(--el-text-color-placeholder, #a8abb2);
  content: attr(data-placeholder);
  float: left;
  height: 0;
  pointer-events: none;
}

:deep(.ProseMirror h1) {
  font-size: 2em;
  font-weight: bold;
  margin: 0.5em 0;
}

:deep(.ProseMirror h2) {
  font-size: 1.5em;
  font-weight: bold;
  margin: 0.5em 0;
}

:deep(.ProseMirror h3) {
  font-size: 1.25em;
  font-weight: bold;
  margin: 0.5em 0;
}

:deep(.ProseMirror ul) {
  padding-left: 1.5em;
  list-style-type: disc;
}

:deep(.ProseMirror ol) {
  padding-left: 1.5em;
  list-style-type: decimal;
}

:deep(.ProseMirror blockquote) {
  border-left: 4px solid var(--el-border-color, #dcdfe6);
  padding-left: 1em;
  margin: 1em 0;
  color: var(--el-text-color-secondary, #909399);
}

:deep(.ProseMirror code) {
  background-color: var(--gray-3);
  padding: 0.2em 0.4em;
  border-radius: 0.25rem;
  border: 1px solid var(--gray-1);
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 0.875em;
  display: inline;
}

/* 代码块样式 */
:deep(.ProseMirror pre) {
  overflow-x: auto;
  background: #1e1e1e;
  border-radius: 0.5rem;
  color: #d4d4d4;
  font-family: 'Fira Code', 'JetBrains Mono', 'Consolas', monospace;
  margin: 1.5rem 0;
  padding: 1rem;
}

:deep(.ProseMirror pre code) {
  background: none;
  color: inherit;
  font-size: 0.875rem;
  padding: 0;
  border: none;
  font-family: inherit;
}

/* 代码高亮样式 - 使用 lowlight 默认主题 */
:deep(.ProseMirror pre .hljs) {
  background: transparent;
  color: inherit;
}

:deep(.ProseMirror pre .hljs-comment),
:deep(.ProseMirror pre .hljs-quote) {
  color: #6a9955;
}

:deep(.ProseMirror pre .hljs-variable),
:deep(.ProseMirror pre .hljs-template-variable),
:deep(.ProseMirror pre .hljs-attribute),
:deep(.ProseMirror pre .hljs-tag),
:deep(.ProseMirror pre .hljs-name),
:deep(.ProseMirror pre .hljs-regexp),
:deep(.ProseMirror pre .hljs-link),
:deep(.ProseMirror pre .hljs-selector-id),
:deep(.ProseMirror pre .hljs-selector-class) {
  color: #9cdcfe;
}

:deep(.ProseMirror pre .hljs-number),
:deep(.ProseMirror pre .hljs-meta),
:deep(.ProseMirror pre .hljs-built_in),
:deep(.ProseMirror pre .hljs-builtin-name),
:deep(.ProseMirror pre .hljs-literal),
:deep(.ProseMirror pre .hljs-type),
:deep(.ProseMirror pre .hljs-params) {
  color: #b5cea8;
}

:deep(.ProseMirror pre .hljs-string),
:deep(.ProseMirror pre .hljs-symbol),
:deep(.ProseMirror pre .hljs-bullet) {
  color: #ce9178;
}

:deep(.ProseMirror pre .hljs-title),
:deep(.ProseMirror pre .hljs-section) {
  color: #dcdcaa;
}

:deep(.ProseMirror pre .hljs-keyword),
:deep(.ProseMirror pre .hljs-selector-tag) {
  color: #569cd6;
}

:deep(.ProseMirror pre .hljs-emphasis) {
  font-style: italic;
}

:deep(.ProseMirror pre .hljs-strong) {
  font-weight: bold;
}

:deep(.ProseMirror pre .hljs-function) {
  color: #dcdcaa;
}

:deep(.ProseMirror hr) {
  border: none;
  border-top: 2px solid var(--el-border-color, #dcdfe6);
  margin: 1em 0;
}

/* 图片样式 */
:deep(.ProseMirror img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 1rem 0;
  display: block;
}

:deep(.ProseMirror img.ProseMirror-selectednode) {
  outline: 3px solid var(--el-color-primary, #409eff);
}
</style>
