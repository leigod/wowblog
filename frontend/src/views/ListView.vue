<template>
  <div class="wy-container">
    <el-container>
      <el-main>
        <el-row :gutter="30">
          <el-col :xs="24" :sm="16">
            <el-card shadow="never" style="margin-bottom: 30px">
              <div class="wy-channel-intro">
                <div class="wy-channel-body">
                  <div class="info">
                    <div class="name">{{ tagPageInfo.name || '' }}</div>
                    <div class="secondary-info">
                      <span>#{{ tagPageInfo.slug || '' }}</span> ·
                      <span>{{ tagPageInfo.follows || 0 }} {{ t('tag.followers') }}</span> ·
                      <span>{{ tagPageStatInfo.total_articles || 0 }} {{ t('tag.articles') }}</span>
                    </div>
                    <div class="functions">
                      <el-button v-if="isFollowing" plain round type="primary" @click="unfollowTag">
                        <el-icon size="20" style="margin-right: 5px">
                          <Check />
                        </el-icon>
                        {{ t('tag.following') }}
                      </el-button>
                      <el-button v-else round type="primary" @click="followTag"
                        >{{ t('tag.follow') }}</el-button
                      >
                      <el-button plain round @click="writeArticle">{{ t('tag.write_article') }}</el-button>
                      <el-button plain circle @click="copyLink">
                        <el-icon size="20">
                          <Link />
                        </el-icon>
                      </el-button>
                    </div>
                  </div>
                  <div class="wy-channel-img-wrapper">
                    <div class="wy-channel-img">
                      <img :src="tagPageInfo.image || default_tag_image" alt="" />
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="400"
                        height="400"
                        fill="none"
                        class="svg-position"
                      >
                        <g class="dark:hidden block">
                          <circle cx="200" cy="200" r="48" stroke="#e4e4e7cc"></circle>
                          <circle cx="200" cy="200" r="72" stroke="#e4e4e7aa"></circle>
                          <circle cx="200" cy="200" r="96" stroke="#e4e4e755"></circle>
                          <circle cx="200" cy="200" r="120" stroke="#e4e4e733"></circle>
                          <circle cx="200" cy="200" r="144" stroke="#e4e4e705"></circle>
                        </g>
                        <g class="hidden dark:block">
                          <circle cx="200" cy="200" r="48" stroke="#3f3f46cc"></circle>
                          <circle cx="200" cy="200" r="72" stroke="#3f3f46aa"></circle>
                          <circle cx="200" cy="200" r="96" stroke="#3f3f4655"></circle>
                          <circle cx="200" cy="200" r="120" stroke="#3f3f4633"></circle>
                          <circle cx="200" cy="200" r="144" stroke="#3f3f4605"></circle>
                        </g>
                      </svg>
                    </div>
                  </div>
                </div>
                <div class="wy-channel-description" v-if="tagPageInfo.tag_desc">
                  <div v-show="!showMore" class="simple-description">
                    <div class="single-text">
                      {{ tagPageInfo.tag_desc }}
                    </div>
                    <div class="btn-more">
                      <el-button type="primary" text @click="showMore = true"
                        >{{ t('tag.read_more') }}</el-button
                      >
                    </div>
                  </div>
                  <div v-show="showMore" class="more-description">
                    <div class="more-text">
                      <div>
                        {{ tagPageInfo.tag_desc }}
                      </div>
                      <el-link style="font-weight: 700">
                        {{ t('tag.know_more') }} <el-icon style="margin-left: 5px"><IconExternalLink /></el-icon>
                      </el-link>
                    </div>
                    <div class="btn-collapse">
                      <el-button type="primary" text @click="showMore = false">
                        <el-icon><IconCornerLeftUp /></el-icon>{{ t('tag.collapse') }}
                      </el-button>
                    </div>
                  </div>
                </div>
              </div>
            </el-card>

            <div class="wy-card-list-type">
              <el-segmented v-model="defaultValue" :options="typeOptions" @change="handleChange">
                <template #default="{ item }">
                  <div class="wy-list-type-nav">
                    <el-icon size="20">
                      <component :is="item.icon" />
                    </el-icon>
                    <div style="margin-left: 5px">{{ item.label }}</div>
                  </div>
                </template>
              </el-segmented>
            </div>

            <div class="wy-card-list">
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
                      <el-avatar :size="50" :src="item.profile_image || default_avatar" />
                    </div>
                    <div class="block">
                      <div class="author">{{ item.full_name || item.username }}</div>
                      <div class="info">
                        @{{ item.username }} -
                        {{ formatDateTime(item.createtime || '', 'YYYY-MM-DD') }}
                      </div>
                    </div>
                  </div>
                  <div class="right">
                    <el-tag
                      type="danger"
                      effect="light"
                      size="default"
                      round
                      v-if="item.is_recommend"
                    >
                      {{ $t('home.list.recommend') }}</el-tag
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
                        {{ (item.content || '').slice(0, 150).replace(/<\/?[^>]+(>|$)/g, '') }}
                      </div>
                    </div>
                    <div class="right" v-if="item.cover">
                      <el-image
                        style="width: 179px; height: 108px"
                        :src="item.cover"
                        fit="cover"
                        class="wy-card-radius"
                      />
                    </div>
                  </div>
                  <div class="info">
                    <div class="left">
                      <span>
                        <el-icon><ChatLineRound /></el-icon> {{ $t('home.list.discuss') }}
                      </span>
                      · <span>{{ item.likes }} {{ $t('home.list.likes') }}</span> ·
                      <span>{{ item.views }} {{ $t('home.list.reads') }}</span>
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
                      <IconifyIcon
                        :icon="
                          item.isBookmarked
                            ? 'material-symbols-light:bookmark-star'
                            : 'material-symbols-light:bookmark-star-outline'
                        "
                        width="28"
                        height="28"
                        :color="item.isBookmarked ? '#eab308' : '#3f3f46'"
                        @click.stop="handleBookmark(item.id, $event)"
                      />
                    </div>
                  </div>
                </div>
              </el-card>
            </div>
            <div v-if="articleList.length >= pageSize" class="wy-load-more">
              <el-button v-if="hasMoreData" type="primary" text @click="handleLoadMore"
                >{{ t('tag.load_more') }}</el-button
              >
              <div v-else class="wy-no-more-data">{{ t('tag.no_more') }}</div>
            </div>
            <div class="wy-card-list" v-if="articleList.length === 0">
              <el-empty style="margin-top: 30px" :description="t('tag.no_articles')" />
            </div>
          </el-col>

          <el-col :xs="24" :sm="8">
            <el-card shadow="never" class="wy-recommend-articles" style="margin-bottom: 30px">
              <div class="wy-card-title">{{ t('tag.trending_articles') }}</div>
              <div class="wy-card-body">
                <div class="article-item" v-for="item in trendingArticleList" :key="item.title">
                  <div class="item-title" @click="handleDetail(item)">{{ item.title }}</div>
                  <div class="item-info">
                    <span class="author">{{ item.full_name || item.username }}</span
                    ><span> · </span><span>{{ item.views || 0 }} {{ t('tag.reads') }}</span>
                  </div>
                </div>
              </div>
            </el-card>

            <el-card shadow="never">
              <div class="wy-card-title">{{ t('tag.top_commenters') }}</div>
              <div class="wy-card-body">
                <div class="commenter-item" v-for="item in commenterList" :key="item.id">
                  <div class="author-area">
                    <el-avatar :size="30" :src="item.avatar" />
                    <span class="author">{{ item.full_name || item.username }}</span>
                  </div>
                  <div class="operations">{{ item.comment_count }} {{ t('tag.comments') }}</div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, toRefs, onMounted, watch, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import {
  getTagPageInfo,
  getTagArticlesList,
  getBlogTagsList,
  getHotArticlesList,
  followTagApi,
  unfollowTagApi,
  bookmarkArticleApi,
  unbookmarkArticleApi,
  checkBookmarkArticleApi,
  checkFollowTagApi,
  batchCheckBookmarkArticleApi,
  getTopCommenters,
  type TopCommenter
} from '../api/services/blog'
import { ElMessage } from 'element-plus'
import { formatDateTime } from '../utils/dateUtils'
import IconifyIcon from '../components/IconIfy.vue'
import IconExternalLink from '../components/icons/IconExternalLink.vue'
import IconCornerLeftUp from '../components/icons/IconCornerLeftUp.vue'
import IconFire from '../components/icons/IconFire.vue'
import { Clock, Link, Check, ChatLineRound } from '@element-plus/icons-vue'

