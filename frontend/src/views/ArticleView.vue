<template>
  <!-- 目录区域 -->
  <div v-if="showArticleTOC" class="table-of-contents" v-html="tableOfContents"></div>
  <div class="wy-container-page">
    <div class="wy-article-container">
      <el-container direction="vertical" class="wy-article-content-container">
        <el-row justify="center">
          <div class="wy-article-cover" v-if="articleDetail?.cover">
            <img :src="articleDetail?.cover" alt="Article Cover" />
          </div>
        </el-row>
        <el-row justify="center" class="wy-title-area">
          <div class="wy-article-title">{{ articleDetail?.title }}</div>
          <div class="wy-article-subtitle" v-if="articleDetail?.subtitle">
            {{ articleDetail?.subtitle }}
          </div>
        </el-row>

        <el-row justify="center" align="middle">
          <div class="wy-article-info" @click="handleAuthorClick" style="cursor: pointer">
            <el-avatar :src="circleUrl" />
          </div>
          <div class="wy-article-info wy-article-author" @click="handleAuthorClick" style="cursor: pointer">{{
            articleAuthor }}</div>
          <div class="wy-article-info">·</div>
          <div class="wy-article-info">
            {{ formatDateTime(articleDetail?.createtime, 'YYYY-MM-DD HH:mm') }}
          </div>
          <div class="wy-article-info">·</div>
          <div class="wy-article-info">{{ t('article.detail.read_time', { minutes: readTime }) }}</div>
        </el-row>
        <!-- 所属系列 -->
        <el-row v-if="articleSeries" justify="center" align="middle" class="wy-article-series-row">
          <div class="wy-article-info">{{ t('article.detail.series') }}</div>
          <div class="wy-article-info wy-article-series-link" @click="handleSeriesClick"
            style="cursor: pointer; color: var(--el-color-primary)">
            {{ articleSeries.name }}
          </div>
        </el-row>
        <!-- 文章内容 -->
        <el-row class="wy-article-content-row">
          <div class="wy-article-content tiptap">
            <div v-html="highlightedContent"></div>
          </div>
        </el-row>

        <el-row>
          <div class="wy-article-tags">
            <el-tag v-for="item in tagTtems" :key="item.id" type="primary" effect="light" round
              @click="handleTagClick(item.slug)">
              {{ item.name }}
            </el-tag>
          </div>
        </el-row>
        <!-- 操作按钮区域A（在文章末尾，跟随文档流） -->
        <el-row justify="center" ref="actionsAnchorRef">
          <div class="wy-article-functions">
            <div class="wy-btn-container" data-like-btn-area-a>
              <div class="wy-overlay">
                <el-tooltip :show-after="1000" class="box-item" effect="dark" content="Like this article"
                  placement="top">
                  <el-button size="large" circle style="border: 0" @click="handleLike">
                    <template #icon><el-icon :size="30">
                        <IconLoveHeart :fill="fillColor" :stroke="fillStroke" />
                      </el-icon>
                    </template>
                  </el-button>
                </el-tooltip>
              </div>
            </div>
            <span style="margin-left: 10px" v-if="articleStat?.likes > 0">{{
              articleStat?.likes
            }}</span>
            <el-divider direction="vertical" />

            <el-tooltip :show-after="1000" class="box-item" effect="dark" content="Write a comment" placement="top">
              <el-button size="large" circle style="border: 0" @click="handleShowCommentDrawer">
                <template #icon>
                  <el-icon :size="30">
                    <ChatLineRound />
                  </el-icon>
                </template>
              </el-button>
            </el-tooltip>
            <span style="margin-left: 5px" v-if="articleStat?.comments > 0">{{
              articleStat?.comments
            }}</span>
            <el-divider direction="vertical" />
            <el-tooltip :show-after="1000" class="box-item" effect="dark" content="Add Bookmark" placement="top">
              <el-button size="large" circle style="border: 0" @click="handleBookmark">
                <template #icon>
                  <IconifyIcon :icon="isBookmarked
                    ? 'material-symbols-light:bookmark-star'
                    : 'material-symbols-light:bookmark-star-outline'
                    " size="35" :color="isBookmarked ? '#ffcc00' : '#3f3f46'" stroke-width="0.2"
                    :stroke="isBookmarked ? 'none' : 'currentColor'" />
                </template>
              </el-button>
            </el-tooltip>
            <span style="margin-left: 5px" v-if="articleStat?.bookmarks > 0">{{
              articleStat?.bookmarks
            }}</span>
            <el-divider direction="vertical" />
            <el-tooltip :show-after="1000" class="box-item" effect="dark" content="Share this article" placement="top">
              <span>
                <el-popover placement="top" width="200" trigger="click">
                  <template #reference>
                    <el-button size="large" circle style="border: 0; position: relative">
                      <template #icon>
                        <el-icon :size="30">
                          <Share />
                        </el-icon>
                      </template>
                    </el-button>
                    <span style="margin-left: 5px" v-if="articleStat?.shares > 0">{{
                      articleStat?.shares
                    }}</span>
                  </template>
                  <template #default>
                    <div class="custom-social-share">
                      <div v-for="network in networks" :key="network.network" :style="{
                        width: '100%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'flex-start',
                        padding: '5px 0',
                        cursor: 'pointer'
                      }" @click="handleSocialShare(network)">
                        <i :class="network.icon"></i>
                        <span style="margin-left: 5px">{{ network.name }}</span>
                      </div>
                    </div>
                  </template>
                </el-popover>
              </span>
            </el-tooltip>
          </div>
        </el-row>
      </el-container>
    </div>

    <!-- 固定操作按钮区域B（始终在视口底部，当按钮A可见时隐藏） -->
    <div v-show="isShowFixedActions" class="wy-fixed-actions-container">
      <div class="wy-article-functions">
        <div class="wy-btn-container" data-like-btn-area-b>
          <div class="wy-overlay">
            <el-tooltip :show-after="1000" class="box-item" effect="dark" content="Like this article" placement="top">
              <el-button size="large" circle style="border: 0" @click="handleLike">
                <template #icon><el-icon :size="30">
                    <IconLoveHeart :fill="fillColor" :stroke="fillStroke" />
                  </el-icon>
                </template>
              </el-button>
            </el-tooltip>
          </div>
        </div>
        <span style="margin-left: 10px" v-if="articleStat?.likes > 0">{{
          articleStat?.likes
          }}</span>
        <el-divider direction="vertical" />

        <el-tooltip :show-after="1000" class="box-item" effect="dark" content="Write a comment" placement="top">
          <el-button size="large" circle style="border: 0" @click="handleShowCommentDrawer">
            <template #icon>
              <el-icon :size="30">
                <ChatLineRound />
              </el-icon>
            </template>
          </el-button>
        </el-tooltip>
        <span style="margin-left: 5px" v-if="articleStat?.comments > 0">{{
          articleStat?.comments
          }}</span>
        <el-divider direction="vertical" />
        <el-tooltip :show-after="1000" class="box-item" effect="dark" content="Add Bookmark" placement="top">
          <el-button size="large" circle style="border: 0" @click="handleBookmark">
            <template #icon>
              <IconifyIcon :icon="isBookmarked
                ? 'material-symbols-light:bookmark-star'
                : 'material-symbols-light:bookmark-star-outline'
                " size="35" :color="isBookmarked ? '#ffcc00' : '#3f3f46'" stroke-width="0.2"
                :stroke="isBookmarked ? 'none' : 'currentColor'" />
            </template>
          </el-button>
        </el-tooltip>
        <span style="margin-left: 5px" v-if="articleStat?.bookmarks > 0">{{
          articleStat?.bookmarks
          }}</span>
        <el-divider direction="vertical" />
        <el-tooltip :show-after="1000" class="box-item" effect="dark" content="Share this article" placement="top">
          <span>
            <el-popover placement="top" width="200" trigger="click">
              <template #reference>
                <el-button size="large" circle style="border: 0; position: relative">
                  <template #icon>
                    <el-icon :size="30">
                      <Share />
                    </el-icon>
                  </template>
                </el-button>
                <span style="margin-left: 5px" v-if="articleStat?.shares > 0">{{
                  articleStat?.shares
                  }}</span>
              </template>
              <template #default>
                <div class="custom-social-share">
                  <div v-for="network in networks" :key="network.network" :style="{
                    width: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'flex-start',
                    padding: '5px 0',
                    cursor: 'pointer'
                  }" @click="handleSocialShare(network)">
                    <i :class="network.icon"></i>
                    <span style="margin-left: 5px">{{ network.name }}</span>
                  </div>
                </div>
              </template>
            </el-popover>
          </span>
        </el-tooltip>
      </div>
    </div>

    <!-- 更多文章 -->
    <div class="wy-article-more">
      <div class="wy-article-more-title">
        <span>MORE ARTICLES</span>
        <el-button link @click="refreshRecommend" :loading="recommendLoading">
          <el-icon>
            <Refresh />
          </el-icon>
          {{ t('tag.read_more').replace('...', '') }}
        </el-button>
      </div>
      <el-container v-if="recommendArticles.length > 0">
        <el-row :gutter="30">
          <el-col v-for="item in recommendArticles" :key="item.id" :xs="24" :md="12" :lg="8">
            <el-card shadow="hover" class="wy-article-card-wrap">
              <div class="wy-article-card" @click="navigateToArticle(item.slug)">
                <div class="head">
                  <el-avatar :size="30" :src="item.author_avatar || generateLetterAvatar(item.author_name)" />
                  <div class="author">{{ item.author_name }}</div>
                </div>
                <div class="head-picture">
                  <!-- 推荐理由标签 - 放在图片右上角 -->
                  <div class="recommend-reason" @click.stop="navigateToArticle(item.slug)">{{ item.reason }}</div>
                  <el-image v-if="item.cover" style="width: 100%; height: 230px" :src="item.cover" fit="cover"
                    class="wy-card-radius image-clickable" />
                  <div v-else class="placeholder-wrap">
                    <PlaceholderImage height="230px" :text="t('article.detail.no_cover')" />
                  </div>
                </div>
                <div class="title">{{ item.title }}</div>
                <div class="summary">{{ item.summary }}</div>
                <div class="meta">
                  <span>{{ formatDateTime(item.pub_time, 'YYYY-MM-DD') }}</span>
                  <span>{{ item.views }} {{ t('home.list.reads').replace('阅读', '') }}</span>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-container>
      <el-empty v-else :description="t('article.detail.no_recommend')" />
    </div>

    <!-- 评论抽屉 -->
    <el-drawer v-model="drawer" direction="rtl" :size="drawerSize">
      <template #header>
        <h3>{{ t('notification.tab_comment') }}</h3>
      </template>
      <template #default>
        <el-container direction="vertical">
          <el-container direction="vertical" v-if="showCommentForm">
            <el-row>
              <div class="wy-comment-author">
                <el-avatar :size="30" :src="appStore.userInfo?.profile_image || '/src/assets/avatar.png'" />
                <div class="author">{{ appStore.userInfo?.username || 'Anonymous' }}</div>
              </div>
            </el-row>
            <el-row>
              <el-input v-model="commentsInput" :rows="5" type="textarea"
                :placeholder="t('article.detail.write_comment')" />
            </el-row>
            <el-row justify="end">
              <el-button type="primary" round style="margin-top: 1rem" @click="handleSubmitComment">{{
                t('article.detail.submit') }}</el-button>
            </el-row>
            <el-divider />
          </el-container>
          <div v-if="commentFormTip.trim() && needLogin" class="wy-comment-form-tip">
            {{ commentFormTip }}
            <el-button type="primary" size="small" @click="handleLogin">{{ t('navbar.item.login') }}</el-button>
          </div>
          <div v-else-if="commentFormTip.trim()" class="wy-comment-form-tip">
            {{ commentFormTip }}
          </div>
          <el-row justify="center">
            <el-empty v-if="commentsList.length === 0">
              <template #description>
                {{ t('article.detail.no_comments') }}<br />
                Be the first one to comment!
              </template>
            </el-empty>
            <div class="wy-comment-list-head" v-else>
              <div class="title">{{ t('article.detail.all_comments', { count: articleStat.comments }) }}</div>
              <div>
                <el-select v-model="commentList_order" :placeholder="t('common.select')" style="width: 150px">
                  <el-option :label="t('home.list.hot')" value="top" />
                  <el-option :label="t('home.list.new')" value="new" />
                </el-select>
              </div>
            </div>
            <div class="wy-comments-list">
              <div class="wy-comment-item" v-for="item in commentsList" :key="item.id">
                <div class="wy-comment-avatar">
                  <el-avatar :size="50">
                    <img :src="item.profile_image || generateLetterAvatar(item.full_name)" alt="用户头像" />
                  </el-avatar>
                </div>
                <div class="wy-comment-body">
                  <div class="authorWrap">
                    <div class="author">{{ item.full_name }}@{{ item.username }}</div>
                    <el-tag type="primary" effect="light" v-if="item.user_id === articleDetail.author">作者</el-tag>
                  </div>
                  <div class="content">
                    {{ item.comment }}
                  </div>
                  <div class="info">
                    {{ formatDateTime(item.createtime, 'MM-DD') }} · {{ item.location }}
                  </div>
                  <div class="operations">
                    <div class="wy-block">
                      <el-button circle style="border: 0">
                        <template #icon>
                          <el-icon :size="20">
                            <IconLoveHeart fill="none" stroke="currentColor" />
                          </el-icon>
                        </template>
                      </el-button>
                      {{ item.likes }}
                    </div>
                    <div class="wy-block">
                      <el-button circle style="border: 0">
                        <template #icon>
                          <el-icon :size="20">
                            <IconUnlike />
                          </el-icon>
                        </template>
                      </el-button>
                      {{ item.unlikes }}
                    </div>
                    <div class="wy-block">
                      <el-button type="info" :text="textBtn" round plain @click="handleShowInnerDrawer(item.id)">{{
                        t('article.detail.reply') }}</el-button>
                    </div>
                  </div>
                  <div class="wy-comment-footer" v-if="item.replys > 0" :data-subject="item.id">
                    <div class="wy-reply-toggle" @click="toggleReplies(item.id)">
                      <el-button type="primary" link size="small">
                        {{ expandedRepliesIds.includes(item.id) ? t('tag.collapse') : t('tag.read_more').replace('...',
                        '') }}
                        {{ t('article.detail.replies', { count: item.replys }) }}
                      </el-button>
                    </div>
                    <div class="wy-replies-list" v-if="expandedRepliesIds.includes(item.id)">
                      <div class="wy-reply-item" v-for="reply in repliesList" :key="reply.id">
                        <div class="wy-comment-avatar">
                          <el-avatar :size="30">
                            <img :src="reply.profile_image || generateLetterAvatar(reply.full_name)" alt="用户头像" />
                          </el-avatar>
                        </div>
                        <div class="wy-comment-body">
                          <div class="authorWrap">
                            <div class="author">{{ reply.full_name }}@{{ reply.username }}</div>
                            <el-tag type="primary" effect="light"
                              v-if="reply.user_id === articleDetail.author">作者</el-tag>
                          </div>
                          <div class="content">
                            <div class="quote" v-if="reply.pid > 0">
                              {{ getQuoteComment(reply.pid) }}
                            </div>
                            {{ reply.comment }}
                          </div>
                          <div class="info">
                            {{ formatDateTime(reply.createtime, 'MM-DD') }} ·
                            {{ reply.location || '-' }}
                          </div>
                          <div class="operations">
                            <div class="wy-block">
                              <el-button circle style="border: 0">
                                <template #icon>
                                  <el-icon :size="20">
                                    <IconLoveHeart fill="none" stroke="currentColor" />
                                  </el-icon>
                                </template>
                              </el-button>
                              {{ reply.likes || 0 }}
                            </div>
                            <div class="wy-block">
                              <el-button circle style="border: 0">
                                <template #icon>
                                  <el-icon :size="20">
                                    <IconUnlike />
                                  </el-icon>
                                </template>
                              </el-button>
                              {{ reply.unlikes || 0 }}
                            </div>
                            <div class="wy-block">
                              <el-button type="info" :text="textBtn" round plain
                                @click.stop="handleShowInnerDrawer(item.id, reply.id)">回复</el-button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </el-row>
        </el-container>
        <!-- 回复评论抽屉 -->
        <el-drawer v-model="innerDrawer" :title="t('article.detail.reply')" :size="replyDrawerSize"
          :append-to-body="true" :before-close="handleInnerDrawerClose">
          <el-container direction="vertical" v-if="showReplyForm">
            <el-row>
              <div class="wy-comment-author">
                <el-avatar :size="30" :src="appStore.userInfo?.profile_image || '/src/assets/avatar.png'" />
                <div class="author">{{ appStore.userInfo?.username || 'Anonymous' }}</div>
              </div>
            </el-row>
            <el-row>
              <el-input v-model="replyInput" :rows="5" type="textarea"
                :placeholder="t('article.detail.write_comment')" />
            </el-row>
            <el-row justify="end">
              <el-button type="primary" round style="margin-top: 1rem" @click="handleSubmitReply">{{
                t('article.detail.submit') }}</el-button>
            </el-row>
            <el-divider />
          </el-container>
          <div v-if="commentFormTip.trim() && needLogin" class="wy-comment-form-tip">
            {{ commentFormTip }}
            <el-button type="primary" size="small" @click="handleLogin">{{ t('navbar.item.login') }}</el-button>
          </div>
          <div v-else-if="commentFormTip.trim()" class="wy-comment-form-tip">
            {{ commentFormTip }}
          </div>
        </el-drawer>
      </template>
    </el-drawer>

    <el-backtop :right="20" :bottom="100">
      <iconify-icon icon="tdesign:backtop" width="24" height="24" />
    </el-backtop>

    <el-dialog v-model="dialogVisible" :title="t('article.detail.share_to_wechat')" width="500">
      <div id="wy-wechat-share-qrcode"></div>
      <div>{{ t('article.detail.scan_qr_code') }}</div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">{{ t('common.cancel') }}</el-button>
          <el-button type="primary" @click="dialogVisible = false">{{ t('common.confirm') }}</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, computed, onUnmounted, reactive, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAppStore } from '@/stores/app'
