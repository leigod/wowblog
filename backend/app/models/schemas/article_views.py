"""
文章浏览记录相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional


class ArticleViewCreate(BaseModel):
    """创建浏览记录"""
    article_id: int = Field(..., description="文章ID")
    view_duration: int = Field(default=0, description="停留时长(秒)")
    ip_address: Optional[str] = Field(None, description="IP地址")
    user_agent: Optional[str] = Field(None, description="浏览器UA")
    device_type: Optional[str] = Field(None, description="设备类型")
    source: Optional[str] = Field(default="direct", description="来源")
    device_fingerprint: Optional[str] = Field(None, description="设备指纹")


class ArticleViewRecord(BaseModel):
    """浏览记录响应"""
    id: int
    article_id: int
    title: str
    slug: str
    cover: Optional[str] = None
    content: Optional[str] = None
    view_time: int
    view_duration: int
    is_deep_read: int
    author_full_name: Optional[str] = None
    author_username: Optional[str] = None
    author_profile_image: Optional[str] = None


class ArticleViewStats(BaseModel):
    """浏览统计响应"""
    total_views: int
    today_views: int
    unique_visitors: int
    deep_reads: int


class DailyViewStats(BaseModel):
    """每日浏览统计"""
    date: str
    views: int
    unique_visitors: int
    deep_reads: int


class TrendViewStats(BaseModel):
    """趋势浏览统计"""
    period: str  # 7days/30days
    daily_stats: list[DailyViewStats]
