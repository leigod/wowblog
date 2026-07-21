// 仪表盘相关语言（中文）
export default {
  title: '导航管理',
  title_info: '添加导航菜单和页面链接',
  btn: {
    add: '添加导航项'
  },
  table: {
    sort: '排序',
    label: '名称',
    type: '类型',
    value: '值',
    actions: '操作'
  },
  form: {
    add_title: '添加导航项',
    edit_title: '编辑导航项',
    label: '名称',
    label_placeholder: '输入导航项名称',
    type: '类型',
    type_placeholder: '选择链接类型',
    type_link: '链接',
    type_page: '页面',
    type_series: '系列',
    type_doc: '文档',
    value: '值',
    value_placeholder: '输入URL，以http://或https://开头',
    page: '页面',
    page_placeholder: '选择一个页面',
    series: '系列',
    series_placeholder: '选择一个系列',
    doc: '文档',
    doc_placeholder: '选择一个文档'
  },
  validation: {
    general: '请输入值',
    label: '请输入导航项名称',
    label_length: '名称不能超过50个字符',
    type: '请选择链接类型',
    value: '请输入值',
    link: '请输入一个有效的URL，以http://或https://开头'
  },
  action: {
    load: {
      page: '加载页面...',
      series: '加载系列...'
    },
    update: {
      sort: {
        success: '更新排序成功',
        error: '更新排序失败'
      },
      navbar: {
        success: '成功更新导航项',
        error: '更新导航项失败'
      }
    },
    delete: {
      navbar: {
        success: '成功删除导航项',
        error: '删除导航项失败'
      }
    },
    create: {
      navbar: {
        success: '成功创建导航项',
        error: '创建导航项失败'
      }
    }
  },
  empty: {
    title: '暂无导航项',
    description: '添加您的第一个导航项以开始'
  }
}