const { t } = useI18n()

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

interface TagInfo {
  id: number
  slug: string
  name: string
  follows?: number
  tag_desc?: string
  image?: string
}

interface TagPageStat {
  total_articles: number
}

const showMore = ref(false)
const defaultValue = ref('Hot')
const router = useRouter()
const route = useRoute()
const typeOptions = [
  {
    label: computed(() => t('tag.hot')),
    value: 'Hot',
    icon: IconFire
  },
  {
    label: computed(() => t('tag.new')),
    value: 'New',
    icon: Clock
  }
]
const tagPageInfo = ref<TagInfo>({ id: 0, slug: '', name: '', follows: 0, tag_desc: '', image: '' })
const tagPageStatInfo = ref<TagPageStat>({ total_articles: 0 })
const trendingArticleList = ref<Article[]>([])
const commenterList = ref<TopCommenter[]>([])
const articleList = ref<Article[]>([])
const default_avatar = '/src/assets/avatar.png'
const default_tag_image = '/src/assets/hash_sign.png'
const currentPage = ref(1)
const pageSize = ref(10)
const totalCount = ref(0)
const hasMoreData = ref(true)
const isFollowing = ref(false)

// 组件挂载时执行
onMounted(() => {
  loadTagPageInfo()
  loadHotArticles()
  loadTopCommenters()
})

