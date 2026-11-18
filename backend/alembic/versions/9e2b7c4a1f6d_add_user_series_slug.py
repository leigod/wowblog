"""add missing wb_user_series.slug column

生产库由 alembic 从旧结构升级而来：b8d2e6f4a9c1 建 wb_user_series 时没有 slug，
slug 后来只补进了全量 SQL（wowblog.sql）。公开 blog 接口 get_blog_site 会
select UserSeries 全字段（含 slug），生产库因此抛
(1054, "Unknown column 'wb_user_series.slug' in 'field list'") -> 500。

本迁移幂等：information_schema 检查列是否存在，已存在则跳过；补列后为历史行
回填按名称生成的 slug（同用户内唯一），避免已有系列在公开页无法访问。

Revision ID: 9e2b7c4a1f6d
Revises: f7a3c1e9d4b2
Create Date: 2026-11-18 20:30:00

"""
from typing import Sequence, Union
import re

from alembic import op
import sqlalchemy as sa

try:
    from pypinyin import lazy_pinyin
except ImportError:  # 降级：迁移不因可选依赖缺失而失败
    lazy_pinyin = None


revision: str = '9e2b7c4a1f6d'
down_revision: Union[str, Sequence[str], None] = 'f7a3c1e9d4b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


MAX_SLUG_LEN = 50
_ASCII_RE = re.compile(r'[a-zA-Z0-9_-]')


def _base_slug(name: str) -> str:
    """与 app.utils.blog_slug.slug_from_name 同口径：中文转拼音，只留 a-z0-9_-。"""
    text = (name or '').strip().lower().replace(' ', '_').replace(',', '-')
    if any('\u4e00' <= ch <= '\u9fff' for ch in text) and lazy_pinyin is not None:
        text = '_'.join(lazy_pinyin(text))
    return ''.join(ch for ch in text if _ASCII_RE.match(ch))[:MAX_SLUG_LEN] or 'item'


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    try:
        existing = {c['name'] for c in inspector.get_columns('wb_user_series')}
    except Exception:
        # 表不存在时不做任何事：这不是本迁移负责创建的表
        return

    if 'slug' not in existing:
        op.add_column(
            'wb_user_series',
            sa.Column('slug', sa.String(length=50), nullable=True,
                      comment='URL slug（同用户内唯一）'),
        )

    # 历史行回填：只处理 slug 为空的记录，按 id 顺序生成确定性后缀，便于复现
    rows = bind.execute(sa.text(
        "SELECT id, user_id, name FROM wb_user_series "
        "WHERE slug IS NULL OR slug = '' ORDER BY id ASC"
    )).fetchall()
    used: dict[int, set[str]] = {}
    for row in rows:
        base = _base_slug(row.name or '')
        seen = used.setdefault(row.user_id, set())
        candidate = base
        index = 2
        while candidate in seen:
            suffix = f'_{index}'
            candidate = f'{base[:MAX_SLUG_LEN - len(suffix)]}{suffix}'
            index += 1
        bind.execute(
            sa.text('UPDATE wb_user_series SET slug = :slug WHERE id = :id'),
            {'slug': candidate, 'id': row.id},
        )
        seen.add(candidate)


def downgrade() -> None:
    # 不删列：slug 可能已被前台链接引用，回退会直接造成 404
    pass
