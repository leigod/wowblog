"""
DocBook API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.models.schemas.docs import (
    DocBookResponse, DocBookCreate, DocBookUpdate
)
from app.models.response import ApiResponse
from app.services.docbook_service import DocBookService
from app.dependencies.authentication import get_current_user, get_current_user_optional
from app.utils.response import success

router = APIRouter(prefix="/docbooks", tags=["文档书"])


@router.get("", response_model=ApiResponse[List[DocBookResponse]])
async def list_docbooks(
    skip: int = Query(0, ge=0, description="跳过条数"),
    limit: int = Query(100, ge=1, le=100, description="每页条数"),
    keyword: str = Query("", description="搜索关键词"),
    db: AsyncSession = Depends(get_db)
):
    """获取文档书列表"""
    docbooks, total = await DocBookService.get_docbook_list(db, skip, limit, keyword)
    return success('ok', docbooks)


@router.get("/count", response_model=ApiResponse[dict])
async def get_docbooks_count(
    keyword: str = Query("", description="搜索关键词"),
    db: AsyncSession = Depends(get_db)
):
    """获取文档书总数"""
    _, total = await DocBookService.get_docbook_list(db, 0, 1, keyword)
    return success('ok', {"total": total})


@router.get("/{docbook_id}", response_model=ApiResponse[DocBookResponse])
async def get_docbook(
    docbook_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取文档书详情"""
    docbook = await DocBookService.get_docbook_detail(docbook_id, db)
    if not docbook:
        raise HTTPException(status_code=404, detail="文档书不存在")
    return success('ok', docbook)


@router.get("/slug/{slug}", response_model=ApiResponse[DocBookResponse])
async def get_docbook_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """通过slug获取文档书"""
    docbook = await DocBookService.get_docbook_by_slug(slug, db)
    if not docbook:
        raise HTTPException(status_code=404, detail="文档书不存在")
    return success('ok', docbook)


@router.post("", response_model=ApiResponse[DocBookResponse], status_code=201)
async def create_docbook(
    docbook: DocBookCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建文档书"""
    # 验证slug唯一性
    if not await DocBookService.validate_slug_unique(docbook.slug, None, db):
        raise HTTPException(status_code=400, detail="URL标识已存在")

    new_docbook = await DocBookService.create_docbook(
        docbook, current_user.id, db
    )
    return success('创建成功', new_docbook)


@router.put("/{docbook_id}", response_model=ApiResponse[DocBookResponse])
async def update_docbook(
    docbook_id: int,
    docbook: DocBookUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新文档书"""
    # 检查文档书是否存在
    existing = await DocBookService.get_docbook_detail(docbook_id, db)
    if not existing:
        raise HTTPException(status_code=404, detail="文档书不存在")

    # 检查权限
    if existing.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限编辑此文档书")

    # 如果修改了slug，验证唯一性
    if docbook.slug and docbook.slug != existing.slug:
        if not await DocBookService.validate_slug_unique(docbook.slug, docbook_id, db):
            raise HTTPException(status_code=400, detail="URL标识已存在")

    updated = await DocBookService.update_docbook(docbook_id, docbook, db)
    return success('更新成功', updated)


@router.delete("/{docbook_id}", response_model=ApiResponse[dict])
async def delete_docbook(
    docbook_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除文档书"""
    # 检查文档书是否存在
    existing = await DocBookService.get_docbook_detail(docbook_id, db)
    if not existing:
        raise HTTPException(status_code=404, detail="文档书不存在")

    # 检查权限
    if existing.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限删除此文档书")

    await DocBookService.delete_docbook(docbook_id, db)
    return success('删除成功', {"message": "删除成功"})