// 加载标签页信息
const loadTagPageInfo = async (): Promise<void> => {
  try {
    const response = await getTagPageInfo(route.params.slug as string)
    if (response.code === 1) {
      tagPageInfo.value = response.data.tag
      tagPageStatInfo.value = response.data
      loadArticlesList()
      // 检查用户是否已关注该标签
      checkFollowingStatus()
    } else {
      router.push('/404')
    }
  } catch (error) {
    console.log('加载标签页信息失败:', error)
    router.push('/404')
  }
}

// 加载文章列表页
const loadArticlesList = async (): Promise<void> => {
  try {
    const response = await getTagArticlesList(
      tagPageInfo.value.id,
      currentPage.value,
      pageSize.value,
      defaultValue.value.toLowerCase() as 'hot' | 'new'
    )
    if (response.code === 1) {
      // 如果是第一页，则替换列表；否则追加新数据
      if (currentPage.value === 1) {
        articleList.value = response.data.list
      } else {
        articleList.value = [...articleList.value, ...response.data.list]
      }
      // 更新总记录数和是否有更多数据
      totalCount.value = response.data.total
      pageSize.value = response.data.pageSize
      hasMoreData.value = response.data.list.length >= pageSize.value

      // 先加载标签
      await loadArticlesTags()

      // 再加载收藏状态
      await checkArticlesBookmarkStatus()
    } else {
      ElMessage.error(t('tag.load_articles_failed'))
    }
  } catch (error) {
    ElMessage.error(t('tag.load_articles_failed'))
  }
}

