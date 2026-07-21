from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base
from datetime import datetime


class BlogNav(Base):
    __tablename__ = 'wb_nav'

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String(100), index=True)
    nav_type = Column(String(10))
    type = Column(String(50))
    value = Column(String(100))
    sort = Column(Integer, default=0)
    status = Column(Integer, default=1)
