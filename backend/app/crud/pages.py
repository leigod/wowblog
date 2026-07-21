import app.models.data.pages as models
import app.models.schemas.pages as schemas
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List


# 查询所有页面
async def get_pages(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(models.BlogPage).offset(skip).limit(limit)
    )
    return [schemas.BlogPage.model_validate(page) for page in result.scalars().all()]


# 根据ID获取页面
async def get_page(db: AsyncSession, page_id: int):
    result = await db.execute(
        select(models.BlogPage).where(models.BlogPage.id == page_id)
    )
    page = result.scalar_one_or_none()
    if page:
        return page
    return None


# 添加页面
async def create_page(db: AsyncSession, page: schemas.BlogPageCreate):
    new_page = models.BlogPage(**page.dict())
    db.add(new_page)
    await db.commit()
    await db.refresh(new_page)
    return new_page


# 修改页面
async def update_page(db: AsyncSession, page_id: int, page: schemas.BlogPageUpdate):
    result = await db.execute(
        select(models.BlogPage).where(models.BlogPage.id == page_id)
    )
    page_to_update = result.scalar_one_or_none()
    if page_to_update:
        update_data = page.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(page_to_update, key, value)
        await db.commit()
        await db.refresh(page_to_update)
        return page_to_update
    return None


# 修改页面显示状态
async def update_page_status(db: AsyncSession, page_id: int, page: schemas.BlogPageUpdateStatus):
    result = await db.execute(
        select(models.BlogPage).where(models.BlogPage.id == page_id)
    )
    page_to_update = result.scalar_one_or_none()
    if page_to_update:
        update_data = page.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(page_to_update, key, value)
        await db.commit()
        await db.refresh(page_to_update)
        return page_to_update
    return None


# 删除页面
async def delete_page(db: AsyncSession, page_id: int):
    result = await db.execute(
        select(models.BlogPage).where(models.BlogPage.id == page_id)
    )
    page_to_delete = result.scalar_one_or_none()
    if page_to_delete:
        await db.delete(page_to_delete)
        await db.commit()
        return page_to_delete
    return None


# 根据slug获取页面
async def get_page_by_slug(db: AsyncSession, slug: str):
    result = await db.execute(
        select(models.BlogPage).where(models.BlogPage.slug == slug)
    )
    page = result.scalar_one_or_none()
    if page:
        return page
    return None