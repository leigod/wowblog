# WowBlog

> 一个基于 Vue 3 + FastAPI 的现代内容管理系统(CCMS)/博客系统,前后端分离,支持富文本编辑、多角色权限、实时通知、文章推荐与中英双语。

<!-- 📸 建议在此放置项目截图或 GIF(可将图片放到 docs/screenshot.png 后取消下面注释)-->
<!-- ![WowBlog 截图](docs/screenshot.png) -->

## ✨ 功能特性

- 📝 富文本编辑(Tiptap),支持文章 / 文档 / 文档书多级内容
- 👥 多角色权限(Admin / Editor / Contributor 等),基于权限位的细粒度控制
- 🔐 JWT 认证 + bcrypt 密码哈希,可选接入 Apple / Google / GitHub OAuth
- 🔔 WebSocket 实时通知与消息推送
- 📊 文章浏览统计与推荐接口
- 🌐 中英双语(i18n)
- 🗄️ MySQL + Redis(限流 / 缓存),Alembic 管理迁移
- 🐳 一键 Docker 部署(含 Nginx 反代)

## 🛠 技术栈

| 层 | 技术 |
|---|---|
| **前端** | Vue 3.4 · Vite 5 · TypeScript 5 · Element Plus · Tiptap 2 · Pinia · Vue Router · ECharts 6 · vue-i18n(beta) |
| **后端** | Python 3.13 · FastAPI · SQLAlchemy 2.0(async)· aiomysql · Redis · Alembic · PyJWT · bcrypt |
| **基础设施** | MySQL 8 · Redis 7 · Nginx · Docker Compose |

## 📁 项目结构

```
wowblog/
├── frontend/            # Vue 3 前端
│   ├── src/
│   └── docs/
├── backend/             # FastAPI 后端
│   ├── app/
│   │   ├── routers/     # 路由层(11 个模块)
│   │   ├── crud/        # 数据访问层
│   │   ├── models/      # ORM 模型 + Pydantic schemas
│   │   ├── services/    # 业务逻辑层
│   │   ├── middleware/  # 限流等中间件
│   │   └── ...
│   ├── alembic/         # Alembic 迁移(目前仅 baseline)
│   ├── migrations/      # 历史 SQL 迁移(业务表 schema 来源)
│   └── docker/          # Nginx / MySQL 初始化配置
├── LICENSE
└── README.md
```

## 🚀 快速开始

### 前置要求

- **Node.js** ≥ 20
- **Python** ≥ 3.13
- **Docker** & **Docker Compose**(推荐,一键拉起 MySQL/Redis/后端)

### 方式一:Docker 一键启动(推荐)

后端依赖 MySQL 与 Redis,使用 Docker Compose 最省心:

```bash
cd backend
cp .env.example .env          # 按需修改,生产环境务必设置强随机的 JWT_SECRET_KEY
docker compose up -d --build
```

启动后:

- 后端 API:http://localhost:8000
- 健康检查:http://localhost:8000/health
- API 文档(开发环境):http://localhost:8000/docs

前端开发模式:

```bash
cd frontend
cp .env.example .env.local    # 配置 VITE_API_BASE_URL
npm install
npm run dev                   # http://localhost:5173
```

### 方式二:本地开发(不使用 Docker)

需自行准备 MySQL 与 Redis。

```bash
# 后端
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env           # 配置数据库、Redis、JWT_SECRET_KEY
uvicorn app.main:app --reload --port 8000

# 前端
cd frontend
npm install
npm run dev
```

## ⚙️ 环境变量

前后端各有独立的 `.env.example`,复制为 `.env`(后端)/ `.env.local`(前端)后修改:

- 前端:`frontend/.env.example`(`VITE_API_BASE_URL` 等)
- 后端:`backend/.env.example`(数据库、JWT、CORS、Redis、SMTP、OAuth 等)

> ⚠️ 生产环境**必须**设置强随机的 `JWT_SECRET_KEY`,切勿使用默认或开发值。`JWT_SECRET_KEY` 缺失时,生产环境会拒绝启动。

## 🗃 数据库迁移

项目使用 Alembic 管理 schema,目前仅包含 baseline 初始化;业务表结构以 `backend/migrations/*.sql` 为准。首次部署需:

```bash
cd backend
alembic upgrade head                              # 初始化 Alembic baseline
mysql -u <user> -p <db> < migrations/*.sql        # 执行业务表结构 SQL
```

## 📜 常用脚本

**前端**(`cd frontend`):

| 命令 | 用途 |
|---|---|
| `npm run dev` | 启动开发服务器 |
| `npm run build` | 生产构建(自动剔除 `console`) |
| `npm run type-check` | TypeScript 类型检查 |
| `npm run lint` | ESLint 检查并自动修复 |
| `npm run test:unit` | 单元测试(Vitest) |

**后端**(`cd backend`):

| 命令 | 用途 |
|---|---|
| `uvicorn app.main:app --reload` | 启动开发服务器 |
| `pytest` | 运行测试(需 MySQL/Redis) |
| `alembic upgrade head` | 执行数据库迁移 |

## 📦 部署

详见 [backend/docs/DEPLOYMENT.md](backend/docs/DEPLOYMENT.md)(本地 / Docker / 生产)。

## 🤝 贡献

欢迎提 Issue 与 Pull Request!请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

提交信息遵循 [Conventional Commits](https://www.conventionalcommits.org/):`feat`、`fix`、`docs`、`refactor`、`test`、`chore`、`perf`、`ci`。

## 📄 许可证

[MIT License](LICENSE) © 2026 leigod
