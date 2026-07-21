import { VueRenderer } from '@tiptap/vue-3'
import tippy from 'tippy.js'

import MentionList from './MentionList.vue'
import { searchUsersForMention } from '@/api/services/user'

// 本地定义用户接口，避免导入问题
interface MentionUser {
  id: number
  username: string
  full_name?: string
  profile_image?: string
}

interface MentionItem {
  id: number
  name: string
  username: string
  avatar: string
}

// 缓存用户搜索结果
const userCache = new Map<string, MentionItem[]>()
const CACHE_TTL = 5 * 60 * 1000 // 5分钟缓存
const cacheTimestamps = new Map<string, number>()

// 从 API 数据转换为 mention item 格式
const formatMentionItem = (user: MentionUser): MentionItem => ({
  id: user.id,
  name: user.full_name || user.username,
  username: user.username,
  avatar: user.profile_image || '/src/assets/avatar.png'
})

// 搜索用户（带缓存）
const searchUsers = async (query: string): Promise<MentionItem[]> => {
  // 添加空值检查，避免发送空请求
  if (!query || query.trim().length === 0) {
    return []
  }

  const cacheKey = query.toLowerCase()
  const now = Date.now()

  // 检查缓存
  const cachedTimestamp = cacheTimestamps.get(cacheKey)
  if (cachedTimestamp && now - cachedTimestamp < CACHE_TTL) {
    const cached = userCache.get(cacheKey)
    if (cached) return cached
  }

  try {
    const response = await searchUsersForMention(query) as { code: number; data: MentionUser[] }
    if (response.code === 1 && response.data) {
      const items = response.data.map(formatMentionItem)
      // 更新缓存
      userCache.set(cacheKey, items)
      cacheTimestamps.set(cacheKey, now)
      return items
    }
  } catch (error) {
    console.error('搜索用户失败:', error)
  }

  return []
}

export default {
  items: async ({ query }: { query: string }) => {
    if (!query || query.length < 1) return []

    const items = await searchUsers(query)
    return items.slice(0, 5) // 限制显示5个结果
  },

  render: () => {
    let component: any
    let popup: any

    return {
      onStart: (props: any) => {
        component = new VueRenderer(MentionList, {
          props,
          editor: props.editor
        })

        if (!props.clientRect) {
          return
        }

        popup = tippy('body', {
          getReferenceClientRect: props.clientRect,
          appendTo: () => document.body,
          content: component.element,
          showOnCreate: true,
          interactive: true,
          trigger: 'manual',
          placement: 'bottom-start'
        })
      },

      onUpdate(props: any) {
        component.updateProps(props)

        if (!props.clientRect) {
          return
        }

        popup[0].setProps({
          getReferenceClientRect: props.clientRect
        })
      },

      onKeyDown(props: any) {
        if (props.event.key === 'Escape') {
          popup[0].hide()

          return true
        }

        return component.ref?.onKeyDown(props)
      },

      onExit() {
        popup[0].destroy()
        component.destroy()
      }
    }
  }
}
