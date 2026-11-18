import { createRouter, createWebHistory } from 'vue-router'
const IndexView = () => import('@/views/IndexView.vue')
const ArticleView = () => import('@/views/ArticleView.vue')
const ListView = () => import('@/views/ListView.vue')
const ArticleEditView = () => import('@/views/ArticleEditView.vue')
const PageView = () => import('@/views/PageView.vue')
const SeriesView = () => import('@/views/SeriesView.vue')
// Author 个人博客首页（magazine 等布局）
const BlogHomeView = () => import('@/views/blog/BlogHomeView.vue')
const BlogSeriesView = () => import('@/views/blog/BlogSeriesView.vue')
const BlogCategoryView = () => import('@/views/blog/BlogCategoryView.vue')
const CategoryView = () => import('@/views/CategoryView.vue')
const LoginView = () => import('@/views/LoginView.vue')
const FrontLoginView = () => import('@/views/FrontLoginView.vue')
const RegisterView = () => import('@/views/RegisterView.vue')
const EmptyView = () => import('@/views/EmptyView.vue')
const ForbiddenView = () => import('@/views/ForbiddenView.vue')
// 文档模块视图组件
const DocBookView = () => import('@/views/DocBookView.vue')
const DocView = () => import('@/views/DocView.vue')
// 目录索引页（一级导航可点击的落地页）
const DocBookIndexView = () => import('@/views/DocBookIndexView.vue')
const CategoryIndexView = () => import('@/views/CategoryIndexView.vue')
const SeriesIndexView = () => import('@/views/SeriesIndexView.vue')
// 管理后台文档管理视图
const DocBookManagementView = () => import('@/views/admin/DocBookManagementView.vue')
const DocManagementView = () => import('@/views/admin/DocManagementView.vue')
// 管理后台视图组件（按需创建）
const AdminDashboard = () => import('@/views/admin/DashboardView.vue')
const AdminAnalytics = () => import('@/views/admin/AnalyticsView.vue')
const AdminSettings = () => import('@/views/admin/SettingsView.vue')
const AdminAppearance = () => import('@/views/admin/AppearanceView.vue')
const ArticleManagementView = () => import('@/views/admin/ArticleManagementView.vue')
const CategoryManagementView = () => import('@/views/admin/CategoryManagementView.vue')
const CreateCategoryView = () => import('@/views/admin/CreateCategoryView.vue')
const SeriesManagementView = () => import('@/views/admin/SeriesManagementView.vue')
const CreateSeriesView = () => import('@/views/admin/CreateSeriesView.vue')
const CreateArticleView = () => import('@/views/admin/CreateArticleView.vue')
const NavbarManagementView = () => import('@/views/admin/NavbarManagementView.vue')
const PageManagementView = () => import('@/views/admin/PageManagementView.vue')
const CreatePageView = () => import('@/views/admin/CreatePageView.vue')
const TagManagementView = () => import('@/views/admin/TagManagementView.vue')
const ContentEditorView = () => import('@/views/admin/ContentEditorView.vue')
const EditPageView = () => import('@/views/admin/EditPageView.vue')
const EditSeriesView = () => import('@/views/admin/EditSeriesView.vue')
const EditCategoryView = () => import('@/views/admin/EditCategoryView.vue')
const MemberManagementView = () => import('@/views/admin/MemberManagementView.vue')
const UserManagementView = () => import('@/views/admin/UserManagementView.vue')
const EditArticleView = () => import('@/views/admin/EditArticleView.vue')
const CommentManagementView = () => import('@/views/admin/CommentManagementView.vue')
const AdminLogsView = () => import('@/views/admin/AdminLogsView.vue')
// Author 个人博客工作台（Creator）
const CreatorSettingsView = () => import('@/views/creator/CreatorSettingsView.vue')
const CreatorAppearanceView = () => import('@/views/creator/CreatorAppearanceView.vue')
const CreatorCategoriesView = () => import('@/views/creator/CreatorCategoriesView.vue')
const CreatorSeriesView = () => import('@/views/creator/CreatorSeriesView.vue')
const CreatorNavsView = () => import('@/views/creator/CreatorNavsView.vue')
const CreatorArticlesView = () => import('@/views/creator/CreatorArticlesView.vue')
const SearchResultView = () => import('@/views/SearchResult.vue')
const NotificationsView = () => import('@/views/NotificationsView.vue')
const InviteAcceptView = () => import('@/views/InviteAcceptView.vue')
const MyArticlesView = () => import('@/views/MyArticlesView.vue')
const ChangePasswordView = () => import('@/views/ChangePasswordView.vue')

