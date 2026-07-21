<template>
  <div class="wy-container">
    <el-container>
      <el-main>
        <el-row :gutter="30">
          <el-col :xs="24" :sm="24" :md="16">
            <div style="border-radius: 8px">
              <el-carousel :height="carouselHeight" class="wy-card-radius">
                <el-carousel-item v-for="item in recommendArticleList" :key="item.id">
                  <div class="wy-carousel-item" @click="handleDetail(item)">
                    <div class="wy-carousel-caption">
                      <div class="title">{{ item.title }}</div>
                      <div class="description">
                        {{ item.content.slice(0, 80).replace(/<\/?[^>]+(>|$)/g, '') }}...
                      </div>
                    </div>
                    <el-image
                      class="wy-carousel-img"
                      :src="item.cover || item.og_image"
                      fit="cover"
                    />
                  </div>
                </el-carousel-item>
              </el-carousel>
            </div>
          </el-col>
          <el-col :xs="24" :sm="24" :md="8">
            <el-card shadow="never" class="wy-card-radius wy-last-update-list">
              <div class="wy-card-title">{{ $t('home.list.lastupdated') }}</div>
              <div class="wy-card-body">
                <div class="last-item" v-for="item in recentArticleList" :key="item.article.id">
                  <span class="item-category"
                    >[<el-link
                      :title="item.category_name"
                      :href="'/category/' + item.category_slug"
                      >{{ truncateCategory(item.category_name) }}</el-link
                    >]</span
                  >
                  <span class="item-title">
                    <el-link :title="item.article.title" :href="'/article/' + item.article.slug">{{
                      item.article.title
                    }}</el-link></span
                  >
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <el-row :gutter="30" class="wy-padding-top30">
          <el-col :xs="24" :sm="24" :md="16" class="wy-card-list">
            <div style="display: flex; gap: 10px; margin-bottom: 20px">
              <el-button
                round
                :type="currentActiveTab === 'all' ? 'primary' : 'default'"
                :plain="currentActiveTab === 'all' ? true : false"
                @click="handleTabClick('all')"
              >
                <IconifyIcon icon="quill:list" width="20" height="20"></IconifyIcon>
                <span style="margin-left: 10px">{{ $t('home.list.tab.all') }}</span></el-button
              >
              <el-button
                round
                :type="currentActiveTab === 'following' ? 'primary' : 'default'"
                :plain="currentActiveTab === 'following' ? true : false"
                @click="handleTabClick('following')"
              >
                <IconifyIcon icon="cuida:users-outline" width="20" height="20"></IconifyIcon>
                <span style="margin-left: 10px">{{
                  $t('home.list.tab.following')
                }}</span></el-button
              >
              <el-button
                round
                :type="currentActiveTab === 'featured' ? 'primary' : 'default'"
                :plain="currentActiveTab === 'featured' ? true : false"
                @click="handleTabClick('featured')"
              >
                <IconifyIcon icon="la:medal" width="20" height="20"></IconifyIcon>
                <span style="margin-left: 10px">{{ $t('home.list.tab.featured') }}</span></el-button
              >
            </div>
            <div v-if="currentActiveTab === 'all'">
              <!--默认列表-->
              <el-card
                v-for="item in articleList"
                :key="item.id"
                shadow="hover"
                class="wy-card wy-card-radius"
                @click="handleDetail(item)"
              >
                <div class="wy-card-header">
                  <div class="left">
                    <div class="block">
                      <el-avatar
                        :size="50"
                        :src="item.author_profile_image || default_avatar"
                        @click.stop="handleProfile(item.author_username)"
                      />
                    </div>
                    <div class="block">
                      <div class="author">{{ item.author_full_name }}</div>
                      <div class="info">
                        @{{ item.author_username }} ·
                        {{ formatDateTime(item.createtime, 'YYYY-MM-DD') }}
                      </div>
                    </div>
                  </div>
                  <div class="right">
                    <el-tag
                      type="danger"
                      effect="light"
                      size="default"
                      round
                      v-if="item.is_featured"
                    >
                      <template #default>
                        <div style="display: flex; align-items: center">
                          <IconifyIcon icon="la:medal" width="16" height="16"></IconifyIcon>
                          {{ $t('home.list.recommend') }}
                        </div>
                      </template></el-tag
                    >
                  </div>
                </div>
                <div class="wy-card-body">
                  <div class="content">
                    <div class="left">
                      <div class="title">
                        {{ item.title }}
                      </div>
                      <div class="summary">
                        {{ item.content.slice(0, 150).replace(/<\/?[^>]+(>|$)/g, '') }}
                      </div>
                    </div>
                    <div class="right" v-if="item.cover">
                      <el-image
                        :src="item.cover"
                        fit="cover"
                        class="wy-card-radius wy-card-image"
                      />
                    </div>
                  </div>
                  <div class="info">
                    <div class="left">
                      <span>
                        <el-icon><ChatLineRound /></el-icon> {{ $t('home.list.discuss') }}
                      </span>
                      · <span>{{ item.stats?.likes }} {{ $t('home.list.likes') }}</span> ·
                      <span>{{ item.stats?.views }} {{ $t('home.list.reads') }}</span>
                    </div>
                    <div class="right">
                      <el-button
                        type="info"
                        size="small"
                        plain
                        round
                        style="border: 1px solid #e4e7ed; font-weight: 400"
                        @click.stop="handleLabel(tag)"
                        v-for="tag in item.displayTags"
                        :key="tag.id"
                        >{{ tag.name }}</el-button
                      >
                      <el-divider direction="vertical" />
                      <span style="margin-top: 5px">
                        <IconifyIcon
                          :icon="
                            item.isBookmarked
                              ? 'material-symbols-light:bookmark-star'
                              : 'material-symbols-light:bookmark-star-outline'
                          "
                          :color="item.isBookmarked ? '#ffcc00' : '#3f3f46'"
                          :stroke="item.isBookmarked ? '#ffcc00' : '#cccccc'"
                          @click.stop="handleBookmark(item.id, $event)"
                      /></span>
                    </div>
                  </div>
                </div>
              </el-card>
              <div v-if="articleList.length >= pageSize" class="wy-load-more">
                <el-button v-if="hasMoreData" type="primary" text @click="handleLoadMore('all')">{{
                  $t('home.list.loadmore')
                }}</el-button>
                <div v-else class="wy-no-more-data">-- {{ $t('home.list.nomore') }} --</div>
              </div>
            </div>
            <div v-else-if="currentActiveTab === 'following'">
              <!--关注列表-->
              <el-card
                v-for="item in followingArticleList"
                :key="item.id"
                shadow="hover"
                class="wy-card wy-card-radius"
                @click="handleDetail(item)"
              >
                <div class="wy-card-header">
                  <div class="left">
                    <div class="block">
                      <el-avatar
                        :size="50"
                        :src="item.author_profile_image || default_avatar"
                        @click.stop="handleProfile(item.author_username)"
                      />
                    </div>
                    <div class="block">
                      <div class="author">{{ item.author_full_name }}</div>
                      <div class="info">
                        @{{ item.author_username }} ·
                        {{ formatDateTime(item.createtime, 'YYYY-MM-DD') }}
                      </div>
                    </div>
                  </div>
                  <div class="right">
                    <el-tag
                      type="danger"
                      effect="light"
                      size="default"
                      round
                      v-if="item.is_featured"
                    >
                      <template #default>
                        <div style="display: flex; align-items: center">
                          <IconifyIcon icon="la:medal" width="16" height="16"></IconifyIcon>
                          {{ $t('home.list.recommend') }}
                        </div>
                      </template></el-tag
                    >
                  </div>
                </div>
                <div class="wy-card-body">
                  <div class="content">
                    <div class="left">
                      <div class="title">
                        {{ item.title }}
                      </div>
                      <div class="summary">
                        {{ item.content.slice(0, 150).replace(/<\/?[^>]+(>|$)/g, '') }}
                      </div>
                    </div>
                    <div class="right" v-if="item.cover">
                      <el-image
                        :src="item.cover"
                        fit="cover"
                        class="wy-card-radius wy-card-image"
                      />
                    </div>
                  </div>
                  <div class="info">
                    <div class="left">
                      <span>
                        <el-icon><ChatLineRound /></el-icon> {{ $t('home.list.discuss') }}
                      </span>
                      · <span>{{ item.stats?.likes }} {{ $t('home.list.likes') }}</span> ·
                      <span>{{ item.stats?.views }} {{ $t('home.list.reads') }}</span>
                    </div>
                    <div class="right">
                      <el-button
                        type="info"
                        size="small"
                        plain
                        round
                        style="border: 1px solid #e4e7ed; font-weight: 400"
                        @click.stop="handleLabel(tag)"
                        v-for="tag in item.displayTags"
                        :key="tag.id"
                        >{{ tag.name }}</el-button
                      >
                      <el-divider direction="vertical" />
                      <span style="margin-top: 5px">
                        <IconifyIcon
                          :icon="
                            item.isBookmarked
                              ? 'material-symbols-light:bookmark-star'
                              : 'material-symbols-light:bookmark-star-outline'
                          "
                          :color="item.isBookmarked ? '#ffcc00' : '#3f3f46'"
                          :stroke="item.isBookmarked ? '#ffcc00' : '#cccccc'"
                          @click.stop="handleBookmark(item.id, $event)"
                      /></span>
                    </div>
                  </div>
                </div>
              </el-card>
              <div v-if="followingArticleList.length >= followingPageSize" class="wy-load-more">
                <el-button
                  v-if="hasMoreFollowingData"
                  type="primary"
                  text
                  @click="handleLoadMore('following')"
                  >{{ $t('home.list.loadmore') }}</el-button
                >
                <div v-else class="wy-no-more-data">-- {{ $t('home.list.nomore') }} --</div>
              </div>
            </div>
            <div v-else>
              <!--精选列表-->
              <el-card
                v-for="item in featuredArticleList"
                :key="item.id"
                shadow="hover"
                class="wy-card wy-card-radius"
                @click="handleDetail(item)"
              >
                <div class="wy-card-header">
                  <div class="left">
                    <div class="block">
                      <el-avatar
                        :size="50"
                        :src="item.author_profile_image || default_avatar"
                        @click.stop="handleProfile(item.author_username)"
                      />
                    </div>
                    <div class="block">
                      <div class="author">{{ item.author_full_name }}</div>
                      <div class="info">
                        @{{ item.author_username }} ·
                        {{ formatDateTime(item.createtime, 'YYYY-MM-DD') }}
                      </div>
                    </div>
                  </div>
                  <div class="right">
                    <el-tag
                      type="danger"
                      effect="light"
                      size="default"
                      round
                      v-if="item.is_featured"
                    >
                      <template #default>
                        <div style="display: flex; align-items: center">
                          <IconifyIcon icon="la:medal" width="16" height="16"></IconifyIcon>
                          {{ $t('home.list.recommend') }}
                        </div>
                      </template></el-tag
                    >
                  </div>
                </div>
                <div class="wy-card-body">
                  <div class="content">
                    <div class="left">
                      <div class="title">
                        {{ item.title }}
                      </div>
                      <div class="summary">
                        {{ item.content.slice(0, 150).replace(/<\/?[^>]+(>|$)/g, '') }}
                      </div>
                    </div>
                    <div class="right" v-if="item.cover">
                      <el-image
                        :src="item.cover"
                        fit="cover"
                        class="wy-card-radius wy-card-image"
                      />
                    </div>
                  </div>
                  <div class="info">
                    <div class="left">
                      <span>
                        <el-icon><ChatLineRound /></el-icon> {{ $t('home.list.discuss') }}
                      </span>
                      · <span>{{ item.stats?.likes }} {{ $t('home.list.likes') }}</span> ·
                      <span>{{ item.stats?.views }} {{ $t('home.list.reads') }}</span>
                    </div>
                    <div class="right">
                      <el-button
                        type="info"
                        size="small"
                        plain
                        round
                        style="border: 1px solid #e4e7ed; font-weight: 400"
                        @click.stop="handleLabel(tag)"
                        v-for="tag in item.displayTags"
                        :key="tag.id"
                        >{{ tag.name }}</el-button
                      >
                      <el-divider direction="vertical" />
                      <span style="margin-top: 5px">
                        <IconifyIcon
                          :icon="
                            item.isBookmarked
                              ? 'material-symbols-light:bookmark-star'
                              : 'material-symbols-light:bookmark-star-outline'
                          "
                          :color="item.isBookmarked ? '#ffcc00' : '#3f3f46'"
                          :stroke="item.isBookmarked ? '#ffcc00' : '#cccccc'"
                          @click.stop="handleBookmark(item.id, $event)"
                      /></span>
                    </div>
                  </div>
                </div>
              </el-card>
              <div v-if="featuredArticleList.length >= featuredPageSize" class="wy-load-more">
                <el-button
                  v-if="hasMoreFeaturedData"
                  type="primary"
                  text
                  @click="handleLoadMore('featured')"
                  >{{ $t('home.list.loadmore') }}</el-button
                >
                <div v-else class="wy-no-more-data">-- {{ $t('home.list.nomore') }} --</div>
              </div>
            </div>
          </el-col>
          <el-col :xs="24" :sm="24" :md="8">
            <el-card shadow="never" class="wy-recommend-articles" style="margin-bottom: 30px">
              <div class="wy-card-title">{{ $t('home.list.trending') }}</div>
              <div class="wy-card-body">
                <div
                  class="article-item"
                  v-for="item in trendingArticleList"
                  :key="item.title"
                  @click="handleDetail(item)"
                >
                  <div class="item-title">{{ item.title }}</div>
                  <div class="item-info">
                    <span class="author">{{ item.full_name }}</span
                    ><span> · </span><span>{{ item.views }} {{ $t('home.list.reads') }}</span>
                  </div>
                </div>
              </div>
            </el-card>

            <el-card shadow="never" style="margin-bottom: 30px">
              <div class="wy-card-title">{{ $t('home.list.hottag') }}</div>
              <div class="wy-card-body">
                <div class="wy-hot-tags">
                  <el-tag
                    v-for="item in tagTtems"
                    :key="item.id"
                    type="primary"
                    effect="light"
                    round
                    @click="handleLabel(item)"
                  >
                    {{ item.name }}
                  </el-tag>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <el-row :gutter="30" class="wy-row wy-padding-top30">
          <el-col :xs="24" :sm="24" :md="16">
            <!-- <el-pagination
              v-model:current-page="currentPage"
              :page-size="pageSize"
              :total="totalArticles"
              :hide-on-single-page="true"
              @current-change="handleCurrentChange"
            /> -->
          </el-col>
          <el-col :xs="24" :sm="24" :md="8"> </el-col>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { Medal } from '@element-plus/icons-vue'
