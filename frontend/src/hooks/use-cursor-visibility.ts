'use client'

import { watch, onMounted, onBeforeUnmount, type Ref } from 'vue'
import { Editor } from '@tiptap/core'
import { useWindowSize } from './use-window-size'

/**
 * Custom composable to ensure the Tiptap editor cursor remains visible by scrolling the window
 * @param editorRef A Ref to the Tiptap editor instance
 */
export function useCursorVisibility(editorRef: Ref<Editor | null | undefined>) {
  const windowSize = useWindowSize()

  let resizeObserver: ResizeObserver | null = null

  const checkCursorVisibility = () => {
    const editor = editorRef.value
    if (!editor || !editor.view.dom.parentElement || !editor.isFocused) return

    const { selection } = editor.state
    // Ensure domAtPos and node exist and node has getBoundingClientRect
    try {
      const pos = editor.view.domAtPos(selection.from)
      if (!pos || !pos.node) return
      const node = pos.node as HTMLElement
      if (!node || typeof node.getBoundingClientRect !== 'function') return

      const { top, bottom } = node.getBoundingClientRect()
      const currentOffsetTop = windowSize.value.offsetTop // Access .value for ref

      if (top < currentOffsetTop) {
        window.scrollTo({
          top: window.scrollY + top - currentOffsetTop - 10,
          behavior: 'smooth'
        })
      } else if (bottom > window.innerHeight) {
        window.scrollTo({
          top: window.scrollY + bottom - window.innerHeight + 10,
          behavior: 'smooth'
        })
      }
    } catch (error) {
      // domAtPos can sometimes throw an error if the position is invalid
      console.warn('Error in useCursorVisibility while getting DOM node at position:', error)
    }
  }

  onMounted(() => {
    const editor = editorRef.value
    if (editor && editor.view.dom.parentElement) {
      resizeObserver = new ResizeObserver(checkCursorVisibility)
      resizeObserver.observe(editor.view.dom.parentElement)
    }
  })

  onBeforeUnmount(() => {
    if (resizeObserver) {
      resizeObserver.disconnect()
      resizeObserver = null
    }
  })

  watch(
    [editorRef, () => windowSize.value.offsetTop],
    () => {
      // Re-observe if editor instance changes or if already observing
      if (resizeObserver && editorRef.value && editorRef.value.view.dom.parentElement) {
        resizeObserver.disconnect()
        resizeObserver.observe(editorRef.value.view.dom.parentElement)
      }
      // Initial check or check on offsetTop change
      checkCursorVisibility()
    },
    { immediate: false, deep: true }
  ) // deep true for editorRef if it's a complex object, though usually not needed for the ref itself

  // Also listen to editor's focus and update events to trigger visibility check
  watch(editorRef, (newEditor, oldEditor) => {
    if (oldEditor) {
      oldEditor.off('focus', checkCursorVisibility)
      oldEditor.off('update', checkCursorVisibility)
    }
    if (newEditor) {
      newEditor.on('focus', checkCursorVisibility)
      newEditor.on('update', checkCursorVisibility) // Check on content updates too
      // Initial check if editor becomes available and focused
      if (newEditor.isFocused) {
        checkCursorVisibility()
      }
    }
  })
}
