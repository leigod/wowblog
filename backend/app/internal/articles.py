from fastapi import APIRouter, Depends, HTTPException, Request, Form, Path, Body

from app.models.response import ApiResponse
from app.database import get_db
from app.utils.response import success, error
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated, Optional

import re
import pypinyin
import random
import string

import app.models.schemas.articles as schemasArticles
import app.models.schemas.tags as schemasTags
import app.models.schemas.users as schemasUsers
import app.crud.articles as crudArticles
import app.crud.tags as crudTags
import app.crud.users as crudUsers
from app.dependencies.authentication import get_current_user_id
from app.services import notification_service


router = APIRouter()


###########
# 文章管理
###########

# 获取文章列表
@router.post('/articles/list', response_model=ApiResponse[dict])
async def get_article_list(currentpage: int = 1, pagesize: int = 10,
                           data: schemasArticles.BlogArticleListRequest = None, db: AsyncSession = Depends(get_db)):
    # 确保页码和每页数量为正数
    currentPage = max(1, currentpage)
    pageSize = max(1, pagesize)

    # 计算偏移量
    skip = (currentPage - 1) * pageSize

    articlelist = await crudArticles.get_articles(db, skip=skip, limit=pageSize, reqdata=data)
    total = await crudArticles.get_articles_count(db, reqdata=data)
    return success(data={
        "list": articlelist,
        "total": total,
        "page": currentPage,
        "pageSize": pageSize
    })


# 获取不同状态文章总数
@router.get("/articles/countbystatus", response_model=ApiResponse[dict])
async def get_articles_count_by_status(db: AsyncSession = Depends(get_db)):
    count_result = await crudArticles.get_articles_count_by_status(db)
    
    # 创建包含所有可能状态的字典，默认值为0
    count_dict = {
        "draft": 0,
        "published": 0,
        "scheduled": 0,
        "deleted": 0
    }
    
    # 更新数据库中存在的状态的计数
    for status, count in count_result:
        count_dict[status] = count
    
    return success(data=count_dict)


