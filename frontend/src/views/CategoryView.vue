<template>
  <div class="wy-container">
    <el-container>
      <el-main>
        <el-row :gutter="30" justify="space-between">
          <el-col :xs="24" :sm="12" :md="12">
            <el-tag type="primary">{{ $t('category.info.tag') }}</el-tag>
            <h1>{{ categoryDetail.name }}</h1>
            <div class="wy-category-desc">{{ categoryDetail.cat_desc }}</div>
          </el-col>
          <el-col :xs="24" :sm="12" :md="12" class="wy-page-cover-wrapper">
            <img
              v-if="categoryDetail.image"
              :src="categoryDetail.image"
              alt="分类封面"
              class="wy-page-cover"
            />
          </el-col>
        </el-row>
        <el-row
          ><el-divider>{{ $t('category.info.title') }}</el-divider>
        </el-row>
        <el-row>
          <el-col :xs="24" class="wy-card-list">
            <el-card
              v-for="item in categoryArticlesList"
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
                      {{ item.content.slice(0, 150).replace(/<\/?[^>]+(>|$)/g, '') }}
                    </div>
                  </div>
                  <div class="right" v-if="item.cover">
                    <el-image :src="item.cover" fit="cover" class="wy-card-radius wy-card-image" />
                  </div>
                </div>
                <div class="info">
                  <div class="left">
                    <span>
                      <el-icon><ChatLineRound /></el-icon>
                      {{ $t('home.list.discuss') }}
                    </span>
                    · <span>{{ item.likes }} {{ $t('home.list.likes') }}</span> ·
                    <span>{{ item.views }} {{ $t('home.list.reads') }}</span> ·
                    <span>{{
                      $t('list.view.readtime', { minutes: getReadTime(item.content) })
                    }}</span>
                  </div>
                  <div class="right"></div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
        <!-- 加载更多按钮 -->
        <div
          class="load-more-container"
          v-if="hasMore && categoryArticlesList.length > 0"
          style="margin-top: 20px; text-align: center"
        >
          <el-button type="primary" @click="loadMore" :loading="loading" v-loading="loading">
            加载更多
          </el-button>
        </div>
        <!-- 没有更多数据提示 -->
        <div
          v-if="!hasMore && categoryArticlesList.length > 0"
          class="no-more-tip"
          style="margin-top: 20px; text-align: center; color: #909399; padding: 20px"
        >
          我也是有底线的
        </div>
        <el-empty v-if="categoryArticlesList.length === 0 && !loading" description="暂无文章" />
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { getCategoryDetailApi, getCategoryArticlesList } from '@/api/services/blog'
import { ElMessage } from 'element-plus'
import { formatDateTime } from '@/utils/dateUtils'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const categoryDetail = ref<any>({})
const categoryArticlesList = ref<any>([])
const default_avatar = 'src/assets/avatar.png'

// 分页相关状态
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const loading = ref(false)
const hasMore = ref(true) // 是否有更多数据

// 获取文章列表的方法
const fetchArticles = async (page: number, size: number, append: boolean = false) => {
  const categorySlug = route.params.categorySlug as string
  loading.value = true

  try {
    // 调用API获取分类下的文章列表，传递分页参数
    const articlesRes = await getCategoryArticlesList(categorySlug, page, size)

    if (articlesRes.code === 1) {
      const newArticles = articlesRes.data.list || []

      // 根据append参数决定是追加数据还是替换数据
      if (append) {
        categoryArticlesList.value = [...categoryArticlesList.value, ...newArticles]
      } else {
        categoryArticlesList.value = newArticles
      }

      // 更新总数
      total.value = articlesRes.data.total || 0

      // 判断是否还有更多数据
      if (categoryArticlesList.value.length >= total.value || newArticles.length < size) {
        hasMore.value = false
      } else {
        hasMore.value = true
      }
    } else {
      ElMessage.error('获取系列文章列表失败')
    }
  } catch (error) {
    console.error('加载文章列表出错:', error)
    ElMessage.error('加载文章列表出错')
  } finally {
    loading.value = false
  }
}

// 加载更多数据
const loadMore = async () => {
  currentPage.value++
  await fetchArticles(currentPage.value, pageSize.value, true)
}

