"""
文章浏览记录 CRUD 操作
"""
import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, case, update
from typing import List, Optional
import app.models.data.article_views as models
import app.models.data.articles as models_articles
import app.models.data.users as models_users


async def create_view_record(
    db: AsyncSession,
    user_id: Optional[int],
    article_id: int,
    view_duration: int = 0,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    device_type: Optional[str] = None,
    source: str = "direct",
    device_fingerprint: Optional[str] = None,
) -> models.ArticleView:
    """创建浏览记录"""
    # 判断是否为认真阅读 (停留时长 > 30秒)
    is_deep_read = 1 if view_duration > 30 else 0
    is_logged_in = 1 if user_id else 0

    view_record = models.ArticleView(
        user_id=user_id,
        article_id=article_id,
        view_time=int(time.time()),
        view_duration=view_duration,
        is_deep_read=is_deep_read,
        ip_address=ip_address,
        user_agent=user_agent,
        device_type=device_type,
        source=source,
        device_fingerprint=device_fingerprint,
        is_logged_in=is_logged_in
    )
    db.add(view_record)
    await db.flush()
    return view_record


async def get_user_reading_history(
    db: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
) -> List[dict]:
    """
    获取用户阅读历史 (去重后返回)
    同一篇文章只返回最近一次的浏览记录
    """
    # 子查询: 获取每篇文章的最新浏览时间
    subquery = (
        select(
            models.ArticleView.article_id,
            func.max(models.ArticleView.view_time).label('max_view_time')
        )
        .where(models.ArticleView.user_id == user_id)
        .where(models.ArticleView.is_logged_in == 1)
        .group_by(models.ArticleView.article_id)
        .subquery()
    )

    # 主查询: 获取去重后的浏览记录详情
    query = (
        select(
            models.ArticleView.id,
            models.ArticleView.article_id,
            models.ArticleView.view_time,
            models.ArticleView.view_duration,
            models.ArticleView.is_deep_read,
            models_articles.BlogArticle.title,
            models_articles.BlogArticle.slug,
            models_articles.BlogArticle.cover,
            models_articles.BlogArticle.content,
            models_users.User.full_name.label('author_full_name'),
            models_users.User.username.label('author_username'),
            models_users.User.profile_image.label('author_profile_image'),
        )
        .join(models_articles.BlogArticle, models_articles.BlogArticle.id == models.ArticleView.article_id)
        .join(models_users.User, models_users.User.id == models_articles.BlogArticle.author)
        .join(
            subquery,
            and_(
                models.ArticleView.article_id == subquery.c.article_id,
                models.ArticleView.view_time == subquery.c.max_view_time
            )
        )
        .order_by(desc(models.ArticleView.view_time))
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)
    rows = result.all()

    return [
        {
            'id': row.id,
            'article_id': row.article_id,
            'title': row.title,
            'slug': row.slug,
            'cover': row.cover,
            'content': row.content,
            'view_time': row.view_time,
            'view_duration': row.view_duration,
            'is_deep_read': row.is_deep_read,
            'author_full_name': row.author_full_name,
            'author_username': row.author_username,
            'author_profile_image': row.author_profile_image,
        }
        for row in rows
    ]


async def get_user_reading_history_count(
    db: AsyncSession,
    user_id: int,
) -> int:
    """获取用户阅读历史去重后的数量"""
    query = (
        select(func.count(func.distinct(models.ArticleView.article_id)))
        .where(models.ArticleView.user_id == user_id)
        .where(models.ArticleView.is_logged_in == 1)
    )
    result = await db.execute(query)
    return result.scalar() or 0


async def delete_view_record(
    db: AsyncSession,
    record_id: int,
    user_id: int,
) -> bool:
    """删除单条浏览记录"""
    from sqlalchemy import delete
    query = (
        delete(models.ArticleView)
        .where(and_(
            models.ArticleView.id == record_id,
            models.ArticleView.user_id == user_id
        ))
    )
    await db.execute(query)
    await db.commit()
    return True


async def clear_user_reading_history(
    db: AsyncSession,
    user_id: int,
) -> int:
    """清空用户所有浏览记录，返回删除数量"""
    from sqlalchemy import delete
    # 先获取数量
    count_query = (
        select(func.count())
        .where(models.ArticleView.user_id == user_id)
    )
    result = await db.execute(count_query)
    count = result.scalar() or 0

    # 删除
    delete_query = (
        delete(models.ArticleView)
        .where(models.ArticleView.user_id == user_id)
    )
    await db.execute(delete_query)
    await db.commit()
    return count


