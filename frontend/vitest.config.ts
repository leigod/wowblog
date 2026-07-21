import { fileURLToPath } from 'node:url'
import { mergeConfig, defineConfig, configDefaults } from 'vitest/config'
import viteConfig from './vite.config'

// vite.config 以函数形式导出（按 command 切换 esbuild.drop），
// vitest 以 serve/test 上下文解析为普通对象，再合并测试配置。
const base: any = typeof viteConfig === 'function'
  ? (viteConfig as any)({ command: 'serve', mode: 'test' })
  : viteConfig

export default mergeConfig(
  base,
  defineConfig({
    test: {
      environment: 'jsdom',
      exclude: [...configDefaults.exclude, 'e2e/**'],
      root: fileURLToPath(new URL('./', import.meta.url))
    }
  })
)
