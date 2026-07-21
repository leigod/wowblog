"""
DocBook 业务逻辑层
"""
import app.crud.docbook as crud
import app.crud.doc as doc_crud
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import app.models.schemas.docs as schemas


class DocBookService:
    """文档书服务"""

    @staticmethod
    async def get_docbook_list(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        keyword: str = ''
    ) -> tuple[List[schemas.DocBookResponse], int]:
        """获取文档书列表（带分页）"""
        total = await crud.get_docbooks_count(db, keyword)
        docbooks = await crud.get_docbooks(db, skip, limit, keyword)

        # 为每个文档书填充文档数量和作者名称
        result = []
        for docbook in docbooks:
            doc_count = await crud.get_doc_count(db, docbook.id)
            # 先从 ORM 对象创建 schema，然后更新额外字段
            docbook_response = schemas.DocBookResponse.model_validate(docbook)
            docbook_response.doc_count = doc_count
            docbook_response.author_name = None
            result.append(docbook_response)

        return result, total

    @staticmethod
    async def get_docbook_detail(
        docbook_id: int,
        db: AsyncSession
    ) -> Optional[schemas.DocBookResponse]:
        """获取文档书详情"""
        docbook = await crud.get_docbook_by_id(db, docbook_id)
        if not docbook:
            return None

        doc_count = await crud.get_doc_count(db, docbook.id)
        docbook_response = schemas.DocBookResponse.model_validate(docbook)
        docbook_response.doc_count = doc_count
        docbook_response.author_name = None
        return docbook_response

    @staticmethod
    async def get_docbook_by_slug(
        slug: str,
        db: AsyncSession
    ) -> Optional[schemas.DocBookResponse]:
        """通过slug获取文档书"""
        docbook = await crud.get_docbook_by_slug(db, slug)
        if not docbook:
            return None

        doc_count = await crud.get_doc_count(db, docbook.id)
        docbook_response = schemas.DocBookResponse.model_validate(docbook)
        docbook_response.doc_count = doc_count
        docbook_response.author_name = None
        return docbook_response

    @staticmethod
    async def create_docbook(
        docbook: schemas.DocBookCreate,
        author_id: int,
        db: AsyncSession
    ) -> schemas.DocBookResponse:
        """创建文档书"""
        new_docbook = await crud.create_docbook(db, docbook, author_id)
        docbook_response = schemas.DocBookResponse.model_validate(new_docbook)
        docbook_response.doc_count = 0
        docbook_response.author_name = None
        return docbook_response

    @staticmethod
    async def update_docbook(
        docbook_id: int,
        docbook: schemas.DocBookUpdate,
        db: AsyncSession
    ) -> Optional[schemas.DocBookResponse]:
        """更新文档书"""
        updated = await crud.update_docbook(db, docbook_id, docbook)
        if not updated:
            return None

        doc_count = await crud.get_doc_count(db, updated.id)
        docbook_response = schemas.DocBookResponse.model_validate(updated)
        docbook_response.doc_count = doc_count
        docbook_response.author_name = None
        return docbook_response

    @staticmethod
    async def delete_docbook(
        docbook_id: int,
        db: AsyncSession
    ) -> bool:
        """删除文档书"""
        deleted = await crud.delete_docbook(db, docbook_id)
        return deleted is not None

    @staticmethod
    async def validate_slug_unique(
        slug: str,
        exclude_id: Optional[int] = None,
        db: Optional[AsyncSession] = None
    ) -> bool:
        """验证slug是否唯一"""
        existing = await crud.get_docbook_by_slug(db, slug)
        if existing is None:
            return True
        return existing.id == exclude_id

    @staticmethod
    async def can_access_docbook(
        docbook_id: int,
        db: AsyncSession,
        user_id: Optional[int] = None
    ) -> bool:
        """检查用户是否有权限访问文档书"""
        docbook = await crud.get_docbook_by_id(db, docbook_id)
        if not docbook:
            return False

        # 公开文档书所有人可访问
        if docbook.is_public:
            return True

        # 非公开文档书需要作者权限
        return user_id is not None and user_id == docbook.author_id
