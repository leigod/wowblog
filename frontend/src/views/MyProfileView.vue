<template>
  <div class="profile-container">
    <!-- 顶部用户信息 -->
    <div class="profile-header">
      <el-avatar class="avatar" :size="100">
        <img
          :src="userProfile.avatarUrl || generateLetterAvatar(userProfile.name)"
          alt="用户头像"
        />
      </el-avatar>
      <div class="user-info">
        <h1 class="username">{{ userProfile.name }}</h1>
        <p class="user-tagline">{{ userProfile.tagline }}</p>
        <div class="user-meta">
          <span class="meta-item">Member Since {{ userProfile.joinDate }}</span>
          <el-button type="primary" size="small" class="edit-btn" @click="handleEditProfile"
            >编辑资料</el-button
          >
        </div>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="profile-content">
      <!-- 博客链接 -->
      <el-card class="blog-card">
        <div class="blog-info">
          <el-icon class="blog-icon"><Document /></el-icon>
          <div class="blog-details">
            <h3 class="blog-title">{{ userProfile.blog.title }}</h3>
            <p class="blog-subtitle">{{ userProfile.blog.url }}</p>
          </div>
          <el-button type="text" class="read-btn">Read the blog</el-button>
        </div>
      </el-card>

      <!-- 三个信息卡片 -->
      <div class="info-cards">
        <!-- 关于我 -->
        <el-card class="info-card">
          <div class="card-header">
            <h2 class="card-title">About Me</h2>
            <el-button type="text" size="small" class="add-btn">+ Add info</el-button>
          </div>
          <div class="card-content">
            <p>{{ userProfile.about }}</p>
          </div>
        </el-card>

        <!-- 技能栈 -->
        <el-card class="info-card">
          <div class="card-header">
            <h2 class="card-title">My Tech Stack</h2>
            <el-button type="text" size="small" class="add-btn">+ Add skills</el-button>
          </div>
          <div class="card-content">
            <el-tag v-for="(skill, index) in userProfile.techStack" :key="index" class="mx-1">
              {{ skill }}
            </el-tag>
          </div>
        </el-card>

        <!-- 可用服务 -->
        <el-card class="info-card">
          <div class="card-header">
            <h2 class="card-title">I am available for</h2>
            <el-button type="text" size="small" class="add-btn">+ Add Available For</el-button>
          </div>
          <div class="card-content">
            <p>{{ userProfile.availableFor }}</p>
          </div>
        </el-card>
      </div>

      <!-- 徽章区域 -->
      <div class="badges-section">
        <h2 class="section-title">Badges</h2>
        <el-card class="badges-card">
          <div class="badge-item">
            <div class="badge-icon">
              <el-icon><GoldMedal /></el-icon>
            </div>
            <div class="badge-info">
              <h3 class="badge-name">Self Starter</h3>
              <p class="badge-date">Earned on Jul 25, 2024</p>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 最近活动 -->
      <div class="activity-section">
        <h2 class="section-title">Recent Activity</h2>
        <el-card class="activity-card">
          <div class="activity-item">
            <div class="activity-date">Jul 26, 2024</div>
            <div class="activity-content">
              <p>Wrote an article</p>
              <h3 class="activity-title">"Theming"</h3>
            </div>
          </div>
          <el-divider />
          <div class="activity-item">
            <div class="activity-date"></div>
            <el-button type="text" class="show-more-btn">Show more</el-button>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElCard, ElButton, ElAvatar, ElIcon, ElDivider, ElMessage } from 'element-plus'
import { Document, GoldMedal } from '@element-plus/icons-vue'
import { getUserMe } from '@/api/services/user'
import { generateLetterAvatar } from '@/utils/avatarUtils'
import { formatDateTime } from '@/utils/dateUtils'

// 定义用户资料类型
interface UserProfile {
  name: string
  tagline: string
  joinDate: string
  avatarUrl: string
  blog: {
    title: string
    url: string
  }
  about: string
  techStack: string[]
  availableFor: string
  badges: Array<{
    name: string
    icon: string
    date: string
  }>
  activities: Array<{
    date: string
    type: string
    title: string
  }>
}

