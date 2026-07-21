<template>
  <div class="profile-container">
    <!-- 顶部用户信息 -->
    <div class="profile-header">
      <el-avatar class="avatar" :size="160">
        <img :src="userProfile.profile_image ||
          generateLetterAvatar(userProfile.full_name || userProfile.username)
          " alt="用户头像" />
      </el-avatar>
      <div class="user-info">
        <h1 class="username">{{ userProfile.full_name }}</h1>
        <p class="user-title">{{ userProfile.profile_tagline || '暂无简介' }}</p>
        <div class="user-meta">
          <span class="meta-item">{{ articleCount }} {{ t('profile.articles') }}</span>
          <span class="meta-item">{{ followersCount }} {{ t('profile.followers') }}</span>
          <el-button v-if="!isCurrentUser && isAuthenticated" type="primary" size="small" class="follow-btn"
            @click="handleFollowUser">
            {{ isFollowing ? t('profile.unfollow') : t('profile.follow') }}
          </el-button>
          <el-button v-if="isCurrentUser" type="primary" size="small" class="edit-btn" @click="handleEditProfile">
            {{ t('profile.edit_profile') }}
          </el-button>
        </div>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="profile-content">
      <div class="wy-profile-item">
        <div class="user-social">
          <el-icon class="social-icon">
            <user />
          </el-icon>
          <span>{{ userProfile.social_profiles?.github || t('profile.no_github') }}</span>
        </div>
        <div class="user-location">
          <el-icon class="location-icon">
            <location />
          </el-icon>
          <span>{{ userProfile.location || t('profile.no_location') }}</span>
        </div>
        <div class="user-join">
          <el-icon class="join-icon">
            <calendar />
          </el-icon>
          <span>{{ t('profile.member_since') }} {{ formattedJoinDate }}</span>
        </div>
      </div>

      <div class="wy-profile-item-line">
        <!-- 个人简介 -->
        <div class="info-card">
          <div class="card-header">
            <h2 class="card-title">{{ t('profile.about_me') }}</h2>
          </div>
          <div class="card-content">
            <p>{{ userProfile.profile_bio || t('profile.no_bio') }}</p>
          </div>
        </div>

        <!-- 技能栈 -->
        <div class="info-card">
          <div class="card-header">
            <h2 class="card-title">{{ t('profile.tech_stack') }}</h2>
          </div>
          <div class="card-content">
            <el-tag v-for="(skill, index) in userProfile.tech_stack" :key="index" class="mx-1" v-show="skill">
              {{ skill }}
            </el-tag>
            <p v-if="!userProfile.tech_stack || userProfile.tech_stack.length === 0">{{ t('profile.no_tech_stack') }}
            </p>
          </div>
        </div>

        <!--个人服务-->
        <div class="info-card">
          <div class="card-header">
            <h2 class="card-title">{{ t('profile.available_for') }}</h2>
          </div>
          <div class="card-content">
            <p>{{ userProfile.available_for || t('profile.no_available') }}</p>
          </div>
        </div>
      </div>

      <div class="info-card">
        <div class="card-header">
          <h2 class="card-title">{{ t('profile.recent_activity') }}</h2>
        </div>
        <div class="card-content">
          <el-timeline v-if="userActivities.length > 0" style="max-width: 600px">
            <el-timeline-item v-for="(activity, index) in userActivities" :key="index"
              :timestamp="formatDate(activity.time)" placement="top">
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
          <el-empty v-else :description="t('profile.no_activity')" :image-size="80" />
        </div>
      </div>

      <!-- 社交媒体链接 -->
      <el-card v-if="hasSocialLinks" class="social-card">
        <div class="card-header">
          <h2 class="card-title">{{ t('profile.social_media') }}</h2>
        </div>
        <div class="card-content">
          <ul class="social-links-list">
            <li v-for="platform in socialPlatforms" :key="platform.key" class="social-link-item">
              <IconifyIcon :icon="platform.icon" :color="platform.color" class="social-icon" />
              <span class="social-name">{{ platform.name }}</span>
              <a v-if="userProfile.social_profiles?.[platform.key]" :href="userProfile.social_profiles[platform.key]"
                target="_blank" rel="noopener noreferrer" class="social-link-text">
                {{ userProfile.social_profiles[platform.key] }}
              </a>
            </li>
          </ul>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElCard, ElButton, ElAvatar, ElTag, ElMessage, ElTimeline, ElTimelineItem, ElEmpty } from 'element-plus'
