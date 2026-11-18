"""wb_articles.category_id allow NULL

Revision ID: c9e1f5a8b3d6
Revises: b8d2e6f4a9c1
Create Date: 2026-11-16 22:15:00.000000

Author（Creator 工作台）发布文章时平台分类由审核者后续指定，
category_id 必须允许为空（与 schema/前端「网站分类可选」对齐）。
series_id 本就允许 NULL，无需处理。
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c9e1f5a8b3d6'
down_revision: Union[str, Sequence[str], None] = 'b8d2e6f4a9c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'wb_articles', 'category_id',
        existing_type=sa.Integer(),
        nullable=True,
        comment='平台分类（审核发布时由 Admin/Editor 选择，Author 提交时可为空）',
    )


def downgrade() -> None:
    # 回滚前需保证无 NULL 行，否则会失败（这也是预期行为）
    op.alter_column('wb_articles', 'category_id',
                    existing_type=sa.Integer(), nullable=False)
