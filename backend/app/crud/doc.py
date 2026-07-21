"""
Doc CRUD 操作
"""
import app.models.data.docs as models
import app.models.schemas.docs as schemas
from sqlalchemy import select, update, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import time


async def get_docs_count(
    db: AsyncSession,
    docbook_id: int,
    keyword: str = '',
    status: Optional[str] = None
) -> int:
    """获取文档数量"""
    query = select(func.count()).select_from(models.Doc).where(models.Doc.docbook_id == docbook_id)
    if keyword:
        query = query.where(or_(
            models.Doc.title.like(f'%{keyword}%'),
            models.Doc.content.like(f'%{keyword}%')
        ))
    if status:
        query = query.where(models.Doc.status == status)
    result = await db.execute(query)
    return result.scalar_one()


async def get_docs(
    db: AsyncSession,
    docbook_id: int,
    skip: int = 0,
    limit: int = 100,
    keyword: str = '',
    status: Optional[str] = None
) -> List[models.Doc]:
    """获取文档列表"""
    query = select(models.Doc).where(
        models.Doc.docbook_id == docbook_id
    ).offset(skip).limit(limit).order_by(
        models.Doc.parent_id,
        models.Doc.sort_order
    )
    if keyword:
        query = query.where(or_(
            models.Doc.title.like(f'%{keyword}%'),
            models.Doc.content.like(f'%{keyword}%')
        ))
    if status:
        query = query.where(models.Doc.status == status)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_doc_by_id(db: AsyncSession, doc_id: int) -> Optional[models.Doc]:
    """通过ID获取文档"""
    result = await db.execute(
        select(models.Doc).where(models.Doc.id == doc_id)
    )
    return result.scalar_one_or_none()


async def get_doc_by_slug(db: AsyncSession, docbook_id: int, slug: str) -> Optional[models.Doc]:
    """通过slug获取文档"""
    result = await db.execute(
        select(models.Doc).where(
            models.Doc.docbook_id == docbook_id,
            models.Doc.slug == slug
        )
    )
    return result.scalar_one_or_none()


async def get_doc_tree(db: AsyncSession, docbook_id: int, include_draft: bool = False) -> List[schemas.DocTreeNode]:
    """获取文档树（用于侧边栏导航）

    Args:
        db: 数据库会话
        docbook_id: 文档书ID
        include_draft: 是否包含草稿状态的文档（默认为False，后台管理时可设为True）
    """
    # 根据参数决定是否包含草稿
    if include_draft:
        # 包含所有状态的文档
        query = select(models.Doc).where(
            models.Doc.docbook_id == docbook_id
        ).order_by(
            models.Doc.parent_id,
            models.Doc.sort_order
        )
    else:
        # 只显示已发布和隐藏的文档（前端用户页面）
        query = select(models.Doc).where(
            models.Doc.docbook_id == docbook_id,
            models.Doc.status.in_(['published', 'hidden'])
        ).order_by(
            models.Doc.parent_id,
            models.Doc.sort_order
        )

    result = await db.execute(query)
    docs = list(result.scalars().all())

    # 构建树形结构
    def build_tree(parent_id: int = 0) -> List[schemas.DocTreeNode]:
        children = []
        for doc in docs:
            if doc.parent_id == parent_id:
                node = schemas.DocTreeNode(
                    id=doc.id,
                    title=doc.title,
                    slug=doc.slug,
                    level=doc.level,
                    parent_id=doc.parent_id,
                    sort_order=doc.sort_order,
                    status=doc.status,
                    children=build_tree(doc.id)
                )
                children.append(node)
        return children

    return build_tree()


async def get_breadcrumbs(
    db: AsyncSession,
    doc: models.Doc
) -> List[models.Doc]:
    """获取面包屑导航路径"""
    if not doc.path or doc.path == '0':
        return []

    path_ids = [int(id) for id in doc.path.split('/') if id]
    if not path_ids:
        return []

    result = await db.execute(
        select(models.Doc).where(models.Doc.id.in_(path_ids))
    )
    path_docs = {doc.id: doc for doc in result.scalars().all()}

    # 按路径顺序返回
    breadcrumbs = []
    for pid in path_ids:
        if pid in path_docs:
            breadcrumbs.append(path_docs[pid])

    return breadcrumbs