import { getUserByUsername, getUserActivity, checkUserFollowStatus, toggleUserFollow } from '@/api/services/user'
import { getUserArticles, getUserArticleCount } from '@/api/services/articles'
import { useAppStore } from '@/stores/app'
import type { TimelineActivity } from '@/api/services/user'
import { generateLetterAvatar } from '@/utils/avatarUtils'
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
  // 这里简化处理，实际应该比较用户ID或用户名
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

// 用户活动数据
const userActivities = ref<TimelineActivity[]>([])

// 关注相关数据
const isFollowing = ref(false)
const followersCount = ref(0)
const articleCount = ref(0)

// 格式化加入日期
const formattedJoinDate = computed(() => {
  if (!userProfile.value.createtime) return ''
  return formatDateTime(userProfile.value.createtime, 'YYYY年MM月DD日')
})

// 检查是否有社交媒体链接
const hasSocialLinks = computed(() => {
  const social = userProfile.value.social_profiles
  return social && (social.github || social.twitter || social.linkedin || social.website || social.weibo || social.zhihu || social.douyin || social.bilibili || social.xiaohongshu || social.gitee || social.instagram || social.dribbble || social.wechat)
})

// 社交媒体平台配置
const socialPlatforms = [
  { key: 'wechat', name: t('profile_edit.wechat'), icon: 'ic:baseline-wechat', color: '#07c160' },
  { key: 'weibo', name: t('profile_edit.weibo'), icon: 'ri:weibo-fill', color: '#e6162d' },
  { key: 'zhihu', name: t('profile_edit.zhihu'), icon: 'ant-design:zhihu-circle-filled', color: '#0084ff' },
  { key: 'douyin', name: t('profile_edit.douyin'), icon: 'mage:tiktok-circle', color: '#000000' },
  { key: 'bilibili', name: t('profile_edit.bilibili'), icon: 'streamline-ultimate:bilibili-logo-bold', color: '#00a1d6' },
  { key: 'xiaohongshu', name: t('profile_edit.xiaohongshu'), icon: 'simple-icons:xiaohongshu', color: '#ff2442' },
  { key: 'gitee', name: t('profile_edit.gitee'), icon: 'simple-icons:gitee', color: '#c71d23' },
  { key: 'github', name: 'GitHub', icon: 'mdi:github', color: '#333333' },
  { key: 'twitter', name: 'Twitter', icon: 'mdi:twitter', color: '#1da1f2' },
  { key: 'linkedin', name: 'LinkedIn', icon: 'mdi:linkedin', color: '#0077b5' },
  { key: 'instagram', name: 'Instagram', icon: 'mingcute:instagram-fill', color: '#e1306c' },
  { key: 'dribbble', name: 'Dribbble', icon: 'ant-design:dribbble-circle-filled', color: '#ea4c89' },
  { key: 'website', name: t('profile_edit.website'), icon: 'mdi:web', color: '#666666' }
]

