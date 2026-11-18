"""add missing user profile columns

补齐 wb_users 的个人资料扩展列。这些列从未有独立的 alembic 迁移，只存在于
全量 SQL（wowblog.sql）中。凡是靠 alembic 从旧结构一路升级上来的库（如生产），
都不会有这些列，导致 get_blog_site 直接 select(User.social_profiles) 时抛
SQLAlchemyError -> 500。

本迁移幂等：通过 information_schema 逐列检查，已存在则跳过，缺失才添加。
这样本地库（列齐全）和生产库（可能缺列）跑 upgrade head 都安全。

Revision ID: f7a3c1e9d4b2
Revises: d2a4b7c9e1f5
Create Date: 2026-11-18 18:40:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f7a3c1e9d4b2'
down_revision: Union[str, Sequence[str], None] = 'd2a4b7c9e1f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# 需要保证存在的列（与全量 SQL wowblog.sql 定义保持一致）
COLUMNS = [
    ('profile_tagline', sa.String(100)),
    ('location', sa.String(100)),
    ('gender', sa.Integer()),
    ('birthday', sa.Integer()),
    ('school', sa.String(100)),
    ('profile_bio', sa.Text()),
    ('tech_stack', sa.String(300)),
    ('available_for', sa.String(300)),
    ('social_profiles', sa.Text()),
    ('updatetime', sa.Integer()),
    ('notification_check_at', sa.Integer()),
    ('privacy_show_bookmarks', sa.Integer()),
    ('privacy_show_likes', sa.Integer()),
    ('privacy_show_comments', sa.Integer()),
    ('privacy_show_views', sa.Integer()),
]


def _existing_columns() -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    try:
        return {c['name'] for c in inspector.get_columns('wb_users')}
    except Exception:
        # 表都不存在时交由后续迁移/全量 SQL 处理，此处不重复建表
        return set()


def upgrade() -> None:
    existing = _existing_columns()
    for name, col_type in COLUMNS:
        if name in existing:
            continue
        op.add_column('wb_users', sa.Column(name, col_type, nullable=True))


def downgrade() -> None:
    # 补列迁移不回退：避免误删生产库中的真实资料数据。
    pass
