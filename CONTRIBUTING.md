# 贡献指南

感谢你对 WowBlog 的关注!欢迎通过 Issue 和 Pull Request 参与贡献。

## 开发环境

参考 [README.md](README.md) 的「快速开始」搭建本地环境。前置:Node ≥ 20、Python ≥ 3.13、MySQL、Redis。

## 代码规范

### 前端(`frontend/`)

- 使用 `<script setup lang="ts">` 与 Composition API
- 组件命名 PascalCase,样式使用 `scoped`
- 优先 TypeScript 严格模式,避免 `any`;必要时用类型守卫而非 `as unknown as T`
- 提交前运行:`npm run type-check && npm run lint`

### 后端(`backend/`)

- 遵循 PEP 8,使用 ruff 格式化、mypy 类型检查
- 分层架构:路由 → 服务 → CRUD → 模型,认证 / 会话用依赖注入
- 提交前运行:`ruff check . && mypy app && pytest`
- **安全红线**:密码必须用 bcrypt(禁止 MD5);密钥、Token、数据库连接串只能来自环境变量,严禁硬编码;用户输入必须校验

## 提交规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>: <description>
```

类型:`feat`、`fix`、`docs`、`refactor`、`test`、`chore`、`perf`、`ci`。

## Pull Request 流程

1. Fork 仓库,从 `main` 创建分支:`feat/<short-desc>` 或 `fix/<short-desc>`
2. 保证 `type-check`、`lint`、`test` 通过
3. PR 描述清晰,关联相关 Issue(如 `Closes #123`)
4. 等待 review,根据反馈迭代

## 报告 Bug / 提建议

通过 GitHub Issue 提交,尽量包含:

- 复现步骤
- 预期行为与实际行为
- 环境信息(操作系统、Node / Python 版本、浏览器、是否 Docker)
