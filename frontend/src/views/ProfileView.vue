<template>
  <div class="profile-page">
    <!-- 通栏头部：背景色由头像主色动态生成 -->
    <header class="profile-hero" :style="heroVars">
      <div class="hero-inner">
        <el-avatar class="hero-avatar" :size="112">
          <img
            :src="
              userProfile.profile_image ||
              generateLetterAvatar(userProfile.full_name || userProfile.username)
            "
            alt="用户头像"
          />
        </el-avatar>
        <h1 class="hero-name">{{ userProfile.full_name }}</h1>
        <div class="hero-meta">
          <span class="meta-item">@{{ userProfile.username }}</span>
          <span v-if="locationShort" class="meta-item">
            <el-icon><location /></el-icon>
            <span class="meta-text">{{ locationShort }}</span>
          </span>
          <span v-if="formattedJoinDate" class="meta-item">
            <el-icon><calendar /></el-icon>
            <span class="meta-text">{{ t('profile.member_since') }} {{ formattedJoinDate }}</span>
          </span>
          <span class="meta-item">{{ articleCount }} {{ t('profile.articles') }}</span>
          <span class="meta-item">{{ followersCount }} {{ t('profile.followers') }}</span>
        </div>
        <p v-if="userProfile.profile_tagline" class="hero-tagline">
          {{ userProfile.profile_tagline }}
        </p>
        <div class="hero-actions">
          <a
            v-if="websiteUrl"
            class="action-btn action-website"
            :href="websiteUrl"
            target="_blank"
            rel="noopener noreferrer"
          >
            <el-icon><LinkIcon /></el-icon>
            <span>{{ t('profile.website') }}</span>
          </a>
          <button class="action-btn" type="button" @click="handleShare">
            <el-icon><share /></el-icon>
            <span>{{ t('profile.share') }}</span>
          </button>
          <a
            v-for="s in headerSocials"
            :key="s.key"
            class="action-icon"
            :href="s.url"
            target="_blank"
            rel="noopener noreferrer"
            :title="s.title"
          >
            <IconifyIcon :icon="s.icon" class="action-icon-glyph" />
          </a>
          <span
            v-for="s in headerSocialStatics"
            :key="s.key"
            class="action-icon action-icon-static"
            :title="`${s.title}: ${s.value}`"
          >
            <IconifyIcon :icon="s.icon" class="action-icon-glyph" />
          </span>
          <el-button
            v-if="!isCurrentUser && isAuthenticated"
            type="primary"
            size="small"
            class="action-follow"
            @click="handleFollowUser"
          >
            {{ isFollowing ? t('profile.unfollow') : t('profile.follow') }}
          </el-button>
          <el-button
            v-if="isCurrentUser"
            type="primary"
            size="small"
            class="action-follow"
            @click="handleEditProfile"
          >
            {{ t('profile.edit_profile') }}
          </el-button>
        </div>
      </div>
    </header>

    <!-- 主体双栏 -->
    <div class="profile-body">
      <main class="profile-main">
        <div class="profile-tabs" role="tablist">
          <button
            type="button"
            class="profile-tab"
            :class="{ active: activeTab === 'articles' }"
            role="tab"
            :aria-selected="activeTab === 'articles'"
            @click="activeTab = 'articles'"
          >
            {{ t('profile.tab_articles') }}
            <span class="tab-count">{{ articleCount }}</span>
          </button>
          <button
            type="button"
            class="profile-tab"
            :class="{ active: activeTab === 'comments' }"
            role="tab"
            :aria-selected="activeTab === 'comments'"
            @click="activeTab = 'comments'"
          >
            {{ t('profile.tab_comments') }}
            <span class="tab-count">{{ commentsTotal }}</span>
          </button>
          <button
            type="button"
            class="profile-tab"
            :class="{ active: activeTab === 'activity' }"
            role="tab"
            :aria-selected="activeTab === 'activity'"
            @click="activeTab = 'activity'"
          >
            {{ t('profile.tab_activity') }}
            <span class="tab-count">{{ activityTotal }}</span>
          </button>
        </div>

        <!-- 文章列表 -->
        <div v-if="activeTab === 'articles'" class="article-list">
          <article
            v-for="a in userArticles"
            :key="a.id"
            class="article-item"
            @click="navigateToArticle(a.slug)"
          >
            <h3 class="article-title">{{ a.title }}</h3>
            <p v-if="a.subtitle" class="article-excerpt">{{ a.subtitle }}</p>
            <div class="article-meta">
              <span class="meta-piece">
                <el-icon><calendar /></el-icon>
                {{ formatDate(a.pub_time || a.createtime) }}
              </span>
              <span class="meta-piece">
                <el-icon><ViewIcon /></el-icon>
                {{ a.reads || 0 }} {{ t('profile.reads') }}
              </span>
            </div>
          </article>
          <el-empty
            v-if="userArticles.length === 0"
            :description="t('profile.no_articles')"
            :image-size="80"
          />
          <div v-if="hasMoreArticles" class="load-more-wrap">
            <button class="load-more-btn" type="button" :disabled="articleLoading" @click="loadMoreArticles">
              {{ articleLoading ? t('profile.loading') : t('profile.load_more') }}
            </button>
          </div>
        </div>

        <!-- 评论列表 -->
        <div v-else-if="activeTab === 'comments'" class="comment-list">
          <div v-for="c in userComments" :key="c.id" class="comment-item">
            <div class="comment-avatar" aria-hidden="true">{{ commentInitial }}</div>
            <div class="comment-body">
              <div class="comment-bubble">{{ c.comment }}</div>
              <div class="comment-meta">
                <router-link :to="`/article/${c.article_slug}`" class="comment-article">
                  <el-icon><document /></el-icon>
                  <span class="comment-article-title">{{ c.article_title }}</span>
                </router-link>
                <span class="meta-dot">·</span>
                <span>{{ formatDate(c.createtime) }}</span>
                <template v-if="c.likes > 0">
                  <span class="meta-dot">·</span>
                  <span class="meta-piece">
                    <el-icon><caret-top /></el-icon>
                    {{ c.likes }}
                  </span>
                </template>
              </div>
            </div>
          </div>
          <el-empty
            v-if="userComments.length === 0"
            :description="t('profile.no_comments')"
            :image-size="80"
          />
        </div>

        <!-- 动态时间线 -->
        <div v-else class="activity-panel">
          <el-timeline v-if="userActivities.length > 0" class="activity-timeline">
            <el-timeline-item
              v-for="(activity, index) in userActivities"
              :key="index"
              :timestamp="formatDate(activity.time)"
              placement="top"
            >
              <div class="activity-item">
                <!-- 发布文章 -->
                <div v-if="activity.type === 'article'" class="activity-content">
                  <el-tag type="primary" size="small">{{ t('profile.article_published') }}</el-tag>
                  <router-link :to="`/article/${activity.slug}`" class="activity-link">
                    {{ activity.title }}
                  </router-link>
                </div>

                <!-- 点赞文章 -->
                <div v-else-if="activity.type === 'like'" class="activity-content">
                  <el-tag type="warning" size="small">{{ t('profile.article_liked') }}</el-tag>
                  <span class="activity-action">{{ t('profile.liked_article') }}</span>
                  <router-link :to="`/article/${activity.article_slug}`" class="activity-link">
                    {{ activity.article_title }}
                  </router-link>
                </div>

                <!-- 收藏文章 -->
                <div v-else-if="activity.type === 'bookmark'" class="activity-content">
                  <el-tag type="success" size="small">{{ t('profile.article_bookmarked') }}</el-tag>
                  <span class="activity-action">{{ t('profile.bookmarked_article') }}</span>
                  <router-link :to="`/article/${activity.article_slug}`" class="activity-link">
                    {{ activity.article_title }}
                  </router-link>
                </div>

                <!-- 评论文章 -->
                <div v-else-if="activity.type === 'comment'" class="activity-content">
                  <el-tag type="info" size="small">{{ t('profile.article_commented') }}</el-tag>
                  <span class="activity-action">{{ t('profile.commented_article') }}</span>
                  <router-link :to="`/article/${activity.article_slug}`" class="activity-link">
                    {{ activity.article_title }}
                  </router-link>
                  <p class="comment-text">"{{ activity.comment_content }}"</p>
                </div>
              </div>
            </el-timeline-item>
          </el-timeline>
          <el-empty
            v-if="userActivities.length === 0"
            :description="t('profile.no_activity')"
            :image-size="80"
          />
        </div>
      </main>

      <!-- 右侧栏 -->
      <aside class="profile-side">
        <div class="side-card">
          <h3 class="side-title">{{ t('profile.about_me') }}</h3>
          <p class="side-text">{{ userProfile.profile_bio || t('profile.no_bio') }}</p>
        </div>
        <div class="side-card">
          <h3 class="side-title">{{ t('profile.available_for') }}</h3>
          <p class="side-text">{{ userProfile.available_for || t('profile.no_available') }}</p>
        </div>
        <div v-if="techStackList.length > 0" class="side-card">
          <h3 class="side-title">{{ t('profile.tech_stack') }}</h3>
          <div class="side-tags">
            <el-tag v-for="(skill, index) in techStackList" :key="index" size="small">{{
              skill
            }}</el-tag>
          </div>
        </div>
        <!-- blog 入口：仅当用户开通博客时显示 -->
        <div v-if="blogInfo" class="side-card side-blog-card">
          <h3 class="side-title">
            {{ t('profile.blogs_title', { name: userProfile.full_name || username }) }}
          </h3>
          <div class="blog-entry" @click="goBlog">
            <div class="blog-entry-icon">
              <IconifyIcon icon="mdi:web" />
            </div>
            <div class="blog-entry-main">
              <div class="blog-entry-name">{{ blogInfo.blogName }}</div>
              <div class="blog-entry-meta">
                @{{ username }} · {{ blogInfo.posts }} {{ t('profile.blog_posts') }}
              </div>
            </div>
            <el-icon class="blog-entry-arrow"><ArrowRight /></el-icon>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElButton, ElAvatar, ElTag, ElMessage, ElEmpty, ElIcon, ElTimeline, ElTimelineItem } from 'element-plus'
