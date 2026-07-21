<template>
  <div class="wy-container">
    <h2>Create Article</h2>
    <tiptap-editor />
  </div>
</template>

<script setup>
import TiptapEditor from '@/components/TiptapEditor.vue'
</script>

<style scoped lang="scss">
.wy-container {
  display: flex;
  flex-direction: column;
  width: 1200px;
}
</style>
