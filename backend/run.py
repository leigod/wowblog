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
    uvicorn.run("app.main:app", host=host, port=port)
