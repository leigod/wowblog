export default {
  title: '系统设置',

  // 标签页
  tabs: {
    basic: '基础设置',
    message: '消息推送',
    email: '邮件配置'
  },

  // 基础设置
  basic: {
    site_title: '网站标题',
    site_title_placeholder: '请输入网站标题',
    site_logo: '网站Logo',
    upload_logo_tip: '支持 PNG、JPG、SVG、ICO 格式，文件大小小于 2MB',
    favicon: '网站收藏图标',
    upload_favicon_tip: '支持 ICO、PNG、SVG 格式，文件大小小于 1MB',
    disable_comments: '禁止评论',
    disable_comments_hint: '全局设置，开启后所有文章将禁用评论，优先级高于文章内设置',
    disable_doc_comments: '禁止文档评论',
    disable_doc_comments_hint: '全局设置，开启后所有文档将禁用评论',
    save: '保存设置'
  },

  // 上传相关
  upload: {
    drop_text: 'Drop file here or <em>click to upload</em>',
    uploading: '上传中',
    remove_image: '移除图片'
  },

  // 消息推送
  message: {
    push_method: '消息推送方式',
    method_websocket: '实时推送（WebSocket）',
    method_websocket_desc: '即时接收新消息通知，需要浏览器支持 WebSocket',
    method_polling: '定时轮询',
    method_polling_desc: '定期检查新消息，兼容性更好但有一定延迟',

    polling_interval: '轮询间隔',
    polling_interval_unit: '秒',
    polling_interval_hint: '设置越小，消息越实时，但会消耗更多服务器资源',

    save_message: '保存消息推送设置',
    test_connection: '测试连接',
    send_test_message: '发送测试消息',

    connection_status: '连接状态',
    connected: '已连接',
    disconnected: '未连接',
    connection_hint: 'WebSocket 连接状态，实时消息推送需要保持连接',
    ws_url_label: 'WebSocket URL:'
  },

  // 邮件配置
  email: {
    section_title: 'SMTP 邮件配置',
    section_desc: '配置邮件服务器后，系统可以发送邀请通知、注册验证等邮件。点击下方的邮件服务商进行配置。',

    table: {
      provider: '服务商',
      smtp_host: 'SMTP 服务器',
      port: '端口',
      from_email: '发件邮箱',
      from_name: '发件名称',
      status: '状态',
      config_status: '配置状态',
      actions: '操作',
      enabled: '启用',
      disabled: '禁用',
      configured: '已配置',
      not_configured: '未配置',
      edit: '编辑',
      configure: '配置'
    },

    empty: '暂无邮件配置',

    dialog: {
      add_title: '添加邮件配置',
      edit_title: '编辑邮件配置',
      provider: '服务商',
      smtp_host: 'SMTP 服务器',
      smtp_host_placeholder: 'smtp.example.com',
      port: '端口',
      smtp_user: 'SMTP 用户名',
      smtp_user_placeholder: '请输入邮箱地址',
      smtp_user_edit_hint: '编辑时需要重新输入用户名',
      smtp_pass: 'SMTP 密码',
      smtp_pass_placeholder: '应用专用密码',
      smtp_pass_edit_placeholder: '留空则保持原密码不变',
      smtp_pass_hint: '如果不修改密码，请将此字段留空',
      from_email: '发件邮箱',
      from_email_placeholder: '请输入发件邮箱地址',
      from_name: '发件名称',
      from_name_placeholder: 'Blog Notification',
      use_tls: '使用 TLS',
      is_active: '启用',
      btn_cancel: '取消',
      btn_confirm: '确定'
    }
  },

  // 邮件服务商
  providers: {
    gmail: 'Gmail',
    outlook: 'Outlook',
    qq: 'QQ 邮箱',
    '163': '163 邮箱',
    custom: '自定义'
  },

  // 消息提示
  message_tip: {
    save_success: '设置保存成功！',
    save_failed: '保存失败',
    message_save_success: '消息推送设置保存成功！',
    message_save_hint: '请点击"测试连接"按钮验证 WebSocket 连接',
    message_save_failed: '保存失败，请检查网络连接',
    ws_connect_success: 'WebSocket 连接成功',
    ws_connect_failed: 'WebSocket 连接失败',
    ws_connect_timeout: 'WebSocket 连接超时，请检查后端服务是否在 localhost:8000 运行',
    ws_test_failed: 'WebSocket 连接测试失败',
    test_message_sent: '测试消息已发送，请查看控制台',
    test_message_failed: '发送测试消息失败',
    token_not_found: '未找到认证 token，请先登录',
    logo_upload_success: '网站Logo上传成功',
    favicon_upload_success: '网站收藏图标上传成功',
    upload_failed: '上传失败',
    logo_format_error: '只能上传 PNG、JPG、SVG、ICO 格式的文件',
    logo_size_error: '文件大小不能超过2MB',
    favicon_format_error: 'Favicon 只能上传 ICO、PNG、SVG 格式的文件',
    favicon_size_error: 'Favicon 文件大小不能超过1MB',
    email_load_failed: '加载邮件配置失败',
    email_update_success: '邮件配置已更新',
    email_update_failed: '更新失败',
    invalid_operation: '无效的操作',
    operation_failed: '操作失败，请检查网络连接'
  }
}
