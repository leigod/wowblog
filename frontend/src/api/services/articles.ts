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
 * 获取文章列表
 * @param currentPage 当前页码
 * @param pageSize 每页数量
 * @param data 查询参数
 * @returns
 */
export const getManageArticlesList = (
  currentPage: number,
  pageSize: number,
  data: ArticleSearchParams
) => {
  return request({
    url: `/admin/articles/list?currentpage=${currentPage}&pagesize=${pageSize}`,
    method: 'POST',
    data
  })
}

/**
 * 获取不同状态文章总数
 * @returns
 */
export const getArticlesStatusCount = () => {
  return request({
    url: '/admin/articles/countbystatus',
    method: 'GET'
  })
}

/**
 * 添加文章
 * @param data
 * @returns
 */
export const addArticle = (data: any) => {
  return request({
    url: '/admin/articles/add',
    method: 'POST',
    data
  })
}

/**
 * 更新文章
 * @param id 文章ID
 * @param data 文章数据
 * @returns
 */
export const updateArticle = (id: string, data: any) => {
  return request({
    url: `/admin/articles/update/${id}`,
    method: 'POST',
    data
  })
}

/**
 * 读取自己文章的详情（前台通道，供编辑页回填）
 * 供 Author/Contributor 使用：/admin/articles/detail 仅 Admin 可用。
 * 后端校验只能读取本人文章（Admin 例外）。
 */
export const getMyArticleDetail = (id: string) => {
  return request({
    url: `/blog/articles/mydetail/${id}`,
    method: 'GET'
  })
}

/**
 * 更新自己的文章（前台通道）
 * 供 Author/Contributor 使用：/admin 通道仅 Admin 可用，作者保存会被拦截。
 * 后端校验只能编辑本人文章。
 */
export const updateMyArticle = (id: string, data: any) => {
  return request({
    url: `/blog/articles/update/${id}`,
    method: 'POST',
    data
  })
}

/**
 * 删除自己的文章（前台通道，作者本人校验）
 */
export const deleteMyArticle = (id: string) => {
  return request({
    url: `/blog/articles/delete/${id}`,
    method: 'DELETE'
  })
}

/**
 * 更新自己文章的状态（发布/取消发布，前台通道，作者本人校验）
 */
export const updateMyArticleStatus = (id: string, status: 'draft' | 'published' | 'scheduled' | 'deleted') => {
  return request({
    url: `/blog/articles/update_status/${id}`,
    method: 'POST',
    data: { status }
  })
}

/**
 * 更新自己文章的个人 blog 置顶/排序（仅影响 /blog/:username 展示顺序）
 */
export const updateMyArticleBlogMeta = (id: string | number, data: { blog_top?: number; blog_sort?: number }) => {
  return request({
    url: `/blog/articles/update_blog_meta/${id}`,
    method: 'POST',
    data
  })
}

/**
 * 更新文章运营状态
 * @param id 文章ID
 * @param data 文章运营状态数据is_pin,is_recommend,is_featured
 * @returns
 */
export const updateArticleOpStatus = (id: string, data: any) => {
  return request({
    url: `/admin/articles/update/op_status/${id}`,
    method: 'POST',
    data
  })
}

/**
 * 获取管理文章详情
 * @param id 文章ID
 * @returns
 */
export const getArticleDetail = (id: string) => {
  return request({
    url: `/admin/articles/detail/${id}`,
    method: 'GET'
  })
}

/**
 * 获取文章作者列表
 * @param keyword 作者姓名或用户名关键词
 * @returns
 */
export const getArticleAuthorsList = (keyword: string = '') => {
  if (!keyword) {
    return request({
      url: `/admin/articles/authors/list`,
      method: 'GET'
    })
  }
  return request({
    url: `/admin/articles/authors/list?keyword=${keyword}`,
    method: 'GET'
  })
}

/**
 * 获取文章标签列表
 * @param keyword 标签关键词
 * @returns
 */
export const getArticleTagsList = (keyword: string = '') => {
  if (!keyword) {
    return request({
      url: `/admin/articles/tags/list`,
      method: 'GET'
    })
  }
  return request({
    url: `/admin/articles/tags/list?keyword=${keyword}`,
    method: 'GET'
  })
}

/**
 * 删除文章（物理删除）
 * @param id 文章ID
 * @returns
 */
export const deleteArticle = (id: string) => {
  return request({
    url: `/admin/articles/delete/${id}`,
    method: 'DELETE'
  })
}

/**
 * 更新文章状态
 * @param id 文章ID
 * @param status 新状态
 * @returns
 */
/**
 * 更新文章平台排序权重（Admin 后台，仅更新 wb_articles.sort 一个字段）
 */
export const updateArticleSort = (id: string | number, sort: number) => {
  return request({
    url: `/admin/articles/update/sort/${id}`,
    method: 'POST',
    data: { sort }
  })
}

