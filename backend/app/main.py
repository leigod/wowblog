import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from app.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    general_exception_handler
)
from app.routers import blog, users, media, auth, docbook, doc, notifications, admin_comments, member_invitations, websocket
from app.internal import admin, upload, articles
from app.dependencies.authentication import get_current_active_admin_user
from app.utils.logger import cleanup_old_logs, compress_old_logs, DateRotatingFileHandler
from fastapi.responses import JSONResponse
from app.middleware.rate_limit import check_rate_limit, RATE_LIMITS

# 生产环境关闭交互式文档（/docs、/redoc、/openapi.json），开发环境保留
_is_production = os.getenv("ENVIRONMENT", "development").lower() == "production"


async def _log_cleanup_loop():
    """后台定时清理/压缩旧日志（每天一次），防止日志无界增长"""
    while True:
        await asyncio.sleep(86400)
        try:
            log_dir = DateRotatingFileHandler.BASE_LOG_DIR
            compress_old_logs(log_dir, days_to_keep=30)
            cleanup_old_logs(log_dir, days_to_keep=90)
        except Exception:
            pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动日志清理后台任务，关闭时取消"""
    task = asyncio.create_task(_log_cleanup_loop())
    yield
    task.cancel()


app = FastAPI(
    docs_url=None if _is_production else "/docs",
    redoc_url=None if _is_production else "/redoc",
    openapi_url=None if _is_production else "/openapi.json",
    lifespan=lifespan,
)

# 挂载静态文件目录
# 将/static路径映射到app/uploads目录，使上传的文件可以通过URL访问
app.mount("/static", StaticFiles(directory="app/uploads"), name="static")

# 配置 CORS
# 注意：当 allow_credentials=True 时，不能使用通配符 "*"
# 必须指定具体的前端地址
# 从 ALLOWED_ORIGINS 环境变量读取（逗号分隔）
# 注意：allow_credentials=True 时不能用通配符 "*"，必须指定具体地址
_default_origins = "http://localhost:5173,http://localhost:5174,http://localhost:5177"
origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", _default_origins).split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 注册异常处理器
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(blog.router, prefix="/api", tags=['blog'])
app.include_router(users.router, prefix='/api', tags=['users'])
app.include_router(media.router, prefix='/api', tags=['media'])
app.include_router(auth.router, prefix='/api', tags=['auth'])
app.include_router(
    admin.router,
    prefix='/api/admin',
    tags=['admin'],
    dependencies=[Depends(get_current_active_admin_user)],
    responses={404: {"description": "Not Found!"}}
)
app.include_router(upload.router, prefix='/api', tags=['upload'])
app.include_router(articles.router, prefix='/api/admin', tags=['articles'], dependencies=[Depends(get_current_active_admin_user)],
    responses={404: {"description": "Not Found!"}})

# 文档模块路由
app.include_router(docbook.router, prefix='/api', tags=['docbook'])
app.include_router(doc.router, prefix='/api', tags=['doc'])

# 通知模块路由
app.include_router(notifications.router, prefix='/api', tags=['notifications'])

# 评论管理模块路由
app.include_router(admin_comments.router, prefix='/api', tags=['admin_comments'])

# 成员邀请模块路由
app.include_router(member_invitations.router, prefix='/api', tags=['member_invitations'])

# WebSocket 路由
app.include_router(websocket.router, prefix='/api', tags=['websocket'])



@app.middleware("http")
async def global_rate_limit(request: Request, call_next):
    """全局限流兜底：跳过健康检查/静态资源，默认 300 次/分钟（多 worker 经 Redis 共享计数）"""
    path = request.url.path
    if path.startswith("/health") or path.startswith("/static"):
        return await call_next(request)
    try:
        max_req, window = RATE_LIMITS["default"]
        await check_rate_limit(
            request, max_requests=max_req, window_seconds=window, key_prefix="global"
        )
    except HTTPException as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=getattr(exc, "headers", None),
        )
    return await call_next(request)


@app.get("/health")
async def health():
    """健康检查端点（供容器 HEALTHCHECK / 负载均衡探活使用，不依赖数据库）"""
    return {"status": "ok"}


@app.get("/")
async def root():
    raise HTTPException(status_code=404, detail="Not found")
    # return {"message": "Hello Bigger Applications!"}