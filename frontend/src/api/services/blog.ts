import { request } from '../http'

/**
 * 文章查询筛选条件接口定义
 */
export interface ArticleSearchParams {
  keyword?: string | null
  authors?: string | number[] | null
  tags?: string | number[] | null
  time?: ArticleTimeSearchParams | null
  status?: 'draft' | 'published' | 'scheduled' | 'deleted' | null
}

/**
 * 文章列表查询时间筛选条件接口定义
 */
export interface ArticleTimeSearchParams {
  op?: '>' | '<' | '=' | 'between'
  value?: (number | string)[]
}

/**
 * 首页文章列表查询条件接口定义
 */
export interface HomeArticleSearchParams {
  type: 'all' | 'featured' | 'following' | 'recommend'
  uid?: number
}

/**
 * 评论接口定义
 */
export interface Comment {
  article_id: number
  type: 'subject' | 'reply'
  subject_id?: number
  comment: string
}

/**
 * 获取博客详情
 * @param slug 博客ID
 * @returns
 */
export const getBlogDetail = (slug: string) => {
  return request({
    url: `/blog/articles/detail/${slug}`,
    method: 'GET'
  })
}

/**
 * 获取博客文章列表
 * @param currentPage 当前页码
 * @param pageSize 每页数量
 * @param data 查询参数
 * @returns
 */
export const getBlogList = (
  currentpage: number,
  pagesize: number,
  data: HomeArticleSearchParams
) => {
  return request({
    url: `/blog/articles/list?currentpage=${currentpage}&pagesize=${pagesize}`,
    method: 'POST',
    data
  })
}

/**
 * 获取博客文章标签列表
 * @param data 标签ID列表
 * @returns
 */
export const getBlogTagsList = (data: string[]) => {
  return request({
    url: `/blog/articles/item/tags`,
    method: 'POST',
    data
  })
}

/**
 * 获取博客文章统计数据
 * @param article_ids 文章ID列表
 * @returns
 */
export const getBlogStats = (article_ids: string[]) => {
  return request({
    url: `/blog/articles/stat?article_ids=${article_ids.join(',')}`,
    method: 'GET'
  })
}

/**
 * 获取最近更新文章
 * @param limit 文章数量
 * @returns
 */
export const getRecentBlog = (limit: number = 7) => {
  if (limit <= 0) {
    limit = 7
  }
  if (limit > 20) {
    limit = 20
  }
  return request({
    url: `/blog/articles/recent?limit=${limit}`,
    method: 'GET'
  })
}

/**
 * 获取热门标签列表
 */
export const getHotTagsList = (limit: number = 15) => {
  if (limit <= 0) {
    limit = 15
  }
  if (limit > 30) {
    limit = 30
  }
  return request({
    url: `/blog/tags/hot?limit=${limit}`,
    method: 'GET'
  })
}

/**
 * 获取热门文章列表
 * @param limit 文章数量
 * @param days 时间范围（天）
 * @returns
 */
export const getHotArticlesList = (limit: number = 15, days: number = 7) => {
  if (limit <= 0) {
    limit = 15
  }
  if (limit > 30) {
    limit = 30
  }
  if (days <= 0) {
    days = 7
  }
  if (days > 30) {
    days = 30
  }
  return request({
    url: `/blog/articles/hot?limit=${limit}&days=${days}`,
    method: 'GET'
  })
}

/**
 * 获取标签文章列表页信息
 * @param slug 标签ID
 * @returns
 */
export const getTagPageInfo = (slug: string) => {
  return request({
    url: `/blog/tags/detail/${slug}`,
    method: 'GET'
  })
}

/**
 * 获取标签文章列表
 * @param tag_id 标签ID
 * @param currentpage 当前页码
 * @param pagesize 每页数量
 * @param type 查询参数hot、new
 * @returns
 */
export const getTagArticlesList = (
  tag_id: number,
  currentpage: number,
  pagesize: number,
  type: 'hot' | 'new'
) => {
  return request({
    url: `/blog/tags/articles/${tag_id}?currentpage=${currentpage}&pagesize=${pagesize}&type=${type}`,
    method: 'GET'
  })
}

/**
 * 关注标签
 * @param tag_id 标签ID
 * @returns
 */