import {
  Location,
  Calendar,
  Share,
  Link as LinkIcon,
  Document,
  CaretTop,
  View as ViewIcon,
  ArrowRight
} from '@element-plus/icons-vue'
import {
  getUserByUsername,
  getUserComments,
  getUserActivity,
  checkUserFollowStatus,
  toggleUserFollow
} from '@/api/services/user'
import type { UserCommentItem, TimelineActivity } from '@/api/services/user'
import { getUserArticles, getUserArticleCount } from '@/api/services/articles'
import { getBlogSite, getBlogArticles } from '@/api/services/creator'
import { useAppStore } from '@/stores/app'
import { generateLetterAvatar } from '@/utils/avatarUtils'
import { getHeroPalette } from '@/utils/avatarColor'
import type { HeroPalette } from '@/utils/avatarColor'
import { formatDateTime } from '@/utils/dateUtils'
import IconifyIcon from '@/components/IconIfy.vue'

// 初始化路由和i18n
const router = useRouter()
const route = useRoute()
const { t } = useI18n()
const appStore = useAppStore()

// 获取用户名参数
const username = computed(() => route.params.username as string)

// 检查是否已认证
const isAuthenticated = computed(() => !!appStore.token)

// 检查是否为当前登录用户
const isCurrentUser = computed(() => {
  return isAuthenticated.value && appStore.userInfo?.username === username.value
})

