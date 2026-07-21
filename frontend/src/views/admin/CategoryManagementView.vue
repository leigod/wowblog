<template>
  <div class="category-management-container">
    <div class="page-header">
      <div>
        <h1>{{ t('admin.category.title') }}</h1>
        <p>{{ t('admin.category.title_info') }}</p>
      </div>
      <el-button
        type="primary"
        size="default"
        class="create-category-btn"
        @click="navigateToCreateCategory"
      >
        <el-icon><Plus /></el-icon> {{ t('admin.category.btn.add') }}
      </el-button>
    </div>

    <div class="table-container">
      <!-- 移动端卡片布局 -->
      <template v-if="isMobile">
        <div v-loading="loading" class="mobile-categories-container">
          <template v-for="category in categoryList" :key="category.id">
            <el-card class="mobile-category-card">
              <div class="category-card-header">
                <div class="category-title">
                  <el-image
                    v-if="category.coverImage"
                    :src="category.coverImage"
                    alt="封面"
                    class="category-cover"
                    :preview-src-list="[category.coverImage]"
                    preview-teleported
                  />
                  <div v-else class="category-cover-placeholder">
                    <el-icon><Folder /></el-icon>
                  </div>
                  <div class="category-info">
                    <h3>{{ category.name }}</h3>
                    <p v-if="category.description">{{ category.description }}</p>
                  </div>
                </div>
              </div>

              <div class="category-card-body">
                <div class="info-row">
                  <span class="label">{{ t('admin.category.table.head.slug') }}:</span>
                  <span class="value">/{{ category.slug }}</span>
                </div>
                <div class="info-row">
                  <span class="label">{{ t('admin.category.table.head.parent') }}:</span>
                  <span class="value">{{ category.parentName || t('admin.category.table.no_parent') }}</span>
                </div>
                <div class="info-row">
                  <span class="label">{{ t('admin.category.table.head.order') }}:</span>
                  <el-select v-model="category.articleSort" size="small" @change="handleSortChange(category)">
                    <el-option :label="t('admin.category.table.head.order_new')" value="newest"></el-option>
                    <el-option :label="t('admin.category.table.head.order_hot')" value="hottest"></el-option>
                    <el-option :label="t('admin.category.table.head.order_pubtime')" value="oldest"></el-option>
                  </el-select>
                </div>
                <div class="info-row">
                  <span class="label">{{ t('admin.category.table.head.weight') }}:</span>
                  <span class="value">{{ category.sort }}</span>
                </div>
              </div>

              <template #footer>
                <div class="category-card-actions">
                  <el-button @click="handleEdit(category)" size="small">
                    <el-icon><Edit /></el-icon>
                  </el-button>
                  <el-button @click="handleDelete(category)" type="danger" size="small">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </template>
            </el-card>

            <!-- 递归渲染子分类 -->
            <template v-if="category.children && category.children.length > 0">
              <div class="children-container">
                <CategoryMobileTree
                  v-for="child in category.children"
                  :key="child.id"
                  :category="child"
                  :depth="1"
                  @edit="handleEdit"
                  @delete="handleDelete"
                  @sort-change="handleSortChange"
                />
              </div>
            </template>
          </template>
        </div>
      </template>

      <!-- 桌面端表格布局 -->
      <el-table
        v-else
        v-loading="loading"
        :data="categoryList"
        :row-key="(row) => row.id"
        :header-cell-style="{
          backgroundColor: '#fafafa',
          fontWeight: 800,
          fontSize: '1rem',
          padding: '12px 14px',
          textAlign: 'center'
        }"
        ref="categoryTableRef"
        default-expand-all
        class="wy-table"
      >
        <!-- <el-table-column type="index" label="序号" width="80"></el-table-column> -->
        <el-table-column
          prop="name"
          :label="t('admin.category.table.head.name')"
          width="200"
        ></el-table-column>
        <el-table-column :label="t('admin.category.table.head.parent')" width="200" align="center">
          <template #default="{ row }">{{
            row.parentName || t('admin.category.table.no_parent')
          }}</template>
        </el-table-column>
        <el-table-column
          prop="description"
          :label="t('admin.category.table.head.description')"
          show-overflow-tooltip
          align="center"
        ></el-table-column>
        <el-table-column
          prop="slug"
          :label="t('admin.category.table.head.slug')"
          width="180"
          show-overflow-tooltip
          align="center"
        ></el-table-column>
        <el-table-column :label="t('admin.category.table.head.cover')" width="120" align="center">
          <template #default="{ row }">
            <el-image
              v-if="row.coverImage"
              :src="row.coverImage"
              alt="封面"
              style="width: 40px; height: 40px; object-fit: cover"
              :preview-src-list="[row.coverImage]"
              preview-teleported
            />
            <span v-else class="no-image">{{ t('admin.category.table.no_cover') }}</span>
          </template>
        </el-table-column>
        <el-table-column
          prop="articleSort"
          :label="t('admin.category.table.head.order')"
          width="120"
          align="center"
        >
          <template #default="{ row }">
            <el-select v-model="row.articleSort" size="small" @change="handleSortChange(row)">
              <el-option
                :label="t('admin.category.table.head.order_new')"
                value="newest"
              ></el-option>
              <el-option
                :label="t('admin.category.table.head.order_hot')"
                value="hottest"
              ></el-option>
              <el-option
                :label="t('admin.category.table.head.order_pubtime')"
                value="oldest"
              ></el-option>
            </el-select>
          </template>
        </el-table-column>
        <el-table-column
          prop="sort"
          :label="t('admin.category.table.head.weight')"
          width="100"
          align="center"
        ></el-table-column>
        <el-table-column :label="t('admin.category.table.head.sort')" width="100" align="center">
          <template #default>
            <div class="allow-drag" style="cursor: move">
              <IconifyIcon icon="material-symbols:drag-indicator" />
            </div>
          </template>
        </el-table-column>
        <el-table-column
          :label="t('admin.category.table.head.actions')"
          width="200"
          fixed="right"
          align="center"
        >
          <template #default="{ row }">
            <div class="operation-buttons">
              <el-button circle type="default" @click="handleEdit(row)">
                <el-icon><Edit /></el-icon
              ></el-button>
              <el-button type="default" circle class="text-danger" @click="handleDelete(row)"
                ><el-icon><Delete /></el-icon
              ></el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Plus, Delete, Edit, Menu, More, Folder } from '@element-plus/icons-vue'
