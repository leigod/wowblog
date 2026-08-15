# 多阶段构建 Dockerfile for WowBlog Backend
# Stage 1: 构建阶段——把依赖装入 /opt/venv（固定路径，不依赖任何用户家目录）
FROM python:3.13-slim AS builder

WORKDIR /build

# 说明：requirements 全部依赖均有 manylinux 预编译 wheel 或为纯 Python（bcrypt/
# cryptography/pillow/pydantic-core 等官方二进制分发），无需 gcc/g++ 现场编译。
# 旧版在这里 apt-get 装 gcc/g++，会访问境外 Debian 源，国内服务器极慢，已移除。
# 若未来新增无 wheel 的源码包，构建会当场报错（fail fast），届时再按需加回编译器
# 并换成国内镜像源（如 mirrors.aliyun.com）。

# 复制依赖文件
COPY requirements.txt .

# 建虚拟环境并装入依赖（venv 固定在 /opt/venv，默认 755 权限，任意用户可读可执行）
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt


# Stage 2: 运行阶段
FROM python:3.13-slim

# PATH 指向 venv，确保 appuser 能直接执行 uvicorn
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

# 创建非 root 用户
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# 从构建阶段复制虚拟环境
COPY --from=builder /opt/venv /opt/venv

# 复制项目文件
COPY . .

# 创建必要的目录并归属给 appuser
RUN mkdir -p app/logs app/uploads && \
    chown -R appuser:appuser /app

# 切换到非 root 用户
USER appuser

EXPOSE 8000

# 健康检查：打 /health 端点（与 /docs 解耦）
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health').status==200 else 1)" || exit 1

# 启动命令
# 先跑 alembic 迁移再启动服务（迁移失败则容器拒绝启动——fail fast，
# DB 结构不匹配时不应带病运行）。首次对新库部署：baseline(cd6757a448f8) 为空操作，
# 会从 wb_user_oauth 起依次建表/加列，与 dump 导入的存量结构兼容。
# --proxy-headers：信任反代（Nginx/Apache）转发的 X-Forwarded-Proto/For，使后端知晓真实 https 协议，
# 避免 FastAPI 尾斜杠重定向(307)把 Location 降级成 http（反代 https 场景必加）
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --workers 4"]
