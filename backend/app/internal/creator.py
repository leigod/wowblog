"""Author 个人博客（Creator 工作台）接口组。

挂载于 /api/creator 前缀，整组依赖 get_current_blog_owner（Admin/Author）。
所有数据操作以当前认证用户的 id 收敛——请求中不携带 user_id 参数，
跨用户读写无路径。与 /api/admin/* 的平台管理接口完全隔离。

对应前台呈现：/blog/:username（公开只读，另在 blog.py 实现）。
"""
from typing import Annotated, List
import json

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.authentication import get_current_blog_owner
from app.models.response import ApiResponse
from app.utils.response import success, error
from app.models.schemas import user_blog as schemas
from app.crud import user_blog as crud


router = APIRouter()


###########
# blog 配置（常规设置 + 外观设置）
###########

async def _read_social_profiles(db: AsyncSession, user_id: int) -> list[dict]:
    """读 wb_users.social_profiles（与个人资料同源），转为 [{platform, url}] 列表。

    get_current_blog_owner 返回的是 Pydantic schema（无该字段），需直查 ORM 列。
    """
    from sqlalchemy import select as sa_select
    from app.models.data.users import User as UserModel

    row = await db.execute(
        sa_select(UserModel.social_profiles).where(UserModel.id == user_id)
    )
    raw_text = row.scalar_one_or_none()
    try:
        raw = json.loads(raw_text) if raw_text else {}
        if isinstance(raw, dict):
            return [{'platform': k, 'url': str(v)} for k, v in raw.items() if v]
    except (ValueError, TypeError):
        pass
    return []


@router.get('/blog/config', response_model=ApiResponse[schemas.UserBlogConfig])
async def get_blog_config(
    current_user: Annotated[object, Depends(get_current_blog_owner)],
    db: AsyncSession = Depends(get_db),
):
    """读取当前用户的 blog 配置；首次访问自动开通（生成默认配置行）。

    social_links 与个人资料同源：实际数据在 wb_users.social_profiles（JSON 对象），
    此处转换为列表形态给前端编辑；wb_user_blogs.social_links 列停用。
    """
    config = await crud.get_or_create_blog_config(db, user_id=current_user.id)
    data = schemas.UserBlogConfig.model_validate(config)
    data.social_links = await _read_social_profiles(db, current_user.id)
    return success(data=data)


@router.put('/blog/config', response_model=ApiResponse[schemas.UserBlogConfig])
async def update_blog_config(
    config_data: schemas.UserBlogConfigUpdate,
    current_user: Annotated[object, Depends(get_current_blog_owner)],
    db: AsyncSession = Depends(get_db),
):
    """更新 blog 配置（名称/说明/impressum/logo/favicon/布局），支持部分字段提交。

    social_links 单独处理：转回 JSON 对象写入 wb_users.social_profiles（与个人资料同源），
    不落 wb_user_blogs.social_links。
    """
    from sqlalchemy import update as sa_update
    from app.models.data.users import User as UserModel

    update_payload = config_data.model_dump(exclude_unset=True)
    social_list = update_payload.pop('social_links', None)

    if social_list is not None:
        social_dict = {
            str(item.get('platform', '')).strip(): str(item.get('url', '')).strip()
            for item in social_list if isinstance(item, dict)
        }
        social_dict = {k: v for k, v in social_dict.items() if k and v}
        await db.execute(
            sa_update(UserModel)
            .where(UserModel.id == current_user.id)
            .values(social_profiles=json.dumps(social_dict, ensure_ascii=False))
        )
        await db.commit()

    config = await crud.update_blog_config(
        db, user_id=current_user.id,
        data=schemas.UserBlogConfigUpdate(**update_payload)
    )
    # 响应与 GET 一致：social_links 以列表形态回显（PUT 分支用刚写入的 social_dict）
    data = schemas.UserBlogConfig.model_validate(config)
    data.social_links = (
        [{'platform': k, 'url': v} for k, v in social_dict.items()]
        if social_list is not None
        else await _read_social_profiles(db, current_user.id)
    )
    return success(data=data)


###########
# blog 分类（仅一级，可排序）
###########

@router.get('/categories', response_model=ApiResponse[List[schemas.UserCategory]])
async def list_categories(
    current_user: Annotated[object, Depends(get_current_blog_owner)],
    db: AsyncSession = Depends(get_db),
):
    categories = await crud.get_categories(db, user_id=current_user.id)
    return success(data=categories)


@router.post('/categories', response_model=ApiResponse[schemas.UserCategory])
async def create_category(
    data: schemas.UserCategoryCreate,
    current_user: Annotated[object, Depends(get_current_blog_owner)],
    db: AsyncSession = Depends(get_db),
):
    """新建分类。slug 需同用户内唯一，冲突时返回错误由前端重新生成。"""
    existing = {c.slug for c in await crud.get_categories(db, user_id=current_user.id)}
    if data.slug in existing:
        return error(msg='分类 slug 已存在，请更换')
    category = await crud.create_category(db, user_id=current_user.id, data=data)
    return success(data=category)


