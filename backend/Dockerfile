# 多阶段构建 Dockerfile for WowBlog Backend
# Stage 1: 构建阶段——把依赖装入 /opt/venv（固定路径，不依赖任何用户家目录）
FROM python:3.13-slim AS builder

WORKDIR /build

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

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
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
