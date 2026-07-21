export default {
  title: '文档书管理',
  title_info: '管理您的文档集合',
  search_placeholder: '搜索文档书...',
  btn_create: '新建文档书',

  table: {
    cover: '封面',
    name: '名称',
    doc_count: '文档数',
    visibility: '可见性',
    sort_order: '排序',
    update_time: '更新时间',
    actions: '操作'
  },

  actions: {
    manage_docs: '管理文档',
    edit: '编辑',
    delete: '删除'
  },

  visibility: {
    public: '公开',
    private: '私密'
  },

  theme: {
    default: '默认',
    minimal: '简约',
    dark: '深色'
  },

  empty: {
    title: '暂无文档书',
    description: '点击"新建文档书"创建您的第一个文档集合'
  },

  dialog: {
    create_title: '新建文档书',
    edit_title: '编辑文档书',

    form: {
      name: '名称',
      name_placeholder: '请输入文档书名称',
      slug: 'URL标识',
      slug_placeholder: '请输入URL标识，如：my-docs',
      slug_prefix: '/docs/',
      description: '描述',
      description_placeholder: '请输入文档书描述',
      cover: '封面图',
      icon: '图标',
      icon_placeholder: '图标（emoji或图标名）',
      settings: '设置',
      visibility: '可见性',
      visibility_public: '公开',
      visibility_private: '私密',
      show_sidebar: '显示侧边栏',
      allow_comment: '允许评论',
      allow_search: '允许搜索',
      theme: '主题',
      theme_placeholder: '选择主题',
      sort_order: '排序'
    },

    cover_upload: {
      click_to_upload: '点击上传封面',
      upload_tip: '支持 JPG、PNG、WebP 格式，不超过 2MB',
      uploading: '上传中...',
      remove_cover: '移除封面'
    },

    btn_cancel: '取消',
    btn_confirm: '确定'
  },

  confirm_delete: {
    title: '确认删除',
    message: '确定要删除文档书"{name}"吗？删除后将同时删除所有文档，此操作不可恢复。',
    confirm_btn: '确定',
    cancel_btn: '取消'
  },

  validation: {
    name_required: '请输入文档书名称',
    name_too_long: '名称不能超过100个字符',
    slug_required: '请输入URL标识',
    slug_too_long: 'URL标识不能超过100个字符',
    slug_invalid: '只能包含小写字母、数字和连字符'
  },

  message: {
    load_failed: '加载失败',
    create_success: '创建成功',
    update_success: '更新成功',
    delete_success: '删除成功',
    delete_failed: '删除失败',
    upload_success: '封面上传成功',
    upload_failed: '上传失败',
    operation_failed: '操作失败',
    image_format_error: '只能上传 JPG/PNG/WebP 格式的图片!',
    image_size_error: '图片大小不能超过 2MB!'
  }
}