@router.put('/categories/{category_id}', response_model=ApiResponse[schemas.UserCategory])
async def update_category(
    category_id: Annotated[int, Path()],
    data: schemas.UserCategoryUpdate,
    current_user: Annotated[object, Depends(get_current_blog_owner)],
    db: AsyncSession = Depends(get_db),
):
    if data.slug is not None:
        categories = await crud.get_categories(db, user_id=current_user.id)
        # 除自身外的 slug 集合（自己保持原 slug 不算冲突）
        others = {c.slug for c in categories if c.id != category_id}
        if data.slug in others:
            return error(msg='分类 slug 已存在，请更换')
    category = await crud.update_category(
        db, user_id=current_user.id, category_id=category_id, data=data
    )
    if not category:
        return error(msg='分类不存在')
    return success(data=category)


@router.delete('/categories/{category_id}', response_model=ApiResponse[dict])
async def delete_category(
    category_id: Annotated[int, Path()],
    current_user: Annotated[object, Depends(get_current_blog_owner)],
    db: AsyncSession = Depends(get_db),
):
    deleted = await crud.delete_category(db, user_id=current_user.id, category_id=category_id)
    if not deleted:
        return error(msg='分类不存在')
    return success(data={'deleted': category_id})


@router.post('/categories/sortbatch', response_model=ApiResponse[dict])
async def sort_categories(
    data: schemas.SortBatchRequest,
    current_user: Annotated[object, Depends(get_current_blog_owner)],
    db: AsyncSession = Depends(get_db),
):
    changed = await crud.sort_categories(db, user_id=current_user.id, ids=data.ids)
    return success(data={'changed': changed})


###########
# blog 系列（可排序）
###########

@router.get('/series', response_model=ApiResponse[List[schemas.UserSeries]])
async def list_series(
    current_user: Annotated[object, Depends(get_current_blog_owner)],
    db: AsyncSession = Depends(get_db),
):
    series_list = await crud.get_series_list(db, user_id=current_user.id)
    return success(data=series_list)


@router.post('/series', response_model=ApiResponse[schemas.UserSeries])
async def create_series(
    data: schemas.UserSeriesCreate,
    current_user: Annotated[object, Depends(get_current_blog_owner)],
    db: AsyncSession = Depends(get_db),
):
    series = await crud.create_series(db, user_id=current_user.id, data=data)
    return success(data=series)


@router.put('/series/{series_id}', response_model=ApiResponse[schemas.UserSeries])
async def update_series(
    series_id: Annotated[int, Path()],
    data: schemas.UserSeriesUpdate,
    current_user: Annotated[object, Depends(get_current_blog_owner)],
    db: AsyncSession = Depends(get_db),
):
    series = await crud.update_series(db, user_id=current_user.id, series_id=series_id, data=data)
    if not series:
        return error(msg='系列不存在')
    return success(data=series)


@router.delete('/series/{series_id}', response_model=ApiResponse[dict])
async def delete_series(
    series_id: Annotated[int, Path()],
    current_user: Annotated[object, Depends(get_current_blog_owner)],
    db: AsyncSession = Depends(get_db),
):
    deleted = await crud.delete_series(db, user_id=current_user.id, series_id=series_id)
    if not deleted:
        return error(msg='系列不存在')
    return success(data={'deleted': series_id})


@router.post('/series/sortbatch', response_model=ApiResponse[dict])
async def sort_series(
    data: schemas.SortBatchRequest,
    current_user: Annotated[object, Depends(get_current_blog_owner)],
    db: AsyncSession = Depends(get_db),
):
    changed = await crud.sort_series(db, user_id=current_user.id, ids=data.ids)
    return success(data={'changed': changed})


###########
# blog 导航（无系统项；类型 link/category/series）
###########

@router.get('/navs', response_model=ApiResponse[List[schemas.UserNav]])
async def list_navs(
    current_user: Annotated[object, Depends(get_current_blog_owner)],
    db: AsyncSession = Depends(get_db),
):
    navs = await crud.get_navs(db, user_id=current_user.id)
    return success(data=navs)


@router.post('/navs', response_model=ApiResponse[schemas.UserNav])
async def create_nav(
    data: schemas.UserNavCreate,
    current_user: Annotated[object, Depends(get_current_blog_owner)],
    db: AsyncSession = Depends(get_db),
):
    nav = await crud.create_nav(db, user_id=current_user.id, data=data)
    return success(data=nav)


@router.put('/navs/{nav_id}', response_model=ApiResponse[schemas.UserNav])
async def update_nav(
    nav_id: Annotated[int, Path()],
    data: schemas.UserNavUpdate,
    current_user: Annotated[object, Depends(get_current_blog_owner)],
    db: AsyncSession = Depends(get_db),
):
    nav = await crud.update_nav(db, user_id=current_user.id, nav_id=nav_id, data=data)
    if not nav:
        return error(msg='导航不存在')
    return success(data=nav)


@router.delete('/navs/{nav_id}', response_model=ApiResponse[dict])
async def delete_nav(
    nav_id: Annotated[int, Path()],
    current_user: Annotated[object, Depends(get_current_blog_owner)],
    db: AsyncSession = Depends(get_db),
):
    deleted = await crud.delete_nav(db, user_id=current_user.id, nav_id=nav_id)
    if not deleted:
        return error(msg='导航不存在')
    return success(data={'deleted': nav_id})


@router.post('/navs/sortbatch', response_model=ApiResponse[dict])
async def sort_navs(
    data: schemas.SortBatchRequest,
    current_user: Annotated[object, Depends(get_current_blog_owner)],
    db: AsyncSession = Depends(get_db),
):
    changed = await crud.sort_navs(db, user_id=current_user.id, ids=data.ids)
    return success(data={'changed': changed})
