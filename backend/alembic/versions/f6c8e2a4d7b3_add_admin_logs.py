"""add wb_admin_logs

Revision ID: f6c8e2a4d7b3
Revises: e5b7d9f3c2a6
Create Date: 2026-08-13 22:00:00.000000

管理员操作日志表：审计中间件自动记录后台写操作 + 登录/登出。
只记"改"不记"看"；detail 中敏感字段（password/secret/token 等）脱敏为 ***。
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f6c8e2a4d7b3'
down_revision: Union[str, Sequence[str], None] = 'e5b7d9f3c2a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'wb_admin_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True, comment='操作人用户ID'),
        sa.Column('username', sa.String(length=50), nullable=True, comment='操作人用户名（冗余）'),
        sa.Column('role', sa.String(length=20), nullable=True, comment='操作人角色'),
        sa.Column('action', sa.String(length=100), nullable=True, comment='动作: login/logout 或 METHOD:path'),
        sa.Column('method', sa.String(length=10), nullable=True, comment='HTTP 方法'),
        sa.Column('path', sa.String(length=200), nullable=True, comment='请求路径'),
        sa.Column('detail', sa.Text(), nullable=True, comment='请求体 JSON（已脱敏）'),
        sa.Column('status_code', sa.Integer(), nullable=True, comment='响应状态码'),
        sa.Column('ip', sa.String(length=45), nullable=True, comment='客户端IP'),
        sa.Column('user_agent', sa.String(length=500), nullable=True, comment='User-Agent'),
        sa.Column('createtime', sa.Integer(), nullable=True, comment='创建时间戳'),
        sa.PrimaryKeyConstraint('id'),
        mysql_charset='utf8mb4',
        mysql_engine='InnoDB',
    )
    op.create_index('idx_al_user_id', 'wb_admin_logs', ['user_id'], unique=False)
    op.create_index('idx_al_action', 'wb_admin_logs', ['action'], unique=False)
    op.create_index('idx_al_createtime', 'wb_admin_logs', ['createtime'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_al_createtime', table_name='wb_admin_logs')
    op.drop_index('idx_al_action', table_name='wb_admin_logs')
    op.drop_index('idx_al_user_id', table_name='wb_admin_logs')
    op.drop_table('wb_admin_logs')