const router = createRouter({
  // history: createWebHistory(import.meta.env.BASE_URL),
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // 前端用户登录
    {
      path: '/login',
      name: 'login',
      component: FrontLoginView,
      meta: {
        title: '登录',
        layout: 'blank'
      }
    },
    // 管理后台登录
    {
      path: '/admin/login',
      name: 'admin-login',
      component: LoginView,
      meta: {
        title: '管理后台登录',
        layout: 'blank'
      }
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
      meta: {
        title: '用户注册',
        layout: 'blank'
      }
    },
    {
      path: '/invite/accept/:token',
      name: 'invite-accept',
      component: InviteAcceptView,
      meta: {
        title: '接受邀请',
        layout: 'blank'
      }
    },
    {
      path: '/',
      name: 'home',
      component: IndexView,
      meta: {
        title: '首页'
      }
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue')
    },
    {
      path: '/article/:slug',
      name: 'article',
      component: ArticleView,
      // 顶栏/footer 由组件内按文章来源动态渲染（网站版/ blog 版），故用 blank 布局
      meta: { title: '文章详情', layout: 'blank' }
    },
    {
      path: '/tag/:slug',
      name: 'tag',
      component: ListView,
      meta: {
        title: '文章列表'
      }
    },
    {
      path: '/profile/:username',
      name: 'UserProfile',
      component: () => import('@/views/ProfileView.vue'),
      meta: {
        title: '用户资料'
      }
    },
    {
      path: '/profile/edit',
      name: 'ProfileEdit',
      component: () => import('@/views/ProfileEditView.vue'),
      meta: {
        title: '编辑个人资料',
        requiresAuth: true,
        roles: ['Admin', 'User', 'Editor', 'Contributor', 'Author']
      }
    },
    {
      path: '/change-password',
      name: 'ChangePassword',
      component: ChangePasswordView,
      meta: {
        title: '修改密码',
        requiresAuth: true,
        roles: ['Admin', 'User', 'Editor', 'Contributor', 'Author']
      }
    },
    {
      path: '/search',
      name: 'search',
      component: SearchResultView,
      meta: {
        title: '搜索结果'
      }
    },
    {
      path: '/bookmarks',
      name: 'Bookmarks',
      component: () => import('@/views/BookmarksView.vue'),
      meta: {
        title: '我的收藏',
        requiresAuth: true
      }
    },
    {
      path: '/history',
      name: 'ReadingHistory',
      component: () => import('@/views/ReadingHistoryView.vue'),
      meta: {
        title: '阅读历史',
        requiresAuth: true
      }
    },
    {
      path: '/notifications',
      name: 'notifications',
      component: NotificationsView,
      meta: {
        title: '消息通知',
        requiresAuth: true
      }
    },
    {
      // Author 个人博客首页（公开访问；blank 布局自绘顶栏与 footer）
      path: '/blog/:username',
      name: 'blog-home',
      component: BlogHomeView,
      meta: { title: 'Blog', layout: 'blank' }
    },
    {
      // Author 个人博客的系列列表页（公开访问；blank 布局自绘顶栏与 footer）
      path: '/blog/:username/series/:seriesSlug',
      name: 'blog-series',
      component: BlogSeriesView,
      meta: { title: 'Blog Series', layout: 'blank' }
    },
    {
      // Author 个人博客的分类列表页（公开访问；blank 布局自绘顶栏与 footer）
      path: '/blog/:username/category/:categorySlug',
      name: 'blog-category',
      component: BlogCategoryView,
      meta: { title: 'Blog Category', layout: 'blank' }
    },
    {
      path: '/my-articles',
      name: 'my-articles',
      component: MyArticlesView,
      meta: {
        title: '我的文章',
        requiresAuth: true,
        roles: ['Contributor']
      }
    },
    {
      path: '/403',
      name: 'forbidden',
      component: ForbiddenView,
      meta: {
        title: '禁止访问'
      }
    },
    {
      path: '/404',
      name: 'empty',
      component: EmptyView,
      meta: {
        title: '404'
      }
    },
    /**
     * 在路由配置中添加动态路由
     * 动态路由参数以冒号 : 开头，用于匹配动态部分
     * 例如，/page/:pageSlug 可以匹配 /page/about 或 /page/contact
     * 然后在 `DynamicPageView` 中通过 pageSlug 参数从API加载对应页面内容。
     * ###  注意事项
     * - 动态路由需配合后端API提供页面数据
     * - 需在导航守卫中处理404页面（当页面不存在时）
     * - 考虑使用 vue-router 的 beforeResolve 钩子预加载页面数据
     */
    {
      path: '/page/:pageSlug',
      name: 'dynamic-page',
      component: PageView,
      meta: { title: '动态页面' }
    },
    {
      path: '/series',
      name: 'series-index',
      component: SeriesIndexView,
      meta: { title: '全部系列' }
    },
    {
      path: '/series/:seriesSlug',
      name: 'dynamic-series',
      component: SeriesView,
      meta: { title: '动态系列' }
    },
    {
      path: '/category',
      name: 'category-index',
      component: CategoryIndexView,
      meta: { title: '全部分类' }
    },
    {
      path: '/category/:categorySlug',
      name: 'dynamic-category',
      component: CategoryView,
      meta: { title: '动态分类' }
    },
    // 文档模块路由
    {
      path: '/docs',
      name: 'docbook-index',
      component: DocBookIndexView,
      meta: { title: '文档' }
    },
    {
      path: '/docs/:docbookSlug',
      name: 'docbook',
      component: DocBookView,
      meta: { title: '文档' }
    },
    {
      path: '/docs/:docbookSlug/:docSlug',
      name: 'doc',
      component: DocView,
      meta: { title: '文档详情' }
    },
    {
      path: '/articleedit',
      name: 'articleedit',
      component: ArticleEditView,
      meta: {
        title: '文章编辑'
      }
    },
    // 管理后台路由
    {
      path: '/admin',
      name: 'admin',
      redirect: '/admin/dashboard',
      meta: {
        layout: 'admin',
        title: '管理后台',
        roles: ['Admin'],
        requiresAuth: true
      },
      children: [
        {
          path: 'dashboard',
          name: 'admin-dashboard',
          component: AdminDashboard,
          meta: {
            layout: 'admin',
            title: '控制台',
            roles: ['Admin']
          }
        },
        {
          path: 'analytics',
          name: 'admin-analytics',
          component: AdminAnalytics,
          meta: {
            layout: 'admin',
            title: '数据分析',
            roles: ['Admin']
          }
        },
        {
          path: 'settings',
          name: 'admin-settings',
          component: AdminSettings,
          meta: {
            layout: 'admin',
            title: '系统设置',
            roles: ['Admin']
          }
        },
        {
          path: 'appearance',
          name: 'admin-appearance',
          component: AdminAppearance,
          meta: {
            layout: 'admin',
            title: '外观管理',
            roles: ['Admin']
          }
        },
        {
          path: 'articles',
          name: 'admin-articles',
          component: ArticleManagementView,
          meta: {
            layout: 'admin',
            title: '文章管理',
            roles: ['Admin']
          }
        },
        {
          path: 'categories',
          name: 'admin-categories',
          component: CategoryManagementView,
          meta: {
            layout: 'admin',
            title: '分类管理',
            roles: ['Admin']
          }
        },
        {
          path: 'categories/create',
          name: 'admin-categories-create',
          component: CreateCategoryView,
          meta: {
            layout: 'admin',
            title: '创建分类',
            roles: ['Admin']
          }
        },
        {
          path: 'categories/edit/:id',
          name: 'admin-categories-edit',
          component: EditCategoryView,
          meta: {
            layout: 'admin',
            title: '编辑分类',
            roles: ['Admin']
          }
        },
        {
          path: 'series',
          name: 'admin-series',
          component: SeriesManagementView,
          meta: {
            layout: 'admin',
            title: '系列管理',
            roles: ['Admin']
          }
        },
        {
          path: 'series/create',
          name: 'admin-series-create',
          component: CreateSeriesView,
          meta: {
            layout: 'admin',
            title: '创建系列',
            roles: ['Admin']
          }
        },
        {
          path: 'series/edit/:id',
          name: 'admin-series-edit',
          component: EditSeriesView,
          meta: {
            layout: 'admin',
            title: '编辑系列',
            roles: ['Admin']
          }
        },
        {
          path: 'navbar',
          name: 'admin-navbar',
          component: NavbarManagementView,
          meta: {
            layout: 'admin',
            title: '导航管理',
            roles: ['Admin']
          }
        },
        {
          path: 'pages',
          name: 'admin-pages',
          component: PageManagementView,
          meta: {
            layout: 'admin',
            title: '页面管理',
            roles: ['Admin']
          }
        },
        {
          path: 'pages/create',
          name: 'admin-pages-create',
          component: CreatePageView,
          meta: {
            layout: 'admin',
            title: '创建页面',
            roles: ['Admin']
          }
        },
        {
          path: 'pages/edit/:id',
          name: 'admin-pages-edit',
          component: EditPageView,
          meta: {
            layout: 'admin',
            title: '编辑页面',
            roles: ['Admin']
          }
        },
        {
          path: 'content-editor',
          name: 'admin-content-editor',
          component: ContentEditorView,
          meta: {
            title: '内容编辑器',
            roles: ['Admin'],
            layout: 'blank'
          }
        },
        {
          path: 'tags',
          name: 'admin-tags',
          component: TagManagementView,
          meta: { layout: 'admin', title: '标签管理', roles: ['Admin'] }
        },
        {
          path: 'members',
          name: 'admin-members',
          component: MemberManagementView,
          meta: { layout: 'admin', title: '成员管理', roles: ['Admin'] }
        },
        {
          path: 'users',
          name: 'admin-users',
          component: UserManagementView,
          meta: { layout: 'admin', title: '用户管理', roles: ['Admin'] }
        },
        {
          path: 'docbooks',
          name: 'admin-docbooks',
          component: DocBookManagementView,
          meta: { layout: 'admin', title: '文档书管理', roles: ['Admin'] }
        },
        {
          path: 'docs/:docbookId',
          name: 'admin-docs',
          component: DocManagementView,
          meta: { layout: 'admin', title: '文档管理', roles: ['Admin'] }
        },
        {
          path: 'comments',
          name: 'admin-comments',
          component: CommentManagementView,
          meta: { layout: 'admin', title: '评论管理', roles: ['Admin'] }
        },
        {
          path: 'logs',
          name: 'admin-logs',
          component: AdminLogsView,
          meta: { layout: 'admin', title: '操作日志', roles: ['Admin'] }
        }
      ]
    },
    {
      // Author 个人博客工作台：布局由 meta.layout='admin'（App.vue 的 currentLayout）承担，
      // 父路由不挂 component——否则 AdminLayout 会被渲染两层（外层由 App.vue 包，
      // 内层又作为路由组件渲染在内容区里，形成套娃）。/admin 父路由同此模式。
      path: '/creator',
      meta: { layout: 'admin', roles: ['Author', 'Admin'] },
      children: [
        {
          path: '',
          redirect: '/creator/settings'
        },
        {
          path: 'settings',
          name: 'creator-settings',
          component: CreatorSettingsView,
          meta: { layout: 'admin', title: '常规设置', roles: ['Author', 'Admin'] }
        },
        {
          path: 'appearance',
          name: 'creator-appearance',
          component: CreatorAppearanceView,
          meta: { layout: 'admin', title: '外观设置', roles: ['Author', 'Admin'] }
        },
        {
          path: 'categories',
          name: 'creator-categories',
          component: CreatorCategoriesView,
          meta: { layout: 'admin', title: '分类管理', roles: ['Author', 'Admin'] }
        },
        {
          path: 'series',
          name: 'creator-series',
          component: CreatorSeriesView,
          meta: { layout: 'admin', title: '系列管理', roles: ['Author', 'Admin'] }
        },
        {
          path: 'navs',
          name: 'creator-navs',
          component: CreatorNavsView,
          meta: { layout: 'admin', title: '导航管理', roles: ['Author', 'Admin'] }
        },
        {
          path: 'articles',
          name: 'creator-articles',
          component: CreatorArticlesView,
          meta: { layout: 'admin', title: '文章管理', roles: ['Author', 'Admin'] }
        }
      ]
    },
    {
      path: '/admin/articles/create',
      name: 'admin-articles-create',
      component: CreateArticleView,
      meta: {
        title: '创建文章',
        roles: ['Admin'],
        requiresAuth: true,
        layout: 'blank'
      }
    },
    {
      path: '/admin/articles/edit/:id',
      name: 'admin-articles-edit',
      component: EditArticleView,
      meta: {
        title: '编辑文章',
        roles: ['Admin'],
        requiresAuth: true,
        layout: 'blank'
      }
    },
    // Contributor 的文章创建和编辑路由（Author 已迁移至 /creator/articles/*）
    {
      path: '/my-articles/create',
      name: 'my-articles-create',
      component: CreateArticleView,
      meta: {
        title: '创建文章',
        roles: ['Contributor'],
        requiresAuth: true,
        layout: 'blank'
      }
    },
    {
      path: '/my-articles/edit/:id',
      name: 'my-articles-edit',
      component: EditArticleView,
      meta: {
        title: '编辑文章',
        roles: ['Contributor'],
        requiresAuth: true,
        layout: 'blank'
      }
    },
    // Author 的文章创建/编辑：复用同组件，组件内按路由前缀进入 creator 模式
    // （发布抽屉显示 Blog 分类/系列选择，平台分类隐藏——平台分类由审核者定）
    {
      path: '/creator/articles/create',
      name: 'creator-articles-create',
      component: CreateArticleView,
      meta: {
        title: '创建文章',
        roles: ['Author', 'Admin'],
        requiresAuth: true,
        layout: 'blank'
      }
    },
    {
      path: '/creator/articles/edit/:id',
      name: 'creator-articles-edit',
      component: EditArticleView,
      meta: {
        title: '编辑文章',
        roles: ['Author', 'Admin'],
        requiresAuth: true,
        layout: 'blank'
      }
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 检查路由是否需要认证
  const requiresAuth = to.meta.requiresAuth || to.meta.roles

  if (requiresAuth) {
    // 从 localStorage 检查 token
    const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token')

    // 如果没有 token，重定向到登录页
    if (!token) {
      console.warn('用户未登录，重定向到登录页')
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
      return
    }

    // 如果路由有角色要求，检查用户角色
    if (to.meta.roles && Array.isArray(to.meta.roles)) {
      const userInfo = localStorage.getItem('userInfo')
      const userRole = userInfo ? JSON.parse(userInfo).role : null

      if (!userRole || !to.meta.roles.includes(userRole)) {
        console.warn('用户权限不足，重定向到禁止访问页')
        next('/403')
        return
      }
    }
  }

  next()
})

export default router
