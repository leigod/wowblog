"""
DocBook CRUD 操作
"""
import app.models.data.docs as models
import app.models.schemas.docs as schemas
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import time


async def get_docbooks_count(db: AsyncSession, keyword: str = '') -> int:
    """获取文档书总数"""
    query = select(func.count()).select_from(models.DocBook)
    if keyword:
        query = query.where(models.DocBook.name.like(f'%{keyword}%'))
    result = await db.execute(query)
    return result.scalar_one()


async def get_docbooks(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    keyword: str = ''
) -> List[models.DocBook]:
    """获取文档书列表"""
    query = select(models.DocBook).offset(skip).limit(limit).order_by(models.DocBook.sort_order)
    if keyword:
        query = query.where(models.DocBook.name.like(f'%{keyword}%'))
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_docbook_by_id(db: AsyncSession, docbook_id: int) -> Optional[models.DocBook]:
    """通过ID获取文档书"""
    result = await db.execute(
        select(models.DocBook).where(models.DocBook.id == docbook_id)
    )
    return result.scalar_one_or_none()


async def get_docbook_by_slug(db: AsyncSession, slug: str) -> Optional[models.DocBook]:
    """通过slug获取文档书"""
    result = await db.execute(
        select(models.DocBook).where(models.DocBook.slug == slug)
    )
    return result.scalar_one_or_none()


async def create_docbook(
    db: AsyncSession,
    docbook: schemas.DocBookCreate,
    author_id: int
) -> models.DocBook:
    """创建文档书"""
    new_docbook = models.DocBook(
        **docbook.model_dump(),
        author_id=author_id,
        createtime=int(time.time()),
        updatetime=int(time.time())
    )
    db.add(new_docbook)
    await db.commit()
    await db.refresh(new_docbook)
    return new_docbook


async def update_docbook(
    db: AsyncSession,
    docbook_id: int,
    docbook: schemas.DocBookUpdate
) -> Optional[models.DocBook]:
    """更新文档书"""
    result = await db.execute(
        select(models.DocBook).where(models.DocBook.id == docbook_id)
    )
    docbook_to_update = result.scalar_one_or_none()
    if docbook_to_update:
        update_data = docbook.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(docbook_to_update, key, value)
        docbook_to_update.updatetime = int(time.time())
        await db.commit()
        await db.refresh(docbook_to_update)
    return docbook_to_update


async def delete_docbook(db: AsyncSession, docbook_id: int) -> Optional[models.DocBook]:
    """删除文档书"""
    result = await db.execute(
        select(models.DocBook).where(models.DocBook.id == docbook_id)
    )
    docbook_to_delete = result.scalar_one_or_none()
    if docbook_to_delete:
        await db.delete(docbook_to_delete)
        await db.commit()
    return docbook_to_delete


async def get_doc_count(db: AsyncSession, docbook_id: int) -> int:
    """获取文档书中的文档数量"""
    result = await db.execute(
        select(func.count()).select_from(models.Doc).where(models.Doc.docbook_id == docbook_id)
    )
    return result.scalar_one()
