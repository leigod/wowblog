/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

declare module '*.json' {
  const value: any
  export default value
}

// React modules for Tiptap image-upload-node
declare module 'react' {
  export * from 'react'
}

declare module '@/components/tiptap-icons/close-icon' {
  export const CloseIcon: any
  export default any
}
