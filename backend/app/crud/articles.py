import time
from fastapi import HTTPException
import app.models.data.articles as models
import app.models.data.tags as models_tags
import app.models.data.users as models_users
import app.models.data.category as models_category
import app.models.data.series as models_series
import app.models.schemas.articles as schemas
import app.models.schemas.tags as schemas_tags
import app.models.schemas.users as schemas_users
import app.models.schemas.category as schemas_category
from app.dependencies.authentication import get_current_user_id
from sqlalchemy import and_, select, update, insert, func, or_, cast, Date
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Literal
from datetime import datetime, timedelta


# 获取不同状态文章列表总数
async def get_articles_count_by_status(db: AsyncSession):
    query = select(models.BlogArticle.status, func.count()).select_from(models.BlogArticle).group_by(models.BlogArticle.status)
    result = await db.execute(query)
    return result.fetchall()

# 获取文章总数
async def get_articles_count(db: AsyncSession, reqdata: schemas.BlogArticleListRequest = None):
    # 进行join查询并统计文章总数，使用distinct确保计数准确
    query = select(func.count(models.BlogArticle.id.distinct())).select_from(models.BlogArticle)
    query = query.join(models_users.User, models.BlogArticle.author == models_users.User.id)
    # query = select(models.BlogArticle, models_users.User.full_name, models_users.User.username, models_users.User.profile_image)
    # query = query.join(models_users.User, models.BlogArticle.author == models_users.User.id)
    # query = query.order_by(models.BlogArticle.id.desc())
    
    # 只有当reqdata不为None时才处理过滤条件
    if reqdata:
        if reqdata.status and reqdata.status != '':
            if reqdata.status not in ['draft', 'published', 'scheduled', 'deleted']:
                raise ValueError('Invalid status')
            query = query.where(models.BlogArticle.status == reqdata.status)
        if reqdata.authors and len(reqdata.authors) > 0:
            # 如果是字符串，尝试分割成列表
            if isinstance(reqdata.authors, str):
                authors_list = [int(a.strip()) for a in reqdata.authors.split(',') if a.strip().isdigit()]
                if authors_list:
                    query = query.where(models.BlogArticle.author.in_(authors_list))
            elif hasattr(reqdata.authors, '__iter__') and not isinstance(reqdata.authors, (str, bytes)):
                # 如果是可迭代对象且不是字符串
                query = query.where(models.BlogArticle.author.in_(reqdata.authors))
        if reqdata.tags and len(reqdata.tags) > 0:
            # 构建SQL LIKE条件，匹配包含任意指定标签ID的文章
            # tags是逗号分隔的字符串，例如"2,8,12,372"
            tag_conditions = []
            # 检查tags是否为字符串，如果是则分割成列表
            tags_list = []
            if isinstance(reqdata.tags, str):
                tags_list = [t.strip() for t in reqdata.tags.split(',') if t.strip().isdigit()]
            elif hasattr(reqdata.tags, '__iter__') and not isinstance(reqdata.tags, (str, bytes)):
                # 如果是可迭代对象且不是字符串
                tags_list = [str(t) for t in reqdata.tags if str(t).isdigit()]
            for tag_id in tags_list:
                # 匹配三种情况：标签在开头、中间或结尾
                tag_conditions.append(models.BlogArticle.tags.like(f'%,{tag_id},%'))  # 中间
                tag_conditions.append(models.BlogArticle.tags.like(f'{tag_id},%'))     # 开头
                tag_conditions.append(models.BlogArticle.tags.like(f'%,{tag_id}'))     # 结尾
                tag_conditions.append(models.BlogArticle.tags == f'{tag_id}')          # 只有一个标签
            
             # 使用OR连接所有条件
            if tag_conditions:
                query = query.where(or_(*tag_conditions))
        if reqdata.time and reqdata.time.value:
            if reqdata.time.op == '>':
                query = query.where(models.BlogArticle.createtime > reqdata.time.value[0])
            elif reqdata.time.op == '=':
                query = query.where(models.BlogArticle.createtime == reqdata.time.value[0])
            elif reqdata.time.op == 'between':
                query = query.where(models.BlogArticle.createtime.between(reqdata.time.value[0], reqdata.time.value[1]))
        
        if reqdata.keyword and reqdata.keyword != '':
            query = query.where(models.BlogArticle.title.like(f'%{reqdata.keyword}%'))
    result = await db.execute(query)
    return result.scalar_one_or_none()

# 查询所有文章
async def get_articles(db: AsyncSession, skip: int = 0, limit: int = 100, reqdata: schemas.BlogArticleListRequest = None):
    # 选择文章表的所有字段和用户表的特定字段
    query = select(models.BlogArticle, models_users.User.full_name, models_users.User.username, models_users.User.profile_image)
    query = query.join(models_users.User, models.BlogArticle.author == models_users.User.id)
    query = query.offset(skip).limit(limit).order_by(models.BlogArticle.id.desc())
    
    # 只有当reqdata不为None时才处理过滤条件
    if reqdata:
        if reqdata.status and reqdata.status != '':
            if reqdata.status not in ['draft', 'published', 'scheduled', 'deleted']:
                raise ValueError('Invalid status')
            query = query.where(models.BlogArticle.status == reqdata.status)
        if reqdata.authors and len(reqdata.authors) > 0:
            # 如果是字符串，尝试分割成列表
            if isinstance(reqdata.authors, str):
                authors_list = [int(a.strip()) for a in reqdata.authors.split(',') if a.strip().isdigit()]
                if authors_list:
                    query = query.where(models.BlogArticle.author.in_(authors_list))
            elif hasattr(reqdata.authors, '__iter__') and not isinstance(reqdata.authors, (str, bytes)):
                # 如果是可迭代对象且不是字符串
                query = query.where(models.BlogArticle.author.in_(reqdata.authors))
        if reqdata.tags and len(reqdata.tags) > 0:
            # 构建SQL LIKE条件，匹配包含任意指定标签ID的文章
            # tags是逗号分隔的字符串，例如"2,8,12,372"
            tag_conditions = []
            # 检查tags是否为字符串，如果是则分割成列表
            tags_list = []
            if isinstance(reqdata.tags, str):
                tags_list = [t.strip() for t in reqdata.tags.split(',') if t.strip().isdigit()]
            elif hasattr(reqdata.tags, '__iter__') and not isinstance(reqdata.tags, (str, bytes)):
                # 如果是可迭代对象且不是字符串
                tags_list = [str(t) for t in reqdata.tags if str(t).isdigit()]
            for tag_id in tags_list:
                # 匹配三种情况：标签在开头、中间或结尾
                tag_conditions.append(models.BlogArticle.tags.like(f'%,{tag_id},%'))  # 中间
                tag_conditions.append(models.BlogArticle.tags.like(f'{tag_id},%'))     # 开头
                tag_conditions.append(models.BlogArticle.tags.like(f'%,{tag_id}'))     # 结尾
                tag_conditions.append(models.BlogArticle.tags == f'{tag_id}')          # 只有一个标签
            
            # 使用OR连接所有条件
            if tag_conditions:
                query = query.where(or_(*tag_conditions))
        if reqdata.time and reqdata.time.value:
            if reqdata.time.op == '>':
                query = query.where(models.BlogArticle.createtime > reqdata.time.value[0])
            elif reqdata.time.op == '=':
                query = query.where(models.BlogArticle.createtime == reqdata.time.value[0])
            elif reqdata.time.op == 'between':
                query = query.where(models.BlogArticle.createtime.between(reqdata.time.value[0], reqdata.time.value[1]))
        
        if reqdata.keyword and reqdata.keyword != '':
            query = query.where(models.BlogArticle.title.like(f'%{reqdata.keyword}%'))
    result = await db.execute(query)
    articles_with_user_info = []
    for row in result.all():
        article, full_name, username, profile_image = row
        # 将文章对象转换为字典
        article_dict = schemas.BlogArticle.model_validate(article).model_dump()
        # 添加用户信息
        article_dict['author_full_name'] = full_name
        article_dict['author_username'] = username
        article_dict['author_profile_image'] = profile_image
        articles_with_user_info.append(article_dict)
    
    return articles_with_user_info


