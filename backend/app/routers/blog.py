from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import uvicorn
import re
import json
import os
from datetime import datetime

from app.models.response import ApiResponse
from app.database import get_db
from app.utils.response import success, error
from app.utils.logger import api_logger
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Literal

import app.models.data.navs as models
import app.models.data.users as modelsUsers
import app.models.schemas.navs as schemas
import app.models.schemas.articles as schemasArticles
import app.models.schemas.tags as schemasTags
import app.models.schemas.users as schemasUsers
import app.models.schemas.comments as schemasComments
import app.models.schemas.pages as schemasPages
import app.models.schemas.series as schemasSeries
import app.models.schemas.category as schemasCategory
import app.crud.pages as crudPages
import app.crud.articles as crudArticles
import app.crud.tags as crudTags
import app.crud.navs as crud
import app.crud.users as crudUsers
import app.crud.comments as crudComments
import app.crud.series as crudSeries
import app.crud.category as crudCategory
import app.crud.article_views as crudArticleViews
from app.dependencies.authentication import get_current_user_id, get_current_user, get_optional_user_id
from fastapi import Header



router = APIRouter()


# API:获取所有导航
@router.get("/blog/navs", response_model=ApiResponse[List[dict]])
async def get_navs(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    navs = await crud.get_navs(db, skip=skip, limit=limit)
    return success('ok', navs)


@router.get("/blog/navs/{nav_id}", response_model=ApiResponse[List[schemas.BlogNav]])
async def get_nav(nav_id: int, db: AsyncSession = Depends(get_db)):
    nav = await crud.get_nav(db, nav_id=nav_id)
    if nav is None:
        raise HTTPException(status_code=404, detail="Nav not found")
    return success('success', nav)


# 按slug获取blog文章详情
@router.get("/blog/articles/detail/{slug}", response_model=ApiResponse[schemasArticles.BlogArticleResponse])
async def get_article_detail(
    slug: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_optional_user_id)
):
    article_data = await crudArticles.get_article_by_slug(db, article_slug=slug)
    if article_data is None:
        raise HTTPException(status_code=404, detail="Article not found")

    # 创建浏览记录（异步，不阻塞响应）
    try:
        # 获取请求头信息
        user_agent = request.headers.get('user-agent', '')
        ip_address = request.client.host if request.client else None
        device_type = 'mobile' if 'Mobile' in user_agent or 'Android' in user_agent or 'iPhone' in user_agent else 'desktop'

        await crudArticleViews.create_view_record(
            db=db,
            user_id=user_id,
            article_id=article_data['article'].id,
            view_duration=0,  # 初始为0，后续可以通过API更新
            ip_address=ip_address,
            user_agent=user_agent[:500] if user_agent else None,
            device_type=device_type,
            source='direct'
        )
        await db.commit()
    except Exception:
        # 浏览记录创建失败不影响文章详情返回
        api_logger.exception("创建浏览记录失败")

    # 更新文章阅读数
    statData = schemasArticles.ArticleStatDataUpdate(views=1)
    await crudArticles.update_article_statistics(db, article_id=article_data['article'].id, stat_data=statData)
    return success('success', article_data)


# 草稿文章预览（仅Admin和Editor可访问）
@router.get("/blog/articles/preview/{article_id}", response_model=ApiResponse[schemasArticles.BlogArticleResponse])
async def preview_article(
    article_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: modelsUsers.User = Depends(get_current_user)
):
    """
    预览草稿文章
    权限：仅 Admin 和 Editor 可访问
    """
    # 检查权限
    if current_user.role not in ['Admin', 'Editor']:
        raise HTTPException(status_code=403, detail="Only Admin and Editor can preview draft articles")

    # 获取文章（包括草稿状态）
    article_data = await crudArticles.get_article_by_id_for_preview(db, article_id=article_id)
    if article_data is None:
        raise HTTPException(status_code=404, detail="Article not found")

    return success('success', article_data)


# 获取首页文章列表data:{type:all,following,featured,recommend}
@router.post("/blog/articles/list", response_model=ApiResponse[dict])
async def get_article_list(data: schemasArticles.HomeArticleListRequest = None, currentpage: int = 1, pagesize: int = 10,
                            db: AsyncSession = Depends(get_db)):
    if (not data):
        return error('参数错误')
    # 确保页码和每页数量为正数
    currentPage = max(1, currentpage)
    pageSize = max(1, pagesize)

    # 计算偏移量
    skip = (currentPage - 1) * pageSize

    articlelist = await crudArticles.get_home_article_list(reqdata=data, db=db, skip=skip, limit=pageSize)
    total = await crudArticles.get_home_article_count(db, reqdata=data)
    return success(data={
        "list": articlelist,
        "total": total,
        "page": currentPage,
        "pageSize": pageSize
    })


# 获取博客文章列表显示的tag
@router.post("/blog/articles/item/tags", response_model=ApiResponse[List[schemasTags.BlogTag]])
async def get_article_tags(data: List[str], db: AsyncSession = Depends(get_db)):
    tags = await crudArticles.get_article_tags(db, tag_ids=','.join(data))
    if tags is None:
        raise HTTPException(status_code=404, detail="Tags not found")
    return success('success', tags)


# 更新文章点赞、评论、收藏、转发数据
@router.post("/blog/articles/item/updatestat/{article_id}", response_model=ApiResponse[schemasArticles.ArticleStatData])
async def update_article_statistics(article_id: int, data: schemasArticles.ArticleStatDataUpdate, db: AsyncSession = Depends(get_db)):
    db_article = await crudArticles.get_article(db, article_id=article_id)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    result = await crudArticles.update_article_statistics(db, article_id=article_id, stat_data=data)
    if result is None:
        raise HTTPException(status_code=404, detail="Update failed")
    return success('success', result)


