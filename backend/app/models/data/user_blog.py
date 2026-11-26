"""Author 个人博客数据模型（Creator 工作台）。

与平台数据的归属关系：
- 站点级数据（wb_categories / wb_series / wb_navs / wb_config）只归平台（Admin）所有；
- 本文件四张表都带 user_id，是 Author 个人 blog 的私有数据；
- wb_articles 通过 blog_category_id / blog_series_id 关联本文件的分类与系列，
  与平台聚合用的 category_id / series_id 互不影响。
"""
from sqlalchemy import Column, Integer, String, Text, JSON
from app.database import Base
from datetime import datetime


def _now() -> int:
    return int(datetime.now().timestamp())


class UserBlogConfig(Base):
    """blog 主配置：每个 Author 一行（user_id 唯一）。"""
    __tablename__ = 'wb_user_blogs'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True, comment='博主用户ID（一人一行）')
    blog_name = Column(String(100), comment='blog名称（空则前台回退显示用户名）')
    blog_description = Column(String(300), comment='blog说明')
    impressum = Column(Text, comment='法律声明（blog页脚展示，部分司法辖区强制）')
    logo = Column(String(255), comment='blog logo（建议 500x125 4:1 透明 PNG）')
    favicon = Column(String(255), comment='blog favicon（建议 32x32/64x64 方形 PNG）')
    social_links = Column(JSON, comment='社媒账号列表：[{"platform":"github","url":"..."}]')
    homepage_layout = Column(String(20), default='magazine',
                             comment='首页布局风格: magazine/stacked/grid')
    # 图片水印（NULL=跟随全站 wb_config 设置，0/1=博客级显式覆盖）
    watermark_enabled = Column(Integer, nullable=True, comment='blog图片水印开关：NULL=跟随全站，0=关闭，1=开启')
    watermark_mode = Column(String(10), nullable=True, comment='水印样式：NULL=跟随全站，corner=右下角，tile=平铺')
    createtime = Column(Integer, default=_now, comment='开通时间戳（版权年份起点）')
    updatetime = Column(Integer, default=_now, onupdate=_now, comment='更新时间戳')


class UserCategory(Base):
    """blog 分类：仅一级、可排序，同用户内 slug 唯一。"""
    __tablename__ = 'wb_user_categories'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, comment='归属博主用户ID')
    name = Column(String(100), comment='分类名')
    slug = Column(String(50), comment='URL slug（同用户内唯一）')
    sort = Column(Integer, default=0)
    createtime = Column(Integer, default=_now)


class UserSeries(Base):
    """blog 系列：可排序，同用户内 slug 唯一。文章通过 wb_articles.blog_series_id 关联。"""
    __tablename__ = 'wb_user_series'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, comment='归属博主用户ID')
    name = Column(String(100), comment='系列名')
    description = Column(String(300), comment='系列说明')
    slug = Column(String(50), comment='URL slug（同用户内唯一）')
    sort = Column(Integer, default=0)
    createtime = Column(Integer, default=_now)


class UserNav(Base):
    """blog 导航：无系统默认项；类型仅 link / category / series。"""
    __tablename__ = 'wb_user_navs'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, comment='归属博主用户ID')
    label = Column(String(50), comment='导航标签')
    type = Column(String(20), comment="类型: link / category / series")
    value = Column(String(100), comment='link=URL；category/series=对应表ID')
    sort = Column(Integer, default=0)
    status = Column(Integer, default=1, comment='1=显示 0=隐藏')
    createtime = Column(Integer, default=_now)
