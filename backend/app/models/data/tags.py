from sqlalchemy import Column, Integer, String, DateTime, Text
from app.database import Base
from datetime import datetime


class BlogTag(Base):
    __tablename__ = 'wb_tags'

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(10))
    name = Column(String(20), index=True)
    slug = Column(String(20))
    image = Column(String(100))
    tag_desc = Column(String(200))
    counts = Column(Integer, default=0)
    views = Column(Integer, default=0)
    follows = Column(Integer, default=0)
    status = Column(String(20))