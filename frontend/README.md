# WowBlog Frontend

Vue 3 前端,属于 [WowBlog](../README.md) monorepo 的 `frontend/` 子包。

完整的安装、运行、部署说明请参阅[根目录 README](../README.md)。

## 常用命令

| 命令 | 用途 |
|---|---|
| `npm run dev` | 启动开发服务器(http://localhost:5173,代理 `/api` 到后端 8000) |
| `npm run build` | 生产构建(自动剔除 `console` / `debugger`) |
| `npm run type-check` | TypeScript 类型检查 |
| `npm run lint` | ESLint 检查并自动修复 |
| `npm run format` | Prettier 格式化 `src/` |
| `npm run test:unit` | 单元测试(Vitest) |

## 环境变量

复制 `.env.example` 为 `.env.local` 并按需修改,至少配置 `VITE_API_BASE_URL`(指向后端地址,默认 `http://127.0.0.1:8000/api`)。

## 技术栈

Vue 3.4 · Vite 5 · TypeScript 5 · Element Plus · Tiptap 2 · Pinia · Vue Router · ECharts 6 · vue-i18n(beta)

> 注:单元测试目前仅含脚手架示例,欢迎补充。
