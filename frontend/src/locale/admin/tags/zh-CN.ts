export default {
  title: '标签管理',
  title_info: '创建和管理内容标签',
  btn: {
    add: '创建标签'
  },
  table: {
    name: '标签名称',
    slug: '标签Slug',
    description: '标签描述',
    cover: '封面',
    visibility: '显示状态',
    actions: '操作',
    no_cover: '无'
  },
  action: {
    update: {
      sort: {
        success: '页面排序更新成功',
        error: '更新标签排序失败'
      }
    },
    delete: {
      confirm: '确定删除标签"{tagname}"吗？',
      title: '删除确认',
      btn: {
        confirm: '删除',
        cancel: '取消'
      },
      success: '标签"{tagname}"删除成功',
      error: '删除标签"{tagname}"失败'
    },
    empty: {
      title: '暂无数据',
      description: '创建您的第一个标签来组织您的文章'
    },
    search: {
      placeholder: '请输入标签名称关键字'
    },
    show: '显示标签',
    hide: '隐藏标签',
    toggle: {
      success: '{action}"{tagname}"成功！',
      error: '{action}"{tagname}"失败！'
    }
  },
  drawer: {
    create: {
      title: '创建标签',
      description: '为您的博客创建一个新标签。',
      success: '标签创建成功！',
      error: '创建标签失败！',
      btn: '创建标签'
    },
    edit: {
      title: '编辑标签',
      description: '编辑现有标签的详细信息。',
      success: '标签更新成功！',
      error: '更新标签失败！',
      btn: '更新标签'
    },
    form: {
      name: '标签名称',
      name_placeholder: '输入标签名称',
      slug: '标签Slug',
      slug_placeholder: 'tag-path',
      slug_helptip:
        '例如：javascript-basics。仅允许小写字母、数字、"-"和"_"。仅包含路径，不包含域名。',
      type: '标签类型',
      type_placeholder: '请选择标签类型',
      type_sys: '系统标签',
      type_user: '用户标签',
      description: '标签描述',
      description_placeholder: '输入标签描述',
      status: '显示状态',
      status_visible: '显示',
      status_hidden: '隐藏',
      cover: '标签图片',
      cover_info: '上传一张图片用于显示在标签详情页或标签列表页。',
      upload: '将文件拖放到此处或 <em>点击上传</em><br />',
      upload_helptip: '推荐尺寸：640 x 640 px，jpg/png 文件大小小于 2M',
      validate: '请在提交前完成必填信息填写。',
      uploaderror: {
        format: '请上传 jpg/png 格式的图片。',
        size: '图片大小不能超过 2MB。',
        default: '上传图片失败，请重试。'
      },
      uploadsuccess: '图片上传成功！'
    },
    validate: {
      name: '请输入标签名称。',
      name_length: '标签名称长度必须在 2 到 30 个字符之间。',
      slug: '请输入标签Slug。',
      slug_format: 'Slug 只能包含字母、数字、短横线和下划线。',
      slug_length: 'Slug 长度必须在 2 到 30 个字符之间。',
      type: '请选择标签类型。'
    }
  }
}
