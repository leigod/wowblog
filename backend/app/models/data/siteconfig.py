from typing import Optional, Literal
from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum as SQLEnum
from app.database import Base
import json


class SiteConfig(Base):
    __tablename__ = 'wb_config'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    site_title: Mapped[Optional[str]] = mapped_column(String(100))
    site_logo: Mapped[Optional[str]] = mapped_column(String(100))
    site_favicon: Mapped[Optional[str]] = mapped_column(String(100))
    language: Mapped[Optional[str]] = mapped_column(String(10))
    dark_mode: Mapped[str] = mapped_column(String(20), default='system')
    disable_comment: Mapped[int] = mapped_column(Integer, default=0)
    doc_comment: Mapped[int] = mapped_column(Integer, default=1, comment='文档评论开关，0=禁用，1=开启')
    _footer_config: Mapped[Optional[str]] = mapped_column(
        'footer_config',
        Text,
        nullable=True,
        comment='Footer配置JSON'
    )

    # 文档模块配置
    default_homepage: Mapped[Literal['blog', 'doc']] = mapped_column(
        SQLEnum('blog', 'doc'),
        default='blog',
        comment='默认首页类型'
    )
    default_docbook_id: Mapped[Optional[int]] = mapped_column(Integer, comment='默认文档书ID')
    doc_subdomain: Mapped[Optional[str]] = mapped_column(String(100), comment='文档模块子域名')

    # 消息推送配置
    message_push_method: Mapped[Literal['websocket', 'polling']] = mapped_column(
        SQLEnum('websocket', 'polling', name='messagepushmethod'),
        default='websocket',
        comment='消息推送方式：websocket=实时推送，polling=定时轮询'
    )
    polling_interval: Mapped[int] = mapped_column(
        Integer,
        default=30,
        comment='轮询间隔（秒），仅当push_method为polling时有效'
    )

    # 注册配置
    enable_register: Mapped[int] = mapped_column(Integer, default=1, comment='是否开启注册，0=不开启，1=开启')
    register_role: Mapped[str] = mapped_column(String(20), default='User', comment='用户注册默认角色')

    # 文章审核通知配置
    enable_article_review_notification: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment='是否开启文章审核通知，0=不开启，1=开启'
    )
    article_review_notification_roles: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment='文章审核通知接收角色，JSON数组格式，如["Admin","Editor"]'
    )

    @property
    def footer_config(self):
        """获取 footer_config，自动解析 JSON"""
        if self._footer_config:
            try:
                return json.loads(self._footer_config)
            except (json.JSONDecodeError, TypeError):
                return None
        return None

    @footer_config.setter
    def footer_config(self, value):
        """设置 footer_config，自动序列化为 JSON 字符串"""
        if value is None:
            self._footer_config = None
        elif isinstance(value, str):
            self._footer_config = value
        else:
            self._footer_config = json.dumps(value, ensure_ascii=False)
