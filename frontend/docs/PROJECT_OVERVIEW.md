# CMS Site 项目概览

## 项目简介

这是一个基于 Vue 3 + TypeScript 的 CMS（内容管理系统）项目，提供文章管理、分类/系列管理、页面管理、标签管理等功能。项目集成了强大的 Tiptap 富文本编辑器，支持暗黑模式和国际化。

## 技术栈

| 技术 | 版本 |
|------|------|
| **框架** | Vue 3.4.29 + TypeScript |
| **构建工具** | Vite 5.3.1 |
| **UI组件库** | Element Plus 2.7.8 + @layui/layui-vue |
| **状态管理** | Pinia 2.1.7 |
| **路由** | Vue Router 4.3.3 |
| **国际化** | vue-i18n |
| **富文本编辑器** | Tiptap 2.12+ |
| **图标** | Element Plus Icons + FontAwesome + Iconify |

## 项目结构

```
src/
├── api/                  # API 服务层
│   ├── http.ts          # HTTP 请求配置
│   ├── index.ts         # API 入口
│   └── services/        # 各业务模块 API
├── components/           # 组件
│   ├── layouts/         # 布局组件
│   ├── tiptap-icons/    # Tiptap 编辑器图标
│   ├── tiptap-ui/       # Tiptap UI 组件
│   ├── TiptapEditor.vue # 核心富文本编辑器
│   └── ...
├── extensions/           # Tiptap 扩展
│   ├── slash/           # 斜杠命令扩展
│   ├── mention/         # 提及扩展
│   └── linkitem/        # 链接项扩展
├── hooks/                # Vue 3 组合式 API hooks
├── lib/                  # 工具库
├── locale/               # 国际化文件
├── router/               # 路由配置
│   ├── index.ts         # 路由定义
│   └── permission.ts    # 权限守卫
├── stores/               # Pinia 状态管理
│   ├── app.ts           # 应用全局状态
│   └── counter.ts       # 示例状态
├── styles/               # 全局样式
│   ├── element/         # Element Plus 样式覆盖
│   └── dark/            # 暗黑模式样式
├── types/                # TypeScript 类型定义
├── views/                # 页面视图
│   ├── admin/           # 管理后台页面
│   ├── ArticleView.vue  # 文章详情页
│   ├── ListView.vue     # 列表页
│   └── ...
└── assets/               # 静态资源
```

## 核心功能模块

### 1. 内容管理系统

#### 文章管理
- 文章列表（分页、搜索、筛选）
- 创建/编辑文章（富文本编辑器）
- 文章状态管理（草稿、发布）
- 文章删除

#### 分类/系列管理
- 分类 CRUD 操作
- 系列 CRUD 操作
- 分类与文章关联

#### 页面管理
- 独立页面创建（关于页、联系页等）
- 页面内容编辑
- 动态路由支持 (`/page/:pageSlug`)

#### 标签管理
- 标签 CRUD 操作
- 标签与文章关联

#### 导航管理
- 导航菜单配置
- 菜单项排序

### 2. 富文本编辑器 (TiptapEditor)

**位置**: `src/components/TiptapEditor.vue` (2426行)

#### 功能特性

**文本格式化**
- 标题（H1, H2, H3）
- 加粗、斜体、下划线、删除线
- 文本颜色选择
- 高亮（多种颜色）

**列表**
- 无序列表
- 有序列表
- 任务列表（带复选框）

**对齐方式**
- 左对齐、居中、右对齐、两端对齐

**插入内容**
- 链接（支持新窗口打开）
- 图片（URL插入、本地上传）
- 水平分隔线
- 硬换行

**代码**
- 行内代码
- 代码块（语法高亮支持：JS, TS, CSS, HTML）

**表格**
- 插入表格
- 添加/删除行列
- 删除表格

**其他**
- 上标/下标
- 引用块
- 清除格式
- 撤销/重做

#### 交互特性
- 固定工具栏（移动端底部固定）
- 气泡菜单（选中文字时显示）
- 浮动菜单（空行时显示）
- 响应式设计

### 3. 用户系统

#### 认证功能
- 用户登录
- 用户注册
- 临时 Token（10分钟有效期）
- 权限控制（基于角色）

#### 用户资料
- 个人资料编辑
- 头像上传
- 用户信息展示

#### 角色类型
- Admin（管理员）
- User（普通用户）
- Editor（编辑）
- Contributor（贡献者）

### 4. 主题系统

#### 主题模式
- **跟随系统** - 自动跟随操作系统主题
- **浅色模式** - 固定浅色主题
- **深色模式** - 固定深色主题

#### 配置存储
- 用户配置保存在 `localStorage`
- 支持 `USER_CONFIG_KEY` 存储
- 配置项包括：
  - `language` - 界面语言
  - `admin_language` - 后台语言
  - `themeMode` - 主题模式
  - `followSystem` - 是否跟随系统

### 5. 国际化 (i18n)

#### 支持语言
- `zh-CN` - 简体中文
- `en-US` - 英文

#### 配置
- Vue I18n 10.0.0-beta.5
- Element Plus 多语言支持
- 语言切换实时生效

## 路由结构

