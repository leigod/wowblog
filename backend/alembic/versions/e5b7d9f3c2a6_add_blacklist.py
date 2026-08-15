"""add wb_blacklist

Revision ID: e5b7d9f3c2a6
Revises: d4f6a8c2e5b1
Create Date: 2026-08-13 20:00:00.000000

启用"禁评黑名单"功能（此前 model/CRUD/router 骨架已存在但表未建）：
wb_blacklist 用户行为级黑名单（type=comment 禁评，独立于 wb_users.status=block 登录级封禁）。
expire_at 为 NULL 表示永久；到期由查询端惰性判断（expire_at > now），无需定时任务。
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e5b7d9f3c2a6'
down_revision: Union[str, Sequence[str], None] = 'd4f6a8c2e5b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'wb_blacklist',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='用户ID'),
        sa.Column('type', sa.String(length=20), nullable=True, comment='限制类型: comment/post/login'),
        sa.Column('reason', sa.String(length=200), nullable=True, comment='拉黑原因'),
        sa.Column('admin_id', sa.Integer(), nullable=True, comment='操作管理员ID'),
        sa.Column('note', sa.Text(), nullable=True, comment='备注'),
        sa.Column('expire_at', sa.Integer(), nullable=True, comment='过期时间，NULL表示永久'),
        sa.Column('status', sa.String(length=20), nullable=True, comment='状态: active/inactive'),
        sa.Column('created_at', sa.Integer(), nullable=True, comment='创建时间'),
        sa.Column('updated_at', sa.Integer(), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        mysql_charset='utf8mb4',
        mysql_engine='InnoDB',
    )
    op.create_index('idx_user_id', 'wb_blacklist', ['user_id'], unique=False)
    op.create_index('idx_type', 'wb_blacklist', ['type'], unique=False)
    op.create_index('idx_status', 'wb_blacklist', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_status', table_name='wb_blacklist')
    op.drop_index('idx_type', table_name='wb_blacklist')
    op.drop_index('idx_user_id', table_name='wb_blacklist')
    op.drop_table('wb_blacklist')
