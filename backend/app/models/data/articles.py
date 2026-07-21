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
    category_id = Column(Integer, index=True)
    series_id = Column(Integer, index=True)
    tags = Column(String(100))
    status = Column(String(20))
    pub_time = Column(Integer)
    slug = Column(String(100))
    seo_title = Column(String(100))
    seo_desc = Column(String(300))
    og_image = Column(String(100))
    disable_comments = Column(Integer, default=0)
    enable_table_content = Column(Integer, default=0)
    is_pin = Column(Integer, default=0)
    is_recommend = Column(Integer, default=0)
    is_featured = Column(Integer, default=0)
    updatetime = Column(Integer, default=lambda: int(time.time()))
    createtime = Column(Integer, default=lambda: int(time.time()))


class BlogArticleStatData(Base):
    __tablename__ = 'wb_articles_data'

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, index=True)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    bookmarks = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    views = Column(Integer, default=0)