import { ref, reactive, toRefs, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import type { TagProps } from 'element-plus'
import { ElMessage } from 'element-plus'
import {
  getBlogList,
  getBlogTagsList,
  getBlogStats,
  getRecentBlog,
  getHotTagsList,
  getHotArticlesList,
  bookmarkArticleApi,
  unbookmarkArticleApi,
  checkBookmarkArticleApi,
  batchCheckBookmarkArticleApi
} from '@/api/services/blog'
import type { HomeArticleSearchParams } from '@/api/services/blog'
import { formatDateTime } from '@/utils/dateUtils'
import IconifyIcon from '../components/IconIfy.vue'

// import zhCN from './locale/zh-CN'

// 定义文章接口类型
interface Article {
  id: number
  title: string
  username: string
  avatar?: string
  profile_image?: string
  full_name?: string
  slug: string
  content?: string
  cover?: string
  createtime?: string
  is_recommend?: boolean
  likes?: number
  views?: number
  isBookmarked?: boolean
  tags?: string
  displayTags?: Array<{ id: number; name: string; slug: string }>
}

const { t } = useI18n()
const router = useRouter()
const appStore = useAppStore()

const default_avatar = 'src/assets/avatar.png'

const currentPage = ref(1)
const pageSize = ref(10)
const totalArticles = ref(0)
const articleList = ref<any[]>([])
const followingCurrentPage = ref(1)
const followingPageSize = ref(10)
const followingTotalArticles = ref(0)
const followingArticleList = ref<any[]>([])
const recommendArticleList = ref<any[]>([])
const featuredCurrentPage = ref(1)
const featuredPageSize = ref(10)
const featuredTotalArticles = ref(0)
const featuredArticleList = ref<any[]>([])
const currentActiveTab = ref('all')
const hasMoreData = ref(true)
const hasMoreFollowingData = ref(true)
const hasMoreFeaturedData = ref(true)
const recentArticleList = ref<any[]>([])

const carouselHeight = ref('350px')
const handleResize = () => {
  if (window.innerWidth < 768) {
    carouselHeight.value = '203px'
  } else {
    carouselHeight.value = '350px'
  }
}
// 处理页面可见性变化
let savedScrollPosition = 0
let wasHidden = false

// 截取字符串函数 - 用于分类名称（最多4个字符）
const truncateCategory = (text: string): string => {
  if (!text) return ''
  return text.length > 4 ? text.slice(0, 4) + '...' : text
}

// 截取字符串函数 - 用于文章标题（最多18个字符）
const truncateTitle = (text: string): string => {
  if (!text) return ''
  return text.length > 18 ? text.slice(0, 18) + '...' : text
}

const handleVisibilityChange = () => {
  if (document.visibilityState === 'hidden') {
    // 当页面变为隐藏状态时，保存当前滚动位置
    savedScrollPosition = window.scrollY
    wasHidden = true
  } else if (document.visibilityState === 'visible' && wasHidden) {
    // 当页面从隐藏状态变为可见状态时，重新获取文章列表
    getArticleList()
    wasHidden = false
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
  document.addEventListener('visibilitychange', handleVisibilityChange)
  // 确保路由切换时不会恢复滚动位置
  savedScrollPosition = 0
  getArticleList()
  loadRecommendArticles()
  loadRecentArticles()
  loadHotTags()
  loadHotArticles()
})
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  document.removeEventListener('visibilitychange', handleVisibilityChange)
})
const handleDetail = (item: any) => {
  const articleName = item.slug
  router.push(`/article/${articleName}`)
}
const handleLabel = (tag: any) => {
  if (tag && tag.slug) {
    router.push(`/tag/${tag.slug}`)
  }
}
const trendingArticleList = ref<any[]>([])
type Item = { id: number; type: string; name: string; slug: string; counts: number }
const tagTtems = ref<Array<Item>>([])

