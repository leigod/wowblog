"""
管理后台评论管理 CRUD 操作
"""
import time
from sqlalchemy import and_, select, update, insert, func, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Tuple
import app.models.data.comments as models_comments
import app.models.data.articles as models_articles
import app.models.data.users as models_users
import app.models.admin_comments as models_admin
import app.models.schemas.admin_comments as schemas


async def get_comment_list(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    status: str = 'all',
    audit_status: Optional[str] = None,
    user_id: Optional[int] = None,
    article_id: Optional[int] = None,
    keyword: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Tuple[List[schemas.CommentListItem], int]:
    """
    获取评论列表
    返回: (评论列表, 总数)
    """
    # 构建查询条件
    conditions = []

    # 状态筛选
    if status and status != 'all':
        # 注意：数据库中status=1表示正常，需要映射
        if status == 'normal':
            conditions.append(models_comments.BlogComments.status == 1)
        elif status == 'hidden':
            conditions.append(models_comments.BlogComments.status == 0)
        elif status == 'deleted':
            conditions.append(models_comments.BlogComments.status == -1)

    # 审核状态筛选
    if audit_status:
        # 需要检查字段是否存在，如果不存在则忽略
        if hasattr(models_comments.BlogComments, 'audit_status'):
            conditions.append(models_comments.BlogComments.audit_status == audit_status)

    # 用户ID筛选
    if user_id:
        conditions.append(models_comments.BlogComments.user_id == user_id)

    # 文章ID筛选
    if article_id:
        conditions.append(models_comments.BlogComments.article_id == article_id)

    # 关键词搜索
    if keyword:
        conditions.append(
            or_(
                models_comments.BlogComments.comment.like(f'%{keyword}%'),
                models_users.User.username.like(f'%{keyword}%'),
            )
        )

    # 日期范围筛选
    if start_date:
        try:
            start_timestamp = int(time.mktime(time.strptime(start_date, '%Y-%m-%d')))
            conditions.append(models_comments.BlogComments.createtime >= start_timestamp)
        except (ValueError, TypeError):
            pass

    if end_date:
        try:
            end_timestamp = int(time.mktime(time.strptime(end_date, '%Y-%m-%d'))) + 86400
            conditions.append(models_comments.BlogComments.createtime < end_timestamp)
        except (ValueError, TypeError):
            pass

    # 构建查询
    stmt = select(
        models_comments.BlogComments,
        models_users.User.username,
        models_users.User.profile_image,
        models_articles.BlogArticle.title,
        models_articles.BlogArticle.slug,
    ).outerjoin(
        models_users.User,
        models_comments.BlogComments.user_id == models_users.User.id,
    ).outerjoin(
        models_articles.BlogArticle,
        models_comments.BlogComments.article_id == models_articles.BlogArticle.id,
    )

    # 应用条件
    if conditions:
        stmt = stmt.where(and_(*conditions))

    # 排序
    stmt = stmt.order_by(desc(models_comments.BlogComments.createtime))

    # 计算总数
    count_stmt = select(func.count()).select_from(models_comments.BlogComments)
    if conditions:
        # 需要重新join来支持用户名搜索
        if keyword:
            count_stmt = count_stmt.join(
                models_users.User,
                models_comments.BlogComments.user_id == models_users.User.id,
            )
        count_stmt = count_stmt.where(and_(*conditions))

    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    # 分页
    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)

    # 执行查询
    result = await db.execute(stmt)
    rows = result.fetchall()

    # 构建结果
    comment_list = []
    for row in rows:
        comment = row[0]
        username = row[1] if row else '未知用户'
        user_avatar = row[2] if row else None
        article_title = row[3] if row and len(row) > 3 else None
        article_slug = row[4] if row and len(row) > 4 else None

        # 状态映射
        status_value = 'normal'
        if comment.status == 0:
            status_value = 'hidden'
        elif comment.status == -1:
            status_value = 'deleted'

        # 获取审核状态
        audit_status_value = getattr(comment, 'audit_status', 'approved')

        comment_list.append(schemas.CommentListItem(
            id=comment.id,
            user_id=comment.user_id,
            username=username,
            user_avatar=user_avatar,
            article_id=comment.article_id,
            article_title=article_title,
            article_slug=article_slug,
            comment=comment.comment,
            status=status_value,
            audit_status=audit_status_value,
            ip=comment.ip,
            created_at=comment.createtime,
            updated_at=getattr(comment, 'updatetime', None),
            replys=comment.replys,
            likes=comment.likes,
            parent_id=comment.pid,
            sensitive_words=getattr(comment, 'sensitive_words', None),
        ))

    return comment_list, total


