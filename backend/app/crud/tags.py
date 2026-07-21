import app.models.data.tags as models
import app.models.schemas.tags as schemas
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List


# 获取标签总数
async def get_tags_count(db: AsyncSession, keyword: str = ''):
    query = select(func.count()).select_from(models.BlogTag)
    if keyword and keyword != '':
        query = query.where(models.BlogTag.name.like(f'%{keyword}%'))
    result = await db.execute(query)
    return result.scalar_one()

# 查询所有标签
async def get_tags(db: AsyncSession, skip: int = 0, limit: int = 100, keyword: str = ''):
    query = select(models.BlogTag).offset(skip).limit(limit)
    if keyword and keyword != '':
        query = query.where(models.BlogTag.name.like(f'%{keyword}%'))
    result = await db.execute(query)
    return [schemas.BlogTag.model_validate(item) for item in result.scalars().all()]


# 根据ID获取标签
async def get_tag(db: AsyncSession, tag_id: int):
    result = await db.execute(
        select(models.BlogTag).where(models.BlogTag.id == tag_id)
    )
    tag = result.scalar_one_or_none()
    if tag:
        return tag
    return None


# 根据名称获取标签
async def get_tag_by_name(db: AsyncSession, tag_name: str):
    result = await db.execute(
        select(models.BlogTag).where(models.BlogTag.name == tag_name)
    )
    tag = result.scalar_one_or_none()
    if tag:
        return tag
    return None


# 根据slug获取标签
async def get_tag_by_slug(db: AsyncSession, tag_slug: str):
    result = await db.execute(
        select(models.BlogTag).where(models.BlogTag.slug == tag_slug).where(models.BlogTag.status == 'normal')
    )
    tag = result.scalar_one_or_none()
    if tag:
        return tag
    return None

# 添加标签
async def create_tag(db: AsyncSession, tag: schemas.BlogTagCreate):
    new_tag = models.BlogTag(**tag.model_dump(exclude_unset=True))
    db.add(new_tag)
    await db.commit()
    await db.refresh(new_tag)
    return new_tag


# 修改标签
async def update_tag(db: AsyncSession, tag_id: int, tag: schemas.BlogTagUpdate):
    result = await db.execute(
        select(models.BlogTag).where(models.BlogTag.id == tag_id)
    )
    tag_to_update = result.scalar_one_or_none()
    if tag_to_update:
        update_data = tag.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(tag_to_update, key, value)
        await db.commit()
        await db.refresh(tag_to_update)
        return tag_to_update
    return None


# 修改页面显示状态
async def update_tag_status(db: AsyncSession, tag_id: int, tag: schemas.BlogTagUpdateStatus):
    result = await db.execute(
        select(models.BlogTag).where(models.BlogTag.id == tag_id)
    )
    tag_to_update = result.scalar_one_or_none()
    if tag_to_update:
        update_data = tag.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(tag_to_update, key, value)
        await db.commit()
        await db.refresh(tag_to_update)
        return tag_to_update
    return None


# 删除页面
async def delete_tag(db: AsyncSession, tag_id: int):
    result = await db.execute(
        select(models.BlogTag).where(models.BlogTag.id == tag_id)
    )
    tag_to_delete = result.scalar_one_or_none()
    if tag_to_delete:
        await db.delete(tag_to_delete)
        await db.commit()
        return tag_to_delete
    return None


# 查询标签
async def search_tag(db: AsyncSession, search: str):
    result = await db.execute(
        select(models.BlogTag).where(models.BlogTag.name.like(f'%{search}%'))
    )
    tags = result.scalars().all()
    return [schemas.BlogTag.model_validate(item) for item in tags]


# 前端用户搜索标签（只返回正常状态的标签）
async def search_tag_frontend(db: AsyncSession, search: str, limit: int = 20):
    """前端用户搜索标签，只返回status='normal'的标签"""
    result = await db.execute(
        select(models.BlogTag)
        .where(
            models.BlogTag.name.like(f'%{search}%'),
            models.BlogTag.status == 'normal'
        )
        .limit(limit)
    )
    tags = result.scalars().all()
    return [schemas.BlogTag.model_validate(item) for item in tags]


# 获取热门标签
async def get_hot_tags(db: AsyncSession, limit: int = 10):
    result = await db.execute(
        select(models.BlogTag)
        .order_by(models.BlogTag.counts.desc())
        .limit(limit)
    )
    tags = result.scalars().all()
    return [schemas.BlogTag.model_validate(item) for item in tags]


# 更新标签浏览量
async def update_tag_views(db: AsyncSession, tag_id: int):
    await db.execute(
        update(models.BlogTag).where(models.BlogTag.id == tag_id).values(views=models.BlogTag.views + 1)
    )
    await db.commit()
