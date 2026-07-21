<template>
  <node-view-wrapper>
    <a :href="node.attrs.href" :target="node.attrs.target">
      <node-view-content>超链接</node-view-content>
    </a>
  </node-view-wrapper>
</template>

<script>
import { NodeViewContent, nodeViewProps, NodeViewWrapper } from '@tiptap/vue-3'

export default {
  props: nodeViewProps,

  components: {
    NodeViewWrapper,
    NodeViewContent
  }
}
</script>

<style lang="scss"></style>