# 根据ID获取文章
async def get_article(db: AsyncSession, article_id: int):
    result = await db.execute(
        select(models.BlogArticle, models_users.User.full_name, models_users.User.username, models_users.User.profile_image)
        .join(models_users.User, models.BlogArticle.author == models_users.User.id)
        .where(models.BlogArticle.id == article_id)
    )
    article_with_user = result.first()
    if not article_with_user:
        return None

    article, full_name, username, profile_image = article_with_user

    # 添加作者信息到article对象（用于前端显示）
    article.author_full_name = full_name
    article.author_username = username
    article.author_profile_image = profile_image

    # 处理标签，将标签id转换为名称
    if article.tags and article.tags != '':
        tag_ids = [int(tag_id) for tag_id in article.tags.split(',') if tag_id.strip().isdigit()]
        if tag_ids:
            # 查询标签名称
            tag_names_result = await db.execute(
                select(models_tags.BlogTag.id, models_tags.BlogTag.name).where(models_tags.BlogTag.id.in_(tag_ids))
            )
            tag_names = tag_names_result.all()

            # 创建ID到名称的映射
            tag_id_to_name = {tag_id: name for tag_id, name in tag_names}

            # 保持原始顺序，用名称替换ID
            named_tags = []
            for tag_id in tag_ids:
                if tag_id in tag_id_to_name:
                    named_tags.append(tag_id_to_name[tag_id])
                else:
                    # 如果找不到对应的标签名称，保留原始ID
                    named_tags.append(str(tag_id))

            # 更新标签字段为名称字符串
            article.tags = ','.join(named_tags)
    return article


# 根据名称获取文章
async def get_article_by_name(db: AsyncSession, article_name: str):
    result = await db.execute(
        select(models.BlogArticle).where(models.BlogArticle.name == article_name)
    )
    article = result.scalar_one_or_none()
    if article:
        return article
    return None


# 检查slug唯一性
async def check_article_slug_unique(db: AsyncSession, slug: str):
    result = await db.execute(
        select(models.BlogArticle).where(models.BlogArticle.slug == slug)
    )
    article = result.scalar_one_or_none()
    if article:
        return False
    return True

# 根据slug获取文章
async def get_article_by_slug(db: AsyncSession, article_slug: str):
    result = await db.execute(
        select(models.BlogArticle, models_users.User.full_name, models_users.User.username, models_users.User.profile_image)
        .join(models_users.User, models.BlogArticle.author == models_users.User.id)
        .where(models.BlogArticle.slug == article_slug)
    )
    # 获取结果
    article_with_user = result.first()
    if not article_with_user:
        return None
    
    article, full_name, username, profile_image = article_with_user
    
    # 处理标签信息
    tags = []
    if article.tags and article.tags != '':
        tag_ids = [int(tag_id) for tag_id in article.tags.split(',') if tag_id.strip().isdigit()]
        if tag_ids:
            # 查询完整的标签对象
            tag_result = await db.execute(
                select(models_tags.BlogTag)
                .where(models_tags.BlogTag.id.in_(tag_ids))
            )
            tags = tag_result.scalars().all()
    
    # 获取文章统计数据（可能有重复记录，只取第一条）
    stat_data_result = await db.execute(
        select(models.BlogArticleStatData)
        .where(models.BlogArticleStatData.article_id == article.id)
        .order_by(models.BlogArticleStatData.id)
    )
    stat_data_row = stat_data_result.first()
    stat_data = stat_data_row[0] if stat_data_row else None

    # 获取系列信息
    series = None
    if article.series_id:
        series_result = await db.execute(
            select(models_series.BlogSeries)
            .where(models_series.BlogSeries.id == article.series_id)
        )
        series = series_result.scalar_one_or_none()

    # 构建响应数据
    response_data = {
        "article": article,
        "username": username,
        "full_name": full_name,
        "profile_image": profile_image,
        "tags": tags,
        "stat_data": stat_data,
        "series": series,
    }

    return response_data


# 按ID获取文章用于预览（包括草稿，仅Admin/Editor可访问）
async def get_article_by_id_for_preview(db: AsyncSession, article_id: int):
    result = await db.execute(
        select(models.BlogArticle, models_users.User.full_name, models_users.User.username, models_users.User.profile_image)
        .join(models_users.User, models.BlogArticle.author == models_users.User.id)
        .where(models.BlogArticle.id == article_id)
    )
    # 获取结果
    article_with_user = result.first()
    if not article_with_user:
        return None

    article, full_name, username, profile_image = article_with_user

    # 处理标签信息
    tags = []
    if article.tags and article.tags != '':
        tag_ids = [int(tag_id) for tag_id in article.tags.split(',') if tag_id.strip().isdigit()]
        if tag_ids:
            # 查询完整的标签对象
            tag_result = await db.execute(
                select(models_tags.BlogTag)
                .where(models_tags.BlogTag.id.in_(tag_ids))
            )
            tags = tag_result.scalars().all()

    # 获取统计数据（可能有重复记录，只取第一条）
    stat_data_result = await db.execute(
        select(models.BlogArticleStatData)
        .where(models.BlogArticleStatData.article_id == article.id)
        .order_by(models.BlogArticleStatData.id)
    )
    stat_data_row = stat_data_result.first()
    stat_data = stat_data_row[0] if stat_data_row else None

    # 获取系列信息
    series = None
    if article.series_id:
        series_result = await db.execute(
            select(models_series.BlogSeries)
            .where(models_series.BlogSeries.id == article.series_id)
        )
        series = series_result.scalar_one_or_none()

    # 构建响应数据
    response_data = {
        "article": article,
        "username": username,
        "full_name": full_name,
        "profile_image": profile_image,
        "tags": tags,
        "stat_data": stat_data,
        "series": series,
    }

    return response_data


# 添加文章
async def create_article(db: AsyncSession, article: schemas.BlogArticleCreate):
    new_article = models.BlogArticle(**article.model_dump(exclude_unset=True))
    db.add(new_article)
    # 不需要立即提交，先刷新获取ID
    await db.flush()  # flush会将数据写入数据库但不提交事务，这样就能获取到ID
    
    # 使用flush后得到的ID创建统计数据
    await db.execute(
        insert(models.BlogArticleStatData)
        .values(
            article_id=new_article.id,  # flush后已经有ID了
            likes=0,
            comments=0,
            bookmarks=0,
            shares=0,
            views=0
        )
    )
    
    # 现在才一次性提交整个事务
    await db.commit()
    await db.refresh(new_article)
    return new_article


# 修改文章
async def update_article(db: AsyncSession, article_id: int, article: schemas.BlogArticleUpdate):
    result = await db.execute(
        select(models.BlogArticle).where(models.BlogArticle.id == article_id)
    )
    article_to_update = result.scalar_one_or_none()
    if article_to_update:
        update_data = article.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(article_to_update, key, value)
        await db.commit()
        await db.refresh(article_to_update)
        return article_to_update
    return None


