"""add user blog tables (Author workspace)

Revision ID: b8d2e6f4a9c1
Revises: f6c8e2a4d7b3
Create Date: 2026-11-16 16:30:00.000000

Author 个人博客功能（Creator 工作台）数据层：
- wb_user_blogs:        blog 主配置（每个 Author 一行）：名称/简介/impressum/logo/favicon/社媒/布局
- wb_user_categories:   blog 分类（仅一级，可排序）——与平台多级分类(wb_categories)语义隔离
- wb_user_series:       blog 系列（可排序）
- wb_user_navs:         blog 导航（无系统项；类型仅 link/category/series）
- wb_articles 加 blog_category_id / blog_series_id：文章在自己 blog 里的归属（均可空），
  与平台分类 category_id（审核发布时由 Admin/Editor 选择，可空）互不影响。
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b8d2e6f4a9c1'
down_revision: Union[str, Sequence[str], None] = 'f6c8e2a4d7b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'wb_user_blogs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='博主用户ID（一人一行）'),
        sa.Column('blog_name', sa.String(length=100), nullable=True, comment='blog名称（空则前台回退显示用户名）'),
        sa.Column('blog_description', sa.String(length=300), nullable=True, comment='blog说明'),
        sa.Column('impressum', sa.Text(), nullable=True, comment='法律声明（blog页脚展示，部分司法辖区强制）'),
        sa.Column('logo', sa.String(length=255), nullable=True, comment='blog logo（建议 500x125 4:1 透明 PNG）'),
        sa.Column('favicon', sa.String(length=255), nullable=True, comment='blog favicon（建议 32x32/64x64 方形 PNG）'),
        sa.Column('social_links', sa.JSON(), nullable=True, comment='社媒账号列表 JSON：[{"platform":"github","url":"..."}]'),
        sa.Column('homepage_layout', sa.Enum('magazine', 'stacked', 'grid', name='userbloglayout'),
                  nullable=False, server_default='magazine', comment='首页布局风格'),
        sa.Column('createtime', sa.Integer(), nullable=True, comment='开通时间戳（版权年份起点）'),
        sa.Column('updatetime', sa.Integer(), nullable=True, comment='更新时间戳'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', name='uq_user_blogs_user_id'),
        mysql_charset='utf8mb4',
        mysql_engine='InnoDB',
    )
    op.create_index('ix_user_blogs_user_id', 'wb_user_blogs', ['user_id'])

    op.create_table(
        'wb_user_categories',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='归属博主用户ID'),
        sa.Column('name', sa.String(length=100), nullable=False, comment='分类名'),
        sa.Column('slug', sa.String(length=50), nullable=False, comment='URL slug（同用户内唯一）'),
        sa.Column('sort', sa.Integer(), nullable=True, comment='排序权重'),
        sa.Column('createtime', sa.Integer(), nullable=True, comment='创建时间戳'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'slug', name='uq_user_categories_user_slug'),
        mysql_charset='utf8mb4',
        mysql_engine='InnoDB',
    )
    op.create_index('ix_user_categories_user_id', 'wb_user_categories', ['user_id'])

    op.create_table(
        'wb_user_series',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='归属博主用户ID'),
        sa.Column('name', sa.String(length=100), nullable=False, comment='系列名'),
        sa.Column('description', sa.String(length=300), nullable=True, comment='系列说明'),
        sa.Column('sort', sa.Integer(), nullable=True, comment='排序权重'),
        sa.Column('createtime', sa.Integer(), nullable=True, comment='创建时间戳'),
        sa.PrimaryKeyConstraint('id'),
        mysql_charset='utf8mb4',
        mysql_engine='InnoDB',
    )
    op.create_index('ix_user_series_user_id', 'wb_user_series', ['user_id'])

    op.create_table(
        'wb_user_navs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='归属博主用户ID'),
        sa.Column('label', sa.String(length=50), nullable=False, comment='导航标签'),
        sa.Column('type', sa.Enum('link', 'category', 'series', name='usernavtype'),
                  nullable=False, comment='类型（无平台导航的系统项与页面类型）'),
        sa.Column('value', sa.String(length=100), nullable=False, comment='link=URL；category/series=对应表ID'),
        sa.Column('sort', sa.Integer(), nullable=True, comment='排序权重'),
        sa.Column('status', sa.Integer(), nullable=True, comment='1=显示 0=隐藏'),
        sa.Column('createtime', sa.Integer(), nullable=True, comment='创建时间戳'),
        sa.PrimaryKeyConstraint('id'),
        mysql_charset='utf8mb4',
        mysql_engine='InnoDB',
    )
    op.create_index('ix_user_navs_user_id', 'wb_user_navs', ['user_id'])

    op.add_column('wb_articles',
                  sa.Column('blog_category_id', sa.Integer(), nullable=True,
                            comment='文章在作者自己blog中的分类（wb_user_categories.id，可空）'))
    op.add_column('wb_articles',
                  sa.Column('blog_series_id', sa.Integer(), nullable=True,
                            comment='文章在作者自己blog中的系列（wb_user_series.id，可空）'))
    op.create_index('ix_articles_blog_category_id', 'wb_articles', ['blog_category_id'])
    op.create_index('ix_articles_blog_series_id', 'wb_articles', ['blog_series_id'])


def downgrade() -> None:
    op.drop_index('ix_articles_blog_series_id', table_name='wb_articles')
    op.drop_index('ix_articles_blog_category_id', table_name='wb_articles')
    op.drop_column('wb_articles', 'blog_series_id')
    op.drop_column('wb_articles', 'blog_category_id')
    op.drop_index('ix_user_navs_user_id', table_name='wb_user_navs')
    op.drop_table('wb_user_navs')
    op.drop_index('ix_user_series_user_id', table_name='wb_user_series')
    op.drop_table('wb_user_series')
    op.drop_index('ix_user_categories_user_id', table_name='wb_user_categories')
    op.drop_table('wb_user_categories')
    op.drop_index('ix_user_blogs_user_id', table_name='wb_user_blogs')
    op.drop_table('wb_user_blogs')
