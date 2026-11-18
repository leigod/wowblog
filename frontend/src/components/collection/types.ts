/**
 * 目录索引页（文档 / 分类 / 系列）与分类系列详情页共用的展示类型。
 * 放在独立 .ts 里：<script setup> 内不允许 export 语句。
 */

export interface CollectionChip {
  key: string | number
  label: string
  to: string
}

export interface CollectionItem {
  key: string | number
  title: string
  desc?: string
  cover?: string
  letter?: string
  to: string
  meta?: string[]
  chips?: CollectionChip[]
  /** 参与搜索匹配的额外文本（如子分类名、slug） */
  searchText?: string
}

export interface TaxonomyCrumb {
  label: string
  to?: string
}

/** 分类详情页下方的子分类入口（自身没有直收文章时的下一跳） */
export interface TaxonomyChild {
  label: string
  to: string
}

export interface TaxonomyArticle {
  id: number
  slug: string
  title: string
  content?: string
  cover?: string
  createtime?: number
  views?: number
  likes?: number
  author_username?: string
}
