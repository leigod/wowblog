export default {
  title: '系列',
  title_info: '创建和管理您的系列',
  btn: {
    add: '创建新系列',
    view: '查看系列'
  },
  action: {
    update: {
      sort: {
        success: '系列排序更新成功',
        error: '更新系列排序失败'
      }
    },
    delete: {
      confirm: '确定删除此系列吗？',
      success: '系列删除成功',
      error: '删除系列失败'
    },
    empty: {
      title: '暂无系列',
      description: '创建您的第一个系列来组织您的文章'
    }
  },
  page: {
    create: {
      title: '创建新系列',
      description: '为您的博客创建一个新系列。',
      success: '系列创建成功！',
      error: '创建系列失败！',
      btn: '创建系列'
    },
    edit: {
      title: '编辑系列',
      description: '编辑现有系列的详细信息。',
      success: '系列更新成功！',
      error: '更新系列失败！',
      btn: '更新系列'
    },
    form: {
      name: '系列名称',
      name_placeholder: '输入系列名称',
      slug: '系列路径',
      slug_placeholder: 'series-path',
      slug_helptip:
        '例如：javascript-basics。仅允许小写字母、数字、"-"和"_"。仅包含路径，不包含域名。',
      description: '系列描述',
      description_placeholder: '输入系列描述',
      cover: '系列封面',
      upload: '将文件拖放到此处或 <em>点击上传</em><br />',
      upload_helptip: '推荐尺寸：800 x 800 px，jpg/png 文件大小小于 2M',
      validate: '请在提交前完成系列信息。',
      uploaderror: {
        format: '请上传 jpg/png 格式的图片。',
        size: '图片大小不能超过 2MB。',
        default: '上传图片失败，请重试。'
      },
      uploadsuccess: '图片上传成功！',
      cover_helptip: '为您的系列添加封面图片。',
      order: '系列文章排序',
      order_helptip: '在系列中排序您的文章并按',
      order_oldest: '最早的优先',
      order_newest: '最新的优先'
    },
    validate: {
      name: '请输入系列名称。',
      name_length: '系列名称长度必须在 2 到 50 个字符之间。',
      slug: '请输入系列路径。',
      slug_format: '路径只能包含字母、数字、短横线和下划线。',
      slug_length: '路径长度必须在 2 到 100 个字符之间。',
      description: '请输入系列描述。',
      article_sort: '请选择文章排序顺序。'
    },
    load: {
      success: '系列数据加载成功。',
      error: '加载系列数据失败，请稍后重试。'
    }
  }
}