const handleTabClick = (tab: string) => {
  currentActiveTab.value = tab
  if (tab === 'all') {
    getArticleList()
  } else if (tab === 'following') {
    if (appStore.userInfo.id && appStore.token) {
      getFollowingArticleList()
    } else {
      followingArticleList.value = []
    }
  } else if (tab === 'featured') {
    getFeaturedArticleList()
  }
}

// 获取轮播推荐文章
const loadRecommendArticles = async () => {
  const params: HomeArticleSearchParams = {
    type: 'recommend'
  }
  const res = await getBlogList(1, 6, params)
  if (res.code === 1) {
    recommendArticleList.value = res.data.list
  }
}

// 获取文章列表
const getArticleList = async () => {
  const params: HomeArticleSearchParams = {
    type: 'all'
  }
  const res = await getBlogList(currentPage.value, pageSize.value, params)
  if (res.code === 1) {
    // 如果是第一页，则替换列表；否则追加新数据
    if (currentPage.value === 1) {
      articleList.value = res.data.list
    } else {
      articleList.value = [...articleList.value, ...res.data.list]
    }
    totalArticles.value = res.data.total
    pageSize.value = res.data.pageSize

    // 判断是否还有更多数据
    hasMoreData.value = articleList.value.length < totalArticles.value
    // 异步加载每篇文章的标签
    await loadArticlesTags()
    // 异步加载文章的统计数据
    await loadArticleStats()
    // 再加载收藏状态
    await checkArticlesBookmarkStatus()
    // 数据加载完成后，只有在页面从隐藏状态恢复时才恢复滚动位置
    // 使用setTimeout确保DOM已经更新
    setTimeout(() => {
      if (savedScrollPosition > 0) {
        window.scrollTo({ top: savedScrollPosition, behavior: 'smooth' })
        // 重置保存的位置，避免影响正常的页面浏览
        savedScrollPosition = 0
      }
    }, 100)
  }
}

