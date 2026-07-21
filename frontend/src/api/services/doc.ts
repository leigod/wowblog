/**
 * 文档模块 API 服务
 */
import { request } from '../http'
import type { ApiResponse } from '../types'

// ==================== 类型定义 ====================

export interface DocBook {
  id: number
  name: string
  slug: string
  description?: string
  cover?: string
  icon?: string
  is_public: boolean
  show_sidebar: boolean
  allow_comment: boolean
  allow_search: boolean
  theme: string
  home_doc_id?: number
  sort_order: number
  author_id: number
  author_name?: string
  doc_count: number
  createtime: number
  updatetime: number
}

export interface DocBookCreate {
  name: string
  slug: string
  description?: string
  cover?: string
  icon?: string
  is_public?: boolean
  show_sidebar?: boolean
  allow_comment?: boolean
  allow_search?: boolean
  theme?: string
  home_doc_id?: number
  sort_order?: number
}

export interface DocBookUpdate {
  name?: string
  slug?: string
  description?: string
  cover?: string
  icon?: string
  is_public?: boolean
  show_sidebar?: boolean
  allow_comment?: boolean
  allow_search?: boolean
  theme?: string
  home_doc_id?: number
  sort_order?: number
}

export type DocStatus = 'draft' | 'published' | 'hidden'

export interface Doc {
  id: number
  docbook_id: number
  title: string
  slug: string
  content?: string
  excerpt?: string
  parent_id: number
  level: number
  path: string
  sort_order: number
  status: DocStatus
  author_id: number
  author_name?: string
  createtime: number
  updatetime: number
  pubtime?: number
  view_count: number
  comment_count: number
  children?: Doc[]
}

export interface DocCreate {
  docbook_id: number
  title: string
  slug: string
  content?: string
  excerpt?: string
  parent_id?: number
  sort_order?: number
  status?: DocStatus
}

export interface DocUpdate {
  title?: string
  slug?: string
  content?: string
  excerpt?: string
  parent_id?: number
  sort_order?: number
  status?: DocStatus
}

export interface DocTreeNode {
  id: number
  title: string
  slug: string
  level: number
  parent_id: number
  sort_order: number
  status: string
  children: DocTreeNode[]
}

export interface DocNavigation {
  prev?: Doc
  next?: Doc
  parent?: Doc
  breadcrumbs: Doc[]
}

export interface DocListParams {
  docbook_id: number
  skip?: number
  limit?: number
  keyword?: string
  status?: DocStatus
}

export interface DocBookListParams {
  skip?: number
  limit?: number
  keyword?: string
}

// ==================== DocBook API ====================

export const docBookApi = {
  // 获取文档书列表
  list: (params: DocBookListParams = {}) => {
    return request<ApiResponse<DocBook[]>>({
      url: '/docbooks',
      method: 'get',
      params
    })
  },

  // 获取文档书总数
  count: (keyword: string = '') => {
    return request<ApiResponse<{ total: number }>>({
      url: '/docbooks/count',
      method: 'get',
      params: { keyword }
    })
  },

  // 获取文档书详情
  getById: (id: number) => {
    return request<ApiResponse<DocBook>>({
      url: `/docbooks/${id}`,
      method: 'get'
    })
  },

  // 通过slug获取文档书
  getBySlug: (slug: string) => {
    return request<ApiResponse<DocBook>>({
      url: `/docbooks/slug/${slug}`,
      method: 'get'
    })
  },

  // 创建文档书
  create: (data: DocBookCreate) => {
    return request<ApiResponse<DocBook>>({
      url: '/docbooks',
      method: 'post',
      data
    })
  },

  // 更新文档书
  update: (id: number, data: DocBookUpdate) => {
    return request<ApiResponse<DocBook>>({
      url: `/docbooks/${id}`,
      method: 'put',
      data
    })
  },

  // 删除文档书
  delete: (id: number) => {
    return request({
      url: `/docbooks/${id}`,
      method: 'delete'
    })
  }
}

// ==================== Doc API ====================

export const docApi = {
  // 获取文档列表
  list: (params: DocListParams) => {
    return request<ApiResponse<Doc[]>>({
      url: '/docs',
      method: 'get',
      params
    })
  },

  // 获取文档总数
  count: (params: Pick<DocListParams, 'docbook_id' | 'keyword' | 'status'>) => {
    return request<ApiResponse<{ total: number }>>({
      url: '/docs/count',
      method: 'get',
      params
    })
  },

  // 获取文档树
  getTree: (docbook_id: number, include_draft: boolean = false) => {
    return request<ApiResponse<DocTreeNode[]>>({
      url: '/docs/tree',
      method: 'get',
      params: { docbook_id, include_draft }
    })
  },

  // 搜索文档
  search: (docbook_id: number, keyword: string, limit: number = 20) => {
    return request<ApiResponse<Doc[]>>({
      url: '/docs/search',
      method: 'get',
      params: { docbook_id, keyword, limit }
    })
  },

  // 获取文档详情
  getById: (id: number) => {
    return request<ApiResponse<Doc>>({
      url: `/docs/${id}`,
      method: 'get'
    })
  },

  // 通过slug获取文档
  getBySlug: (slug: string, docbook_id: number) => {
    return request<ApiResponse<Doc>>({
      url: `/docs/slug/${slug}`,
      method: 'get',
      params: { docbook_id }
    })
  },

  // 获取文档导航
  getNavigation: (id: number) => {
    return request<ApiResponse<DocNavigation>>({
      url: `/docs/${id}/navigation`,
      method: 'get'
    })
  },

  // 获取子文档
  getChildren: (id: number, status?: DocStatus) => {
    return request<ApiResponse<Doc[]>>({
      url: `/docs/${id}/children`,
      method: 'get',
      params: status ? { status } : undefined
    })
  },

  // 创建文档
  create: (data: DocCreate) => {
    return request<ApiResponse<Doc>>({
      url: '/docs',
      method: 'post',
      data
    })
  },

  // 更新文档
  update: (id: number, data: DocUpdate) => {
    return request<ApiResponse<Doc>>({
      url: `/docs/${id}`,
      method: 'put',
      data
    })
  },

  // 删除文档
  delete: (id: number) => {
    return request({
      url: `/docs/${id}`,
      method: 'delete'
    })
  },

  // 移动文档
  move: (id: number, new_parent_id: number, new_sort_order: number) => {
    return request<ApiResponse<Doc>>({
      url: `/docs/${id}/move`,
      method: 'post',
      params: { new_parent_id, new_sort_order }
    })
  }
}

// ==================== Doc Comment API ====================

// 评论接口定义
export interface DocComment {
  doc_id: number
  type: 'subject' | 'reply'
  subject_id?: number
  comment: string
}

export const docCommentApi = {
  // 获取文档评论列表
  getList: (
    doc_id: number,
    type: 'subject' | 'reply' = 'subject',
    subject_id?: number,
    order: 'top' | 'new' = 'top',
    currentpage: number = 1,
    pagesize: number = 10
  ) => {
    return request({
      url: `/docs/${doc_id}/comments`,
      method: 'get',
      params: {
        doc_id,
        type,
        subject_id: subject_id || 0,
        order,
        currentpage,
        pagesize
      }
    })
  },

  // 创建文档评论/回复
  create: (doc_id: number, comment: DocComment) => {
    return request({
      url: `/docs/${doc_id}/comments`,
      method: 'post',
      data: comment
    })
  }
}

export default {
  docBook: docBookApi,
  doc: docApi,
  docComment: docCommentApi
}
