"""
Doc API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.models.schemas.docs import (
    DocResponse, DocCreate, DocUpdate, DocTreeNode, DocNavigation
)
from app.models.response import ApiResponse
from app.services.doc_service import DocService
from app.services.docbook_service import DocBookService
from app.dependencies.authentication import get_current_user, get_current_user_id
from app.utils.response import success
from app.crud import comments as crudComments
from app.crud import siteconfig as crudSiteConfig
from app.models.schemas import comments as schemasComments

router = APIRouter(prefix="/docs", tags=["文档"])


@router.get("", response_model=ApiResponse[List[DocResponse]])
async def list_docs(
    docbook_id: int = Query(..., description="文档书ID"),
    skip: int = Query(0, ge=0, description="跳过条数"),
    limit: int = Query(100, ge=1, le=100, description="每页条数"),
    keyword: str = Query("", description="搜索关键词"),
    status: str = Query(None, description="状态筛选"),
    db: AsyncSession = Depends(get_db)
):
    """获取文档列表"""
    # 检查文档书是否存在
    docbook = await DocBookService.get_docbook_detail(docbook_id, db)
    if not docbook:
        raise HTTPException(status_code=404, detail="文档书不存在")

    docs, total = await DocService.get_doc_list(docbook_id, db, skip, limit, keyword, status)
    return success('ok', docs)


@router.get("/count", response_model=ApiResponse[dict])
async def get_docs_count(
    docbook_id: int = Query(..., description="文档书ID"),
    keyword: str = Query("", description="搜索关键词"),
    status: str = Query(None, description="状态筛选"),
    db: AsyncSession = Depends(get_db)
):
    """获取文档总数"""
    _, total = await DocService.get_doc_list(docbook_id, db, 0, 1, keyword, status)
    return success('ok', {"total": total})


@router.get("/tree", response_model=ApiResponse[List[DocTreeNode]])
async def get_doc_tree(
    docbook_id: int = Query(..., description="文档书ID"),
    include_draft: bool = Query(False, description="是否包含草稿状态文档"),
    db: AsyncSession = Depends(get_db)
):
    """获取文档树（用于侧边栏导航或后台管理）"""
    # 检查文档书是否存在
    docbook = await DocBookService.get_docbook_detail(docbook_id, db)
    if not docbook:
        raise HTTPException(status_code=404, detail="文档书不存在")

    tree = await DocService.get_doc_tree(docbook_id, db, include_draft)
    return success('ok', tree)


@router.get("/search", response_model=ApiResponse[List[DocResponse]])
async def search_docs(
    docbook_id: int = Query(..., description="文档书ID"),
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    limit: int = Query(20, ge=1, le=100, description="返回条数"),
    db: AsyncSession = Depends(get_db)
):
    """搜索文档"""
    # 检查文档书是否存在
    docbook = await DocBookService.get_docbook_detail(docbook_id, db)
    if not docbook:
        raise HTTPException(status_code=404, detail="文档书不存在")

    results = await DocService.search_docs(docbook_id, keyword, db, limit)
    return success('ok', results)


@router.get("/slug/{slug}", response_model=ApiResponse[DocResponse])
async def get_doc_by_slug(
    slug: str,
    docbook_id: int = Query(..., description="文档书ID"),
    db: AsyncSession = Depends(get_db)
):
    """通过slug获取文档"""
    doc = await DocService.get_doc_by_slug(docbook_id, slug, db)
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    return success('ok', doc)


@router.get("/{doc_id}", response_model=ApiResponse[DocResponse])
async def get_doc(
    doc_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取文档详情"""
    doc = await DocService.get_doc_detail(doc_id, db)
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    return success('ok', doc)


