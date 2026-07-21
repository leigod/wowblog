import time
from fastapi import HTTPException, Request
import app.models.data.comments as models
import app.models.data.tags as models_tags
import app.models.data.users as models_users
import app.models.data.articles as models_articles
import app.models.schemas.comments as schemas
from sqlalchemy import and_, select, update, insert, func, or_, cast, Date
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Literal
import datetime
from app.utils.location import get_ip_location
from app.services.notification_service import NotificationService


# 获取评论/回复列表
async def get_comment_list(
    db: AsyncSession,
    article_id: int | None = None,
    doc_id: int | None = None,
    type: str = 'reply',
    subject_id: int = 0,
    order: str = 'top',
    page: int = 1,
    page_size: int = 10,
) -> List[schemas.BlogCommentListItem]:
    # 分页参数
    offset = (page - 1) * page_size

    # 构建查询条件
    conditions = [
        models.BlogComments.type == type,
        models.BlogComments.subject_id == subject_id,
        models.BlogComments.status == 1,
    ]

    # 根据article_id或doc_id查询
    if article_id is not None:
        conditions.append(models.BlogComments.article_id == article_id)
    elif doc_id is not None:
        conditions.append(models.BlogComments.doc_id == doc_id)
    else:
        raise ValueError("必须提供 article_id 或 doc_id")

    # 查询评论列表
    stmt = select(
        models.BlogComments,
        models_users.User.username,
        models_users.User.full_name,
        models_users.User.profile_image,
    ).join(
        models_users.User,
        models.BlogComments.user_id == models_users.User.id,
    ).where(
        and_(*conditions)
    )
    if order == 'top':
        stmt.order_by(
            models.BlogComments.replys.desc(),
            models.BlogComments.likes.desc(),
            models.BlogComments.createtime.desc(),
        )
    else:
        stmt.order_by(
            models.BlogComments.createtime.desc(),
        )
    stmt.offset(
        offset
    ).limit(
        page_size
    )
    # 执行查询
    result = await db.execute(stmt)
    # 映射结果到模型
    comments = result.fetchall()
    # 转换为列表
    comment_list = []
    for row in comments:
        comment = row[0]  # BlogComment 实体
        # 将IP转换为所在地location
        location = get_ip_location(comment.ip) if comment.ip else "未知"
        # 处理可能为 None 的 full_name，提供默认值
        full_name = row.full_name if row.full_name else "匿名用户"
        profile_image = row.profile_image if row.profile_image else None
        comment_list.append(schemas.BlogCommentListItem(
            id=comment.id,
            user_id=comment.user_id,
            article_id=comment.article_id,
            doc_id=comment.doc_id,
            comment=comment.comment,
            ip=comment.ip,
            type=comment.type,
            subject_id=comment.subject_id,
            pid=comment.pid,
            likes=comment.likes,
            unlikes=comment.unlikes,
            replys=comment.replys,
            createtime=comment.createtime,
            username=row.username,
            full_name=full_name,
            profile_image=profile_image,
            location=location,
        ))

    return comment_list


