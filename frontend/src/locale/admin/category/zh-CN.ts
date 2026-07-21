// 分类管理相关语言（中文）
export default {
  title: '分类管理',
  title_info: '创建和管理您的内容分类。',
  btn: {
    add: '添加新分类',
    edit: '编辑分类',
    delete: '删除分类'
  },
  table: {
    head: {
      name: '分类名称',
      slug: '分类Slug',
      description: '分类描述',
      parent: '父分类',
      cover: '分类封面',
      order: '文章排序',
      order_new: '最新优先',
      order_hot: '最热优先',
      order_pubtime: '最早发布',
      weight: '权重',
      sort: '排序',
      actions: '操作'
    },
    no_parent: '无',
    no_cover: '无'
  },
  form: {
    name: '分类名称',
    slug: '分类标识',
    description: '分类描述',
    parent: '父分类'
  },
  action: {
    delete: {
      title: '删除分类',
      confirmbtn: '删除',
      cancelbtn: '取消',
      confirm: '确定删除此分类吗？',
      success: '分类删除成功。',
      error: '删除分类失败。'
    },
    sort: {
      success: '分类文章排序成功。',
      error: '排序分类文章失败。'
    }
  },
  page: {
    create: {
      title: '创建新分类',
      description: '填写以下信息创建新的内容分类',
      success: '分类创建成功！',
      error: '创建分类失败！',
      btn: '创建分类'
    },
    edit: {
      title: '编辑分类',
      description: '编辑现有分类的详细信息。',
      success: '分类修改成功！',
      error: '修改分类失败！',
      btn: '修改分类'
    },
    form: {
      name: '分类名称',
      name_placeholder: '输入分类名称',
      slug: '分类Slug',
      slug_placeholder: '请输入分类slug（只能包含字母、数字、连字符和下划线）',
      slug_helptip:
        'Slug将用于URL中，如：https://example.com/categories/{slug} 只能包含小写字母、数字和短横线。只包含路径，不包含域名。例如：javascript-basics ',
      description: '分类描述',
      description_placeholder: '输入分类描述',
      parent: '父分类',
      parent_placeholder: '请选择父分类',
      parent_default: '无（顶级分类）',
      cover: '分类封面',
      upload: '将文件拖放到此处或 <em>点击上传</em><br />',
      upload_helptip: '推荐尺寸：1200 x 420 px，jpg/png 文件大小小于 2M',
      validate: '请完善分类信息后再提交',
      uploaderror: {
        format: '请上传jpg/png格式的图片',
        size: '图片大小不能超过2MB',
        default: '上传图片失败，请重试'
      },
      uploadsuccess: '图片上传成功！',
      cover_helptip: '为分类添加封面图片。',
      order: '分类文章排序',
      order_helptip: '对分类中的文章进行排序并按以下方式显示'
    },
    validate: {
      name: '请输入分类名称',
      name_length: '分类名称长度必须在 2 到 50 个字符之间',
      slug: '请输入分类Slug',
      slug_format: 'slug只能包含字母、数字、连字符和下划线',
      slug_length: 'slug长度应在2-100个字符之间',
      description: '请输入分类描述',
      article_sort: '请选择文章排序方式'
    },
    load: {
      success: '分类数据加载成功。',
      error: '加载分类数据失败，请稍后重试。'
    }
  }
}
