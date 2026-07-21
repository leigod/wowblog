from pydantic import BaseModel
from datetime import datetime
from pydantic.config import ConfigDict
from typing import Optional, List, Literal
import time
from app.models.schemas.tags import BlogTag
from app.models.schemas.series import BlogSeries


class BlogArticleBase(BaseModel):
    title: str
    subtitle: str | None = None
    cover: str | None = None
    content: str
    author: int
    co_authors: str | None = None
    category_id: int
    series_id: int | None = None
    tags: str | None = None
    status: Literal['draft', 'published', 'scheduled', 'deleted'] = 'draft'
    pub_time: int | None = int(time.time())
    slug: str
    seo_title: str | None = None
    seo_desc: str | None = None
    og_image: str | None = None
    disable_comments: int | None = 0
    enable_table_content: int | None = 0
    model_config = ConfigDict(from_attributes=True)


class BlogArticleCreate(BlogArticleBase):
    is_pin: int | None = 0
    is_recommend: int | None = 0
    createtime: int | None = int(time.time())


class BlogArticleUpdate(BlogArticleBase):
    # 更新文章时不允许修改作者，将 author 设为可选字段
    author: int | None = None
    # is_pin: int | None = 0
    # is_recommend: int | None = 0
    updatetime: int | None = int(time.time())


class BlogArticleUpdateStatus(BaseModel):
    status: Literal['draft', 'published', 'scheduled', 'deleted'] = 'draft'


class BlogArticleUpdatePin(BaseModel):
    is_pin: int | None = 0


class BlogArticleUpdateRecommend(BaseModel):
    is_recommend: int | None = 0

class BlogArticleUpdateOpStatus(BaseModel):
    is_pin: int | None = 0
    is_recommend: int | None = 0
    is_featured: int | None = 0


class ArticleTimeSearch(BaseModel):
    op: Literal['>', '<', '>=', '<=', '=', 'between'] = '>='
    value: List[int] | int | None = None

class BlogArticleListRequest(BaseModel):
    keyword: str | None = None
    tags: str | List[int] | None = None
    authors: str | List[int] | None = None
    time: ArticleTimeSearch | None = None
    status: Literal['draft', 'published', 'scheduled', 'deleted'] | None = None


class HomeArticleListRequest(BaseModel):
    type: Literal['all', 'following', 'featured', 'recommend'] = 'all'
    uid: int | None = None


class ArticleStatData(BaseModel):
    article_id: int
    likes: int | None = 0
    comments: int | None = 0
    bookmarks: int | None = 0
    shares: int | None = 0
    views: int | None = 0

class ArticleStatDataUpdate(BaseModel):
    likes: int | None = 0
    comments: int | None = 0
    bookmarks: int | None = 0
    shares: int | None = 0
    views: int | None = 0


class BlogArticle(BlogArticleBase):
    id: int
    is_pin: int | None = 0
    is_recommend: int | None = 0
    is_featured: int | None = 0
    createtime: int | None = int(time.time())
    # 作者详细信息（用于管理后台显示）
    author_full_name: str | None = None
    author_username: str | None = None
    author_profile_image: str | None = None

    model_config = ConfigDict(from_attributes=True)


class BlogArticleResponse(BaseModel):
    # 文章基本信息
    article: BlogArticle
    # 用户信息
    username: str
    full_name: str
    profile_image: str | None = None
    # 标签列表（不再是字符串）
    tags: List[BlogTag] = []
    # 文章统计数据
    stat_data: ArticleStatData
    # 系列信息
    series: Optional['BlogSeries'] = None

    model_config = ConfigDict(from_attributes=True)


class RecentArticles(BaseModel):
    # 文章基本信息
    article: BlogArticle
    # 分类信息
    category_name: str
    category_slug: str
    
    model_config = ConfigDict(from_attributes=True)


class HotArticles(BaseModel):
    # 文章基本信息
    title: str
    slug: str
    # 用户信息
    username: str
    full_name: str
    # 文章阅读数
    views: int | None = 0
    
    model_config = ConfigDict(from_attributes=True)


class ArticlesListItem(BaseModel):
    # 文章基本信息
    title: str
    content: str | None = None
    cover: str | None = None
    slug: str
    is_recommend: int | None = 0
    is_pin: int | None = 0
    tags: str | None = ''
    pub_time: int | None = int(time.time())
    createtime: int | None = int(time.time())
    # 用户信息
    username: str
    full_name: str
    profile_image: str | None = ''
    # 文章阅读数
    views: int | None = 0
    likes: int | None = 0
    
    model_config = ConfigDict(from_attributes=True)