async def get_today_stats(
    db: AsyncSession,
) -> dict:
    """获取今日浏览统计"""
    # 获取今天0点的Unix时间戳
    today_start = int(time.time()) - (int(time.time()) % 86400)

    # 总浏览量
    total_query = (
        select(func.count())
        .where(models.ArticleView.view_time >= today_start)
    )
    total_result = await db.execute(total_query)
    total_views = total_result.scalar() or 0

    # 认真阅读数
    deep_query = (
        select(func.count())
        .where(and_(
            models.ArticleView.view_time >= today_start,
            models.ArticleView.is_deep_read == 1
        ))
    )
    deep_result = await db.execute(deep_query)
    deep_reads = deep_result.scalar() or 0

    # 独立访客数 (去重user_id和device_fingerprint)
    unique_query = (
        select(func.count(func.distinct(case(
            (models.ArticleView.user_id.isnot(None), models.ArticleView.user_id),
            else_=models.ArticleView.device_fingerprint
        ))))
        .where(models.ArticleView.view_time >= today_start)
    )
    unique_result = await db.execute(unique_query)
    unique_visitors = unique_result.scalar() or 0

    return {
        'total_views': total_views,
        'unique_visitors': unique_visitors,
        'deep_reads': deep_reads,
    }


async def get_total_stats(
    db: AsyncSession,
) -> dict:
    """获取总浏览统计"""
    total_query = select(func.count())
    total_result = await db.execute(total_query)
    total_views = total_result.scalar() or 0

    deep_query = (
        select(func.count())
        .where(models.ArticleView.is_deep_read == 1)
    )
    deep_result = await db.execute(deep_query)
    deep_reads = deep_result.scalar() or 0

    return {
        'total_views': total_views,
        'deep_reads': deep_reads,
    }


async def get_daily_trend(
    db: AsyncSession,
    days: int = 7,
) -> List[dict]:
    """获取每日浏览趋势"""
    # 计算时间范围
    now = int(time.time())
    start_time = now - (days * 86400)

    # 对齐到当天0点
    start_time = start_time - (start_time % 86400)

    query = (
        select(
            func.date(func.from_unixtime(models.ArticleView.view_time)).label('view_date'),
            func.count().label('views'),
            func.count(func.distinct(case(
                (models.ArticleView.user_id.isnot(None), models.ArticleView.user_id),
                else_=models.ArticleView.device_fingerprint
            ))).label('unique_visitors'),
            func.sum(case(
                (models.ArticleView.is_deep_read == 1, 1),
                else_=0
            )).label('deep_reads')
        )
        .where(models.ArticleView.view_time >= start_time)
        .group_by(func.date(func.from_unixtime(models.ArticleView.view_time)))
        .order_by(func.date(func.from_unixtime(models.ArticleView.view_time)))
    )

    result = await db.execute(query)
    rows = result.all()

    return [
        {
            'date': str(row.view_date),
            'views': row.views,
            'unique_visitors': row.unique_visitors,
            'deep_reads': row.deep_reads or 0,
        }
        for row in rows
    ]


async def update_view_duration(
    db: AsyncSession,
    user_id: Optional[int],
    article_id: int,
    view_duration: int,
) -> bool:
    """更新浏览记录的阅读时长"""
    if not user_id:
        return False

    # 查找最近的浏览记录（最近创建的）
    query = (
        select(models.ArticleView)
        .where(and_(
            models.ArticleView.user_id == user_id,
            models.ArticleView.article_id == article_id
        ))
        .order_by(desc(models.ArticleView.view_time))
        .limit(1)
    )
    result = await db.execute(query)
    view_record = result.scalar_one_or_none()

    if view_record:
        # 更新阅读时长和深度阅读标志
        is_deep_read = 1 if view_duration > 30 else 0
        update_query = (
            update(models.ArticleView)
            .where(models.ArticleView.id == view_record.id)
            .values(
                view_duration=view_duration,
                is_deep_read=is_deep_read
            )
        )
        await db.execute(update_query)
        await db.commit()
        return True
    return False