export const updateArticleStatus = (id: string, status: 'draft' | 'published' | 'scheduled' | 'deleted') => {
  return request({
    url: `/admin/articles/update/status/${id}`,
    method: 'POST',
    data: { status }
  })
}

/**
 * 根据用户名获取用户文章列表
 * @param username 用户名
 * @param limit 返回数量限制
 * @param status 文章状态过滤
 * @param offset 偏移量（分页用）
 * @returns
 */
export const getUserArticles = (
  username: string,
  limit?: number,
  status?: string | null,
  offset?: number
) => {
  const limitNum = limit ?? 10
  let url = `/blog/articles/user/${username}?limit=${limitNum}`
  if (status) {
    url += `&status=${status}`
  }
  if (typeof offset === 'number' && offset > 0) {
    url += `&offset=${offset}`
  }
  return request({
    url,
    method: 'GET'
  })
}

/**
 * 获取用户文章总数
 * @param username 用户名
 * @returns
 */
export const getUserArticleCount = (username: string) => {
  return request({
    url: `/blog/articles/user/${username}/count`,
    method: 'GET'
  })
}

/**
 * 创建文章（公开接口，供Author和Contributor使用）
 * @param data 文章数据
 * @returns
 */
export const createArticle = (data: any) => {
  return request({
    url: '/blog/articles/create',
    method: 'POST',
    data
  })
}

/**
 * 搜索结果文章接口定义
 */
export interface SearchResultArticle {
  id: number
  title: string
  slug: string
  subtitle: string | null
  cover: string | null
  content: string
  tags: string | null
  pub_time: number
  createtime: number
  author_full_name: string
  author_username: string
  author_profile_image: string | null
  reads: number
  likes: number
}

/**
 * 搜索结果响应接口定义
 * API返回格式: { code: 1, data: { list: [], total: 0 } }
 */
export interface SearchResponseData {
  list: SearchResultArticle[]
  total: number
  page: number
  pageSize: number
  keyword: string
}

export interface SearchResponse {
  code: number
  msg: string
  data: SearchResponseData
}

/**
 * 全站文章搜索
 * @param keyword 搜索关键词
 * @param currentPage 当前页码
 * @param pageSize 每页数量
 * @returns Promise<SearchResponse>
 */
export const searchArticles = (
  keyword: string,
  currentPage: number = 1,
  pageSize: number = 10
): Promise<SearchResponse> => {
  return request({
    url: `/blog/articles/search?keyword=${encodeURIComponent(keyword)}&currentpage=${currentPage}&pagesize=${pageSize}`,
    method: 'GET'
  })
}

/**
 * 推荐文章接口定义
 */
export interface RecommendArticle {
  id: number
  title: string
  slug: string
  cover: string | null
  summary: string
  author_name: string
  author_avatar: string | null
  author_username: string
  pub_time: number
  views: number
  tags: string | null
  reason: string
  score: number
}

/**
 * 推荐文章响应接口定义
 */
export interface RecommendResponse {
  code: number
  msg: string
  data: {
    list: RecommendArticle[]
    total: number
  }
}

/**
 * 获取推荐文章
 * @param articleId 当前文章ID
 * @param limit 返回数量，默认3
 * @param offset 偏移量，用于换一批，默认0
 * @returns Promise<RecommendArticle[]>
 */
export const getRecommendArticles = (
  articleId: number,
  limit: number = 3,
  offset: number = 0
): Promise<RecommendResponse> => {
  return request({
    url: `/blog/articles/${articleId}/recommend?limit=${limit}&offset=${offset}`,
    method: 'GET'
  })
}

/**
 * 获取统计数据
 * @returns Promise<any>
 */
export const getStatistics = () => {
  return request({
    url: '/blog/articles/statistics',
    method: 'GET'
  })
}

/**
 * 获取TOP文章
 * @param type 类型：views(浏览量)、likes(点赞数)、comments(评论数)
 * @param limit 返回数量，默认10
 * @returns Promise<any>
 */
export const getTopArticles = (type: 'views' | 'likes' | 'comments' = 'views', limit: number = 10) => {
  return request({
    url: `/blog/articles/top?type=${type}&limit=${limit}`,
    method: 'GET'
  })
}

/**
 * 获取浏览量趋势数据
 * @param days 天数：7、30、90
 * @returns Promise<any>
 */
export const getViewTrend = (days: 7 | 30 | 90 = 7) => {
  return request({
    url: `/blog/articles/trend?days=${days}`,
    method: 'GET'
  })
}

/**
 * 草稿文章预览（仅限 Admin 和 Editor）
 * @param articleId 文章ID
 * @returns Promise<any>
 */
export const previewDraftArticle = (articleId: string) => {
  return request({
    url: `/blog/articles/preview/${articleId}`,
    method: 'GET'
  })
}


