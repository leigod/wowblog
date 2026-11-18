"""WowBlog 后端启动脚本。

生产部署优先用 gunicorn(见 docs/宝塔面板部署.md B.2):

    gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000

本脚本用于不便使用 gunicorn 的场景,例如宝塔 Python 项目管理器的「Python」启动方式:

    python run.py

host / port 可用环境变量 APP_HOST / APP_PORT 覆盖(默认 127.0.0.1:8000)。
"""
import os

import uvicorn

if __name__ == "__main__":
    host = os.getenv("APP_HOST", "127.0.0.1")
    port = int(os.getenv("APP_PORT", "8000"))
    # 开发时 APP_RELOAD=1 开启热重载（改代码自动生效）；生产环境默认关闭。
    # reload_excludes 排除日志目录：日志写入 app/logs/ 会触发热重载，
    # 形成「请求→写日志→重启→请求失败」死循环（间歇性 CORS/连接失败元凶）。
    reload = os.getenv("APP_RELOAD", "").lower() in ("1", "true", "yes")
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        reload_excludes=["app/logs/*", "logs/*", "*.log"] if reload else None,
    )
