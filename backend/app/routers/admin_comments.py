"""
管理后台评论管理 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import time

from app.database import get_db
from app.dependencies.authentication import get_current_user
from app.models.data.users import User
import app.crud.admin_comments as crud
import app.models.schemas.admin_comments as schemas

router = APIRouter(prefix='/admin/comments', tags=['评论管理'])


def success(msg: str = "操作成功", **kwargs):
    """统一成功响应"""
    return {
        "code": 1,
        "msg": msg,
        **kwargs
    }


def error(msg: str = "操作失败", code: int = 0):
    """统一错误响应"""
    return {
        "code": code,
        "msg": msg
    }


# ==================== 评论管理 ====================

@router.get('/list')
async def get_comment_list(
    page: int = 1,
    page_size: int = 20,
    status: str = 'all',
    audit_status: Optional[str] = None,
    user_id: Optional[int] = None,
    article_id: Optional[int] = None,
    keyword: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取评论列表

    参数:
    - page: 页码
    - page_size: 每页数量
    - status: 状态筛选 (all/normal/hidden/deleted)
    - audit_status: 审核状态筛选 (pending/approved/rejected)
    - user_id: 用户ID筛选
    - article_id: 文章ID筛选
    - keyword: 关键词搜索
    - start_date: 开始日期 (YYYY-MM-DD)
    - end_date: 结束日期 (YYYY-MM-DD)
    """
    # 检查权限
    if current_user.role not in ['Admin', 'Editor']:
        raise HTTPException(status_code=403, detail='无权访问')

    comment_list, total = await crud.get_comment_list(
        db=db,
        page=page,
        page_size=page_size,
        status=status,
        audit_status=audit_status,
        user_id=user_id,
        article_id=article_id,
        keyword=keyword,
        start_date=start_date,
        end_date=end_date,
    )

    return success(
        msg='获取成功',
        list=comment_list,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post('/{comment_id}/status')
async def update_comment_status(
    comment_id: int,
    status_update: schemas.CommentStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    更新评论状态

    参数:
    - status: normal/hidden/deleted
    - reason: 操作原因
    """
    # 检查权限
    if current_user.role not in ['admin', 'editor']:
        raise HTTPException(status_code=403, detail='无权操作')

    comment = await crud.update_comment_status(
        db=db,
        comment_id=comment_id,
        status=status_update.status,
        reason=status_update.reason,
        admin_id=current_user.id,
    )

    if not comment:
        raise HTTPException(status_code=404, detail='评论不存在')

    return success(msg='状态更新成功')


@router.post('/{comment_id}/audit')
async def update_comment_audit(
    comment_id: int,
    audit_update: schemas.CommentAuditUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    更新评论审核状态

    参数:
    - audit_status: pending/approved/rejected
    - reason: 审核原因
    """
    # 检查权限
    if current_user.role not in ['admin', 'editor']:
        raise HTTPException(status_code=403, detail='无权操作')

    comment = await crud.update_comment_audit_status(
        db=db,
        comment_id=comment_id,
        audit_status=audit_update.audit_status,
        reason=audit_update.reason,
        admin_id=current_user.id,
    )

    if not comment:
        raise HTTPException(status_code=404, detail='评论不存在或审核功能未启用')

    return success(msg='审核状态更新成功')


@router.post('/batch')
async def batch_operation(
    batch_op: schemas.CommentBatchOperation,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    批量操作评论

    参数:
    - action: approve/reject/hide/show/delete
    - comment_ids: 评论ID列表
    - reason: 操作原因
    """
    # 检查权限
    if current_user.role not in ['admin', 'editor']:
        raise HTTPException(status_code=403, detail='无权操作')

    if not batch_op.comment_ids:
        raise HTTPException(status_code=400, detail='请选择要操作的评论')

    count = await crud.batch_update_comments(
        db=db,
        action=batch_op.action,
        comment_ids=batch_op.comment_ids,
        reason=batch_op.reason,
        admin_id=current_user.id,
    )

    action_map = {
        'approve': '通过',
        'reject': '拒绝',
        'hide': '隐藏',
        'show': '显示',
        'delete': '删除',
    }

    return success(msg=f'已{action_map.get(batch_op.action, batch_op.action)}{count}条评论')


@router.get('/statistics')
async def get_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取评论统计数据"""
    # 检查权限
    if current_user.role not in ['Admin', 'Editor']:
        raise HTTPException(status_code=403, detail='无权访问')

    stats = await crud.get_comment_statistics(db)
    return success(
        msg='获取成功',
        data={
            'total_comments': stats.total_comments,
            'pending_audit': stats.pending_audit,
            'today_comments': stats.today_comments,
            'week_comments': stats.week_comments,
            'hidden_comments': stats.hidden_comments,
            'deleted_comments': stats.deleted_comments,
            'sensitive_detected': stats.sensitive_detected,
        }
    )


# ==================== 敏感词管理 ====================

@router.get('/sensitive-words/list')
async def get_sensitive_words(
    page: int = 1,
    page_size: int = 20,
    keyword: Optional[str] = None,
    type: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取敏感词列表"""
    # 检查权限
    if current_user.role != 'Admin':
        raise HTTPException(status_code=403, detail='仅管理员可访问')

    words, total = await crud.get_sensitive_words(
        db=db,
        page=page,
        page_size=page_size,
        keyword=keyword,
        type=type,
        status=status,
    )

    return success(
        msg='获取成功',
        data=[{
            'id': w.id,
            'word': w.word,
            'type': w.type,
            'replacement': w.replacement,
            'category': w.category,
            'status': w.status,
            'created_at': w.created_at,
            'created_by': w.created_by,
        } for w in words],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post('/sensitive-words/create')
async def create_sensitive_word(
    word_data: schemas.SensitiveWordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建敏感词"""
    # 检查权限
    if current_user.role != 'Admin':
        raise HTTPException(status_code=403, detail='仅管理员可操作')

    word = await crud.create_sensitive_word(
        db=db,
        word_data=word_data,
        created_by=current_user.id,
    )

    return success(msg='创建成功', data={'id': word.id})


@router.post('/sensitive-words/{word_id}/update')
async def update_sensitive_word(
    word_id: int,
    word_data: schemas.SensitiveWordUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新敏感词"""
    # 检查权限
    if current_user.role != 'Admin':
        raise HTTPException(status_code=403, detail='仅管理员可操作')

    word = await crud.update_sensitive_word(
        db=db,
        word_id=word_id,
        word_data=word_data,
    )

    if not word:
        raise HTTPException(status_code=404, detail='敏感词不存在')

    return success(msg='更新成功')


@router.delete('/sensitive-words/{word_id}/delete')
async def delete_sensitive_word(
    word_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除敏感词"""
    # 检查权限
    if current_user.role != 'Admin':
        raise HTTPException(status_code=403, detail='仅管理员可操作')

    result = await crud.delete_sensitive_word(db=db, word_id=word_id)

    if not result:
        raise HTTPException(status_code=404, detail='敏感词不存在')

    return success(msg='删除成功')


# ==================== 黑名单管理 ====================

@router.get('/blacklist/list')
async def get_blacklist(
    page: int = 1,
    page_size: int = 20,
    type: Optional[str] = None,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取黑名单列表"""
    # 检查权限
    if current_user.role != 'Admin':
        raise HTTPException(status_code=403, detail='仅管理员可访问')

    blacklist, total = await crud.get_blacklist(
        db=db,
        page=page,
        page_size=page_size,
        type=type,
        status=status,
        keyword=keyword,
    )

    return success(
        msg='获取成功',
        data=blacklist,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post('/blacklist/create')
async def create_blacklist(
    blacklist_data: schemas.BlacklistCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建黑名单"""
    # 检查权限
    if current_user.role != 'Admin':
        raise HTTPException(status_code=403, detail='仅管理员可操作')

    bl = await crud.create_blacklist(
        db=db,
        blacklist_data=blacklist_data,
        admin_id=current_user.id,
    )

    return success(msg='创建成功', data={'id': bl.id})


@router.post('/blacklist/{blacklist_id}/update')
async def update_blacklist(
    blacklist_id: int,
    status: Optional[str] = None,
    expire_at: Optional[int] = None,
    note: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新黑名单"""
    # 检查权限
    if current_user.role != 'Admin':
        raise HTTPException(status_code=403, detail='仅管理员可操作')

    bl = await crud.update_blacklist(
        db=db,
        blacklist_id=blacklist_id,
        status=status,
        expire_at=expire_at,
        note=note,
    )

    if not bl:
        raise HTTPException(status_code=404, detail='黑名单记录不存在')

    return success(msg='更新成功')


@router.delete('/blacklist/{blacklist_id}/delete')
async def delete_blacklist(
    blacklist_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除黑名单"""
    # 检查权限
    if current_user.role != 'Admin':
        raise HTTPException(status_code=403, detail='仅管理员可操作')

    result = await crud.delete_blacklist(db=db, blacklist_id=blacklist_id)

    if not result:
        raise HTTPException(status_code=404, detail='黑名单记录不存在')

    return success(msg='删除成功')


# ==================== 系统设置 ====================

@router.get('/settings')
async def get_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取评论相关设置"""
    # 检查权限
    if current_user.role not in ['Admin', 'Editor']:
        raise HTTPException(status_code=403, detail='无权访问')

    audit_enabled = await crud.get_comment_audit_enabled(db)

    return success(
        msg='获取成功',
        data={
            'comment_audit_enabled': audit_enabled,
        }
    )


@router.post('/settings/update')
async def update_settings(
    key: str,
    value: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新系统设置"""
    # 检查权限
    if current_user.role != 'Admin':
        raise HTTPException(status_code=403, detail='仅管理员可操作')

    # 限制可更新的设置项
    allowed_keys = ['comment_audit_enabled', 'comment_auto_audit']
    if key not in allowed_keys:
        raise HTTPException(status_code=400, detail='不允许修改此设置项')

    setting = await crud.update_system_setting(
        db=db,
        key=key,
        value=value,
        updated_by=current_user.id,
    )

    return success(msg='设置已更新')