# 修改文章状态
async def update_article_status(db: AsyncSession, article_id: int, article: schemas.BlogArticleUpdateStatus):
    result = await db.execute(
        select(models.BlogArticle).where(models.BlogArticle.id == article_id)
    )
    article_to_update = result.scalar_one_or_none()
    if article_to_update:
        update_data = article.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(article_to_update, key, value)
        await db.commit()
        await db.refresh(article_to_update)
        return article_to_update
    return None

# 修改文章运营状态
async def update_article_op_status(db: AsyncSession, article_id: int, article: schemas.BlogArticleUpdateOpStatus):
    result = await db.execute(
        select(models.BlogArticle).where(models.BlogArticle.id == article_id)
    )
    article_to_update = result.scalar_one_or_none()
    if article_to_update:
        update_data = article.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(article_to_update, key, value)
        await db.commit()
        await db.refresh(article_to_update)
        return article_to_update
    return None

# 删除文章
async def delete_article(db: AsyncSession, article_id: int):
    result = await db.execute(
        select(models.BlogArticle).where(models.BlogArticle.id == article_id)
    )
    article_to_delete = result.scalar_one_or_none()
    if article_to_delete:
        await db.delete(article_to_delete)
        await db.commit()
        return article_to_delete
    return None


# 查询文章
async def search_article(db: AsyncSession, search: str):
    result = await db.execute(
        select(models.BlogArticle).where(models.BlogArticle.title.like(f'%{search}%'))
    )
    articles = result.scalars().all()
    return [schemas.BlogArticle.model_validate(item) for item in articles]


# 获取文章标签列表
async def get_article_tag_list(db: AsyncSession, keyword: str = ''):
    search_tags = []
    if keyword and keyword != '':
        result = await db.execute(
            select(models_tags.BlogTag.id).where(models_tags.BlogTag.name.like(f'%{keyword}%'))
        )
        search_tags = result.scalars().all()
        # 如果搜索不到标签，直接返回空列表
        if not search_tags:
            return []
        # 获取所有文章的标签id
        query = select(models.BlogArticle.tags)
    else:
        # 获取最新10篇文章tag不为空的标签id
        query = select(models.BlogArticle.tags).order_by(models.BlogArticle.id.desc()).limit(10).where((models.BlogArticle.tags != '') | (models.BlogArticle.tags != None))

    result = await db.execute(query)
    tag_strings = result.scalars().all()
    
    # 合并所有标签id（处理逗号分隔的字符串格式）
    all_tag_ids = []
    for tag_string in tag_strings:
        if tag_string and isinstance(tag_string, str):
            # 分割逗号分隔的字符串并转换为整数
            try:
                # 去除可能的空格并分割
                tag_ids = [int(tag.strip()) for tag in tag_string.split(',') if tag.strip().isdigit()]
                all_tag_ids.extend(tag_ids)
            except (ValueError, TypeError):
                # 忽略无效的标签格式
                continue
    
    # 去重
    unique_tag_ids = list(set(all_tag_ids))
    
    if not unique_tag_ids:
        return []
    
    if search_tags:
        # 从unique_tag_ids中搜索符合search_tags的标签ID，即寻找两者的交集
        # 使用集合操作求交集
        unique_tag_ids = list(set(unique_tag_ids) & set(search_tags))
        
        # 如果交集为空，直接返回空列表
        if not unique_tag_ids:
            return []
    
    # 获取所有标签
    result = await db.execute(
        select(models_tags.BlogTag).where(models_tags.BlogTag.id.in_(unique_tag_ids))
    )
    tags = result.scalars().all()
    return [schemas_tags.BlogTag.model_validate(item) for item in tags]


# 获取文章作者列表
async def get_article_authors(db: AsyncSession, keyword: str = ''):
    if keyword and keyword != '':
        result = await db.execute(
            select(models_users.User.id).where(models_users.User.full_name.like(f'%{keyword}%') | (models_users.User.username.like(f'%{keyword}%'))).where(models_users.User.role.in_(['Admin', 'Editor', 'Contributor'])).where(models_users.User.status == 'normal')
        )
        authors = result.scalars().all()
        query = select(models.BlogArticle.author).where(models.BlogArticle.author.in_(authors))
    else:
        # 获取所有文章的作者id
        query = select(models.BlogArticle.author)

    result = await db.execute(query)
    author_ids = result.scalars().all()
    # 去重
    unique_author_ids = list(set(author_ids))

    # 获取所有文章的共同创作者id
    result2 = await db.execute(
        select(models.BlogArticle.co_authors)
    )
    co_author_ids = result2.scalars().all()
    # 合并所有共同创作者id（处理逗号分隔的字符串格式）
    all_co_author_ids = []
    for co_author_string in co_author_ids:
        if co_author_string and isinstance(co_author_string, str):
            # 分割逗号分隔的字符串并转换为整数
            try:
                # 去除可能的空格并分割
                co_author_ids = [int(co_author.strip()) for co_author in co_author_string.split(',') if co_author.strip().isdigit()]
                all_co_author_ids.extend(co_author_ids)
            except (ValueError, TypeError):
                # 忽略无效的标签格式
                continue
    
    # 去重
    unique_co_author_ids = list(set(all_co_author_ids))

    if keyword and keyword != '':
        # 需要在共同创作者中找寻符合关键字的作者
        # 从unique_co_author_ids中搜索符合keyword的作者ID，即寻找两者的交集
        # 使用集合操作求交集
        unique_co_author_ids = list(set(unique_co_author_ids) & set(authors))
        
        # 如果交集为空，直接返回空列表
        if not unique_co_author_ids:
            unique_co_author_ids = []
    
    # 合并所有作者id
    all_author_ids = unique_author_ids + unique_co_author_ids
    # 去重
    unique_author_ids = list(set(all_author_ids))
    if not unique_author_ids:
        return []
    
    # 获取所有作者
    result = await db.execute(
        select(models_users.User).where(models_users.User.id.in_(unique_author_ids))
    )
    authors = result.scalars().all()
    return [schemas_users.Member.model_validate(item) for item in authors]


# 获取博客文章tag
async def get_article_tags(db: AsyncSession, tag_ids: str = ''):
    # 处理标签信息
    tags = []
    if tag_ids and tag_ids != '':
        tag_ids_int = [int(tag_id) for tag_id in tag_ids.split(',') if tag_id.strip().isdigit()]
        if tag_ids_int:
            # 查询完整的标签对象
            tag_result = await db.execute(
                select(models_tags.BlogTag)
                .where(models_tags.BlogTag.id.in_(tag_ids_int))
            )
            tags = tag_result.scalars().all()
            return [schemas_tags.BlogTag.model_validate(tag) for tag in tags]
        return None
    return None


# 添加文章初始化统计数据
async def add_article_init_statistics(db: AsyncSession, article_id: int):
    # 添加文章初始化统计数据
    result = await db.execute(
        insert(models.BlogArticleStatData)
        .values(
            article_id=article_id,
            likes=0,
            comments=0,
            bookmarks=0,
            shares=0,
            views=0,
        )
    )


# 更新文章统计数据
async def update_article_statistics(db: AsyncSession, article_id: int, stat_data: schemas.ArticleStatDataUpdate):
    # 更新文章统计数据（可能有重复记录，只取第一条）
    result = await db.execute(
        select(models.BlogArticleStatData)
        .where(models.BlogArticleStatData.article_id == article_id)
        .order_by(models.BlogArticleStatData.id)
    )
    row = result.first()
    article_to_update = row[0] if row else None
    if article_to_update:
        update_data = stat_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(article_to_update, key) and isinstance(value, (int, float)):
                # 获取当前值并与新值相加
                current_value = getattr(article_to_update, key)
                new_value = current_value + value
                setattr(article_to_update, key, new_value)
        await db.commit()
        await db.refresh(article_to_update)
        return article_to_update
    return None


