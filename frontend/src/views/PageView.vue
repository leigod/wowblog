<template>
  <div class="wy-container">
    <el-container>
      <el-main>
        <el-row>
          <el-col :xs="24">
            <img v-if="pageCover" :src="pageCover" alt="页面封面" class="wy-page-cover" />
          </el-col>
        </el-row>
        <el-row>
          <h1>{{ pageDetail.title }}</h1>
        </el-row>
        <el-row>
          <el-col :xs="24">
            <div class="wy-article-content tiptap">
              <div v-html="pageContent"></div>
            </div>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { getPageDetailApi } from '@/api/services/blog'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const pageCover = ref('')
const pageContent = ref('')
const pageDetail = ref<any>({ title: '' })

onMounted(async () => {
  try {
    // 从路由参数中获取页面slug
    const pageSlug = route.params.pageSlug as string

    // 调用API获取页面详情
    const res = await getPageDetailApi(pageSlug)

    if (res.code === 1) {
      // 更新页面数据
      pageCover.value = res.data.image
      pageContent.value = res.data.content
      pageDetail.value = res.data

      // 过滤content中的所有html标签
      const content = pageContent.value.replace(/<\/?[^>]+(>|$)/g, '')

      // 动态设置浏览器标题和meta标签
      if (pageDetail.value?.title) {
        const title = pageDetail.value.title
        const description = pageDetail.value.seo_desc || content.slice(0, 150)
        const imageUrl = pageDetail.value.image || ''

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
      ElMessage.error('获取页面信息失败')
      router.push({ name: '404' })
    }
  } catch (error) {
    console.error('加载页面内容出错:', error)
    ElMessage.error('加载页面内容出错')
    router.push({ name: '404' })
  }
})

// 定义组件名称
defineOptions({ name: 'PageView' })
</script>

<style scoped>
.wy-container {
  display: flex;
  width: 1200px;
}
.wy-page-cover {
  width: 100%;
  height: 400px;
  object-fit: cover;
}
@media only screen and (max-width: 767px) {
  .wy-container {
    display: flex;
    width: 100%;
  }
  .wy-page-cover {
    width: 100%;
    height: 200px;
    object-fit: cover;
  }
  .el-main {
    --el-main-padding: 10px !important;
  }
}
</style>
