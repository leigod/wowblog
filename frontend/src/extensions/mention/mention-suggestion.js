import { VueRenderer } from '@tiptap/vue-3'
import tippy from 'tippy.js'
import { searchUsersForMention } from '@/api/services/member'
import MentionList from './MentionList.vue'

export default {
  items: async ({ query }) => {
    // 添加空值检查，避免发送空请求
    if (!query || query.trim().length === 0) {
      return []
    }

    try {
      // 从后端获取用户列表
      const response = await searchUsersForMention(query)
      if (response && response.data) {
        // 转换数据格式以适配前端需求
        return response.data.map(user => ({
          id: user.id,
          name: user.full_name || user.username, // 显示名称优先使用全名
          username: user.username, // 用户名用于显示 @username
          avatar: user.profile_image || '/src/assets/avatar.png' // 使用用户头像或默认头像
        })).slice(0, 5)
      }
      return []
    } catch (error) {
      console.error('搜索用户失败:', error)
      return []
    }
  },

  render: () => {
    let component
    let popup

    return {
      onStart: (props) => {
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

      onUpdate(props) {
        component.updateProps(props)

        if (!props.clientRect) {
          return
        }

        popup[0].setProps({
          getReferenceClientRect: props.clientRect
        })
      },

      onKeyDown(props) {
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