# 批量获取文章统计数据
async def get_articles_stat_data(article_ids: List[int], db: AsyncSession):
    stat_data = await db.execute(select(models.BlogArticleStatData).where(models.BlogArticleStatData.article_id.in_(article_ids)))
    return stat_data.scalars().all()


# 获取首页文章列表
async def get_home_article_list(reqdata: schemas.HomeArticleListRequest, db: AsyncSession, skip: int = 0, limit: int = 10):
    # 构建查询
    query = select(models.BlogArticle, models_users.User.full_name, models_users.User.username, models_users.User.profile_image) \
        .join(models_users.User, models.BlogArticle.author == models_users.User.id) \
        .where(models.BlogArticle.status == 'published') \
        .order_by(models.BlogArticle.is_pin.desc(), models.BlogArticle.createtime.desc()) \
        .offset(skip) \
        .limit(limit)
    
    if reqdata.type == 'featured':
        query = query.where(models.BlogArticle.is_featured == True)
    elif reqdata.type == 'recommend':
        query = query.where(models.BlogArticle.is_recommend == True)
    elif reqdata.type == 'following':
        if reqdata.uid:
            # 获取用户关注的作者id或共同创作者id
            author_query = select(models_users.UserInteractionData.target_id).where(models_users.UserInteractionData.user_id == reqdata.uid) \
            .join(models_users.User, models_users.UserInteractionData.target_id == models_users.User.id) \
            .where(models_users.UserInteractionData.type == 'FOLLOW_USER') \
            .where(models_users.User.role.in_(['Admin', 'Editor','Contributor']))
            author_ids = await db.execute(author_query)
            # 获取用户关注的tag ID
            tag_query = select(models_users.UserInteractionData.target_id).where(models_users.UserInteractionData.user_id == reqdata.uid) \
            .join(models_tags.BlogTag, models_users.UserInteractionData.target_id == models_tags.BlogTag.id) \
            .where(models_users.UserInteractionData.type == 'FOLLOW_TAG') \
            .where(models_tags.BlogTag.status == 'normal')
            tag_ids = await db.execute(tag_query)
            # 构建条件列表
            conditions = []
            
            # 添加作者条件
            author_ids_list = author_ids.scalars().all()
            if author_ids_list:
                conditions.append(models.BlogArticle.author.in_(author_ids_list))
                # 添加共同作者条件
                coauthor_conditions = []
                for coauthor_id in author_ids_list:
                    coauthor_conditions.append(models.BlogArticle.co_authors.like(f'%{coauthor_id}%'))  # 中间
                    coauthor_conditions.append(models.BlogArticle.co_authors.like(f'{coauthor_id}%'))   # 开头
                    coauthor_conditions.append(models.BlogArticle.co_authors.like(f'%{coauthor_id}'))   # 结尾
                    coauthor_conditions.append(models.BlogArticle.co_authors.like(f'{coauthor_id}'))    # 只有一个共同作者
                if coauthor_conditions:
                    conditions.append(or_(*coauthor_conditions))
            
            # 构建标签条件 - 使用LIKE而不是any()
            tag_ids_list = tag_ids.scalars().all()
            if tag_ids_list:
                tag_conditions = []
                for tag_id in tag_ids_list:
                    # 匹配三种情况：标签在开头、中间或结尾
                    tag_conditions.append(models.BlogArticle.tags.like(f'%,{tag_id},%'))  # 中间
                    tag_conditions.append(models.BlogArticle.tags.like(f'{tag_id},%'))     # 开头
                    tag_conditions.append(models.BlogArticle.tags.like(f'%,{tag_id}'))     # 结尾
                    tag_conditions.append(models.BlogArticle.tags == f'{tag_id}')          # 只有一个标签
                if tag_conditions:
                    conditions.append(or_(*tag_conditions))
            
            # 如果有条件，添加到查询中
            if conditions:
                query = query.where(or_(*conditions))
        else:
            # 如果用户未登录，返回空列表
            query = query.where(models.BlogArticle.author == reqdata.uid)

    # 执行查询
    result = await db.execute(query)
    articles_with_user_info = []
    for row in result.all():
        article, full_name, username, profile_image = row
        # 将文章对象转换为字典
        article_dict = schemas.BlogArticle.model_validate(article).model_dump()
        # 添加用户信息
        article_dict['author_full_name'] = full_name
        article_dict['author_username'] = username
        article_dict['author_profile_image'] = profile_image
        articles_with_user_info.append(article_dict)
    
    return articles_with_user_info


# 获取首页文章列表文章总数
async def get_home_article_count(db: AsyncSession, reqdata: schemas.HomeArticleListRequest):
    query = select(func.count(models.BlogArticle.id)) \
        .join(models_users.User, models.BlogArticle.author == models_users.User.id) \
        .where(models.BlogArticle.status == 'published') \
        .order_by(models.BlogArticle.is_pin.desc(), models.BlogArticle.createtime.desc())
    
    if reqdata.type == 'featured':
        query = query.where(models.BlogArticle.is_featured == True)
    elif reqdata.type == 'recommend':
        query = query.where(models.BlogArticle.is_recommend == True)
    elif reqdata.type == 'following':
        if reqdata.uid:
            # 获取用户关注的作者id或共同创作者id
            author_query = select(models_users.UserInteractionData.target_id).where(models_users.UserInteractionData.user_id == reqdata.uid) \
            .join(models_users.User, models_users.UserInteractionData.target_id == models_users.User.id) \
            .where(models_users.UserInteractionData.type == 'FOLLOW_USER') \
            .where(models_users.User.role.in_(['Admin', 'Editor','Contributor']))
            author_ids = await db.execute(author_query)
            # 获取用户关注的tag ID
            tag_query = select(models_users.UserInteractionData.target_id).where(models_users.UserInteractionData.user_id == reqdata.uid) \
            .join(models_tags.BlogTag, models_users.UserInteractionData.target_id == models_tags.BlogTag.id) \
            .where(models_users.UserInteractionData.type == 'FOLLOW_TAG') \
            .where(models_tags.BlogTag.status == 'normal')
            tag_ids = await db.execute(tag_query)
            # 构建条件列表
            conditions = []
            
            # 添加作者条件
            author_ids_list = author_ids.scalars().all()
            if author_ids_list:
                conditions.append(models.BlogArticle.author.in_(author_ids_list))
                # 添加共同作者条件
                coauthor_conditions = []
                for coauthor_id in author_ids_list:
                    coauthor_conditions.append(models.BlogArticle.co_authors.like(f'%{coauthor_id}%'))  # 中间
                    coauthor_conditions.append(models.BlogArticle.co_authors.like(f'{coauthor_id}%'))   # 开头
                    coauthor_conditions.append(models.BlogArticle.co_authors.like(f'%{coauthor_id}'))   # 结尾
                    coauthor_conditions.append(models.BlogArticle.co_authors.like(f'{coauthor_id}'))    # 只有一个共同作者
                if coauthor_conditions:
                    conditions.append(or_(*coauthor_conditions))
            
            # 构建标签条件 - 使用LIKE而不是any()
            tag_ids_list = tag_ids.scalars().all()
            if tag_ids_list:
                tag_conditions = []
                for tag_id in tag_ids_list:
                    # 匹配三种情况：标签在开头、中间或结尾
                    tag_conditions.append(models.BlogArticle.tags.like(f'%,{tag_id},%'))  # 中间
                    tag_conditions.append(models.BlogArticle.tags.like(f'{tag_id},%'))     # 开头
                    tag_conditions.append(models.BlogArticle.tags.like(f'%,{tag_id}'))     # 结尾
                    tag_conditions.append(models.BlogArticle.tags == f'{tag_id}')          # 只有一个标签
                if tag_conditions:
                    conditions.append(or_(*tag_conditions))
            
            # 如果有条件，添加到查询中
            if conditions:
                query = query.where(or_(*conditions))
        else:
            # 如果用户未登录，返回空列表
            query = query.where(models.BlogArticle.author == reqdata.uid)
    result = await db.execute(query)
    return result.scalar_one_or_none()


