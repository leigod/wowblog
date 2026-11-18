import { request } from '../http'

/**
 * Author 个人博客（Creator 工作台）API。
 * 后端 /api/creator/*，整组仅 Admin/Author 可访问，数据按当前登录用户隔离。
 */

// ---------- 类型 ----------

export interface UserBlogConfig {
  id: number
  user_id: number
  blog_name: string | null
  blog_description: string | null
  impressum: string | null
  logo: string | null
  favicon: string | null
  social_links: { platform: string; url: string }[] | null
  homepage_layout: 'magazine' | 'stacked' | 'grid'
  createtime: number
  updatetime: number
}

export type BlogLayout = 'magazine' | 'stacked' | 'grid'

export interface UserBlogCategory {
  id: number
  user_id: number
  name: string
  slug: string
  sort: number
  createtime: number
}

export interface UserBlogSeries {
  id: number
  user_id: number
  name: string
  description: string | null
  slug: string
  sort: number
  createtime: number
}

export interface UserBlogNav {
  id: number
  user_id: number
  label: string
  type: 'link' | 'category' | 'series'
  value: string
  sort: number
  status: number
  createtime: number
}

// ---------- blog 配置 ----------

/**
 * 个人博客首页公开配置包（/blog/:username 页面数据）：blog 配置 + 导航 + 分类 + 系列。
 * 无需登录；未开通（无 wb_user_blogs 行）时 data.blog.opened=false。
 */
export const getBlogSite = (username: string) => {
  return request({
    url: `/blog/site/${username}`,
    method: 'GET'
  })
}

/**
 * 某博主已发布文章列表（公开；/blog/:username 焦点区与卡片列表共用）。
 * @param offset 「加载更多」偏移
 * @param blogCat / blog_series 博客维度聚合过滤（wb_user_categories / wb_user_series 的 id）
 */
export const getBlogArticles = (
  username: string,
  params: { limit?: number; offset?: number; blogCat?: number; blogSeries?: number } = {}
) => {
  const q = new URLSearchParams()
  q.set('status', 'published')
  q.set('limit', String(params.limit ?? 6))
  if (params.offset) q.set('offset', String(params.offset))
  if (params.blogCat) q.set('blog_cat', String(params.blogCat))
  if (params.blogSeries) q.set('blog_series', String(params.blogSeries))
  return request({
    url: `/blog/articles/user/${username}?${q.toString()}`,
    method: 'GET'
  })
}

/**
 * 公开：某博主的单个 blog 系列详情（按 slug）。用于 /blog/:username/series/:slug 页面。
 */
export const getPublicBlogSeries = (username: string, seriesSlug: string) => {
  return request({
    url: `/blog/site/${encodeURIComponent(username)}/series/${encodeURIComponent(seriesSlug)}`,
    method: 'GET'
  })
}

/**
 * 公开：某博主 blog 系列下的已发布文章列表（按系列 slug）。
 */
export const getPublicBlogSeriesArticles = (
  username: string,
  seriesSlug: string,
  params: { page?: number; pageSize?: number } = {}
) => {
  const q = new URLSearchParams()
  q.set('currentpage', String(params.page ?? 1))
  q.set('pagesize', String(params.pageSize ?? 10))
  return request({
    url: `/blog/site/${encodeURIComponent(username)}/series/${encodeURIComponent(seriesSlug)}/articles?${q.toString()}`,
    method: 'GET'
  })
}

/**
 * 公开：某博主的单个 blog 分类详情（按 slug）。用于 /blog/:username/category/:slug 页面。
 */
export const getPublicBlogCategory = (username: string, categorySlug: string) => {
  return request({
    url: `/blog/site/${encodeURIComponent(username)}/category/${encodeURIComponent(categorySlug)}`,
    method: 'GET'
  })
}

/**
 * 公开：某博主 blog 分类下的已发布文章列表（按分类 slug）。
 */
export const getPublicBlogCategoryArticles = (
  username: string,
  categorySlug: string,
  params: { page?: number; pageSize?: number } = {}
) => {
  const q = new URLSearchParams()
  q.set('currentpage', String(params.page ?? 1))
  q.set('pagesize', String(params.pageSize ?? 10))
  return request({
    url: `/blog/site/${encodeURIComponent(username)}/category/${encodeURIComponent(categorySlug)}/articles?${q.toString()}`,
    method: 'GET'
  })
}

export const getBlogConfig = () => {
  return request({
    url: '/creator/blog/config',
    method: 'GET'
  })
}

export const updateBlogConfig = (
  data: Partial<Pick<UserBlogConfig,
    'blog_name' | 'blog_description' | 'impressum' | 'logo' | 'favicon' | 'social_links' | 'homepage_layout'>>
) => {
  return request({
    url: '/creator/blog/config',
    method: 'PUT',
    data
  })
}

// ---------- 分类 ----------

export const getUserCategories = () => {
  return request({ url: '/creator/categories', method: 'GET' })
}

export const createUserCategory = (data: { name: string; slug?: string; sort?: number }) => {
  return request({ url: '/creator/categories', method: 'POST', data })
}

export const updateUserCategory = (
  id: number,
  data: Partial<{ name: string; slug: string; sort: number }>
) => {
  return request({ url: `/creator/categories/${id}`, method: 'PUT', data })
}

export const deleteUserCategory = (id: number) => {
  return request({ url: `/creator/categories/${id}`, method: 'DELETE' })
}

export const sortUserCategories = (ids: number[]) => {
  return request({ url: '/creator/categories/sortbatch', method: 'POST', data: { ids } })
}

// ---------- 系列 ----------

export const getUserSeriesList = () => {
  return request({ url: '/creator/series', method: 'GET' })
}

export const createUserSeries = (data: { name: string; description?: string; slug?: string; sort?: number }) => {
  return request({ url: '/creator/series', method: 'POST', data })
}

export const updateUserSeries = (
  id: number,
  data: Partial<{ name: string; description: string; slug: string; sort: number }>
) => {
  return request({ url: `/creator/series/${id}`, method: 'PUT', data })
}

export const deleteUserSeries = (id: number) => {
  return request({ url: `/creator/series/${id}`, method: 'DELETE' })
}

export const sortUserSeries = (ids: number[]) => {
  return request({ url: '/creator/series/sortbatch', method: 'POST', data: { ids } })
}

// ---------- 导航 ----------

export const getUserNavs = () => {
  return request({ url: '/creator/navs', method: 'GET' })
}

export const createUserNav = (data: {
  label: string
  type: 'link' | 'category' | 'series'
  value: string
  sort?: number
  status?: number
}) => {
  return request({ url: '/creator/navs', method: 'POST', data })
}

export const updateUserNav = (
  id: number,
  data: Partial<{ label: string; type: 'link' | 'category' | 'series'; value: string; sort: number; status: number }>
) => {
  return request({ url: `/creator/navs/${id}`, method: 'PUT', data })
}

export const deleteUserNav = (id: number) => {
  return request({ url: `/creator/navs/${id}`, method: 'DELETE' })
}

export const sortUserNavs = (ids: number[]) => {
  return request({ url: '/creator/navs/sortbatch', method: 'POST', data: { ids } })
}
