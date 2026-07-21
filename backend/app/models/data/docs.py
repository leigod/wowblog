"""
文档模块数据模型
"""
from typing import Optional, Literal
from sqlalchemy import Column, Integer, String, Text, Boolean, Enum as SQLEnum, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class DocBook(Base):
    """文档书模型"""
    __tablename__ = 'wb_docbook'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment='文档书名称')
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True, comment='URL标识')
    description: Mapped[Optional[str]] = mapped_column(Text, comment='文档书描述')
    cover: Mapped[Optional[str]] = mapped_column(String(500), comment='封面图URL')
    icon: Mapped[Optional[str]] = mapped_column(String(100), comment='图标')

    # 设置
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, comment='是否公开')
    show_sidebar: Mapped[bool] = mapped_column(Boolean, default=True, comment='是否显示侧边栏')
    allow_comment: Mapped[bool] = mapped_column(Boolean, default=True, comment='是否允许评论')
    allow_search: Mapped[bool] = mapped_column(Boolean, default=True, comment='是否允许搜索')

    # 主题
    theme: Mapped[str] = mapped_column(String(50), default='default', comment='主题样式')

    # 首页文档
    home_doc_id: Mapped[Optional[int]] = mapped_column(Integer, comment='首页文档ID')

    # 作者信息
    author_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True, comment='创建者ID')

    # 排序
    sort_order: Mapped[int] = mapped_column(Integer, default=0, comment='排序')

    # 时间
    createtime: Mapped[int] = mapped_column(Integer, nullable=False, comment='创建时间')
    updatetime: Mapped[int] = mapped_column(Integer, nullable=False, comment='更新时间')

    # 关系
    docs = relationship("Doc", back_populates="docbook", cascade="all, delete-orphan")


class Doc(Base):
    """文档模型"""
    __tablename__ = 'wb_doc'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    docbook_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('wb_docbook.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment='所属文档书ID'
    )

    # 内容字段
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment='文档标题')
    slug: Mapped[str] = mapped_column(String(255), nullable=False, comment='URL标识')
    content: Mapped[Optional[str]] = mapped_column(Text, comment='文档内容（Markdown）')
    excerpt: Mapped[Optional[str]] = mapped_column(Text, comment='摘要')

    # 树形结构
    parent_id: Mapped[int] = mapped_column(Integer, default=0, index=True, comment='父文档ID，0为顶级')
    level: Mapped[int] = mapped_column(Integer, default=1, comment='层级深度')
    path: Mapped[Optional[str]] = mapped_column(String(500), comment='树路径：0/1/2')
    sort_order: Mapped[int] = mapped_column(Integer, default=0, comment='同级排序')

    # 状态
    status: Mapped[Literal['draft', 'published', 'hidden']] = mapped_column(
        SQLEnum('draft', 'published', 'hidden'),
        default='draft',
        index=True,
        comment='状态'
    )

    # 作者和时间
    author_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True, comment='作者ID')
    createtime: Mapped[int] = mapped_column(Integer, nullable=False, comment='创建时间')
    updatetime: Mapped[int] = mapped_column(Integer, nullable=False, comment='更新时间')
    pubtime: Mapped[Optional[int]] = mapped_column(Integer, comment='发布时间')

    # 统计
    view_count: Mapped[int] = mapped_column(Integer, default=0, comment='浏览次数')
    comment_count: Mapped[int] = mapped_column(Integer, default=0, comment='评论数')

    # SEO
    seo_title: Mapped[Optional[str]] = mapped_column(String(255), comment='SEO标题')
    seo_keywords: Mapped[Optional[str]] = mapped_column(String(500), comment='SEO关键词')
    seo_description: Mapped[Optional[str]] = mapped_column(Text, comment='SEO描述')

    # 关系
    docbook = relationship("DocBook", back_populates="docs")

    # 复合索引
    __table_args__ = (
        Index('uk_docbook_slug', 'docbook_id', 'slug', unique=True),
    )
