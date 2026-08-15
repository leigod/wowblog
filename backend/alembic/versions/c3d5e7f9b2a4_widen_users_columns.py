"""widen wb_users columns to match model

Revision ID: c3d5e7f9b2a4
Revises: b2f4e6a8c1d3
Create Date: 2026-08-13 16:00:00.000000

放宽 wb_users 几列以匹配 model（审计发现 model 比 DB 宽，用户输入会 Data truncated）：
  profile_bio  varchar(300) → text        （自我介绍可超 300 字）
  school       varchar(50)  → varchar(100)
  login_ip     varchar(15)  → varchar(45) （支持 IPv6，最长 39 字符）
  join_ip      varchar(15)  → varchar(45)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c3d5e7f9b2a4'
down_revision: Union[str, Sequence[str], None] = 'b2f4e6a8c1d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('wb_users', 'profile_bio', existing_type=sa.String(length=300), type_=sa.Text(), existing_nullable=True)
    op.alter_column('wb_users', 'school', existing_type=sa.String(length=50), type_=sa.String(length=100), existing_nullable=True)
    op.alter_column('wb_users', 'login_ip', existing_type=sa.String(length=15), type_=sa.String(length=45), existing_nullable=True)
    op.alter_column('wb_users', 'join_ip', existing_type=sa.String(length=15), type_=sa.String(length=45), existing_nullable=True)


def downgrade() -> None:
    op.alter_column('wb_users', 'join_ip', existing_type=sa.String(length=45), type_=sa.String(length=15), existing_nullable=True)
    op.alter_column('wb_users', 'login_ip', existing_type=sa.String(length=45), type_=sa.String(length=15), existing_nullable=True)
    op.alter_column('wb_users', 'school', existing_type=sa.String(length=100), type_=sa.String(length=50), existing_nullable=True)
    op.alter_column('wb_users', 'profile_bio', existing_type=sa.Text(), type_=sa.String(length=300), existing_nullable=True)