// 获取关注的文章列表
const getFollowingArticleList = async () => {
  const params: HomeArticleSearchParams = {
    type: 'following',
    uid: appStore.userInfo.id || 0
  }
  const res = await getBlogList(followingCurrentPage.value, followingPageSize.value, params)
  if (res.code === 1) {
    // 如果是第一页，则替换列表；否则追加新数据
    if (followingCurrentPage.value === 1) {
      followingArticleList.value = res.data.list
    } else {
      followingArticleList.value = [...followingArticleList.value, ...res.data.list]
    }
    followingTotalArticles.value = res.data.total
    followingPageSize.value = res.data.pageSize

    // 判断是否还有更多数据
    hasMoreFollowingData.value = followingArticleList.value.length < followingTotalArticles.value
    // 异步加载每篇文章的标签
    await loadArticlesTags()
    // 异步加载文章的统计数据
    await loadArticleStats()
    // 再加载收藏状态
    await checkArticlesBookmarkStatus()
  }
}

// 获取精选文章列表
const getFeaturedArticleList = async () => {
  const params: HomeArticleSearchParams = {
    type: 'featured'
  }
  const res = await getBlogList(featuredCurrentPage.value, featuredPageSize.value, params)
  if (res.code === 1) {
    // 如果是第一页，则替换列表；否则追加新数据
    if (featuredCurrentPage.value === 1) {
      featuredArticleList.value = res.data.list
    } else {
      featuredArticleList.value = [...featuredArticleList.value, ...res.data.list]
    }
    featuredTotalArticles.value = res.data.total
    featuredPageSize.value = res.data.pageSize

    // 判断是否还有更多数据
    hasMoreFeaturedData.value = featuredArticleList.value.length < featuredTotalArticles.value
    // 异步加载每篇文章的标签
    await loadArticlesTags()
    // 异步加载文章的统计数据
    await loadArticleStats()
    // 再加载收藏状态
    await checkArticlesBookmarkStatus()
  }
}

