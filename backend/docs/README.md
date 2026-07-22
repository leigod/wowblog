# WowBlog 文档

## 文档索引

| 文档 | 描述 |
|------|------|
| [DEPLOYMENT.md](DEPLOYMENT.md) | 部署指南 - 包含本地开发、Docker 和生产环境部署 |


## 快速链接

### 开发相关

- [API 文档](http://localhost:8000/docs) - Swagger UI（需启动服务）
- [环境变量配置](../.env.example) - 环境变量模板
- [依赖列表](../requirements.txt) - Python 依赖

### 部署相关

- [Docker 配置](../Dockerfile) - Docker 镜像构建
- [Docker Compose](../docker-compose.yml) - 容器编排配置
- [Nginx 配置示例](../docker/nginx/) - 反向代理配置（待创建）

## 测试

```bash
# 运行所有测试
pytest

# 使用虚拟环境中的 pytest
python -m pytest

# 或者
uv run pytest


# 运行特定标记的测试
pytest -m unit
pytest -m integration

# 查看覆盖率报告
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

## 贡献指南

1. 遵循 PEP 8 代码规范
2. 为新功能添加测试
3. 更新相关文档
4. 提交前运行 `pytest` 和 `mypy`

## 许可证

[待添加]