# 添加评论/回复
async def add_comment(
    db: AsyncSession,
    request: Request,
    comment: schemas.BlogCommentCreateForm,
    user_id: int,
) -> models.BlogComments:
    # 创建评论实体
    # 确保article_id和doc_id都不为null（数据库约束），使用0表示无关联
    article_id = comment.article_id if comment.article_id is not None else 0
    doc_id = comment.doc_id if comment.doc_id is not None else 0

    comment_entity = models.BlogComments(
        user_id=user_id,
        article_id=article_id,
        doc_id=doc_id,
        comment=comment.comment,
        ip=request.client.host,
        type=comment.type,
        subject_id=comment.subject_id,
        pid=comment.pid if comment.type == 'reply' else 0,
    )
    # 添加到数据库
    db.add(comment_entity)

    # 获取当前用户信息
    current_user = await db.execute(select(models_users.User).where(models_users.User.id == user_id))
    current_user = current_user.scalar_one_or_none()

    # 处理文章评论的通知
    if comment.article_id is not None and comment.article_id > 0:
        # 获取文章信息
        article_stmt = select(models_articles.BlogArticle).where(
            models_articles.BlogArticle.id == comment.article_id
        )
        article_result = await db.execute(article_stmt)
        article = article_result.scalar_one_or_none()

        if article and current_user:
            # 如果是回复评论
            if comment.type == 'reply' and comment.subject_id > 0:
                # 获取被回复的评论
                parent_comment_stmt = select(models.BlogComments).where(
                    models.BlogComments.id == comment.subject_id
                )
                parent_comment_result = await db.execute(parent_comment_stmt)
                parent_comment = parent_comment_result.scalar_one_or_none()

                # 给被回复的用户发送通知（排除自己）
                if parent_comment and parent_comment.user_id != user_id:
                    await NotificationService.create_reply_notification(
                        db,
                        recipient_user_id=parent_comment.user_id,
                        actor_id=user_id,
                        actor_name=current_user.full_name or current_user.username,
                        actor_avatar=current_user.profile_image,
                        article_id=article.id,
                        article_title=article.title,
                        article_slug=article.slug,
                        reply_content=comment.comment
                    )
            else:
                # 给文章作者发送评论通知（排除自己）
                if article.author != user_id:
                    await NotificationService.create_comment_notification(
                        db,
                        recipient_user_id=article.author,
                        actor_id=user_id,
                        actor_name=current_user.full_name or current_user.username,
                        actor_avatar=current_user.profile_image,
                        article_id=article.id,
                        article_title=article.title,
                        article_slug=article.slug,
                        comment_content=comment.comment
                    )

            # 解析评论中的@mention
            await NotificationService.create_mentions_notifications(
                db,
                content=comment.comment,
                actor_id=user_id,
                actor_name=current_user.full_name or current_user.username,
                actor_avatar=current_user.profile_image,
                article_id=article.id,
                article_title=article.title,
                article_slug=article.slug,
                mention_type='comment',
                exclude_user_id=user_id
            )

    if comment.type == 'reply':
        # 增加回复数
        stmt = update(models.BlogComments).where(
            models.BlogComments.id == comment.subject_id
        ).values(
            replys=models.BlogComments.replys + 1
        )
        await db.execute(stmt)

    # 根据评论类型增加评论数
    if comment.article_id is not None and comment.article_id > 0:
        # 文章评论：增加文章评论数
        stmt = update(models_articles.BlogArticleStatData).where(
            models_articles.BlogArticleStatData.article_id == comment.article_id
        ).values(
            comments=models_articles.BlogArticleStatData.comments + 1
        )
        await db.execute(stmt)
    elif comment.doc_id is not None and comment.doc_id > 0:
        # 文档评论：增加文档评论数
        import app.models.data.docs as models_docs
        stmt = update(models_docs.Doc).where(
            models_docs.Doc.id == comment.doc_id
        ).values(
            comment_count=models_docs.Doc.comment_count + 1
        )
        await db.execute(stmt)

    await db.commit()
    await db.refresh(comment_entity)
    return comment_entity


# 获取本周活跃评论者
async def get_top_commenters(
    db: AsyncSession,
    limit: int = 5,
    days: int = 7
) -> List[schemas.TopCommenter]:
    """
    获取指定天数内活跃的评论者

    参数:
        db: 数据库会话
        limit: 返回数量限制
        days: 统计天数，默认7天

    返回:
        评论者列表，包含用户信息和评论数量
    """
    from sqlalchemy import func

    # 计算时间范围（当前时间戳 - days * 24 * 60 * 60）
    current_time = int(time.time())
    start_time = current_time - (days * 24 * 60 * 60)

    # 构建查询：统计指定时间范围内每个用户的评论数量
    stmt = select(
        models_users.User.id,
        models_users.User.username,
        models_users.User.full_name,
        models_users.User.profile_image,
        func.count(models.BlogComments.id).label('comment_count')
    ).join(
        models.BlogComments,
        models.BlogComments.user_id == models_users.User.id
    ).where(
        and_(
            models.BlogComments.createtime >= start_time,
            models.BlogComments.createtime <= current_time,
            models.BlogComments.status == 1,  # 只统计状态正常的评论
            # 只统计文章评论（article_id > 0）
            models.BlogComments.article_id > 0
        )
    ).group_by(
        models_users.User.id,
        models_users.User.username,
        models_users.User.full_name,
        models_users.User.profile_image
    ).order_by(
        func.count(models.BlogComments.id).desc()
    ).limit(limit)

    result = await db.execute(stmt)
    commenter_rows = result.fetchall()

    # 转换为 TopCommenter 列表
    commenters = []
    for row in commenter_rows:
        commenters.append(schemas.TopCommenter(
            id=row.id,
            username=row.username,
            full_name=row.full_name,
            avatar=row.profile_image,
            comment_count=row.comment_count
        ))

    return commenters