# 创建文章
@router.post("/articles/add", response_model=ApiResponse[schemasArticles.BlogArticle])
async def create_article(
    article: schemasArticles.BlogArticleBase,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    tag_names = article.tags.split(",") if article.tags else None
    if article.co_authors == "" or article.co_authors == []:
        article.co_authors = None
    else:
        article.co_authors = ",".join(article.co_authors)
    if article.series_id == "":
        article.series_id = None
    elif type(article.series_id) == str:
        article.series_id = int(article.series_id)
    # 处理pub_time：如果是毫秒级时间戳则转换为秒级
    if hasattr(article, 'pub_time') and article.pub_time and article.pub_time > 10**12:
        article.pub_time = article.pub_time // 1000
    if (article.slug == "" or article.slug == None):
        # 检查标题是否包含中文字符
        if any('一' <= char <= '鿿' for char in article.title):
            # 包含中文，使用 pypinyin 转换
            article.slug = "_".join(pypinyin.lazy_pinyin(article.title)).lower()
        else:
            # 纯英文标题：空格替换为下划线，逗号替换为短横线，并转换为小写
            article.slug = article.title.replace(" ", "_").replace(",", "-").lower()
        # 移除所有非字母、数字、下划线、短横线的字符
        article.slug = re.sub(r"[^a-zA-Z0-9_-]", "", article.slug)
    # 文章slug具有唯一性，查询是否存在相同slug的文章，如存在则在slug后添加短横线和6位小写字母数字随机数
    if await crudArticles.check_article_slug_unique(db, slug=article.slug):
        article.slug += "_" + "".join(random.sample(string.ascii_lowercase + string.digits, 6))

    # 使用新列表存储标签ID，避免在遍历过程中修改原列表
    tag_ids = []
    if tag_names:
        for tag_name in tag_names:
            tag = await crudTags.get_tag_by_name(db, tag_name)
            if not tag:
                # 使用pypinyin自动处理中文字符，非中文字符会原样保留
                tag_slug = "_".join(pypinyin.lazy_pinyin(tag_name))
                # 替换空格和斜杠为下划线
                tag_slug = tag_slug.replace(" ", "_").lower()
                tag_slug = tag_slug.replace("/", "_")
                # 移除所有非字母、数字、下划线、短横线的字符
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

    # 准备创建文章的数据，排除 author 字段，使用当前登录用户的 ID
    article_data = article.model_dump(exclude_unset=True)
    article_data.pop('author', None)  # 移除请求体中的 author，使用当前用户
    add_article_data = schemasArticles.BlogArticleCreate(**article_data, author=user_id)
    db_article = await crudArticles.create_article(db, article=add_article_data)

    # 获取当前用户信息（用于@mention通知）
    current_user = await crudUsers.get_user_by_id(db, user_id)
    if current_user and article.content:
        # 解析文章内容中的@mention并发送通知
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

    return success(data=db_article)


# 更新文章
@router.post("/articles/update/{article_id}", response_model=ApiResponse[schemasArticles.BlogArticle])
async def update_article(
    article_id: int,
    article: schemasArticles.BlogArticleUpdate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    old_article = await crudArticles.get_article(db, article_id=article_id)
    if old_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    tag_names = article.tags.split(",") if article.tags else None
    if article.co_authors == "" or article.co_authors == []:
        article.co_authors = None
    else:
        article.co_authors = ",".join(article.co_authors)
    if article.series_id == "":
        article.series_id = None
    elif type(article.series_id) == str:
        article.series_id = int(article.series_id)
    # 处理pub_time：如果是毫秒级时间戳则转换为秒级
    if hasattr(article, 'pub_time') and article.pub_time and article.pub_time > 10**12:
        article.pub_time = article.pub_time // 1000
    if (article.slug == "" or article.slug == None):
        # 检查标题是否包含中文字符
        if any('一' <= char <= '鿿' for char in article.title):
            # 包含中文，使用 pypinyin 转换
            article.slug = "_".join(pypinyin.lazy_pinyin(article.title)).lower()
        else:
            # 纯英文标题：空格替换为下划线，逗号替换为短横线，并转换为小写
            article.slug = article.title.replace(" ", "_").replace(",", "-").lower()
        # 移除所有非字母、数字、下划线、短横线的字符
        article.slug = re.sub(r"[^a-zA-Z0-9_-]", "", article.slug)
        if not await crudArticles.check_article_slug_unique(db, slug=article.slug):
            article.slug += "_" + "".join(random.sample(string.ascii_lowercase + string.digits, 6))
    elif old_article.slug != article.slug:
        # 文章slug具有唯一性，查询是否存在相同slug的文章，如存在则在slug后添加短横线和6位小写字母数字随机数
        if not await crudArticles.check_article_slug_unique(db, slug=article.slug):
            article.slug += "_" + "".join(random.sample(string.ascii_lowercase + string.digits, 6))

    # 使用新列表存储标签ID，避免在遍历过程中修改原列表
    tag_ids = []
    if tag_names:
        for tag_name in tag_names:
            tag = await crudTags.get_tag_by_name(db, tag_name)
            if not tag:
                # 使用pypinyin自动处理中文字符，非中文字符会原样保留
                tag_slug = "_".join(pypinyin.lazy_pinyin(tag_name))
                # 替换空格和斜杠为下划线
                tag_slug = tag_slug.replace(" ", "_").lower()
                tag_slug = tag_slug.replace("/", "_")
                # 移除所有非字母、数字、下划线、短横线的字符
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

    db_article = await crudArticles.update_article(db, article_id, article)
    if db_article:
        # 获取当前用户信息（用于@mention通知）
        current_user = await crudUsers.get_user_by_id(db, user_id)
        # 只有当内容有变化时才发送@mention通知
        if current_user and hasattr(article, 'content') and article.content and article.content != old_article.content:
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
        return success(data=db_article)
    return error(data={'error': '文章不存在或已被删除'})


# 更新文章运营状态
@router.post("/articles/update/op_status/{article_id}", response_model=ApiResponse[schemasArticles.BlogArticle])
async def update_article_op_status(article_id: int, article: schemasArticles.BlogArticleUpdateOpStatus, db: AsyncSession = Depends(get_db)):
    db_article = await crudArticles.update_article_op_status(db, article_id, article)
    if db_article:
        return success(data=db_article)
    return error(data={'error': '文章不存在或已被删除'})


# 更新文章状态
@router.post("/articles/update/status/{article_id}", response_model=ApiResponse[schemasArticles.BlogArticle])
async def update_article_status(article_id: int, status_data: schemasArticles.BlogArticleUpdateStatus, db: AsyncSession = Depends(get_db)):
    """更新文章状态（用于软删除/恢复等操作）"""
    old_article = await crudArticles.get_article(db, article_id=article_id)
    if old_article is None:
        return error(data={'error': '文章不存在或已被删除'})

    # 只更新状态字段，传递完整的 status_data 对象
    db_article = await crudArticles.update_article_status(db, article_id, status_data)
    if db_article:
        return success(data=db_article)
    return error(data={'error': '更新状态失败'})


# 获取文章详情
@router.get("/articles/detail/{article_id}", response_model=ApiResponse[schemasArticles.BlogArticle])
async def get_article_detail(article_id: int, db: AsyncSession = Depends(get_db)):
    db_article = await crudArticles.get_article(db, article_id)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return success(data=db_article)


# 获取文章作者列表
@router.get("/articles/authors/list", response_model=ApiResponse[List[schemasUsers.Member]])
async def get_article_authors(db: AsyncSession = Depends(get_db), keyword: str = ''):
    authors = await crudArticles.get_article_authors(db, keyword=keyword)
    return success(data=authors)


# 获取文章标签列表
@router.get("/articles/tags/list", response_model=ApiResponse[List[schemasTags.BlogTag]])
async def get_article_tags(db: AsyncSession = Depends(get_db), keyword: str = ''):
    tags = await crudArticles.get_article_tag_list(db, keyword=keyword)
    return success(data=tags)


# 删除文章
@router.delete("/articles/delete/{article_id}", response_model=ApiResponse[schemasArticles.BlogArticle])
async def delete_article(article_id: int, db: AsyncSession = Depends(get_db)):
    db_article = await crudArticles.delete_article(db, article_id)
    if db_article:
        return success(data=db_article)
    return error(data={'error': '文章不存在或已被删除'})


