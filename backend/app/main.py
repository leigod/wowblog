import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.exc import SQLAlchemyError
from app.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    general_exception_handler
)
from app.routers import blog, users, media, auth, docbook, doc, notifications, admin_comments, member_invitations, websocket
from app.routers import admin_logs
from app.middleware.admin_audit import admin_audit_middleware
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


# 修正反代后的重定向协议降级：强制把 3xx 重定向 Location 的 http:// 改成 https://
# 背景：FastAPI 尾斜杠重定向(如 /users/me → /users/me/)生成的 Location，在 Apache 反代
# (ProxyPass 用 http://127.0.0.1:8000)时会降级成 http://，导致浏览器从 https 被重定向到 http 而失败。
# 宝塔 Apache 的 RequestHeader X-Forwarded-Proto 在反代场景不可靠，故在后端响应阶段直接强制修正。
@app.middleware("http")
async def _force_https_redirect(request, call_next):
    response = await call_next(request)
    # 仅生产环境(经 https 反代)修正协议降级；本地 http 开发不触发，避免把本地 http 重定向误改成 https
    if _is_production and response.status_code in (301, 302, 307, 308):
        location = response.headers.get("location")
        if location and location.startswith("http://"):
            response.headers["location"] = "https://" + location[len("http://"):]
    return response


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

# Session 中间件：authlib OAuth 的 state / nonce 经由签名 cookie 中转（无状态，多 worker 友好）。
# 密钥优先用独立的 SESSION_SECRET_KEY，留空则回退到 JWT_SECRET_KEY（开发平滑），生产环境必须显式设置。
_session_secret = os.getenv("SESSION_SECRET_KEY") or os.getenv("JWT_SECRET_KEY")
if not _session_secret:
    if _is_production:
        raise ValueError("SESSION_SECRET_KEY（或 JWT_SECRET_KEY）在生产环境必须设置")
    _session_secret = "dev-session-secret-change-me"
app.add_middleware(
    SessionMiddleware,
    secret_key=_session_secret,
    max_age=600,          # 10 分钟，足够完成一次 OAuth 授权往返
    same_site="lax",
    https_only=_is_production,
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

# 管理员操作日志（审计中间件自动写入，此处提供查询）
app.include_router(admin_logs.router, prefix='/api/admin', tags=['admin_logs'])

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


# 管理员操作审计：记录后台写操作 + 登录/登出（最后注册 = 最外层，记录最终响应码）
# 写入失败只 warning 不影响主请求；详见 app/middleware/admin_audit.py
@app.middleware("http")
async def admin_audit(request: Request, call_next):
    return await admin_audit_middleware(request, call_next)


@app.get("/health")
async def health():
    """健康检查端点（供容器 HEALTHCHECK / 负载均衡探活使用，不依赖数据库）"""
    return {"status": "ok"}


@app.get("/")
async def root():
    raise HTTPException(status_code=404, detail="Not found")
    # return {"message": "Hello Bigger Applications!"}