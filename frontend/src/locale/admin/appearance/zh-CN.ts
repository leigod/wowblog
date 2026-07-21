export default {
  title: '外观管理',

  // 标签页
  tabs: {
    general: '通用设置',
    footer: '底部设置'
  },

  // 表单项
  default_language: '默认语言',
  default_language_hint:
    '网站默认语言，用户可在文章页面切换语言，切换后的设置保存在用户本地，用户下次访问时将依照本地保存的设置执行',

  dark_mode: '深色模式',
  dark_mode_system: '跟随系统',
  dark_mode_dark: '深色模式',
  dark_mode_light: '浅色模式',
  dark_mode_hint:
    '网站深色模式全局设置，初次访问网站用户的默认设置，用户可自行切换，切换后的设置保存在用户本地，用户下次访问时将依照本地保存的设置执行深色模式',

  default_homepage_type: '默认首页类型',
  homepage_type_blog: '博客',
  homepage_type_doc: '文档',
  default_homepage_hint:
    '设置网站默认首页类型，选择"博客"时首页显示博客列表，选择"文档"时首页显示指定文档书',

  default_docbook: '默认文档书',
  default_docbook_hint: '当默认首页类型选择为"文档"时，访问首页将显示此文档书的内容',
  no_docbook_hint: '暂无文档书，请先创建文档书',

  doc_subdomain: '文档模块子域名',
  doc_subdomain_placeholder: '例如: docs.example.com',
  doc_subdomain_hint:
    '设置文档模块的子域名，配置后可通过独立子域名访问文档模块。留空则使用主域名路径访问',

  // Footer 设置
  footer: {
    logo: '网站Logo',
    logo_url: 'Logo 链接',
    logo_url_placeholder: '请输入 Logo 图片链接',
    logo_url_hint: '网站底部显示的 Logo 图片链接',

    site_description: '网站描述',
    site_description_placeholder: '请输入网站描述',
    site_description_hint: '网站底部显示的简短描述，用于介绍网站',

    social_media: '社交媒体',
    select_icon: '选择图标',
    url_placeholder: '请输入链接',
    social_media_hint: '添加社交媒体链接，图标将从 Iconify 图标库中选择',
    add_social: '添加社交媒体',
    remove: '删除',

    nav_groups: '导航分组',
    group_name_placeholder: '分组名称',
    nav_groups_hint: '创建导航链接分组，每组可包含多个链接',
    add_nav_group: '添加分组',
    add_link: '添加链接',
    link_name_placeholder: '显示文本',

    copyright: '版权信息',
    copyright_placeholder: '请输入版权信息，例如：© 2024 MySite',
    copyright_hint: '显示在网站底部的版权声明',

    icp_info: 'ICP 备案信息',
    icp_text_placeholder: '例如：京ICP备12345678号',
    icp_info_hint: '添加网站的 ICP 备案信息，可显示多个备案号',
    add_icp: '添加备案信息'
  },

  save_button: '保存设置',

  // 语言选项
  languages: {
    'zh-CN': '简体中文',
    'en-US': 'English'
  },

  // 消息提示
  message: {
    save_success: '设置保存成功！',
    save_failed: '保存失败',
    fetch_docbooks_failed: '获取文档书列表失败',
    load_config_failed: '获取网站配置失败'
  }
}
