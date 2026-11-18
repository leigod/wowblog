<template>
  <div class="wy-container-page" :class="{ 'article-blog-mode': isBlogArticle }">
    <!-- 顶栏：blog 版用博客自绘顶栏，网站版用站点导航 -->
    <BlogTopbar
      v-if="isBlogArticle && blogSite.blog"
      :blog="blogSite.blog"
      :navs="blogSite.navs || []"
      :categories="blogSite.categories || []"
      :blog-title="blogTitle"
      :site-favicon="appStore.site_favicon || '/favicon.ico'"
      :is-dark="appStore.isDark"
      :is-authenticated="!!appStore.token && !!appStore.userRole"
      @nav-click="(nav: any) => handleBlogNavClick(nav)"
      @brand-click="goBlogHome"
      @toggle-dark="appStore.toggleDarkMode()"
      @go-write="goWriteNew"
      @search="(kw: string) => router.push({ path: '/search', query: { q: kw } })"
    />
    <el-header v-else class="wy-article-site-header">
      <site-nav :is-dark="appStore.isDark" @change-dark-mode="appStore.toggleDarkMode()" />
    </el-header>

    <div class="wy-article-container">
      <el-container direction="vertical" class="wy-article-content-container">
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
          <div
            class="wy-article-info wy-article-author"
            @click="handleAuthorClick"
            style="cursor: pointer"
          >
            {{ articleAuthor }}
          </div>
          <div class="wy-article-info">·</div>
          <div class="wy-article-info">
            {{ formatDateTime(articleDetail?.createtime, 'YYYY-MM-DD HH:mm') }}
          </div>
          <div class="wy-article-info">·</div>
          <div class="wy-article-info">
            {{ t('article.detail.read_time', { minutes: readTime }) }}
          </div>
        </el-row>
        <!-- 所属系列（横条 pill）：Part of series + 系列名 + 箭头 -->
        <el-row v-if="activeSeriesProgress" justify="center" class="wy-series-pill-row">
          <div class="wy-series-pill" @click="handleSeriesProgressClick(activeSeriesProgress)">
            <div class="wy-series-pill-left">
              <el-icon class="wy-series-pill-icon"><CollectionTag /></el-icon>
              <span class="wy-series-pill-label">{{ t('article.detail.series_prefix') }}</span>
              <span class="wy-series-pill-name">{{ activeSeriesProgress.name }}</span>
            </div>
            <el-icon class="wy-series-pill-arrow"><ArrowRight /></el-icon>
          </div>
        </el-row>
        <!-- 封面：置于标题下方、破格到 1120px（8px 圆角），标题区仍收在 950px 版心 -->
        <div class="wy-article-cover" v-if="articleDetail?.cover">
          <img :src="articleDetail?.cover" alt="Article Cover" />
        </div>
        <!-- 文章内容 -->
        <el-row class="wy-article-content-row">
          <div class="wy-article-content tiptap">
            <div v-html="highlightedContent"></div>
          </div>
        </el-row>

        <el-row>
          <div class="wy-article-tags">
            <el-tag
              v-for="item in tagTtems"
              :key="item.id"
              type="primary"
              effect="light"
              round
              @click="handleTagClick(item.slug)"
            >
              {{ item.name }}
            </el-tag>
          </div>
        </el-row>
        <!-- 标签下方的所属系列卡片：Part N of M + 进度条 + 描述 -->
        <el-row v-if="activeSeriesProgress" justify="center" class="wy-series-card-row">
          <div class="wy-series-card" @click="handleSeriesProgressClick(activeSeriesProgress)">
            <div class="wy-series-card-head">
              <el-icon class="wy-series-card-icon"><CollectionTag /></el-icon>
              <span class="wy-series-card-name">{{ activeSeriesProgress.name }}</span>
            </div>
            <div class="wy-series-card-progress-label">
              {{
                t('article.detail.series_part', {
                  index: activeSeriesProgress.index,
                  total: activeSeriesProgress.total
                })
              }}
            </div>
            <div class="wy-series-card-bar">
              <div
                class="wy-series-card-bar-fill"
                :style="{
                  width: (activeSeriesProgress.index / activeSeriesProgress.total) * 100 + '%'
                }"
              ></div>
            </div>
            <div v-if="activeSeriesProgress.description" class="wy-series-card-desc">
              {{ activeSeriesProgress.description }}
            </div>
          </div>
        </el-row>
        <!-- 操作按钮区域A（在文章末尾，跟随文档流） -->
        <el-row justify="center" ref="actionsAnchorRef">
          <div class="wy-article-functions">
            <div class="wy-btn-container" data-like-btn-area-a>
              <div class="wy-overlay">
                <el-tooltip
                  :show-after="1000"
                  class="box-item"
                  effect="dark"
                  content="Like this article"
                  placement="top"
                >
                  <el-button size="large" circle style="border: 0" @click="handleLike">
                    <template #icon
                      ><el-icon :size="30">
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

            <el-tooltip
              :show-after="1000"
              class="box-item"
              effect="dark"
              content="Write a comment"
              placement="top"
            >
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
            <el-tooltip
              :show-after="1000"
              class="box-item"
              effect="dark"
              content="Add Bookmark"
              placement="top"
            >
              <el-button size="large" circle style="border: 0" @click="handleBookmark">
                <template #icon>
                  <IconifyIcon
                    :icon="
                      isBookmarked
                        ? 'material-symbols-light:bookmark-star'
                        : 'material-symbols-light:bookmark-star-outline'
                    "
                    size="35"
                    :color="isBookmarked ? '#ffcc00' : '#3f3f46'"
                    stroke-width="0.2"
                    :stroke="isBookmarked ? 'none' : 'currentColor'"
                  />
                </template>
              </el-button>
            </el-tooltip>
            <span style="margin-left: 5px" v-if="articleStat?.bookmarks > 0">{{
              articleStat?.bookmarks
            }}</span>
            <el-divider direction="vertical" />
            <el-tooltip
              :show-after="1000"
              class="box-item"
              effect="dark"
              content="Share this article"
              placement="top"
            >
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
                      <div
                        v-for="network in networks"
                        :key="network.network"
                        :style="{
                          width: '100%',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'flex-start',
                          padding: '5px 0',
                          cursor: 'pointer'
                        }"
                        @click="handleSocialShare(network)"
                      >
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
            <el-tooltip
              :show-after="1000"
              class="box-item"
              effect="dark"
              content="Like this article"
              placement="top"
            >
              <el-button size="large" circle style="border: 0" @click="handleLike">
                <template #icon
                  ><el-icon :size="30">
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

        <el-tooltip
          :show-after="1000"
          class="box-item"
          effect="dark"
          content="Write a comment"
          placement="top"
        >
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
        <el-tooltip
          :show-after="1000"
          class="box-item"
          effect="dark"
          content="Add Bookmark"
          placement="top"
        >
          <el-button size="large" circle style="border: 0" @click="handleBookmark">
            <template #icon>
              <IconifyIcon
                :icon="
                  isBookmarked
                    ? 'material-symbols-light:bookmark-star'
                    : 'material-symbols-light:bookmark-star-outline'
                "
                size="35"
                :color="isBookmarked ? '#ffcc00' : '#3f3f46'"
                stroke-width="0.2"
                :stroke="isBookmarked ? 'none' : 'currentColor'"
              />
            </template>
          </el-button>
        </el-tooltip>
        <span style="margin-left: 5px" v-if="articleStat?.bookmarks > 0">{{
          articleStat?.bookmarks
        }}</span>
        <el-divider direction="vertical" />
        <el-tooltip
          :show-after="1000"
          class="box-item"
          effect="dark"
          content="Share this article"
          placement="top"
        >
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
                  <div
                    v-for="network in networks"
                    :key="network.network"
                    :style="{
                      width: '100%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'flex-start',
                      padding: '5px 0',
                      cursor: 'pointer'
                    }"
                    @click="handleSocialShare(network)"
                  >
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

    <!-- 更多文章：blog 版显示「更多来自该 blog 的文章」+ blog 信息区；网站版保留推荐卡片 -->
    <template v-if="isBlogArticle">
      <!-- 通栏浅灰背景；内部 .wy-blog-more 限定 1200px 居中 -->
      <div class="wy-blog-more-section">
        <div class="wy-blog-more">
          <div class="wy-blog-more-title">{{ t('article.detail.more_from_blog') }}</div>
          <div v-if="blogMoreArticles.length > 0" class="wy-blog-more-grid">
            <div
              v-for="item in blogMoreArticles"
              :key="item.id"
              class="wy-blog-more-card"
              @click="goBlogArticle(item.slug)"
            >
              <div class="wy-blog-more-card-text">
                <div class="wy-blog-more-card-title">{{ item.title }}</div>
                <div class="wy-blog-more-card-summary">{{ item.subtitle || '' }}</div>
                <div class="wy-blog-more-card-meta">
                  {{ formatArticleDate(item.pub_time) }} · {{ blogReadMinutes(item) }}
                  {{ t('blog.home.min') }} read
                </div>
              </div>
              <div v-if="item.cover" class="wy-blog-more-card-thumb">
                <img :src="item.cover" :alt="item.title" />
              </div>
            </div>
          </div>
          <el-empty v-else :description="t('article.detail.no_recommend')" />

          <!-- blog 信息区：favicon/头像 + 名称 + 文章数 + 简介 + 社媒 -->
          <div class="wy-blog-info-card">
            <div class="wy-blog-info-logo">
              <img
                v-if="blogSite.blog?.favicon || blogSite.user?.profile_image"
                :src="blogSite.blog?.favicon || blogSite.user?.profile_image"
                :alt="blogTitle"
              />
              <span v-else>{{ blogTitle.charAt(0) }}</span>
            </div>
            <div class="wy-blog-info-main">
              <div class="wy-blog-info-head">
                <span class="wy-blog-info-name" @click="goBlogHome">{{ blogTitle }}</span>
                <span class="wy-blog-info-count"
                  >{{ blogPostsCount }} {{ t('blog.home.posts') }}</span
                >
              </div>
              <div class="wy-blog-info-desc">{{ blogSite.blog?.blog_description || '' }}</div>
            </div>
            <div v-if="blogSocialLinks.length > 0" class="wy-blog-info-social">
              <a
                v-for="link in blogSocialLinks"
                :key="link.platform"
                :href="isUrl(link.url) ? link.url : 'javascript:;'"
                :title="link.platform"
                target="_blank"
                rel="noopener"
              >
                <IconifyIcon :icon="socialIcon(link.platform)" :size="18" />
              </a>
            </div>
          </div>
        </div>
      </div>
    </template>
    <div v-else class="wy-article-more">
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
                  <el-avatar
                    :size="30"
                    :src="item.author_avatar || generateLetterAvatar(item.author_name)"
                  />
                  <div class="author">{{ item.author_name }}</div>
                </div>
                <div class="head-picture">
                  <div class="recommend-reason" @click.stop="navigateToArticle(item.slug)">
                    {{ item.reason }}
                  </div>
                  <el-image
                    v-if="item.cover"
                    style="width: 100%; height: 230px"
                    :src="item.cover"
                    fit="cover"
                    class="wy-card-radius image-clickable"
                  />
                  <div v-else class="placeholder-wrap">
                    <div class="placeholder-cover">
                      <span class="placeholder-mark" aria-hidden="true">{{
                        (item.title || 'W').trim().charAt(0)
                      }}</span>
                      <span class="placeholder-label">{{ t('article.detail.no_cover') }}</span>
                    </div>
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
                <el-avatar :size="30" :src="appStore.userInfo?.profile_image || '/avatar.png'" />
                <div class="author">{{ appStore.userInfo?.username || 'Anonymous' }}</div>
              </div>
            </el-row>
            <el-row>
              <el-input
                v-model="commentsInput"
                :rows="5"
                type="textarea"
                :placeholder="t('article.detail.write_comment')"
              />
            </el-row>
            <el-row justify="end">
              <el-button
                type="primary"
                round
                style="margin-top: 1rem"
                @click="handleSubmitComment"
                >{{ t('article.detail.submit') }}</el-button
              >
            </el-row>
            <el-divider />
          </el-container>
          <div v-if="commentFormTip.trim() && needLogin" class="wy-comment-form-tip">
            {{ commentFormTip }}
            <el-button type="primary" size="small" @click="handleLogin">{{
              t('navbar.item.login')
            }}</el-button>
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
              <div class="title">
                {{ t('article.detail.all_comments', { count: articleStat.comments }) }}
              </div>
              <div>
                <el-select
                  v-model="commentList_order"
                  :placeholder="t('common.select')"
                  style="width: 150px"
                >
                  <el-option :label="t('home.list.hot')" value="top" />
                  <el-option :label="t('home.list.new')" value="new" />
                </el-select>
              </div>
            </div>
            <div class="wy-comments-list">
              <div class="wy-comment-item" v-for="item in commentsList" :key="item.id">
                <div class="wy-comment-avatar">
                  <el-avatar :size="50">
                    <img
                      :src="item.profile_image || generateLetterAvatar(item.full_name)"
                      alt="用户头像"
                    />
                  </el-avatar>
                </div>
                <div class="wy-comment-body">
                  <div class="authorWrap">
                    <div class="author">{{ item.full_name }}@{{ item.username }}</div>
                    <el-tag
                      type="primary"
                      effect="light"
                      v-if="item.user_id === articleDetail.author"
                      >作者</el-tag
                    >
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
                      <el-button
                        type="info"
                        :text="textBtn"
                        round
                        plain
                        @click="handleShowInnerDrawer(item.id)"
                        >{{ t('article.detail.reply') }}</el-button
                      >
                    </div>
                  </div>
                  <div class="wy-comment-footer" v-if="item.replys > 0" :data-subject="item.id">
                    <div class="wy-reply-toggle" @click="toggleReplies(item.id)">
                      <el-button type="primary" link size="small">
                        {{
                          expandedRepliesIds.includes(item.id)
                            ? t('tag.collapse')
                            : t('tag.read_more').replace('...', '')
                        }}
                        {{ t('article.detail.replies', { count: item.replys }) }}
                      </el-button>
                    </div>
                    <div class="wy-replies-list" v-if="expandedRepliesIds.includes(item.id)">
                      <div class="wy-reply-item" v-for="reply in repliesList" :key="reply.id">
                        <div class="wy-comment-avatar">
                          <el-avatar :size="30">
                            <img
                              :src="reply.profile_image || generateLetterAvatar(reply.full_name)"
                              alt="用户头像"
                            />
                          </el-avatar>
                        </div>
                        <div class="wy-comment-body">
                          <div class="authorWrap">
                            <div class="author">{{ reply.full_name }}@{{ reply.username }}</div>
                            <el-tag
                              type="primary"
                              effect="light"
                              v-if="reply.user_id === articleDetail.author"
                              >作者</el-tag
                            >
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
                              <el-button
                                type="info"
                                :text="textBtn"
                                round
                                plain
                                @click.stop="handleShowInnerDrawer(item.id, reply.id)"
                                >回复</el-button
                              >
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
        <el-drawer
          v-model="innerDrawer"
          :title="t('article.detail.reply')"
          :size="replyDrawerSize"
          :append-to-body="true"
          :before-close="handleInnerDrawerClose"
        >
          <el-container direction="vertical" v-if="showReplyForm">
            <el-row>
              <div class="wy-comment-author">
                <el-avatar :size="30" :src="appStore.userInfo?.profile_image || '/avatar.png'" />
                <div class="author">{{ appStore.userInfo?.username || 'Anonymous' }}</div>
              </div>
            </el-row>
            <el-row>
              <el-input
                v-model="replyInput"
                :rows="5"
                type="textarea"
                :placeholder="t('article.detail.write_comment')"
              />
            </el-row>
            <el-row justify="end">
              <el-button type="primary" round style="margin-top: 1rem" @click="handleSubmitReply">{{
                t('article.detail.submit')
              }}</el-button>
            </el-row>
            <el-divider />
          </el-container>
          <div v-if="commentFormTip.trim() && needLogin" class="wy-comment-form-tip">
            {{ commentFormTip }}
            <el-button type="primary" size="small" @click="handleLogin">{{
              t('navbar.item.login')
            }}</el-button>
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
          <el-button type="primary" @click="dialogVisible = false">{{
            t('common.confirm')
          }}</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 页内目录：≥1420px 左侧常显 / 1060~1419px 右侧骨架悬浮 / 更窄隐藏。
         两种形态都只在封面滚出视口后出现，避免与 1120px 宽的封面互相压叠。 -->
    <aside
      v-if="showArticleTOC"
      class="wy-toc-rail"
      :class="{ 'is-visible': tocVisible }"
      aria-label="table of contents"
    >
      <div class="wy-toc-heading">{{ t('article.detail.toc_title') }}</div>
      <div class="wy-toc-scroll" v-html="tableOfContents"></div>
    </aside>

    <aside v-if="showArticleTOC" class="wy-toc-skel" :class="{ 'is-visible': tocVisible }">
      <div class="wy-toc-skel-bars" aria-hidden="true">
        <span class="bar"></span>
        <span class="bar"></span>
        <span class="bar"></span>
        <span class="bar"></span>
        <span class="bar"></span>
      </div>
      <div class="wy-toc-skel-panel">
        <div class="wy-toc-heading">{{ t('article.detail.toc_title') }}</div>
        <div class="wy-toc-scroll" v-html="tableOfContents"></div>
      </div>
    </aside>

    <!-- 移动端目录：<1100px 显示浮动按钮，点开右侧抽屉（避开左下返回顶部按钮） -->
    <button
      v-if="showArticleTOC"
      class="wy-toc-fab"
      type="button"
      :aria-label="t('article.detail.toc_title')"
      @click="tocDrawerVisible = true"
    >
      <el-icon><Tickets /></el-icon>
    </button>
    <el-drawer
      v-model="tocDrawerVisible"
      direction="rtl"
      size="284px"
      :title="t('article.detail.toc_title')"
      class="wy-toc-drawer-outer"
    >
      <div class="wy-toc-drawer">
        <div class="wy-toc-scroll" v-html="tableOfContents"></div>
      </div>
    </el-drawer>

    <!-- footer：blog 版用博客自绘页脚，网站版用站点页脚 -->
    <BlogFooter
      v-if="isBlogArticle && blogSite.blog"
      :impressum="blogSite.blog.impressum"
      :createtime="blogSite.blog.createtime"
      :blog-title="blogTitle"
      :site-favicon="appStore.site_favicon || '/favicon.ico'"
    />
    <site-footer v-else class="wy-article-site-footer" />
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, computed, onUnmounted, reactive, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAppStore } from '@/stores/app'
import type { TagProps } from 'element-plus'
import {
  Star,
  ChatLineRound,
  CollectionTag,
  Share,
  Refresh,
  Tickets,
  ArrowRight
} from '@element-plus/icons-vue'
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
import { getBlogSite, getBlogArticles } from '@/api/services/creator'
import SiteNav from '@/components/SiteNav.vue'
import SiteFooter from '@/components/SiteFooter.vue'
import BlogTopbar from '@/components/blog/BlogTopbar.vue'
import BlogFooter from '@/components/blog/BlogFooter.vue'
import { highlightCodeBlock } from '@/utils/codeHighlight'
import { formatDateTime } from '@/utils/dateUtils'
import IconifyIcon from '../components/IconIfy.vue'
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

