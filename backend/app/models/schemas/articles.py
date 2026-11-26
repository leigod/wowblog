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
    # 平台分类/系列：审核发布时由 Admin/Editor 选择；Author 提交时可空
    category_id: int | None = None
    series_id: int | None = None
    # 作者自己 blog 的分类/系列（wb_user_categories / wb_user_series 的 id）：
    # Author 在 Creator 工作台发布时选择，非必填，与平台维度互不影响
    blog_category_id: int | None = None
    blog_series_id: int | None = None
    # 个人 blog 内置顶/排序（仅影响 /blog/:username 展示顺序）
    blog_top: int | None = 0
    blog_sort: int | None = 0
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
    # 平台维度的排序权重（Admin 后台可编辑；与个人 blog 的 blog_sort 互不影响）
    sort: int | None = None
    updatetime: int | None = int(time.time())


class BlogArticleUpdateBlogMeta(BaseModel):
    """个人 blog 维度的置顶/排序（Author 在 Creator 工作台自行管理）。"""
    blog_top: int | None = None
    blog_sort: int | None = None


class BlogArticleUpdateSort(BaseModel):
    """平台维度的排序权重（Admin 后台编辑 wb_articles.sort）。"""
    sort: int


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
    # 首页编辑推荐区已展示的文章 id：下方列表排除，避免同一篇上下重复出现
    exclude_ids: list[int] = []


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
    # 平台排序权重（Admin 后台可编辑）
    sort: int | None = 0
    createtime: int | None = int(time.time())
    # 作者详细信息（用于管理后台显示）
    author_full_name: str | None = None
    author_username: str | None = None
    author_profile_image: str | None = None

    model_config = ConfigDict(from_attributes=True)


class SeriesProgress(BaseModel):
    """详情页「所属系列」卡片：文章在系列中的位置与跳转信息。

    source='site' → 平台系列，跳 /series/{slug}；
    source='blog' → 作者个人 blog 系列，跳 /blog/{username}/series/{slug}。
    """
    id: int
    name: str
    slug: str | None = None
    description: str | None = None
    index: int = 1
    total: int = 1
    source: Literal['site', 'blog'] = 'site'


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
    # 系列信息（平台系列，兼容旧版详情页顶部横条）
    series: Optional['BlogSeries'] = None
    # ---- 动态详情页布局相关 ----
    # 作者角色：Author/Admin/Contributor/...；供前端判断是否切换 blog 版布局
    author_role: str | None = None
    # 作者是否开通了个人 blog（wb_user_blogs 有行）
    blog_opened: bool = False
    # 平台系列的所属进度（source='site'，跳 /series/{slug}）
    series_progress: Optional[SeriesProgress] = None
    # 个人 blog 系列的所属进度（source='blog'，跳 /blog/{username}/series/{slug}）
    blog_series_progress: Optional[SeriesProgress] = None

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
