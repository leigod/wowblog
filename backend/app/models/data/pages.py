from sqlalchemy import Column, Integer, String, DateTime, Text
from app.database import Base
from datetime import datetime


class BlogPage(Base):
    __tablename__ = 'wb_pages'

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(10))
    title = Column(String(20), index=True)
    content = Column(Text)
    slug = Column(String(20))
    image = Column(String(100))
    seo_desc = Column(String(300))
    status = Column(String(10))
    createtime = Column(Integer, default=lambda: int(datetime.now().timestamp()))
    updatetime = Column(Integer, default=lambda: int(datetime.now().timestamp()))