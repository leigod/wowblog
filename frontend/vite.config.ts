import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'

import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

// https://vitejs.dev/config/
export default defineConfig(({ command }) => ({
  esbuild: {
    // 生产构建（command === 'build'）移除所有 console.* 与 debugger，
    // 一次性杜绝 token/敏感信息经 console.log 泄露到生产 bundle；
    // dev (serve) 保留 console 便于调试。
    drop: command === 'build' ? ['console', 'debugger'] : []
  },
  plugins: [
    vue(),
    vueJsx(),
    AutoImport({
      resolvers: [ElementPlusResolver()]
    }),
    Components({
      resolvers: [ElementPlusResolver()]
    })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        // WebSocket 支持
        ws: true
      },
      '/ws': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        // WebSocket 支持
        ws: true,
        // 重写路径，将 /ws 转发到 /api/ws
        rewrite: (path) => path.replace(/^\/ws/, '/api/ws')
      }
    }
  },
  build: {
    rollupOptions: {
      output: {
        // vendor 分割：把大依赖拆为独立稳定 chunk，减小入口包并利于缓存命中
        manualChunks(id: string) {
          if (id.includes('node_modules')) {
            if (id.includes('@tiptap') || id.includes('prosemirror')) return 'tiptap'
            if (id.includes('marked') || id.includes('highlight.js')) return 'markdown'
            if (id.includes('element-plus') || id.includes('@element-plus')) return 'element-plus'
          }
        }
      }
    }
  }
}))
