<template>
  <div class="page-management-container">
    <div class="page-header">
      <div>
        <h1>{{ t('admin.pages.title') }}</h1>
        <p>{{ t('admin.pages.title_info') }}</p>
      </div>

      <el-button type="primary" size="default" class="create-button" @click="handleCreate">
        <el-icon><Plus /></el-icon> {{ t('admin.pages.btn.add') }}
      </el-button>
    </div>

    <!-- Pages Table - Desktop -->
    <div class="page-table-container">
      <el-table
        v-if="!isMobile"
        :data="pages"
        class="page-table"
        :header-cell-style="{
          backgroundColor: '#fafafa',
          fontWeight: 800,
          fontSize: '1rem',
          padding: '12px 14px'
        }"
        :cell-style="{
          padding: '12px 14px'
        }"
        :row-key="(row) => row.id"
      >
        <el-table-column prop="name" :label="t('admin.pages.table.name')" />
        <el-table-column prop="slug" :label="t('admin.pages.table.slug')" />
        <el-table-column prop="description" :label="t('admin.pages.table.description')" />
        <el-table-column :label="t('admin.pages.table.actions')" width="230">
          <template #default="{ row }">
            <el-tooltip
              :content="row.visible ? t('admin.pages.action.hide') : t('admin.pages.action.show')"
              placement="top"
            >
              <el-button type="default" circle text @click="handleToggleVisibility(row)">
                <IconifyIcon
                  :icon="row.visible ? 'clarity:eye-show-solid' : 'clarity:eye-hide-solid'"
                  stroke-width="0.1"
                  :color="row.visible ? '#409eff' : '#909399'"
                  width="20"
                  height="20"
                />
              </el-button>
            </el-tooltip>
            <el-dropdown trigger="click">
              <el-button type="default" circle text class="more-button">
                <el-icon><More /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="handleView(row)">
                    <span style="margin-left: -2px; margin-right: 2px; line-height: 12px"
                      ><IconifyIcon
                        icon="pepicons-pencil:open"
                        width="20"
                        height="20"
                        stroke-width="0.1"
                    /></span>
                    {{ t('admin.general.btn.view') }}
                  </el-dropdown-item>
                  <el-dropdown-item @click="handleEdit(row)">
                    <el-icon><Edit /></el-icon> {{ t('admin.general.btn.edit') }}
                  </el-dropdown-item>
                  <el-dropdown-item @click="handleDelete(row)" class="danger">
                    <el-icon><Delete /></el-icon> {{ t('admin.general.btn.delete') }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pages Cards - Mobile -->
      <div v-else class="page-cards">
        <el-card v-for="row in pages" :key="row.id" class="page-card" shadow="hover">
          <div class="card-header">
            <el-tag :type="row.visible ? 'success' : 'info'" size="small">
              {{ row.visible ? t('admin.pages.table.visible') : t('admin.pages.table.hidden') }}
            </el-tag>
            <el-button
              type="default"
              size="small"
              text
              @click="handleToggleVisibility(row)"
              class="visibility-toggle"
            >
              <IconifyIcon
                :icon="row.visible ? 'clarity:eye-hide-solid' : 'clarity:eye-show-solid'"
                stroke-width="0.1"
                :color="row.visible ? '#409eff' : '#909399'"
                width="18"
                height="18"
              />
            </el-button>
          </div>
          <div class="card-body">
            <div class="info-row">
              <span class="label">{{ t('admin.pages.table.name') }}:</span>
              <span class="value">{{ row.name }}</span>
            </div>
            <div class="info-row">
              <span class="label">{{ t('admin.pages.table.slug') }}:</span>
              <span class="value slug-value">{{ row.slug }}</span>
            </div>
            <div class="info-row">
              <span class="label">{{ t('admin.pages.table.description') }}:</span>
              <span class="value description-value">{{ row.description || '-' }}</span>
            </div>
          </div>
          <div class="card-footer">
            <el-button size="small" @click="handleView(row)">
              <el-icon><View /></el-icon> {{ t('admin.general.btn.view') }}
            </el-button>
            <el-button size="small" @click="handleEdit(row)">
              <el-icon><Edit /></el-icon> {{ t('admin.general.btn.edit') }}
            </el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">
              <el-icon><Delete /></el-icon> {{ t('admin.general.btn.delete') }}
            </el-button>
          </div>
        </el-card>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="pages.length === 0" class="empty-state">
      <div class="empty-state-icon">
        <el-icon><Document /></el-icon>
      </div>
      <h3 class="empty-state-title">{{ t('admin.pages.action.empty.title') }}</h3>
      <p class="empty-state-description">{{ t('admin.pages.action.empty.description') }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

import {
  ElTable,
  ElTableColumn,
  ElButton,
  ElDropdown,
  ElDropdownMenu,
  ElDropdownItem,
  ElIcon,
  ElMessage,
  ElMessageBox,
  ElCard,
  ElTag
} from 'element-plus'
import { View, Edit, Delete, More, Plus, Document, Hide } from '@element-plus/icons-vue'
import IconifyIcon from '@/components/IconIfy.vue'
import { useMobileDetection } from '@/composables/useMobileDetection'
import {
  getManagePageList,
  updatePageStatus,
  deletePage,
  createPage,
  updatePage
} from '@/api/services/pages'

// Types
interface Page {
  id: string
  name: string
  slug: string
  description: string
  createdAt: string
  visible: boolean
}

// i18n
const { t } = useI18n()

// 移动端检测
const { isMobile } = useMobileDetection()

// State
const router = useRouter()
const pages = ref<Page[]>([])

// 响应式抽屉宽度
const drawerSize = computed(() => isMobile.value ? '100%' : '50%')

// Methods
const handleView = (page: Page) => {
  // Implement view page logic
  //ElMessage.info(`Viewing page: ${page.name}`)
  router.push(`/page/${page.slug}`)
}

const handleToggleVisibility = async (page: Page) => {
  page.visible = !page.visible
  console.log(page.visible)
  try {
    const res = await updatePageStatus(page.id, page.visible ? 'normal' : 'hidden')
    console.log(res)
    if (res.code === 1) {
      ElMessage.info(
        t('admin.pages.action.toggle.success', {
          action: page.visible ? 'Showing' : 'Hiding',
          pagename: page.name
        })
      )
    } else {
      ElMessage.error(
        t('admin.pages.action.toggle.error', {
          action: page.visible ? 'Showing' : 'Hiding',
          pagename: page.name
        })
      )
    }
  } catch (error) {
    ElMessage.error(
      t('admin.pages.action.toggle.error', {
        action: page.visible ? 'Showing' : 'Hiding',
        pagename: page.name
      })
    )
  }
}

const handleEdit = (page: Page) => {
  // Implement edit page logic
  router.push(`/admin/pages/edit/${page.id}`)
}

const handleDelete = async (page: Page) => {
  ElMessageBox.confirm(t('admin.pages.action.delete.confirm'))
    .then(async () => {
      try {
        const res = await deletePage(page.id)
        console.log(res)
        if (res.code === 1) {
          ElMessage.success(t('admin.pages.action.delete.success', { pagename: page.name }))
          // In a real application, you would show a confirmation dialog first
          pages.value = pages.value.filter((p) => p.id !== page.id)
        } else {
          ElMessage.error(t('admin.pages.action.delete.error', { pagename: page.name }))
        }
      } catch (error) {
        ElMessage.error(t('admin.pages.action.delete.error', { pagename: page.name }))
      }
    })
    .catch(() => {
      // catch error
    })
}

const handleCreate = () => {
  // Navigate to create new page
  router.push('/admin/pages/create')
}

onMounted(() => {
  loadPages()
})

// 获取页面列表
const loadPages = async () => {
  try {
    const pageList = await getManagePageList()
    console.log(pageList)
    // 为 item 添加类型定义，避免隐式 any 类型
    pages.value = pageList.data.map((item: any) => ({
      id: item.id,
      name: item.title,
      slug: item.slug,
      description: (item.content || '').slice(0, 150).replace(/<\/?[^>]+(>|$)/g, ''),
      createdAt: item.createtime,
      visible: item.status == 'normal'
    }))
  } catch (error) {
    console.error('加载页面列表失败:', error)
    // 将错误向上传播，确保全局错误处理能够正常工作
    throw error
  }
}
</script>

<style scoped>
.page-management-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e5e7eb;
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

.page-table-container {
  width: 100%;
  display: flex;
  justify-content: center;
}

.page-table {
  width: 80%;
  margin-bottom: 80px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.visibility-button {
  margin-right: 5px;
}
.visibility-button.visible .el-icon {
  color: #409eff;
}

.visibility-button.hidden .el-icon {
  color: #909399;
  opacity: 0.6;
}

.fixed-action-bar {
  position: fixed;
  bottom: 20px;
  right: 20px;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
  color: #666;
}

.empty-state-icon {
  font-size: 48px;
  margin-bottom: 16px;
  color: #ccc;
}

.more-button {
  padding: 0;
}

/* 移动端适配 */
@media (max-width: 767px) {
  .page-management-container {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    padding-bottom: 12px;
  }

  .page-header h1 {
    font-size: 20px;
  }

  .page-header p {
    font-size: 13px;
  }

  .create-button {
    width: 100%;
  }

  /* 页面卡片样式 */
  .page-cards {
    display: flex;
    flex-direction: column;
    gap: 12px;
    width: 100%;
  }

  .page-card {
    margin: 0;
    width: 100%;
  }

  .page-card .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    margin-bottom: 12px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--el-border-color-lighter);
  }

  .page-card .card-body {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .page-card .info-row {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    font-size: 13px;
  }

  .page-card .info-row .label {
    color: var(--el-text-color-secondary);
    min-width: 60px;
    flex-shrink: 0;
  }

  .page-card .info-row .value {
    color: var(--el-text-color-regular);
    word-break: break-all;
    flex: 1;
  }

  .page-card .info-row .slug-value {
    color: #3b82f6;
    font-family: monospace;
  }

  .page-card .info-row .description-value {
    color: #6b7280;
    font-size: 12px;
    line-height: 1.4;
  }

  .page-card .card-footer {
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid var(--el-border-color-lighter);
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }

  .page-card .card-footer .el-button {
    flex: 1;
    min-width: 80px;
  }

  .page-card .visibility-toggle {
    padding: 4px;
  }

  /* 空状态优化 */
  .empty-state {
    padding: 40px 16px;
  }

  .empty-state-icon {
    font-size: 36px;
  }

  .empty-state-title {
    font-size: 16px;
  }

  .empty-state-description {
    font-size: 13px;
  }
}
</style>