// 加载用户数据
const loadUserData = async () => {
  try {
    // 获取用户基本信息
    const res = await getUserByUsername(username.value)
    userProfile.value = res.data || {}
    console.log(userProfile.value)

    // 获取用户文章数据
    const articlesRes = await getUserArticles(username.value, 10)
    userArticles.value = articlesRes.data || []

    // 获取用户文章总数
    const countRes = await getUserArticleCount(username.value)
    // 后端返回 {published: number, draft: number}，统计已发布的文章数
    articleCount.value = countRes.data?.published || 0

    // 获取用户最近活动
    const activityRes = await getUserActivity(username.value, 10)
    userActivities.value = activityRes.data?.activities || []
    console.log('User activity:', activityRes.data)

    // 获取关注者数量
    followersCount.value = userProfile.value.followers_count || 0
  } catch (error) {
    console.error('加载用户数据失败:', error)
    ElMessage.error(t('profile_edit.load_failed'))
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
</script>

<style scoped lang="scss">
@media (min-width: 1280px) {
  .profile-container {
    width: 1200px;
    margin: 40px auto;
    padding: 3.5rem 7rem 6rem;
    border-radius: 0.5rem;
    border: 1px solid #e0e0e0;
  }

  .wy-profile-item-line {
    flex-direction: row;
  }
}

@media (min-width: 1024px) and (max-width: 1279px) {
  .profile-container {
    width: 1200px;
    margin: 0 auto;
    padding: 3.5rem 2rem 6rem;
    border-radius: 0.5rem;
    border: 1px solid #e0e0e0;
  }

  .wy-profile-item-line {
    flex-direction: row;
  }
}

@media (max-width: 1023px) {

  .wy-profile-item-line {
    flex-direction: column;
  }

  .wy-profile-item {
    flex-direction: column;
  }
}

.profile-container {
  width: 1200px;
  margin: 40px auto;
  border-radius: 0.5rem;
}

.wy-profile-item {
  width: 100%;
  display: flex;
  gap: 20px;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
  border-radius: 0.5rem;
  border: 1px solid #e0e0e0;
  padding: 20px;

  .user-social {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .user-location,
  .user-join {
    display: flex;
    align-items: center;
    gap: 5px;
  }
}

.profile-header {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;

  .avatar {
    margin-right: 20px;
    // border: 4px solid #fff;
    // box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  }

  .user-info {
    flex: 1;

    .username {
      margin: 0 0 5px 0;
      font-size: 28px;
      font-weight: 600;
    }

    .user-title {
      margin: 0 0 15px 0;
      color: #666;
      font-size: 16px;
    }

    .user-meta {
      display: flex;
      align-items: center;
      gap: 20px;
      flex-wrap: wrap;

      .meta-item {
        color: #888;
        font-size: 14px;
      }
    }
  }
}

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.wy-profile-item-line {
  display: flex;
  gap: 20px;
}

.info-card,
.social-card {
  border-radius: 0.5rem;
  border: 1px solid #e0e0e0;
  padding: 20px;
  width: 100%;
  min-height: 340px;

  .card-header {
    margin-bottom: 15px;

    .card-title {
      margin: 0;
      font-size: 18px;
      font-weight: 500;
    }
  }

  .card-content {
    p {
      margin: 0;
      color: #666;
      line-height: 1.6;
    }

    span {
      margin-right: 5px;
    }

    .social-links-list {
      list-style: none;
      padding: 0;
      margin: 0;

      .social-link-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 0;
        border-bottom: 1px solid #f0f0f0;

        &:last-child {
          border-bottom: none;
        }

        .social-icon {
          font-size: 24px;
          flex-shrink: 0;
        }

        .social-name {
          font-weight: 500;
          color: #333;
          min-width: 80px;
        }

        .social-link-text {
          color: #999;
          text-decoration: none;
          font-size: 14px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          max-width: 400px;
          transition: color 0.3s;

          &:hover {
            color: #409eff;
          }
        }
      }
    }
  }
}

.articles-section {
  .section-title {
    margin: 0 0 15px 0;
    font-size: 20px;
    font-weight: 500;
  }

  .articles-list {}

  .empty-articles {
    padding: 40px 0;
    text-align: center;
    color: #999;
  }
}

.article-card {
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  }

  .article-item {
    .article-content {
      .article-title {
        margin: 0 0 10px 0;
        font-size: 18px;
        font-weight: 500;
        color: #333;
      }

      .article-excerpt {
        margin: 0 0 10px 0;
        color: #666;
        line-height: 1.5;
        display: -webkit-box;
        line-clamp: 2;
        box-orient: vertical;
        overflow: hidden;
      }

      .article-meta {
        display: flex;
        gap: 20px;
        font-size: 14px;
        color: #888;

        .meta-date,
        .meta-reads {
          display: flex;
          align-items: center;
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .profile-header {
    flex-direction: column;
    text-align: center;

    .user-info {
      .user-meta {
        flex-direction: column;
        gap: 10px;
      }
    }
  }
}

// 活动相关样式
.activity-item {
  .activity-content {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;

    .activity-link {
      color: #409eff;
      text-decoration: none;
      font-weight: 500;

      &:hover {
        text-decoration: underline;
      }
    }

    .activity-action {
      color: #666;
      font-size: 14px;
    }

    .comment-text {
      margin: 8px 0 0 0;
      padding: 8px 12px;
      background-color: #f5f7fa;
      border-radius: 4px;
      color: #666;
      font-size: 14px;
      font-style: italic;
    }
  }
}
</style>
