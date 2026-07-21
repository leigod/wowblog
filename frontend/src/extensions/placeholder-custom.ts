/**
 * 自定义 Placeholder 扩展
 * 使用 CSS 方式实现占位符功能
 */
import { Extension } from '@tiptap/core'

export const CustomPlaceholder = Extension.create({
  name: 'customPlaceholder',

  addOptions() {
    return {
      placeholder: ''
    }
  },

  onCreate() {
    const { editor } = this
    const placeholderText = this.options.placeholder
    if (!placeholderText) return

    // 定义更新函数
    const updatePlaceholder = () => {
      if (!editor.view) return
      const dom = editor.view.dom as HTMLElement
      const isEmpty = editor.isEmpty

      if (isEmpty) {
        dom.setAttribute('data-placeholder', placeholderText)
        dom.classList.add('is-empty')
      } else {
        dom.removeAttribute('data-placeholder')
        dom.classList.remove('is-empty')
      }
    }

    // 初始化时设置 placeholder
    updatePlaceholder()

    // 监听内容变化
    editor.on('update', updatePlaceholder)

    // 监听选择变化
    editor.on('selectionUpdate', updatePlaceholder)
  }
})
