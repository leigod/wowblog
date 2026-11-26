from typing import Optional, Literal
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON
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

    # 文章审核配置
    # 审核总开关：开启时 Author 发布固定为草稿（发布状态选择隐藏），由 Admin/Editor 放行
    article_review_enabled: Mapped[int] = mapped_column(
        Integer,
        default=1,
        server_default='1',
        comment='文章审核开关：1=开启（作者发布固定草稿待审核），0=关闭（作者可选发布状态）'
    )
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

    # OAuth 社交登录配置
    oauth_enabled: Mapped[int] = mapped_column(Integer, default=0, comment='是否启用社交登录，0=禁用，1=启用')
    enabled_oauth_providers: Mapped[Optional[list]] = mapped_column(JSON, default=list, comment='启用的 OAuth provider 列表，如["github","gitee"]')

    # 内容安全配置
    sensitive_words_enabled: Mapped[int] = mapped_column(Integer, default=0, comment='是否启用敏感词过滤，0=关闭，1=启用')

    # 图片水印配置（全站默认；Author 可在 wb_user_blogs 覆盖）
    watermark_enabled: Mapped[int] = mapped_column(Integer, default=0, server_default='0', comment='图片水印开关：1=开启，0=关闭')
    watermark_mode: Mapped[str] = mapped_column(String(10), default='corner', server_default='corner', comment='水印样式：corner=右下角单戳，tile=平铺防裁剪')

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
