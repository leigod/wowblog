<template>
  <footer class="site-footer">
    <!-- 上部区域 75% -->
    <div class="footer-main">
      <div class="footer-container">
        <!-- 左侧小区域 25%: Logo、描述、社交媒体 -->
        <div v-if="hasLeftContent" class="footer-left">
          <!-- Logo -->
          <div v-if="footerConfig && footerConfig.logo_url" class="footer-logo">
            <img :src="footerConfig.logo_url" alt="Site Logo" />
          </div>

          <!-- 网站描述 -->
          <p v-if="footerConfig && footerConfig.site_description" class="footer-description">
            {{ footerConfig.site_description }}
          </p>

          <!-- 社交媒体图标 -->
          <div v-if="footerConfig && footerConfig.social_media && footerConfig.social_media.length > 0"
            class="footer-social">
            <a v-for="(media, index) in footerConfig.social_media" :key="index" :href="media.url" target="_blank"
              rel="noopener noreferrer" class="social-link">
              <IconifyIcon :icon="media.icon" />
            </a>
          </div>
        </div>

        <!-- 右侧大区域 75%: 功能链接分组 -->
        <div v-if="hasRightContent" class="footer-right">
          <div v-for="(group, groupIndex) in (footerConfig ? footerConfig.nav_groups : [])" :key="groupIndex"
            class="footer-nav-group">
            <h4 v-if="group.group_name" class="nav-group-title">{{ group.group_name }}</h4>
            <ul v-if="group.links && group.links.length > 0" class="nav-group-links">
              <li v-for="(link, linkIndex) in group.links" :key="linkIndex">
                <a :href="link.url" target="_blank" rel="noopener noreferrer">
                  {{ link.name }}
                </a>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- 下部区域 25%: 版权和 ICP 信息 -->
    <div class="footer-bottom">
      <div class="footer-container">
        <!-- 版权信息 -->
        <p class="footer-copyright">
          {{ copyrightText }}
        </p>

        <!-- ICP 信息 -->
        <div v-if="hasIcpInfo" class="footer-icp">
          <a v-for="(icp, index) in footerConfig?.icp_info" :key="index" :href="icp.url" target="_blank"
            rel="noopener noreferrer">
            {{ icp.text }}
          </a>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import IconifyIcon from '@/components/IconIfy.vue'
import { getSystemConfig } from '@/api/services/common'

// 社交媒体类型
interface SocialMedia {
  icon: string
  url: string
}

// 导航链接
interface NavLink {
  name: string
  url: string
}

// 导航分组
interface NavGroup {
  group_name: string
  links: NavLink[]
}

// ICP 信息
interface IcpInfo {
  text: string
  url: string
}

// Footer 配置
interface FooterConfig {
  logo_url: string
  site_description: string
  social_media: SocialMedia[]
  nav_groups: NavGroup[]
  copyright: string
  icp_info: IcpInfo[]
}

const footerConfig = ref<FooterConfig | null>(null)

// 动态版权年份
const currentYear = new Date().getFullYear()
const baseYear = 2026
const copyrightYear = computed(() => {
  if (currentYear === baseYear) {
    return `© ${baseYear}`
  } else if (currentYear > baseYear) {
    return `© ${baseYear} - ${currentYear}`
  } else {
    return `© ${baseYear}`
  }
})

// 计算是否有左侧内容
const hasLeftContent = computed(() => {
  return footerConfig.value &&
    (footerConfig.value.logo_url ||
      footerConfig.value.site_description ||
      (footerConfig.value.social_media && footerConfig.value.social_media.length > 0))
})

// 计算是否有右侧内容
const hasRightContent = computed(() => {
  return footerConfig.value &&
    footerConfig.value.nav_groups &&
    footerConfig.value.nav_groups.length > 0
})

// 计算是否有 ICP 信息
const hasIcpInfo = computed(() => {
  return footerConfig.value &&
    footerConfig.value.icp_info &&
    footerConfig.value.icp_info.length > 0
})

// 版权信息文本
const copyrightText = computed(() => {
  if (footerConfig.value && footerConfig.value.copyright) {
    return `${copyrightYear.value} ${footerConfig.value.copyright}`
  }
  return `${copyrightYear.value} CMS Site. All rights reserved.`
})

// 获取 Footer 配置
const fetchFooterConfig = async () => {
  try {
    const response = await getSystemConfig()
    if (response.code === 1 && response.data && response.data.footer_config) {
      footerConfig.value = response.data.footer_config
    }
  } catch (error) {
    // 静默失败，显示默认 footer
    console.debug('获取 Footer 配置失败，使用默认配置:', error)
  }
}

onMounted(() => {
  fetchFooterConfig()
})
</script>

<style scoped>
.site-footer {
  width: 100%;
  background-color: #000;
  border-top: 1px solid #333;
  margin-top: auto;
  color: #fff;
}

.footer-main {
  padding: 40px 0;
}

.footer-bottom {
  padding: 20px 0;
  border-top: 1px solid #333;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

/* 左侧区域 */
.footer-left {
  flex: 0 0 25%;
  max-width: 300px;
}

.footer-logo {
  margin-bottom: 16px;
}

.footer-logo img {
  /* max-width: 120px; */
  max-height: 60px;
  object-fit: contain;
}

.footer-description {
  font-size: 14px;
  color: #999;
  line-height: 1.6;
  margin-bottom: 20px;
}

.footer-social {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.social-link {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  padding-top: 5px;
  background-color: #ffffff26;
  color: #fff;
  cursor: pointer;
  transition: background-color 0.2s;
}

.social-link:hover {
  background-color: #ffffff50;
  /* transform: translateY(-2px); */
}

/* 右侧区域 */
.footer-right {
  flex: 1;
  display: flex;
  gap: 40px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.footer-nav-group {
  min-width: 120px;
}

.nav-group-title {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  margin: 0 0 12px 0;
}

.nav-group-links {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-group-links li {
  margin-bottom: 8px;
}

.nav-group-links a {
  font-size: 14px;
  color: #999;
  text-decoration: none;
  transition: color 0.3s;
}

.nav-group-links a:hover {
  color: #ffffff;
}

/* 底部区域 */
.footer-bottom .footer-container {
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.footer-copyright {
  font-size: 13px;
  color: #666;
  margin: 0;
}

.footer-icp {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.footer-icp a {
  font-size: 12px;
  color: #666;
  text-decoration: none;
  transition: color 0.3s;
}

.footer-icp a:hover {
  color: #999999;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .footer-container {
    flex-direction: column;
    gap: 30px;
  }

  .footer-left {
    flex: 1;
    max-width: 100%;
  }

  .footer-right {
    justify-content: flex-start;
    width: 100%;
  }

  .footer-nav-group {
    min-width: 50%;
  }

  .footer-bottom .footer-container {
    flex-direction: column;
    align-items: center;
  }
}
</style>
