import { mergeAttributes, Node } from '@tiptap/core'
import { VueNodeViewRenderer } from '@tiptap/vue-3'

import LinkItem from './LinkItem.vue'

export default Node.create({
  name: 'LinkItem',

  group: 'block',

  content: 'block+',

  draggable: true,

  parseHTML() {
    return [
      {
        tag: 'a'
      }
    ]
  },

  renderHTML({ HTMLAttributes }) {
    if (this.options.HTMLAttributes.href) {
      // strip out the href
      return ['a', mergeAttributes(this.options.HTMLAttributes, { ...HTMLAttributes, href: '' }), 0]
    }

    return ['a', mergeAttributes(this.options.HTMLAttributes, HTMLAttributes), 0]
  },

  addNodeView() {
    return VueNodeViewRenderer(LinkItem)
  }
})
