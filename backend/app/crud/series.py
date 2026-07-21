import app.models.data.series as models
import app.models.data.articles as models_articles
import app.models.data.users as models_users
import app.models.schemas.series as schemas
import app.models.schemas.articles as schemas_articles
import app.models.schemas.users as schemasUsers
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List


# 查询所有系列
async def get_series_list(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(models.BlogSeries).offset(skip).limit(limit).order_by(models.BlogSeries.sort.asc())
    )
    return [schemas.BlogSeries.model_validate(series) for series in result.scalars().all()]


# 根据ID获取系列详情
async def get_series(db: AsyncSession, series_id: int):
    result = await db.execute(
        select(models.BlogSeries).where(models.BlogSeries.id == series_id)
    )
    data = result.scalar_one_or_none()
    if data:
        return data
    return None


# 添加系列
async def create_series(db: AsyncSession, series: schemas.BlogSeriesCreate):
    new_series = models.BlogSeries(**series.dict())
    db.add(new_series)
    await db.commit()
    await db.refresh(new_series)
    return new_series


# 修改系列
async def update_series(db: AsyncSession, series_id: int, series: schemas.BlogSeriesUpdate):
    result = await db.execute(
        select(models.BlogSeries).where(models.BlogSeries.id == series_id)
    )
    series_to_update = result.scalar_one_or_none()
    if series_to_update:
        update_data = series.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(series_to_update, key, value)
        await db.commit()
        await db.refresh(series_to_update)
        return series_to_update
    return None


# 批量修改系列排序
async def update_series_sort(db: AsyncSession, series_ids: List[int]) -> List[models.BlogSeries]:
    # 创建ID到排序值的映射 {id: index}
    id_to_sort = {series_id: idx for idx, series_id in enumerate(series_ids)}
    
    # 批量查询所有相关记录
    result = await db.execute(
        select(models.BlogSeries).where(models.BlogSeries.id.in_(series_ids))
    )
    series_to_update = result.scalars().all()
    
    # 更新排序值
    for series in series_to_update:
        series.sort = id_to_sort[series.id]
    
    # 提交事务
    await db.commit()
    
    # 刷新并返回所有更新后的记录
    updated_series = []
    for series in series_to_update:
        await db.refresh(series)
        updated_series.append(series)
    
    return updated_series



# 删除系列
async def delete_series(db: AsyncSession, series_id: int):
    result = await db.execute(
        select(models.BlogSeries).where(models.BlogSeries.id == series_id)
    )
    series_to_delete = result.scalar_one_or_none()
    if series_to_delete:
        await db.delete(series_to_delete)
        await db.commit()
        return series_to_delete
    return None



# 根据slug获取series详情
async def get_series_by_slug(db: AsyncSession, slug: str):
    result = await db.execute(
        select(models.BlogSeries).where(models.BlogSeries.slug == slug)
    )
    data = result.scalar_one_or_none()
    if data:
        return data
    return None


# 根据slug获取该series下的文章列表
async def get_articles_by_series_slug(db: AsyncSession, slug: str, skip: int = 0, limit: int = 100):
    series = await get_series_by_slug(db, slug)
    if series is None:
        return None
    if series.articles_order == 'asc':
        result = await db.execute(
            select(models_articles.BlogArticle,models_users.User.full_name, models_users.User.username, models_users.User.profile_image, models_articles.BlogArticleStatData)
            .join(models_users.User, models_articles.BlogArticle.author == models_users.User.id)
            .join(models_articles.BlogArticleStatData, models_articles.BlogArticle.id == models_articles.BlogArticleStatData.article_id)
            .where(models_articles.BlogArticle.series_id == series.id)
            .where(models_articles.BlogArticle.status == 'published')
            .offset(skip).limit(limit).order_by(models_articles.BlogArticle.pub_time.asc())
        )
    else:
        result = await db.execute(
            select(models_articles.BlogArticle,models_users.User.full_name, models_users.User.username, models_users.User.profile_image, models_articles.BlogArticleStatData)
            .join(models_users.User, models_articles.BlogArticle.author == models_users.User.id)
            .join(models_articles.BlogArticleStatData, models_articles.BlogArticle.id == models_articles.BlogArticleStatData.article_id)
            .where(models_articles.BlogArticle.series_id == series.id)
            .where(models_articles.BlogArticle.status == 'published')
            .offset(skip).limit(limit).order_by(models_articles.BlogArticle.pub_time.desc())
        )
    articles_with_user_info = []
    for row in result.all():
        article, full_name, username, profile_image, stat_data = row
        # 将文章对象转换为字典
        article_dict = schemas_articles.BlogArticle.model_validate(article).model_dump()
        # 添加用户信息
        article_dict['author_full_name'] = full_name
        article_dict['author_username'] = username
        article_dict['author_profile_image'] = profile_image
        # 添加文章统计数据
        article_dict['likes'] = stat_data.likes
        article_dict['comments'] = stat_data.comments
        article_dict['views'] = stat_data.views
        article_dict['bookmarks'] = stat_data.bookmarks
        article_dict['shares'] = stat_data.shares
        articles_with_user_info.append(article_dict)
    
    return articles_with_user_info


# 获取series下的文章总数
async def get_article_count_by_series_slug(db: AsyncSession, slug: str):
    series = await get_series_by_slug(db, slug)
    if series is None:
        return None
    result = await db.execute(
        select(func.count(models_articles.BlogArticle.id.distinct())).select_from(models_articles.BlogArticle)
        .join(models_users.User, models_articles.BlogArticle.author == models_users.User.id)
        .where(models_articles.BlogArticle.series_id == series.id)
        .where(models_articles.BlogArticle.status == 'published')
    )
    return result.scalar_one()