/* ---------- 动态详情页布局：作者为 Author 或开通了 blog 时切换到 blog 版 ---------- */
// 详情接口返回的作者角色 / blog 开通状态
const authorRole = ref<string>('')
const blogOpened = ref(false)
// 是否使用 blog 版布局：作者是 Author，或作者开通了 blog
const isBlogArticle = computed(() => authorRole.value === 'Author' || blogOpened.value)
// blog 站点配置（顶栏/footer/信息区数据源）
const blogSite = ref<any>({ blog: null, navs: [], categories: [], series: [], user: {} })
// 所属系列进度（平台 / 个人 blog 两个维度）
const seriesProgress = ref<any>(null)
const blogSeriesProgress = ref<any>(null)
// 当前详情页要展示的系列卡片（blog 版优先 blog 系列，网站版用平台系列）
const activeSeriesProgress = computed(() =>
  isBlogArticle.value ? blogSeriesProgress.value || seriesProgress.value : seriesProgress.value
)
// 「更多来自该 blog 的文章」
const blogMoreArticles = ref<BlogMoreItem[]>([])
const BLOG_MORE_COUNT = 4
type BlogMoreItem = {
  id: number
  title: string
  slug: string
  cover: string | null
  subtitle: string | null
  pub_time: number | null
  content_len?: number
  reads?: number
}
const blogTitle = computed(
  () => blogSite.value.blog?.blog_name || blogSite.value.user?.full_name || articleAuthor.value
)
const blogPostsCount = ref(0)
const blogSocialLinks = computed(() => {
  const links = blogSite.value.blog?.social_links
  return Array.isArray(links) ? links.filter((l: any) => l?.platform && l?.url) : []
})
// 目录相关
const showArticleTOC = ref(false)
const tableOfContents = ref('')
// 目录是否进入可见态（封面滚出后才出现，见 updateTocState）
const tocVisible = ref(false)