async def update_comment_status(
    db: AsyncSession,
    comment_id: int,
    status: str,
    reason: Optional[str] = None,
    admin_id: Optional[int] = None,
) -> Optional[models_comments.BlogComments]:
    """
    更新评论状态
    status: normal/hidden/deleted
    """
    # 状态映射到数据库值
    status_map = {
        'normal': 1,
        'hidden': 0,
        'deleted': -1,
    }

    if status not in status_map:
        return None

    db_status = status_map[status]

    # 获取当前状态
    comment_stmt = select(models_comments.BlogComments).where(
        models_comments.BlogComments.id == comment_id
    )
    comment_result = await db.execute(comment_stmt)
    comment = comment_result.scalar_one_or_none()

    if not comment:
        return None

    from_status = 'normal' if comment.status == 1 else ('hidden' if comment.status == 0 else 'deleted')

    # 更新状态
    stmt = update(models_comments.BlogComments).where(
        models_comments.BlogComments.id == comment_id
    ).values(
        status=db_status,
        updatetime=int(time.time())
    )

    await db.execute(stmt)

    # 记录审核日志
    await _create_audit_log(
        db,
        comment_id=comment_id,
        action=status,
        from_status=from_status,
        to_status=status,
        admin_id=admin_id,
        reason=reason
    )

    await db.commit()
    await db.refresh(comment)

    return comment


async def update_comment_audit_status(
    db: AsyncSession,
    comment_id: int,
    audit_status: str,
    reason: Optional[str] = None,
    admin_id: Optional[int] = None,
) -> Optional[models_comments.BlogComments]:
    """
    更新评论审核状态
    audit_status: pending/approved/rejected
    """
    # 检查是否有audit_status字段
    if not hasattr(models_comments.BlogComments, 'audit_status'):
        return None

    # 获取当前评论
    comment_stmt = select(models_comments.BlogComments).where(
        models_comments.BlogComments.id == comment_id
    )
    comment_result = await db.execute(comment_stmt)
    comment = comment_result.scalar_one_or_none()

    if not comment:
        return None

    from_status = getattr(comment, 'audit_status', 'pending')

    # 更新审核状态
    update_data = {
        'audit_status': audit_status,
        'updatetime': int(time.time())
    }

    # 添加审核人和审核时间
    if admin_id:
        update_data['reviewed_by'] = admin_id
        update_data['reviewed_at'] = int(time.time())

    stmt = update(models_comments.BlogComments).where(
        models_comments.BlogComments.id == comment_id
    ).values(**update_data)

    await db.execute(stmt)

    # 记录审核日志
    await _create_audit_log(
        db,
        comment_id=comment_id,
        action=audit_status,
        from_status=from_status,
        to_status=audit_status,
        admin_id=admin_id,
        reason=reason
    )

    await db.commit()
    await db.refresh(comment)

    return comment


async def batch_update_comments(
    db: AsyncSession,
    action: str,
    comment_ids: List[int],
    reason: Optional[str] = None,
    admin_id: Optional[int] = None,
) -> int:
    """
    批量操作评论
    action: approve(通过)/reject(拒绝)/hide(隐藏)/show(显示)/delete(删除)
    """
    if not comment_ids:
        return 0

    updated_count = 0

    for comment_id in comment_ids:
        if action == 'approve':
            # 审核通过
            comment = await update_comment_audit_status(
                db, comment_id, 'approved', reason, admin_id
            )
            if comment:
                updated_count += 1

        elif action == 'reject':
            # 审核拒绝
            comment = await update_comment_audit_status(
                db, comment_id, 'rejected', reason, admin_id
            )
            if comment:
                updated_count += 1

        elif action == 'hide':
            # 隐藏评论
            comment = await update_comment_status(
                db, comment_id, 'hidden', reason, admin_id
            )
            if comment:
                updated_count += 1

        elif action == 'show':
            # 显示评论
            comment = await update_comment_status(
                db, comment_id, 'normal', reason, admin_id
            )
            if comment:
                updated_count += 1

        elif action == 'delete':
            # 删除评论
            comment = await update_comment_status(
                db, comment_id, 'deleted', reason, admin_id
            )
            if comment:
                updated_count += 1

    await db.commit()
    return updated_count


