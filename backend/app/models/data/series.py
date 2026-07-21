from sqlalchemy import Column, Integer, String, DateTime, Text
from app.database import Base
from datetime import datetime


class BlogSeries(Base):
    __tablename__ = 'wb_series'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    series_desc = Column(String(300))
    slug = Column(String(20))
    image = Column(String(100))
    articles_order = Column(String(10))
    sort = Column(Integer, default=0)
    createtime = Column(Integer, default=lambda: int(datetime.now().timestamp()))
    updatetime = Column(Integer, default=lambda: int(datetime.now().timestamp()))