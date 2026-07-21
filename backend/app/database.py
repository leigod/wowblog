from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from datetime import datetime
from app.models.response import ApiResponse
import os

# 首先加载环境变量（必须在读取环境变量之前调用）
from dotenv import load_dotenv
load_dotenv()

# 从环境变量读取数据库配置，如果不存在则使用默认值（仅用于开发）
DATABASE_HOST = os.getenv('DATABASE_HOST', '127.0.0.1')
DATABASE_PORT = os.getenv('DATABASE_PORT', '8889')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'wowblog')
DATABASE_USER = os.getenv('DATABASE_USER', 'root')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')

# 验证必要的环境变量
if not DATABASE_PASSWORD:
    raise ValueError(
        "DATABASE_PASSWORD environment variable not set. "
        "Please set it in your .env file or environment."
    )

# MySQL连接配置
DATABASE_URL = f"mysql+aiomysql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

# 创建数据库引擎
# 连接池配置优化
# - pool_size: 常驻连接数，根据应用并发需求调整
# - max_overflow: 额外连接数，在高峰期使用
# - pool_pre_ping: 连接健康检查，防止连接超时
# - pool_recycle: 连接回收时间，防止数据库断开连接
# - pool_timeout: 获取连接的超时时间
# - echo: SQL日志（生产环境应关闭）
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,           # 常驻连接池大小
    max_overflow=20,         # 额外连接数
    pool_pre_ping=True,     # 启用连接健康检查
    pool_recycle=3600,      # 1小时后自动回收连接
    pool_timeout=30,        # 获取连接超时时间（秒）
    echo=False,             # 生产环境关闭SQL日志
    connect_args={
        "charset": "utf8mb4",
        "connect_timeout": 10
    }
)

AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# 异步依赖项
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# def success(msg: str = 'ok', data: any = None) -> ApiResponse:
#     return ApiResponse(
#         msg=msg,
#         time=int(datetime.now().timestamp()),
#         data=data
#     )


# 基础模型类
Base = declarative_base()
