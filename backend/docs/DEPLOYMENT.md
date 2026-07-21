# WowBlog 后端部署指南

本文档提供 WowBlog 后端项目的完整部署指南。

## 目录

- [系统要求](#系统要求)
- [本地开发部署](#本地开发部署)
- [Docker 部署](#docker-部署)
- [生产环境部署](#生产环境部署)
- [环境变量配置](#环境变量配置)
- [数据库迁移](#数据库迁移)
- [性能优化](#性能优化)
- [监控和日志](#监控和日志)
- [故障排查](#故障排查)

---

## 系统要求

### 最低要求

- **Python**: 3.13+
- **MySQL**: 8.0+
- **内存**: 512MB
- **磁盘**: 1GB

### 推荐配置

- **CPU**: 2核心
- **内存**: 2GB
- **磁盘**: 10GB SSD

---

## 本地开发部署

### 1. 克隆项目

```bash
git clone https://github.com/your-repo/wowblog.git
cd wowblog
```

### 2. 创建虚拟环境

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入实际配置
```

### 5. 初始化数据库

```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE wowblog CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 运行迁移（如果有）
# alembic upgrade head
```

### 6. 启动服务

```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 7. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Docker 部署

### 1. 使用 Docker Compose（推荐）

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 停止并删除数据
docker-compose down -v
```

### 2. 单独构建和运行

```bash
# 构建镜像
docker build -t wowblog:latest .

# 运行容器
docker run -d \
  --name wowblog \
  -p 8000:8000 \
  --env-file .env \
  wowblog:latest
```

### 3. Docker 环境变量

创建 `.env` 文件或使用 `docker-compose.yml` 中的环境变量部分。

---

## 生产环境部署

### 1. 使用 Gunicorn + Uvicorn

#### 安装 Gunicorn

```bash
pip install gunicorn
```

#### 启动命令

```bash
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile - \
  --log-level info
```

### 2. 使用 Systemd 服务

创建服务文件 `/etc/systemd/system/wowblog.service`:

```ini
[Unit]
Description=WowBlog FastAPI Application
After=network.target mysql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/wowblog
Environment="PATH=/var/www/wowblog/.venv/bin"
ExecStart=/var/www/wowblog/.venv/bin/gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile /var/log/wowblog/access.log \
    --error-logfile /var/log/wowblog/error.log \
    --log-level info

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启用并启动服务:

```bash
sudo systemctl daemon-reload
sudo systemctl enable wowblog
sudo systemctl start wowblog
sudo systemctl status wowblog
```

### 3. 使用 Nginx 反向代理

配置文件 `/etc/nginx/sites-available/wowblog`:

```nginx
upstream wowblog_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL 证书配置
    ssl_certificate /etc/ssl/certs/wowblog.crt;
    ssl_certificate_key /etc/ssl/private/wowblog.key;

    # SSL 安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # 客户端最大请求大小
    client_max_body_size 10M;

    # 静态文件
    location /static/ {
        alias /var/www/wowblog/app/uploads/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # API 代理
    location /api/ {
        proxy_pass http://wowblog_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # 超时配置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 健康检查
    location /health {
        proxy_pass http://wowblog_backend/health;
        access_log off;
    }
}
```

启用配置:

```bash
sudo ln -s /etc/nginx/sites-available/wowblog /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 环境变量配置

### 必需变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `DATABASE_PASSWORD` | 数据库密码 | `secure_password` |
| `JWT_SECRET_KEY` | JWT 签名密钥 | 随机 32 字符串 |

### 生成 JWT 密钥

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 数据库迁移

### 使用 Alembic（如果已配置）

```bash
# 初始化 Alembic（首次）
alembic init alembic

# 生成迁移
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

### 手动执行 SQL

```bash
mysql -u root -p wowblog < schema.sql
```

---

## 性能优化

### 1. 数据库优化

```sql
-- 创建索引
CREATE INDEX idx_articles_created ON articles(createtime);
CREATE INDEX idx_articles_author ON articles(author_id);
CREATE INDEX idx_articles_status ON articles(status);

-- 配置优化（my.cnf）
[mysqld]
innodb_buffer_pool_size = 1G
max_connections = 200
query_cache_size = 64M
```

### 2. 应用优化

- **工作进程数**: CPU 核心数 × 2 + 1
- **连接池大小**: 10-20
- **启用缓存**: Redis 或 Memcached

### 3. 使用 CDN

将静态资源（图片、CSS、JS）托管到 CDN。

---

## 监控和日志

### 1. 日志配置

```python
# app/logging_config.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app/logs/app.log'),
        logging.StreamHandler()
    ]
)
```

### 2. 使用 Prometheus 监控

```python
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)
```

### 3. 健康检查端点

```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}
```

---

## 故障排查

### 常见问题

#### 1. 数据库连接失败

```bash
# 检查数据库状态
sudo systemctl status mysql

# 检查连接
mysql -u wowblog -p -h localhost

# 检查防火墙
sudo ufw allow 3306
```

#### 2. 服务启动失败

```bash
# 查看日志
sudo journalctl -u wowblog -n 50

# 检查端口占用
sudo lsof -i :8000
```

#### 3. 权限问题

```bash
# 修正文件权限
sudo chown -R www-data:www-data /var/www/wowblog
sudo chmod -R 755 /var/www/wowblog
```

---

## 安全检查清单

部署前确认：

- [ ] 更改所有默认密码
- [ ] 设置 `DEBUG=false`
- [ ] 配置 HTTPS/SSL
- [ ] 限制 CORS 源
- [ ] 启用速率限制
- [ ] 配置防火墙
- [ ] 定期备份数据库
- [ ] 更新依赖包
- [ ] 审查日志配置

---

## 备份策略

### 数据库备份

```bash
# 每日备份脚本
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/mysql"
mysqldump -u root -p wowblog | gzip > $BACKUP_DIR/wowblog_$DATE.sql.gz

# 保留最近 7 天
find $BACKUP_DIR -name "wowblog_*.sql.gz" -mtime +7 -delete
```

### 文件备份

```bash
# 备份上传文件
rsync -avz /var/www/wowblog/app/uploads /backup/uploads
```

---

## 更新部署

### 零停机更新

```bash
# 1. 拉取新代码
git pull origin main

# 2. 激活虚拟环境并更新依赖
source .venv/bin/activate
pip install -r requirements.txt

# 3. 运行数据库迁移
alembic upgrade head

# 4. 重启服务（逐个重启）
sudo systemctl reload wowblog@1
sudo systemctl reload wowblog@2
# ...
```

---

## 联系支持

如有问题，请联系：

- Email: support@example.com
- GitHub Issues: https://github.com/your-repo/wowblog/issues
