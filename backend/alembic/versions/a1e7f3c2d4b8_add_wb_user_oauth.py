"""add wb_user_oauth

Revision ID: a1e7f3c2d4b8
Revises: cd6757a448f8
Create Date: 2026-08-12 12:00:00.000000

新建用户第三方登录绑定表 wb_user_oauth，供 OAuth 社交登录使用。
字段严格对照 app/models/data/user_oauth.py:UserOAuth（避免与 autogenerate 产生 drift）。
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1e7f3c2d4b8'
down_revision: Union[str, Sequence[str], None] = 'cd6757a448f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: 创建 wb_user_oauth 表。"""
    op.create_table(
        'wb_user_oauth',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('provider_user_id', sa.String(length=255), nullable=False),
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('raw_data', sa.JSON(), nullable=True),
        sa.Column('createtime', sa.Integer(), nullable=True),
        sa.Column('updatetime', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['wb_users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        mysql_charset='utf8mb4',
        mysql_engine='InnoDB',
    )
    op.create_index('ix_wb_user_oauth_id', 'wb_user_oauth', ['id'], unique=False)
    op.create_index('ix_wb_user_oauth_user_id', 'wb_user_oauth', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema: 删除 wb_user_oauth 表。"""
    op.drop_index('ix_wb_user_oauth_user_id', table_name='wb_user_oauth')
    op.drop_index('ix_wb_user_oauth_id', table_name='wb_user_oauth')
    op.drop_table('wb_user_oauth')