import type { TagProps } from 'element-plus'
import { Star, ChatLineRound, CollectionTag, Share, Refresh } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import QRCodeStyling from 'qr-code-styling'
import {
  getBlogDetail,
  createBlogCommentApi,
  getBlogCommentsList,
  likeArticleApi,
  addLikeArticleApi,
  unlikeArticleApi,
  checkLikeArticleApi,
  checkBookmarkArticleApi,
  bookmarkArticleApi,
  unbookmarkArticleApi,
  updateViewDurationApi
} from '@/api/services/blog'
import { getRecommendArticles, type RecommendArticle } from '@/api/services/articles'
import { highlightCodeBlock } from '@/utils/codeHighlight'
import { formatDateTime } from '@/utils/dateUtils'
import IconifyIcon from '../components/IconIfy.vue'
import PlaceholderImage from '../components/PlaceholderImage.vue'
import { generateLetterAvatar } from '@/utils/avatarUtils'

// import type { DrawerProps } from 'element-plus'
// import IconLoveHeart from './components/icons/IconLoveHeart.vue'
const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const { t } = useI18n()

// API 基础 URL（用于 sendBeacon 等不通过 axios 的请求）
const API_BASE_URL = (import.meta.env as any).VITE_API_BASE_URL || 'http://127.0.0.1:8000/api'

