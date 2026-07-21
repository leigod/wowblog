# API 请求封装说明

本项目提供了完整的API请求封装解决方案，基于axios实现，包含请求拦截、响应处理、错误统一管理等功能。

## 目录结构

```
src/api/
├── index.ts            # API模块主入口
├── http.ts             # HTTP请求核心配置
├── types.ts            # 通用类型定义
└── services/           # API服务集合
    ├── common.ts       # 通用API服务
    └── user.ts         # 用户相关API服务
```

## 核心功能

1. **请求拦截**：自动添加token、设置全局loading状态
2. **响应拦截**：统一处理响应数据、错误处理
3. **错误处理**：自动弹出错误提示、401重定向等
4. **类型支持**：完整的TypeScript类型定义
5. **模块化设计**：按业务模块组织API服务

## 使用方法

### 基础请求

```typescript
import { request } from '@/api';

// 发起GET请求
const fetchData = async () => {
  try {
    const data = await request({
      url: '/api/data',
      method: 'GET',
      params: {
        id: 1
      }
    });
    console.log(data);
  } catch (error) {
    console.error('请求失败:', error);
  }
};

// 发起POST请求
const submitData = async (formData: any) => {
  try {
    const data = await request({
      url: '/api/submit',
      method: 'POST',
      data: formData
    });
    console.log(data);
  } catch (error) {
    console.error('提交失败:', error);
  }
};
```

### 使用封装的API服务

```typescript
import { getUserInfo, updateUserInfo } from '@/api/services/user';

// 获取用户信息
const loadUserInfo = async () => {
  try {
    const userInfo = await getUserInfo();
    console.log(userInfo);
  } catch (error) {
    console.error('加载用户信息失败:', error);
  }
};

// 更新用户信息
const updateProfile = async (profileData: any) => {
  try {
    const result = await updateUserInfo(profileData);
    console.log(result);
  } catch (error) {
    console.error('更新用户信息失败:', error);
  }
};
```

### 文件上传

```typescript
import { updateUserAvatar } from '@/api/services/user';

// 上传用户头像
const handleAvatarUpload = async (file: File) => {
  try {
    const result = await updateUserAvatar(file);
    console.log(result);
  } catch (error) {
    console.error('上传头像失败:', error);
  }
};
```

## 全局加载状态

系统已集成全局加载状态，在App.vue中使用element-plus的ElLoading组件实现，当发起API请求时会自动显示加载动画。

## 错误处理机制

1. **业务错误**：当后端返回非200状态码时，会自动弹出错误消息
2. **401错误**：自动清除token并跳转到登录页
3. **403错误**：提示无权限访问
4. **404错误**：提示请求的资源不存在
5. **500错误**：提示服务器内部错误
6. **网络错误**：提示网络连接问题

## 扩展API服务

要添加新的API服务，只需在`src/api/services/`目录下创建新的服务文件，然后在`src/api/index.ts`中导出即可。

例如，创建文章相关的API服务：

1. 创建`src/api/services/article.ts`文件
2. 在`src/api/index.ts`中添加导出：`export * from './services/article';`

## 环境变量配置

API基础URL可通过环境变量配置：

```env
VITE_API_BASE_URL=https://api.example.com
```

如果未配置，则默认为`/api`。