### 前台路由
| 路径 | 组件 | 说明 |
|------|------|------|
| `/` | IndexView | 首页 |
| `/about` | AboutView | 关于页 |
| `/article/:slug` | ArticleView | 文章详情 |
| `/tag/:slug` | ListView | 标签文章列表 |
| `/category/:categorySlug` | CategoryView | 分类文章列表 |
| `/series/:seriesSlug` | SeriesView | 系列文章列表 |
| `/page/:pageSlug` | PageView | 动态页面 |
| `/profile/:username` | ProfileView | 用户资料 |
| `/profile/edit` | ProfileEditView | 编辑个人资料 |

### 认证路由
| 路径 | 组件 | 说明 |
|------|------|------|
| `/login` | LoginView | 登录页 |
| `/register` | RegisterView | 注册页 |

### 管理后台路由 (`/admin/*`)
| 路径 | 组件 | 说明 |
|------|------|------|
| `/admin/dashboard` | DashboardView | 控制台 |
| `/admin/settings` | SettingsView | 系统设置 |
| `/admin/articles` | ArticleManagementView | 文章管理 |
| `/admin/articles/create` | CreateArticleView | 创建文章 |
| `/admin/articles/edit/:id` | EditArticleView | 编辑文章 |
| `/admin/categories` | CategoryManagementView | 分类管理 |
| `/admin/categories/create` | CreateCategoryView | 创建分类 |
| `/admin/categories/edit/:id` | EditCategoryView | 编辑分类 |
| `/admin/series` | SeriesManagementView | 系列管理 |
| `/admin/series/create` | CreateSeriesView | 创建系列 |
| `/admin/series/edit/:id` | EditSeriesView | 编辑系列 |
| `/admin/pages` | PageManagementView | 页面管理 |
| `/admin/pages/create` | CreatePageView | 创建页面 |
| `/admin/pages/edit/:id` | EditPageView | 编辑页面 |
| `/admin/navbar` | NavbarManagementView | 导航管理 |
| `/admin/tags` | TagManagementView | 标签管理 |
| `/admin/members` | MemberManagementView | 成员管理 |
| `/admin/content-editor` | ContentEditorView | 内容编辑器 |

## 状态管理 (Pinia)

### app.ts - 应用全局状态

**State**
```typescript
{
  token: string | null           // 访问令牌
  userRole: string | null        // 用户角色
  userInfo: Userinfo             // 用户信息
  language: string               // 界面语言
  admin_language: string         // 后台语言
  isDark: boolean                // 是否深色模式
  isThemeFollowSystem: boolean   // 是否跟随系统
  loading: boolean               // 全局加载状态
  site_logo: string | null       // 站点Logo
  site_title: string | null      // 站点标题
  site_favicon: string | null    // 站点图标
  disable_comment: boolean       // 是否禁用评论
  dark_mode: string              // 深色模式设置
}
```

**Actions**
- `initTheme()` - 初始化主题
- `getTempToken()` - 获取临时令牌
- `fetchSiteConfig()` - 获取站点配置
- `applySiteConfig()` - 应用站点配置
- `setLanguage()` - 设置语言
- `toggleDarkMode()` - 切换深色模式
- `setDarkMode()` - 设置深色模式
- `setUserRole()` - 设置用户角色
- `setUserInfo()` - 设置用户信息
- `clearUserInfo()` - 清除用户信息

## 开发指南

### 环境要求
- Node.js 20+
- npm 或 yarn

### 安装依赖
```bash
npm install
```

### 开发运行
```bash
npm run dev
```

### 构建生产
```bash
npm run build
```

### 类型检查
```bash
npm run type-check
```

### 代码检查
```bash
npm run lint
```

### 运行测试
```bash
npm run test:unit
```

## 配置文件说明

### vite.config.ts
- Vue 3 插件配置
- JSX 支持
- 自动导入（Element Plus, LayuiVue）
- 路径别名 `@` 指向 `src`

### tsconfig.json
- TypeScript 编译配置
- 模块解析策略

### .env.local
环境变量配置文件（需手动创建，参考 `.env.example`）

## 常见问题

### Q: 如何添加新的 API 服务？
在 `src/api/services/` 下创建新的服务文件，然后在 `src/api/index.ts` 中导出。

### Q: 如何添加新的页面？
在 `src/views/` 下创建 Vue 组件，然后在 `src/router/index.ts` 中添加路由配置。

### Q: 如何修改 Tiptap 编辑器功能？
编辑 `src/components/TiptapEditor.vue` 或 `src/components/SlashEditor.vue`，修改扩展配置或工具栏按钮。

### Q: 如何添加新的国际化语言？
在 `src/locale/` 下添加新的语言文件（如 `ja-JP.ts`），然后在 `src/locale/index.ts` 中注册。

## 依赖说明

### 核心依赖
- `vue` - Vue 3 框架
- `vue-router` - 路由管理
- `pinia` - 状态管理
- `element-plus` - UI 组件库
- `@tiptap/*` - 富文本编辑器

### 开发依赖
- `vite` - 构建工具
- `typescript` - TypeScript 支持
- `eslint` - 代码检查
- `prettier` - 代码格式化
- `vitest` - 单元测试

## 更新日志

本文档生成日期: 2026-05-20

---

**注意**: 本文档基于项目当前状态生成，如有代码变更请及时更新文档内容。