async def get_comment_statistics(
    db: AsyncSession,
) -> schemas.CommentStatistics:
    """
    获取评论统计数据
    """
    now = int(time.time())
    day_start = now - 86400  # 24小时前
    week_start = now - 604800  # 7天前

    # 总评论数
    total_stmt = select(func.count()).select_from(models_comments.BlogComments).where(
        models_comments.BlogComments.status != -1
    )
    total_result = await db.execute(total_stmt)
    total_comments = total_result.scalar() or 0

    # 待审核评论数
    pending_audit = 0
    if hasattr(models_comments.BlogComments, 'audit_status'):
        pending_stmt = select(func.count()).select_from(models_comments.BlogComments).where(
            and_(
                models_comments.BlogComments.status != -1,
                models_comments.BlogComments.audit_status == 'pending'
            )
        )
        pending_result = await db.execute(pending_stmt)
        pending_audit = pending_result.scalar() or 0

    # 今日评论数
    today_stmt = select(func.count()).select_from(models_comments.BlogComments).where(
        and_(
            models_comments.BlogComments.status != -1,
            models_comments.BlogComments.createtime >= day_start
        )
    )
    today_result = await db.execute(today_stmt)
    today_comments = today_result.scalar() or 0

    # 本周评论数
    week_stmt = select(func.count()).select_from(models_comments.BlogComments).where(
        and_(
            models_comments.BlogComments.status != -1,
            models_comments.BlogComments.createtime >= week_start
        )
    )
    week_result = await db.execute(week_stmt)
    week_comments = week_result.scalar() or 0

    # 被隐藏评论数
    hidden_stmt = select(func.count()).select_from(models_comments.BlogComments).where(
        models_comments.BlogComments.status == 0
    )
    hidden_result = await db.execute(hidden_stmt)
    hidden_comments = hidden_result.scalar() or 0

    # 被删除评论数
    deleted_stmt = select(func.count()).select_from(models_comments.BlogComments).where(
        models_comments.BlogComments.status == -1
    )
    deleted_result = await db.execute(deleted_stmt)
    deleted_comments = deleted_result.scalar() or 0

    # 含敏感词评论数
    sensitive_detected = 0
    if hasattr(models_comments.BlogComments, 'sensitive_words'):
        sensitive_stmt = select(func.count()).select_from(models_comments.BlogComments).where(
            and_(
                models_comments.BlogComments.status != -1,
                models_comments.BlogComments.sensitive_words.isnot(None),
                models_comments.BlogComments.sensitive_words != ''
            )
        )
        sensitive_result = await db.execute(sensitive_stmt)
        sensitive_detected = sensitive_result.scalar() or 0

    return schemas.CommentStatistics(
        total_comments=total_comments,
        pending_audit=pending_audit,
        today_comments=today_comments,
        week_comments=week_comments,
        hidden_comments=hidden_comments,
        deleted_comments=deleted_comments,
        sensitive_detected=sensitive_detected,
    )


async def _create_audit_log(
    db: AsyncSession,
    comment_id: int,
    action: str,
    from_status: str,
    to_status: str,
    admin_id: Optional[int] = None,
    reason: Optional[str] = None,
):
    """创建审核日志"""
    if not hasattr(models_admin, 'CommentAuditLog'):
        return

    log = models_admin.CommentAuditLog(
        comment_id=comment_id,
        action=action,
        from_status=from_status,
        to_status=to_status,
        admin_id=admin_id,
        reason=reason,
        created_at=int(time.time())
    )
    db.add(log)


# ==================== 敏感词管理 ====================

async def get_sensitive_words(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    keyword: Optional[str] = None,
    type: Optional[str] = None,
    status: Optional[str] = None,
) -> Tuple[List[models_admin.SensitiveWord], int]:
    """
    获取敏感词列表
    """
    conditions = []

    if keyword:
        conditions.append(models_admin.SensitiveWord.word.like(f'%{keyword}%'))

    if type:
        conditions.append(models_admin.SensitiveWord.type == type)

    if status:
        conditions.append(models_admin.SensitiveWord.status == status)

    # 构建查询
    stmt = select(models_admin.SensitiveWord)

    if conditions:
        stmt = stmt.where(and_(*conditions))

    # 计算总数
    count_stmt = select(func.count()).select_from(models_admin.SensitiveWord)
    if conditions:
        count_stmt = count_stmt.where(and_(*conditions))

    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    # 排序和分页
    stmt = stmt.order_by(desc(models_admin.SensitiveWord.created_at))
    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)

    result = await db.execute(stmt)
    words = result.scalars().all()

    return list(words), total