import { useMobileDetection } from '@/composables/useMobileDetection'
import {
  ElTable,
  ElTableColumn,
  ElButton,
  ElImage,
  ElSelect,
  ElOption,
  ElLoading,
  ElMessage,
  ElMessageBox
} from 'element-plus'
import Sortable from 'sortablejs'
import type { Table } from 'element-plus'
import {
  updateCategorySort,
  getManageCategoryList,
  deleteCategory,
  updateCategoryArticleSort
} from '@/api/services/categories'
import IconifyIcon from '@/components/IconIfy.vue'
import CategoryMobileTree from '@/components/CategoryMobileTree.vue'

// 定义表格行数据类型
interface TableRowData {
  id: number
  [key: number]: any
}

// 分类数据接口
export interface Category {
  id: number
  name: string
  parentId: number | null
  parentName?: string
  description: string
  slug: string
  coverImage: string | null
  articleSort: 'newest' | 'hottest' | 'oldest'
  sort: number
  children?: Category[]
}

// 引入i18n
const { t } = useI18n()

// 移动端检测
const { isMobile } = useMobileDetection()

// 状态定义
const categoryList = ref<Category[]>([])
const loading = ref(true)
const categoryTableRef = ref<InstanceType<typeof ElTable>>()
const router = useRouter()

// 生命周期钩子
onMounted(async () => {
  // 加载分类列表数据
  await loadCategoryList()

  // 初始化拖拽排序
  nextTick(() => {
    initDragAndDrop()
  })
})

