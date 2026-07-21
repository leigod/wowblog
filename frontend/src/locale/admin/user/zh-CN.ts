export default {
  title: '用户管理',
  title_info: '管理系统所有注册用户',
  section_title: '用户列表',
  search_placeholder: '搜索用户名或邮箱',
  status_filter: {
    all: '全部',
    normal: '正常',
    disabled: '禁用'
  },
  table: {
    user: '用户',
    email: '邮箱',
    role: '角色',
    status: '状态',
    articles_count: '文章数',
    comments_count: '评论数',
    actions: '操作'
  },
  roles: {
    Admin: '管理员',
    Editor: '编辑',
    Author: '作者',
    Contributor: '贡献者',
    User: '用户'
  },
  actions: {
    view: '查看',
    send_message: '发消息',
    more: '更多',
    edit_role: '修改角色',
    reset_password: '重置密码',
    delete_user: '删除用户',
    view_profile: '查看个人资料页'
  },
  drawer: {
    title: '用户详情',
    view_profile: '查看个人资料页'
  },
  detail_section: {
    basic_info: '基本信息',
    email: '邮箱',
    mobile: '手机',
    gender: '性别',
    register_time: '注册时间',
    status: '状态',
    statistics: '统计信息',
    articles_count: '文章数',
    comments_count: '评论数',
    bio: '个人简介',
    gender_male: '男',
    gender_female: '女',
    gender_unknown: '-'
  },
  message_dialog: {
    title: '发送消息',
    recipient: '收件人',
    message_type: '消息类型',
    type_system: '系统通知',
    type_reminder: '提醒',
    message_title: '标题',
    title_placeholder: '请输入消息标题',
    content: '内容',
    content_placeholder: '请输入消息内容',
    send: '发送',
    cancel: '取消',
    warning: '请填写消息标题和内容'
  },
  role_dialog: {
    title: '修改用户角色',
    user: '用户',
    role: '角色',
    confirm: '确定',
    cancel: '取消'
  },
  reset_password_confirm: {
    title: '重置密码确认',
    message: '确认为用户 {name} 重置密码？重置后的密码将发送到用户邮箱。',
    confirm: '确定',
    cancel: '取消'
  },
  delete_user_confirm: {
    title: '删除用户确认',
    message: '确定删除用户 {name}？此操作不可恢复，用户的所有数据将被删除。',
    confirm: '确定',
    cancel: '取消'
  },
  message: {
    send_success: '消息发送成功',
    send_failed: '消息发送失败',
    status_update_success: '用户 {username} 状态已更新为{status}',
    status_update_failed: '状态更新失败',
    role_update_success: '用户角色修改成功',
    role_update_failed: '角色修改失败',
    password_reset_success: '密码重置成功，新密码已发送到用户邮箱',
    password_reset_failed: '密码重置失败',
    delete_success: '用户删除成功',
    delete_failed: '用户删除失败',
    load_failed: '加载用户列表失败',
    user_not_found: '用户不存在'
  },
  status: {
    normal: '正常',
    disabled: '禁用'
  }
}
