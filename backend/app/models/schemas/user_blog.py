"""Author 个人博客（Creator 工作台）的请求/响应模型。"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Literal
import time


# ---------- blog 配置 ----------

class UserBlogConfigUpdate(BaseModel):
    """配置更新：部分字段提交（exclude_unset 落地），user_id 不可改。"""
    blog_name: Optional[str] = Field(None, max_length=100)
    blog_description: Optional[str] = Field(None, max_length=300)
    impressum: Optional[str] = None
    logo: Optional[str] = Field(None, max_length=255)
    favicon: Optional[str] = Field(None, max_length=255)
    social_links: Optional[List[dict]] = None
    homepage_layout: Optional[Literal['magazine', 'stacked', 'grid']] = None
    # 图片水印：None=跟随全站（不提交/显式置 null），0/1=博客级覆盖
    watermark_enabled: Optional[Literal[0, 1]] = None
    watermark_mode: Optional[Literal['corner', 'tile']] = None


class UserBlogConfig(UserBlogConfigUpdate):
    id: int
    user_id: int
    createtime: int
    updatetime: int
    model_config = ConfigDict(from_attributes=True)


# ---------- blog 分类 ----------

class UserCategoryCreate(BaseModel):
    name: str = Field(max_length=100)
    slug: Optional[str] = Field(None, max_length=50, description='URL slug，同用户内唯一；留空按名称自动生成')
    sort: int = 0


class UserCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    slug: Optional[str] = Field(None, max_length=50)
    sort: Optional[int] = None


class UserCategory(UserCategoryCreate):
    id: int
    user_id: int
    createtime: int
    model_config = ConfigDict(from_attributes=True)


# ---------- blog 系列 ----------

class UserSeriesCreate(BaseModel):
    name: str = Field(max_length=100)
    description: Optional[str] = Field(None, max_length=300)
    slug: Optional[str] = Field(None, max_length=50, description='URL slug，同用户内唯一；留空按名称自动生成')
    sort: int = 0


class UserSeriesUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=300)
    slug: Optional[str] = Field(None, max_length=50)
    sort: Optional[int] = None


class UserSeries(UserSeriesCreate):
    id: int
    user_id: int
    createtime: int
    model_config = ConfigDict(from_attributes=True)


# ---------- blog 导航 ----------

class UserNavCreate(BaseModel):
    label: str = Field(max_length=50)
    type: Literal['link', 'category', 'series']
    value: str = Field(max_length=100, description='link=URL；category/series=对应表ID')
    sort: int = 0
    status: int = 1


class UserNavUpdate(BaseModel):
    label: Optional[str] = Field(None, max_length=50)
    type: Optional[Literal['link', 'category', 'series']] = None
    value: Optional[str] = Field(None, max_length=100)
    sort: Optional[int] = None
    status: Optional[int] = None


class UserNav(UserNavCreate):
    id: int
    user_id: int
    createtime: int
    model_config = ConfigDict(from_attributes=True)


class SortBatchRequest(BaseModel):
    """批量排序：ids 按新顺序排列，索引即新 sort 值。"""
    ids: List[int]