const loadCategoryList = async () => {
  loading.value = true
  try {
    const res = await getManageCategoryList()
    if (res.code === 1) {
      // 服务端返回的扁平数据转换为树形结构
      const categoriesData = res.data

      // 创建分类映射表用于快速查找
      const categoryMap = new Map<number, Category>()

      // 初始化顶级分类数组
      const rootCategories: Category[] = []

      // 第一步：将所有分类转换为目标格式并添加到映射表
      categoriesData.forEach((item: any) => {
        // 将服务端字段映射到客户端格式
        const category: Category = {
          id: item.id,
          name: item.name,
          parentId: item.pid,
          description: item.cat_desc || '',
          slug: item.slug,
          coverImage: item.image || null,
          articleSort: convertArticlesOrderToSortType(item.articles_order),
          sort: item.sort || 0,
          children: []
        }

        categoryMap.set(category.id, category)

        // 识别顶级分类
        if (item.pid === 0 || item.pid === null || item.pid === '0') {
          rootCategories.push(category)
        }
      })

      // 第二步：构建树形结构，为每个分类添加子分类
      categoriesData.forEach((item: any) => {
        // 跳过顶级分类
        if (item.pid === 0 || item.pid === null || item.pid === '0') {
          return
        }

        const childCategory = categoryMap.get(item.id)
        const parentCategory = categoryMap.get(item.pid)

        if (childCategory && parentCategory) {
          // 添加父分类名称
          childCategory.parentName = parentCategory.name
          // 将子分类添加到父分类的children数组中
          parentCategory.children?.push(childCategory)
        }
      })

      // 第三步：根据sort字段排序分类
      sortCategoriesBySortField(rootCategories)

      // 更新分类列表数据
      categoryList.value = rootCategories
    }
  } catch (error) {
    console.error('加载分类列表失败:', error)
  } finally {
    loading.value = false
  }
}

/**
 * 将服务端的articles_order转换为客户端的articleSort枚举值
 */
const convertArticlesOrderToSortType = (articlesOrder: string): 'newest' | 'hottest' | 'oldest' => {
  if (articlesOrder.includes('desc')) {
    if (articlesOrder.includes('id')) {
      return 'newest'
    }
    if (articlesOrder.includes('views')) {
      return 'hottest'
    }
  } else if (articlesOrder.includes('asc')) {
    if (articlesOrder.includes('pubtime') || articlesOrder.includes('id')) {
      return 'oldest'
    }
  }
  // 默认返回newest
  return 'newest'
}

/**
 * 根据sort字段对分类进行排序
 */
const sortCategoriesBySortField = (categories: Category[]): void => {
  if (!categories || categories.length === 0) {
    return
  }

  // 对当前级别的分类按sort字段降序排序
  categories.sort((a, b) => {
    // 确保sort字段存在且为数字
    const sortA = typeof a.sort === 'number' ? a.sort : 0
    const sortB = typeof b.sort === 'number' ? b.sort : 0

    // 服务端按sort值倒序排序，所以我们也使用降序排序
    return sortB - sortA
  })

  // 递归对每个分类的子分类进行排序
  categories.forEach((category) => {
    if (category.children && Array.isArray(category.children) && category.children.length > 0) {
      sortCategoriesBySortField(category.children)
    }
  })
}

/**
 * 根据分类ID获取该分类及其所有后代分类的ID列表
 */
const getAllDescendantCategoryIds = (categories: Category[], parentId: number): number[] => {
  let ids: number[] = []

  // 先添加父分类ID
  ids.push(parentId)

  // 递归查找所有子分类和孙分类
  const findDescendants = (cats: Category[], parentCategoryId: number) => {
    cats.forEach((category) => {
      if (category.parentId === parentCategoryId) {
        ids.push(category.id)
        // 递归查找当前子分类的子分类
        findDescendants(cats, category.id)
      }
    })
  }

  // 将整个分类树扁平化为一维数组以便基于pid查找
  const flattenCategories = (cats: Category[]): Category[] => {
    let result: Category[] = []
    cats.forEach((category) => {
      result.push(category)
      if (category.children && category.children.length > 0) {
        result = result.concat(flattenCategories(category.children))
      }
    })
    return result
  }

  const flatCategories = flattenCategories(categories)
  findDescendants(flatCategories, parentId)

  return ids
}

