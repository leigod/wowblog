from sqlalchemy.orm import Session
import app.models.data.siteconfig as models
import app.models.schemas.siteconfig as schemas
from sqlalchemy import and_, func, insert, select, or_, update
from sqlalchemy.ext.asyncio import AsyncSession
import hashlib
import os
import time
import json
from fastapi import HTTPException, Request
from app.utils.auth import get_password_hash
from typing import TypedDict


# 获取站点配置
async def get_site_config(db: AsyncSession):
    result = await db.execute(
        select(models.SiteConfig)
    )
    site_config = result.scalar_one_or_none()
    if site_config:
        return site_config
    return None

# 更新站点配置
async def update_site_config(db: AsyncSession, site_config: schemas.SiteConfig):
    # 获取当前配置
    current_result = await db.execute(
        select(models.SiteConfig).where(models.SiteConfig.id == 1)
    )
    current_config = current_result.scalar_one_or_none()

    if current_config:
        # 局部更新：只写请求里实际带来的字段。后台各页签保存时只发送自己的字段，
        # 不能展开整份 Schema——没发送的字段会被 Schema 默认值覆盖，保存一个页签
        # 就会把其它页签的设置重置（如关掉文章审核后保存基础设置，审核又变回开启）。
        # 显式传 null 表示清空；但 NOT NULL 列（如 disable_comment）仍按「不修改」处理。
        nullable_columns = {c.name for c in models.SiteConfig.__table__.columns if c.nullable}
        update_data = {
            key: value
            for key, value in site_config.model_dump(exclude_unset=True).items()
            if value is not None or key.lstrip('_') in nullable_columns
        }

        # footer_config 在模型里是 _footer_config 列（Text，存 JSON 字符串）
        if 'footer_config' in update_data:
            footer_config = update_data.pop('footer_config')
            if isinstance(footer_config, (dict, list)):
                update_data['_footer_config'] = json.dumps(footer_config, ensure_ascii=False)
            elif isinstance(footer_config, str):
                # 如果已经是字符串，直接赋值给 _footer_config
                update_data['_footer_config'] = footer_config
            else:
                # null：清空页脚配置
                update_data['_footer_config'] = None

        if update_data:
            await db.execute(
                update(models.SiteConfig)
                .values(**update_data)
                .where(models.SiteConfig.id == 1)
            )
            await db.commit()
            # 刷新以获取最新数据
            await db.refresh(current_config)
            return current_config
    return None

