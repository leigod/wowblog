"""
文档模块 Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


# ==================== DocBook Schemas ====================

class DocBookBase(BaseModel):
    """文档书基础模型"""
    name: str = Field(..., max_length=100, description="文档书名称")
    slug: str = Field(..., max_length=100, description="URL标识")
    description: Optional[str] = Field(None, description="文档书描述")
    cover: Optional[str] = Field(None, max_length=500, description="封面图URL")
    icon: Optional[str] = Field(None, max_length=100, description="图标")
    is_public: bool = Field(True, description="是否公开")
    show_sidebar: bool = Field(True, description="是否显示侧边栏")
    allow_comment: bool = Field(True, description="是否允许评论")
    allow_search: bool = Field(True, description="是否允许搜索")
    theme: str = Field("default", max_length=50, description="主题样式")
    home_doc_id: Optional[int] = Field(None, description="首页文档ID")
    sort_order: int = Field(0, description="排序")


class DocBookCreate(DocBookBase):
    """创建文档书"""
    pass


class DocBookUpdate(BaseModel):
    """更新文档书"""
    name: Optional[str] = Field(None, max_length=100)
    slug: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    cover: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = Field(None, max_length=100)
    is_public: Optional[bool] = None
    show_sidebar: Optional[bool] = None
    allow_comment: Optional[bool] = None
    allow_search: Optional[bool] = None
    theme: Optional[str] = None
    home_doc_id: Optional[int] = None
    sort_order: Optional[int] = None


class DocBookResponse(DocBookBase):
    """文档书响应"""
    id: int
    author_id: int
    author_name: Optional[str] = None
    doc_count: int = 0
    createtime: int
    updatetime: int

    class Config:
        from_attributes = True


# ==================== Doc Schemas ====================

class DocStatus(str, Enum):
    """文档状态"""
    draft = "draft"
    published = "published"
    hidden = "hidden"


class DocBase(BaseModel):
    """文档基础模型"""
    docbook_id: int = Field(..., description="所属文档书ID")
    title: str = Field(..., max_length=255, description="文档标题")
    slug: str = Field(..., max_length=255, description="URL标识")
    content: Optional[str] = Field(None, description="文档内容（Markdown）")
    excerpt: Optional[str] = Field(None, description="摘要")
    parent_id: int = Field(0, description="父文档ID，0为顶级")
    sort_order: int = Field(0, description="同级排序")
    status: DocStatus = Field(DocStatus.draft, description="状态")


class DocCreate(DocBase):
    """创建文档"""
    pass


class DocUpdate(BaseModel):
    """更新文档"""
    title: Optional[str] = Field(None, max_length=255)
    slug: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None
    excerpt: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None
    status: Optional[DocStatus] = None


class DocResponse(DocBase):
    """文档响应"""
    id: int
    level: int
    path: str
    author_id: int
    author_name: Optional[str] = None
    createtime: int
    updatetime: int
    pubtime: Optional[int] = None
    view_count: int
    comment_count: int
    children: List['DocResponse'] = []

    class Config:
        from_attributes = True


class DocTreeNode(BaseModel):
    """文档树节点"""
    id: int
    title: str
    slug: str
    level: int
    parent_id: int
    sort_order: int
    status: str
    children: List['DocTreeNode'] = []


class DocNavigation(BaseModel):
    """文档导航"""
    prev: Optional[DocResponse] = None
    next: Optional[DocResponse] = None
    parent: Optional[DocResponse] = None
    breadcrumbs: List[DocResponse] = []


# 更新前向引用
DocResponse.model_rebuild()
DocTreeNode.model_rebuild()
