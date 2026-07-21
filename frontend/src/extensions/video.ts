/**
 * 在线视频扩展
 * 支持插入 mp4、webm 等格式的在线视频
 */
import { Node, mergeAttributes } from '@tiptap/core'

export interface VideoOptions {
  HTMLAttributes: Record<string, any>
}

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    video: {
      /**
       * 插入在线视频
       */
      setVideo: (options: {
        src: string
        controls?: boolean
        autoplay?: boolean
        loop?: boolean
        width?: string
      }) => ReturnType
    }
  }
}

export const VideoExtension = Node.create<VideoOptions>({
  name: 'video',

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
      src: {
        default: null,
        parseHTML: element => {
          const video = element as HTMLVideoElement
          return video.src || element.getAttribute('data-src')
        }
      },
      controls: {
        default: true,
        parseHTML: element => {
          return element.hasAttribute('controls')
        }
      },
      autoplay: {
        default: false,
        parseHTML: element => {
          return element.hasAttribute('autoplay')
        }
      },
      loop: {
        default: false,
        parseHTML: element => {
          return element.hasAttribute('loop')
        }
      },
      width: {
        default: '100%',
        parseHTML: element => {
          return element.style.width || element.getAttribute('data-width') || '100%'
        }
      }
    }
  },

  parseHTML() {
    return [
      {
        tag: 'video[data-video]',
        getAttrs: node => {
          const video = node as HTMLVideoElement
          return {
            src: video.src || video.getAttribute('data-src'),
            controls: video.hasAttribute('controls'),
            autoplay: video.hasAttribute('autoplay'),
            loop: video.hasAttribute('loop'),
            width: video.style.width || video.getAttribute('data-width')
          }
        }
      }
    ]
  },

  renderHTML({ node }) {
    const { src, controls, autoplay, loop, width } = node.attrs

    console.log('VideoExtension renderHTML:', { src, controls, autoplay, loop, width })

    return [
      'video',
      mergeAttributes({
        'data-video': 'true',
        'data-src': src,
        'src': src,
        'controls': controls === true ? '' : undefined,
        'autoplay': autoplay === true ? '' : undefined,
        'loop': loop === true ? '' : undefined,
        'data-width': width,
        'style': `width: ${width}; max-width: 100%; border-radius: 8px; background: #000;`,
        'class': 'custom-video-player'
      }, this.options.HTMLAttributes)
    ]
  },

  addCommands() {
    return {
      setVideo:
        (options: { src: string; controls?: boolean; autoplay?: boolean; loop?: boolean; width?: string }) =>
        ({ commands }) => {
          console.log('setVideo command:', options)
          return commands.insertContent({
            type: this.name,
            attrs: options
          })
        }
    }
  }
})

export default VideoExtension
