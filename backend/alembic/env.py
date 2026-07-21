from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

import os
from dotenv import load_dotenv

# 加载 .env，并导入 app 的 Base.metadata。
# 所有 model 必须被 import 才会注册到 Base.metadata，故导入 app.main 兜底（router→crud→model 链全覆盖）。
load_dotenv()
from app.database import Base  # noqa: E402
import app.main  # noqa: E402,F401  确保全部 model 注册到 metadata

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# alembic 用同步驱动；app 用 aiomysql，这里换成 pymysql 构造同步 URL
_db_user = os.getenv("DATABASE_USER", "root")
_db_pass = os.getenv("DATABASE_PASSWORD", "")
_db_host = os.getenv("DATABASE_HOST", "127.0.0.1")
_db_port = os.getenv("DATABASE_PORT", "3306")
_db_name = os.getenv("DATABASE_NAME", "wowblog")
config.set_main_option(
    "sqlalchemy.url",
    f"mysql+pymysql://{_db_user}:{_db_pass}@{_db_host}:{_db_port}/{_db_name}",
)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """离线模式：仅生成 SQL 脚本，不连库"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """在线模式：连库执行迁移"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
