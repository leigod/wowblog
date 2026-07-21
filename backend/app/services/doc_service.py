"""
Doc 业务逻辑层
"""
import app.crud.doc as crud
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import app.models.schemas.docs as schemas


class DocService:
    """文档服务"""

    @staticmethod
    async def get_doc_list(
        docbook_id: int,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        keyword: str = '',
        status: Optional[str] = None
    ) -> tuple[List[schemas.DocResponse], int]:
        """获取文档列表（带分页）"""
        total = await crud.get_docs_count(db, docbook_id, keyword, status)
        docs = await crud.get_docs(db, docbook_id, skip, limit, keyword, status)

        result = []
        for doc in docs:
            doc_response = schemas.DocResponse.model_validate(doc)
            doc_response.author_name = None
            result.append(doc_response)

        return result, total

    @staticmethod
    async def get_doc_detail(
        doc_id: int,
        db: AsyncSession,
        increase_view: bool = True
    ) -> Optional[schemas.DocResponse]:
        """获取文档详情"""
        doc = await crud.get_doc_by_id(db, doc_id)
        if not doc:
            return None

        # 增加浏览次数
        if increase_view:
            await crud.increase_view_count(db, doc_id)

        doc_response = schemas.DocResponse.model_validate(doc)
        doc_response.author_name = None
        return doc_response

    @staticmethod
    async def get_doc_by_slug(
        docbook_id: int,
        slug: str,
        db: AsyncSession,
        increase_view: bool = True
    ) -> Optional[schemas.DocResponse]:
        """通过slug获取文档"""
        doc = await crud.get_doc_by_slug(db, docbook_id, slug)
        if not doc:
            return None

        # 增加浏览次数
        if increase_view:
            await crud.increase_view_count(db, doc.id)

        doc_response = schemas.DocResponse.model_validate(doc)
        doc_response.author_name = None
        return doc_response

    @staticmethod
    async def get_doc_tree(
        docbook_id: int,
        db: AsyncSession,
        include_draft: bool = False
    ) -> List[schemas.DocTreeNode]:
        """获取文档树

        Args:
            docbook_id: 文档书ID
            db: 数据库会话
            include_draft: 是否包含草稿状态的文档（默认为False）
        """
        return await crud.get_doc_tree(db, docbook_id, include_draft)

    @staticmethod
    async def get_doc_navigation(
        doc_id: int,
        db: AsyncSession
    ) -> Optional[schemas.DocNavigation]:
        """获取文档导航"""
        doc = await crud.get_doc_by_id(db, doc_id)
        if not doc:
            return None

        return await crud.get_navigation(db, doc)

    @staticmethod
    async def create_doc(
        docbook_id: int,
        doc: schemas.DocCreate,
        author_id: int,
        db: AsyncSession
    ) -> schemas.DocResponse:
        """创建文档"""
        # 确保docbook_id正确
        doc.docbook_id = docbook_id
        new_doc = await crud.create_doc(db, doc, author_id)

        doc_response = schemas.DocResponse.model_validate(new_doc)
        doc_response.author_name = None
        return doc_response

    @staticmethod
    async def update_doc(
        doc_id: int,
        doc: schemas.DocUpdate,
        db: AsyncSession
    ) -> Optional[schemas.DocResponse]:
        """更新文档"""
        updated = await crud.update_doc(db, doc_id, doc)
        if not updated:
            return None

        doc_response = schemas.DocResponse.model_validate(updated)
        doc_response.author_name = None
        return doc_response

    @staticmethod
    async def delete_doc(
        doc_id: int,
        db: AsyncSession
    ) -> bool:
        """删除文档"""
        deleted = await crud.delete_doc(db, doc_id)
        return deleted is not None

    @staticmethod
    async def move_doc(
        doc_id: int,
        new_parent_id: int,
        new_sort_order: int,
        db: AsyncSession
    ) -> Optional[schemas.DocResponse]:
        """移动文档（拖拽排序）"""
        moved = await crud.move_doc(db, doc_id, new_parent_id, new_sort_order)
        if not moved:
            return None

        doc_response = schemas.DocResponse.model_validate(moved)
        doc_response.author_name = None
        return doc_response

    @staticmethod
    async def search_docs(
        docbook_id: int,
        keyword: str,
        db: AsyncSession,
        limit: int = 20
    ) -> List[schemas.DocResponse]:
        """搜索文档"""
        docs = await crud.search_docs(db, docbook_id, keyword, limit)

        result = []
        for doc in docs:
            doc_response = schemas.DocResponse.model_validate(doc)
            doc_response.author_name = None
            result.append(doc_response)

        return result

    @staticmethod
    async def validate_slug_unique(
        docbook_id: int,
        slug: str,
        exclude_id: Optional[int] = None,
        db: Optional[AsyncSession] = None
    ) -> bool:
        """验证slug在文档书内是否唯一"""
        existing = await crud.get_doc_by_slug(db, docbook_id, slug)
        if existing is None:
            return True
        return existing.id == exclude_id

    @staticmethod
    async def get_doc_children(
        doc_id: int,
        db: AsyncSession,
        status: Optional[str] = None
    ) -> List[schemas.DocResponse]:
        """获取子文档列表"""
        children = await crud.get_doc_children(db, doc_id, status)

        result = []
        for child in children:
            child_response = schemas.DocResponse.model_validate(child)
            child_response.author_name = None
            result.append(child_response)

        return result
