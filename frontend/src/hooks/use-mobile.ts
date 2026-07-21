import { ref, onMounted, onBeforeUnmount, readonly } from 'vue'

const MOBILE_BREAKPOINT = 1024

/**
 * Custom composable to determine if the current view is mobile
 * @returns A readonly ref, true if the current view is mobile, false otherwise
 */
export function useMobile() {
  const isMobile = ref(false)

  let mql: MediaQueryList | undefined

  const handler = (e: MediaQueryListEvent | MediaQueryList) => {
    isMobile.value = e.matches
  }

  onMounted(() => {
    if (typeof window !== 'undefined') {
      mql = window.matchMedia(`(max-width: ${MOBILE_BREAKPOINT}px)`)
      // Set initial state
      handler(mql)
      // Add listener
      if ('addEventListener' in mql) {
        mql.addEventListener('change', handler)
      } else {
        // Fallback for older browsers
        ;(mql as any).addListener(handler)
      }
    }
  })

  onBeforeUnmount(() => {
    if (mql) {
      if ('removeEventListener' in mql) {
        mql.removeEventListener('change', handler)
      } else {
        // Fallback for older browsers
        ;(mql as any).removeListener(handler)
      }
    }
  })

  return readonly(isMobile)
}
