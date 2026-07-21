// 管理后台多语言入口文件
// 按视图分类的管理后台语言文件将在这里导入和合并

// 导入通用管理后台语言
import general from './general/index'

// 导入按视图分类的语言文件
import analytics from './analytics/index'
import article from './article/index'
import category from './category/index'
import comment from './comment/index'
import dashboard from './dashboard/index'
import navbar from './navbar/index'
import series from './series/index'
import pages from './pages/index'
import tags from './tags/index'
import members from './members/index'
import user from './user/index'
import docbook from './docbook/index'
import doc from './doc/index'
import settings from './settings/index'
import appearance from './appearance/index'

// 导出合并后的语言对象
export default {
  general,
  analytics,
  article,
  category,
  comment,
  dashboard,
  navbar,
  series,
  pages,
  tags,
  members,
  user,
  docbook,
  doc,
  settings,
  appearance
  // 可以添加更多模块
}