# 获取最近更新文章
async def get_recently_updated_articles(db: AsyncSession, limit: int = 5):
    result = await db.execute(
        select(models.BlogArticle, models_category.BlogCategory.name, models_category.BlogCategory.slug)
        .join(models_category.BlogCategory, models.BlogArticle.category_id == models_category.BlogCategory.id)
        .where(models.BlogArticle.status == 'published')
        .order_by(models.BlogArticle.createtime.desc())
        .limit(limit)
    )
    # 处理结果，构建符合 RecentArticles 模型要求的数据结构
    articles = []
    for article, category_name, category_slug in result.all():
        # 构建符合模型要求的字典
        article_data = {
            'article': article,  # BlogArticle 对象
            'category_name': category_name,  # 分类名称
            'category_slug': category_slug  # 分类 slug
        }
        articles.append(article_data)
        
    return articles


# 获取热门文章
async def get_hot_articles(db: AsyncSession, limit: int = 5, days: int = 7):
    result = await db.execute(
        select(models.BlogArticle, models_users.User.username, models_users.User.full_name, models.BlogArticleStatData.views)
        .join(models_users.User, models.BlogArticle.author == models_users.User.id)
        .join(models.BlogArticleStatData, models.BlogArticle.id == models.BlogArticleStatData.article_id)
        .where(models.BlogArticle.status == 'published')
        .where(models.BlogArticle.createtime >= datetime.now() - timedelta(days=days))
        .order_by(models.BlogArticleStatData.views.desc())
        .limit(limit)
    )
    # 处理结果，构建符合HotArticle模型要求的数据结构
    articles = []
    for article, username, full_name, views in result.all():
        # 构建符合模型要求的字典
        article_data = {
            'title': article.title,  # 文章标题
            'slug': article.slug,  # 文章 slug
            'username': username,  # 作者用户名
            'full_name': full_name,  # 作者全名
            'views': views or 0  # 文章阅读数，默认值为0
        }
        articles.append(article_data)
        
    return articles


# 按标签id获取文章列表
async def get_articles_by_tag_id(db: AsyncSession, tag_id: int, skip: int = 0, limit: int = 10, type: Literal['hot', 'new'] = 'hot'):
    # 构建查询基础
    query = (
        select(models.BlogArticle, models.BlogArticleStatData.views, models.BlogArticleStatData.likes, models_users.User.username, models_users.User.full_name, models_users.User.profile_image)
        .join(models_users.User, models.BlogArticle.author == models_users.User.id)
        .join(models.BlogArticleStatData, models.BlogArticle.id == models.BlogArticleStatData.article_id)
        .where(models.BlogArticle.status == 'published')
        .where((models.BlogArticle.tags == str(tag_id)) | 
               (models.BlogArticle.tags.startswith(f"{tag_id},") | 
               (models.BlogArticle.tags.endswith(f",{tag_id}")) | 
               (models.BlogArticle.tags.contains(f",{tag_id},"))))
    )
    
    # 根据类型添加排序条件
    if type == 'hot':
        query = query.order_by(models.BlogArticleStatData.views.desc())
    elif type == 'new':
        query = query.order_by(models.BlogArticle.createtime.desc())
    
    result = await db.execute(query.offset(skip).limit(limit))

    articles = []
    for article, views, likes, username, full_name, profile_image in result.all():
        # 构建符合模型要求的字典
        article_data = {
            'id': article.id,
            'title': article.title,  # 文章标题
            'content': article.content,  # 文章内容
            'cover': article.cover,  # 文章封面
            'slug': article.slug,  # 文章 slug
            'is_recommend': article.is_recommend,  # 是否推荐
            'is_pin': article.is_pin,  # 是否置顶
            'tags': article.tags,  # 文章标签
            'pub_time': article.pub_time,  # 发布时间
            'createtime': article.createtime,  # 创建时间
            'username': username,  # 作者用户名
            'full_name': full_name,  # 作者全名
            'profile_image': profile_image,  # 作者头像
            'views': views or 0,  # 文章阅读数，默认值为0
            'likes': likes or 0,  # 文章点赞数，默认值为0
        }
        articles.append(article_data)
        
    return articles


# 查询标签下的文章总数
async def get_articles_count_by_tag_id(db: AsyncSession, tag_id: int, type: Literal['all','hot', 'new'] = 'hot'):
    result = await db.execute(
        select(func.count(models.BlogArticle.id))
        .join(models_users.User, models.BlogArticle.author == models_users.User.id)
        .join(models.BlogArticleStatData, models.BlogArticle.id == models.BlogArticleStatData.article_id)
        .where(models.BlogArticle.status == 'published')
        .where((models.BlogArticle.tags == str(tag_id)) | 
               (models.BlogArticle.tags.startswith(f"{tag_id},") | 
               (models.BlogArticle.tags.endswith(f",{tag_id}")) | 
               (models.BlogArticle.tags.contains(f",{tag_id},"))))
    )
    return result.scalar_one()


# 用于验证文章是否存在的专用函数
async def validate_article_exists(db: AsyncSession, article_id: int) -> bool:
    result = await db.execute(
        select(models.BlogArticle.id).where(models.BlogArticle.id == article_id)
    )
    return result.scalar_one_or_none() is not None

