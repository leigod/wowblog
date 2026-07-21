"""
用户OAuth绑定数据模型
"""
from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey
from app.database import Base
from datetime import datetime


class UserOAuth(Base):
    """用户第三方登录绑定表"""
    __tablename__ = 'wb_user_oauth'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('wb_users.id', ondelete='CASCADE'), nullable=False, index=True)
    provider = Column(String(50), nullable=False)  # google, github, apple, wechat, qq, alipay
    provider_user_id = Column(String(255), nullable=False)  # 第三方平台的用户ID
    access_token = Column(Text, nullable=True)  # 访问令牌
    refresh_token = Column(Text, nullable=True)  # 刷新令牌
    email = Column(String(255), nullable=True)  # 第三方邮箱
    avatar_url = Column(String(500), nullable=True)  # 第三方头像URL
    raw_data = Column(JSON, nullable=True)  # 原始用户数据
    createtime = Column(Integer, default=lambda: int(datetime.now().timestamp()))
    updatetime = Column(Integer, default=lambda: int(datetime.now().timestamp()), onupdate=lambda: int(datetime.now().timestamp()))
