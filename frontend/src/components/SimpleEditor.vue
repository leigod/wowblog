<template>
  <div>
    <Editor.MenuBar :editor="editor">
      <template #default="{ commands, isActive }">
        <div class="menubar">
          <button @click="commands.bold" :class="{ 'is-active': isActive.bold() }">Bold</button>
          <button @click="commands.italic" :class="{ 'is-active': isActive.italic() }">
            Italic
          </button>
          <button @click="commands.heading({ level: 1 })">H1</button>
          <button @click="commands.heading({ level: 2 })">H2</button>
          <button @click="commands.paragraph">Paragraph</button>
          <button @click="commands.unorderedList">UL</button>
          <button @click="commands.orderedList">OL</button>
          <button @click="commands.blockquote">Blockquote</button>
          <button @click="commands.codeBlock">Code Block</button>
        </div>
      </template>
    </Editor.MenuBar>

    <Editor.Content :editor="editor" />
  </div>
</template>

<script setup>
import { Editor } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'

import { onMounted, onBeforeUnmount } from 'vue'

const editor = new Editor({
  content: '<p>Hello World!</p>',
  extensions: [StarterKit]
})

onMounted(() => {
  // 初始化逻辑
})

onBeforeUnmount(() => {
  editor.destroy()
})
</script>

<style scoped>
.menubar {
  border: 1px solid #ccc;
  padding: 5px;
}
</style>
