/**
 * 自定义 Mention 扩展
 * 支持 id、username、name 等属性，并显示用户姓名
 */
import Mention from '@tiptap/extension-mention'
import { mergeAttributes } from '@tiptap/core'

export const CustomMention = Mention.extend({
  name: 'mention',

  addAttributes() {
    return {
      ...this.parent?.(),
      username: {
        default: null,
        parseHTML: element => element.getAttribute('data-username')
      },
      name: {
        default: null,
        parseHTML: element => element.getAttribute('data-name')
      }
    }
  },

  renderHTML({ node }) {
    return [
      'a',
      mergeAttributes({
        'href': `/user/${node.attrs.username}`,
        'class': 'mention',
        'data-mention': 'true',
        'data-id': node.attrs.id,
        'data-username': node.attrs.username,
        'data-name': node.attrs.name
      }),
      `@${node.attrs.name}`
    ]
  }
})

export default CustomMention