async def create_sensitive_word(
    db: AsyncSession,
    word_data: schemas.SensitiveWordCreate,
    created_by: int,
) -> models_admin.SensitiveWord:
    """创建敏感词"""
    word = models_admin.SensitiveWord(
        word=word_data.word,
        type=word_data.type,
        replacement=word_data.replacement,
        category=word_data.category,
        status='active',
        created_at=int(time.time()),
        created_by=created_by,
    )
    db.add(word)
    await db.commit()
    await db.refresh(word)
    return word


async def update_sensitive_word(
    db: AsyncSession,
    word_id: int,
    word_data: schemas.SensitiveWordUpdate,
) -> Optional[models_admin.SensitiveWord]:
    """更新敏感词"""
    stmt = select(models_admin.SensitiveWord).where(
        models_admin.SensitiveWord.id == word_id
    )
    result = await db.execute(stmt)
    word = result.scalar_one_or_none()

    if not word:
        return None

    # 更新字段
    update_data = {}
    if word_data.word is not None:
        update_data['word'] = word_data.word
    if word_data.type is not None:
        update_data['type'] = word_data.type
    if word_data.replacement is not None:
        update_data['replacement'] = word_data.replacement
    if word_data.category is not None:
        update_data['category'] = word_data.category
    if word_data.status is not None:
        update_data['status'] = word_data.status

    if update_data:
        await db.execute(
            update(models_admin.SensitiveWord).where(
                models_admin.SensitiveWord.id == word_id
            ).values(**update_data)
        )
        await db.commit()
        await db.refresh(word)

    return word


async def delete_sensitive_word(
    db: AsyncSession,
    word_id: int,
) -> bool:
    """删除敏感词"""
    stmt = select(models_admin.SensitiveWord).where(
        models_admin.SensitiveWord.id == word_id
    )
    result = await db.execute(stmt)
    word = result.scalar_one_or_none()

    if not word:
        return False

    await db.delete(word)
    await db.commit()
    return True


# ==================== 黑名单管理 ====================

async def get_blacklist(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    type: Optional[str] = None,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
) -> Tuple[List[schemas.BlacklistResponse], int]:
    """
    获取黑名单列表
    """
    conditions = []

    if type:
        conditions.append(models_admin.Blacklist.type == type)

    if status:
        conditions.append(models_admin.Blacklist.status == status)

    if keyword:
        conditions.append(
            models_users.User.username.like(f'%{keyword}%')
        )

    # 构建查询
    stmt = select(
        models_admin.Blacklist,
        models_users.User.username,
        models_users.User.profile_image,
    ).outerjoin(
        models_users.User,
        models_admin.Blacklist.user_id == models_users.User.id,
    )

    if conditions:
        stmt = stmt.where(and_(*conditions))

    # 计算总数
    count_stmt = select(func.count()).select_from(models_admin.Blacklist)
    if conditions:
        # 如果有用户名搜索，需要join
        if keyword:
            count_stmt = count_stmt.join(
                models_users.User,
                models_admin.Blacklist.user_id == models_users.User.id,
            )
        count_stmt = count_stmt.where(and_(*conditions))

    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    # 排序和分页
    stmt = stmt.order_by(desc(models_admin.Blacklist.created_at))
    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)

    result = await db.execute(stmt)
    rows = result.fetchall()

    # 构建结果
    blacklist = []
    for row in rows:
        bl = row[0]
        username = row[1] if row and len(row) > 1 else None
        user_avatar = row[2] if row and len(row) > 2 else None

        # 获取管理员名称
        admin_name = None
        if bl.admin_id:
            admin_stmt = select(models_users.User.username).where(
                models_users.User.id == bl.admin_id
            )
            admin_result = await db.execute(admin_stmt)
            admin_name = admin_result.scalar()

        blacklist.append(schemas.BlacklistResponse(
            id=bl.id,
            user_id=bl.user_id,
            username=username,
            user_avatar=user_avatar,
            type=bl.type,
            reason=bl.reason,
            note=bl.note,
            expire_at=bl.expire_at,
            status=bl.status,
            created_at=bl.created_at,
            admin_name=admin_name,
        ))

    return blacklist, total


