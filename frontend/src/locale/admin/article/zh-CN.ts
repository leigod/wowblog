// 文章管理相关语言（中文）
export default {
  list: {
    title: '文章和草稿',
    subtitle: '您文章和草稿的状态概览',
    tab: {
      all: '所有',
      published: '已发布',
      draft: '草稿',
      scheduled: '定时发布',
      deleted: '已删除'
    },
    search_placeholder: '搜索文章',
    author_search_placeholder: '搜索作者',
    tag_search_placeholder: '搜索标签',
    filter: '筛选',
    filter_articles: '筛选文章',
    authors: '作者',
    tags: '标签',
    date: {
      tab_title: '日期',
      previous_day: '前一天',
      past_3_day: '过去3天',
      past_week: '过去一周',
      past_month: '过去一个月',
      custome_date: '自定义日期',
      custome_date_range: '自定义日期范围',
      start_date: '开始日期',
      end_date: '结束日期'
    },
    table: {
      head: {
        title: '文章标题',
        slug: 'Slug',
        top: '置顶',
        featured: '加精',
        recommend: '轮播推荐',
        actions: '操作'
      },
      menu: {
        pin_to_blog: '置顶',
        unpin: '取消置顶',
        delete: '删除',
        recommend_to_home: '推荐到首页',
        un_recommend: '取消推荐',
        featured: '加精',
        un_featured: '取消加精',
        preview: '预览',
        cancel: '取消',
        restore: '恢复',
        permanently_delete: '永久删除'
      }
    },
    empty: {
      published: {
        title: '没有发布的文章',
        description: '发布您的第一篇文章以开始您的写作之旅。'
      },
      draft: {
        title: '没有草稿文章',
        description: '创建新草稿开始写作。'
      },
      scheduled: {
        title: '没有定时发布的文章',
        description: '计划新文章在稍后发布。'
      },
      deleted: {
        title: '没有删除的文章',
        description: '已删除的文章在这里存储。恢复它们以再次可见。'
      },
      default: {
        title: '没有文章',
        description: '创建新文章以开始您的写作之旅。'
      }
    }
  },
  btn: {
    publish: '发布',
    preview: '预览',
    addcover: '添加封面',
    addsubtitle: '添加副标题',
    update: '更新'
  },
  text: {
    article_editor: '文章编辑器'
  },
  publishform: {
    category: '所属分类',
    series: '所属系列',
    status: '发布状态',
    status_published: '已发布',
    status_draft: '草稿',
    status_scheduled: '定时发布',
    publish_time: '发布时间',
    author: '作者',
    author_tooltip:
      '作者变更将在文章发表后生效。<br/>在那之前，你的文章将保留在草稿中。一旦发布，<br/>新作者将能够编辑它。',
    change_author: '变更作者',
    co_author: '共同作者',
    co_author_addbtn: '添加共同作者',
    co_author_tooltip:
      '从您的团队中选择最多4位合著者。合著者将<br/>无法编辑文章，但会被列为合作者在草稿预览<br/>和文章页面中显示。',
    slug: '文章Slug',
    slug_placeholder: '请输入文章Slug',
    tags: '文章标签',
    tags_placeholder: '请输入文章标签',
    seo_title: 'SEO 标题',
    seo_title_placeholder: '请输入SEO标题',
    seo_description: 'SEO 描述',
    seo_description_placeholder: '请输入SEO描述',
    og_image: '社交媒体转发图片',
    og_image_helptip:
      '请上传一张图片，将用作社交媒体转发或网络引用。如果没有图像，将使用文章封面图像。',
    og_image_placeholder: '推荐尺寸：1200 x 630 px，仅限jpg/png图像，大小不超过2M',
    table: '生成目录',
    table_helptip: '生成文章目录，方便读者快速导航。',
    disable_comments: '禁用评论',
    disable_comments_helptip: '这将隐藏文章下方的评论区。'
  },
  dialog: {
    delete: {
      title: '删除文章',
      description: '确认删除此文章吗？此操作无法撤销。',
      confirm: '删除',
      cancel: '取消',
      success: '文章删除成功。',
      error: '删除文章失败。'
    },
    update: {
      status: {
        success: '文章状态更新成功。',
        error: '更新文章状态失败。'
      },
      success: '文章更新成功。',
      error: '更新文章失败。'
    }
  }
}