// 异步加载所有文章的标签
const loadArticlesTags = async () => {
  // 为每篇文章初始化displayTags数组
  articleList.value.forEach((article) => {
    article.displayTags = []
  })

  // 提取所有不同的tag_ids集合
  const allTagIds = new Set<string>()
  articleList.value.forEach((article) => {
    if (article.tags && typeof article.tags === 'string') {
      // 解析字符串格式的tags，如"16,17,22"
      const tagIds = article.tags
        .split(',')
        .map((id: string) => id.trim())
        .filter((id: string) => id)
      tagIds.forEach((tagId: string) => allTagIds.add(tagId))
    }
  })

  // 如果有标签ID，则批量获取标签信息
  if (allTagIds.size > 0) {
    const res = await getBlogTagsList(Array.from(allTagIds))
    if (res.code === 1) {
      const tagsMap = new Map<string, any>()
      res.data.forEach((tag: any) => {
        tagsMap.set(tag.id.toString(), tag)
      })

      // 将标签分配给对应的文章
      articleList.value.forEach((article) => {
        if (article.tags && typeof article.tags === 'string') {
          // 解析字符串格式的tags并映射到标签对象
          const tagIds = article.tags
            .split(',')
            .map((id: string) => id.trim())
            .filter((id: string) => id)
          article.displayTags = tagIds
            .map((tagId: string) => tagsMap.get(tagId.toString()))
            .filter((tag: any) => tag !== undefined)
            // 按counts字段降序排序，只显示前3个标签
            .sort((a: any, b: any) => (b.counts || 0) - (a.counts || 0))
            .slice(0, 3)
        }
      })
    }
  }
}