// 移动端目录抽屉
const tocDrawerVisible = ref(false)

// 抽屉打开后目录是首次渲染，需要重新挂一次点击监听
watch(tocDrawerVisible, (open) => {
  if (!open) return
  nextTick(() => {
    setTimeout(() => setupTableOfContentsListeners(), 60)
  })
})
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
      // 标题不写进 HTML：模板里用 i18n 渲染（zh「本文目录」/ en「On this page」）
      tableOfContentsHtml = renderTableOfContents(items)
      // 保存带有ID的内容到临时属性
      articleDetail.value.contentWithIds = contentWithIds
      showArticleTOC.value = true
      tableOfContents.value = tableOfContentsHtml

      // 监听目录点击事件
      setTimeout(() => {
        setupTableOfContentsListeners()
        updateTocState()
      }, 80)
    }
  } else {
    // 如果禁用了目录功能，移除目录HTML
    showArticleTOC.value = false
    tableOfContents.value = ''
  }
}

// 目录点击：平滑滚动 + 立即把高亮切到目标章节
const setupTableOfContentsListeners = () => {
  const tocLinks = document.querySelectorAll(
    '.wy-toc-rail .toc-link, .wy-toc-skel .toc-link, .wy-toc-drawer .toc-link'
  )
  tocLinks.forEach((link) => {
    link.addEventListener('click', (e) => {
      e.preventDefault()
      const targetId = (e.currentTarget as HTMLElement).getAttribute('data-id')
      if (targetId) {
        const targetElement = document.getElementById(targetId)
        if (targetElement) {
          // scroll-margin-top 已在样式里留出 sticky 顶栏的高度，这里直接滚到标题
          targetElement.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          })
          document.querySelectorAll('.toc-link').forEach((el) => el.classList.remove('active'))
          document.querySelectorAll(`.toc-link[data-id="${targetId}"]`).forEach((el) => {
            el.classList.add('active')
          })
          // 移动端抽屉：跳转后收起，回到正文
          tocDrawerVisible.value = false
        }
      }
    })
  })
}