// 操作按钮显示状态
const isShowFixedActions = ref(true)
// 操作按钮A的引用（用于IntersectionObserver）
const actionsAnchorRef = ref<HTMLElement | null>(null)

const dialogVisible = ref(false)

const textBtn = ref(true)
const showCommentForm = ref(false)
const showReplyForm = ref(false)

const commentList_order = ref('top')
const circleUrl = ref('../assets/avatar.png')
const imgurl = 'https://fuss10.elemecdn.com/e/5d/4a731a90594a4af544c0c25941171jpeg.jpeg'
const fillColor = ref('none')
const fillStroke = ref('currentColor')
const commentsInput = ref('')
const replyInput = ref('')

const networks = [
  { network: 'weixin', name: '微信', icon: 'fab fa-lg fa-weixin', color: '#07C160' },
  { network: 'xiaohongshu', name: '小红书', icon: 'fas fa-lg fa-book', color: '#FF2442' },
  { network: 'zhihu', name: '知乎', icon: 'fab fa-lg fa-quora', color: '#0066FF' },
  { network: 'weibo', name: '微博', icon: 'fab fa-lg fa-weibo', color: '#e9152d' },
  { network: 'baidu', name: '百度', icon: 'fas fa-lg fa-paw', color: '#2529d8' },
  { network: 'qq', name: 'QQ', icon: 'fab fa-lg fa-qq', color: '#12B7F5' },
  { network: 'baidu', name: 'Baidu', icon: 'fas fa-lg fa-paw', color: '#2529d8' },
  { network: 'buffer', name: 'Buffer', icon: 'fab fa-lg fa-buffer', color: '#323b43' },
  { network: 'email', name: 'Email', icon: 'far fa-lg fa-envelope', color: '#333333' },
  { network: 'evernote', name: 'Evernote', icon: 'fab fa-lg fa-evernote', color: '#2dbe60' },
  { network: 'facebook', name: 'Facebook', icon: 'fab fa-lg fa-facebook-f', color: '#1877f2' },
  { network: 'flipboard', name: 'Flipboard', icon: 'fab fa-lg fa-flipboard', color: '#e12828' },
  {
    network: 'hackernews',
    name: 'HackerNews',
    icon: 'fab fa-lg fa-hacker-news',
    color: '#ff4000'
  },
  { network: 'instapaper', name: 'Instapaper', icon: 'fas fa-lg fa-italic', color: '#428bca' },
  { network: 'line', name: 'Line', icon: 'fab fa-lg fa-line', color: '#00c300' },
  { network: 'linkedin', name: 'LinkedIn', icon: 'fab fa-lg fa-linkedin', color: '#007bb5' },
  {
    network: 'messenger',
    name: 'Messenger',
    icon: 'fab fa-lg fa-facebook-messenger',
    color: '#0084ff'
  },
  {
    network: 'odnoklassniki',
    name: 'Odnoklassniki',
    icon: 'fab fa-lg fa-odnoklassniki',
    color: '#ed812b'
  },
  { network: 'pinterest', name: 'Pinterest', icon: 'fab fa-lg fa-pinterest', color: '#bd081c' },
  { network: 'pocket', name: 'Pocket', icon: 'fab fa-lg fa-get-pocket', color: '#ef4056' },
  { network: 'quora', name: 'Quora', icon: 'fab fa-lg fa-quora', color: '#a82400' },
  { network: 'reddit', name: 'Reddit', icon: 'fab fa-lg fa-reddit-alien', color: '#ff4500' },
  { network: 'skype', name: 'Skype', icon: 'fab fa-lg fa-skype', color: '#00aff0' },
  { network: 'sms', name: 'SMS', icon: 'far fa-lg fa-comment-dots', color: '#333333' },
  {
    network: 'stumbleupon',
    name: 'StumbleUpon',
    icon: 'fab fa-lg fa-stumbleupon',
    color: '#eb4924'
  },
  {
    network: 'telegram',
    name: 'Telegram',
    icon: 'fab fa-lg fa-telegram-plane',
    color: '#0088cc'
  },
  { network: 'tumblr', name: 'Tumblr', icon: 'fab fa-lg fa-tumblr', color: '#35465c' },
  { network: 'twitter', name: 'Twitter', icon: 'fab fa-lg fa-twitter', color: '#1da1f2' },
  { network: 'viber', name: 'Viber', icon: 'fab fa-lg fa-viber', color: '#59267c' },
  { network: 'vk', name: 'Vk', icon: 'fab fa-lg fa-vk', color: '#4a76a8' },
  { network: 'whatsapp', name: 'Whatsapp', icon: 'fab fa-lg fa-whatsapp', color: '#25d366' },
  { network: 'wordpress', name: 'Wordpress', icon: 'fab fa-lg fa-wordpress', color: '#21759b' },
  { network: 'xing', name: 'Xing', icon: 'fab fa-lg fa-xing', color: '#026466' },
  { network: 'yammer', name: 'Yammer', icon: 'fab fa-lg fa-yammer', color: '#0072c6' },
  { network: 'fakeblock', name: 'Custom Network', icon: 'fab fa-lg fa-vuejs', color: '#41b883' }
]

const expandedRepliesIds = ref<number[]>([])
const handleSocialShare = (network: any) => {
  const url = encodeURIComponent(pageUrl.value)
  const title = encodeURIComponent(pageTitle.value)
  const description = encodeURIComponent(pageDescription.value || '')

  let shareUrl = ''

  switch (network.network) {
    case 'weixin': {
      // 修复重复弹出对话框问题：完全重写实现，确保只显示一个对话框
      const qrCodeUrl: string = decodeURIComponent(url)
      // const containerId: string = 'qr-code-container-' + Date.now();
      const containerId: string = 'wy-wechat-share-qrcode'

      dialogVisible.value = true
      // 对话框显示后创建并渲染二维码
      setTimeout(() => {
        try {
          const container: HTMLElement | null = document.getElementById(containerId)
          if (container) {
            // 创建二维码实例
            const qrCode = new QRCodeStyling({
              width: 256,
              height: 256,
              data: qrCodeUrl,
              margin: 10,
              dotsOptions: {
                color: '#000000',
                type: 'square'
              },
              backgroundOptions: {
                color: '#ffffff'
              }
            })

            // 清空容器并渲染二维码
            container.innerHTML = ''
            qrCode.append(container)
          }
        } catch (error: unknown) {
          console.error('二维码生成失败:', error)
          ElMessage.error(t('article.detail.qrcode_failed'))
        }
      }, 100)

      // 确保函数提前返回，不执行后续代码
      return
    }
    case 'xiaohongshu':
      // 小红书没有官方分享API，提示用户复制链接
      ElMessageBox({
        title: t('article.detail.tip'),
        message: t('article.detail.copy_link_hint'),
        type: 'info'
      })
      navigator.clipboard.writeText(decodeURIComponent(url))
      ElMessage.success(t('article.detail.link_copied'))
      break
    case 'zhihu':
      shareUrl = `https://www.zhihu.com/share?url=${url}&title=${title}`
      break
    case 'weibo':
      shareUrl = `http://service.weibo.com/share/share.php?url=${url}&title=${title}&pic=&appkey=`
      break
    case 'qq':
      shareUrl = `https://connect.qq.com/widget/shareqq/index.html?url=${url}&title=${title}&desc=${description}`
      break
    case 'facebook':
      shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${url}`
      break
    case 'twitter':
      shareUrl = `https://twitter.com/intent/tweet?url=${url}&text=${title}`
      break
    case 'linkedin':
      shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${url}`
      break
    case 'email':
      shareUrl = `mailto:?subject=${title}&body=${description} ${url}`
      break
    case 'whatsapp':
      shareUrl = `https://api.whatsapp.com/send?text=${title} ${url}`
      break
    default:
      // 对于其他平台，使用通用分享方式
      shareUrl = url
  }

  if (shareUrl) {
    window.open(shareUrl, '_blank', 'noopener,noreferrer')
  }
}

