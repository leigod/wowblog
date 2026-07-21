/**
 * Tiptap 自定义命令扩展
 * 用于触发组件内的方法（如打开上传对话框）
 */
import { Extension } from '@tiptap/core'
import type { Editor } from '@tiptap/core'

export const CustomCommands = Extension.create({
  name: 'customCommands',

  addCommands() {
    return {
      openUploadDialog:
        () =>
        ({ editor }: { editor: Editor }) => {
          editor.view.dom.dispatchEvent(new CustomEvent('open-upload-dialog'))
          return true
        },
      openInsertImageDialog:
        () =>
        ({ editor }: { editor: Editor }) => {
          editor.view.dom.dispatchEvent(new CustomEvent('open-insert-image-dialog'))
          return true
        },
      openLinkDialog:
        () =>
        ({ editor }: { editor: Editor }) => {
          editor.view.dom.dispatchEvent(new CustomEvent('open-link-dialog'))
          return true
        },
      openDouyinDialog:
        () =>
        ({ editor }: { editor: Editor }) => {
          editor.view.dom.dispatchEvent(new CustomEvent('open-douyin-dialog'))
          return true
        },
      openVideoDialog:
        () =>
        ({ editor }: { editor: Editor }) => {
          editor.view.dom.dispatchEvent(new CustomEvent('open-video-dialog'))
          return true
        }
    } as any
  }
})