// 用户资料数据
const userProfile = ref<any>({})

// 用户文章数据
const userArticles = ref<
  Array<{
    id: number
    title: string
    slug: string
    subtitle: string | null
    cover: string | null
    pub_time: number
    createtime: number
    reads: number
  }>
>([])

// 用户评论数据
const userComments = ref<UserCommentItem[]>([])
const commentsTotal = ref(0)

// 用户动态数据（时间线）
const userActivities = ref<TimelineActivity[]>([])
const activityTotal = ref(0)

// 文章分页
const ARTICLE_PAGE_SIZE = 10
const articleLoading = ref(false)
const hasMoreArticles = computed(() => userArticles.value.length < articleCount.value)

// 关注相关数据
const isFollowing = ref(false)
const followersCount = ref(0)
const articleCount = ref(0)

// 右侧栏 blog 入口（仅当用户开通博客时显示）
const blogInfo = ref<{ blogName: string; posts: number } | null>(null)

// Tab 状态
const activeTab = ref<'articles' | 'comments' | 'activity'>('articles')

// 头部配色（头像主色动态生成）
const palette = ref<HeroPalette>({
  base: '#3a6ea5',
  light: '#dbe7f5',
  lightSoft: '#eef3fa',
  dark: '#1d2c40',
  darkSoft: '#141c28'
})