// 异步加载文章统计数据
const loadArticleStats = async () => {
  try {
    // 检查articleList是否为空
    if (articleList.value.length === 0) {
      console.log('Article list is empty, skipping stats loading')
      return
    }

    // 确保articleIds是字符串数组
    const articleIds = articleList.value.map((article) => String(article.id))
    console.log('Loading stats for article IDs:', articleIds)

    const res = await getBlogStats(articleIds)
    console.log('Stats API response:', res)

    if (res.code === 1) {
      // 检查响应数据是否存在
      if (!res.data) {
        console.error('No stats data returned:', res)
        // 为每篇文章设置默认统计数据，确保页面不会显示空值
        articleList.value.forEach((article) => {
          article.stats = {
            likes: 0,
            views: 0
          }
        })
        return
      }

      // 处理可能的不同数据结构
      const statsMap = new Map<string, any>()

      // 情况1：res.data是数组（预期格式）
      if (Array.isArray(res.data)) {
        console.log('情况1：res.data是数组')
        res.data.forEach((stat: any) => {
          // 确保stat有article_id属性并转换为字符串
          const articleId = stat.article_id ? String(stat.article_id) : null
          if (articleId) {
            // console.log('Adding stat for article:', articleId, stat)
            // 标准化统计数据格式
            const normalizedStats = {
              likes: stat.likes || stat.like_count || 0,
              views: stat.views || stat.view_count || 0
            }
            statsMap.set(articleId, normalizedStats)
          }
        })
      }
      // 情况2：res.data是对象（可能的其他格式）
      else if (typeof res.data === 'object' && res.data !== null) {
        console.log('情况2：res.data是对象')
        // 遍历对象的所有键
        Object.keys(res.data).forEach((key) => {
          const stat = res.data[key]
          const articleId = String(key)

          // 标准化统计数据格式
          const normalizedStats = {
            likes: stat.likes || stat.like_count || 0,
            views: stat.views || stat.view_count || 0
          }
          statsMap.set(articleId, normalizedStats)
        })
      }

      // 为每篇文章设置统计数据
      articleList.value.forEach((article) => {
        const articleIdStr = String(article.id)
        // 获取标准化的统计数据或使用默认值
        article.stats = statsMap.get(articleIdStr) || {
          likes: 0,
          views: 0
        }
        // console.log('Article', articleIdStr, 'stats:', article.stats)
      })
    } else {
      // console.error('Stats API returned error:', res.code, res.message)
      // API返回错误时，为每篇文章设置默认统计数据
      articleList.value.forEach((article) => {
        article.stats = {
          likes: 0,
          views: 0
        }
      })
    }
  } catch (error) {
    console.error('Error loading article stats:', error)
    // 发生异常时，为每篇文章设置默认统计数据
    articleList.value.forEach((article) => {
      article.stats = {
        likes: 0,
        views: 0
      }
    })
  }
}

// 获取最近更新文章
const loadRecentArticles = async () => {
  const res = await getRecentBlog()
  if (res.code === 1) {
    recentArticleList.value = res.data || []
  }
}

// 获取热门标签列表
const loadHotTags = async () => {
  const res = await getHotTagsList()
  if (res.code === 1) {
    tagTtems.value = res.data || []
  }
}

// 获取热门文章列表
const loadHotArticles = async (limit: number = 5, days: number = 7) => {
  const res = await getHotArticlesList(limit, days)
  if (res.code === 1) {
    trendingArticleList.value = res.data || []
  }
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  getArticleList()
  console.log(`current page: ${val}`)
}
// 处理加载更多
const handleLoadMore = (tab: string) => {
  if (tab === 'all') {
    currentPage.value++
    getArticleList()
  } else if (tab === 'following') {
    followingCurrentPage.value++
    getFollowingArticleList()
  } else if (tab === 'featured') {
    featuredCurrentPage.value++
    getFeaturedArticleList()
  }
}

