import { VueRenderer } from '@tiptap/vue-3'
import tippy from 'tippy.js'

import CommandsList from './CommandsList.vue'

export default {
  items: ({ query }) => {
    return [
      {
        title: 'Basic',
        cntitle: '基础',
        children: [
          {
            title: '普通文本',
            icon: 'mingcute:text-line',
            description: '输入普通文本',
            command: ({ editor, range }) => {
              editor.chain().focus().deleteRange(range).setNode('paragraph').run()
            }
          },
          {
            title: '一级标题',
            icon: 'lucide:heading-1',
            description: '输入一级标题',
            command: ({ editor, range }) => {
              editor.chain().focus().deleteRange(range).setNode('heading', { level: 1 }).run()
            }
          },
          {
            title: '二级标题',
            description: '输入二级标题',
            icon: 'lucide:heading-2',
            command: ({ editor, range }) => {
              editor.chain().focus().deleteRange(range).setNode('heading', { level: 2 }).run()
            }
          },
          {
            title: '三级标题',
            description: '输入三级标题',
            icon: 'lucide:heading-3',
            command: ({ editor, range }) => {
              editor.chain().focus().deleteRange(range).setNode('heading', { level: 3 }).run()
            }
          },
          {
            title: '无序列表',
            description: '创建一个简单的无序列表',
            icon: 'lucide:list',
            command: ({ editor, range }) => {
              console.log('无序列表', editor, range)
              editor.chain().focus().deleteRange(range).toggleBulletList().run()
            }
          },
          {
            title: '有序列表',
            description: '创建一个简单的序号列表',
            icon: 'lucide:list-ordered',
            command: ({ editor, range }) => {
              editor.chain().focus().deleteRange(range).toggleOrderedList().run()
            }
          },
          {
            title: '任务列表',
            description: '创建一个简单的任务列表',
            icon: 'lucide:list-todo',
            command: ({ editor, range }) => {
              editor.chain().focus().deleteRange(range).toggleTaskList().run()
            }
          },
          {
            title: '链接',
            icon: 'lucide:link',
            description: '插入一个链接',
            command: ({ editor, range }) => {
              editor.chain().focus().deleteRange(range).openLinkDialog().run()
            }
          },
          {
            title: '分隔线',
            icon: 'lucide:minus',
            description: '插入一个分隔线',
            command: ({ editor, range }) => {
              console.log('分割线', editor, range)
              editor.chain().focus().deleteRange(range).setHorizontalRule().run()
            }
          }
        ]
      },
      {
        title: 'Advanced',
        cntitle: '高级',
        children: [
          {
            title: '代码行',
            description: '输入代码行',
            icon: 'lucide:code',
            command: ({ editor, range }) => {
              editor.chain().focus().deleteRange(range).toggleCode().run()
            }
          },
          {
            title: '代码块',
            description: '输入代码块',
            icon: 'lucide:square-code',
            command: ({ editor, range }) => {
              editor.chain().focus().deleteRange(range).setNode('codeBlock').run()
            }
          },
          {
            title: '引用',
            description: '输入引用',
            icon: 'lucide:text-quote',
            command: ({ editor, range }) => {
              editor.chain().focus().deleteRange(range).toggleBlockquote().run()
            }
          },
          {
            title: '表格',
            description: '插入表格',
            icon: 'lucide:table',
            command: ({ editor, range }) => {
              editor.chain().focus().deleteRange(range).insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()
            }
          },
          {
            title: '提到',
            description: '提到用户',
            icon: 'akar-icons:mention',
            command: ({ editor, range }) => {
              editor.chain().focus().deleteRange(range).insertContent('@').run()
            }
          }
        ]
      },
      {
        title: 'Media',
        cntitle: '媒体',
        children: [
          {
            title: '插入图片',
            description: '从URL插入一张网络图片',
            icon: 'lucide:image',
            command: ({ editor, range }) => {
              editor.chain().focus().deleteRange(range).openInsertImageDialog().run()
            }
          },
          {
            title: '上传图片',
            description: '上传一张本地图片',
            icon: 'lucide:upload',
            command: ({ editor, range }) => {
              editor.chain().focus().deleteRange(range).openUploadDialog().run()
            }
          },
          {
            title: '插入视频',
            description: '从URL插入一段网络视频',
            icon: 'icon-park-outline:video',
            command: ({ editor, range }) => {
              editor.chain().focus().deleteRange(range).openVideoDialog().run()
            }
          },
          {
            title: '插入抖音视频',
            description: '从URL插入一段抖音网络视频',
            icon: 'ic:baseline-tiktok',
            command: ({ editor, range }) => {
              editor.chain().focus().deleteRange(range).openDouyinDialog().run()
            }
          }
        ]
      }
    ]
      .filter((item) => item.title.toLowerCase().startsWith(query.toLowerCase()))
      .slice(0, 10)
  },

  render: () => {
    let component
    let popup

    return {
      onStart: (props) => {
        component = new VueRenderer(CommandsList, {
          // using vue 2:
          // parent: this,
          // propsData: props,
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
