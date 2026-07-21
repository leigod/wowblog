import { ref, computed, onMounted, onUnmounted, type Ref } from 'vue'

/**
 * 移动端检测组合式函数
 * @param breakpoint - 断点值（像素），默认768px
 * @returns 移动端检测相关的响应式数据和方法
 */
export function useMobileDetection(breakpoint = 768) {
  // 窗口宽度
  const windowWidth: Ref<number> = ref(window.innerWidth)

  // 处理窗口大小变化
  const handleResize = () => {
    windowWidth.value = window.innerWidth
  }

  // 判断是否为移动端（小于断点值）
  const isMobile = computed(() => windowWidth.value < breakpoint)

  // 判断是否为平板（断点到1024px之间）
  const isTablet = computed(() =>
    windowWidth.value >= breakpoint && windowWidth.value < 1024
  )

  // 判断是否为桌面端（1024px及以上）
  const isDesktop = computed(() => windowWidth.value >= 1024)

  // 判断是否为小屏幕手机（小于480px）
  const isSmallMobile = computed(() => windowWidth.value < 480)

  // 判断是否为大屏幕手机/小平板（480px到断点）
  const isLargeMobile = computed(() =>
    windowWidth.value >= 480 && windowWidth.value < breakpoint
  )

  // 组件挂载时添加事件监听
  onMounted(() => {
    window.addEventListener('resize', handleResize)
  })

  // 组件卸载时移除事件监听
  onUnmounted(() => {
    window.removeEventListener('resize', handleResize)
  })

  return {
    windowWidth,
    isMobile,
    isTablet,
    isDesktop,
    isSmallMobile,
    isLargeMobile,
    handleResize
  }
}

/**
 * 获取响应式尺寸
 * @param mobileValue - 移动端值
 * @param tabletValue - 平板端值
 * @param desktopValue - 桌面端值
 * @returns 根据屏幕尺寸返回相应的值
 */
export function useResponsiveValue<T>(
  mobileValue: T,
  tabletValue?: T,
  desktopValue?: T
): Ref<T> {
  const { windowWidth } = useMobileDetection()

  return computed(() => {
    if (windowWidth.value < 768) {
      return mobileValue
    } else if (windowWidth.value < 1024) {
      return tabletValue !== undefined ? tabletValue : mobileValue
    } else {
      return desktopValue !== undefined ? desktopValue : (tabletValue !== undefined ? tabletValue : mobileValue)
    }
  }) as Ref<T>
}