/**
 * 目录可见性与章节高亮（scrollspy）。
 * 可见性：封面滚出视口后才出现——封面宽 1120px，会伸进两侧留白，
 * 而目录就挂在那片留白里，不同时出现就永远不会互相压叠。
 * 高亮：取「最后一个已经滚到阅读区（顶部 120px 以内）的标题」作为当前章节。
 */
const updateTocState = () => {
  if (!showArticleTOC.value) return

  const coverEl = document.querySelector('.wy-article-cover') as HTMLElement | null
  const footerEl = document.querySelector('.wy-footer') as HTMLElement | null
  const coverPassed = !coverEl || coverEl.getBoundingClientRect().bottom <= 96
  const footerVisible = footerEl ? footerEl.getBoundingClientRect().top < window.innerHeight : false
  tocVisible.value = coverPassed && !footerVisible

  const headings = Array.from(
    document.querySelectorAll(
      '.wy-article-content h1[id], .wy-article-content h2[id], .wy-article-content h3[id], .wy-article-content h4[id], .wy-article-content h5[id], .wy-article-content h6[id]'
    )
  ) as HTMLElement[]

  if (!headings.length) return

  let currentId = headings[0].id
  for (const heading of headings) {
    if (heading.getBoundingClientRect().top <= 120) {
      currentId = heading.id
    } else {
      break
    }
  }

  document.querySelectorAll('.toc-link').forEach((el) => {
    el.classList.toggle('active', el.getAttribute('data-id') === currentId)
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
      circleUrl.value = res.data.profile_image || '/avatar.png'
      articleAuthor.value = res.data.full_name || 'Unknown'
      articleUsername.value = res.data.username || ''
      articleStat.value = res.data.stat_data
      articleSeries.value = res.data.series
      // 动态布局判断字段
      authorRole.value = res.data.author_role || ''
      blogOpened.value = !!res.data.blog_opened
      seriesProgress.value = res.data.series_progress || null
      blogSeriesProgress.value = res.data.blog_series_progress || null

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

// 加载 blog 版详情页所需的附加数据：站点配置 + 更多来自该 blog 的文章
// 仅当作者开通了 blog 时调用（サイト接口对未开通用户 blog.opened=false）
const loadBlogExtras = async () => {
  if (!blogOpened.value || !articleUsername.value) {
    blogSite.value = { blog: null, navs: [], categories: [], series: [], user: {} }
    blogMoreArticles.value = []
    blogPostsCount.value = 0
    return
  }
  try {
    const siteRes = await getBlogSite(articleUsername.value)
    if (siteRes.code === 1 && siteRes.data) {
      blogSite.value = siteRes.data
    }
    const listRes = await getBlogArticles(articleUsername.value, { limit: BLOG_MORE_COUNT + 1 })
    if (listRes.code === 1 && listRes.data) {
      blogPostsCount.value = listRes.data.total || 0
      // 排除当前文章，取前 N 篇
      const list = (listRes.data.list || []) as any[]
      blogMoreArticles.value = list
        .filter((a) => a.slug !== articleDetail.value?.slug)
        .slice(0, BLOG_MORE_COUNT)
        .map((a) => ({
          id: a.id,
          title: a.title,
          slug: a.slug,
          cover: a.cover,
          subtitle: a.subtitle,
          pub_time: a.pub_time,
          content_len: a.content_len,
          reads: a.reads ?? a.views
        }))
    }
  } catch (error) {
    console.error('加载 blog 附加数据失败:', error)
  }
}

// 浏览器标签页 favicon：blog 版显示该 blog 的图标，网站版显示站点图标。
// 用 watch 而非只在加载后设置一次，是为了覆盖三种时序：
// ① slug 切换时组件复用（不重新 mount）；② blog 配置异步返回；③ 站点配置 applySiteConfig 异步覆盖 favicon。
watch(
  [
    isBlogArticle,
    () => appStore.site_favicon,
    () => blogSite.value.blog?.favicon,
    () => blogSite.value.user?.profile_image
  ],
  () => {
    const blogIcon = blogSite.value.blog?.favicon || blogSite.value.user?.profile_image || ''
    const href =
      isBlogArticle.value && blogIcon ? blogIcon : appStore.site_favicon || '/favicon.ico'
    const link = document.getElementById('dynamic-favicon') as HTMLLinkElement | null
    if (link) link.href = href
  },
  { immediate: true }
)

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
  const animation = animElement.animate(
    [
      { transform: 'translate(-50%, -50%) scale(0.5)', opacity: 0 },
      { transform: 'translate(-50%, -50%) scale(1)', opacity: 1, offset: 0.1 },
      { transform: 'translate(-50%, -150%) scale(1.2)', opacity: 0 }
    ],
    {
      duration: 1200,
      easing: 'ease-out',
      fill: 'forwards'
    }
  )

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
  // blog 版附加数据（站点配置 + 更多来自该 blog 的文章）
  await loadBlogExtras()

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
  douyinWrappers.forEach((wrapper) => {
    // 如果已经有 iframe，跳过
    if (wrapper.querySelector('iframe')) return

    const embedUrl = wrapper.getAttribute('data-embed-url')
    if (!embedUrl) return

    // 创建一个容器，居中显示抖音播放器
    const innerWrapper = document.createElement('div')
    innerWrapper.style.cssText =
      'display: flex; justify-content: center; background: #000; border-radius: 8px; overflow: hidden;'

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
      // blog 版附加数据
      await loadBlogExtras()

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
    ).catch((error) => {
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
  // 目录可见性 + 章节高亮（与下方浮动操作按钮的显隐互不影响）
  updateTocState()

  const anchorElement = actionsAnchorRef.value
  if (!anchorElement) return

  // actionsAnchorRef 绑定到 el-row 组件，需要通过 $el 获取实际 DOM 元素
  const domElement = (anchorElement as any).$el || (anchorElement as HTMLElement)

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
  // 离开详情页恢复站点 favicon，避免 blog 图标残留到其他页面
  const link = document.getElementById('dynamic-favicon') as HTMLLinkElement | null
  if (link) link.href = appStore.site_favicon || '/favicon.ico'
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
    const response = await getRecommendArticles(
      Number(articleDetail.value.id),
      3,
      recommendOffset.value
    )
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

// 点击作者：网站版与 blog 版统一跳平台资料页
const handleAuthorClick = () => {
  if (!articleUsername.value) return
  router.push(`/profile/${articleUsername.value}`)
}

// 所属系列卡片点击：按系列来源分流
// - source='site' → 平台系列 /series/{slug}
// - source='blog' → 个人 blog 系列 /blog/{username}/series/{slug}
const handleSeriesProgressClick = (sp: any) => {
  if (!sp) return
  if (sp.source === 'blog') {
    router.push(`/blog/${articleUsername.value}/series/${sp.slug}`)
  } else if (sp.slug) {
    router.push(`/series/${sp.slug}`)
  }
}

// 顶部旧版系列链接点击（兼容网站版顶部横条）
const handleSeriesClick = () => {
  if (activeSeriesProgress.value) {
    handleSeriesProgressClick(activeSeriesProgress.value)
  } else if (articleSeries.value?.slug) {
    router.push(`/series/${articleSeries.value.slug}`)
  }
}

// 社媒图标映射（与 BlogHomeView 一致）
const socialIcon = (platform: string) => {
  const map: Record<string, string> = {
    github: 'mdi:github',
    twitter: 'mdi:twitter',
    x: 'mdi:twitter',
    linkedin: 'mdi:linkedin',
    instagram: 'mdi:instagram',
    dribbble: 'mdi:basketball',
    website: 'mdi:web',
    weibo: 'mdi:sina-weibo',
    wechat: 'mdi:wechat',
    zhihu: 'mdi:alpha-z-circle',
    bilibili: 'mdi:bilibili',
    douyin: 'mdi:music-note',
    xiaohongshu: 'mdi:book-open-variant',
    gitee: 'mdi:git',
    email: 'mdi:email-outline',
    rss: 'mdi:rss'
  }
  return map[(platform || '').toLowerCase()] || 'mdi:link-variant'
}
const isUrl = (value: string) => /^https?:\/\//i.test(value || '')
const formatArticleDate = (ts: number | null) => {
  if (!ts) return ''
  return new Date(ts * 1000).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}
const blogReadMinutes = (a: BlogMoreItem) => Math.max(1, Math.ceil((a.content_len || 0) / 400))
const goBlogArticle = (slug: string) => {
  if (slug) router.push(`/article/${slug}`)
}
const goBlogHome = () => {
  if (articleUsername.value) router.push(`/blog/${articleUsername.value}`)
}
// blog 顶栏导航：link 外链新开；category/series 跳该博客的专属列表页（按 slug）
const handleBlogNavClick = (nav: any) => {
  if (!nav) return
  if (nav.type === 'link') {
    if (nav.value) window.open(nav.value, '_blank')
    return
  }
  if (!articleUsername.value) return
  if (nav.type === 'series') {
    const slug = blogSite.value.series?.find((s: any) => String(s.id) === nav.value)?.slug || nav.value
    router.push(`/blog/${articleUsername.value}/series/${slug}`)
  } else {
    // 分类导航 value 存 wb_user_categories.id，映射到 slug 后走 /blog/:username/category/:slug
    const slug = blogSite.value.categories?.find((c: any) => String(c.id) === nav.value)?.slug || nav.value
    router.push(`/blog/${articleUsername.value}/category/${slug}`)
  }
}
const goWriteNew = () => {
  window.open(
    appStore.userRole === 'Author' ? '/creator/articles/create' : '/my-articles/create',
    '_blank'
  )
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
  /* 详情页整页通栏：顶栏/footer 必须撑满视口，宽度约束下沉到各内容区块。
     早期这里写死 max-width:1500px，导致顶栏和 footer 被一起框住（大屏两侧留白）。 */
  width: 100%;
  box-sizing: border-box;
  justify-content: center;
  align-items: stretch;
}

.wy-article-container {
  width: 100%;
  max-width: 950px;
  box-sizing: border-box;
  padding: 30px 10px;
  margin: 0 auto;
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
  width: 100%;
  max-width: 1200px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  /* 内部 el-row :gutter="30" 会带 -15px 左右负 margin，
     原 10px padding 吸收不住，加上来正好抵平，避免右侧外凸。 */
  padding: 0 25px;
  margin: 0 auto 8rem;
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
  /* 原为 135deg 紫色渐变，与全站 Zinc + 品牌蓝脱节 */
  background: var(--wy-brand, #2f5fd0);
  color: var(--wy-on-brand, #ffffff);
  font-size: 0.75rem;
  line-height: 1.5;
  border-radius: var(--wy-radius-pill, 999px);
  font-weight: 500;
  z-index: 1;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.18);
}

/* 无封面兜底：与卡片同宽同高，低饱和品牌渐变 + 标题首字水印 */
.wy-article-card .placeholder-wrap {
  height: 230px;
  border-radius: var(--wy-radius-md, 8px);
  overflow: hidden;
}

.wy-article-card .placeholder-cover {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  background: linear-gradient(
    135deg,
    var(--wy-brand-soft, #eef3fd) 0%,
    var(--wy-bg-muted, #f5f5f5) 100%
  );
}

.wy-article-card .placeholder-mark {
  font-size: 56px;
  font-weight: 700;
  line-height: 1;
  color: var(--wy-brand, #2f5fd0);
  opacity: 0.22;
  user-select: none;
}

.wy-article-card .placeholder-label {
  font-size: 12px;
  color: var(--wy-text-tertiary, var(--el-text-color-secondary));
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
  /* 2 行钳制 + 2 行最小高度：无摘要的卡片不再参差 */
  line-height: 1.4;
  min-height: 2.8em;
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-clamp: 2;
}

.wy-article-card .summary {
  font-size: 1rem;
  font-weight: 400;
  color: var(--el-text-color-secondary);
  line-height: 1.5rem;
  min-height: 3rem; /* 2 行 × 1.5rem，空摘要也占住位置，三卡 meta 行对齐 */
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
  transition:
    top 1s ease-out,
    opacity 1s ease-out,
    transform 1s ease-out;
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

  /* 内部栅格 gutter 30 → 每侧 -15px 负 margin；padding 必须 ≥15px 才不会横向溢出
     （原 10px 在 390px 视口实测多出 5px），15px 同时也正好是移动端合适的边距 */
  .wy-article-more {
    padding: 0 15px;
    margin-bottom: 3rem;
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

      > label {
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

      > div {
        flex: 1 1 auto;
        min-width: 0;

        p {
          margin: 0.25rem 0;
        }
      }

      &[data-checked='true'] {
        > div {
          opacity: 0.5;
          text-decoration: line-through;
        }

        > div p {
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

      > * {
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

  /* Code and preformatted text styles
     内联代码保持行内显示（同 SlashEditor 的说明），块级展示由 pre 承担 */
  code {
    background-color: var(--purple-light);
    border-radius: 0.4rem;
    color: var(--black);
    font-size: 0.85rem;
    padding: 0.25rem 0.5rem;
    border: 1px solid var(--gray-3);
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
  /* 破格：标题区 950px，封面放到 1120px 并居中，两侧留白收窄后气势明显变强。
     父容器是内容盒（930px），用负的 margin-left 撑开，窄屏由 min() 自动回收。 */
  width: min(1120px, calc(100vw - 32px));
  margin-left: calc((100% - min(1120px, 100vw - 32px)) / 2);
  margin-bottom: 3rem;
  border-radius: 8px;
  overflow: hidden;
  background: var(--wy-bg-muted, #f4f4f5);

  img {
    display: block;
    width: 100%;
    height: auto;
    max-height: 640px;
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

/* ==================== 动态详情页：顶栏/footer 包装 ==================== */
.wy-article-site-header {
  height: auto;
  padding: 0;
}
.wy-article-site-footer {
  display: block;
}
/* blog 版整页背景与博客首页一致，顶栏自绘 */
.article-blog-mode {
  background: var(--el-bg-color-page, #f7f8fa);
  min-height: 100vh;
}

/* ==================== 所属系列 pill（顶部横条，截图2） ==================== */
.wy-series-pill-row {
  margin: 0.5rem 0 1rem;
}
.wy-series-pill {
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  min-width: min(40rem, 100%);
  max-width: 100%;
  padding: 9px 18px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 22px;
  background: var(--el-bg-color);
  cursor: pointer;
  transition:
    border-color 0.2s,
    box-shadow 0.2s;
}
.wy-series-pill-left {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
.wy-series-pill:hover {
  border-color: var(--el-color-primary);
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.05);
}
.wy-series-pill-icon {
  font-size: 16px;
  color: var(--el-text-color-secondary);
}
.wy-series-pill-label {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}
.wy-series-pill-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}
.wy-series-pill-arrow {
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

/* ==================== 标签下方系列卡片（截图3） ==================== */
.wy-series-card-row {
  margin: 1.5rem 0;
  padding: 0 24px;
}
.wy-series-card {
  width: 100%;
  max-width: 760px;
  padding: 20px 24px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 12px;
  background: var(--el-bg-color);
  cursor: pointer;
  transition:
    border-color 0.2s,
    box-shadow 0.2s;
}
.wy-series-card:hover {
  border-color: var(--el-color-primary);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}
.wy-series-card-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}
.wy-series-card-icon {
  font-size: 18px;
  color: var(--el-color-primary);
}
.wy-series-card-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}
.wy-series-card-progress-label {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  margin-bottom: 8px;
}
.wy-series-card-bar {
  width: 100%;
  height: 3px;
  border-radius: 3px;
  background: var(--el-fill-color);
  overflow: hidden;
  margin-bottom: 10px;
}
.wy-series-card-bar-fill {
  height: 100%;
  border-radius: 3px;
  background: var(--el-text-color-primary);
}
.wy-series-card-desc {
  font-size: 13px;
  line-height: 1.7;
  color: var(--el-text-color-secondary);
}

/* ==================== 更多来自该 blog（截图1） + blog 信息区 ==================== */
/* 通栏浅灰背景：背景撑满视口，内部内容仍限定 1200px 居中（对齐目标站截图） */
.wy-blog-more-section {
  width: 100%;
  margin-top: 3rem;
  /* 上下留白加大：浅灰通栏区与正文、页脚之间留出更清晰的呼吸感 */
  padding: 72px 24px 80px;
  background: var(--el-fill-color-light);
  box-sizing: border-box;
}
/* 列表区与正文封面同宽（1120px） */
.wy-blog-more {
  max-width: 1120px;
  margin: 0 auto;
}
.wy-blog-more-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--el-text-color-primary);
  margin-bottom: 20px;
}
.wy-blog-more-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}
.wy-blog-more-card {
  display: flex;
  gap: 16px;
  align-items: stretch;
  min-height: 200px;
  padding: 16px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 12px;
  background: var(--el-bg-color);
  cursor: pointer;
  transition:
    box-shadow 0.2s,
    border-color 0.2s;
}
.wy-blog-more-card:hover {
  border-color: var(--el-color-primary);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}
/* 文字 : 图片 = 6 : 4 */
.wy-blog-more-card-text {
  flex: 6;
  min-width: 0;
  display: flex;
  flex-direction: column;
}
.wy-blog-more-card-title {
  font-size: 16px;
  font-weight: 600;
  line-height: 1.5;
  color: var(--el-text-color-primary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.wy-blog-more-card-summary {
  font-size: 14px;
  line-height: 1.6;
  color: var(--el-text-color-secondary);
  margin-top: 6px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.wy-blog-more-card-meta {
  font-size: 13px;
  color: var(--el-text-color-placeholder);
  margin-top: auto;
  padding-top: 8px;
}
.wy-blog-more-card-thumb {
  flex: 4;
  min-width: 0;
  align-self: stretch;
  border-radius: 8px;
  overflow: hidden;
  background: var(--el-fill-color-light);
}
.wy-blog-more-card-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.wy-blog-info-card {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 20px;
  padding: 20px 24px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 12px;
  background: var(--el-bg-color);
}
.wy-blog-info-logo {
  width: 48px;
  height: 48px;
  flex-shrink: 0;
  border-radius: 10px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  /* 透明背景：有图时直接露出图片，无图时首字母用主色保证可读 */
  background: transparent;
  color: var(--el-color-primary);
  font-size: 20px;
  font-weight: 600;
}
.wy-blog-info-logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.wy-blog-info-main {
  flex: 1;
  min-width: 0;
}
.wy-blog-info-head {
  display: flex;
  align-items: baseline;
  gap: 10px;
}
.wy-blog-info-name {
  font-size: 17px;
  font-weight: 700;
  color: var(--el-text-color-primary);
  cursor: pointer;
}
.wy-blog-info-count {
  font-size: 14px;
  color: var(--el-text-color-secondary);
}
.wy-blog-info-desc {
  font-size: 14px;
  line-height: 1.6;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}
.wy-blog-info-social {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}
.wy-blog-info-social a {
  color: var(--el-text-color-secondary);
  display: inline-flex;
}
.wy-blog-info-social a:hover {
  color: var(--el-color-primary);
}
@media (max-width: 768px) {
  .wy-blog-more-grid {
    grid-template-columns: 1fr;
  }
  .wy-blog-info-card {
    flex-wrap: wrap;
  }
}
</style>

<!-- 目录样式 - 非scoped，确保 v-html 渲染的目录内容能应用样式 -->
<style>
/* ---------- 页内目录 ----------
   旧实现是钉在视口左上角（top:80/left:10）且宽度随文字伸缩：宽封面一定被压、
   小屏一定压正文。现在改成「挂在版心两侧留白里的目录」：
   ≥1420px 左侧常显 / 1100~1419px 右侧骨架（hover 展开）/ 更窄隐藏。
   两种形态都只在封面滚出视口后才淡入，所以永远不会和 1120px 封面叠在一起。 */
.wy-toc-rail,
.wy-toc-skel {
  position: fixed;
  top: 96px;
  z-index: 900;
  opacity: 0;
  visibility: hidden;
  transform: translateY(6px);
  transition:
    opacity 0.22s ease,
    transform 0.22s ease,
    visibility 0.22s;
  font-size: 13px;
  line-height: 1.5;
  color: var(--wy-text-secondary, #52525b);
}

.wy-toc-rail.is-visible,
.wy-toc-skel.is-visible {
  opacity: 1;
  visibility: visible;
  transform: none;
}

.wy-toc-heading {
  margin-bottom: 10px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--wy-text-tertiary, #71717a);
}

/* 目录过长时目录自己滚，不把整页撑高 */
.wy-toc-rail .wy-toc-scroll,
.wy-toc-skel-panel .wy-toc-scroll {
  max-height: calc(100vh - 220px);
  overflow: hidden auto;
  overscroll-behavior: contain;
}

.wy-toc-rail .wy-toc-scroll::-webkit-scrollbar,
.wy-toc-skel-panel .wy-toc-scroll::-webkit-scrollbar {
  width: 4px;
}

.wy-toc-rail .wy-toc-scroll::-webkit-scrollbar-thumb,
.wy-toc-skel-panel .wy-toc-scroll::-webkit-scrollbar-thumb {
  border-radius: 4px;
  background: var(--wy-border-strong, #d4d4d8);
}

/* ---------- 形态一：左侧常显 ---------- */
.wy-toc-rail {
  display: none;
  left: max(16px, calc(50% - 475px - 232px));
  width: 208px;
}

/* ---------- 形态二：右侧骨架，hover 展开 ---------- */
.wy-toc-skel {
  display: none;
  right: max(12px, calc(50% - 527px));
  width: 40px;
}

.wy-toc-skel-bars {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
  padding: 4px 0;
}

.wy-toc-skel-bars .bar {
  display: block;
  height: 2px;
  border-radius: 2px;
  background: var(--wy-border-strong, #d4d4d8);
}

.wy-toc-skel-bars .bar:nth-child(1) {
  width: 16px;
}
.wy-toc-skel-bars .bar:nth-child(2) {
  width: 26px;
}
.wy-toc-skel-bars .bar:nth-child(3) {
  width: 21px;
}
.wy-toc-skel-bars .bar:nth-child(4) {
  width: 30px;
}
.wy-toc-skel-bars .bar:nth-child(5) {
  width: 18px;
}

.wy-toc-skel-panel {
  position: absolute;
  top: -12px;
  right: -8px;
  width: 248px;
  max-height: calc(100vh - 180px);
  padding: 14px;
  border-radius: 10px;
  background: var(--wy-bg-surface, #fff);
  border: 1px solid var(--wy-border-subtle, #e4e4e7);
  box-shadow: var(--wy-shadow-card-hover, 0 8px 24px rgba(24, 24, 27, 0.08));
  opacity: 0;
  visibility: hidden;
  transform: translateX(6px);
  transition:
    opacity 0.18s ease,
    transform 0.18s ease,
    visibility 0.18s;
}

.wy-toc-skel:hover .wy-toc-skel-panel,
.wy-toc-skel:focus-within .wy-toc-skel-panel {
  opacity: 1;
  visibility: visible;
  transform: none;
}

/* ---------- 目录列表 ---------- */
.wy-toc-rail .toc-list,
.wy-toc-skel .toc-list,
.wy-toc-rail ul,
.wy-toc-skel ul {
  list-style: none !important;
  margin: 0;
  padding: 0;
}

.wy-toc-rail .toc-item,
.wy-toc-skel .toc-item {
  margin: 0;
}

.wy-toc-rail .toc-link,
.wy-toc-skel .toc-link {
  display: block;
  padding: 5px 6px 5px 0;
  border-left: 2px solid transparent;
  color: var(--wy-text-secondary, #52525b);
  text-decoration: none !important;
  transition:
    color 0.15s ease,
    border-color 0.15s ease;
  /* 目录可折行：长标题不撑破 208px 栏宽 */
  white-space: normal;
  overflow-wrap: anywhere;
}

.wy-toc-rail .toc-link:hover,
.wy-toc-skel .toc-link:hover {
  color: var(--wy-text-primary, #18181b);
}

.wy-toc-rail .toc-link.active,
.wy-toc-skel .toc-link.active {
  padding-left: 8px;
  border-left-color: var(--wy-brand, #2f5fd0);
  color: var(--wy-brand, #2f5fd0);
  font-weight: 500;
}

/* 层级缩进（类挂在 li 上） */
.wy-toc-rail .toc-level-2,
.wy-toc-skel .toc-level-2 {
  padding-left: 12px;
}
.wy-toc-rail .toc-level-3,
.wy-toc-skel .toc-level-3 {
  padding-left: 24px;
}
.wy-toc-rail .toc-level-4,
.wy-toc-skel .toc-level-4 {
  padding-left: 32px;
}
.wy-toc-rail .toc-level-5,
.wy-toc-skel .toc-level-5 {
  padding-left: 36px;
}
.wy-toc-rail .toc-level-6,
.wy-toc-skel .toc-level-6 {
  padding-left: 40px;
}

@media (min-width: 1420px) {
  .wy-toc-rail {
    display: block;
  }
}

@media (min-width: 1100px) and (max-width: 1419px) {
  .wy-toc-skel {
    display: block;
  }
}

/* 目录跳转后标题不被 sticky 顶栏压住 */
.wy-article-content h1,
.wy-article-content h2,
.wy-article-content h3,
.wy-article-content h4,
.wy-article-content h5,
.wy-article-content h6 {
  scroll-margin-top: 96px;
}

/* ---------- 移动端：目录浮动按钮 + 抽屉（<1100px 才出现） ---------- */
.wy-toc-fab {
  display: none;
  position: fixed;
  right: 20px;
  /* 返回顶部按钮在 bottom:100，这里叠在它上方，保持右下角一块操作区 */
  bottom: 168px;
  z-index: 950;
  width: 44px;
  height: 44px;
  padding: 0;
  border-radius: 50%;
  border: 1px solid var(--wy-border-subtle, #e4e4e7);
  background: var(--wy-bg-surface, #fff);
  color: var(--wy-text-secondary, #52525b);
  box-shadow: var(--wy-shadow-card-hover, 0 4px 16px rgba(24, 24, 27, 0.1));
  cursor: pointer;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  transition:
    transform 0.16s ease,
    color 0.16s ease;

  &:active {
    transform: scale(0.94);
    color: var(--wy-brand, #2f5fd0);
  }
}

@media (max-width: 1099px) {
  .wy-toc-fab {
    display: flex;
  }
}

/* 抽屉内的目录列表（v-html 内容，沿用全局样式） */
.wy-toc-drawer {
  font-size: 14px;
  line-height: 1.5;
  color: var(--wy-text-secondary, #52525b);
}

.wy-toc-drawer .wy-toc-scroll {
  max-height: calc(100vh - 160px);
  overflow: hidden auto;
  overscroll-behavior: contain;
}

.wy-toc-drawer .toc-list,
.wy-toc-drawer ul {
  list-style: none !important;
  margin: 0;
  padding: 0;
}

.wy-toc-drawer .toc-item {
  margin: 0;
}

.wy-toc-drawer .toc-link {
  display: block;
  padding: 7px 6px 7px 10px;
  border-left: 2px solid transparent;
  color: var(--wy-text-secondary, #52525b);
  text-decoration: none !important;
  white-space: normal;
  overflow-wrap: anywhere;
  transition:
    color 0.15s ease,
    border-color 0.15s ease;
}

.wy-toc-drawer .toc-link:active {
  color: var(--wy-brand, #2f5fd0);
}

.wy-toc-drawer .toc-link.active {
  border-left-color: var(--wy-brand, #2f5fd0);
  color: var(--wy-brand, #2f5fd0);
  font-weight: 500;
}

.wy-toc-drawer .toc-level-2 {
  padding-left: 12px;
}
.wy-toc-drawer .toc-level-3 {
  padding-left: 24px;
}
.wy-toc-drawer .toc-level-4 {
  padding-left: 32px;
}
.wy-toc-drawer .toc-level-5 {
  padding-left: 36px;
}
.wy-toc-drawer .toc-level-6 {
  padding-left: 40px;
}
</style>
