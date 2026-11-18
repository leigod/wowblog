import Sortable from 'sortablejs'
import { nextTick, onBeforeUnmount, type Ref } from 'vue'

/**
 * 列表拖拽排序（Creator 工作台的分类/系列/导航共用）。
 *
 * 拖拽结束后就地重排 listRef 并把新顺序的 id 数组交给 onReorder
 * （由调用方调 sortbatch 接口持久化）。
 *
 * @param containerRef 拖拽容器元素 ref（其直接子元素为列表行）
 * @param listRef 与容器渲染顺序绑定的响应式数组
 * @param onReorder 拖拽完成后的持久化回调（收到新顺序的 id 数组）
 * @param handleClass 拖拽手柄的类名
 */
export function useSortableList<T extends { id: number }>(
  containerRef: Ref<HTMLElement | null>,
  listRef: Ref<T[]>,
  onReorder: (ids: number[]) => Promise<void>,
  handleClass = '.drag-handle'
) {
  let instance: Sortable | null = null

  const init = async () => {
    await nextTick()
    if (!containerRef.value) return
    instance?.destroy()
    instance = Sortable.create(containerRef.value, {
      handle: handleClass,
      animation: 150,
      onEnd: async ({ oldIndex, newIndex }) => {
        if (oldIndex === undefined || newIndex === undefined || oldIndex === newIndex) return
        const arr = [...listRef.value]
        const [moved] = arr.splice(oldIndex, 1)
        arr.splice(newIndex, 0, moved)
        listRef.value = arr
        await onReorder(arr.map((i) => i.id))
      }
    })
  }

  const destroy = () => {
    instance?.destroy()
    instance = null
  }

  onBeforeUnmount(destroy)
  return { init, destroy }
}
