from sqlalchemy import Column, Integer, String, DateTime, Text
from app.database import Base
from datetime import datetime
import time

class BlogArticle(Base):
    __tablename__ = 'wb_articles'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), index=True)
    subtitle = Column(String(200))
    cover = Column(String(100))
    content = Column(Text)
    author = Column(Integer, index=True)
    co_authors = Column(String(100))
    # 平台分类：审核发布时由 Admin/Editor 指定，Author 提交时可为空（迁移 c9e1f5a8b3d6）
    category_id = Column(Integer, index=True, nullable=True)
    series_id = Column(Integer, index=True)
    # 作者自己 blog 的分类/系列归属（wb_user_categories / wb_user_series.id），
    # 与平台维度 category_id/series_id 互不影响；均可为空（P1 迁移 b8d2e6f4a9c1）
    blog_category_id = Column(Integer, index=True, comment='Blog 分类（wb_user_categories.id，可空）')
    blog_series_id = Column(Integer, index=True, comment='Blog 系列（wb_user_series.id，可空）')
    # 个人 blog 内置顶/排序（仅影响 /blog/:username 展示顺序，与平台 is_pin/sort 互不影响）
    blog_top = Column(Integer, nullable=False, default=0, server_default='0',
                      comment='个人blog内置顶：1=置顶（焦点区优先），0=普通')
    blog_sort = Column(Integer, nullable=False, default=0, server_default='0',
                       comment='个人blog内排序权重（大者靠前）')
    tags = Column(String(100))
    status = Column(String(20))
    # ORM default 兜底：客户端未传 pub_time 时（crud 按 exclude_unset 落库，
    # schema 默认值不进 fields_set 会被剥掉），由 SQLAlchemy 填当前时间。
    # 此前无 default 且 DB 列 NOT NULL，不传即 1048（历史漂移：模型未声明 nullable=False）
    pub_time = Column(Integer, default=lambda: int(time.time()))
    slug = Column(String(100))
    seo_title = Column(String(100))
    seo_desc = Column(String(300))
    og_image = Column(String(100))
    disable_comments = Column(Integer, default=0)
    enable_table_content = Column(Integer, default=0)
    is_pin = Column(Integer, default=0)
    is_recommend = Column(Integer, default=0)
    is_featured = Column(Integer, default=0)
    # onupdate: ORM 发出 UPDATE 时自动刷新时间戳（项目对本文表全部走 ORM 更新）；
    # 此前无 onupdate，行更新后 updatetime 仍是旧值，排查问题时具有误导性
    updatetime = Column(Integer, default=lambda: int(time.time()), onupdate=lambda: int(time.time()))
    createtime = Column(Integer, default=lambda: int(time.time()))
    sort = Column(Integer, default=0, comment='排序权重')
    deletetime = Column(Integer, nullable=True, comment='软删时间戳，NULL=未删')


class BlogArticleStatData(Base):
    __tablename__ = 'wb_articles_data'

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, index=True)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    bookmarks = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    views = Column(Integer, default=0)
