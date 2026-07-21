from pydantic import BaseModel, Field
from pydantic.config import ConfigDict
from typing import Literal, Optional, Any

class SiteConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    site_title: str | None = None
    site_logo: str | None = None
    site_favicon: str | None = None
    language: str | None = "zh-CN"
    dark_mode: Literal['system', 'dark','light'] = "system"
    disable_comment: int | None = 0
    doc_comment: int | None = 1

    # 文档模块配置
    default_homepage: Literal['blog', 'doc'] = "blog"
    default_docbook_id: Optional[int] = None
    doc_subdomain: Optional[str] = None

    # 消息推送配置
    message_push_method: Literal['websocket', 'polling'] = "websocket"
    polling_interval: int = 30

    # Footer 配置
    footer_config: Any | None = None

    # 注册配置
    enable_register: Literal[0, 1] = 1
    register_role: Literal['User', 'Contributor', 'Author'] = "User"

    # 文章审核通知配置
    enable_article_review_notification: Literal[0, 1] = 0
    article_review_notification_roles: Optional[str] = None  # JSON数组格式