const isDark = computed(() => appStore.isDark)

const heroVars = computed(() => ({
  '--hero-c1': isDark.value ? palette.value.dark : palette.value.light,
  '--hero-c2': isDark.value ? palette.value.darkSoft : palette.value.lightSoft
}))

// 根据头像更新配色
const refreshHeroPalette = async () => {
  const next = await getHeroPalette(
    userProfile.value.profile_image,
    userProfile.value.username || username.value || ''
  )
  palette.value = next
}

// 格式化加入日期
const formattedJoinDate = computed(() => {
  if (!userProfile.value.createtime) return ''
  return formatDateTime(userProfile.value.createtime, 'YYYY年MM月DD日')
})

// 头像首字母（评论列表用）
const commentInitial = computed(() => {
  const name = userProfile.value.full_name || userProfile.value.username || 'U'
  return name.trim().charAt(0).toUpperCase()
})

// 技术栈
const techStackList = computed(() => {
  const list = userProfile.value.tech_stack
  return Array.isArray(list) ? list.filter((s: any) => !!s) : []
})

// 网站链接（social_profiles.website，自动补协议）
const websiteUrl = computed(() => {
  const site = userProfile.value.social_profiles?.website
  if (!site) return ''
  return /^https?:\/\//i.test(site) ? site : `https://${site}`
})

// 地点精简：只显示到省/直辖市一级（如 China, 天津 / Japan, Tokyo）
const locationShort = computed(() => {
  const loc = userProfile.value.location
  if (!loc) return ''
  const parts = String(loc)
    .split(/[，,]/)
    .map((s: string) => s.trim())
    .filter(Boolean)
  if (parts.length >= 2) return `${parts[0]}, ${parts[1]}`
  return parts[0] || ''
})

// 社媒平台配置（全量；website 单独用胶囊按钮展示，不在图标区重复）
const SOCIAL_PLATFORM_DEFS = [
  { key: 'wechat', icon: 'ic:baseline-wechat', title: 'WeChat' },
  { key: 'weibo', icon: 'ri:weibo-fill', title: 'Weibo' },
  { key: 'zhihu', icon: 'ant-design:zhihu-circle-filled', title: 'Zhihu' },
  { key: 'douyin', icon: 'mage:tiktok-circle', title: 'Douyin' },
  { key: 'bilibili', icon: 'streamline-ultimate:bilibili-logo-bold', title: 'Bilibili' },
  { key: 'xiaohongshu', icon: 'simple-icons:xiaohongshu', title: 'Xiaohongshu' },
  { key: 'gitee', icon: 'simple-icons:gitee', title: 'Gitee' },
  { key: 'github', icon: 'mdi:github', title: 'GitHub' },
  { key: 'twitter', icon: 'mdi:twitter', title: 'Twitter' },
  { key: 'linkedin', icon: 'mdi:linkedin', title: 'LinkedIn' },
  { key: 'instagram', icon: 'mingcute:instagram-fill', title: 'Instagram' },
  { key: 'dribbble', icon: 'ant-design:dribbble-circle-filled', title: 'Dribbble' }
]

// 值是否像网址（可点击跳转）；微信号这类纯 ID 只展示图标 + 悬浮提示
const looksLikeUrl = (v: string) => /^https?:\/\//i.test(v) || (/^[^\s]+\.[^\s]+/.test(v) && !/\s/.test(v))

// 头部社媒图标：可跳转的渲染为链接
const headerSocials = computed(() => {
  const social = userProfile.value.social_profiles || {}
  return SOCIAL_PLATFORM_DEFS.filter((d) => !!social[d.key] && looksLikeUrl(social[d.key])).map(
    (d) => ({
      ...d,
      url: /^https?:\/\//i.test(social[d.key]) ? social[d.key] : `https://${social[d.key]}`
    })
  )
})

