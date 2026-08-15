"""add wb_config oauth columns

Revision ID: b2f4e6a8c1d3
Revises: a1e7f3c2d4b8
Create Date: 2026-08-13 14:00:00.000000

wb_config 加两列：
  - oauth_enabled            是否启用社交登录（0/1）
  - enabled_oauth_providers  启用的 provider 列表（JSON 数组）
用于后台运营者决定开放哪些社媒登录/绑定。凭据仍存 .env。
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b2f4e6a8c1d3'
down_revision: Union[str, Sequence[str], None] = 'a1e7f3c2d4b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('wb_config', sa.Column('oauth_enabled', sa.Integer(), nullable=True, comment='是否启用社交登录，0=禁用，1=启用'))
    op.add_column('wb_config', sa.Column('enabled_oauth_providers', sa.JSON(), nullable=True, comment='启用的 OAuth provider 列表'))


def downgrade() -> None:
    op.drop_column('wb_config', 'enabled_oauth_providers')
    op.drop_column('wb_config', 'oauth_enabled')
