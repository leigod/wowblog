/**
 * 支持对齐的 Image 扩展
 */
import Image from '@tiptap/extension-image'
import { mergeAttributes } from '@tiptap/core'

export const ImageAligned = Image.extend({
  name: 'image',
  inline: false,
  allowBase64: true,
  group: 'block',

  addAttributes() {
    return {
      ...this.parent?.(),
      align: {
        default: 'left',
        parseHTML: (element) => {
          const imgElement = element as HTMLElement
          const dataAlign = imgElement.getAttribute('data-align')
          if (dataAlign) return dataAlign

          // 从包裹的 div 获取
          const wrapper = imgElement.parentElement
          if (wrapper && wrapper.classList.contains('image-wrapper')) {
            const wrapperAlign = wrapper.getAttribute('data-align')
            if (wrapperAlign) return wrapperAlign
          }

          return 'left'
        },
        renderHTML: (attributes) => {
          return {
            'data-align': attributes.align || 'left'
          }
        }
      }
    }
  },

  renderHTML({ node, HTMLAttributes }) {
    const align = node.attrs.align || 'left'

    // 将图片包裹在一个 div 中以应用 text-align
    return [
      'div',
      {
        'data-align': align,
        'class': 'image-wrapper',
        'style': `text-align: ${align}; margin: 1.5rem 0;`
      },
      [
        'img',
        mergeAttributes(HTMLAttributes, {
          'data-align': align,
          'style': 'display: inline-block; max-width: 100%; height: auto;'
        })
      ]
    ]
  }
})