// 头部社媒图标：非链接（如微信号）渲染为静态图标，悬浮显示账号
const headerSocialStatics = computed(() => {
  const social = userProfile.value.social_profiles || {}
  return SOCIAL_PLATFORM_DEFS.filter((d) => !!social[d.key] && !looksLikeUrl(social[d.key])).map(
    (d) => ({ ...d, value: social[d.key] })
  )
})

// 加载用户数据
const loadUserData = async () => {
  try {
    // 获取用户基本信息
    const res = await getUserByUsername(username.value)
    userProfile.value = res.data || {}

    // 头部配色依赖头像
    refreshHeroPalette()

    // 获取用户文章数据（仅已发布，与文章总数口径一致；接口返回 {list,total}）
    const articlesRes = await getUserArticles(username.value, ARTICLE_PAGE_SIZE, 'published')
    userArticles.value = articlesRes.data?.list || []

    // 获取用户文章总数
    const countRes = await getUserArticleCount(username.value)
    // 后端返回 {published: number, draft: number}，统计已发布的文章数
    articleCount.value = countRes.data?.published || 0

    // 获取用户评论列表
    const commentsRes = await getUserComments(username.value, 10)
    userComments.value = commentsRes.data?.list || []
    commentsTotal.value = commentsRes.data?.total || 0

    // 获取用户动态（时间线）
    const activityRes = await getUserActivity(username.value, 10)
    userActivities.value = activityRes.data?.activities || []
    activityTotal.value = activityRes.data?.total || userActivities.value.length

    // 获取关注者数量
    followersCount.value = userProfile.value.followers_count || 0

    // 获取 blog 入口信息（失败不影响主流程）
    await loadBlogInfo()
  } catch (error) {
    console.error('加载用户数据失败:', error)
    ElMessage.error(t('profile_edit.load_failed'))
  }
}

// 加载右侧栏 blog 入口：仅当用户开通博客时显示名称与文章数
const loadBlogInfo = async () => {
  blogInfo.value = null
  try {
    const siteRes = await getBlogSite(username.value)
    const site = siteRes.data
    if (!site?.blog?.opened) return
    // 已发布文章数作为 posts 数（limit=1 仅取 total）
    const articlesRes = await getBlogArticles(username.value, { limit: 1 })
    blogInfo.value = {
      blogName: site.blog.blog_name || site.user?.full_name || username.value,
      posts: articlesRes.data?.total || 0
    }
  } catch (error) {
    // blog 入口是附加信息，加载失败静默忽略
    console.error('加载 blog 入口信息失败:', error)
  }
}

// 点击 blog 入口：跳转该用户的个人博客首页
const goBlog = () => {
  router.push(`/blog/${username.value}`)
}

// 「加载更多」：追加下一页文章
const loadMoreArticles = async () => {
  if (articleLoading.value) return
  articleLoading.value = true
  try {
    const res = await getUserArticles(
      username.value,
      ARTICLE_PAGE_SIZE,
      'published',
      userArticles.value.length
    )
    const list = res.data?.list || []
    // 去重追加（防翻页期间有新文章导致重复）
    const seen = new Set(userArticles.value.map((a) => a.id))
    userArticles.value.push(...list.filter((a: any) => !seen.has(a.id)))
  } catch (error) {
    console.error('加载更多文章失败:', error)
    ElMessage.error(t('profile_edit.load_failed'))
  } finally {
    articleLoading.value = false
  }
}

// 关注/取消关注用户
const handleFollowUser = async () => {
  if (!isAuthenticated.value) {
    ElMessage.warning(t('profile_edit.please_login'))
    return
  }

  try {
    const res = await toggleUserFollow(username.value)
    if (res.code === 1) {
      isFollowing.value = res.data.is_following
      followersCount.value += res.data.is_following ? 1 : -1
      ElMessage.success(res.data.message)
    }
  } catch (error) {
    console.error('关注操作失败:', error)
    ElMessage.error(t('profile_edit.save_failed'))
  }
}

// 分享（复制个人主页链接）
const handleShare = async () => {
  try {
    await navigator.clipboard.writeText(window.location.href)
    ElMessage.success(t('profile.link_copied'))
  } catch {
    ElMessage.error(t('profile.share_failed'))
  }
}

// 加载关注状态
const loadFollowStatus = async () => {
  if (!isAuthenticated.value || isCurrentUser.value) return

  try {
    const res = await checkUserFollowStatus(username.value)
    if (res.code === 1) {
      isFollowing.value = res.data.is_following
    }
  } catch (error) {
    console.error('加载关注状态失败:', error)
  }
}