onMounted(async () => {
  try {
    // 从路由参数中获取分类slug
    const categorySlug = route.params.categorySlug as string

    // 调用API获取分类详情
    const res = await getCategoryDetailApi(categorySlug)

    if (res.code === 1) {
      // 更新分类数据
      categoryDetail.value = res.data

      // 动态设置浏览器标题和meta标签
      if (categoryDetail.value?.name) {
        const title = categoryDetail.value.name
        const description = categoryDetail.value.cat_desc
        const imageUrl = categoryDetail.value.image || ''

        // 设置页面标题
        document.title = title + ' - ' + appStore.site_title || '默认标题'

        // 设置meta description
        const metaDesc = document.querySelector('meta[name="description"]')
        if (metaDesc) {
          metaDesc.setAttribute('content', description)
        } else {
          // 如果不存在，创建新的meta标签
          const newMetaDesc = document.createElement('meta')
          newMetaDesc.name = 'description'
          newMetaDesc.content = description
          document.head.appendChild(newMetaDesc)
        }

        // 设置Open Graph标签
        document.querySelector('meta[property="og:title"]')?.setAttribute('content', title)
        document
          .querySelector('meta[property="og:description"]')
          ?.setAttribute('content', description)
        if (imageUrl) {
          document.querySelector('meta[property="og:image"]')?.setAttribute('content', imageUrl)
        }

        // 设置Twitter卡片标签
        document.querySelector('meta[name="twitter:title"]')?.setAttribute('content', title)
        document
          .querySelector('meta[name="twitter:description"]')
          ?.setAttribute('content', description)
        if (imageUrl) {
          document.querySelector('meta[name="twitter:image"]')?.setAttribute('content', imageUrl)
        }
      }
    } else {
      // 错误处理
      ElMessage.error('获取系列信息失败')
      router.push({ name: '404' })
    }

    // 初始化时获取第一页文章列表
    await initArticles()
  } catch (error) {
    console.error('加载系列内容出错:', error)
    ElMessage.error('加载系列内容出错')
    router.push({ name: '404' })
  }
})

// 监测路由参数变化，重新加载数据
watch(
  () => route.params.categorySlug,
  async (newSlug, oldSlug) => {
    if (newSlug !== oldSlug) {
      // 当分类slug变化时，重新加载分类详情和文章列表
      await initArticles()
      try {
        const categorySlug = route.params.categorySlug as string
        const res = await getCategoryDetailApi(categorySlug)
        if (res.code === 1) {
          categoryDetail.value = res.data
          if (categoryDetail.value?.name) {
            const title = categoryDetail.value.name
            const description = categoryDetail.value.cat_desc
            const imageUrl = categoryDetail.value.image || ''

            document.title = title + ' - ' + appStore.site_title || '默认标题'

            const metaDesc = document.querySelector('meta[name="description"]')
            if (metaDesc) {
              metaDesc.setAttribute('content', description)
            } else {
              const newMetaDesc = document.createElement('meta')
              newMetaDesc.name = 'description'
              newMetaDesc.content = description
              document.head.appendChild(newMetaDesc)
            }

            document.querySelector('meta[property="og:title"]')?.setAttribute('content', title)
            document
              .querySelector('meta[property="og:description"]')
              ?.setAttribute('content', description)
            if (imageUrl) {
              document.querySelector('meta[property="og:image"]')?.setAttribute('content', imageUrl)
            }

            document.querySelector('meta[name="twitter:title"]')?.setAttribute('content', title)
            document
              .querySelector('meta[name="twitter:description"]')
              ?.setAttribute('content', description)
            if (imageUrl) {
              document
                .querySelector('meta[name="twitter:image"]')
                ?.setAttribute('content', imageUrl)
            }
          }
        } else {
          ElMessage.error('获取系列信息失败')
          router.push({ name: '404' })
        }
      } catch (error) {
        console.error('加载系列内容出错:', error)
        ElMessage.error('加载系列内容出错')
        router.push({ name: '404' })
      }
    }
  }
)

// 初始化时获取第一页文章列表
const initArticles = async () => {
  currentPage.value = 1
  await fetchArticles(currentPage.value, pageSize.value, false)
}

// 处理用户点击跳转个人中心
const handleProfile = (username: string) => {
  router.push(`/profile/${username}`)
}

const handleDetail = (item: any) => {
  const articleName = item.slug
  router.push(`/article/${articleName}`)
}

// 计算文章阅读时间
const getReadTime = (content: string) => {
  const contentText = content.replace(/<\/?[^>]+(>|$)/g, '')
  const readWords = 400 //成年人专注阅读每分钟阅读150-200字，专注阅读800字
  return `${Math.ceil(contentText.length / readWords)}`
}

// 定义组件名称
defineOptions({ name: 'CategoryView' })
</script>

<style scoped>
.wy-container {
  display: flex;
  width: 1200px;
}
.wy-page-cover-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
}

.wy-card-list {
  margin-bottom: 20px;
}
.wy-page-cover {
  width: 300px;
  height: 300px;
  object-fit: cover;
}
@media only screen and (max-width: 767px) {
  .wy-container {
    display: flex;
    width: 100%;
  }
  .wy-page-cover {
    margin-top: 2rem;
    width: 200px;
    height: 200px;
    object-fit: cover;
  }
  .el-main {
    --el-main-padding: 10px !important;
  }
}
</style>
