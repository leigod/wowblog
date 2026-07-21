export default {
  title: '页面管理',
  title_info: '创建和管理您的页面',
  btn: {
    add: '创建新页面'
  },
  table: {
    name: '页面名称',
    slug: '页面Slug',
    description: '页面描述',
    actions: '操作',
    visible: '已显示',
    hidden: '已隐藏'
  },
  action: {
    update: {
      sort: {
        success: '页面排序更新成功',
        error: '更新页面排序失败'
      }
    },
    delete: {
      confirm: '确定删除此页面吗？',
      success: '页面删除成功',
      error: '删除页面失败'
    },
    empty: {
      title: '暂无数据',
      description: '创建您的第一个页面来组织您的文章'
    },
    show: '显示页面',
    hide: '隐藏页面',
    toggle: {
      success: '{action}页面"{pagename}"成功！',
      error: '{action}页面"{pagename}"失败！'
    }
  },
  page: {
    create: {
      title: '创建新页面',
      description: '为您的博客创建一个新页面。',
      success: '页面创建成功！',
      error: '创建页面失败！',
      btn: '创建页面'
    },
    edit: {
      title: '编辑页面',
      description: '编辑现有页面的详细信息。',
      success: '页面更新成功！',
      error: '更新页面失败！',
      btn: '更新页面'
    },
    form: {
      title: '页面名称',
      title_placeholder: '输入页面名称',
      slug: '页面Slug',
      slug_placeholder: 'page-path',
      slug_helptip:
        '例如：javascript-basics。仅允许小写字母、数字、"-"和"_"。仅包含路径，不包含域名。',
      content: '页面内容',
      content_placeholder: '点击打开编辑器并通过 WYSIWYG 添加内容。',
      content_edit: '点击编辑页面内容',
      cover: '页面封面',
      cover_info: '用于社交媒体分享的图片。',
      cover_helptip: '这张图片将在社交媒体上显示，例如 Twitter、Facebook 等。',
      upload: '将文件拖放到此处或 <em>点击上传</em><br />',
      upload_helptip: '推荐尺寸：1200 x 420 px，jpg/png 文件大小小于 2M',
      validate: '请在提交前完成页面信息填写。',
      uploaderror: {
        format: '请上传 jpg/png 格式的图片。',
        size: '图片大小不能超过 2MB。',
        default: '上传图片失败，请重试。'
      },
      uploadsuccess: '图片上传成功！',
      seodesc: 'SEO 描述',
      seodesc_placeholder: '输入页面的 SEO 描述。',
      seodesc_helptip:
        '最佳描述长度在 160 个字符以内。搜索引擎将在搜索结果中显示此描述。如果未提供，将使用页面内容。'
    },
    validate: {
      title: '请输入页面名称。',
      title_length: '页面名称长度必须在 2 到 100 个字符之间。',
      slug: '请输入页面路径。',
      slug_format: '路径只能包含字母、数字、短横线和下划线。',
      slug_length: '路径长度必须在 2 到 100 个字符之间。',
      content: '请输入页面内容。',
      seodesc_length: 'SEO 描述长度必须在 500 个字符以内，建议160个字符最佳'
    }
  }
}
