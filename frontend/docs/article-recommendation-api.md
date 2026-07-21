# 文章推荐功能设计文档

## 功能概述

为文章详情页提供智能推荐功能，帮助用户发现更多相关内容。

## API设计

### 接口地址

```
GET /blog/articles/{article_id}/recommend
```

### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| article_id | number | 是 | 当前文章ID（路径参数） |
| limit | number | 否 | 返回数量，默认3，最大10 |

### 响应格式

```json
{
  "code": 1,
  "msg": "ok",
  "data": [
    {
      "id": 1,
      "title": "文章标题",
      "slug": "article-slug",
      "cover": "封面图URL",
      "summary": "文章摘要（100字内）",
      "author_name": "作者名",
      "author_avatar": "作者头像URL",
      "author_username": "username",
      "pub_time": 1716000000,
      "views": 1234,
      "tags": ["标签1", "标签2"],
      "reason": "相关标签：Vue、TypeScript",
      "score": 85.5
    }
  ]
}
```

## 推荐算法

### 标签权重计算（IDF算法）

```
标签权重 = log(文章总数 / 使用该标签的文章数)
```

- 热门标签（使用次数多）→ 权重低
- 冷门标签（使用次数少）→ 权重高

### 推荐流程

```
步骤1：构建候选池
├─ 时间范围：最近30日内
├─ 状态：已发布
└─ 排除：当前文章

步骤2：统计标签频率
└─ 计算每个标签的IDF值

步骤3：计算每篇文章得分
├─ 标签相关性得分：Σ(标签IDF × 20)
├─ 同作者加成：+10分
├─ 时效性加成：7日内 +5分
└─ 点击量归一化：(点击量 / 最大点击量) × 10

步骤4：确定推荐理由
├─ 优先级1：同作者 + 7日内 → "同作者最新文章"
├─ 优先级2：同作者 → "更多来自该作者"
├─ 优先级3：标签重合 ≥ 2 → "相关标签：xxx、yyy"
└─ 默认：→ "热门推荐"

步骤5：按得分降序，取前N篇
```

## 前端展示

### ArticleView.vue 组件

```vue
<template>
  <div class="wy-article-more">
    <div class="wy-article-more-title">
      MORE ARTICLES
      <el-button link @click="refreshRecommend">
        <el-icon><Refresh /></el-icon>
        换一批
      </el-button>
    </div>
    <el-row :gutter="30">
      <el-col v-for="item in recommendArticles" :key="item.id">
        <el-card>
          <!-- 推荐理由标签 -->
          <div class="recommend-reason">{{ item.reason }}</div>
          <!-- 文章卡片内容 -->
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
```

### 功能特性

1. **推荐理由显示**：卡片左上角显示推荐理由标签
2. **换一批功能**：点击刷新获取新的推荐结果
3. **响应式布局**：适配不同屏幕尺寸

## 性能优化

1. **缓存策略**：
   - 标签IDF值缓存1小时
   - 推荐结果缓存5分钟

2. **查询优化**：
   - 一次性查询获取文章及标签（避免N+1）
   - 使用索引优化查询性能

## 更新日志

- 2026-05-23：初始设计文档
