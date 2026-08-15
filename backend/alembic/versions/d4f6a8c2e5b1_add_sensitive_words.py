"""add wb_sensitive_words + config switch

Revision ID: d4f6a8c2e5b1
Revises: c3d5e7f9b2a4
Create Date: 2026-08-13 18:00:00.000000

启用"敏感词过滤"功能（此前 model/router 骨架已存在但表未建）：
  1. 建 wb_sensitive_words 敏感词表（type 三档: banned 拦截 / review 标记审核 / replace 替换）
  2. wb_config 加 sensitive_words_enabled 开关列（0=关闭过滤，1=启用）

注：MySQL 索引名为表内唯一（idx_word/idx_type/idx_status 与其他表同名不冲突；
此前 sqlite create_all 的全局索引冲突是 sqlite 特性，不影响 MySQL）。
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd4f6a8c2e5b1'
down_revision: Union[str, Sequence[str], None] = 'c3d5e7f9b2a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'wb_sensitive_words',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('word', sa.String(length=100), nullable=False, comment='敏感词'),
        sa.Column('type', sa.String(length=20), nullable=True, comment='类型: banned(禁止)/review(需审核)/replace(替换)'),
        sa.Column('replacement', sa.String(length=100), nullable=True, comment='替换内容'),
        sa.Column('category', sa.String(length=50), nullable=True, comment='分类: politics/porn/adult/spam/other'),
        sa.Column('status', sa.String(length=20), nullable=True, comment='状态: active/inactive'),
        sa.Column('created_at', sa.Integer(), nullable=True, comment='创建时间'),
        sa.Column('created_by', sa.Integer(), nullable=True, comment='创建人ID'),
        sa.PrimaryKeyConstraint('id'),
        mysql_charset='utf8mb4',
        mysql_engine='InnoDB',
    )
    op.create_index('idx_word', 'wb_sensitive_words', ['word'], unique=False)
    op.create_index('idx_type', 'wb_sensitive_words', ['type'], unique=False)
    op.create_index('idx_status', 'wb_sensitive_words', ['status'], unique=False)

    op.add_column('wb_config', sa.Column('sensitive_words_enabled', sa.Integer(), nullable=True, comment='是否启用敏感词过滤，0=关闭，1=启用'))

    # 评论审核链路补齐：此前 audit_status 等列 DB/model 双缺，评论管理"审核"功能一直空转
    # （crud 里 hasattr 防御直接 return None，即用户遇到的"改审核状态无响应"根因）
    op.add_column('wb_comments', sa.Column('audit_status', sa.String(length=20), nullable=False, server_default='approved', comment='审核状态: pending/approved/rejected'))
    op.add_column('wb_comments', sa.Column('updatetime', sa.Integer(), nullable=True, comment='更新时间'))
    op.add_column('wb_comments', sa.Column('reviewed_by', sa.Integer(), nullable=True, comment='审核人ID'))
    op.add_column('wb_comments', sa.Column('reviewed_at', sa.Integer(), nullable=True, comment='审核时间'))


def downgrade() -> None:
    op.drop_column('wb_comments', 'reviewed_at')
    op.drop_column('wb_comments', 'reviewed_by')
    op.drop_column('wb_comments', 'updatetime')
    op.drop_column('wb_comments', 'audit_status')
    op.drop_column('wb_config', 'sensitive_words_enabled')
    op.drop_index('idx_status', table_name='wb_sensitive_words')
    op.drop_index('idx_type', table_name='wb_sensitive_words')
    op.drop_index('idx_word', table_name='wb_sensitive_words')
    op.drop_table('wb_sensitive_words')