// 检查用户是否登录
const checkUserLogin = async (): Promise<boolean> => {
  // 从本地缓存中读取用户信息，判断是否已登陆
  const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
  if (!userInfo || !userInfo.id) {
    ElMessage.error('请先登录')
    router.push(`/login`)
    return false
  } else {
    return true
  }
}

// 批量检查文章收藏状态
const checkArticlesBookmarkStatus = async (): Promise<void> => {
  if (articleList.value.length === 0) return
  const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
  if (!userInfo || !userInfo.id) return

  try {
    // 提取所有文章ID
    const articleIds = articleList.value.map((article: Article) => article.id)
    console.log(articleIds)
    const response = await batchCheckBookmarkArticleApi(articleIds)

    if (response.code === 1) {
      // 新数据结构：result是一个对象，键为文章ID字符串，值为收藏状态布尔值
      const bookmarkResults = response.data?.result || {}

      // 为每篇文章设置收藏状态
      articleList.value.forEach((article: Article) => {
        // 从对象中获取当前文章的收藏状态，如果不存在则默认为false
        article.isBookmarked = bookmarkResults[article.id.toString()] || false
      })
    }
  } catch (error) {
    console.log('批量检查收藏状态失败:', error)
    // 出错时默认所有文章未收藏
    articleList.value.forEach((article: Article) => {
      article.isBookmarked = false
    })
  }
}

// 单篇检查文章收藏状态 - 用于点击操作后的状态更新
const checkSingleBookmarkStatus = async (article_id: number): Promise<boolean> => {
  try {
    const response = await checkBookmarkArticleApi(article_id)
    if (response.code === 1) {
      return response.data.is_bookmarked
    }
  } catch (error) {
    console.log('检查收藏状态失败:', error)
  }
  return false
}

// 处理收藏文章点击事件
const handleBookmark = async (article_id: number, event: Event): Promise<void> => {
  // 阻止事件冒泡，避免触发文章详情点击
  event.stopPropagation()

  const article = articleList.value.find((article) => article.id === article_id)
  if (!article) return

  // 先保存当前状态，用于回滚
  const oldStatus = article.isBookmarked

  // 立即更新UI状态，提升用户体验
  article.isBookmarked = !oldStatus

  try {
    let success = false

    if (oldStatus) {
      success = await unbookmarkArticle(article_id)
    } else {
      success = await bookmarkArticle(article_id)
    }

    // 检查是否成功执行，false表示用户未登录
    if (!success) {
      // 回滚UI状态
      article.isBookmarked = oldStatus
      // 不需要显示额外的错误消息，因为checkUserLogin已经处理了
      return
    }

    // API调用成功，不需要额外操作，状态已经更新
  } catch (error) {
    console.error('收藏/取消收藏操作失败:', error)

    // API调用失败，回滚UI状态
    article.isBookmarked = oldStatus

    // 显示错误消息
    ElMessage.error('操作失败，请重试')
  }
}

// 收藏文章
const bookmarkArticle = async (article_id: number): Promise<boolean> => {
  const result = await checkUserLogin()
  if (!result) {
    // checkUserLogin已经处理了未登录的情况，包括显示错误消息和跳转
    return false
  }

  const response = await bookmarkArticleApi(article_id)
  if (response.code !== 1) {
    throw new Error('收藏文章失败')
  }

  ElMessage.success('收藏文章成功')
  return true
}

// 取消收藏文章
const unbookmarkArticle = async (article_id: number): Promise<boolean> => {
  const result = await checkUserLogin()
  if (!result) {
    // checkUserLogin已经处理了未登录的情况，包括显示错误消息和跳转
    return false
  }

  const response = await unbookmarkArticleApi(article_id)
  if (response.code !== 1) {
    throw new Error('取消收藏文章失败')
  }

  ElMessage.success('取消收藏文章成功')
  return true
}

// 处理用户点击跳转个人中心
const handleProfile = (username: string) => {
  router.push(`/profile/${username}`)
}

// 定义组件名称
defineOptions({ name: 'IndexView' })
</script>

<style>
.wy-container {
  display: flex;
  width: 1200px;
}
.wy-padding-top30 {
  padding-top: 30px;
}
.wy-carousel-container {
  height: 350px;
}
.wy-carousel-item {
  width: 100%;
  height: 100%;
  position: relative;
  cursor: pointer;
}
.wy-carousel-img {
  width: 100%;
  height: 350px;
  position: absolute;
  top: 0;
  left: 0;
  z-index: 1;
  pointer-events: none;
}

.wy-carousel-caption {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  padding: 20px;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.4));
  color: white;
  z-index: 10;
  box-sizing: border-box;
  pointer-events: none;
}

.wy-carousel-caption .title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 8px;
}

