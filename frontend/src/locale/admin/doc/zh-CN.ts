export default {
  title: '文档管理',
  title_info: '管理文档书中的文档',

  // 返回按钮
  back_to_list: '返回文档书列表',
  btn_create: '新建文档',

  // 状态标签
  status_tabs: {
    all: '全部',
    published: '已发布',
    draft: '草稿',
    hidden: '隐藏'
  },

  // 状态值
  status: {
    published: '已发布',
    draft: '草稿',
    hidden: '隐藏'
  },

  // 搜索和筛选
  search_placeholder: '搜索文档...',
  filter_parent_placeholder: '筛选父文档',
  filter_parent_all: '全部',
  parent_select_placeholder: '选择父文档（可选）',
  top_level_doc: '（顶级文档）',

  // 表格列
  table: {
    title: '标题',
    slug: 'URL标识',
    level: '层级',
    sort_order: '排序',
    view_count: '浏览',
    comment_count: '评论',
    update_time: '更新时间',
    actions: '操作'
  },

  // 操作按钮
  actions: {
    view: '查看',
    edit: '编辑',
    delete: '删除'
  },

  // 空状态
  empty: {
    title: '暂无文档',
    description: '点击"新建文档"创建您的第一个文档'
  },

  // 对话框
  dialog: {
    create_title: '新建文档',
    edit_title: '编辑文档',

    form: {
      title: '标题',
      title_placeholder: '请输入文档标题',
      slug: 'URL标识',
      slug_placeholder: '请输入URL标识',
      slug_prefix: '/{slug}/',
      parent: '父文档',
      sort_order: '排序',
      status: '状态',
      excerpt: '摘要',
      excerpt_placeholder: '文档摘要（可选）',
      content: '内容',
      content_placeholder: '开始编写文档内容...'
    },

    btn_cancel: '取消',
    btn_confirm: '确定'
  },

  // 确认删除
  confirm_delete: {
    title: '确认删除',
    message: '确定要删除文档"{title}"吗？{hasChildren}删除后子文档也将被删除。',
    has_children: '删除后子文档也将被删除。',
    confirm_btn: '确定',
    cancel_btn: '取消'
  },

  // 表单验证
  validation: {
    title_required: '请输入文档标题',
    title_too_long: '标题不能超过255个字符',
    slug_required: '请输入URL标识',
    slug_too_long: 'URL标识不能超过255个字符',
    slug_invalid: '只能包含小写字母、数字和连字符'
  },

  // 消息提示
  message: {
    load_failed: '加载失败',
    docbook_not_found: '文档书不存在',
    load_docbook_failed: '加载文档书失败',
    create_success: '创建成功',
    update_success: '更新成功',
    delete_success: '删除成功',
    delete_failed: '删除失败',
    operation_failed: '操作失败'
  },

  // 层级标签
  level_label: 'Lv'
}
