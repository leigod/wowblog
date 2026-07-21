from sqlalchemy import Column, Integer, String, DateTime, Text
from app.database import Base
import time


class User(Base):
    __tablename__ = 'wb_users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(20), index=True)
    password = Column(String(32))
    salt = Column(String(64))
    full_name = Column(String(20), default=None)
    email = Column(String(50), unique=True, index=True)
    mobile = Column(String(11), unique=True, index=True)
    profile_image = Column(String(100), default=None)
    status = Column(String(10), default='normal')
    role = Column(String(20), default='user')
    gender = Column(Integer, default=0)
    birthday = Column(Integer, default=None)
    visibility = Column(String(10), default='Private')
    login_ip = Column(String(20), default=None)
    login_time = Column(Integer, default=None)
    join_ip = Column(String(20), default=None)
    createtime = Column(Integer, default=int(time.time()))
    # 扩展字段
    profile_tagline = Column(String(100), default=None)
    location = Column(String(100), default=None)
    school = Column(String(100), default=None)
    profile_bio = Column(Text, default=None)
    tech_stack = Column(String(300), default=None)
    available_for = Column(String(300), default=None)
    social_profiles = Column(Text, default=None)
    # 隐私设置
    privacy_show_bookmarks = Column(Integer, default=1)
    privacy_show_likes = Column(Integer, default=1)
    privacy_show_comments = Column(Integer, default=1)
    privacy_show_views = Column(Integer, default=1)


class UserInteractionData(Base):
    __tablename__ = 'wb_users_data'

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(20))
    user_id = Column(Integer, index=True)
    target_id = Column(Integer, index=True)
    status = Column(Integer, default=1) 
    createtime = Column(Integer, default=int(time.time()))
    updatetime = Column(Integer, default=int(time.time()))