// 异步加载所有文章的标签
const loadArticlesTags = async (): Promise<void> => {
  // 为每篇文章初始化displayTags数组
  articleList.value.forEach((article: Article) => {
    article.displayTags = []
  })

  // 提取所有不同的tag_ids集合
  const allTagIds = new Set<string>()
  articleList.value.forEach((article: Article) => {
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
      articleList.value.forEach((article: Article) => {
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

// 获取热门文章列表
const loadHotArticles = async (limit: number = 5, days: number = 7): Promise<void> => {
  const res = await getHotArticlesList(limit, days)
  if (res.code === 1) {
    trendingArticleList.value = res.data || []
  }
}

// 获取本周活跃评论者
const loadTopCommenters = async (limit: number = 5): Promise<void> => {
  try {
    const res = await getTopCommenters(limit)
    if (res.code === 1) {
      commenterList.value = res.data || []
    }
  } catch (error) {
    console.error('Failed to load top commenters:', error)
    commenterList.value = []
  }
}

// 处理点击文章详情
const handleDetail = (item: Article): void => {
  const articleName = item.slug
  router.push(`/article/${articleName}`)
}

// 处理标签点击
const handleLabel = (tag: { slug: string }): void => {
  if (tag && tag.slug) {
    router.push(`/tag/${tag.slug}`)
  }
}

// 处理切换类型
const handleChange = (val: string): void => {
  defaultValue.value = val
  loadArticlesList()
}

// 处理加载更多
const handleLoadMore = (): void => {
  currentPage.value++
  loadArticlesList()
}

// 检查用户是否登录
const checkUserLogin = async (): Promise<boolean> => {
  // 从本地缓存中读取用户信息，判断是否已登陆
  const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
  const link = '/tag/' + tagPageInfo.value.slug
  if (!userInfo || !userInfo.id) {
    ElMessage.error(t('tag.login_required'))
    router.push(`/login?redirect=${link}`)
    return false
  } else {
    return true
  }
}

// 检查用户是否已关注该标签
const checkFollowingStatus = async (): Promise<void> => {
  const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
  if (!userInfo || !userInfo.id) {
    isFollowing.value = false
    return
  } else {
    try {
      const response = await checkFollowTagApi(tagPageInfo.value.id)
      if (response.code === 1) {
        isFollowing.value = response.data.is_following
      }
    } catch (error) {
      console.log('检查关注状态失败:', error)
    }
  }
}

// 关注标签
const followTag = async (): Promise<void> => {
  const result = await checkUserLogin()
  if (!result) {
    return
  }
  try {
    const response = await followTagApi(tagPageInfo.value.id)
    if (response.code === 1) {
      isFollowing.value = true
      ElMessage.success(t('tag.follow_success'))
    } else {
      ElMessage.error(t('tag.follow_failed'))
    }
  } catch (error) {
    ElMessage.error(t('tag.follow_failed'))
  }
}

// 取消关注标签
const unfollowTag = async (): Promise<void> => {
  const result = await checkUserLogin()
  if (!result) {
    return
  }
  try {
    const response = await unfollowTagApi(tagPageInfo.value.id)
    if (response.code === 1) {
      isFollowing.value = false
      ElMessage.success(t('tag.unfollow_success'))
    } else {
      ElMessage.error(t('tag.unfollow_failed'))
    }
  } catch (error) {
    ElMessage.error(t('tag.unfollow_failed'))
  }
}

// 批量检查文章收藏状态
const checkArticlesBookmarkStatus = async (): Promise<void> => {
  if (articleList.value.length === 0) return

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
    ElMessage.error(t('tag.bookmark_failed'))
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
    throw new Error('Bookmark failed')
  }

  ElMessage.success(t('tag.bookmark_success'))
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
    throw new Error('Unbookmark failed')
  }

  ElMessage.success(t('tag.unbookmark_success'))
  return true
}

// 复制链接
const copyLink = (): void => {
  const link = window.location.href
  navigator.clipboard.writeText(link).then(() => {
    ElMessage.success(t('tag.copy_link_success'))
  })
}

// 写文章
const writeArticle = (): void => {
  window.open('/my-articles/create', '_blank')
}

// 监听路由参数变化，当标签slug变化时重新加载数据
watch(
  () => route.params.slug,
  (newSlug, oldSlug) => {
    if (newSlug && newSlug !== oldSlug) {
      loadTagPageInfo()
    }
  }
)

// 定义组件名称
defineOptions({ name: 'ListView' })
</script>

<style scoped>
.wy-container {
  display: flex;
  width: 1200px;
}
.wy-channel-intro {
  display: flex;
  flex-direction: column;
}
.wy-channel-body {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  width: 100%;
}
.wy-channel-body .info {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  gap: 0.5rem;
}
.wy-channel-body .info .name {
  font-size: 1.5rem;
  line-height: 2rem;
  font-weight: 600;
  color: var(--el-text-color-regular);
  margin-bottom: 0.5rem;
}
.wy-channel-body .info .secondary-info {
  color: var(--el-text-color-secondary);
  font-size: 1rem;
  line-height: 1.5rem;
  margin-bottom: 0.5rem;
}
.wy-channel-body .info .functions {
  margin-top: 0.6rem;
  margin-bottom: 0.5rem;
}
.wy-channel-description {
  background-color: var(--el-fill-color-light);
  margin-top: 0.6rem;
  padding-top: 0.75rem;
  padding-bottom: 0.75rem;
  padding-left: 1rem;
  padding-right: 1rem;
  font-size: 1.1rem;
  line-height: 1.75rem;
  gap: 1rem;
  border-radius: 0.5rem;
  z-index: 10;
}
.wy-channel-description .simple-description {
  display: flex;
}
.wy-channel-description .more-description {
  display: flex;
  flex-direction: column;
}
.wy-channel-description .simple-description .single-text {
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  line-clamp: 1;
  -webkit-line-clamp: 1;
}
.wy-channel-description .more-description .btn-collapse {
  display: flex;
  justify-content: center;
}

.wy-card-list-type {
  margin-bottom: 30px;
}
.wy-card-list-type .el-segmented {
  --el-segmented-item-selected-color: var(--el-color-primary);
  --el-segmented-item-selected-bg-color: var(--el-color-primary-light-7);
  --el-border-radius-base: 16px;
}
.wy-list-type-nav {
  display: flex;
  align-items: center;
}
.wy-card-radius {
  border-radius: 8px;
}
.wy-card:hover {
  cursor: pointer;
}
.wy-card:not(:first-of-type) {
  margin-top: 30px;
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
.wy-card-body .article-item {
  display: flex;
  flex-direction: column;
}
.wy-card-title {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--el-text-color-regular);
  margin-bottom: 1rem;
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

.wy-card-body .commenter-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.wy-card-body .commenter-item:not(:last-child) {
  margin-bottom: 1rem;
}
.wy-card-body .commenter-item .author-area {
  display: flex;
  align-items: center;
}
.wy-card-body .commenter-item .author-area .author {
  margin-left: 5px;
}
.wy-card-body .content,
.wy-card-body .info {
  display: flex;
  justify-content: space-between;
  padding-top: 15px;
}
.wy-card-body .info .right {
  display: flex;
}
.wy-card-body .content .right {
  width: 179px;
  height: 108px;
  border-radius: 8px;
}
.wy-card-body .content .left {
  display: flex;
  flex-direction: column;
  width: 500px;
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

.wy-channel-img-wrapper {
  display: block;
}
.wy-channel-img {
  position: relative;
  border-radius: 9999px;
  overflow: visible;
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
}
.wy-channel-img img {
  width: 3rem;
  height: 3rem;
  max-width: 100%;
  border-radius: 9999px;
  object-fit: cover;
}
.wy-channel-img svg {
  position: absolute;
  top: -168px;
  left: -176px;
  z-index: 0;
  opacity: 0.2;
}
.dark\:hidden {
  display: none;
}
.dark\:block {
  display: block;
}

.wy-load-more {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 30px;
}

.wy-no-more-data {
  text-align: center;
  color: #909399;
  font-size: 14px;
  padding: 20px 0;
}

@media only screen and (max-width: 767px) {
  .wy-container {
    display: flex;
    width: 100%;
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
    --el-main-padding: 10px;
  }
}
</style>