.wy-carousel-caption .description {
  font-size: 16px;
  opacity: 0.9;
}
.wy-card-radius {
  border-radius: 8px;
}
/* .wy-card-list .wy-card-radius:first {
  margin-top: 0;
} */
.wy-card:hover {
  cursor: pointer;
}
.wy-card:not(:first-of-type) {
  margin-top: 30px;
}

.el-carousel__item h3 {
  color: #475669;
  opacity: 0.75;
  line-height: 150px;
  margin: 0;
  text-align: center;
}
.el-carousel__item:nth-child(2n) {
  background-color: #99a9bf;
}

.el-carousel__item:nth-child(2n + 1) {
  background-color: #d3dce6;
}

.wy-last-update-list {
  max-height: 350px;
}
.wy-card-title {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--el-text-color-regular);
  margin-bottom: 1rem;
}
.wy-card-body .last-item {
  font-size: 1.25rem;
  display: flex;
}
.wy-card-body .last-item:not(:last-child) {
  margin-bottom: 0.7rem;
}
.wy-no-more-data {
  text-align: center;
  color: #909399;
  font-size: 14px;
  padding: 20px 0;
}
.wy-card-body .last-item .item-category {
  color: var(--el-text-color-regular);
  cursor: pointer;
  /* overflow: hidden; */
  white-space: nowrap;
  margin-right: 5px;
  /* text-overflow: ellipsis; */
  /* min-width: 50px; */
  /* max-width: 100px; */
}
.wy-card-body .last-item .item-title {
  color: var(--el-text-color-regular);
  cursor: pointer;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}
.wy-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.wy-card-header .left {
  display: flex;
}
.wy-card-header .left .block {
  margin-right: 10px;
}
.wy-card-header .author {
  font-weight: 800;
  font-size: 14px;
  line-height: 28px;
}
.wy-card-header .info {
  color: #909399;
}
.wy-card-body {
  display: flex;
  flex-direction: column;
}
.wy-card-body .content,
.wy-card-body .info {
  display: flex;
  justify-content: space-between;
  padding-top: 15px;
}
.wy-card-body .info .right {
  display: flex;
  align-items: center;
}
.wy-card-body .content .right {
  width: 179px;
  height: 108px;
  border-radius: 8px;
}
.wy-card-body .content .left {
  display: flex;
  flex-direction: column;
  /* width: 500px; */
  flex: 1;
  margin-right: 10px;
}
.wy-card-body .title {
  font-weight: 800;
  font-size: 24px;
  line-height: 30px;
  padding-bottom: 10px;
}
.wy-card-body .summary {
  font-size: 18px;
  color: #909399;
  line-height: 28px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  line-clamp: 2;
  -webkit-line-clamp: 2;
}
.wy-card-image {
  width: 179px;
  height: 108px;
}

.wy-card-body .article-item:not(:last-child) {
  margin-bottom: 1.2rem;
}
.wy-card-body .article-item .item-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--el-text-color-regular);
  cursor: pointer;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  margin-bottom: 0.5rem;
}
.wy-card-body .article-item .item-title:hover {
  text-decoration: underline;
  color: var(--el-color-primary);
}
.wy-card-body .article-item .item-info {
  display: flex;
  justify-content: flex-start;
  color: var(--el-text-color-secondary);
}
.wy-card-body .article-item .item-info span {
  margin-right: 8px;
}
.wy-card-body .article-item .item-info .author {
  cursor: pointer;
}

.wy-hot-tags {
  display: flex;
  /*margin-top: 3rem;*/
  /*padding: 0 45px;*/
  flex-wrap: wrap;
}
.wy-hot-tags span {
  cursor: pointer;
  margin: 5px;
}
.wy-hot-tags span:hover {
  cursor: pointer;
  margin: 5px;
  background-color: var(--el-color-primary);
  color: var(--el-color-white);
}

.wy-load-more {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 30px;
}

@media only screen and (max-width: 767px) {
  .wy-container {
    display: flex;
    width: 100%;
  }
  .wy-carousel-img {
    width: 100%;
    height: 203px;
  }
  .wy-carousel-caption {
    padding: 15px;
  }
  .wy-carousel-caption .title {
    font-size: 16px;
    -webkit-line-clamp: 1;
    line-clamp: 1;
    overflow: hidden;
  }
  .wy-carousel-caption .description {
    font-size: 12px;
    -webkit-line-clamp: 1;
    line-clamp: 1;
    overflow: hidden;
  }
  .wy-last-update-list {
    max-height: 350px;
    margin-top: 30px;
  }
  .wy-recommend-articles {
    margin-top: 30px;
  }
  .wy-card-image {
    width: 144px;
    height: 86px;
  }
  .el-main {
    --el-main-padding: 10px !important;
  }
}
</style>