@router.get("/{doc_id}/navigation", response_model=ApiResponse[DocNavigation])
async def get_doc_navigation(
    doc_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取文档导航（上一篇/下一篇/面包屑）"""
    nav = await DocService.get_doc_navigation(doc_id, db)
    if not nav:
        raise HTTPException(status_code=404, detail="文档不存在")
    return success('ok', nav)


@router.get("/{doc_id}/children", response_model=ApiResponse[List[DocResponse]])
async def get_doc_children(
    doc_id: int,
    status: str = Query(None, description="状态筛选"),
    db: AsyncSession = Depends(get_db)
):
    """获取子文档列表"""
    children = await DocService.get_doc_children(doc_id, db, status)
    return success('ok', children)


@router.post("", response_model=ApiResponse[DocResponse], status_code=201)
async def create_doc(
    doc: DocCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建文档"""
    # 检查文档书是否存在
    docbook = await DocBookService.get_docbook_detail(doc.docbook_id, db)
    if not docbook:
        raise HTTPException(status_code=404, detail="文档书不存在")

    # 检查权限
    if docbook.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限在此文档书创建文档")

    # 验证slug唯一性
    if not await DocService.validate_slug_unique(doc.docbook_id, doc.slug, None, db):
        raise HTTPException(status_code=400, detail="URL标识在此文档书中已存在")

    new_doc = await DocService.create_doc(doc.docbook_id, doc, current_user.id, db)
    return success('创建成功', new_doc)


@router.put("/{doc_id}", response_model=ApiResponse[DocResponse])
async def update_doc(
    doc_id: int,
    doc: DocUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新文档"""
    # 检查文档是否存在
    existing = await DocService.get_doc_detail(doc_id, db, increase_view=False)
    if not existing:
        raise HTTPException(status_code=404, detail="文档不存在")

    # 检查文档书权限
    docbook = await DocBookService.get_docbook_detail(existing.docbook_id, db)
    if not docbook or docbook.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限编辑此文档")

    # 如果修改了slug，验证唯一性
    if doc.slug and doc.slug != existing.slug:
        if not await DocService.validate_slug_unique(existing.docbook_id, doc.slug, doc_id, db):
            raise HTTPException(status_code=400, detail="URL标识在此文档书中已存在")

    updated = await DocService.update_doc(doc_id, doc, db)
    return success('更新成功', updated)


@router.delete("/{doc_id}", response_model=ApiResponse[dict])
async def delete_doc(
    doc_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除文档"""
    # 检查文档是否存在
    existing = await DocService.get_doc_detail(doc_id, db, increase_view=False)
    if not existing:
        raise HTTPException(status_code=404, detail="文档不存在")

    # 检查文档书权限
    docbook = await DocBookService.get_docbook_detail(existing.docbook_id, db)
    if not docbook or docbook.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限删除此文档")

    await DocService.delete_doc(doc_id, db)
    return success('删除成功', {"message": "删除成功"})


@router.post("/{doc_id}/move", response_model=ApiResponse[DocResponse])
async def move_doc(
    doc_id: int,
    new_parent_id: int = Query(..., description="新父文档ID，0表示顶级"),
    new_sort_order: int = Query(..., description="新排序位置"),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """移动文档（拖拽排序）"""
    # 检查文档是否存在
    existing = await DocService.get_doc_detail(doc_id, db, increase_view=False)
    if not existing:
        raise HTTPException(status_code=404, detail="文档不存在")

    # 检查文档书权限
    docbook = await DocBookService.get_docbook_detail(existing.docbook_id, db)
    if not docbook or docbook.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限移动此文档")

    # 不能将文档移动到自己或自己的子文档下
    if new_parent_id == doc_id:
        raise HTTPException(status_code=400, detail="不能将文档移动到自己下")

    if new_parent_id != 0:
        # 检查新父文档是否在当前文档的子树中
        parent_doc = await DocService.get_doc_detail(new_parent_id, db, increase_view=False)
        if parent_doc and existing.path in parent_doc.path:
            raise HTTPException(status_code=400, detail="不能将文档移动到自己的子文档下")

    moved = await DocService.move_doc(doc_id, new_parent_id, new_sort_order, db)
    return success('移动成功', moved)


# 获取文档评论列表
@router.get("/{doc_id}/comments", response_model=ApiResponse[List[schemasComments.BlogCommentListItem]])
async def get_doc_comment_list(
    doc_id: int,
    type: str = 'reply',
    subject_id: int = 0,
    order: str = 'top',
    currentpage: int = 1,
    pagesize: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """获取文档评论列表"""
    comment_list = await crudComments.get_comment_list(
        db,
        doc_id=doc_id,
        type=type,
        subject_id=subject_id,
        order=order,
        page=currentpage,
        page_size=pagesize,
    )
    return success(data=comment_list)


# 创建文档评论/回复
@router.post("/{doc_id}/comments", response_model=ApiResponse[schemasComments.BlogComment])
async def create_doc_comment(
    doc_id: int,
    request: Request,
    comment: schemasComments.BlogCommentCreateForm,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """创建文档评论/回复"""
    # 检查全局文档评论设置
    site_config = await crudSiteConfig.get_site_config(db)
    if not site_config or site_config.doc_comment != 1:
        raise HTTPException(status_code=403, detail="文档评论功能已关闭")

    # 设置doc_id
    comment.doc_id = doc_id
    comment.article_id = None

    comment_entity = await crudComments.add_comment(
        db,
        request=request,
        comment=comment,
        user_id=user_id,
    )
    return success(data=comment_entity)
