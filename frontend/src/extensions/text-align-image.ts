/**
 * 扩展 TextAlign 以支持图片对齐，同时保持文本对齐功能
 */
import { Extension } from '@tiptap/core'
import TextAlign from '@tiptap/extension-text-align'

export const TextAlignImage = Extension.create({
  name: 'textAlignImage',

  addExtensions() {
    return [
      TextAlign.extend({
        addCommands() {
          return {
            setTextAlign:
              (alignment: string) =>
              ({ state, tr, dispatch }) => {
                const { selection } = state

                let modified = false

                state.doc.nodesBetween(selection.from, selection.to, (node, pos) => {
                  if (node.type.name === 'image') {
                    if (dispatch) {
                      tr.setNodeMarkup(pos, undefined, {
                        ...node.attrs,
                        align: alignment
                      })
                    }
                    modified = true
                  } else if (node.type.name === 'paragraph' || node.type.name === 'heading') {
                    if (dispatch) {
                      tr.setNodeMarkup(pos, undefined, {
                        ...node.attrs,
                        textAlign: alignment
                      })
                    }
                    modified = true
                  }
                })

                return modified
              }
          }
        }
      }).configure({
        types: ['heading', 'paragraph']
      })
    ]
  }
})
