import app.models.data.category as models
import app.models.data.articles as models_articles
import app.models.data.users as models_users
import app.models.schemas.category as schemas
import app.models.schemas.articles as schemas_articles
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List


# 查询所有分类
async def get_category_list(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(models.BlogCategory).offset(skip).limit(limit).order_by(models.BlogCategory.sort.desc()).order_by(
            models.BlogCategory.id.desc())
    )
    return [schemas.BlogCategory.model_validate(item) for item in result.scalars().all()]


# 根据ID获取分类
async def get_category(db: AsyncSession, category_id: int):
    result = await db.execute(
        select(models.BlogCategory).where(models.BlogCategory.id == category_id)
    )
    data = result.scalar_one_or_none()
    if data:
        return data
    return None


# 添加分类
async def create_category(db: AsyncSession, category: schemas.BlogCategoryCreate):
    new_category = models.BlogCategory(**category.dict())
    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)
    return new_category


# 修改分类
async def update_category(db: AsyncSession, category_id: int, category: schemas.BlogCategoryUpdate):
    result = await db.execute(
        select(models.BlogCategory).where(models.BlogCategory.id == category_id)
    )
    category_to_update = result.scalar_one_or_none()
    if category_to_update:
        update_data = category.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(category_to_update, key, value)
        await db.commit()
        await db.refresh(category_to_update)
        return category_to_update
    return None


# 修改分类排序
async def update_category_sort(db: AsyncSession, category_id: int, pid: int, sort_values: int):
    result = await db.execute(
        select(models.BlogCategory).where(models.BlogCategory.id == category_id)
    )
    categories_to_update = result.scalar_one_or_none()
    if categories_to_update:
        await db.execute(
            update(models.BlogCategory).where(models.BlogCategory.id == category_id).values(pid=pid, sort=sort_values)
        )
        await db.commit()
        await db.refresh(categories_to_update)
        return categories_to_update
    return None


# 删除分类
async def delete_category(db: AsyncSession, category_id: int):
    result = await db.execute(
        select(models.BlogCategory).where(models.BlogCategory.id == category_id)
    )
    category_to_delete = result.scalar_one_or_none()
    if category_to_delete:
        await db.delete(category_to_delete)
        await db.commit()
        return category_to_delete
    return None



# 修改分类下文章排序
async def update_category_articles_sort(db: AsyncSession, category_id: int, category: schemas.BlogCategoryUpdateArticlesOrder):
    result = await db.execute(
        select(models.BlogCategory).where(models.BlogCategory.id == category_id)
    )
    category_to_update = result.scalar_one_or_none()
    if category_to_update:
        category_to_update.articles_order = category.articles_order
        await db.commit()
        await db.refresh(category_to_update)
        return category_to_update
    return None


# 根据slug获取分类
async def get_category_by_slug(db: AsyncSession, slug: str):
    result = await db.execute(
        select(models.BlogCategory).where(models.BlogCategory.slug == slug)
    )
    data = result.scalar_one_or_none()
    if data:
        return data
    return None


# 根据slug获取分类下文章列表
async def get_category_articles(db: AsyncSession, slug: str, skip: int = 0, limit: int = 100):
    category = await get_category_by_slug(db, slug)
    if not category:
        return None
    query = select(models_articles.BlogArticle,models_users.User.full_name, models_users.User.username, models_users.User.profile_image, models_articles.BlogArticleStatData) \
            .join(models_users.User, models_articles.BlogArticle.author == models_users.User.id) \
                .join(models_articles.BlogArticleStatData, models_articles.BlogArticle.id == models_articles.BlogArticleStatData.article_id) \
    .where(models_articles.BlogArticle.category_id == category.id) \
    .where(models_articles.BlogArticle.status == 'published') \
    .offset(skip).limit(limit)

    if category.articles_order == 'id desc':
        result = query.order_by(models_articles.BlogArticle.id.desc())
    elif category.articles_order == 'pubtime asc':
        result = query.order_by(models_articles.BlogArticle.pub_time.asc())
    elif category.articles_order == 'views desc':
        result = query.order_by(models_articles.BlogArticleStatData.views.desc())
    
    result = await db.execute(result)

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


# 获取分类下文章数
async def get_category_articles_count(db: AsyncSession, category_slug: str):
    category = await get_category_by_slug(db, category_slug)
    if not category:
        return 0
    result = await db.execute(
        select(func.count(models_articles.BlogArticle.id)).where(models_articles.BlogArticle.category_id == category.id).where(models_articles.BlogArticle.status == 'published')
    )
    count = result.scalar_one_or_none()
    if count:
        return count
    return 0