// 初始化拖拽排序
const initDragAndDrop = () => {
  if (!categoryTableRef.value) return

  const table = categoryTableRef.value.$el.querySelector('.el-table__body-wrapper tbody')
  if (!table) return

  // 存储当前拖拽的行及其所有子行
  let draggedRows: Element[] = []
  // 存储当前拖拽分类及其所有子分类的扁平ID列表
  let draggedCategoryIds: number[] = []

  new Sortable(table, {
    animation: 150,
    handle: '.allow-drag',
    // 支持跨级别拖拽
    filter: '.drag-ghost',
    // 自定义拖拽项的选择方式，支持整个分类树一起拖拽
    onStart: (evt) => {
      // 清空之前存储的行和ID列表
      draggedRows = []
      draggedCategoryIds = []

      // 获取拖拽的起始行，并添加类型断言
      const startRow = evt.item as Element | null
      if (!startRow) return

      // 获取所有行
      const allRows = Array.from(table.querySelectorAll('.el-table__row')) as Element[]
      const startIndex = allRows.indexOf(startRow)

      // 将树形结构扁平化为一维数组，用于获取分类ID
      const flattenCategories = (categories: Category[]): Category[] => {
        let result: Category[] = []
        categories.forEach((category) => {
          result.push(category)
          if (category.children && category.children.length > 0) {
            result = result.concat(flattenCategories(category.children))
          }
        })
        return result
      }

      const flatCategories = flattenCategories(categoryList.value)

      // 获取起始行对应的分类ID
      if (startIndex >= 0 && startIndex < flatCategories.length) {
        const mainCategoryId = flatCategories[startIndex].id

        // 使用新方法：根据pid关系获取该分类及其所有后代分类的ID
        draggedCategoryIds = getAllDescendantCategoryIds(categoryList.value, mainCategoryId)

        console.log('拖拽的分类ID列表（基于pid关系）:', draggedCategoryIds)

        // 根据ID列表找出对应的行元素
        draggedRows = allRows.filter((row, index) => {
          return (
            index < flatCategories.length && draggedCategoryIds.includes(flatCategories[index].id)
          )
        })
      }

      // 添加拖拽样式，突出显示正在拖拽的整个分类树
      draggedRows.forEach((row) => {
        row.classList.add('being-dragged')
      })
    },

    // 拖拽结束时移除拖拽样式
    onEnd: async (evt) => {
      // 移除拖拽样式
      draggedRows.forEach((row) => {
        row.classList.remove('being-dragged')
      })

      // 确保我们有有效的分类ID列表
      if (draggedCategoryIds.length === 0) {
        draggedRows = []
        return
      }

      const { newIndex } = evt
      if (newIndex === undefined) {
        draggedRows = []
        draggedCategoryIds = []
        return
      }

      try {
        // 首先需要将树形结构扁平化为一维数组
        const flattenCategories = (categories: Category[]): Category[] => {
          let result: Category[] = []
          categories.forEach((category) => {
            result.push(category)
            if (category.children && category.children.length > 0) {
              result = result.concat(flattenCategories(category.children))
            }
          })
          return result
        }

        const flatCategories = flattenCategories(categoryList.value)

        // 检查索引是否有效
        if (newIndex === undefined || newIndex < 0 || newIndex >= flatCategories.length) {
          console.error('索引无效:', { newIndex })
          ElMessage.error('排序失败：索引无效')
          draggedRows = []
          draggedCategoryIds = []
          return
        }

        // 使用draggedCategoryIds数组中的第一个ID作为拖拽的主分类ID
        const draggedCategory =
          draggedCategoryIds.length > 0
            ? findCategoryById(categoryList.value, draggedCategoryIds[0])
            : null

        // 查找目标位置的分类
        let targetCategory
        let targetRow

        // 找到目标行元素
        const rows = Array.from(table.querySelectorAll('.el-table__row')) as Element[]
        if (newIndex >= 0 && newIndex < rows.length) {
          targetRow = rows[newIndex] as Element

          // 获取目标行对应的分类ID
          const targetRowIndex = Array.from(table.querySelectorAll('.el-table__row')).indexOf(
            targetRow
          )
          if (targetRowIndex >= 0 && targetRowIndex < flatCategories.length) {
            const targetCategoryId = flatCategories[targetRowIndex].id
            targetCategory = findCategoryById(categoryList.value, targetCategoryId)
          }
        }

        console.log('拖拽的分类:', draggedCategory)
        console.log('目标位置分类:', targetCategory)
        console.log('拖拽的分类ID列表:', draggedCategoryIds)

        if (!draggedCategory || !targetCategory) {
          console.error('未找到对应的分类数据', { draggedCategoryIds, targetCategory })
          ElMessage.error('排序失败：未找到对应的分类数据')
          // 确保清理拖拽状态
          draggedRows = []
          draggedCategoryIds = []
          return
        }

        // 检查是否会导致循环引用
        // 例如，如果将分类移动到其子分类下
        // 或者将包含该分类的分类树移动到该分类下
        let isCircularReference = false
        if (targetCategory && draggedCategory) {
          // 检查目标分类是否是被拖动分类的子分类
          isCircularReference = isDescendant(draggedCategory, targetCategory.id)

          // 检查目标分类是否是被拖动分类树中的任何一个分类的子分类
          // 这里需要遍历所有被拖动的分类ID
          for (const categoryId of draggedCategoryIds) {
            const category = findCategoryById(categoryList.value, categoryId)
            if (category && isDescendant(category, targetCategory.id)) {
              isCircularReference = true
              break
            }
          }

          // 检查被拖动分类是否就是目标分类本身
          if (draggedCategoryIds.includes(targetCategory.id)) {
            isCircularReference = true
          }
        }

        if (isCircularReference) {
          ElMessage.warning('不能将分类拖放到其子分类下或自身')
          // 确保清理拖拽状态
          draggedRows = []
          draggedCategoryIds = []
          return
        }

        // 确定新的父分类ID
        // 对于顶级分类之间的拖动，我们只需要保持同级关系
        // 当拖动带有子分类的顶级分类时，整个分类树应该作为一个整体移动
        let newParentId = 0

        // 获取目标行的缩进级别
        const targetRowIndent = targetRow ? getRowIndent(targetRow) : 0

        // 尝试获取原始拖拽行的缩进级别（如果可以找到的话）
        let draggedRowIndent = 0
        const firstDraggedRow = draggedRows.length > 0 ? draggedRows[0] : null
        if (firstDraggedRow) {
          draggedRowIndent = getRowIndent(firstDraggedRow)
        }

        console.log('缩进级别信息:', { targetRowIndent, draggedRowIndent })

        // 如果目标行是顶级分类（缩进为0），那么保持同级关系
        // 或者目标行和被拖动行是同一缩进级别，那么保持同级关系
        if (targetRowIndent === 0 || targetRowIndent === draggedRowIndent) {
          newParentId = 0 // 顶级分类的parentId应为0
        } else {
          // 如果目标行缩进更深，表示要将被拖动分类作为子分类添加
          newParentId = targetCategory.id
        }

        // 重新构建整个分类树结构
        // 1. 先创建一个完整的分类对象，确保包含所有子分类
        // 使用draggedCategoryIds数组中的第一个ID作为拖拽的主分类ID
        const mainCategoryId = draggedCategoryIds.length > 0 ? draggedCategoryIds[0] : null
        const completeCategoryToAdd = mainCategoryId
          ? findCategoryById(categoryList.value, mainCategoryId)
          : null

        if (!completeCategoryToAdd) {
          console.error('未找到完整的分类对象用于添加回分类树')
          ElMessage.error('排序失败：分类数据不完整')
          // 确保清理拖拽状态
          draggedRows = []
          draggedCategoryIds = []
          return
        }

        // 2. 移除被拖拽的所有分类及其所有子分类
        let categoriesWithoutDragged = [...categoryList.value]
        // 使用完整分类对象的ID来移除，确保移除所有相关的分类
        categoriesWithoutDragged = removeCategoryById(
          categoriesWithoutDragged,
          completeCategoryToAdd.id
        )

        console.log('移除被拖拽分类后的数据长度:', categoriesWithoutDragged.length)

        // 3. 计算新位置并添加回分类树
        // 确保添加完整的分类树结构（包括所有子分类）
        const newCategoryList = addCategoryAtPosition(
          categoriesWithoutDragged,
          completeCategoryToAdd,
          targetCategory.id,
          newParentId || 0
        )

        console.log('添加回分类树后的数据长度:', newCategoryList.length)

        // 4. 更新分类列表
        categoryList.value = newCategoryList
        console.log('更新后的分类列表:', newCategoryList)

        // 5. 生成排序数据并发送到后端
        // 使用更新后的分类列表来生成排序数据
        // 注意：先生成排序数据，这样会更新分类的sort字段值
        const sortData = generateSortData(newCategoryList)
        console.log('拖拽后的排序数据:', sortData)

        // 6. 现在再调用sortCategoriesBySortField函数
        // 因为generateSortData已经更新了sort字段值，所以排序会基于最新的顺序
        sortCategoriesBySortField(categoryList.value)
        console.log('排序后的分类列表:', categoryList.value)

        // 5. 调用API更新到服务端
        // 由于接口需要单个对象格式，我们为每个分类调用一次API
        try {
          console.log('开始调用API更新分类排序...')
          for (const data of sortData) {
            console.log(`调用API更新分类 ${data.id}: pid=${data.pid}, sort=${data.sort}`)
            const response = await updateCategorySort(data)
            console.log(`分类 ${data.id} 更新成功，响应:`, response)
          }
          console.log('所有分类排序更新成功')
          ElMessage.success('分类排序更新成功')

          // 使用强制刷新技巧让表格正确显示新的排序结果
          // 先将categoryList设置为空数组，然后在下一个渲染周期设置回更新后的数据
          const updatedCategories = [...categoryList.value]
          categoryList.value = []
          setTimeout(() => {
            categoryList.value = updatedCategories
          }, 0)
        } catch (error: any) {
          console.error('分类排序更新失败:', error)
          // 详细记录错误信息
          if (error.response) {
            console.error('API响应错误:', error.response.status, error.response.data)
          } else if (error.request) {
            console.error('无响应:', error.request)
          } else if (error.message) {
            console.error('请求错误:', error.message)
          }
          ElMessage.error('分类排序更新失败')
          // 失败时重新加载数据
          await loadCategoryList()
        } finally {
          // 确保清理拖拽状态
          draggedRows = []
          draggedCategoryIds = []
        }
      } catch (error) {
        console.error('拖拽排序失败:', error)
        ElMessage.error('分类排序更新失败')
        // 失败时重新加载数据
        await loadCategoryList()
        // 确保清理拖拽状态
        draggedRows = []
        draggedCategoryIds = []
      }
    }
  })
}