// 初始化路由
const router = useRouter()

// 用户资料数据
const userProfile = ref<UserProfile>({
  name: '',
  tagline: '',
  joinDate: '',
  avatarUrl: '',
  blog: {
    title: '',
    url: ''
  },
  about: '',
  techStack: [],
  availableFor: '',
  badges: [],
  activities: []
})

// 加载用户数据
const loadUserData = async () => {
  try {
    const res = await getUserMe()

    // 填充用户数据
    userProfile.value = {
      name: res.data.username || '',
      tagline: res.data.profile_tagline || '',
      joinDate: res.data.createtime ? formatDateTime(res.data.createtime, 'YYYY年MM月DD日') : '',
      avatarUrl: res.data.profile_image || '/src/assets/avatar.png',
      blog: {
        title: 'Freebox',
        url: 'freenbox.hashnode.dev'
      },
      about:
        res.data.profile_bio ||
        "You can add info for others to know more about you. You're a freelancer and you want to tell others about your expertise.",
      techStack: Array.isArray(res.data.tech_stack) ? res.data.tech_stack : [],
      availableFor:
        typeof res.data.available_for === 'string'
          ? res.data.available_for
          : 'Let others know what services you offer. You can add freelance work, consulting, etc.',
      badges: [
        {
          name: 'Self Starter',
          icon: 'Shield',
          date: 'Jul 25, 2024'
        }
      ],
      activities: [
        {
          date: 'Jul 26, 2024',
          type: 'Wrote an article',
          title: '"Theming"'
        }
      ]
    }
  } catch (error) {
    console.error('加载用户数据失败:', error)
    ElMessage.error('加载用户数据失败，请稍后重试')
  }
}

// 编辑资料按钮点击事件
const handleEditProfile = () => {
  router.push({ name: 'ProfileEdit' })
}

// 组件挂载时加载数据
onMounted(() => {
  loadUserData()
})
</script>

<style scoped lang="scss">
.profile-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.profile-header {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;

  .avatar {
    margin-right: 20px;
    border: 4px solid #fff;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
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
      gap: 15px;

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

.blog-section {
  .blog-card {
    .blog-info {
      display: flex;
      align-items: center;
      gap: 15px;

      .blog-icon {
        color: #409eff;
        font-size: 24px;
      }

      .blog-details {
        flex: 1;

        .blog-title {
          margin: 0 0 5px 0;
          font-size: 18px;
          font-weight: 500;
        }

        .blog-subtitle {
          margin: 0;
          color: #666;
          font-size: 14px;
        }
      }

      .read-btn {
        color: #409eff;
      }
    }
  }
}

.info-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;

  .info-card {
    height: 100%;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 15px;

      .card-title {
        margin: 0;
        font-size: 18px;
        font-weight: 500;
      }

      .add-btn {
        color: #409eff;
        padding: 0;
      }
    }

    .card-content {
      p {
        margin: 0;
        color: #666;
        line-height: 1.6;
      }
    }
  }
}

.badges-section,
.activity-section {
  .section-title {
    margin: 0 0 15px 0;
    font-size: 20px;
    font-weight: 500;
  }

  .badges-card,
  .activity-card {
    padding: 20px;
  }
}

.badge-item {
  display: flex;
  align-items: center;
  gap: 15px;

  .badge-icon {
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #f0f9eb;
    color: #52c41a;
    border-radius: 50%;
  }

  .badge-info {
    .badge-name {
      margin: 0 0 5px 0;
      font-size: 16px;
      font-weight: 500;
    }

    .badge-date {
      margin: 0;
      color: #888;
      font-size: 14px;
    }
  }
}

.activity-item {
  .activity-date {
    color: #888;
    font-size: 14px;
    margin-bottom: 5px;
  }

  .activity-content {
    p {
      margin: 0 0 5px 0;
      color: #666;
      font-size: 14px;
    }

    .activity-title {
      margin: 0;
      font-size: 16px;
      font-weight: 500;
    }
  }

  .show-more-btn {
    color: #409eff;
    padding: 0;
  }
}

@media (max-width: 768px) {
  .info-cards {
    grid-template-columns: 1fr;
  }

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
</style>
