from pydantic import BaseModel
from datetime import datetime
from pydantic.config import ConfigDict
from typing import Optional, List, Literal
import time

class BlogCommentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    article_id: int | None = None  # 改为可空
    doc_id: int | None = None  # 添加文档ID
    user_id: int
    comment: str
    ip: str | None = None
    likes: int | None = 0
    unlikes: int | None = 0
    replys: int | None = 0
    type: str = 'reply'
    subject_id: int | None = 0
    sort: int | None = 0
    status: int | None = 1
    createtime: int | None = int(time.time())

class BlogCommentCreateForm(BaseModel):
    article_id: int | None = None  # 改为可空
    doc_id: int | None = None  # 添加文档ID
    user_id: int | None = None
    comment: str
    type: str = 'reply'
    subject_id: int | None = 0
    pid: int | None = 0

class BlogCommentCreate(BlogCommentBase):
    article_id: int
    user_id: int
    comment: str
    ip: str | None = None
    likes: int | None = 0
    unlikes: int | None = 0
    replys: int | None = 0
    type: str = 'reply'
    subject_id: int | None = 0
    sort: int | None = 0
    status: int | None = 1
    createtime: int | None = int(time.time())


class BlogCommentListItem(BaseModel):
    # 评论信息
    id: int
    article_id: int | None = None  # 改为可空
    doc_id: int | None = None  # 添加文档ID
    user_id: int
    comment: str
    ip: str | None = None
    likes: int | None = 0
    unlikes: int | None = 0
    replys: int | None = 0
    type: str = 'reply'
    subject_id: int | None = 0
    pid: int | None = 0
    createtime: int | None = int(time.time())
    # 用户信息
    username: str
    full_name: str
    profile_image: str | None = None
    # 其他信息
    location: str | None = None


class BlogComment(BlogCommentBase):
    id: int


class TopCommenter(BaseModel):
    """活跃评论者"""
    id: int
    username: str
    full_name: str | None = None
    avatar: str | None = None
    comment_count: int