async def get_navigation(
    db: AsyncSession,
    doc: models.Doc
) -> schemas.DocNavigation:
    """获取文档导航（上一篇、下一篇、父级）"""
    # 获取已发布文档（与 get_doc_tree 相同的查询逻辑）
    result = await db.execute(
        select(models.Doc).where(
            models.Doc.docbook_id == doc.docbook_id,
            models.Doc.status == 'published'
        ).order_by(
            models.Doc.parent_id,
            models.Doc.sort_order
        )
    )
    all_docs = list(result.scalars().all())

    # 构建树形结构（与 get_doc_tree 的 build_tree 逻辑相同）
    def build_tree(parent_id: int = 0) -> List[models.Doc]:
        children = []
        for d in all_docs:
            if d.parent_id == parent_id:
                children.append(d)
        return children

    # 深度优先遍历获取扁平列表
    def dfs_flatten(nodes: List[models.Doc]) -> List[models.Doc]:
        result = []
        for node in nodes:
            result.append(node)
            # 递归处理子节点
            children = build_tree(node.id)
            result.extend(dfs_flatten(children))
        return result

    # 获取深度优先遍历顺序的文档列表
    root_nodes = build_tree(0)
    ordered_docs = dfs_flatten(root_nodes)

    # 调试：打印扁平化后的文档顺序
    print(f"=== Navigation for doc: {doc.title} (id={doc.id}) ===")
    print("Flattened doc order:")
    for i, d in enumerate(ordered_docs):
        prefix = "  -> " * (d.level - 1) if d.level > 1 else ""
        print(f"  {i}. {prefix}{d.title} (id={d.id}, parent_id={d.parent_id}, sort_order={d.sort_order})")
    print("=" * 50)

    # 查找上一篇和下一篇（跨节点）
    # 在扁平化的线性序列中，上一篇=前一个，下一篇=后一个
    prev_doc = None
    next_doc = None
    for i, d in enumerate(ordered_docs):
        if d.id == doc.id:
            if i > 0:
                prev_doc = ordered_docs[i - 1]
            if i < len(ordered_docs) - 1:
                next_doc = ordered_docs[i + 1]
            break

    # 获取父文档
    parent_doc = None
    if doc.parent_id and doc.parent_id != 0:
        parent_doc = await get_doc_by_id(db, doc.parent_id)

    # 获取面包屑
    breadcrumbs = await get_breadcrumbs(db, doc)

    return schemas.DocNavigation(
        prev=schemas.DocResponse.model_validate(prev_doc) if prev_doc else None,
        next=schemas.DocResponse.model_validate(next_doc) if next_doc else None,
        parent=schemas.DocResponse.model_validate(parent_doc) if parent_doc else None,
        breadcrumbs=[schemas.DocResponse.model_validate(b) for b in breadcrumbs]
    )


def calculate_path(parent: Optional[models.Doc], level: int) -> str:
    """计算文档路径"""
    if parent is None or parent.parent_id == 0:
        return '0'
    return f"{parent.path}/{parent.id}"


async def create_doc(
    db: AsyncSession,
    doc: schemas.DocCreate,
    author_id: int
) -> models.Doc:
    """创建文档"""
    # 获取父文档
    parent = None
    if doc.parent_id and doc.parent_id != 0:
        parent = await get_doc_by_id(db, doc.parent_id)

    # 计算层级和路径
    level = 1
    path = '0'
    if parent:
        level = parent.level + 1
        path = calculate_path(parent, level)

    new_doc = models.Doc(
        **doc.model_dump(),
        level=level,
        path=path,
        author_id=author_id,
        createtime=int(time.time()),
        updatetime=int(time.time())
    )
    db.add(new_doc)
    await db.commit()
    await db.refresh(new_doc)
    return new_doc


