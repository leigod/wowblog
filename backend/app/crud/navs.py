from sqlalchemy.orm import Session
import app.models.data.navs as models
import app.models.data.category as models_category
import app.models.data.series as models_series
import app.crud.pages as crudPages
import app.crud.series as crudSeries
import app.models.schemas.navs as schemas
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any



# 辅助函数：构建分类树结构，最多3级
async def build_category_tree(db: AsyncSession) -> List[Dict[str, Any]]:
    # 获取所有分类
    result = await db.execute(
        select(models_category.BlogCategory)
        .order_by(models_category.BlogCategory.sort.desc(), models_category.BlogCategory.id.desc())
    )
    categories = result.scalars().all()
    
    # 转换为字典以便快速查找
    category_dict = {cat.id: cat for cat in categories}
    
    # 构建树结构，最多3级
    tree = []
    
    # 第一级分类 (pid = 0)
    for cat in categories:
        if cat.pid == 0:
            category_data = {
                'id': cat.id,
                'label': cat.name,
                'slug': cat.slug,
                'url': f'/category/{cat.slug}',
                'children': []
            }
            
            # 第二级分类
            for child_cat in categories:
                if child_cat.pid == cat.id:
                    child_data = {
                        'id': child_cat.id,
                        'label': child_cat.name,
                        'slug': child_cat.slug,
                        'url': f'/category/{child_cat.slug}',
                        'children': []
                    }
                    
                    # 第三级分类
                    for grand_child_cat in categories:
                        if grand_child_cat.pid == child_cat.id:
                            grand_child_data = {
                                'id': grand_child_cat.id,
                                'label': grand_child_cat.name,
                                'slug': grand_child_cat.slug,
                                'url': f'/category/{grand_child_cat.slug}'
                            }
                            child_data['children'].append(grand_child_data)
                    
                    category_data['children'].append(child_data)
            
            tree.append(category_data)
    
    return tree

# 辅助函数，构建系列树，系列仅1级
async def build_series_tree(db: AsyncSession) -> List[Dict[str, Any]]:
    result = await db.execute(
        select(models_series.BlogSeries)
        .order_by(models_series.BlogSeries.sort.asc())
    )
    series = result.scalars().all()
    
    # 转换为字典以便快速查找
    series_dict = {s.id: s for s in series}
    
    # 构建树结构，最多3级
    tree = []
    
    # 第一级分类 (pid = 0)
    for s in series:
        series_data = {
            'id': s.id,
            'label': s.name,
            'slug': s.slug,
            'url': f'/series/{s.slug}'
        }
        
        tree.append(series_data)
    
    return tree

# 获取所有导航
async def get_navs(db: AsyncSession, skip: int = 0, limit: int = 100):
    # 同步查询语法
    # result = await db.query(models.BlogNav).offset(skip).limit(limit).all()
    # return result
    # 使用异步查询语法替换 db.query()
    result = await db.execute(
        select(models.BlogNav).where(models.BlogNav.status == 1).offset(skip).limit(limit).order_by(models.BlogNav.sort.asc())
    )
    # 系统预置2个导航，ID为1和2，分别为“首页”和“分类”
    # 当导航为ID为2的分类导航时，需获取所有分类及其子分类，最多3级，分类的url为/categories/<slug>
    # 当ID为3时，获取所有系列，url为/series/<slug>
    # 当导航的type为page时，url为/pages/<slug>
    # 当导航的type为series时，url为/series/<slug>

    navs = result.scalars().all()
    processed_navs = []
    
    # 构建分类树（如果需要）
    category_tree = None
    series_tree = None
    for nav in navs:
        if nav.id == 2:
            category_tree = await build_category_tree(db)
        elif nav.id == 3:
            series_tree = await build_series_tree(db)
    
    # 处理每个导航项
    for nav in navs:
        nav_data = schemas.BlogNav.model_validate(nav).model_dump()
        
        # 根据导航类型设置URL
        if nav.type == 'page':
            page = await crudPages.get_page(db, nav.value)
            nav_data['url'] = f'/page/{page.slug}'
        elif nav.type == 'series':
            series = await crudSeries.get_series(db, nav.value)
            nav_data['url'] = f'/series/{series.slug}'
        elif nav.type == 'link' and nav.id == 2:
            # 对于分类导航，使用固定URL并添加子分类
            nav_data['url'] = '/category'
            
            # 如果是ID为2的分类导航，添加子分类树
            if nav.id == 2 and category_tree:
                nav_data['children'] = category_tree
        elif nav.type == 'link' and nav.id == 3:
            # 对于系列导航，使用固定URL并添加子系列
            nav_data['url'] = '/series'
            
            # 如果是ID为3的系列导航，添加子系列树
            if nav.id == 3 and series_tree:
                nav_data['children'] = series_tree
        
        processed_navs.append(nav_data)
    
    return processed_navs