/**
 * 根据ID查找分类
 */
const findCategoryById = (categories: Category[], id: number): Category | null => {
  for (const category of categories) {
    if (category.id === id) {
      return category
    }
    if (category.children && category.children.length > 0) {
      const found = findCategoryById(category.children, id)
      if (found) {
        return found
      }
    }
  }
  return null
}

/**
 * 判断一个分类是否是另一个分类的后代
 */
const isDescendant = (parentCategory: Category, childId: number): boolean => {
  if (!parentCategory.children) {
    return false
  }
  for (const child of parentCategory.children) {
    if (child.id === childId) {
      return true
    }
    if (child.children && child.children.length > 0) {
      if (isDescendant(child, childId)) {
        return true
      }
    }
  }
  return false
}

/**
 * 获取行的缩进级别
 */
const getRowIndent = (row: Element): number => {
  const indentEl = row.querySelector('.el-table__indent')
  if (indentEl) {
    const width = parseInt(getComputedStyle(indentEl).width || '0')
    return Math.floor(width / 16) // 假设每个缩进级别是16px
  }
  return 0
}

/**
 * 从分类树中移除指定ID的分类及其所有子分类
 */
const removeCategoryById = (categories: Category[], id: number): Category[] => {
  const newCategories: Category[] = []

  for (const category of categories) {
    // 如果当前分类就是要移除的分类，直接跳过不添加到新数组中
    // 这样它的所有子分类也会被自动移除，因为我们没有处理它们
    if (category.id === id) {
      continue
    }

    // 创建一个新的分类对象
    const newCategory = { ...category }

    // 如果当前分类有子分类，递归处理子分类
    if (category.children && category.children.length > 0) {
      // 递归移除子分类中的目标分类及其子分类
      newCategory.children = removeCategoryById(category.children, id)
    }

    // 添加处理后的分类到新数组中
    newCategories.push(newCategory)
  }

  return newCategories
}

