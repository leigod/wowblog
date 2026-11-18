import { nextTick, onMounted, watch, type Ref } from 'vue'

/**
 * textarea 随内容自动调整高度。
 *
 * 用于沉浸式编辑器的标题/副标题等原生 textarea（Element Plus 的 autosize
 * 只作用于 el-input，原生 textarea 需要自行计算）。内容变化（含编辑页
 * 异步回填）后，以 scrollHeight 重设高度，避免长文本被固定高度截断。
 *
 * @param content 驱动高度的文本内容（v-model 绑定的 ref）
 * @param target textarea 元素 ref
 * @returns 手动触发重算的函数（如切换显示后需要立即校正高度时使用）
 */
export function useAutoTextarea(
  content: Ref<string>,
  target: Ref<HTMLTextAreaElement | null>
) {
  const resize = () => {
    const el = target.value
    if (!el) return
    // 先归零再测量，避免上一次设置的高度影响 scrollHeight 的取值
    el.style.height = 'auto'
    el.style.height = `${el.scrollHeight}px`
  }

  watch(content, () => nextTick(resize))
  onMounted(() => nextTick(resize))

  return resize
}
