/**
 * API模块主入口
 * 导出所有API服务和工具函数
 */

// 导入HTTP请求核心配置
import { request } from './http'

// 导入API服务
export * from './services/user'
export * from './services/doc'
export * from './services/notifications'

// 导出请求函数
export { request }
