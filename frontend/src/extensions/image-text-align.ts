/**
 * 图片对齐扩展 - 将 TextAlign 命令桥接到 ImageAligned
 */
import { Extension } from '@tiptap/core'

export const ImageTextAlign = Extension.create({
  name: 'imageTextAlign',

  addGlobalAttributes() {
    return [
      {
        types: ['image'],
        attributes: {
          align: {
            default: null,
            parseHTML: (element) => {
              const align = (element as HTMLElement).style.textAlign ||
                            (element as HTMLElement).getAttribute('data-align') ||
                            (element as HTMLElement).parentElement?.style.textAlign
              if (align === 'left' || align === 'center' || align === 'right') {
                return align
              }
              return null
            },
            renderHTML: (attributes) => {
              if (!attributes.align) {
                return {}
              }
              return {
                'data-align': attributes.align,
                style: 'display: inline-block;'
              }
            }
          }
        }
      }
    ]
  },

  addCommands() {
    return {
      setImageAlign: (align: string | null) => ({ commands, state }: any) => {
        const { selection } = state
        const { $from } = selection

        // 检查当前选中的是否是图片节点
        const node = $from.node
        if (!node || node.type.name !== 'image') {
          // 尝试查找父节点中的图片
          const currentNode = $from.parent
          if (currentNode && currentNode.type.name === 'image') {
            return commands.updateAttributes('image', { align })
          }
          // 如果当前节点不是图片，正常设置文本对齐
          return commands.setTextAlign(align as any)
        }

        // 如果是图片节点，更新其 align 属性
        return commands.updateAttributes('image', { align })
      }
    } as any
  }
})