const toggleReplies = (commentId: number) => {
  const index = expandedRepliesIds.value.indexOf(commentId)
  if (index > -1) {
    expandedRepliesIds.value.splice(index, 1)
  } else {
    expandedRepliesIds.value.push(commentId)
  }
  loadCommentsList('reply', commentId)
}

type TagItem = { id: number; name: string; slug: string }
const tagTtems = ref<Array<TagItem>>([])

const drawer = ref(false)
const innerDrawer = ref(false)

const articleDetail = ref<any>()
const articleStat = ref<any>()
const articleAuthor = ref('')
const articleUsername = ref('')
const articleSeries = ref<any>()
const readTime = ref('')
// 目录相关
const showArticleTOC = ref(false)
const tableOfContents = ref('')
// 检查当前文章当前用户收藏状态
const isBookmarked = ref(false)

// 阅读时长跟踪相关
const viewStartTime = ref<number>(0)
const isTrackingView = ref(false)


// 推荐文章相关
const recommendArticles = ref<RecommendArticle[]>([])
const recommendLoading = ref(false)
const recommendOffset = ref(0)
// 带代码高亮的文章内容
const highlightedContent = computed(() => {
  if (!articleDetail.value) {
    return ''
  }
  // 优先使用带有ID的内容（用于目录跳转），否则使用原始内容
  const contentToRender = articleDetail.value.contentWithIds || articleDetail.value.content
  return highlightCodeBlock(contentToRender)
})

// 从HTML内容中提取标题并生成目录结构
interface TableOfContentItem {
  id: string
  text: string
  level: number
  children: TableOfContentItem[]
}

// 生成唯一ID
const generateId = (text: string, level: number, index: number) => {
  return `toc-${level}-${text
    .toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/[^a-z0-9-]/g, '')}-${index}`
}

// 提取目录
const extractTableOfContents = (
  html: string
): { items: TableOfContentItem[]; contentWithIds: string } => {
  const parser = new DOMParser()
  const doc = parser.parseFromString(html, 'text/html')
  const headings = Array.from(doc.querySelectorAll('h1, h2, h3, h4, h5, h6'))

  const items: TableOfContentItem[] = []
  const stack: TableOfContentItem[] = []

  headings.forEach((heading, index) => {
    const level = parseInt(heading.tagName.replace('H', ''))
    const text = heading.textContent || ''
    const id = generateId(text, level, index)

    // 直接在 DOM 元素上设置 ID，而不是使用正则替换
    heading.id = id

    const item: TableOfContentItem = {
      id,
      text,
      level,
      children: []
    }

    // 维护目录层级结构
    while (stack.length > 0 && stack[stack.length - 1].level >= level) {
      stack.pop()
    }

    if (stack.length === 0) {
      items.push(item)
    } else {
      stack[stack.length - 1].children.push(item)
    }

    stack.push(item)
  })

  // 将修改后的 DOM 序列化回 HTML 字符串
  const contentWithIds = doc.body.innerHTML

  return { items, contentWithIds }
}

// 渲染目录HTML
const renderTableOfContents = (items: TableOfContentItem[]): string => {
  if (items.length === 0) return ''

  let html = '<ul class="toc-list">'

  items.forEach((item) => {
    html += `<li class="toc-item toc-level-${item.level}">`
    // 使用data-id属性而不是href，避免默认的锚点跳转行为
    html += `<a href="javascript:void(0)" data-id="${item.id}" class="toc-link">${item.text}</a>`

    if (item.children.length > 0) {
      html += renderTableOfContents(item.children)
    }

    html += '</li>'
  })

  html += '</ul>'
  return html
}

// 生成目录
const generateTableOfContents = () => {
  let content = articleDetail.value?.content || '<p>No content yet.</p>'

  let tableOfContentsHtml = ''

  // 如果启用了目录功能，则提取目录
  if (articleDetail.value?.enable_table_content) {
    const { items, contentWithIds } = extractTableOfContents(content)

    if (items.length > 0) {
      tableOfContentsHtml = `
          <h3 class="toc-title">Table of Contents</h3>
            ${renderTableOfContents(items)}
        `
      // 保存带有ID的内容到临时属性
      articleDetail.value.contentWithIds = contentWithIds
      showArticleTOC.value = true
      tableOfContents.value = tableOfContentsHtml

      // 监听目录点击事件
      setTimeout(() => {
        setupTableOfContentsListeners()
      }, 50)
    }
  } else {
    // 如果禁用了目录功能，移除目录HTML
    showArticleTOC.value = false
    tableOfContents.value = ''
  }
}

// 设置目录点击监听器
const setupTableOfContentsListeners = () => {
  const tocLinks = document.querySelectorAll('.table-of-contents .toc-link')
  tocLinks.forEach((link) => {
    link.addEventListener('click', (e) => {
      e.preventDefault()
      const targetId = (e.target as HTMLElement).getAttribute('data-id')
      if (targetId) {
        const targetElement = document.getElementById(targetId)
        if (targetElement) {
          // 平滑滚动到目标元素
          targetElement.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          })
        }
      }
    })
  })
}

// 切换评论表单显示状态
const commentFormTip = ref('')
const needLogin = ref(false)
const toggleCommentForm = () => {
  if (appStore.disable_comment) {
    showCommentForm.value = false
    showReplyForm.value = false
    commentFormTip.value = t('article.detail.comment_disabled')
  } else if (articleDetail.value.disable_comments) {
    showCommentForm.value = false
    showReplyForm.value = false
    commentFormTip.value = t('article.detail.comment_disabled')
  } else if (appStore.userInfo && appStore.userInfo.username) {
    showCommentForm.value = true
    showReplyForm.value = true
    commentFormTip.value = ''
  } else {
    showCommentForm.value = false
    showReplyForm.value = false
    commentFormTip.value = t('article.detail.login_to_comment')
    needLogin.value = true
  }
}

// 处理登录按钮点击
const handleLogin = () => {
  router.push(
    '/login?redirect=' + encodeURIComponent(window.location.pathname + window.location.search)
  )
}