/**
 * 在指定位置添加分类
 */
const addCategoryAtPosition = (
  categories: Category[],
  categoryToAdd: Category,
  targetId: number,
  parentId: number
): Category[] => {
  // 创建一个新的分类对象，确保包含所有子分类
  const newCategoryToAdd = {
    ...categoryToAdd,
    parentId: parentId, // 保持parentId为数字，顶级分类该值为0
    children: [...(categoryToAdd.children || [])] // 深拷贝子分类数组，确保完整保留子分类结构
  }

  // 如果parentId为0，表示添加到顶级分类
  if (parentId === 0) {
    const newCategories = [...categories]

    // 找到目标分类在同级中的位置
    const targetIndex = newCategories.findIndex((c) => c.id === targetId)

    if (targetIndex !== -1) {
      // 直接插入到目标索引位置，而不是目标索引+1
      // 这样可以确保拖拽到任意位置时都能正确更新顺序
      newCategories.splice(targetIndex, 0, newCategoryToAdd)
    } else {
      // 如果没找到目标分类，添加到末尾
      newCategories.push(newCategoryToAdd)
    }

    return newCategories
  }

  // 递归查找父分类并添加
  const result: Category[] = []
  for (const category of categories) {
    if (category.id === parentId) {
      // 找到父分类，添加到目标分类所在的位置
      const parentCategory = { ...category }
      if (!parentCategory.children) {
        parentCategory.children = []
      }

      // 如果是添加到子级
      if (targetId === parentId) {
        // 作为第一个子元素添加
        parentCategory.children.unshift(newCategoryToAdd)
      } else {
        // 找到目标分类在父分类子级中的位置
        const targetIndex = parentCategory.children.findIndex((c) => c.id === targetId)

        if (targetIndex !== -1) {
          // 直接插入到目标索引位置，而不是目标索引+1
          // 这样可以确保拖拽到任意位置时都能正确更新顺序
          parentCategory.children.splice(targetIndex, 0, newCategoryToAdd)
        } else {
          // 如果没找到目标分类，添加到末尾
          parentCategory.children.push(newCategoryToAdd)
        }
      }

      result.push(parentCategory)
    } else {
      // 继续递归查找
      const newCategory = { ...category }
      if (category.children && category.children.length > 0) {
        newCategory.children = addCategoryAtPosition(
          category.children,
          categoryToAdd,
          targetId,
          parentId
        )
      }
      result.push(newCategory)
    }
  }

  return result
}

