export default {
  title: '成员和角色',
  title_info: '管理您博客的成员并定义他们的角色。',
  btn: {
    role_definition: '角色定义',
    invite_member: '邀请成员',
    add_member: '添加成员',
    update: '更新成员',
    add: '添加成员'
  },
  section: {
    manage_members: '管理成员'
  },
  tabs: {
    team_members: '团队成员 ({count})',
    pending_invites: '待处理邀请 ({count})'
  },
  table: {
    name: '姓名',
    role: '角色',
    visibility: '可见性',
    status: '状态',
    actions: '操作',
    email: '邮箱',
    invited_by: '邀请人',
    expires_at: '过期时间',
    created_at: '邀请时间'
  },
  visibility: {
    public: '公开',
    private: '私密'
  },
  status: {
    normal: '正常',
    block: '禁用',
    pending: '待处理',
    accepted: '已接受',
    cancelled: '已取消',
    expired: '已过期'
  },
  gender: {
    male: '男',
    female: '女'
  },
  drawer: {
    member_details: '成员详情',
    role_definition: '角色定义',
    create_title: '添加新成员',
    edit_title: '编辑成员',
    invite_title: '邀请新成员'
  },
  form: {
    username: '用户名',
    username_placeholder: '输入用户名',
    full_name: '全名',
    full_name_placeholder: '输入全名',
    profile_image: '头像',
    gender: '性别',
    email: '邮箱',
    email_placeholder: '输入邮箱',
    mobile: '手机',
    mobile_placeholder: '输入手机号码',
    role: '角色',
    role_placeholder: '选择角色',
    select_role: '选择角色',
    placeholder_email: '输入邮箱',
    placeholder_mobile: '输入手机号',
    language: '邮件语言',
    language_placeholder: '选择邮件语言'
  },
  detail_section: {
    role: '角色',
    visibility: '可见性',
    permissions: '权限'
  },
  message: {
    get_members_error: '获取成员列表失败',
    delete_confirm: '确定要删除这个成员吗？',
    delete_success: '成员删除成功',
    delete_error: '删除成员失败',
    update_success: '成员更新成功',
    add_success: '成员添加成功',
    add_error: '添加成员失败',
    validation_error: '用户名和全名是必填项',
    update_visibility_success: '更新成员可见性成功：{name}',
    update_visibility_error: '更新成员可见性失败：{name}',
    update_status_success: '更新成员状态成功：{name}',
    update_status_error: '更新成员状态失败：{name}',
    submit_failed: '提交失败',
    update_failed: '更新失败',
    invite_success: '邀请已创建并发送邮件',
    invite_error: '邀请创建失败',
    invite_duplicate: '该用户已被邀请此角色，请勿重复邀请',
    resend_success: '邮件已重新发送',
    resend_error: '邮件发送失败',
    cancel_success: '邀请已取消',
    cancel_error: '取消邀请失败',
    cancel_invite_confirm: '确定要取消这个邀请吗？',
    get_invitations_error: '获取邀请列表失败',
    owner_delete_error: '无法删除系统所有者'
  },
  validations: {
    username_required: '用户名不能为空',
    username_length: '用户名长度应为3-20个字符',
    full_name_required: '全名不能为空',
    full_name_length: '全名长度应为3-20个字符',
    email_required: '邮箱不能为空',
    invalid_email: '无效的邮箱格式',
    mobile_length: '手机号必须为11位',
    invalid_mobile: '无效的手机号格式',
    username_and_full_name_required: '用户名和全名不能为空',
    email_duplicate: '该用户已被邀请相同角色'
  },
  roles: {
    administrator: '管理员',
    admin: {
      name: '管理员',
      description: '拥有所有权限的超级用户',
      permissions1: '创建出版物',
      permissions2: '完全控制出版物',
      permissions3: '删除出版物',
      permissions4: '管理出版物'
    },
    editor: {
      name: '编辑',
      description: '可以管理和发布所有文章',
      permissions1: '发布和管理文章',
      permissions2: '管理分类和标签',
      permissions3: '管理评论',
      permissions4: '管理媒体文件'
    },
    author: {
      name: '作者',
      description: '可以独立创建、发布和管理自己的文章',
      permissions1: '创建和发布文章',
      permissions2: '编辑自己的文章',
      permissions3: '管理媒体文件',
      permissions4: '只能管理自己的内容'
    },
    contributor: {
      name: '贡献者',
      description: '可以创建草稿文章（需审核后发布）',
      permissions1: '创建草稿文章',
      permissions2: '编辑自己的草稿',
      permissions3: '需审核后发布',
      permissions4: '适合外部作者投稿'
    },
    subscriber: {
      name: '订阅者',
      description: '只能管理自己的个人资料',
      permissions: 'profile:*'
    },
    admin_permissions: '管理系统设置、发布文章、管理成员和评论',
    editor_permissions: '发布和管理文章、管理分类标签',
    author_permissions: '创建和发布自己的文章',
    contributor_permissions: '创建草稿文章（需审核）'
  },
  search: {
    placeholder: '搜索团队成员'
  },
  invite: {
    title: '邀请成员',
    description: '邀请新成员加入您的团队',
    email_label: '邮箱地址',
    email_placeholder: '输入被邀请者的邮箱',
    role_label: '选择角色',
    role_placeholder: '选择要分配的角色',
    language_label: '邮件语言',
    language_placeholder: '选择邮件发送语言',
    submit: '发送邀请',
    cancel: '取消',
    resend: '重新发送',
    success: '邀请已成功发送！',
    error: '发送邀请失败，请重试',
    status: {
      pending: '待处理',
      accepted: '已接受',
      cancelled: '已取消',
      expired: '已过期'
    },
    created_at: '邀请时间',
    expires_at: '过期时间'
  }
}
