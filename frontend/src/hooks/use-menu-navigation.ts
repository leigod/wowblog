import { ref, watch, onMounted, onBeforeUnmount, type Ref, computed, readonly } from 'vue'
import type { Editor } from '@tiptap/core' // Assuming @tiptap/core for Vue

type Orientation = 'horizontal' | 'vertical' | 'both'

interface MenuNavigationOptions<T> {
  editor?: Ref<Editor | null | undefined>
  containerRef?: Ref<HTMLElement | null | undefined>
  query?: Ref<string | undefined>
  items: Ref<T[]>
  onSelect?: (item: T) => void
  onClose?: () => void
  orientation?: Orientation
  autoSelectFirstItem?: boolean
}

export function useMenuNavigation<T>({
  editor,
  containerRef,
  query,
  items,
  onSelect,
  onClose,
  orientation = 'vertical',
  autoSelectFirstItem = true
}: MenuNavigationOptions<T>) {
  const selectedIndex = ref<number>(autoSelectFirstItem ? 0 : -1)

  const handleKeyboardNavigation = (event: KeyboardEvent) => {
    if (!items.value.length) return false

    const moveNext = () => {
      selectedIndex.value =
        selectedIndex.value === -1 ? 0 : (selectedIndex.value + 1) % items.value.length
    }

    const movePrev = () => {
      selectedIndex.value =
        selectedIndex.value === -1
          ? items.value.length - 1
          : (selectedIndex.value - 1 + items.value.length) % items.value.length
    }

    switch (event.key) {
      case 'ArrowUp': {
        if (orientation === 'horizontal') return false
        event.preventDefault()
        movePrev()
        return true
      }
      case 'ArrowDown': {
        if (orientation === 'horizontal') return false
        event.preventDefault()
        moveNext()
        return true
      }
      case 'ArrowLeft': {
        if (orientation === 'vertical') return false
        event.preventDefault()
        movePrev()
        return true
      }
      case 'ArrowRight': {
        if (orientation === 'vertical') return false
        event.preventDefault()
        moveNext()
        return true
      }
      case 'Tab': {
        event.preventDefault()
        if (event.shiftKey) {
          movePrev()
        } else {
          moveNext()
        }
        return true
      }
      case 'Home': {
        event.preventDefault()
        selectedIndex.value = 0
        return true
      }
      case 'End': {
        event.preventDefault()
        selectedIndex.value = items.value.length - 1
        return true
      }
      case 'Enter': {
        if ((event as any).isComposing) return false // Check for isComposing if applicable
        event.preventDefault()
        if (selectedIndex.value !== -1 && items.value[selectedIndex.value]) {
          onSelect?.(items.value[selectedIndex.value])
        }
        return true
      }
      case 'Escape': {
        event.preventDefault()
        onClose?.()
        return true
      }
      default:
        return false
    }
  }

  let internalTargetElement: HTMLElement | null = null

  const setupEventListeners = () => {
    if (internalTargetElement) {
      internalTargetElement.removeEventListener('keydown', handleKeyboardNavigation, true)
    }

    if (editor?.value) {
      internalTargetElement = editor.value.view.dom
    } else if (containerRef?.value) {
      internalTargetElement = containerRef.value
    }

    if (internalTargetElement) {
      internalTargetElement.addEventListener('keydown', handleKeyboardNavigation, true)
    }
  }

  onMounted(setupEventListeners)
  watch([editor, containerRef], setupEventListeners) // Re-setup if editor or containerRef changes

  onBeforeUnmount(() => {
    if (internalTargetElement) {
      internalTargetElement.removeEventListener('keydown', handleKeyboardNavigation, true)
    }
  })

  watch(query || ref(undefined), () => {
    selectedIndex.value = autoSelectFirstItem ? 0 : -1
  })

  // Ensure selectedIndex is valid when items change
  watch(
    items,
    (newItems) => {
      if (selectedIndex.value >= newItems.length) {
        selectedIndex.value = autoSelectFirstItem && newItems.length > 0 ? 0 : -1
      } else if (newItems.length === 0) {
        selectedIndex.value = -1
      } else if (selectedIndex.value === -1 && autoSelectFirstItem && newItems.length > 0) {
        selectedIndex.value = 0
      }
    },
    { deep: true }
  )

  return {
    selectedIndex: computed(() => (items.value.length ? selectedIndex.value : undefined)),
    setSelectedIndex: (index: number) => {
      selectedIndex.value = index
    }
  }
}