export const followTagApi = (tag_id: number) => {
  return request({
    url: `/blog/tags/follow/${tag_id}`,
    method: 'POST'
  })
}

/**
 * 取消关注标签
 * @param tag_id 标签ID
 * @returns
 */
export const unfollowTagApi = (tag_id: number) => {
  return request({
    url: `/blog/tags/unfollow/${tag_id}`,
    method: 'POST'
  })
}

/**
 * 检查用户是否已关注该标签
 * @param tag_id 标签ID
 * @returns
 */
export const checkFollowTagApi = (tag_id: number) => {
  return request({
    url: `/blog/tags/followstatus/${tag_id}`,
    method: 'GET'
  })
}

/**
 * 收藏文章
 * @param article_id 文章ID
 * @returns
 */
export const bookmarkArticleApi = (article_id: number) => {
  return request({
    url: `/blog/articles/bookmark/${article_id}`,
    method: 'POST'
  })
}

/**
 * 取消收藏文章
 * @param article_id 文章ID
 * @returns
 */
export const unbookmarkArticleApi = (article_id: number) => {
  return request({
    url: `/blog/articles/unbookmark/${article_id}`,
    method: 'POST'
  })
}

/**
 * 检查用户是否已收藏该文章
 * @param article_id 文章ID
 * @returns
 */
export const checkBookmarkArticleApi = (article_id: number) => {
  return request({
    url: `/blog/articles/bookmarkstatus/${article_id}`,
    method: 'GET'
  })
}

/**
 * 批量获取文章列表用户收藏状态
 * @param article_ids 文章ID列表
 * @returns
 */
export const batchCheckBookmarkArticleApi = (article_ids: number[]) => {
  return request({
    url: `/blog/articles/batch/bookmarkstatus?article_ids=${article_ids.join(',')}`,
    method: 'GET'
  })
}

/**
 * 获取用户收藏文章列表
 * @param currentpage 当前页码
 * @param pagesize 每页数量
 * @returns
 */
export const getUserBookmarks = (currentpage: number = 1, pagesize: number = 10) => {
  return request({
    url: `/blog/articles/user/bookmarks?currentpage=${currentpage}&pagesize=${pagesize}`,
    method: 'GET'
  })
}

/**
 * 获取文章评论/回复列表
 * @param article_id 文章ID
 * @param type 评论类型，文章评论subject，回复评论reply
   @param subject_id 文章评论ID，当type为reply时必填，为评论的ID
   @param order 排序方式，top按点赞数排序，new按创建时间排序
 * @param currentpage 当前页码
 * @param pagesize 每页数量
 * @returns
 */
export const getBlogCommentsList = (
  article_id: number,
  type: 'subject' | 'reply' = 'subject',
  subject_id?: number,
  order: 'top' | 'new' = 'top',
  currentpage: number = 1,
  pagesize: number = 10
) => {
  return request({
    url: `/blog/articles/comments/list?article_id=${article_id}&type=${type}${subject_id ? `&subject_id=${subject_id}` : ''}${order ? `&order=${order}` : 'top'}&currentpage=${currentpage}&pagesize=${pagesize}`,
    method: 'GET'
  })
}

/**
 * 创建评论/回复
 * @param comment
 * @returns
 */
export const createBlogCommentApi = (comment: Comment) => {
  return request({
    url: `/blog/articles/comments/create`,
    method: 'POST',
    data: comment
  })
}

/**
 * 更新文章点赞数
 * @param article_id 文章ID
 * @returns
 */
export const likeArticleApi = (article_id: number) => {
  return request({
    url: `/blog/articles/item/updatestat/${article_id}`,
    method: 'POST',
    data: {
      likes: 1
    }
  })
}

/**
 * 点赞文章
 * @param article_id 文章ID
 * @returns
 */
export const addLikeArticleApi = (article_id: number) => {
  return request({
    url: `/blog/articles/like/${article_id}`,
    method: 'POST'
  })
}

/**
 * 取消点赞文章
 * @param article_id 文章ID
 * @returns
 */
export const unlikeArticleApi = (article_id: number) => {
  return request({
    url: `/blog/articles/unlike/${article_id}`,
    method: 'POST'
  })
}

