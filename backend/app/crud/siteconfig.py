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
        # 只更新传入的非 None 字段
        update_data = site_config.model_dump(exclude_none=True)

        # 处理 footer_config：如果是字典，序列化为 JSON 字符串
        if 'footer_config' in update_data and update_data['footer_config'] is not None:
            if isinstance(update_data['footer_config'], (dict, list)):
                update_data['_footer_config'] = json.dumps(update_data['footer_config'], ensure_ascii=False)
                del update_data['footer_config']
            elif isinstance(update_data['footer_config'], str):
                # 如果已经是字符串，直接赋值给 _footer_config
                update_data['_footer_config'] = update_data['footer_config']
                del update_data['footer_config']

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

