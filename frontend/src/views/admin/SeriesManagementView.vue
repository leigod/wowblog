<template>
  <div class="series-management-container">
    <div class="page-header">
      <div>
        <h1>{{ t('admin.series.title') }}</h1>
        <p>{{ t('admin.series.title_info') }}</p>
      </div>
      <el-button
        type="primary"
        size="default"
        class="create-series-btn"
        @click="navigateToCreateSeries"
      >
        <el-icon><Plus /></el-icon> {{ t('admin.series.btn.add') }}
      </el-button>
    </div>

    <div class="series-list-container">
      <!-- Series list items -->
      <div v-for="series in seriesList" :key="series.id" class="series-item">
        <div class="allow-drag" style="cursor: move">
          <IconifyIcon icon="material-symbols:drag-indicator" />
        </div>
        <div class="series-info">
          <span class="series-name">{{ series.name }}</span>
        </div>
        <div class="series-actions">
          <el-button type="default" round class="view-series-btn" @click="viewSeries(series.slug)">
            <IconifyIcon icon="pepicons-pencil:open" />
            <span style="margin-left: 10px">{{ t('admin.series.btn.view') }}</span>
          </el-button>
          <el-dropdown trigger="click">
            <el-button type="default" round text class="more-actions-btn">
              <el-icon><More /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="editSeries(series.id)">
                  <el-icon><Edit /></el-icon> {{ t('admin.general.btn.edit') }}
                </el-dropdown-item>
                <el-dropdown-item @click="deleteSeriesItem(series.id)" class="danger">
                  <el-icon><Delete /></el-icon> {{ t('admin.general.btn.delete') }}
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <!-- Empty state -->
      <div v-if="seriesList.length === 0" class="empty-state">
        <div class="empty-state-icon"><component :is="getEmptyStateIcon()" /></div>
        <h3 class="empty-state-title">{{ getEmptyStateTitle() }}</h3>
        <p class="empty-state-description">{{ getEmptyStateDescription() }}</p>
      </div>
    </div>

    <!-- Fixed action bar -->
    <!-- <div class="fixed-action-bar">
      <el-button
        type="primary"
        size="default"
        class="create-series-btn"
        @click="navigateToCreateSeries"
      >
        <el-icon><Plus /></el-icon> Create new series
      </el-button>
    </div> -->
  </div>
</template>

<script setup lang="ts">
import { ref, h, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { View, More, Edit, Delete, Plus, Reading } from '@element-plus/icons-vue'
import {
  ElButton,
  ElDropdown,
  ElDropdownMenu,
  ElDropdownItem,
  ElIcon,
  ElMessageBox,
  ElMessage
} from 'element-plus'
import { getManageSeriesList, deleteSeries, updateSeriesSort } from '@/api/services/series'
import IconifyIcon from '@/components/IconIfy.vue'
import Sortable from 'sortablejs'
import type { SortableEvent } from 'sortablejs'

// Define series interface
interface Series {
  id: string
  name: string
  slug: string
}

const { t } = useI18n()

// State
const seriesList = ref<Series[]>([]) // Empty initial state
const router = useRouter()
let sortableInstance: Sortable | null = null

// 监听seriesList变化，重新设置拖拽
watch(
  seriesList,
  () => {
    nextTick(() => {
      setSort()
    })
  },
  { immediate: true }
)

seriesList.value = []
// Methods
const viewSeries = (seriesSlug: string) => {
  // Navigation logic will be implemented later
  console.log('View series:', seriesSlug)
  window.open(`/series/${seriesSlug}`, '_blank')
}

const editSeries = (seriesId: string) => {
  // Edit logic will be implemented later
  router.push(`/admin/series/edit/${seriesId}`)
  console.log('Edit series:', seriesId)
}

const deleteSeriesItem = async (seriesId: string) => {
  // Delete logic will be implemented later
  ElMessageBox.confirm(t('admin.series.action.delete.confirm'))
    .then(async () => {
      try {
        const res = await deleteSeries(seriesId)
        if (res.code === 1) {
          ElMessage.success(t('admin.series.action.delete.success'))
          // Refresh series list
          seriesList.value = seriesList.value.filter((p) => p.id !== seriesId)
        } else {
          ElMessage.error(res.msg)
        }
      } catch (error) {
        ElMessage.error(t('admin.series.action.delete.error'))
      }
    })
    .catch(() => {})
}

const navigateToCreateSeries = () => {
  // Navigation to create series page
  router.push('/admin/series/create')
}

// Empty state methods
const getEmptyStateIcon = () => {
  return h(Reading, { class: 'empty-icon' })
}

const getEmptyStateTitle = () => {
  return t('admin.series.action.empty.title')
}

const getEmptyStateDescription = () => {
  return t('admin.series.action.empty.description')
}

// 设置拖拽排序功能
const setSort = () => {
  nextTick(() => {
    const seriesContainer = document.querySelector('.series-list-container') as HTMLElement
    if (!seriesContainer) return

    // 销毁现有实例
    if (sortableInstance) {
      sortableInstance.destroy()
    }

    // 创建新的拖拽实例
    sortableInstance = new Sortable(seriesContainer, {
      handle: '.allow-drag',
      animation: 150,
      onEnd: (event: SortableEvent) => {
        const oldIdx = event.oldIndex ?? -1
        const newIdx = event.newIndex ?? -1
        if (oldIdx === -1 || newIdx === -1 || oldIdx === newIdx) return

        const newItems = [...seriesList.value]
        const [movedItem] = newItems.splice(oldIdx, 1)
        newItems.splice(newIdx, 0, movedItem)
        seriesList.value = newItems
        saveSeriesOrder(newItems.map((item) => item.id))
      }
    })
  })
}

// 保存系列排序
const saveSeriesOrder = async (ids: string[]) => {
  try {
    updateSeriesSort(ids)
      .then(() => {
        ElMessage.success(t('admin.series.action.update.sort.success'))
        loadSeriesList()
      })
      .catch(() => {
        ElMessage.error(t('admin.series.action.update.sort.error'))
        loadSeriesList()
      })
  } catch (error) {
    ElMessage.error(t('admin.series.action.update.sort.error'))
    loadSeriesList()
  }
}

// 加载系列列表
const loadSeriesList = async () => {
  try {
    const response = await getManageSeriesList()
    seriesList.value = response.data
  } catch (error) {
    console.error('Error fetching series list:', error)
  }
}

// Load series list on component mount
onMounted(async () => {
  await loadSeriesList()
  nextTick(() => {
    setSort()
  })
})
</script>

<style scoped lang="scss">
.series-management-container {
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

.series-list-container {
  margin-bottom: 80px; // Space for fixed action bar
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.series-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  margin-bottom: 10px;
  transition: box-shadow 0.2s;
  width: 800px;

  &:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  }
}

.series-info {
  flex: 1;
}

.series-name {
  font-size: 16px;
  font-weight: 500;
}

.series-actions {
  display: flex;
  gap: 10px;
}

.view-series-btn,
.more-actions-btn {
  padding: 5px 10px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  color: #6b7280;
}

.empty-state-icon {
  font-size: 48px;
  margin-bottom: 16px;
  color: #9ca3af;
}

.empty-state-title {
  font-size: 18px;
  font-weight: 500;
  margin-bottom: 8px;
  color: #1f2937;
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

.create-series-btn {
  padding: 10px 20px;
  font-size: 14px;
}

/* 拖拽样式 */
.allow-drag {
  cursor: move;
}

@media screen and (max-width: 1080px) {
  .series-item {
    width: 100%;
  }
}
</style>
