"""
管理后台评论相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ==================== 评论管理 ====================
class CommentListItem(BaseModel):
    """评论列表项"""
    id: int
    user_id: int
    username: str
    user_avatar: Optional[str] = None
    article_id: Optional[int] = None
    article_title: Optional[str] = None
    article_slug: Optional[str] = None
    comment: str
    status: str = 'normal'
    audit_status: str = 'approved'
    ip: Optional[str] = None
    created_at: int
    updated_at: Optional[int] = None
    replys: int = 0
    likes: int = 0
    parent_id: Optional[int] = None
    sensitive_words: Optional[str] = None
    
    class Config:
        from_attributes = True


class CommentListRequest(BaseModel):
    """评论列表请求"""
    page: int = Field(default=1, ge=1, description='页码')
    page_size: int = Field(default=20, ge=1, le=100, description='每页数量')
    status: Optional[str] = Field(default='all', description='状态筛选')
    audit_status: Optional[str] = Field(default=None, description='审核状态筛选')
    user_id: Optional[int] = Field(default=None, description='用户ID筛选')
    article_id: Optional[int] = Field(default=None, description='文章ID筛选')
    keyword: Optional[str] = Field(default=None, description='关键词搜索')
    start_date: Optional[str] = Field(default=None, description='开始日期')
    end_date: Optional[str] = Field(default=None, description='结束日期')


class CommentListResponse(BaseModel):
    """评论列表响应"""
    list: List[CommentListItem]
    total: int
    page: int
    page_size: int


class CommentStatusUpdate(BaseModel):
    """评论状态更新"""
    status: str = Field(description='状态: normal/hidden/deleted')
    reason: Optional[str] = Field(default=None, description='操作原因')


class CommentAuditUpdate(BaseModel):
    """评论审核更新"""
    audit_status: str = Field(description='审核状态: pending/approved/rejected')
    reason: Optional[str] = Field(default=None, description='审核原因')


class CommentBatchOperation(BaseModel):
    """批量操作"""
    action: str = Field(description='操作类型: approve/reject/hide/show/delete')
    comment_ids: List[int] = Field(description='评论ID列表')
    reason: Optional[str] = Field(default=None, description='操作原因')


# ==================== 敏感词管理 ====================
class SensitiveWordCreate(BaseModel):
    """创建敏感词"""
    word: str = Field(..., min_length=1, max_length=100, description='敏感词')
    type: str = Field(default='banned', description='类型: banned/review/replace')
    replacement: Optional[str] = Field(default=None, description='替换内容')
    category: Optional[str] = Field(default='other', description='分类')


class SensitiveWordUpdate(BaseModel):
    """更新敏感词"""
    word: Optional[str] = Field(default=None, min_length=1, max_length=100)
    type: Optional[str] = None
    replacement: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None


class SensitiveWordResponse(BaseModel):
    """敏感词响应"""
    id: int
    word: str
    type: str
    replacement: Optional[str] = None
    category: Optional[str] = None
    status: str
    created_at: int
    created_by: Optional[int] = None
    
    class Config:
        from_attributes = True


# ==================== 黑名单管理 ====================
class BlacklistCreate(BaseModel):
    """创建黑名单"""
    user_id: int = Field(..., description='用户ID')
    type: str = Field(default='comment', description='限制类型')
    reason: Optional[str] = Field(default=None, description='拉黑原因')
    note: Optional[str] = Field(default=None, description='备注')
    expire_at: Optional[int] = Field(default=None, description='过期时间')


class BlacklistResponse(BaseModel):
    """黑名单响应"""
    id: int
    user_id: int
    username: Optional[str] = None
    user_avatar: Optional[str] = None
    type: str
    reason: Optional[str] = None
    note: Optional[str] = None
    expire_at: Optional[int] = None
    status: str
    created_at: int
    admin_name: Optional[str] = None
    
    class Config:
        from_attributes = True


# ==================== 统计数据 ====================
class CommentStatistics(BaseModel):
    """评论统计数据"""
    total_comments: int = Field(description='总评论数')
    pending_audit: int = Field(description='待审核评论数')
    today_comments: int = Field(description='今日评论数')
    week_comments: int = Field(description='本周评论数')
    hidden_comments: int = Field(description='被隐藏评论数')
    deleted_comments: int = Field(description='被删除评论数')
    sensitive_detected: int = Field(description='含敏感词评论数')


# ==================== 系统设置 ====================
class SystemSettingUpdate(BaseModel):
    """系统设置更新"""
    value: str = Field(..., description='设置值')


class SystemSettingResponse(BaseModel):
    """系统设置响应"""
    key: str
    value: str
    type: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True