# 收藏文章
async def add_bookmark(article_id: int, user_id: int, db: AsyncSession):
    # 验证文章是否存在
    article = await validate_article_exists(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    # 查询是否已经存在这条交互数据，如已存在，若状态为已关注，则更新updatetime，若为未关注则更新状态为已关注，并更新updatetime
    # 若不存在，则添加
    user_action = await db.execute(
        select(models_users.UserInteractionData).where(
            and_(
                models_users.UserInteractionData.target_id == article_id,
                models_users.UserInteractionData.user_id == user_id,
                models_users.UserInteractionData.type == "BOOKMARK"
            )
        )
    )
    user_action = user_action.scalars().first()

    is_new_bookmark = user_action is None  # 判断是否是新收藏

    if user_action:
        # 已存在数据，无论状态是否已关注都更新为已关注
        await db.execute(
            update(models_users.UserInteractionData).where(
                models_users.UserInteractionData.id == user_action.id
            ).values(
                status=1,
                updatetime=int(time.time())
            )
        )
    else:
        # 添加用户交互行为
        user_interaction = models_users.UserInteractionData(
            user_id=user_id,
            target_id=article_id,
            type="BOOKMARK"
        )
        db.add(user_interaction)
        await db.flush()

    # 更新文章收藏数
    await db.execute(
        update(models.BlogArticleStatData)
        .where(models.BlogArticleStatData.article_id == article_id)
        .values(bookmarks=func.coalesce(models.BlogArticleStatData.bookmarks, 0) + 1)
    )

    await db.commit()

    # 如果是新收藏且不是作者自己，发送通知
    if is_new_bookmark and article.author != user_id:
        from app.services.notification_service import NotificationService
        from app.crud.users import get_user_by_id

        bookmark_user = await get_user_by_id(db, user_id)
        if bookmark_user:
            await NotificationService.create_bookmark_notification(
                db,
                recipient_user_id=article.author_id,
                actor_id=user_id,
                actor_name=bookmark_user.full_name or bookmark_user.username,
                actor_avatar=bookmark_user.profile_image,
                article_id=article.id,
                article_title=article.title,
                article_slug=article.slug
            )

    return True


# 取消收藏文章
async def remove_bookmark(article_id: int, user_id: int, db: AsyncSession):
    # 验证文章是否存在
    article = await validate_article_exists(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    # 更新用户交互行为
    query = (
        update(models_users.UserInteractionData)
        .where(
            and_(
                models_users.UserInteractionData.user_id == user_id,
                models_users.UserInteractionData.target_id == article_id,
                models_users.UserInteractionData.type == "BOOKMARK"
            )
        )
        .values(
            status=0,
            updatetime=int(time.time()),
        )
    )
    await db.execute(query)
    await db.execute(
        update(models.BlogArticleStatData)
        .where(models.BlogArticleStatData.article_id == article_id)
        .values(bookmarks=func.coalesce(models.BlogArticleStatData.bookmarks, 0) - 1)
    )
    await db.commit()
    return True


# 查询文章收藏状态
async def check_bookmark(article_id: int, user_id: int, db: AsyncSession):
    # 验证文章是否存在
    article = await get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    # 查询用户是否收藏了该文章
    query = (
        select(models_users.UserInteractionData)
        .where(
            and_(
                models_users.UserInteractionData.user_id == user_id,
                models_users.UserInteractionData.target_id == article_id,
                models_users.UserInteractionData.type == "BOOKMARK"
            )
        )
    )
    result = await db.execute(query)
    result = result.scalars().first()
    if result:
        if result.status == 1:
            return True
        return False
    return False


# 批量查询文章收藏状态
async def batch_check_bookmarks(article_ids: List[int], user_id: int, db: AsyncSession):
    # 查询用户是否收藏了这些文章
    query = (
        select(models_users.UserInteractionData)
        .where(
            and_(
                models_users.UserInteractionData.user_id == user_id,
                models_users.UserInteractionData.target_id.in_(article_ids),
                models_users.UserInteractionData.type == "BOOKMARK"
            )
        )
    )
    result = await db.execute(query)
    interactions = result.scalars().all()
    
    # 创建一个字典，用于存储文章ID和对应的收藏状态
    bookmark_status = {}
    
    # 初始化所有文章ID的收藏状态为False
    for article_id in article_ids:
        bookmark_status[str(article_id)] = False
    
    # 更新实际被收藏的文章状态
    for interaction in interactions:
        if interaction.status == 1:  # 状态为1表示已收藏
            bookmark_status[str(interaction.target_id)] = True
    
    return bookmark_status


# 点赞文章
async def add_like(article_id: int, user_id: int, db: AsyncSession):
    # 验证文章是否存在
    article = await validate_article_exists(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    # 查询是否已经存在这条交互数据，如已存在，若状态为已关注，则更新updatetime，若为未关注则更新状态为已关注，并更新updatetime
    # 若不存在，则添加
    user_action = await db.execute(
        select(models_users.UserInteractionData).where(
            and_(
                models_users.UserInteractionData.target_id == article_id,
                models_users.UserInteractionData.user_id == user_id,
                models_users.UserInteractionData.type == "LIKE"
            )
        )
    )
    user_action = user_action.scalars().first()

    is_new_like = user_action is None  # 判断是否是新点赞

    if user_action:
        # 已存在数据，无论状态是否已关注都更新为已关注
        await db.execute(
            update(models_users.UserInteractionData).where(
                models_users.UserInteractionData.id == user_action.id
            ).values(
                status=1,
                updatetime=int(time.time())
            )
        )
    else:
        # 添加用户交互行为
        user_interaction = models_users.UserInteractionData(
            user_id=user_id,
            target_id=article_id,
            type="LIKE"
        )
        db.add(user_interaction)
        await db.flush()

    # 更新文章点赞数
    await db.execute(
        update(models.BlogArticleStatData)
        .where(models.BlogArticleStatData.article_id == article_id)
        .values(likes=func.coalesce(models.BlogArticleStatData.likes, 0) + 1)
    )

    await db.commit()

    # 如果是新点赞且不是作者自己，发送通知
    if is_new_like and article.author != user_id:
        from app.services.notification_service import NotificationService
        from app.crud.users import get_user_by_id

        like_user = await get_user_by_id(db, user_id)
        if like_user:
            await NotificationService.create_like_notification(
                db,
                recipient_user_id=article.author_id,
                actor_id=user_id,
                actor_name=like_user.full_name or like_user.username,
                actor_avatar=like_user.profile_image,
                article_id=article.id,
                article_title=article.title,
                article_slug=article.slug
            )

    return True

# 取消点赞文章
async def remove_like(article_id: int, user_id: int, db: AsyncSession):
    # 验证文章是否存在
    article = await validate_article_exists(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    # 更新用户交互行为
    query = (
        update(models_users.UserInteractionData)
        .where(
            and_(
                models_users.UserInteractionData.user_id == user_id,
                models_users.UserInteractionData.target_id == article_id,
                models_users.UserInteractionData.type == "LIKE"
            )
        )
        .values(
            status=0,
            updatetime=int(time.time()),
        )
    )
    await db.execute(query)
    await db.execute(
        update(models.BlogArticleStatData)
        .where(models.BlogArticleStatData.article_id == article_id)
        .values(likes=func.coalesce(models.BlogArticleStatData.likes, 0) - 1)
    )
    await db.commit()
    return True


# 查询文章点赞状态
async def check_like(article_id: int, user_id: int, db: AsyncSession):
    # 验证文章是否存在
    article = await get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    # 查询用户是否点赞了该文章
    query = (
        select(models_users.UserInteractionData)
        .where(
            and_(
                models_users.UserInteractionData.user_id == user_id,
                models_users.UserInteractionData.target_id == article_id,
                models_users.UserInteractionData.type == "LIKE"
            )
        )
    )
    result = await db.execute(query)
    result = result.scalars().first()
    if result:
        if result.status == 1:
            return True
        return False
    return False


# 根据作者ID获取文章列表
async def get_articles_by_author(db: AsyncSession, author_id: int, limit: int = 10, skip: int = 0, status: str = None):
    # 联表查询文章和统计数据
    query = (
        select(
            models.BlogArticle.id,
            models.BlogArticle.title,
            models.BlogArticle.slug,
            models.BlogArticle.subtitle,
            models.BlogArticle.cover,
            models.BlogArticle.pub_time,
            models.BlogArticle.createtime,
            models.BlogArticle.status,
            models.BlogArticleStatData.views.label('reads')
        )
        .join(models.BlogArticleStatData, models.BlogArticle.id == models.BlogArticleStatData.article_id, isouter=True)
        .where(models.BlogArticle.author == author_id)
        .order_by(models.BlogArticle.createtime.desc())
        .offset(skip)
        .limit(limit)
    )

    # 如果指定了状态，添加状态过滤条件
    if status:
        query = query.where(models.BlogArticle.status == status)

    result = await db.execute(query)
    rows = result.all()

    # 转换为字典列表
    articles = []
    for row in rows:
        articles.append({
            'id': row.id,
            'title': row.title,
            'slug': row.slug,
            'subtitle': row.subtitle,
            'cover': row.cover,
            'pub_time': row.pub_time,
            'createtime': row.createtime,
            'status': row.status,
            'reads': row.reads or 0
        })
    return articles


# 根据作者ID获取文章总数
async def get_articles_count_by_author(db: AsyncSession, author_id: int, status: str = 'published'):
    query = (
        select(func.count())
        .select_from(models.BlogArticle)
        .where(models.BlogArticle.author == author_id)
        .where(models.BlogArticle.status == status)
    )
    result = await db.execute(query)
    return result.scalar() or 0


# 获取用户收藏的文章列表
async def get_user_bookmarked_articles(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 10):
    # 联表查询：用户交互数据 -> 文章 -> 用户 -> 文章统计
    query = (
        select(
            models.BlogArticle.id,
            models.BlogArticle.title,
            models.BlogArticle.slug,
            models.BlogArticle.subtitle,
            models.BlogArticle.cover,
            models.BlogArticle.content,
            models.BlogArticle.tags,
            models.BlogArticle.pub_time,
            models.BlogArticle.createtime,
            models_users.User.full_name.label('author_full_name'),
            models_users.User.username.label('author_username'),
            models_users.User.profile_image.label('author_profile_image'),
            models.BlogArticleStatData.views.label('reads'),
            models.BlogArticleStatData.likes.label('likes')
        )
        .join(models_users.UserInteractionData, models_users.UserInteractionData.target_id == models.BlogArticle.id)
        .join(models_users.User, models_users.User.id == models.BlogArticle.author)
        .outerjoin(models.BlogArticleStatData, models.BlogArticleStatData.article_id == models.BlogArticle.id)
        .where(models_users.UserInteractionData.user_id == user_id)
        .where(models_users.UserInteractionData.type == "BOOKMARK")
        .where(models_users.UserInteractionData.status == 1)
        .where(models.BlogArticle.status == 'published')
        .order_by(models_users.UserInteractionData.updatetime.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    rows = result.all()

    # 转换为字典列表
    articles = []
    for row in rows:
        articles.append({
            'id': row.id,
            'title': row.title,
            'slug': row.slug,
            'subtitle': row.subtitle,
            'cover': row.cover,
            'content': row.content,
            'tags': row.tags,
            'pub_time': row.pub_time,
            'createtime': row.createtime,
            'author_full_name': row.author_full_name,
            'author_username': row.author_username,
            'author_profile_image': row.author_profile_image,
            'reads': row.reads or 0,
            'likes': row.likes or 0
        })
    return articles


# 获取用户收藏的文章总数
async def get_user_bookmarks_count(db: AsyncSession, user_id: int):
    query = (
        select(func.count())
        .select_from(models_users.UserInteractionData)
        .join(models.BlogArticle, models.BlogArticle.id == models_users.UserInteractionData.target_id)
        .where(models_users.UserInteractionData.user_id == user_id)
        .where(models_users.UserInteractionData.type == "BOOKMARK")
        .where(models_users.UserInteractionData.status == 1)
        .where(models.BlogArticle.status == 'published')
    )
    result = await db.execute(query)
    return result.scalar() or 0

# ==================== 文章搜索功能 ====================

async def search_articles(
    db: AsyncSession,
    keyword: str,
    skip: int = 0,
    limit: int = 10
):
    """
    全文搜索文章，搜索标题、副标题和内容
    """
    # 构建搜索条件，在标题、副标题、内容中搜索关键词
    search_conditions = or_(
        models.BlogArticle.title.like(f'%{keyword}%'),
        models.BlogArticle.subtitle.like(f'%{keyword}%'),
        models.BlogArticle.content.like(f'%{keyword}%')
    )
    
    # 联表查询：文章 -> 用户 -> 文章统计
    query = (
        select(
            models.BlogArticle.id,
            models.BlogArticle.title,
            models.BlogArticle.slug,
            models.BlogArticle.subtitle,
            models.BlogArticle.cover,
            models.BlogArticle.content,
            models.BlogArticle.tags,
            models.BlogArticle.pub_time,
            models.BlogArticle.createtime,
            models_users.User.full_name.label('author_full_name'),
            models_users.User.username.label('author_username'),
            models_users.User.profile_image.label('author_profile_image'),
            models.BlogArticleStatData.views.label('reads'),
            models.BlogArticleStatData.likes.label('likes')
        )
        .join(models_users.User, models_users.User.id == models.BlogArticle.author)
        .outerjoin(models.BlogArticleStatData, models.BlogArticleStatData.article_id == models.BlogArticle.id)
        .where(models.BlogArticle.status == 'published')
        .where(search_conditions)
        .order_by(models.BlogArticle.pub_time.desc())
        .offset(skip)
        .limit(limit)
    )
    
    result = await db.execute(query)
    rows = result.all()

    # 转换为字典列表
    articles = []
    for row in rows:
        articles.append({
            'id': row.id,
            'title': row.title,
            'slug': row.slug,
            'subtitle': row.subtitle,
            'cover': row.cover,
            'content': row.content,
            'tags': row.tags,
            'pub_time': row.pub_time,
            'createtime': row.createtime,
            'author_full_name': row.author_full_name,
            'author_username': row.author_username,
            'author_profile_image': row.author_profile_image,
            'reads': row.reads or 0,
            'likes': row.likes or 0
        })
    return articles


async def search_articles_count(
    db: AsyncSession,
    keyword: str
):
    """
    获取搜索结果总数
    """
    # 构建搜索条件
    search_conditions = or_(
        models.BlogArticle.title.like(f'%{keyword}%'),
        models.BlogArticle.subtitle.like(f'%{keyword}%'),
        models.BlogArticle.content.like(f'%{keyword}%')
    )
    
    query = (
        select(func.count(models.BlogArticle.id))
        .select_from(models.BlogArticle)
        .where(models.BlogArticle.status == 'published')
        .where(search_conditions)
    )
    
    result = await db.execute(query)
    return result.scalar() or 0


# ==================== 文章推荐功能 ====================

import math
import re
import random
from datetime import datetime, timezone, timedelta


async def get_recommend_articles(
    db: AsyncSession,
    article_id: int,
    limit: int = 3,
    offset: int = 0
):
    """
    获取推荐文章

    Args:
        db: 数据库会话
        article_id: 当前文章ID
        limit: 返回数量，默认3
        offset: 偏移量，用于换一批功能

    Returns:
        推荐文章列表
    """
    limit = min(max(1, limit), 10)  # 限制在1-10之间

    # 获取当前文章信息
    current_article = await get_article(db, article_id)
    if not current_article:
        return []

    # 获取当前文章的标签ID列表
    current_tag_ids = []
    if current_article.tags and current_article.tags != '':
        current_tag_ids = [int(t) for t in current_article.tags.split(',') if t.strip().isdigit()]

    # 计算180天前的时间戳（扩大候选池）
    hundred_eighty_days_ago = int((datetime.now(timezone.utc) - timedelta(days=180)).timestamp())
    seven_days_ago = int((datetime.now(timezone.utc) - timedelta(days=7)).timestamp())

    # 查询候选文章（最近180日内已发布，排除当前文章）
    query = (
        select(
            models.BlogArticle.id,
            models.BlogArticle.title,
            models.BlogArticle.slug,
            models.BlogArticle.cover,
            models.BlogArticle.content,
            models.BlogArticle.tags,
            models.BlogArticle.author,
            models.BlogArticle.pub_time,
            models.BlogArticle.createtime,
            models_users.User.full_name.label('author_full_name'),
            models_users.User.username.label('author_username'),
            models_users.User.profile_image.label('author_profile_image'),
            models.BlogArticleStatData.views.label('views'),
            models.BlogArticleStatData.likes.label('likes')
        )
        .join(models_users.User, models_users.User.id == models.BlogArticle.author)
        .outerjoin(models.BlogArticleStatData, models.BlogArticleStatData.article_id == models.BlogArticle.id)
        .where(models.BlogArticle.status == 'published')
        .where(models.BlogArticle.id != article_id)
        .where(models.BlogArticle.pub_time >= hundred_eighty_days_ago)
        .order_by(models.BlogArticle.pub_time.desc())
    )

    result = await db.execute(query)
    candidate_articles = result.all()

    if not candidate_articles:
        return []

    # 统计每个标签的使用频率（计算IDF）
    tag_freq = {}
    total_articles = len(candidate_articles)
    for row in candidate_articles:
        if row.tags:
            tag_ids = [int(t) for t in row.tags.split(',') if t.strip().isdigit()]
            for tag_id in tag_ids:
                tag_freq[tag_id] = tag_freq.get(tag_id, 0) + 1

    # 计算IDF权重
    tag_idf = {}
    for tag_id, freq in tag_freq.items():
        tag_idf[tag_id] = math.log(total_articles / (freq + 1))

    # 获取最大点击量（用于归一化）
    max_views = max((row.views or 0) for row in candidate_articles) or 1

    # 计算每篇文章的推荐得分
    scored_articles = []
    for row in candidate_articles:
        score = 0
        common_tags = set()  # 初始化 common_tags，避免未定义错误

        # 标签相关性得分
        if row.tags:
            article_tag_ids = [int(t) for t in row.tags.split(',') if t.strip().isdigit()]
            common_tags = set(current_tag_ids) & set(article_tag_ids)
            for tag_id in common_tags:
                score += tag_idf.get(tag_id, 0) * 20

        # 同作者加成
        if row.author == current_article.author:
            score += 10

        # 7日内加成
        if row.pub_time and row.pub_time >= seven_days_ago:
            score += 5

        # 点击量归一化
        views_score = ((row.views or 0) / max_views) * 10
        score += views_score

        # 确定推荐理由
        reason = "热门推荐"
        if row.author == current_article.author:
            if row.pub_time and row.pub_time >= seven_days_ago:
                reason = "同作者最新文章"
            else:
                reason = "更多来自该作者"
        elif common_tags and len(common_tags) >= 2:
            # 获取标签名称（简化处理，返回标签ID）
            reason = f"相关标签：{len(common_tags)}个共同标签"

        scored_articles.append({
            'id': row.id,
            'title': row.title,
            'slug': row.slug,
            'cover': row.cover,
            'summary': _get_summary(row.content),
            'author_name': row.author_full_name,
            'author_avatar': row.author_profile_image,
            'author_username': row.author_username,
            'pub_time': row.pub_time,
            'views': row.views or 0,
            'tags': row.tags,
            'reason': reason,
            'score': score
        })

    # 按得分排序
    scored_articles.sort(key=lambda x: x['score'], reverse=True)

    # 使用 offset 作为随机种子实现换一批功能
    # 这样同一个 offset 值总是返回相同结果，但不同 offset 返回不同结果
    random.seed(offset)

    # 将文章分成几组，每组内随机打乱顺序
    # 这样可以保持推荐的多样性，同时保证质量
    if len(scored_articles) > limit * 3:
        # 如果候选文章足够多，只对前30篇进行打乱（保持推荐质量）
        shuffle_count = min(30, len(scored_articles))
        top_pool = scored_articles[:shuffle_count]
        rest_pool = scored_articles[shuffle_count:]

        # 对高分文章组进行部分随机打乱
        random.shuffle(top_pool)
        scored_articles = top_pool + rest_pool
    else:
        # 候选文章不多时，全部随机打乱
        random.shuffle(scored_articles)

    # 取前 limit 篇
    result = scored_articles[:limit]

    return {
        "list": result,
        "total": len(result)
    }


def _get_summary(content: str, max_length: int = 100) -> str:
    """提取文章摘要"""
    if not content:
        return ''
    # 移除HTML标签
    text = re.sub(r'<[^>]+>', '', content)
    # 移除多余空白
    text = ' '.join(text.split())
    if len(text) <= max_length:
        return text
    return text[:max_length] + '...'


# ==================== 数据分析功能 ====================

async def get_overall_statistics(db: AsyncSession) -> dict:
    """
    获取总体统计数据

    Returns:
        dict: 包含文章总数、总浏览量、总点赞数、总评论数
    """
    # 获取文章总数（仅已发布）
    total_articles_query = (
        select(func.count())
        .select_from(models.BlogArticle)
        .where(models.BlogArticle.status == 'published')
    )
    total_articles_result = await db.execute(total_articles_query)
    total_articles = total_articles_result.scalar() or 0

    # 获取总浏览量、总点赞数、总评论数（从文章统计数据表聚合）
    stats_query = (
        select(
            func.sum(models.BlogArticleStatData.views),
            func.sum(models.BlogArticleStatData.likes),
            func.sum(models.BlogArticleStatData.comments)
        )
        .select_from(models.BlogArticleStatData)
        .join(models.BlogArticle, models.BlogArticle.id == models.BlogArticleStatData.article_id)
        .where(models.BlogArticle.status == 'published')
    )
    stats_result = await db.execute(stats_query)
    views, likes, comments = stats_result.one()

    return {
        'total_articles': total_articles,
        'total_views': views or 0,
        'total_likes': likes or 0,
        'total_comments': comments or 0
    }


async def get_top_articles(
    db: AsyncSession,
    type: str = 'views',
    limit: int = 10
) -> List[dict]:
    """
    获取 TOP 排行文章

    Args:
        db: 数据库会话
        type: 排序类型，views(浏览量)、likes(点赞数)、comments(评论数)
        limit: 返回数量，默认10

    Returns:
        文章列表，包含文章信息和统计数据
    """
    # 确定排序字段
    if type == 'likes':
        order_field = models.BlogArticleStatData.likes
    elif type == 'comments':
        order_field = models.BlogArticleStatData.comments
    else:  # 默认按浏览量排序
        order_field = models.BlogArticleStatData.views

    # 构建查询
    query = (
        select(
            models.BlogArticle.id,
            models.BlogArticle.title,
            models.BlogArticle.slug,
            models.BlogArticle.pub_time,
            models_users.User.full_name.label('author_full_name'),
            models_users.User.username.label('author_username'),
            models_users.User.profile_image.label('author_profile_image'),
            models.BlogArticleStatData.views.label('reads'),
            models.BlogArticleStatData.likes,
            models.BlogArticleStatData.comments
        )
        .join(models_users.User, models.BlogArticle.author == models_users.User.id)
        .outerjoin(models.BlogArticleStatData, models.BlogArticleStatData.article_id == models.BlogArticle.id)
        .where(models.BlogArticle.status == 'published')
        .order_by(order_field.desc(), models.BlogArticle.pub_time.desc())
        .limit(limit)
    )

    result = await db.execute(query)
    rows = result.all()

    # 转换为字典列表
    articles = []
    for row in rows:
        articles.append({
            'id': row.id,
            'title': row.title,
            'slug': row.slug,
            'author_full_name': row.author_full_name,
            'author_username': row.author_username,
            'author_profile_image': row.author_profile_image,
            'pub_time': row.pub_time,
            'reads': row.reads or 0,
            'likes': row.likes or 0,
            'comments': row.comments or 0
        })

    return articles
