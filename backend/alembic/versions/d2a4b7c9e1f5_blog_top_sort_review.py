"""blog_top/blog_sort + article_review_enabled

Revision ID: d2a4b7c9e1f5
Revises: c9e1f5a8b3d6
Create Date: 2026-11-17 13:30:00.000000

1. wb_articles 加 blog_top / blog_sort：仅影响文章在作者个人 blog 内的排序
   （置顶与自定义顺序），与平台维度的 is_pin / sort 互不影响。
2. wb_config 加 article_review_enabled：文章审核总开关（默认 1=开启）。
   开启时 blog 工作台发布/更新文章隐藏发布状态选择（固定草稿，由审核者放行）；
   关闭时作者可自行选择发布状态。
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd2a4b7c9e1f5'
down_revision: Union[str, Sequence[str], None] = 'c9e1f5a8b3d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('wb_articles',
                  sa.Column('blog_top', sa.Integer(), nullable=False, server_default='0',
                            comment='个人blog内置顶：1=置顶（焦点区优先），0=普通'))
    op.add_column('wb_articles',
                  sa.Column('blog_sort', sa.Integer(), nullable=False, server_default='0',
                            comment='个人blog内排序权重（大者靠前），与置顶组合生效'))
    op.add_column('wb_config',
                  sa.Column('article_review_enabled', sa.Integer(), nullable=False, server_default='1',
                            comment='文章审核开关：1=开启（作者发布固定草稿待审核），0=关闭（作者可选发布状态）'))


def downgrade() -> None:
    op.drop_column('wb_config', 'article_review_enabled')
    op.drop_column('wb_articles', 'blog_sort')
    op.drop_column('wb_articles', 'blog_top')