async def create_blacklist(
    db: AsyncSession,
    blacklist_data: schemas.BlacklistCreate,
    admin_id: int,
) -> models_admin.Blacklist:
    """创建黑名单"""
    bl = models_admin.Blacklist(
        user_id=blacklist_data.user_id,
        type=blacklist_data.type,
        reason=blacklist_data.reason,
        note=blacklist_data.note,
        expire_at=blacklist_data.expire_at,
        admin_id=admin_id,
        status='active',
        created_at=int(time.time()),
        updated_at=int(time.time()),
    )
    db.add(bl)
    await db.commit()
    await db.refresh(bl)
    return bl


async def update_blacklist(
    db: AsyncSession,
    blacklist_id: int,
    status: Optional[str] = None,
    expire_at: Optional[int] = None,
    note: Optional[str] = None,
) -> Optional[models_admin.Blacklist]:
    """更新黑名单"""
    stmt = select(models_admin.Blacklist).where(
        models_admin.Blacklist.id == blacklist_id
    )
    result = await db.execute(stmt)
    bl = result.scalar_one_or_none()

    if not bl:
        return None

    update_data = {'updated_at': int(time.time())}

    if status is not None:
        update_data['status'] = status
    if expire_at is not None:
        update_data['expire_at'] = expire_at
    if note is not None:
        update_data['note'] = note

    await db.execute(
        update(models_admin.Blacklist).where(
            models_admin.Blacklist.id == blacklist_id
        ).values(**update_data)
    )
    await db.commit()
    await db.refresh(bl)

    return bl


async def delete_blacklist(
    db: AsyncSession,
    blacklist_id: int,
) -> bool:
    """删除黑名单"""
    stmt = select(models_admin.Blacklist).where(
        models_admin.Blacklist.id == blacklist_id
    )
    result = await db.execute(stmt)
    bl = result.scalar_one_or_none()

    if not bl:
        return False

    await db.delete(bl)
    await db.commit()
    return True


async def check_user_blacklist(
    db: AsyncSession,
    user_id: int,
    type: str = 'comment',
) -> bool:
    """
    检查用户是否在黑名单中
    返回 True 表示在黑名单中（被拉黑）
    """
    now = int(time.time())

    stmt = select(func.count()).select_from(models_admin.Blacklist).where(
        and_(
            models_admin.Blacklist.user_id == user_id,
            models_admin.Blacklist.type == type,
            models_admin.Blacklist.status == 'active',
            or_(
                models_admin.Blacklist.expire_at.is_(None),
                models_admin.Blacklist.expire_at > now,
            )
        )
    )

    result = await db.execute(stmt)
    count = result.scalar() or 0

    return count > 0


# ==================== 系统设置 ====================

async def get_system_setting(
    db: AsyncSession,
    key: str,
) -> Optional[models_admin.SystemSetting]:
    """获取系统设置"""
    stmt = select(models_admin.SystemSetting).where(
        models_admin.SystemSetting.key == key
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_system_setting(
    db: AsyncSession,
    key: str,
    value: str,
    updated_by: Optional[int] = None,
) -> Optional[models_admin.SystemSetting]:
    """更新或创建系统设置"""
    stmt = select(models_admin.SystemSetting).where(
        models_admin.SystemSetting.key == key
    )
    result = await db.execute(stmt)
    setting = result.scalar_one_or_none()

    now = int(time.time())

    if setting:
        # 更新
        await db.execute(
            update(models_admin.SystemSetting).where(
                models_admin.SystemSetting.key == key
            ).values(
                value=value,
                updated_at=now,
                updated_by=updated_by,
            )
        )
        await db.commit()
        await db.refresh(setting)
        return setting
    else:
        # 创建
        new_setting = models_admin.SystemSetting(
            key=key,
            value=value,
            type='string',
            updated_at=now,
            updated_by=updated_by,
        )
        db.add(new_setting)
        await db.commit()
        await db.refresh(new_setting)
        return new_setting


async def get_comment_audit_enabled(
    db: AsyncSession,
) -> bool:
    """获取是否开启评论审核"""
    setting = await get_system_setting(db, 'comment_audit_enabled')
    if not setting:
        return False
    return setting.value.lower() in ('true', '1', 'yes')
