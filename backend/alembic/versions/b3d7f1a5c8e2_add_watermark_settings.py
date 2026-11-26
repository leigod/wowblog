"""add watermark settings

Revision ID: b3d7f1a5c8e2
Revises: 9e2b7c4a1f6d
Create Date: 2026-11-26 20:00:00.000000

图片水印配置：
- wb_config 加全站默认开关 watermark_enabled / watermark_mode；
- wb_user_blogs 加博客级覆盖（NULL=跟随全站，0/1=显式覆盖）。
上传接口在落盘前按「上传者角色 → 素材三级回退」合成水印。
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b3d7f1a5c8e2'
down_revision: Union[str, Sequence[str], None] = '9e2b7c4a1f6d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'wb_config',
        sa.Column('watermark_enabled', sa.Integer(), nullable=False, server_default='0',
                  comment='图片水印开关：1=开启，0=关闭')
    )
    op.add_column(
        'wb_config',
        sa.Column('watermark_mode', sa.String(length=10), nullable=False, server_default='corner',
                  comment='水印样式：corner=右下角单戳，tile=平铺防裁剪')
    )
    op.add_column(
        'wb_user_blogs',
        sa.Column('watermark_enabled', sa.Integer(), nullable=True,
                  comment='blog图片水印开关：NULL=跟随全站，0=关闭，1=开启')
    )
    op.add_column(
        'wb_user_blogs',
        sa.Column('watermark_mode', sa.String(length=10), nullable=True,
                  comment='水印样式：NULL=跟随全站，corner=右下角，tile=平铺')
    )


def downgrade() -> None:
    op.drop_column('wb_user_blogs', 'watermark_mode')
    op.drop_column('wb_user_blogs', 'watermark_enabled')
    op.drop_column('wb_config', 'watermark_mode')
    op.drop_column('wb_config', 'watermark_enabled')