// 导航到文章详情
const navigateToArticle = (slug: string) => {
  router.push(`/article/${slug}`)
}

// 格式化日期
const formatDate = (dateValue: string | number) => {
  if (!dateValue) return ''
  // 如果是数字，当作 Unix 时间戳处理（秒级）
  if (typeof dateValue === 'number') {
    return new Date(dateValue * 1000).toLocaleDateString('zh-CN')
  }
  // 如果是字符串，直接解析
  return new Date(dateValue).toLocaleDateString('zh-CN')
}

// 处理编辑个人资料
const handleEditProfile = () => {
  router.push('/profile/edit')
}

// 组件挂载时加载数据
onMounted(() => {
  loadUserData()
  loadFollowStatus()
})

// 用户名变化时重新加载
watch(username, () => {
  userArticles.value = []
  userComments.value = []
  userActivities.value = []
  commentsTotal.value = 0
  activityTotal.value = 0
  loadUserData()
  loadFollowStatus()
  activeTab.value = 'articles'
})
</script>

<style scoped lang="scss">
.profile-page {
  width: 100%;
  min-height: 100%;
  background: var(--wy-bg-canvas, #fafafa);
  padding: 15px;
}

/* ===== 通栏头部 ===== */
.profile-hero {
  width: 100%;
  border-radius: 24px 24px 0 0;
  background:
    radial-gradient(90% 130% at 50% -30%, var(--hero-c1) 0%, transparent 62%),
    linear-gradient(180deg, var(--hero-c2) 0%, transparent 100%), var(--wy-bg-canvas, #fafafa);
  padding: 56px 24px 28px;
  text-align: center;
  transition: background var(--wy-duration, 160ms) var(--wy-easing, ease);
}

.hero-inner {
  max-width: 720px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.hero-avatar {
  border: 4px solid var(--wy-bg-surface, #fff);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  background: var(--wy-bg-surface, #fff);
}

.hero-name {
  margin: 18px 0 10px;
  font-size: 30px;
  font-weight: 700;
  color: var(--wy-text-primary, #18181b);
  line-height: 1.25;
}

.hero-meta {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 6px 18px;
  color: var(--wy-text-tertiary, #71717a);
  font-size: 14px;

  .meta-item {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    max-width: 260px;
  }

  .meta-text {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .el-icon {
    font-size: 15px;
    flex-shrink: 0;
  }
}

.hero-tagline {
  margin: 14px 0 0;
  color: var(--wy-text-secondary, #52525b);
  font-size: 16px;
  line-height: 1.6;
  max-width: 640px;
}

.hero-actions {
  margin-top: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 10px;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  height: 36px;
  padding: 0 16px;
  border-radius: var(--wy-radius-pill, 999px);
  border: 1px solid var(--wy-border-strong, #d4d4d8);
  background: var(--wy-bg-surface, #fff);
  color: var(--wy-text-primary, #18181b);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
  transition: all var(--wy-duration, 160ms) var(--wy-easing, ease);

  &:hover {
    border-color: var(--wy-text-tertiary, #71717a);
    box-shadow: var(--wy-shadow-card, 0 2px 12px rgba(24, 24, 27, 0.06));
  }

  .el-icon {
    font-size: 16px;
  }
}

.action-website {
  background: var(--wy-text-primary, #18181b);
  border-color: var(--wy-text-primary, #18181b);
  color: var(--wy-bg-surface, #fff);

  &:hover {
    opacity: 0.88;
    border-color: var(--wy-text-primary, #18181b);
  }
}

.action-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid var(--wy-border-strong, #d4d4d8);
  background: var(--wy-bg-surface, #fff);
  color: var(--wy-text-secondary, #52525b);
  text-decoration: none;
  transition: all var(--wy-duration, 160ms) var(--wy-easing, ease);

  &:hover {
    border-color: var(--wy-text-tertiary, #71717a);
    box-shadow: var(--wy-shadow-card, 0 2px 12px rgba(24, 24, 27, 0.06));
  }

  .action-icon-glyph {
    font-size: 18px;
  }
}

.action-follow {
  margin-left: 4px;
}

/* ===== 主体双栏 ===== */
.profile-body {
  max-width: 1120px;
  margin: 0 auto;
  padding: 36px 24px 72px;
  display: flex;
  gap: 40px;
  align-items: flex-start;
}

.profile-main {
  flex: 1;
  min-width: 0;
}

.profile-side {
  width: 320px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Tabs */
.profile-tabs {
  display: flex;
  gap: 24px;
  border-bottom: 1px solid var(--wy-border-subtle, #e4e4e7);
  margin-bottom: 20px;
}

.profile-tab {
  appearance: none;
  background: none;
  border: none;
  padding: 10px 2px 12px;
  margin-bottom: -1px;
  font-size: 15px;
  font-weight: 500;
  color: var(--wy-text-tertiary, #71717a);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  transition: color var(--wy-duration, 160ms) var(--wy-easing, ease);

  &:hover {
    color: var(--wy-text-primary, #18181b);
  }

  &.active {
    color: var(--wy-text-primary, #18181b);
    border-bottom-color: var(--wy-text-primary, #18181b);
  }

  .tab-count {
    font-size: 12px;
    color: var(--wy-text-tertiary, #71717a);
    background: var(--wy-bg-muted, #f5f5f5);
    border-radius: var(--wy-radius-pill, 999px);
    padding: 1px 8px;
    line-height: 1.5;
  }
}

/* 文章列表 */
.article-list {
  display: flex;
  flex-direction: column;
}

.article-item {
  padding: 18px 4px;
  border-bottom: 1px solid var(--wy-border-subtle, #e4e4e7);
  cursor: pointer;
  transition: background var(--wy-duration, 160ms) var(--wy-easing, ease);

  &:hover .article-title {
    color: var(--wy-brand, #2f5fd0);
  }

  .article-title {
    margin: 0 0 6px;
    font-size: 17px;
    font-weight: 600;
    color: var(--wy-text-primary, #18181b);
    line-height: 1.45;
    transition: color var(--wy-duration, 160ms) var(--wy-easing, ease);
  }

  .article-excerpt {
    margin: 0 0 10px;
    color: var(--wy-text-secondary, #52525b);
    font-size: 14px;
    line-height: 1.6;
    display: -webkit-box;
    line-clamp: 2;
    box-orient: vertical;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .article-meta {
    display: flex;
    align-items: center;
    gap: 16px;
    font-size: 13px;
    color: var(--wy-text-tertiary, #71717a);

    .meta-piece {
      display: inline-flex;
      align-items: center;
      gap: 4px;

      .el-icon {
        font-size: 14px;
      }
    }
  }
}

/* 评论列表 */
.comment-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.comment-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.comment-avatar {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--wy-bg-muted, #f5f5f5);
  border: 1px solid var(--wy-border-subtle, #e4e4e7);
  color: var(--wy-text-secondary, #52525b);
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}

.comment-body {
  flex: 1;
  min-width: 0;
}

.comment-bubble {
  background: var(--wy-bg-muted, #f5f5f5);
  border-radius: 4px 12px 12px 12px;
  padding: 12px 14px;
  color: var(--wy-text-primary, #18181b);
  font-size: 14px;
  line-height: 1.65;
  word-break: break-word;
}

.comment-meta {
  margin-top: 8px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  font-size: 13px;
  color: var(--wy-text-tertiary, #71717a);

  .comment-article {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    color: var(--wy-text-tertiary, #71717a);
    text-decoration: none;
    max-width: 380px;
    transition: color var(--wy-duration, 160ms) var(--wy-easing, ease);

    &:hover {
      color: var(--wy-brand, #2f5fd0);

      .comment-article-title {
        text-decoration: underline;
      }
    }

    .el-icon {
      font-size: 14px;
      flex-shrink: 0;
    }

    .comment-article-title {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }

  .meta-dot {
    color: var(--wy-text-placeholder, #a1a1aa);
  }

  .meta-piece {
    display: inline-flex;
    align-items: center;
    gap: 3px;

    .el-icon {
      font-size: 14px;
    }
  }
}

/* 右侧栏卡片 */
.side-card {
  background: var(--wy-bg-surface, #fff);
  border: 1px solid var(--wy-border-subtle, #e4e4e7);
  border-radius: var(--wy-radius-lg, 12px);
  padding: 18px 20px;

  .side-title {
    margin: 0 0 10px;
    font-size: 15px;
    font-weight: 600;
    color: var(--wy-text-primary, #18181b);
  }

  .side-text {
    margin: 0;
    font-size: 14px;
    line-height: 1.7;
    color: var(--wy-text-secondary, #52525b);
    white-space: pre-wrap;
    word-break: break-word;
  }

  .side-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
}

/* blog 入口卡片 */
.side-blog-card {
  .blog-entry {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    border: 1px solid var(--wy-border-subtle, #e4e4e7);
    border-radius: 10px;
    background: var(--wy-bg-muted, #fafafa);
    cursor: pointer;
    transition:
      border-color 0.2s,
      background 0.2s;

    &:hover {
      border-color: var(--wy-primary, #409eff);
      background: var(--wy-bg-surface, #fff);
    }
  }

  .blog-entry-icon {
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border-radius: 8px;
    background: var(--wy-primary-soft, #ecf5ff);
    color: var(--wy-primary, #409eff);
    font-size: 18px;
  }

  .blog-entry-main {
    flex: 1 1 auto;
    min-width: 0;
  }

  .blog-entry-name {
    font-size: 14px;
    font-weight: 600;
    color: var(--wy-text-primary, #18181b);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .blog-entry-meta {
    margin-top: 2px;
    font-size: 12px;
    color: var(--wy-text-secondary, #52525b);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .blog-entry-arrow {
    flex: 0 0 auto;
    font-size: 15px;
    color: var(--wy-text-tertiary, #a1a1aa);
  }
}

/* 加载更多 */
.load-more-wrap {
  display: flex;
  justify-content: center;
  padding: 22px 0 4px;
}

.load-more-btn {
  appearance: none;
  background: var(--wy-bg-surface, #fff);
  border: 1px solid var(--wy-border-strong, #d4d4d8);
  border-radius: var(--wy-radius-pill, 999px);
  padding: 8px 26px;
  font-size: 14px;
  color: var(--wy-text-secondary, #52525b);
  cursor: pointer;
  transition: all var(--wy-duration, 160ms) var(--wy-easing, ease);

  &:hover:not(:disabled) {
    color: var(--wy-brand, #2f5fd0);
    border-color: var(--wy-brand, #2f5fd0);
  }

  &:disabled {
    opacity: 0.6;
    cursor: default;
  }
}

/* 动态时间线 */
.activity-panel {
  padding-top: 8px;
}

.activity-timeline {
  max-width: 640px;
  padding-left: 4px;
}

.activity-item {
  .activity-content {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;

    .activity-link {
      color: var(--wy-brand, #2f5fd0);
      text-decoration: none;
      font-weight: 500;

      &:hover {
        text-decoration: underline;
      }
    }

    .activity-action {
      color: var(--wy-text-secondary, #52525b);
      font-size: 14px;
    }

    .comment-text {
      width: 100%;
      margin: 8px 0 0 0;
      padding: 8px 12px;
      background: var(--wy-bg-muted, #f5f5f5);
      border-radius: 4px 12px 12px 12px;
      color: var(--wy-text-secondary, #52525b);
      font-size: 14px;
      font-style: italic;
    }
  }
}

/* 社媒图标垂直居中：IconifyIcon 根节点是 div，撑满后内部 flex 居中 */
.action-icon .action-icon-glyph {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

/* 非链接社媒图标（微信号等纯账号值） */
.action-icon-static {
  cursor: default;

  &:hover {
    border-color: var(--wy-border-strong, #d4d4d8);
    box-shadow: none;
  }
}

/* ===== 响应式 ===== */
@media (max-width: 1023px) {
  .profile-body {
    flex-direction: column;
    gap: 28px;
  }

  .profile-side {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .profile-hero {
    border-radius: 16px 16px 0 0;
    padding: 40px 16px 24px;
  }

  .hero-name {
    font-size: 24px;
  }

  .hero-meta {
    gap: 6px 12px;
    font-size: 13px;

    .meta-item {
      max-width: 100%;
    }
  }

  .hero-tagline {
    font-size: 14px;
  }

  .profile-body {
    padding: 24px 16px 56px;
  }
}
</style>