# 批量获取文章统计数据
@router.get("/blog/articles/stat", response_model=ApiResponse[List[schemasArticles.ArticleStatData]])
async def get_article_stat(article_ids: str, db: AsyncSession = Depends(get_db)):
    # 将字符串转换为整数列表
    article_ids_list = [int(id_str) for id_str in article_ids.split(',') if id_str.strip().isdigit()]
    # 调整参数顺序，确保与函数定义一致
    result = await crudArticles.get_articles_stat_data(article_ids=article_ids_list, db=db)
    return success(data=result)


# 获取最近更新文章
@router.get("/blog/articles/recent", response_model=ApiResponse[List[schemasArticles.RecentArticles]])
async def get_recently_updated_articles(db: AsyncSession = Depends(get_db), limit: int = 5):
    articles = await crudArticles.get_recently_updated_articles(db, limit=limit)
    return success('success', articles)


# 获取热门标签列表
@router.get("/blog/tags/hot", response_model=ApiResponse[List[schemasTags.BlogTag]])
async def get_hot_tags(db: AsyncSession = Depends(get_db), limit: int = 10):
    tags = await crudTags.get_hot_tags(db, limit=limit)
    return success('success', tags)


# 搜索标签（前端用户用，只返回正常状态的标签）
@router.get("/blog/tags/search/{keyword}", response_model=ApiResponse[List[schemasTags.BlogTag]])
async def search_tags_frontend(keyword: str, db: AsyncSession = Depends(get_db)):
    """前端用户搜索标签，只返回status='normal'的标签"""
    if not keyword or len(keyword.strip()) == 0:
        return success(data=[])
    tags = await crudTags.search_tag_frontend(db, keyword.strip())
    return success(data=tags)


# 获取热门文章列表
@router.get("/blog/articles/hot", response_model=ApiResponse[List[schemasArticles.HotArticles]])
async def get_hot_articles(db: AsyncSession = Depends(get_db), limit: int = 5, days: int = 7):
    articles = await crudArticles.get_hot_articles(db, limit=limit, days=days)
    return success('success', articles)


# 根据slug获取标签信息
@router.get("/blog/tags/detail/{tag_slug}", response_model=ApiResponse[schemasTags.BlogTagPageInfo])
async def get_tag_detail(tag_slug: str, db: AsyncSession = Depends(get_db)):
    tag = await crudTags.get_tag_by_slug(db, tag_slug=tag_slug)
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    # 更新标签浏览量
    await crudTags.update_tag_views(db, tag_id=tag.id)
    
    taginfo = {
        "tag": tag,
        "total_articles": await crudArticles.get_articles_count_by_tag_id(db, tag_id=tag.id, type='all'),
        "total_followers": 0
        }
    return success('success', data=taginfo)


# 根据标签id获取文章列表
@router.get("/blog/tags/articles/{tag_id}", response_model=ApiResponse[dict])
async def get_tag_articles(
        tag_id: str,
        currentpage: int = 1,
        pagesize: int = 10,
        type: Literal['hot', 'new'] = 'hot',
        db: AsyncSession = Depends(get_db)):
    
     # 确保页码和每页数量为正数
    currentPage = max(1, currentpage)
    pageSize = max(1, pagesize)

    # 计算偏移量
    skip = (currentPage - 1) * pageSize
    
    tag_id = int(tag_id)
    articles = await crudArticles.get_articles_by_tag_id(db, tag_id=tag_id, type=type, skip=skip, limit=pageSize)
    total = await crudArticles.get_articles_count_by_tag_id(db, tag_id=tag_id, type=type)

    return success(data={
        "list": articles,
        "total": total,
        "page": currentPage,
        "pageSize": pageSize
    })


