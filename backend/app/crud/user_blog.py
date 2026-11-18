"""Author 个人博客（Creator 工作台）CRUD。

所有查询都以 user_id 收敛——本模块的数据天然按博主隔离，
不存在跨用户读写路径（user_id 一律来自已认证的当前用户，而非请求参数）。
"""
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.data.user_blog import UserBlogConfig, UserCategory, UserSeries, UserNav
from app.models.schemas import user_blog as schemas
from app.utils.blog_slug import resolve_slug


# ---------- blog 配置 ----------

async def get_blog_config(db: AsyncSession, user_id: int) -> UserBlogConfig | None:
    result = await db.execute(
        select(UserBlogConfig).where(UserBlogConfig.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def create_blog_config(db: AsyncSession, user_id: int) -> UserBlogConfig:
    config = UserBlogConfig(user_id=user_id)
    db.add(config)
    await db.commit()
    await db.refresh(config)
    return config


async def get_or_create_blog_config(db: AsyncSession, user_id: int) -> UserBlogConfig:
    """读取配置；首次访问工作台时自动开通（生成一行默认配置）。"""
    config = await get_blog_config(db, user_id)
    if config is None:
        config = await create_blog_config(db, user_id)
    return config


async def update_blog_config(
    db: AsyncSession, user_id: int, data: schemas.UserBlogConfigUpdate
) -> UserBlogConfig | None:
    config = await get_or_create_blog_config(db, user_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(config, key, value)
    await db.commit()
    await db.refresh(config)
    return config


# ---------- blog 分类 ----------

async def get_categories(db: AsyncSession, user_id: int) -> list[UserCategory]:
    """按 sort 升序返回该博主的全部分类。"""
    result = await db.execute(
        select(UserCategory)
        .where(UserCategory.user_id == user_id)
        .order_by(UserCategory.sort.asc())
    )
    return list(result.scalars().all())


async def create_category(
    db: AsyncSession, user_id: int, data: schemas.UserCategoryCreate
) -> UserCategory:
    payload = data.model_dump()
    payload['slug'] = await resolve_slug(
        db, user_id, payload.get('slug'), payload.get('name') or 'item', UserCategory
    )
    category = UserCategory(user_id=user_id, **payload)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def update_category(
    db: AsyncSession, user_id: int, category_id: int, data: schemas.UserCategoryUpdate
) -> UserCategory | None:
    result = await db.execute(
        select(UserCategory).where(
            UserCategory.id == category_id, UserCategory.user_id == user_id
        )
    )
    category = result.scalar_one_or_none()
    if not category:
        return None
    payload = data.model_dump(exclude_unset=True)
    # slug 留空/显式置空时，若本次改了名称则按新名称生成；否则沿用旧 slug
    if 'slug' in payload and not payload['slug']:
        new_name = payload.get('name') or category.name
        payload['slug'] = await resolve_slug(
            db, user_id, None, new_name, UserCategory, exclude_id=category_id
        )
    elif 'slug' in payload and payload['slug']:
        payload['slug'] = await resolve_slug(
            db, user_id, payload['slug'], payload.get('name') or category.name,
            UserCategory, exclude_id=category_id
        )
    for key, value in payload.items():
        setattr(category, key, value)
    await db.commit()
    await db.refresh(category)
    return category


async def delete_category(db: AsyncSession, user_id: int, category_id: int) -> bool:
    result = await db.execute(
        delete(UserCategory).where(
            UserCategory.id == category_id, UserCategory.user_id == user_id
        )
    )
    await db.commit()
    return result.rowcount > 0


async def sort_categories(db: AsyncSession, user_id: int, ids: list[int]) -> int:
    """按传入顺序重排 sort；仅作用于该博主的分类，返回受影响行数。"""
    sort_map = {category_id: index for index, category_id in enumerate(ids)}
    categories = await get_categories(db, user_id)
    changed = 0
    for category in categories:
        if category.id in sort_map and category.sort != sort_map[category.id]:
            category.sort = sort_map[category.id]
            changed += 1
    if changed:
        await db.commit()
    return changed


# ---------- blog 系列 ----------

async def get_series_list(db: AsyncSession, user_id: int) -> list[UserSeries]:
    result = await db.execute(
        select(UserSeries)
        .where(UserSeries.user_id == user_id)
        .order_by(UserSeries.sort.asc())
    )
    return list(result.scalars().all())


async def create_series(
    db: AsyncSession, user_id: int, data: schemas.UserSeriesCreate
) -> UserSeries:
    payload = data.model_dump()
    payload['slug'] = await resolve_slug(
        db, user_id, payload.get('slug'), payload.get('name') or 'item', UserSeries
    )
    series = UserSeries(user_id=user_id, **payload)
    db.add(series)
    await db.commit()
    await db.refresh(series)
    return series


async def update_series(
    db: AsyncSession, user_id: int, series_id: int, data: schemas.UserSeriesUpdate
) -> UserSeries | None:
    result = await db.execute(
        select(UserSeries).where(UserSeries.id == series_id, UserSeries.user_id == user_id)
    )
    series = result.scalar_one_or_none()
    if not series:
        return None
    payload = data.model_dump(exclude_unset=True)
    # 现有系列可能还没有 slug（历史数据）；每次编辑都确保有值
    if not getattr(series, 'slug', None) and 'slug' not in payload:
        payload['slug'] = await resolve_slug(
            db, user_id, None, payload.get('name') or series.name, UserSeries,
            exclude_id=series_id
        )
    elif 'slug' in payload:
        payload['slug'] = await resolve_slug(
            db, user_id, payload['slug'], payload.get('name') or series.name,
            UserSeries, exclude_id=series_id
        )
    for key, value in payload.items():
        setattr(series, key, value)
    await db.commit()
    await db.refresh(series)
    return series


async def delete_series(db: AsyncSession, user_id: int, series_id: int) -> bool:
    result = await db.execute(
        delete(UserSeries).where(UserSeries.id == series_id, UserSeries.user_id == user_id)
    )
    await db.commit()
    return result.rowcount > 0


async def sort_series(db: AsyncSession, user_id: int, ids: list[int]) -> int:
    sort_map = {series_id: index for index, series_id in enumerate(ids)}
    series_list = await get_series_list(db, user_id)
    changed = 0
    for series in series_list:
        if series.id in sort_map and series.sort != sort_map[series.id]:
            series.sort = sort_map[series.id]
            changed += 1
    if changed:
        await db.commit()
    return changed


# ---------- blog 导航 ----------

async def get_navs(db: AsyncSession, user_id: int) -> list[UserNav]:
    result = await db.execute(
        select(UserNav)
        .where(UserNav.user_id == user_id)
        .order_by(UserNav.sort.asc())
    )
    return list(result.scalars().all())


async def create_nav(db: AsyncSession, user_id: int, data: schemas.UserNavCreate) -> UserNav:
    nav = UserNav(user_id=user_id, **data.model_dump())
    db.add(nav)
    await db.commit()
    await db.refresh(nav)
    return nav


async def update_nav(
    db: AsyncSession, user_id: int, nav_id: int, data: schemas.UserNavUpdate
) -> UserNav | None:
    result = await db.execute(
        select(UserNav).where(UserNav.id == nav_id, UserNav.user_id == user_id)
    )
    nav = result.scalar_one_or_none()
    if not nav:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(nav, key, value)
    await db.commit()
    await db.refresh(nav)
    return nav


async def delete_nav(db: AsyncSession, user_id: int, nav_id: int) -> bool:
    result = await db.execute(
        delete(UserNav).where(UserNav.id == nav_id, UserNav.user_id == user_id)
    )
    await db.commit()
    return result.rowcount > 0


async def sort_navs(db: AsyncSession, user_id: int, ids: list[int]) -> int:
    sort_map = {nav_id: index for index, nav_id in enumerate(ids)}
    navs = await get_navs(db, user_id)
    changed = 0
    for nav in navs:
        if nav.id in sort_map and nav.sort != sort_map[nav.id]:
            nav.sort = sort_map[nav.id]
            changed += 1
    if changed:
        await db.commit()
    return changed
