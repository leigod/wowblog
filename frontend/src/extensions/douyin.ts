/**
 * 抖音视频扩展
 * 支持在编辑器中嵌入抖音视频
 * 使用简单的存储方式：将视频信息存储在 div 属性中
 */
import { Node, mergeAttributes } from '@tiptap/core'

export interface DouyinOptions {
  HTMLAttributes: Record<string, any>
}

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    douyin: {
      /**
       * 插入抖音视频
       */
      setDouyinVideo: (options: { videoId: string; embedUrl: string }) => ReturnType
    }
  }
}

export const DouyinExtension = Node.create<DouyinOptions>({
  name: 'douyinVideo',

  group: 'block',

  atom: true,

  draggable: true,

  addOptions() {
    return {
      HTMLAttributes: {}
    }
  },

  addAttributes() {
    return {
      videoId: {
        default: null,
        parseHTML: element => element.getAttribute('data-video-id'),
        renderHTML: attributes => ({
          'data-video-id': attributes.videoId
        })
      },
      embedUrl: {
        default: null,
        parseHTML: element => element.getAttribute('data-embed-url'),
        renderHTML: attributes => ({
          'data-embed-url': attributes.embedUrl
        })
      }
    }
  },

  parseHTML() {
    return [
      {
        tag: 'div[data-douyin-video]'
      }
    ]
  },

  renderHTML({ node }) {
    const videoId = node.attrs.videoId
    const embedUrl = node.attrs.embedUrl

    console.log('DouyinExtension renderHTML:', { videoId, embedUrl })

    // atom 节点不能有子元素，只返回标签名和属性
    return [
      'div',
      mergeAttributes({
        'data-douyin-video': 'true',
        'data-video-id': videoId,
        'data-embed-url': embedUrl,
        'class': 'douyin-video-wrapper',
        'style': 'position: relative; width: 100%; max-width: 800px; margin: 1.5rem auto;'
      }, this.options.HTMLAttributes)
    ]
  },

  addCommands() {
    return {
      setDouyinVideo:
        (options: { videoId: string; embedUrl: string }) =>
        ({ commands }) => {
          return commands.insertContent({
            type: this.name,
            attrs: options
          })
        }
    }
  }
})

export default DouyinExtension
