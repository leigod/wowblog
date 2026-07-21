import { ref, onMounted, onBeforeUnmount, readonly } from 'vue'

interface WindowSizeState {
  width: number
  height: number
  offsetTop: number
}

/**
 * Custom composable to track window size and viewport information
 * @returns Reactive current window dimensions and offsetTop
 */
export function useWindowSize() {
  const windowSize = ref<WindowSizeState>({
    width: typeof window !== 'undefined' ? window.innerWidth : 0,
    height: typeof window !== 'undefined' ? window.innerHeight : 0,
    offsetTop:
      typeof window !== 'undefined' && window.visualViewport ? window.visualViewport.offsetTop : 0
  })

  const handleResize = () => {
    if (typeof window === 'undefined') return

    const vp = window.visualViewport
    if (!vp) {
      // Fallback for environments without visualViewport (e.g., some test environments or older browsers)
      windowSize.value = {
        width: window.innerWidth,
        height: window.innerHeight,
        offsetTop: 0 // offsetTop is specific to visualViewport
      }
      return
    }

    const { width = 0, height = 0, offsetTop = 0 } = vp

    // Only update state if values have changed
    if (
      width !== windowSize.value.width ||
      height !== windowSize.value.height ||
      offsetTop !== windowSize.value.offsetTop
    ) {
      windowSize.value = { width, height, offsetTop }
    }
  }

  onMounted(() => {
    if (typeof window !== 'undefined') {
      handleResize() // Initial call

      const visualViewport = window.visualViewport
      if (visualViewport) {
        visualViewport.addEventListener('resize', handleResize)
        visualViewport.addEventListener('scroll', handleResize)
      } else {
        // Fallback for environments without visualViewport
        window.addEventListener('resize', handleResize)
        window.addEventListener('scroll', handleResize, { passive: true })
      }
    }
  })

  onBeforeUnmount(() => {
    if (typeof window !== 'undefined') {
      const visualViewport = window.visualViewport
      if (visualViewport) {
        visualViewport.removeEventListener('resize', handleResize)
        visualViewport.removeEventListener('scroll', handleResize)
      } else {
        window.removeEventListener('resize', handleResize)
        window.removeEventListener('scroll', handleResize)
      }
    }
  })

  return readonly(windowSize)
}