// 加载文章详情
const pageTitle = ref('')
const pageDescription = ref('')
const pageUrl = ref(window.location.href)
const loadArticleDetail = async () => {
  try {
    const res = await getBlogDetail(route.params.slug as string)
    if (res.code === 1) {
      if (!res.data.article || res.data.article.status != 'published') {
        router.push('/404')
        return
      }

      articleDetail.value = res.data.article
      tagTtems.value = res.data.tags
      circleUrl.value = res.data.profile_image || '/src/assets/avatar.png'
      articleAuthor.value = res.data.full_name || 'Unknown'
      articleUsername.value = res.data.username || ''
      articleStat.value = res.data.stat_data
      articleSeries.value = res.data.series

      // 过滤文章中的所有html标签
      const content = articleDetail.value.content.replace(/<\/?[^>]+(>|$)/g, '')
      const readWords = 400 //成年人专注阅读每分钟阅读150-200字，专注阅读800字
      readTime.value = `${Math.ceil(content.length / readWords)}`

      // 动态设置浏览器标题和meta标签
      if (articleDetail.value?.title) {
        const title = articleDetail.value.seo_title || articleDetail.value.title
        const description = articleDetail.value.seo_desc || content.slice(0, 150)
        const imageUrl = articleDetail.value.og_image || articleDetail.value.cover || ''

        // 设置页面标题
        document.title = title + ' - ' + appStore.site_title || '默认标题'
        pageTitle.value = title

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
        pageDescription.value = description

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

      // 直接生成目录，移除延迟，确保内容和目录同步
      generateTableOfContents()
    } else {
      router.push('/404')
      return
    }
  } catch (error) {
    router.push('/404')
    return
  }
}

// 检查当前文章当前用户点赞状态
const checkLikeStatus = () => {
  if (appStore.userInfo && appStore.userInfo.username) {
    // 登录状态，已登录
    checkLikeArticleApi(articleDetail.value.id).then((res) => {
      if (res.code === 1 && res.data.is_liked) {
        fillColor.value = 'red'
        fillStroke.value = 'none'
        isLiked.value = true
      }
    })
  }
}

const lastLikeTime = ref(Date.now())
const likeClicks = ref(0)
const isLiked = ref(false)
console.log('页面加载时的时间', lastLikeTime.value)

// JavaScript 实现 +1 向上飘起动画
const showLikeAnimation = (event?: MouseEvent) => {
  // 获取被点击的按钮元素
  let targetButton: HTMLElement | null = null

  if (event && event.target) {
    // 从事件目标向上查找按钮元素
    let el = event.target as HTMLElement
    while (el && el.tagName !== 'BUTTON') {
      el = el.parentElement as HTMLElement
    }
    targetButton = el
  }

  // 如果没有从事件获取到，尝试查找可见的按钮
  if (!targetButton) {
    const btnAreaA = document.querySelector('[data-like-btn-area-a]') as HTMLElement | null
    const btnAreaB = document.querySelector('[data-like-btn-area-b]') as HTMLElement | null

    let targetContainer: HTMLElement | null = null
    if (btnAreaB && window.getComputedStyle(btnAreaB).display !== 'none') {
      targetContainer = btnAreaB
    } else if (btnAreaA) {
      targetContainer = btnAreaA
    }

    if (targetContainer) {
      targetButton = targetContainer.querySelector('button') as HTMLElement
    }
  }

  if (!targetButton) return

  // 创建 +1 动画元素
  const animElement = document.createElement('div')
  animElement.textContent = '+1'

  // 获取按钮位置
  const rect = targetButton.getBoundingClientRect()
  animElement.style.cssText = `
    position: fixed;
    left: ${rect.left + rect.width / 2}px;
    top: ${rect.top + rect.height / 2}px;
    transform: translate(-50%, -50%);
    z-index: 9999;
    color: #fff;
    background-color: #000;
    width: 40px;
    height: 40px;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 20px;
    border-radius: 50%;
    pointer-events: none;
    opacity: 0;
  `

  document.body.appendChild(animElement)

  // 使用 Web Animations API 实现动画
  const animation = animElement.animate([
    { transform: 'translate(-50%, -50%) scale(0.5)', opacity: 0 },
    { transform: 'translate(-50%, -50%) scale(1)', opacity: 1, offset: 0.1 },
    { transform: 'translate(-50%, -150%) scale(1.2)', opacity: 0 }
  ], {
    duration: 1200,
    easing: 'ease-out',
    fill: 'forwards'
  })

  // 动画结束后移除元素
  animation.onfinish = () => {
    animElement.remove()
  }
}

const fillLikeColor = (event?: MouseEvent) => {
  fillColor.value = 'red'
  fillStroke.value = 'none'
  // 延时显示动画，让 tooltip 有时间消失
  setTimeout(() => {
    showLikeAnimation(event)
  }, 200)
}

const handleLike = (event: MouseEvent) => {
  console.log('点击点赞按钮时的时间', Date.now())

  // 保存事件引用供后续使用
  const clickEvent = event

  if (appStore.userInfo && appStore.userInfo.username) {
    // 登录状态，已登录
    if (isLiked.value) {
      // 已点赞，比较与上一次点赞行为的时间差，若大于3秒，则取消点赞
      if (Date.now() - lastLikeTime.value > 3000) {
        unlikeArticleApi(articleDetail.value.id).then((res) => {
          if (res.code === 1) {
            articleStat.value.likes -= likeClicks.value ? likeClicks.value : 1
            isLiked.value = false
            fillColor.value = 'none'
            fillStroke.value = 'black'
          }
        })
      } else {
        // 未超过3秒，增加点赞点击次数，更新点赞数
        likeClicks.value += 1
        likeArticleApi(articleDetail.value.id).then((res) => {
          if (res.code === 1) {
            articleStat.value.likes += 1
            isLiked.value = true
            fillLikeColor(clickEvent)
          }
        })
      }
    } else {
      // 未点赞，首次点赞，记录点赞行为并更新点赞数
      likeClicks.value = 1
      addLikeArticleApi(articleDetail.value.id).then((res) => {
        if (res.code === 1) {
          articleStat.value.likes += 1
          isLiked.value = true
          fillLikeColor(clickEvent)
        }
      })
    }
  } else {
    // 未登录，仅更新文章点赞数
    likeClicks.value = 1
    likeArticleApi(articleDetail.value.id).then((res) => {
      if (res.code === 1) {
        articleStat.value.likes += 1
        isLiked.value = true
        fillLikeColor(clickEvent)
      }
    })
  }
  lastLikeTime.value = Date.now()
}

const handleTagClick = (tag: string) => {
  // 处理标签点击事件，例如跳转到相关文章列表页
  console.log(`点击了标签: ${tag}`)
  router.push(`/tag/${tag}`)
}

// 处理评论抽屉显示
const handleShowCommentDrawer = () => {
  drawer.value = true
  loadCommentsList('subject', 0)
}

// 处理回复抽屉关闭
const handleInnerDrawerClose = () => {
  innerDrawer.value = false
}

// 处理回复抽屉显示
const currentSubjectId = ref(0)
const currentReplyId = ref(0)
const handleShowInnerDrawer = (subjectId: number, replyId: number = 0) => {
  innerDrawer.value = true
  currentSubjectId.value = subjectId
  currentReplyId.value = replyId
}

// 根据屏幕宽度动态计算抽屉宽度
const getDrawerWidth = () => {
  const width = window.innerWidth
  if (width >= 1500) return '40%'
  if (width >= 1280) return '50%'
  if (width >= 992) return '60%'
  if (width >= 768) return '90%'
  return '100%'
}

const getReplyDrawerWidth = () => {
  const width = window.innerWidth
  if (width >= 1500) return '30%'
  if (width >= 1280) return '40%'
  if (width >= 992) return '50%'
  if (width >= 768) return '80%'
  return '90%'
}

const handleResize = () => {
  if (drawer.value) {
    drawer.value = false
    drawerSize.value = getDrawerWidth()
    replyDrawerSize.value = getReplyDrawerWidth()
    drawer.value = true
  } else {
    drawerSize.value = getDrawerWidth()
  }
}

onMounted(async () => {
  // 监听窗口大小变化，重新计算抽屉宽度
  window.addEventListener('resize', handleResize)
  // 监听页面滚动
  window.addEventListener('scroll', handleScroll)
  // 强制页面滚动到顶部
  window.scrollTo({ top: 0, behavior: 'smooth' })
  await loadArticleDetail()

  // 开始跟踪阅读时长
  if (articleDetail.value?.id && appStore.userInfo) {
    viewStartTime.value = Date.now()
    isTrackingView.value = true

    // 监听页面可见性变化（用户切换标签页）
    document.addEventListener('visibilitychange', handleVisibilityChange)
  }

  // 加载推荐文章
  await loadRecommendArticles()
  // 检查当前文章当前用户点赞状态
  checkLikeStatus()
  // 检查当前文章当前用户收藏状态
  checkBookmarkStatus()
  await toggleCommentForm()

  // 渲染抖音视频 iframe
  setTimeout(() => {
    renderDouyinIframes()
  }, 100)
})

// 渲染抖音视频 iframe
const renderDouyinIframes = () => {
  const douyinWrappers = document.querySelectorAll('div[data-douyin-video]')
  douyinWrappers.forEach(wrapper => {
    // 如果已经有 iframe，跳过
    if (wrapper.querySelector('iframe')) return

    const embedUrl = wrapper.getAttribute('data-embed-url')
    if (!embedUrl) return

    // 创建一个容器，居中显示抖音播放器
    const innerWrapper = document.createElement('div')
    innerWrapper.style.cssText = 'display: flex; justify-content: center; background: #000; border-radius: 8px; overflow: hidden;'

    const iframe = document.createElement('iframe')
    iframe.setAttribute('src', embedUrl)
    iframe.setAttribute('frameborder', '0')
    iframe.setAttribute('allowfullscreen', 'true')
    iframe.setAttribute('scrolling', 'no')
    iframe.setAttribute('allow', 'autoplay; fullscreen')
    iframe.setAttribute('referrerpolicy', 'unsafe-url')

    // 抖音播放器原始尺寸 320x720，保持原始尺寸
    iframe.style.cssText = 'width: 320px; height: 720px; border-radius: 8px;'

    innerWrapper.appendChild(iframe)
    wrapper.appendChild(innerWrapper)
  })
}

// 监听文章内容变化，重新渲染抖音视频
watch(
  () => articleDetail.value?.content,
  () => {
    setTimeout(() => {
      renderDouyinIframes()
    }, 100)
  }
)

// 监听路由参数变化，重新加载文章详情
watch(
  () => route.params.slug,
  async (newSlug, oldSlug) => {
    if (newSlug && newSlug !== oldSlug) {
      // 先发送上一篇文章的阅读时长更新
      await sendViewDurationUpdate()

      // 重置状态
      recommendArticles.value = []
      recommendOffset.value = 0
      // 重新加载文章详情
      await loadArticleDetail()

      // 开始跟踪阅读时长
      if (articleDetail.value?.id && appStore.userInfo) {
        viewStartTime.value = Date.now()
        isTrackingView.value = true

        // 监听页面可见性变化（用户切换标签页）
        document.addEventListener('visibilitychange', handleVisibilityChange)
      }
      // 重新加载推荐文章
      await loadRecommendArticles()
      // 检查点赞和收藏状态
      checkLikeStatus()
      checkBookmarkStatus()
      // 等待 DOM 更新后滚动到顶部
      await nextTick()
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }
)

// 处理页面可见性变化
const handleVisibilityChange = () => {
  if (document.hidden) {
    // 页面隐藏时发送阅读时长更新
    sendViewDurationUpdate()
  } else {
    // 页面重新显示时重新开始跟踪
    if (articleDetail.value?.id && appStore.userInfo) {
      viewStartTime.value = Date.now()
      isTrackingView.value = true
    }
  }
}

// 发送阅读时长更新
const sendViewDurationUpdate = () => {
  // 只在登录状态且有开始时间记录时发送
  if (!isTrackingView.value || !viewStartTime.value || !appStore.userInfo) {
    return
  }

  const viewDuration = Math.floor((Date.now() - viewStartTime.value) / 1000) // 转换为秒

  // 只有阅读时长大于0才发送更新
  if (viewDuration > 0 && articleDetail.value?.id) {
    // 使用 fetch API 的 keepalive 选项，确保在页面卸载时也能发送请求
    // 后端 CORS 已正确配置（allow_credentials=True + 具体源）
    const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token')
    const headers: Record<string, string> = {
      'Content-Type': 'application/json'
    }

    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    // 使用 fetch with keepalive，不使用 await（fire-and-forget）
    fetch(
      `${API_BASE_URL}/blog/articles/view/duration?article_id=${articleDetail.value.id}&view_duration=${viewDuration}`,
      {
        method: 'POST',
        headers,
        credentials: 'include', // 包含凭证
        keepalive: true, // 确保在页面卸载时也能发送请求
        body: JSON.stringify({
          article_id: articleDetail.value.id,
          view_duration: viewDuration
        })
      }
    ).catch(error => {
      // 静默处理错误，不影响页面导航
      console.debug('更新阅读时长失败（静默）:', error)
    })
  }

  // 重置跟踪状态
  isTrackingView.value = false
  viewStartTime.value = 0
}

// 处理滚动事件，根据操作按钮A的可见性控制固定按钮B的显示
const handleScroll = () => {
  const anchorElement = actionsAnchorRef.value
  if (!anchorElement) return

  // actionsAnchorRef 绑定到 el-row 组件，需要通过 $el 获取实际 DOM 元素
  const domElement = (anchorElement as any).$el || anchorElement as HTMLElement

  const rect = (domElement as HTMLElement).getBoundingClientRect()
  const windowHeight = window.innerHeight

  // 检测 footer 是否可见
  const footerElement = document.querySelector('.wy-footer') as HTMLElement
  let isFooterVisible = false
  if (footerElement) {
    const footerRect = footerElement.getBoundingClientRect()
    // footer 至少部分在视口内
    isFooterVisible = footerRect.top < windowHeight && footerRect.bottom > 0
  }

  // A元素在视口内可见（至少部分可见）
  const isAVisible = rect.top < windowHeight && rect.bottom > 0

  // 当A可见或footer可见时，隐藏B；否则显示B
  isShowFixedActions.value = !isAVisible && !isFooterVisible
}

onUnmounted(() => {
  // 发送阅读时长更新
  sendViewDurationUpdate()
  window.removeEventListener('resize', handleResize)
  window.removeEventListener('scroll', handleScroll)
  document.removeEventListener('visibilitychange', handleVisibilityChange)
})

// 抽屉初始宽度
const drawerSize = ref(getDrawerWidth())
// 回复抽屉初始宽度
const replyDrawerSize = ref(getReplyDrawerWidth())

// 提交评论
const handleSubmitComment = async () => {
  if (!commentsInput.value.trim()) {
    ElMessage.warning(t('article.detail.enter_comment'))
    return
  }
  try {
    const reqData = {
      article_id: articleDetail.value.id,
      type: 'subject' as 'subject',
      subject_id: 0,
      comment: commentsInput.value
    }
    const res = await createBlogCommentApi(reqData)
    if (res.code === 1) {
      ElMessage.success(t('article.detail.comment_success'))
      commentsInput.value = ''
      await loadCommentsList('subject', 0)
    } else {
      ElMessage.error(res.msg || t('article.detail.comment_failed'))
    }
  } catch (error) {
    ElMessage.error(t('article.detail.comment_failed'))
  }
}

// 提交回复
const handleSubmitReply = async () => {
  if (!replyInput.value.trim()) {
    ElMessage.warning(t('article.detail.enter_comment'))
    return
  }
  try {
    const reqData = {
      article_id: articleDetail.value.id,
      type: 'reply' as 'reply',
      subject_id: Number(currentSubjectId.value),
      pid: Number(currentReplyId.value),
      comment: replyInput.value
    }
    const res = await createBlogCommentApi(reqData)
    if (res.code === 1) {
      ElMessage.success(t('article.detail.reply_success'))
      replyInput.value = ''
      await loadCommentsList('reply', Number(currentSubjectId.value))
      handleInnerDrawerClose()
    } else {
      ElMessage.error(res.msg || t('article.detail.reply_failed'))
    }
  } catch (error) {
    ElMessage.error(t('article.detail.reply_failed'))
  }
}

const commentsList = ref<any>([])
const commentList_page = ref(1)
const commentList_pageSize = ref(10)
const repliesList = ref<any>([])
const replyList_page = ref(1)
const replyList_pageSize = ref(10)
// 加载评论/回复列表
const loadCommentsList = async (type: 'subject' | 'reply' = 'subject', subject_id: number = 0) => {
  try {
    const res = await getBlogCommentsList(
      Number(articleDetail.value.id),
      type,
      subject_id,
      commentList_order.value as 'top' | 'new',
      type === 'subject' ? commentList_page.value : replyList_page.value,
      type === 'subject' ? commentList_pageSize.value : replyList_pageSize.value
    )
    if (res.code === 1) {
      if (type === 'subject') {
        commentsList.value = res.data
      } else {
        repliesList.value = res.data
      }
    } else {
      ElMessage.error(res.msg || t('article.detail.load_comments_failed'))
    }
  } catch (error) {
    ElMessage.error(t('article.detail.load_comments_failed'))
  }
}

// 获取引用评论内容
const getQuoteComment = (pid: number) => {
  const quoteComment = repliesList.value.find((item: any) => item.id === pid)
  return quoteComment ? `@${quoteComment.username}：${quoteComment.comment}` : ''
}

// 检查当前文章当前用户收藏状态
const checkBookmarkStatus = async () => {
  if (appStore.userInfo && appStore.userInfo.username) {
    try {
      const res = await checkBookmarkArticleApi(Number(articleDetail.value.id))
      if (res.code === 1) {
        isBookmarked.value = res.data.is_bookmarked
      }
    } catch (error) {
      console.error('检查收藏状态失败', error)
    }
  }
}

// 收藏/取消收藏文章
const handleBookmark = async () => {
  if (!appStore.userInfo || !appStore.userInfo.username) {
    ElMessage.warning(t('profile_edit.please_login'))
    return
  }
  try {
    if (isBookmarked.value) {
      await unbookmarkArticleApi(Number(articleDetail.value.id))
      ElMessage.success(t('article.detail.unbookmark_success'))
    } else {
      await bookmarkArticleApi(Number(articleDetail.value.id))
      ElMessage.success(t('article.detail.bookmark_success'))
    }
    isBookmarked.value = !isBookmarked.value
  } catch (error) {
    ElMessage.error(t('article.detail.bookmark_failed'))
  }
}


// 加载推荐文章
const loadRecommendArticles = async () => {
  if (!articleDetail.value?.id) return

  try {
    const response = await getRecommendArticles(Number(articleDetail.value.id), 3, recommendOffset.value)
    if (response.code === 1 && response.data) {
      recommendArticles.value = response.data.list || []
      // 如果返回的文章少于请求数量，说明已到末尾，重置offset
      if (response.data.list.length < 3) {
        recommendOffset.value = 0
      }
    }
  } catch (error) {
    console.error('加载推荐文章失败:', error)
  }
}

// 换一批功能
const refreshRecommend = async () => {
  recommendLoading.value = true
  try {
    // 每次增加3的偏移量，获取不同的推荐文章
    recommendOffset.value += 3
    await loadRecommendArticles()
    ElMessage.success('已刷新推荐文章')
  } catch (error) {
    ElMessage.error('刷新失败')
  } finally {
    recommendLoading.value = false
  }
}

// 导航到推荐文章
const navigateToArticle = (slug: string) => {
  console.log('Navigating to article:', slug)
  if (!slug) {
    console.error('Slug is empty')
    return
  }
  router.push(`/article/${slug}`)
}

// 点击作者跳转到作者资料页
const handleAuthorClick = () => {
  if (articleUsername.value) {
    router.push(`/profile/${articleUsername.value}`)
  }
}

// 点击系列跳转到系列主页
const handleSeriesClick = () => {
  if (articleSeries.value?.slug) {
    router.push(`/series/${articleSeries.value.slug}`)
  }
}

// 定义组件名称
defineOptions({ name: 'ArticleView' })
</script>

<style lang="scss">
h3 {
  font-size: 1.5rem;
  font-weight: 600;
}

.wy-container-page {
  display: flex;
  flex-direction: column;
  width: 1500px;
  justify-content: center;
  align-items: center;
}

.wy-article-container {
  width: 950px;
  padding: 30px 10px;
}

.wy-title-area {
  display: flex;
  flex-direction: column;
}

.wy-article-title {
  font-size: 3rem;
  font-weight: 800;
  line-height: 1.5;
  text-align: center;
  /* color: #606266; */
  color: var(--el-text-color-regular);
}

.wy-article-subtitle {
  font-size: 1.5rem;
  font-weight: 600;
  line-height: 1.5;
  text-align: center;
  margin-top: 1.5rem;
  /* color: #606266; */
  color: var(--el-text-color-regular);
}

.wy-article-info {
  font-size: 1.2rem;
  line-height: 1.75;
  /* color: #909399; */
  color: var(--el-text-color-secondary);
  margin-bottom: 3.5rem;
  margin-right: 0.5rem;
  margin-left: 0.5rem;
  margin-top: 2rem;
  font-weight: 300;
}

.wy-article-author {
  font-weight: 500;
}

.wy-article-series-row {
  margin-top: -0.5rem;
  margin-bottom: 0.5rem;
}

.wy-article-series-link:hover {
  text-decoration: underline;
}

.wy-article-content-row {
  width: 100%;
  max-width: 100%;
  overflow: hidden;
}

.wy-article-content {
  font-size: 1.25rem;
  line-height: 2;
  padding: 0 50px;
  max-width: 100%;
  overflow: hidden;
  /* color: #606266; */
  color: var(--el-text-color-regular);
}

.wy-article-content p {
  margin-top: 1.5rem;
}

.wy-article-tags {
  margin-top: 3rem;
  padding: 0 45px;
}

.wy-article-tags span {
  cursor: pointer;
  margin: 5px;
}

.wy-article-tags span:hover {
  cursor: pointer;
  margin: 5px;
  background-color: var(--el-color-primary);
  color: var(--el-color-white);
}

.wy-article-more {
  width: 1500px;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 10px;
  margin-bottom: 8rem;
}

.wy-article-more-title {
  margin-top: 3rem;
  margin-bottom: 1rem;
  font-size: 1.25rem;
}

.wy-article-card-wrap {
  margin-top: 2rem;
  cursor: pointer;
}

.wy-article-card {
  min-height: 430px;
  pointer-events: auto;
}

.wy-article-card .head-picture {
  position: relative;
  pointer-events: auto;
}

.wy-article-card .image-clickable {
  pointer-events: none;
}

.wy-article-card .recommend-reason {
  pointer-events: auto;
  cursor: pointer;
}

.wy-article-card .recommend-reason {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 4px 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 0.75rem;
  border-radius: 12px;
  font-weight: 500;
  z-index: 1;
}

.wy-article-card .meta {
  display: flex;
  gap: 15px;
  font-size: 0.875rem;
  color: var(--el-text-color-secondary);
  margin-top: 0.5rem;
}

.wy-article-card:hover {
  cursor: pointer;
}

.wy-article-card .head,
.wy-comment-author {
  display: flex;
  align-items: center;
  margin-bottom: 0.6rem;
}

.wy-article-card .head .author,
.wy-comment-author .author {
  font-weight: 500;
  font-size: 1rem;
  padding-left: 10px;
}

.wy-article-card .title {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--el-text-color-regular);
  margin-top: 0.7rem;
  margin-bottom: 0.6rem;
}

.wy-article-card .summary {
  font-size: 1rem;
  font-weight: 400;
  color: var(--el-text-color-secondary);
  line-height: 1.5rem;
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  line-clamp: 2;
  -webkit-line-clamp: 2;
}

.wy-article-functions {
  display: flex;
  justify-content: center;
  align-items: center;
  border: 1px solid;
  border-color: var(--el-border-color);
  margin-bottom: 3rem;
  margin-top: 3rem;
  padding: 5px 15px;
  height: 3.5rem;
  border-radius: 3.5rem;
  background-color: var(--wy-background-base-color);
  min-width: 290px;
}

/* 固定按钮容器样式 - 固定在视口底部 */
.wy-fixed-actions-container {
  position: fixed;
  bottom: 20px;
  left: calc(50% - 145px);
  z-index: 100;
}

/* 固定按钮容器内的按钮样式 - 添加阴影 */
.wy-fixed-actions-container .wy-article-functions {
  margin-bottom: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.wy-btn-container {
  position: relative;
  min-width: 31px;
  height: 31px;
  margin-right: 5px;
}

.wy-overlay {
  position: absolute;
  top: 0;
  left: 0;
  margin-top: -5px;
}

.wy-circle {
  position: absolute;
  top: calc(50% - 20px);
  left: 50%;
  transform: translateX(-50%);
  z-index: 1;
  color: var(--el-color-white);
  background-color: var(--el-color-black);
  width: 40px;
  height: 40px;
  line-height: 40px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 20px;
  border-radius: 50%;
  pointer-events: none;
  text-align: center;
}

.slide-fade-enter-from {
  opacity: 0;
  transform: translateX(-50%) scale(0.5);
}

.slide-fade-enter-active {
  transition: all 0.2s ease-out;
}

.slide-fade-enter-to {
  opacity: 1;
  transform: translateX(-50%) scale(1);
}

.slide-fade-leave-from {
  top: calc(50% - 20px);
  opacity: 1;
  transform: translateX(-50%) scale(1);
}

.slide-fade-leave-active {
  transition: top 1s ease-out, opacity 1s ease-out, transform 1s ease-out;
}

.slide-fade-leave-to {
  top: calc(50% - 120px);
  opacity: 0;
  transform: translateX(-50%) scale(1.2);
}

.wy-comments-list {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.wy-comment-item,
.wy-reply-item {
  display: flex;
  width: 100%;
  margin-bottom: 0.6rem;
}

.wy-comment-form-tip {
  font-size: 1rem;
  font-weight: 400;
  color: var(--el-text-color-placeholder);
  margin-bottom: 3.5rem;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 3.5rem;
}

.wy-comment-avatar {
  /* width: 50px; */
  padding-right: 5px;
}

.wy-comment-body {
  /* flex-grow: 1; */
  display: flex;
  flex-direction: column;
  padding-left: 10px;
}

.wy-comment-body .authorWrap {
  display: flex;
  margin-bottom: 0.6rem;
  align-items: center;
}

.wy-comment-body .author {
  font-weight: 600;
  font-size: 1rem;
  color: var(--el-text-color-regular);
  margin-right: 0.5rem;
}

.wy-comment-body .content {
  /*font-weight: 400;*/
  font-size: 0.9rem;
  line-height: 1.5rem;
  color: var(--el-text-color-regular);
  margin-bottom: 1rem;
}

.wy-comment-body .content .quote {
  background-color: var(--el-fill-color-dark);
  color: var(--el-text-color-secondary);
  padding: 8px;
  margin-bottom: 0.5rem;
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  line-clamp: 2;
  -webkit-line-clamp: 2;
}

.wy-comment-body .info {
  color: var(--el-text-color-placeholder);
  margin-bottom: 0.6rem;
}

.wy-comment-body .operations {
  display: flex;
  align-items: center;
  margin-bottom: 0.6rem;
}

.wy-comment-body .operations .wy-block {
  margin-right: 0.5rem;
}

.wy-comment-footer {
  width: 100%;
}

.wy-reply-toggle {
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
}

.wy-replies-list {
  margin-left: 60px;
  /* 缩进显示，与评论主体区分 */
  padding-left: 10px;
  border-left: 2px solid var(--el-border-color);
}

.wy-comment-list-head {
  display: flex;
  justify-content: space-between;
  width: 100%;
  margin-bottom: 2rem;
}

.wy-comment-list-head .title {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--el-text-color-regular);
}

.wy-drawer {
  transition: all 0.3s ease-in-out;
}

@media (max-width: 767px) {

  .wy-container-page,
  .wy-article-more {
    width: 100%;
  }

  .wy-article-container {
    width: 100%;
    padding: 30px 10px;
  }

  .wy-article-content,
  .wy-article-tags {
    padding: 0;
    width: 100%;
  }

  .wy-drawer {
    width: 100% !important;
    max-width: none;
  }

  .table-of-contents {
    display: none;
  }

  .tiptap {
    code {
      overflow-x: auto;
    }
  }
}

.tiptap {
  :first-child {
    margin-top: 0;
  }

  /* List styles */
  ul,
  ol {
    padding: 0 1rem;
    margin: 1.25rem 1rem 1.25rem 0.4rem;

    li p {
      margin-top: 0.25em;
      margin-bottom: 0.25em;
    }
  }

  /* Task List styles */
  ul[data-type='taskList'] {
    list-style: none;
    padding: 0;
    margin: 1.25rem 0;
    padding-left: 0.25em;

    li {
      display: flex;
      flex-direction: row;
      align-items: baseline;

      >label {
        display: flex;
        align-items: center;
        margin: 0;
        flex-shrink: 0;
        padding-top: 4px;
        padding-right: 8px;

        input[type='checkbox'] {
          margin: 0;
          cursor: pointer;
        }
      }

      >div {
        flex: 1 1 auto;
        min-width: 0;

        p {
          margin: 0.25rem 0;
        }
      }

      &[data-checked='true'] {
        >div {
          opacity: 0.5;
          text-decoration: line-through;
        }

        >div p {
          opacity: 0.5;
          text-decoration: line-through;
        }
      }
    }
  }

  /* Heading styles */
  h1,
  h2,
  h3,
  h4,
  h5,
  h6 {
    line-height: 1.1;
    margin-top: 2.5rem;
    text-wrap: pretty;
  }

  h1,
  h2 {
    margin-top: 3.5rem;
    margin-bottom: 1.5rem;
  }

  h1 {
    font-size: 1.4rem;
  }

  h2 {
    font-size: 1.2rem;
  }

  h3 {
    font-size: 1.1rem;
  }

  h4,
  h5,
  h6 {
    font-size: 1rem;
  }

  a {
    color: var(--purple);
    cursor: pointer;

    &:hover {
      color: var(--purple-contrast);
    }
  }

  img {
    display: block;
    height: auto;
    margin: 1.5rem 0;
    max-width: 100%;

    &.ProseMirror-selectednode {
      outline: 3px solid var(--purple);
    }
  }

  video {
    display: block;
    height: auto;
    margin: 1.5rem 0;
    max-width: 100%;
    border-radius: 8px;
  }

  table {
    border-collapse: collapse;
    margin: 0;
    overflow: hidden;
    table-layout: fixed;
    width: 100%;

    td,
    th {
      border: 1px solid var(--gray-3);
      box-sizing: border-box;
      min-width: 1em;
      padding: 6px 8px;
      position: relative;
      vertical-align: top;

      >* {
        margin-bottom: 0;
      }
    }

    th {
      background-color: var(--gray-1);
      font-weight: bold;
      text-align: left;
    }

    .selectedCell:after {
      background: var(--gray-2);
      content: '';
      left: 0;
      right: 0;
      top: 0;
      bottom: 0;
      pointer-events: none;
      position: absolute;
      z-index: 2;
    }

    .column-resize-handle {
      background-color: var(--purple);
      bottom: -2px;
      pointer-events: none;
      position: absolute;
      right: -2px;
      top: 0;
      width: 4px;
    }
  }

  .tableWrapper {
    margin: 1.5rem 0;
    overflow-x: auto;
  }

  &.resize-cursor {
    cursor: ew-resize;
    cursor: col-resize;
  }

  /* Code and preformatted text styles */
  code {
    background-color: var(--purple-light);
    border-radius: 0.4rem;
    color: var(--black);
    font-size: 0.85rem;
    padding: 1.5em 2em;
    border: 1px solid var(--gray-3);
    display: block;
    overflow-x: auto;
  }

  pre {
    background: var(--black);
    border-radius: 0.5rem;
    color: var(--white);
    font-family: 'JetBrainsMono', monospace;
    margin: 1.5rem 0;
    padding: 0.75rem 1rem;

    code {
      background: none;
      color: inherit;
      font-size: 0.8rem;
      padding: 0;
      caret-color: var(--white);
    }

    /* Code styling */
    .hljs-comment,
    .hljs-quote {
      color: #616161;
    }

    .hljs-variable,
    .hljs-template-variable,
    .hljs-attribute,
    .hljs-tag,
    .hljs-name,
    .hljs-regexp,
    .hljs-link,
    .hljs-name,
    .hljs-selector-id,
    .hljs-selector-class {
      color: #f98181;
    }

    .hljs-number,
    .hljs-meta,
    .hljs-built_in,
    .hljs-builtin-name,
    .hljs-literal,
    .hljs-type,
    .hljs-params {
      color: #fbbc88;
    }

    .hljs-string,
    .hljs-symbol,
    .hljs-bullet {
      color: #b9f18d;
    }

    .hljs-title,
    .hljs-section {
      color: #faf594;
    }

    .hljs-keyword,
    .hljs-selector-tag {
      color: #70cff8;
    }

    .hljs-emphasis {
      font-style: italic;
    }

    .hljs-strong {
      font-weight: 700;
    }
  }

  blockquote {
    border-left: 3px solid var(--tt-gray-light-a-200);
    /**--gray-3 */
    margin: 1.5rem 0;
    padding-left: 1rem;
  }

  hr {
    border: none;
    border-top: 1px solid var(--tt-gray-light-a-100);
    /**--gray-2 */
    margin: 2rem 0;
  }

  .mention {
    background-color: var(--purple-light);
    border-radius: 0.4rem;
    box-decoration-break: clone;
    color: var(--purple);
    padding: 0.1rem 0.3rem;
    font-weight: 500;
    text-decoration: none;
  }
}

.wy-article-cover {
  width: 100%;
  /* height: 300px; */
  margin-bottom: 3.5rem;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

/** 分享网络 */
.custom-social-share {
  max-height: 400px;
  overflow-y: auto;
}

.share-network-list {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  justify-content: center;
  max-width: 1000px;
  margin: auto;
}

a[class^='share-network-'] {
  flex: none;
  color: #ffffff;
  background-color: #333;
  border-radius: 3px;
  overflow: hidden;
  display: flex;
  flex-direction: row;
  align-content: center;
  align-items: center;
  cursor: pointer;
  margin: 0 10px 10px 0;
}

a[class^='share-network-'] .fah {
  background-color: rgba(0, 0, 0, 0.2);
  padding: 10px;
  flex: 0 1 auto;
}

a[class^='share-network-'] span {
  padding: 0 10px;
  flex: 1 1 0%;
  font-weight: 500;
}

/* 在线视频样式 */
.custom-video-player {
  display: block;
  margin: 1.5rem auto;
  max-width: 100%;
}

/* 抖音视频样式 */
.douyin-video-wrapper {
  margin: 1.5rem auto;
}

/* 推荐文章卡片样式 */
.wy-card-radius {
  border-radius: 8px;
  overflow: hidden;
}

.placeholder-wrap {
  width: 100%;
  height: 230px;
  border-radius: 8px;
  overflow: hidden;
}
</style>

<!-- 目录样式 - 非scoped，确保v-html渲染的内容能正确应用样式 -->
<style>
.table-of-contents {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
  position: fixed;
  top: 80px;
  left: 10px;
  z-index: 1000;
}

.table-of-contents .toc-title {
  font-size: 1.25rem;
  margin-top: 0;
  margin-bottom: 15px;
  font-weight: 600;
}

.table-of-contents .toc-list {
  list-style-type: none !important;
  padding-left: 0;
  margin: 0;
}

/* 确保所有层级的嵌套列表都没有圆点 */
.table-of-contents .toc-list,
.table-of-contents ul.toc-list,
.table-of-contents .toc-list ul,
.table-of-contents ul {
  list-style-type: none !important;
  padding-left: 0;
  margin: 0;
}

.table-of-contents .toc-item {
  margin: 5px 0;
}

.table-of-contents .toc-link {
  color: #495057;
  text-decoration: none !important;
  display: block;
  padding: 4px 0;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.table-of-contents .toc-link:hover {
  color: #343a40;
  background-color: #e9ecef;
  padding-left: 5px;
}

.table-of-contents .toc-link.active {
  color: #007bff;
  font-weight: 500;
}

/* 目录层级缩进 */
.table-of-contents .toc-level-2 {
  padding-left: 20px;
}

.table-of-contents .toc-level-3 {
  padding-left: 40px;
}

.table-of-contents .toc-level-4 {
  padding-left: 60px;
}

.table-of-contents .toc-level-5 {
  padding-left: 80px;
}

.table-of-contents .toc-level-6 {
  padding-left: 100px;
}
</style>