# 根据ID获取导航
async def get_nav(db: AsyncSession, nav_id: int):
    result = await db.execute(
        select(models.BlogNav).where(models.BlogNav.id == nav_id)
    )
    nav = result.scalar_one_or_none()
    if nav:
        return [schemas.BlogNav.model_validate(nav)]
    return None


# 添加导航
async def create_nav(db: AsyncSession, nav: schemas.BlogNavCreate):
    new_nav = models.BlogNav(**nav.dict())
    db.add(new_nav)
    await db.commit()
    await db.refresh(new_nav)
    return new_nav


# 修改导航
async def update_nav(db: AsyncSession, nav_id: int, nav: schemas.BlogNavUpdate):
    result = await db.execute(
        select(models.BlogNav).where(models.BlogNav.id == nav_id)
    )
    nav_to_update = result.scalar_one_or_none()
    if nav_to_update:
        update_data = nav.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(nav_to_update, key, value)
        await db.commit()
        await db.refresh(nav_to_update)
        return nav_to_update
    return None


# 修改导航排序
async def update_nav_sort(db: AsyncSession, nav_id: int, nav: schemas.BlogNavUpdateSort):
    result = await db.execute(
        select(models.BlogNav).where(models.BlogNav.id == nav_id)
    )
    nav_to_update = result.scalar_one_or_none()
    if nav_to_update:
        update_data = nav.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(nav_to_update, key, value)
        await db.commit()
        await db.refresh(nav_to_update)
        return nav_to_update
    return None


# 批量修改导航排序
# 根据ID列表的索引位置更新对应记录的sort值
# :param db: 数据库会话
# :param nav_ids: 导航ID列表，例如 [4,1,2]
# :return: 更新后的导航记录列表
async def update_navs_sort(db: AsyncSession, nav_ids: List[int]) -> List[models.BlogNav]:
    # 创建ID到排序值的映射 {id: index}
    id_to_sort = {nav_id: idx for idx, nav_id in enumerate(nav_ids)}
    
    # 批量查询所有相关记录
    result = await db.execute(
        select(models.BlogNav).where(models.BlogNav.id.in_(nav_ids))
    )
    navs_to_update = result.scalars().all()
    
    # 更新排序值
    for nav in navs_to_update:
        nav.sort = id_to_sort[nav.id]
    
    # 提交事务
    await db.commit()
    
    # 刷新并返回所有更新后的记录
    updated_navs = []
    for nav in navs_to_update:
        await db.refresh(nav)
        updated_navs.append(nav)
    
    return updated_navs


# 修改导航状态
async def update_nav_status(db: AsyncSession, nav_id: int, nav: schemas.BlogNavUpdateStatus):
    result = await db.execute(
        select(models.BlogNav).where(models.BlogNav.id == nav_id)
    )
    nav_to_update = result.scalar_one_or_none()
    if nav_to_update:
        update_data = nav.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(nav_to_update, key, value)
        await db.commit()
        await db.refresh(nav_to_update)
        return nav_to_update
    return None


# 删除导航
async def delete_nav(db: AsyncSession, nav_id: int):
    result = await db.execute(
        select(models.BlogNav).where(models.BlogNav.id == nav_id)
    )
    nav_to_delete = result.scalar_one_or_none()
    if nav_to_delete:
        await db.delete(nav_to_delete)
        await db.commit()
        return nav_to_delete
    return None
