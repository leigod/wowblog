from sqlalchemy import Column, Integer, String, DateTime, Text
from app.database import Base
import time

class BlogComments(Base):
    __tablename__ = 'wb_comments'
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, default=0)  # 默认为0，支持文档评论
    doc_id = Column(Integer, default=0)  # 添加文档ID字段，默认为0
    user_id = Column(Integer)
    comment = Column(String(500))
    ip = Column(String(15))
    likes = Column(Integer, default=0)
    unlikes = Column(Integer, default=0)
    replys = Column(Integer, default=0)
    type = Column(String(20), default='reply')
    subject_id = Column(Integer, default=0)
    pid=Column(Integer, default=0)
    sort = Column(Integer, default=0)
    status = Column(Integer, default=1)
    createtime = Column(Integer, default=lambda: int(time.time()))
    deletetime = Column(Integer, default=None)