/**
 * 生成排序数据（用于API更新）并更新本地分类对象的sort值
 */
const generateSortData = (
  categories: Category[]
): Array<{ id: number; pid: number; sort: number }> => {
  const result: Array<{ id: number; pid: number; sort: number }> = []

  // 对同级分类进行独立排序
  const processCategories = (cats: Category[], parentId: number) => {
    console.log(`处理父分类ID: ${parentId} 的子分类，数量: ${cats.length}`)

    // 为当前级别的分类分配排序值，从总数开始递减
    const currentLevelCount = cats.length

    cats.forEach((category, index) => {
      // 计算sort值，从当前级别总数开始递减
      const sortValue = currentLevelCount - index
      console.log(
        `分类ID: ${category.id}, 名称: ${category.name}, 排序索引: ${index}, 计算出的sort值: ${sortValue}`
      )

      // 直接更新本地分类对象的sort值
      category.sort = sortValue

      result.push({
        id: category.id,
        pid: parentId,
        sort: sortValue
      })

      // 递归处理子分类
      if (category.children && category.children.length > 0) {
        processCategories(category.children, category.id)
      }
    })
  }

  // 从顶级分类开始处理
  processCategories(categories, 0)

  console.log('生成排序数据:', result)
  return result
}

// 方法定义
const handleEdit = (row: Category) => {
  // 导航到编辑页面
  router.push(`/admin/categories/edit/${row.id}`)
}

const handleDelete = async (row: Category) => {
  // 删除逻辑
  ElMessageBox.confirm(
    t('admin.category.action.delete.confirm'),
    t('admin.category.action.delete.title'),
    {
      confirmButtonText: t('admin.category.action.delete.confirmbtn'),
      cancelButtonText: t('admin.category.action.delete.cancelbtn'),
      type: 'warning'
    }
  )
    .then(async () => {
      try {
        const res = await deleteCategory(String(row.id))
        if (res.code === 1) {
          ElMessage.success(t('admin.category.action.delete.success'))
          // Refresh category list
          // categoryList.value = categoryList.value.filter((p) => p.id !== row.id)
          loadCategoryList()
        } else {
          ElMessage.error(res.msg)
        }
      } catch (error) {
        ElMessage.error(t('admin.category.action.delete.error'))
      }
    })
    .catch(() => {})
  console.log('删除分类:', row.id)
  // 这里可以添加确认对话框和删除API调用
}

const navigateToCreateCategory = () => {
  // 导航到创建分类页面
  router.push('/admin/categories/create')
}