/**
 * 检查用户是否已点赞该文章
 * @param article_id 文章ID
 * @returns
 */
export const checkLikeArticleApi = (article_id: number) => {
  return request({
    url: `/blog/articles/likestatus/${article_id}`,
    method: 'GET'
  })
}

/**
 * 更新文章阅读时长
 * @param article_id 文章ID
 * @param view_duration 阅读时长（秒）
 * @returns
 */
export const updateViewDurationApi = (article_id: number, view_duration: number) => {
  return request({
    url: `/blog/articles/view/duration?article_id=${article_id}&view_duration=${view_duration}`,
    method: 'POST'
  })
}

/**
 * 根据slug获取page详情
 * @param slug page slug
 * @returns
 */
export const getPageDetailApi = (slug: string) => {
  return request({
    url: `/blog/page/${slug}`,
    method: 'GET'
  })
}

/**
 * 根据slug获取series详情
 * @param slug series slug
 * @returns
 */
export const getSeriesDetailApi = (slug: string) => {
  return request({
    url: `/blog/series/${slug}`,
    method: 'GET'
  })
}

/**
 * 根据slug获取series下的文章列表
 * @param slug series slug
 * @param currentpage 当前页码
 * @param pagesize 每页数量
 * @returns
 */
export const getSeriesArticlesList = (
  slug: string,
  currentpage: number = 1,
  pagesize: number = 10
) => {
  return request({
    url: `/blog/series/${slug}/articles?currentpage=${currentpage}&pagesize=${pagesize}`,
    method: 'GET'
  })
}

/**
 * 根据slug获取category详情
 * @param slug category slug
 * @returns
 */
export const getCategoryDetailApi = (slug: string) => {
  return request({
    url: `/blog/category/${slug}`,
    method: 'GET'
  })
}

/**
 * 根据slug获取category下的文章列表
 * @param slug category slug
 * @param currentpage 当前页码
 * @param pagesize 每页数量
 * @returns
 */
export const getCategoryArticlesList = (
  slug: string,
  currentpage: number = 1,
  pagesize: number = 10
) => {
  return request({
    url: `/blog/category/${slug}/articles?currentpage=${currentpage}&pagesize=${pagesize}`,
    method: 'GET'
  })
}

/**
 * 获取用户阅读历史列表
 * @param currentpage 当前页码
 * @param pagesize 每页数量
 * @returns
 */
export const getUserReadingHistory = (currentpage: number = 1, pagesize: number = 20) => {
  return request({
    url: `/blog/articles/user/history?currentpage=${currentpage}&pagesize=${pagesize}`,
    method: 'GET'
  })
}

/**
 * 清空用户阅读历史
 * @returns
 */
export const clearReadingHistory = () => {
  return request({
    url: `/blog/articles/user/history`,
    method: 'DELETE'
  })
}

/**
 * 删除单条阅读历史
 * @param record_id 记录ID
 * @returns
 */
export const deleteReadingHistoryRecord = (record_id: number) => {
  return request({
    url: `/blog/articles/user/history/${record_id}`,
    method: 'DELETE'
  })
}

/**
 * 获取今日浏览统计
 * @returns
 */
export const getTodayViewStats = () => {
  return request({
    url: `/blog/stats/views/today`,
    method: 'GET'
  })
}

/**
 * 获取总浏览统计
 * @returns
 */
export const getTotalViewStats = () => {
  return request({
    url: `/blog/stats/views/total`,
    method: 'GET'
  })
}

/**
 * 获取浏览趋势
 * @param days 天数 (7/30/90)
 * @returns
 */
export const getViewTrend = (days: number = 7) => {
  return request({
    url: `/blog/stats/views/trend?days=${days}`,
    method: 'GET'
  })
}

/**
 * 获取本周活跃评论者
 * @param limit 数量限制，默认5
 * @returns
 */
export const getTopCommenters = (limit: number = 5) => {
  if (limit <= 0) {
    limit = 5
  }
  if (limit > 20) {
    limit = 20
  }
  return request({
    url: `/blog/comments/top-commenters?limit=${limit}`,
    method: 'GET'
  })
}

/**
 * 活跃评论者接口定义
 */
export interface TopCommenter {
  id: number
  username: string
  full_name: string
  avatar: string
  comment_count: number
}