# 关注标签
@router.post("/blog/tags/follow/{tag_id}", response_model=ApiResponse[dict])
async def follow_tag(tag_id: int, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await crudUsers.follow_tag(tag_id=tag_id, user_id=user_id, db=db)
    if result is None:
        raise HTTPException(status_code=404, detail="Follow failed")
    return success('success', data={"result": result})


# 取消关注标签
@router.post("/blog/tags/unfollow/{tag_id}", response_model=ApiResponse[dict])
async def unfollow_tag(tag_id: int, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await crudUsers.unfollow_tag(tag_id=tag_id, user_id=user_id, db=db)
    if result is None:
        raise HTTPException(status_code=404, detail="Unfollow failed")
    return success('success', data={"result": result})


# 检查标签关注状态
@router.get("/blog/tags/followstatus/{tag_id}", response_model=ApiResponse[dict])
async def check_follow_tag(tag_id: int, user_id: int = Depends(get_optional_user_id), db: AsyncSession = Depends(get_db)):
    if user_id is None:
        return success('success', data={'is_following': False})
    is_following = await crudUsers.check_follow_tag(tag_id=tag_id, user_id=user_id, db=db)
    if is_following is None:
        raise HTTPException(status_code=404, detail="Check follow status failed")
    return success('success', data={'is_following': is_following})


# 收藏文章
@router.post("/blog/articles/bookmark/{article_id}", response_model=ApiResponse[dict])
async def bookmark_article(article_id: int, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await crudArticles.add_bookmark(article_id=article_id, user_id=user_id, db=db)
    if result is None:
        raise HTTPException(status_code=404, detail="Bookmark failed")
    return success('success', data={"result": result})


# 取消收藏文章
@router.post("/blog/articles/unbookmark/{article_id}", response_model=ApiResponse[dict])
async def unbookmark_article(article_id: int, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await crudArticles.remove_bookmark(article_id=article_id, user_id=user_id, db=db)
    if result is None:
        raise HTTPException(status_code=404, detail="Unbookmark failed")
    return success('success', data={"result": result})

# 检查文章收藏状态
@router.get("/blog/articles/bookmarkstatus/{article_id}", response_model=ApiResponse[dict])
async def check_bookmark_article(article_id: int, user_id: int = Depends(get_optional_user_id), db: AsyncSession = Depends(get_db)):
    is_bookmarked = await crudArticles.check_bookmark(article_id=article_id, user_id=user_id, db=db)
    if is_bookmarked is None:
        raise HTTPException(status_code=404, detail="Check bookmark status failed")
    return success('success', data={'is_bookmarked': is_bookmarked})


# 批量获取文章收藏状态
@router.get("/blog/articles/batch/bookmarkstatus", response_model=ApiResponse[dict])
async def batch_check_bookmarks(article_ids: str, user_id: int = Depends(get_optional_user_id), db: AsyncSession = Depends(get_db)):
    article_ids = [int(id) for id in article_ids.split(',')]
    # 如果未登录，返回默认未收藏状态
    if user_id is None:
        default_result = {str(article_id): False for article_id in article_ids}
        return success('success', data={'result': default_result})

    is_bookmarked = await crudArticles.batch_check_bookmarks(article_ids=article_ids, user_id=user_id, db=db)
    if is_bookmarked is None:
        raise HTTPException(status_code=404, detail="Check bookmark status failed")
    return success('success', data={'result': is_bookmarked})


# 获取用户收藏文章列表
@router.get("/blog/articles/user/bookmarks", response_model=ApiResponse[dict])
async def get_user_bookmarks(
    currentpage: int = 1,
    pagesize: int = 10,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取当前登录用户的收藏文章列表"""
    skip = (currentpage - 1) * pagesize
    result = await crudArticles.get_user_bookmarked_articles(db, user_id=user_id, skip=skip, limit=pagesize)
    if result is None:
        return success('success', data={'list': [], 'total': 0, 'page': currentpage, 'pageSize': pagesize})

    # 获取总数
    total = await crudArticles.get_user_bookmarks_count(db, user_id=user_id)

    return success(data={
        'list': result,
        'total': total,
        'page': currentpage,
        'pageSize': pagesize
    })


# 点赞文章
@router.post("/blog/articles/like/{article_id}", response_model=ApiResponse[dict])
async def like_article(article_id: int, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await crudArticles.add_like(article_id=article_id, user_id=user_id, db=db)
    if result is None:
        raise HTTPException(status_code=404, detail="Like failed")
    return success('success', data={"result": result})


# 取消点赞文章
@router.post("/blog/articles/unlike/{article_id}", response_model=ApiResponse[dict])
async def unlike_article(article_id: int, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await crudArticles.remove_like(article_id=article_id, user_id=user_id, db=db)
    if result is None:
        raise HTTPException(status_code=404, detail="Unlike failed")
    return success('success', data={"result": result})

# 检查文章点赞状态
@router.get("/blog/articles/likestatus/{article_id}", response_model=ApiResponse[dict])
async def check_like_article(article_id: int, user_id: int = Depends(get_optional_user_id), db: AsyncSession = Depends(get_db)):
    is_liked = await crudArticles.check_like(article_id=article_id, user_id=user_id, db=db)
    if is_liked is None:
        raise HTTPException(status_code=404, detail="Check like status failed")
    return success('success', data={'is_liked': is_liked})


###########
# 评论相关
###########

# 获取评论/回复列表
@router.get("/blog/articles/comments/list", response_model=ApiResponse[List[schemasComments.BlogCommentListItem]])
async def get_comment_list(
    article_id: int,
    type: str = 'reply',
    subject_id: int = 0,
    order: str = 'top',
    currentpage: int = 1,
    pagesize: int = 10,
    db: AsyncSession = Depends(get_db),
):
    comment_list = await crudComments.get_comment_list(
        db,
        article_id=article_id,
        type=type,
        subject_id=subject_id,
        order=order,
        page=currentpage,
        page_size=pagesize,
    )
    return success(data=comment_list)


# 创建评论/回复
@router.post("/blog/articles/comments/create", response_model=ApiResponse[schemasComments.BlogComment])
async def create_comment(
    request: Request,
    comment: schemasComments.BlogCommentCreateForm,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    comment_entity = await crudComments.add_comment(
        db,
        request=request,
        comment=comment,
        user_id=user_id,
    )
    return success(data=comment_entity)



###########
# page相关
###########

# 根据slug获取page详情
@router.get("/blog/page/{slug}", response_model=ApiResponse[schemasPages.BlogPage])
async def get_page_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    page = await crudPages.get_page_by_slug(db, slug=slug)
    if page is None:
        raise HTTPException(status_code=404, detail="Page not found")
    return success(data=page)



###########
# series相关
###########

# 获取所有系列列表（用于文章创建时选择）
@router.get("/blog/series/list", response_model=ApiResponse[List[schemasSeries.BlogSeries]])
async def get_series_list(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """获取所有系列列表，供作者和协作者在创建文章时选择"""
    serieslist = await crudSeries.get_series_list(db, skip=skip, limit=limit)
    return success(data=serieslist)


# 根据slug获取series详情
@router.get("/blog/series/{slug}", response_model=ApiResponse[schemasSeries.BlogSeries])
async def get_series_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    series = await crudSeries.get_series_by_slug(db, slug=slug)
    if series is None:
        raise HTTPException(status_code=404, detail="Series not found")
    return success(data=series)


# 获取series下文章列表
@router.get("/blog/series/{slug}/articles", response_model=ApiResponse[dict])
async def get_articles_by_series_slug(
    slug: str,
    currentpage: int = 1,
    pagesize: int = 10,
    db: AsyncSession = Depends(get_db),
):
    skip = (currentpage - 1) * pagesize
    limit = pagesize
    articles = await crudSeries.get_articles_by_series_slug(db, slug=slug, skip=skip, limit=limit)
    total = await crudSeries.get_article_count_by_series_slug(db, slug=slug)
    return success(data={
        "list": articles,
        "total": total,
        "page": currentpage,
        "pageSize": pagesize
    })



###########
# category相关
###########

# 获取所有分类列表（用于文章创建时选择）
@router.get("/blog/category/list", response_model=ApiResponse[List[schemasCategory.BlogCategory]])
async def get_category_list(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """获取所有分类列表，供作者和协作者在创建文章时选择"""
    categorylist = await crudCategory.get_category_list(db, skip=skip, limit=limit)
    return success(data=categorylist)


# 获取category详情
@router.get("/blog/category/{slug}", response_model=ApiResponse[schemasCategory.BlogCategory])
async def get_category_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    category = await crudCategory.get_category_by_slug(db, slug=slug)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return success(data=category)


# 获取category下文章列表
@router.get("/blog/category/{slug}/articles", response_model=ApiResponse[dict])
async def get_articles_by_category_slug(
    slug: str,
    currentpage: int = 1,
    pagesize: int = 10,
    db: AsyncSession = Depends(get_db),
):
    skip = (currentpage - 1) * pagesize
    limit = pagesize
    articles = await crudCategory.get_category_articles(db, slug=slug, skip=skip, limit=limit)
    if articles is None:
        raise HTTPException(status_code=404, detail="Category not found")
    total = await crudCategory.get_category_articles_count(db, category_slug=slug)
    return success(data={
        "list": articles,
        "total": total,
        "page": currentpage,
        "pageSize": pagesize
    })


###########
# 阅读历史相关 (注意: 必须在 /user/{username} 之前定义)
###########

# 获取用户阅读历史列表 (去重后返回)
@router.get("/blog/articles/user/history", response_model=ApiResponse[dict])
async def get_user_reading_history(
    currentpage: int = 1,
    pagesize: int = 20,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取当前登录用户的阅读历史，同一篇文章只返回最新一次浏览记录"""
    skip = (currentpage - 1) * pagesize
    result = await crudArticleViews.get_user_reading_history(db, user_id=user_id, skip=skip, limit=pagesize)
    total = await crudArticleViews.get_user_reading_history_count(db, user_id=user_id)

    return success(data={
        'list': result,
        'total': total,
        'page': currentpage,
        'pageSize': pagesize
    })


# 清空用户阅读历史
@router.delete("/blog/articles/user/history", response_model=ApiResponse[dict])
async def clear_user_reading_history(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """清空当前用户的所有阅读历史"""
    count = await crudArticleViews.clear_user_reading_history(db, user_id=user_id)
    return success(data={'deleted': count})


# 删除单条阅读历史
@router.delete("/blog/articles/user/history/{record_id}", response_model=ApiResponse[dict])
async def delete_reading_history_record(
    record_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """删除单条阅读历史记录"""
    result = await crudArticleViews.delete_view_record(db, record_id=record_id, user_id=user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Record not found")
    return success(data={'deleted': 1})


# 更新文章阅读时长
@router.post("/blog/articles/view/duration", response_model=ApiResponse[dict])
async def update_view_duration(
    article_id: int,
    view_duration: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """更新当前文章的阅读时长（秒）"""
    result = await crudArticleViews.update_view_duration(
        db=db,
        user_id=user_id,
        article_id=article_id,
        view_duration=view_duration
    )
    return success(data={'updated': result})


# 获取用户文章列表
@router.get("/blog/articles/user/{username}", response_model=ApiResponse[dict])
async def get_articles_by_username(
    username: str,
    limit: int = 10,
    status: str = None,
    db: AsyncSession = Depends(get_db)
):
    # 先获取用户信息
    user = await crudUsers.get_user(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 获取用户文章，支持状态筛选
    articles = await crudArticles.get_articles_by_author(db, author_id=user.id, limit=limit, status=status)
    # 返回前端期望的格式：包含 list 字段
    return success(data={'list': articles, 'total': len(articles)})


# 获取用户文章总数
@router.get("/blog/articles/user/{username}/count", response_model=ApiResponse[dict])
async def get_user_article_count(
    username: str,
    db: AsyncSession = Depends(get_db)
):
    # 先获取用户信息
    user = await crudUsers.get_user(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 获取各状态文章数量
    published_count = await crudArticles.get_articles_count_by_author(db, author_id=user.id, status='published')
    draft_count = await crudArticles.get_articles_count_by_author(db, author_id=user.id, status='draft')

    return success(data={
        'published': published_count,
        'draft': draft_count
    })


# 获取用户文章列表（带状态筛选）
@router.get("/blog/articles/user/{username}/list", response_model=ApiResponse[List[schemasArticles.BlogArticle]])
async def get_user_articles_list(
    username: str,
    status: str = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """获取指定用户的文章列表，可选择按状态筛选"""
    # 先获取用户信息
    user = await crudUsers.get_user(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 获取用户文章
    articles = await crudArticles.get_articles_by_author(db, author_id=user.id, limit=limit)

    # 如果指定了状态，进行筛选
    if status:
        articles = [a for a in articles if a.status == status]

    return success(data=articles)


# 创建文章（供Author和Contributor使用）
@router.post("/blog/articles/create", response_model=ApiResponse[schemasArticles.BlogArticle])
async def create_article_public(
    article: schemasArticles.BlogArticleBase,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    创建文章，供Author和Contributor使用
    - Contributor只能创建草稿
    - Author可以创建草稿或发布文章
    """
    # 导入必要的模块（从internal/articles.py复制）
    import pypinyin
    import random
    import string
    from app.crud import tags as crudTags
    from app.services import notification_service

    # 获取当前用户信息以检查角色
    current_user = await crudUsers.get_user_by_id(db, user_id)
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    # 检查用户角色
    user_role = current_user.role

    # Contributor 只能创建草稿
    if user_role == 'Contributor' and article.status != 'draft':
        raise HTTPException(status_code=403, detail="Contributors can only create draft articles")

    # 处理标签
    tag_names = article.tags.split(",") if article.tags else None
    if article.co_authors == "" or article.co_authors == []:
        article.co_authors = None
    else:
        article.co_authors = ",".join(str(id) for id in article.co_authors)
    if article.series_id == "":
        article.series_id = None
    elif type(article.series_id) == str:
        article.series_id = int(article.series_id)

    # 处理pub_time：如果是毫秒级时间戳则转换为秒级
    if hasattr(article, 'pub_time') and article.pub_time and article.pub_time > 10**12:
        article.pub_time = article.pub_time // 1000

    # 生成slug
    if (article.slug == "" or article.slug == None):
        # 检查标题是否包含中文字符
        if any('一' <= char <= '鿿' for char in article.title):
            # 包含中文，使用 pypinyin 转换
            article.slug = "_".join(pypinyin.lazy_pinyin(article.title)).lower()
        else:
            # 纯英文标题：空格替换为下划线，逗号替换为短横线
            article.slug = article.title.replace(" ", "_").replace(",", "-")
        # 移除所有非字母、数字、下划线、短横线的字符
        article.slug = re.sub(r"[^a-zA-Z0-9_-]", "", article.slug)

    # 文章slug具有唯一性，查询是否存在相同slug的文章
    if await crudArticles.check_article_slug_unique(db, slug=article.slug):
        article.slug += "_" + "".join(random.sample(string.ascii_lowercase + string.digits, 6))

    # 处理标签ID
    tag_ids = []
    if tag_names:
        for tag_name in tag_names:
            tag = await crudTags.get_tag_by_name(db, tag_name)
            if not tag:
                # 使用pypinyin自动处理中文字符
                tag_slug = "_".join(pypinyin.lazy_pinyin(tag_name))
                tag_slug = tag_slug.replace(" ", "_").lower()
                tag_slug = tag_slug.replace("/", "_")
                tag_slug = re.sub(r"[^a-zA-Z0-9_-]", "", tag_slug)
                tag_data = schemasTags.BlogTagCreate(
                    name=tag_name,
                    tag_desc=tag_name,
                    slug=tag_slug,
                    type="user",
                    image=None,
                    status="normal"
                )
                tag = await crudTags.create_tag(db, tag_data)
                tag_ids.append(str(tag.id))
            else:
                tag_ids.append(str(tag.id))
        article.tags = ','.join(tag_ids)
    else:
        article.tags = None

    add_article_data = schemasArticles.BlogArticleCreate(**article.model_dump(exclude_unset=True, exclude={'author'}), author=user_id)
    db_article = await crudArticles.create_article(db, article=add_article_data)

    # 发送@mention通知
    if current_user and article.content:
        await notification_service.NotificationService.create_mentions_notifications(
            db=db,
            content=article.content,
            actor_id=user_id,
            actor_name=current_user.full_name or current_user.username,
            actor_avatar=current_user.profile_image or '',
            article_id=db_article.id,
            article_title=db_article.title,
            article_slug=db_article.slug,
            mention_type='article',
            exclude_user_id=user_id
        )

    # 发送文章审核通知邮件（当Contributor创建草稿时）
    if user_role == 'Contributor' and db_article.status == 'draft':
        try:
            from app.services.email_service import send_article_review_notification, EmailConfig
            from app.crud.siteconfig import get_site_config
            from app.crud.member_invitations import get_active_email_settings

            # 获取站点配置
            site_config = await get_site_config(db)

            if site_config and getattr(site_config, 'enable_article_review_notification', 0) == 1:
                # 解析通知角色
                notify_roles_json = getattr(site_config, 'article_review_notification_roles', None)
                if notify_roles_json:
                    try:
                        notify_roles = json.loads(notify_roles_json)
                        if notify_roles:
                            # 获取邮件配置
                            email_settings = await get_active_email_settings(db)
                            if email_settings:
                                email_config = EmailConfig(
                                    smtp_host=email_settings.smtp_host,
                                    smtp_port=email_settings.smtp_port,
                                    smtp_user=email_settings.smtp_user,
                                    smtp_pass=email_settings.smtp_pass,
                                    from_email=email_settings.from_email,
                                    from_name=email_settings.from_name,
                                    use_tls=email_settings.use_tls,
                                    use_ssl=False
                                )

                                # 获取需要通知的用户
                                reviewers = await crudUsers.get_users_by_roles(db, notify_roles)

                                # 构建审核链接
                                base_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
                                review_url = f"{base_url}/admin/articles/edit/{db_article.id}"

                                # 获取文章摘要
                                article_summary = db_article.content or ''
                                if len(article_summary) > 200:
                                    article_summary = article_summary[:200] + '...'

                                # 提交时间
                                submit_time = datetime.fromtimestamp(db_article.createtime).strftime('%Y-%m-%d %H:%M')

                                # 发送邮件给每个审核人（失败只记日志，不泄露邮箱到 stdout）
                                for reviewer in reviewers:
                                    if reviewer.email:
                                        try:
                                            email_success, error_msg = send_article_review_notification(
                                                email_config=email_config,
                                                to_email=reviewer.email,
                                                reviewer_name=reviewer.full_name or reviewer.username,
                                                author_name=current_user.full_name or current_user.username,
                                                article_title=db_article.title,
                                                article_summary=article_summary,
                                                submit_time=submit_time,
                                                review_url=review_url,
                                                language=site_config.language or 'zh-CN'
                                            )
                                            if not email_success:
                                                api_logger.warning(f"审核通知邮件发送失败: reviewer_id={reviewer.id}, 错误: {error_msg}")
                                        except Exception:
                                            api_logger.exception(f"发送审核通知邮件异常: reviewer_id={reviewer.id}")
                    except json.JSONDecodeError as e:
                        api_logger.warning(f"审核通知角色 JSON 解析失败: {e}")
        except Exception:
            api_logger.exception("发送文章审核通知邮件失败")

    return success(data=db_article)


###########
# 后台浏览统计 (仅管理员)
###########

# 获取今日浏览统计
@router.get("/blog/stats/views/today", response_model=ApiResponse[dict])
async def get_today_view_stats(
    db: AsyncSession = Depends(get_db)
):
    """获取今日浏览统计（总浏览、独立访客、认真阅读数）"""
    stats = await crudArticleViews.get_today_stats(db)
    return success(data=stats)


# 获取总浏览统计
@router.get("/blog/stats/views/total", response_model=ApiResponse[dict])
async def get_total_view_stats(
    db: AsyncSession = Depends(get_db)
):
    """获取总浏览统计"""
    stats = await crudArticleViews.get_total_stats(db)
    return success(data=stats)


# 获取浏览趋势
@router.get("/blog/stats/views/trend", response_model=ApiResponse[dict])
async def get_view_trend(
    days: int = 7,
    db: AsyncSession = Depends(get_db)
):
    """获取浏览趋势（支持7天/30天）"""
    if days not in [7, 30, 90]:
        days = 7
    trend = await crudArticleViews.get_daily_trend(db, days=days)
    return success(data={
        'period': f'{days}days',
        'daily_stats': trend
    })


# ==================== 文章搜索 ====================

# 搜索文章
@router.get("/blog/articles/search", response_model=ApiResponse[dict])
async def search_articles(
    keyword: str = '',
    currentpage: int = 1,
    pagesize: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    全站文章搜索
    - keyword: 搜索关键词，搜索标题、副标题和内容
    - currentpage: 当前页码
    - pagesize: 每页数量
    """
    if not keyword or len(keyword.strip()) == 0:
        return success(data={
            'list': [],
            'total': 0,
            'page': currentpage,
            'pageSize': pagesize,
            'keyword': ''
        })
    
    # 确保页码和每页数量为正数
    currentPage = max(1, currentpage)
    pageSize = max(1, min(100, pagesize))  # 限制最大100条

    # 计算偏移量
    skip = (currentPage - 1) * pageSize
    
    # 执行搜索
    articles = await crudArticles.search_articles(db, keyword=keyword.strip(), skip=skip, limit=pageSize)
    total = await crudArticles.search_articles_count(db, keyword=keyword.strip())
    
    return success(data={
        'list': articles,
        'total': total,
        'page': currentPage,
        'pageSize': pageSize,
        'keyword': keyword
    })


# ==================== 文章推荐 ====================

# 获取推荐文章
@router.get("/blog/articles/{article_id}/recommend", response_model=ApiResponse[dict])
async def get_recommend_articles(
    article_id: int,
    limit: int = 3,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    获取推荐文章

    - article_id: 当前文章ID
    - limit: 返回数量，默认3，最大10
    - offset: 随机偏移量，用于"换一批"功能
    """
    # 限制返回数量
    limit = min(max(1, limit), 10)

    # 获取推荐文章
    articles = await crudArticles.get_recommend_articles(db, article_id=article_id, limit=limit, offset=offset)

    return success(data=articles)


# ==================== 数据分析 API ====================

# 获取总体统计数据
@router.get("/blog/articles/statistics", response_model=ApiResponse[dict])
async def get_overall_statistics(
    db: AsyncSession = Depends(get_db)
):
    """
    获取总体统计数据

    返回：
    - total_articles: 文章总数（已发布）
    - total_views: 总浏览量
    - total_likes: 总点赞数
    - total_comments: 总评论数
    """
    stats = await crudArticles.get_overall_statistics(db)
    return success(data=stats)


# 获取 TOP 排行文章
@router.get("/blog/articles/top", response_model=ApiResponse[List[dict]])
async def get_top_articles(
    type: str = 'views',
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    获取 TOP 排行文章

    参数：
    - type: 排序类型，views(浏览量)、likes(点赞数)、comments(评论数)
    - limit: 返回数量，默认10

    返回：
    - 文章列表，包含文章信息和统计数据
    """
    # 验证类型参数
    if type not in ['views', 'likes', 'comments']:
        type = 'views'

    # 限制返回数量
    limit = min(max(1, limit), 100)

    articles = await crudArticles.get_top_articles(db, type=type, limit=limit)
    return success(data=articles)


# 获取浏览量趋势（兼容前端调用的路径）
@router.get("/blog/articles/trend", response_model=ApiResponse[List[dict]])
async def get_view_trend_compatible(
    days: int = 7,
    db: AsyncSession = Depends(get_db)
):
    """
    获取浏览量趋势

    参数：
    - days: 天数，7、30、90

    返回：
    - 每日浏览量数据列表
    """
    if days not in [7, 30, 90]:
        days = 7

    trend = await crudArticleViews.get_daily_trend(db, days=days)

    # 转换为前端期望的格式
    formatted_trend = []
    for item in trend:
        formatted_trend.append({
            'date': item['date'],
            'views': item['views']
        })

    return success(data=formatted_trend)


# ==================== 用户活动查询 ====================

@router.get("/blog/users/{username}/activity", response_model=ApiResponse[dict])
async def get_user_activity(
    username: str,
    limit: int = 10,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户最近的活动

    参数：
    - username: 用户名
    - limit: 返回数量，默认10，最大50
    - offset: 偏移量，用于分页

    返回：
    - 按时间倒序的用户活动列表
    """
    from sqlalchemy import select, and_, union_all, literal
    import app.models.data.articles as modelsArticles
    import app.models.data.users as modelsUsers
    import app.models.data.comments as modelsComments

    # 限制返回数量
    limit = min(max(1, limit), 50)

    # 获取用户信息
    user = await crudUsers.get_user(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 获取用户隐私设置
    user_result = await db.execute(
        select(modelsUsers.User).where(modelsUsers.User.id == user.id)
    )
    user_model = user_result.scalar_one_or_none()

    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")

    activities = []

    # 1. 查询最近发布的文章（只显示已发布的文章）
    articles_query = select(
        literal('article').label('type'),
        modelsArticles.BlogArticle.id,
        modelsArticles.BlogArticle.title,
        modelsArticles.BlogArticle.slug,
        modelsArticles.BlogArticle.createtime.label('time'),
        literal(None).label('article_id'),
        literal(None).label('article_title'),
        literal(None).label('article_slug'),
        literal(None).label('comment_content')
    ).where(
        and_(
            modelsArticles.BlogArticle.author == user.id,
            modelsArticles.BlogArticle.status == 'published'  # 只显示已发布的文章
        )
    ).order_by(modelsArticles.BlogArticle.createtime.desc()).limit(limit)

    articles_result = await db.execute(articles_query)
    for row in articles_result:
        activities.append({
            'type': 'article',
            'id': row.id,
            'title': row.title,
            'slug': row.slug,
            'action': '发布了文章',
            'time': row.time
        })

    # 2. 查询最近点赞的文章（如果允许展示）
    if user_model.privacy_show_likes:
        likes_query = select(
            literal('like').label('type'),
            literal(None).label('id'),
            literal(None).label('title'),
            literal(None).label('slug'),
            modelsUsers.UserInteractionData.updatetime.label('time'),
            modelsUsers.UserInteractionData.target_id.label('article_id'),
            modelsArticles.BlogArticle.title.label('article_title'),
            modelsArticles.BlogArticle.slug.label('article_slug'),
            literal(None).label('comment_content')
        ).join(
            modelsArticles.BlogArticle,
            modelsUsers.UserInteractionData.target_id == modelsArticles.BlogArticle.id
        ).where(
            and_(
                modelsUsers.UserInteractionData.user_id == user.id,
                modelsUsers.UserInteractionData.type == 'LIKE',
                modelsUsers.UserInteractionData.status == 1,
                modelsArticles.BlogArticle.status == 'published'  # 只显示已发布的文章
            )
        ).order_by(modelsUsers.UserInteractionData.updatetime.desc()).limit(limit)

        likes_result = await db.execute(likes_query)
        for row in likes_result:
            activities.append({
                'type': 'like',
                'article_id': row.article_id,
                'article_title': row.article_title,
                'article_slug': row.article_slug,
                'action': '点赞了文章',
                'time': row.time
            })

    # 3. 查询最近收藏的文章（如果允许展示）
    if user_model.privacy_show_bookmarks:
        bookmarks_query = select(
            literal('bookmark').label('type'),
            literal(None).label('id'),
            literal(None).label('title'),
            literal(None).label('slug'),
            modelsUsers.UserInteractionData.updatetime.label('time'),
            modelsUsers.UserInteractionData.target_id.label('article_id'),
            modelsArticles.BlogArticle.title.label('article_title'),
            modelsArticles.BlogArticle.slug.label('article_slug'),
            literal(None).label('comment_content')
        ).join(
            modelsArticles.BlogArticle,
            modelsUsers.UserInteractionData.target_id == modelsArticles.BlogArticle.id
        ).where(
            and_(
                modelsUsers.UserInteractionData.user_id == user.id,
                modelsUsers.UserInteractionData.type == 'BOOKMARK',
                modelsUsers.UserInteractionData.status == 1,
                modelsArticles.BlogArticle.status == 'published'  # 只显示已发布的文章
            )
        ).order_by(modelsUsers.UserInteractionData.updatetime.desc()).limit(limit)

        bookmarks_result = await db.execute(bookmarks_query)
        for row in bookmarks_result:
            activities.append({
                'type': 'bookmark',
                'article_id': row.article_id,
                'article_title': row.article_title,
                'article_slug': row.article_slug,
                'action': '收藏了文章',
                'time': row.time
            })

    # 4. 查询最近的评论（如果允许展示）
    if user_model.privacy_show_comments:
        comments_query = select(
            literal('comment').label('type'),
            literal(None).label('id'),
            literal(None).label('title'),
            literal(None).label('slug'),
            modelsComments.BlogComments.createtime.label('time'),
            modelsComments.BlogComments.article_id.label('article_id'),
            modelsArticles.BlogArticle.title.label('article_title'),
            modelsArticles.BlogArticle.slug.label('article_slug'),
            modelsComments.BlogComments.comment.label('comment_content')
        ).join(
            modelsArticles.BlogArticle,
            modelsComments.BlogComments.article_id == modelsArticles.BlogArticle.id
        ).where(
            and_(
                modelsComments.BlogComments.user_id == user.id,
                modelsComments.BlogComments.status == 1,
                modelsArticles.BlogArticle.status == 'published'  # 只显示已发布文章的评论
            )
        ).order_by(modelsComments.BlogComments.createtime.desc()).limit(limit)

        comments_result = await db.execute(comments_query)
        for row in comments_result:
            activities.append({
                'type': 'comment',
                'article_id': row.article_id,
                'article_title': row.article_title,
                'article_slug': row.article_slug,
                'comment_content': row.comment_content[:100] if row.comment_content else '',  # 限制评论长度
                'action': '评论了文章',
                'time': row.time
            })

    # 按时间倒序排序所有活动
    activities.sort(key=lambda x: x['time'], reverse=True)

    # 应用分页
    total = len(activities)
    activities = activities[offset:offset + limit]
    has_more = offset + limit < total

    return success(data={
        'activities': activities,
        'total': total,
        'has_more': has_more
    })


# ==================== 用户隐私设置 ====================

@router.put("/blog/users/privacy", response_model=ApiResponse[dict])
async def update_user_privacy(
    privacy_data: schemasUsers.UserPrivacyUpdate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    更新用户隐私设置

    参数：
    - privacy_show_bookmarks: 是否展示收藏的文章（1=是，0=否）
    - privacy_show_likes: 是否展示点赞的文章（1=是，0=否）
    - privacy_show_comments: 是否展示评论活动（1=是，0=否）
    - privacy_show_views: 是否展示浏览记录（1=是，0=否）

    返回：
    - 更新后的隐私设置
    """
    from app.models.data.users import User
    from sqlalchemy import update, select

    # 构建更新数据
    update_values = {}
    if privacy_data.privacy_show_bookmarks is not None:
        update_values['privacy_show_bookmarks'] = privacy_data.privacy_show_bookmarks
    if privacy_data.privacy_show_likes is not None:
        update_values['privacy_show_likes'] = privacy_data.privacy_show_likes
    if privacy_data.privacy_show_comments is not None:
        update_values['privacy_show_comments'] = privacy_data.privacy_show_comments
    if privacy_data.privacy_show_views is not None:
        update_values['privacy_show_views'] = privacy_data.privacy_show_views

    if not update_values:
        return error(msg='没有需要更新的字段')

    # 执行更新
    await db.execute(
        update(User).where(User.id == user_id).values(**update_values)
    )
    await db.commit()

    # 获取更新后的用户信息
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    return success(data={
        'privacy_show_bookmarks': user.privacy_show_bookmarks,
        'privacy_show_likes': user.privacy_show_likes,
        'privacy_show_comments': user.privacy_show_comments,
        'privacy_show_views': user.privacy_show_views
    })


@router.get("/blog/comments/top-commenters", response_model=ApiResponse[List[schemasComments.TopCommenter]])
async def get_top_commenters(
    limit: int = 5,
    days: int = 7,
    db: AsyncSession = Depends(get_db)
):
    """
    获取本周（或指定天数内）活跃评论者

    参数:
        limit: 返回数量限制，默认5，最大20
        days: 统计天数，默认7天

    返回:
        活跃评论者列表，按评论数量降序排列
    """
    # 限制参数范围
    if limit <= 0:
        limit = 5
    if limit > 20:
        limit = 20
    if days <= 0:
        days = 7

    commenter_list = await crudComments.get_top_commenters(db, limit=limit, days=days)
    return success(data=commenter_list)


@router.get("/blog/users/privacy", response_model=ApiResponse[dict])
async def get_user_privacy(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户的隐私设置

    返回：
    - 用户隐私设置
    """
    from app.models.data.users import User
    from sqlalchemy import select

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return success(data={
        'privacy_show_bookmarks': user.privacy_show_bookmarks,
        'privacy_show_likes': user.privacy_show_likes,
        'privacy_show_comments': user.privacy_show_comments,
        'privacy_show_views': user.privacy_show_views
    })


@router.get("/blog/comments/top-commenters", response_model=ApiResponse[List[schemasComments.TopCommenter]])
async def get_top_commenters(
    limit: int = 5,
    days: int = 7,
    db: AsyncSession = Depends(get_db)
):
    """
    获取本周（或指定天数内）活跃评论者

    参数:
        limit: 返回数量限制，默认5，最大20
        days: 统计天数，默认7天

    返回:
        活跃评论者列表，按评论数量降序排列
    """
    # 限制参数范围
    if limit <= 0:
        limit = 5
    if limit > 20:
        limit = 20
    if days <= 0:
        days = 7

    commenter_list = await crudComments.get_top_commenters(db, limit=limit, days=days)
    return success(data=commenter_list)