async def update_doc(
    db: AsyncSession,
    doc_id: int,
    doc: schemas.DocUpdate
) -> Optional[models.Doc]:
    """更新文档"""
    result = await db.execute(
        select(models.Doc).where(models.Doc.id == doc_id)
    )
    doc_to_update = result.scalar_one_or_none()
    if doc_to_update:
        update_data = doc.model_dump(exclude_unset=True)

        # 如果修改了parent_id，需要重新计算level和path
        if 'parent_id' in update_data:
            new_parent_id = update_data['parent_id']
            doc_to_update.parent_id = new_parent_id  # 也要更新 parent_id 本身
            if new_parent_id and new_parent_id != 0:
                parent = await get_doc_by_id(db, new_parent_id)
                if parent:
                    doc_to_update.level = parent.level + 1
                    doc_to_update.path = calculate_path(parent, parent.level + 1)
            else:
                doc_to_update.level = 1
                doc_to_update.path = '0'

        for key, value in update_data.items():
            if key != 'parent_id':
                setattr(doc_to_update, key, value)

        doc_to_update.updatetime = int(time.time())

        # 如果状态从draft变为published，设置发布时间
        if doc_to_update.status == 'published' and not doc_to_update.pubtime:
            doc_to_update.pubtime = int(time.time())

        await db.commit()
        await db.refresh(doc_to_update)

    return doc_to_update


async def delete_doc(db: AsyncSession, doc_id: int) -> Optional[models.Doc]:
    """删除文档"""
    result = await db.execute(
        select(models.Doc).where(models.Doc.id == doc_id)
    )
    doc_to_delete = result.scalar_one_or_none()
    if doc_to_delete:
        await db.delete(doc_to_delete)
        await db.commit()
    return doc_to_delete


async def move_doc(
    db: AsyncSession,
    doc_id: int,
    new_parent_id: int,
    new_sort_order: int
) -> Optional[models.Doc]:
    """移动文档（拖拽排序）"""
    result = await db.execute(
        select(models.Doc).where(models.Doc.id == doc_id)
    )
    doc_to_move = result.scalar_one_or_none()

    if doc_to_move:
        old_parent_id = doc_to_move.parent_id

        # 更新父级和排序
        doc_to_move.parent_id = new_parent_id
        doc_to_move.sort_order = new_sort_order

        # 重新计算层级和路径
        if new_parent_id and new_parent_id != 0:
            parent = await get_doc_by_id(db, new_parent_id)
            if parent:
                doc_to_move.level = parent.level + 1
                doc_to_move.path = calculate_path(parent, parent.level + 1)
        else:
            doc_to_move.level = 1
            doc_to_move.path = '0'

        doc_to_move.updatetime = int(time.time())

        # 如果修改了同级排序，需要更新其他文档的sort_order
        if old_parent_id == new_parent_id:
            await db.execute(
                update(models.Doc).where(
                    models.Doc.docbook_id == doc_to_move.docbook_id,
                    models.Doc.parent_id == new_parent_id,
                    models.Doc.sort_order >= new_sort_order,
                    models.Doc.id != doc_id
                ).values(sort_order=models.Doc.sort_order + 1)
            )

        await db.commit()
        await db.refresh(doc_to_move)

    return doc_to_move


async def increase_view_count(db: AsyncSession, doc_id: int) -> bool:
    """增加浏览次数"""
    result = await db.execute(
        update(models.Doc).where(
            models.Doc.id == doc_id
        ).values(view_count=models.Doc.view_count + 1)
    )
    await db.commit()
    return result.rowcount > 0


async def get_doc_children(
    db: AsyncSession,
    doc_id: int,
    status: Optional[str] = None
) -> List[models.Doc]:
    """获取子文档列表"""
    query = select(models.Doc).where(
        models.Doc.parent_id == doc_id
    ).order_by(models.Doc.sort_order)

    if status:
        query = query.where(models.Doc.status == status)

    result = await db.execute(query)
    return list(result.scalars().all())


async def search_docs(
    db: AsyncSession,
    docbook_id: int,
    keyword: str,
    limit: int = 20
) -> List[models.Doc]:
    """全文搜索文档"""
    result = await db.execute(
        select(models.Doc).where(
            models.Doc.docbook_id == docbook_id,
            models.Doc.status == 'published',
            or_(
                models.Doc.title.like(f'%{keyword}%'),
                models.Doc.content.like(f'%{keyword}%'),
                models.Doc.excerpt.like(f'%{keyword}%')
            )
        ).limit(limit)
    )
    return list(result.scalars().all())