const handleSortChange = async (row: Category) => {
  // 处理文章排序方式变更
  console.log(`分类 ${row.name} 的文章排序方式变为:`, row.articleSort)
  // 这里可以添加保存排序方式到后端的逻辑
  const articleOrder =
    row.articleSort === 'newest'
      ? 'id desc'
      : row.articleSort === 'oldest'
        ? 'pubtime asc'
        : 'views desc'
  try {
    const res = await updateCategoryArticleSort(String(row.id), {
      articles_order: articleOrder
    })
    if (res.code === 1) {
      ElMessage.success(t('admin.category.action.sort.success'))
    } else {
      ElMessage.error(res.msg)
    }
  } catch (error) {
    ElMessage.error(t('admin.category.action.sort.error'))
  }
}
</script>

<style scoped lang="scss">
.category-management-container {
  padding: 20px;
  min-height: 100vh;
  box-sizing: border-box;
}

.page-header {
  margin-bottom: 30px;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 15px;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;

  h1 {
    margin: 0 0 5px 0;
    font-size: 24px;
    font-weight: 600;
  }

  p {
    margin: 0;
    color: #6b7280;
    font-size: 14px;
  }
}

.table-container {
  margin-bottom: 80px; // 为固定操作栏留出空间
}

.wy-table {
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.category-table {
  width: 100%;
}

.operation-buttons {
  display: flex;
  gap: 10px;
}

.no-image {
  display: inline-block;
  width: 40px;
  height: 40px;
  line-height: 40px;
  text-align: center;
  background-color: #f3f4f6;
  border-radius: 4px;
  color: #9ca3af;
  font-size: 12px;
}

.fixed-action-bar {
  position: fixed;
  bottom: 0;
  right: 0;
  left: 0;
  padding: 15px 20px;
  background-color: white;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
}

.create-category-btn {
  padding: 10px 20px;
  font-size: 14px;
}

/* 拖拽样式 */
.el-table .allow-drag {
  cursor: move;
}

/* 拖拽过程中分类树的样式 */
.el-table .being-dragged {
  background-color: #e6f7ff;
  border-left: 3px solid #1890ff;
}

/* 拖动时的占位符样式 */
.drag-ghost {
  opacity: 0.5;
}

/* 优化拖拽时的视觉反馈 */
.el-table__row.being-dragged td {
  background-color: #e6f7ff;
}

/* 为拖拽的行添加过渡效果 */
.el-table__row {
  transition: background-color 0.3s ease;
}

/* 移动端适配 */
@media (max-width: 767px) {
  .page-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .create-category-btn {
    width: 100%;
  }

  /* 移动端分类卡片 */
  .mobile-categories-container {
    padding: 0;
  }

  .mobile-category-card {
    margin-bottom: 12px;
    border-radius: 8px;
  }

  .mobile-category-card :deep(.el-card__body) {
    padding: 16px;
  }

  .child-card {
    margin-left: 16px;
    margin-bottom: 8px;
    border-left: 3px solid var(--el-color-primary);
  }

  .category-card-header {
    margin-bottom: 16px;
  }

  .category-title {
    display: flex;
    gap: 12px;
    align-items: flex-start;
  }

  .category-cover {
    width: 60px;
    height: 60px;
    border-radius: 8px;
    object-fit: cover;
    flex-shrink: 0;
  }

  .category-cover-placeholder {
    width: 60px;
    height: 60px;
    border-radius: 8px;
    background: var(--el-fill-color-light);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    color: var(--el-text-color-placeholder);
  }

  .category-info {
    flex: 1;
    min-width: 0;
  }

  .category-info h3 {
    margin: 0 0 8px 0;
    font-size: 16px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .category-info p {
    margin: 0;
    font-size: 14px;
    color: var(--el-text-color-secondary);
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
  }

  .category-card-body {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .info-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 14px;
  }

  .info-row .label {
    color: var(--el-text-color-secondary);
    flex-shrink: 0;
    margin-right: 8px;
  }

  .info-row .value {
    color: var(--el-text-color-primary);
    text-align: right;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .info-row .el-select {
    width: auto;
    flex-shrink: 0;
  }

  .category-card-actions {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
  }

  /* 对话框宽度优化 */
  .el-dialog {
    width: 95% !important;
  }
}
</style>
