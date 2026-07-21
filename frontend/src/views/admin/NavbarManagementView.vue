<template>
  <div class="navbar-management-container">
    <div class="page-header">
      <div>
        <h1>{{ t('admin.navbar.title') }}</h1>
        <p>{{ t('admin.navbar.title_info') }}</p>
      </div>
      <el-button type="primary" size="default" class="add-button" @click="openDrawer">
        <el-icon>
          <Plus />
        </el-icon> {{ t('admin.navbar.btn.add') }}
      </el-button>
    </div>

    <!-- Navigation Items Table -->
    <div class="navbar-table-container">
      <!-- 桌面端表格 -->
      <el-table v-if="!isMobile" ref="navbarTable" :data="navbarItems" class="navbar-table" :header-cell-style="{
        backgroundColor: '#fafafa',
        fontWeight: 800,
        fontSize: '1rem',
        padding: '12px 14px'
      }" :row-key="(row) => row.id">
        <el-table-column :label="t('admin.navbar.table.sort')" width="100" align="center">
          <template #default>
            <div class="allow-drag" style="cursor: move">
              <IconifyIcon icon="material-symbols:drag-indicator" />
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="label" :label="t('admin.navbar.table.label')" />
        <el-table-column prop="type" :label="t('admin.navbar.table.type')">
          <template #default="{ row }">{{ formatType(row.type) }}</template>
        </el-table-column>
        <el-table-column prop="value" :label="t('admin.navbar.table.value')">
          <template #default="{ row }">
            <span v-if="row.type === 'link'" class="link-value">{{ row.value }}</span>
            <span v-else class="page-series-value">{{ row.valueLabel }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('admin.navbar.table.actions')">
          <template #default="{ row }">
            <el-dropdown trigger="click">
              <el-button type="default" size="small" text circle class="action-button">
                <el-icon>
                  <More />
                </el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="handleEdit(row)">
                    <el-icon>
                      <Edit />
                    </el-icon> {{ t('admin.general.btn.edit') }}
                  </el-dropdown-item>
                  <el-dropdown-item @click="handleDelete(row)" class="danger" v-if="row.nav_type !== 'sys'">
                    <el-icon>
                      <Delete />
                    </el-icon> {{ t('admin.general.btn.delete') }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <!-- 移动端卡片 -->
      <div v-else class="navbar-cards">
        <el-card v-for="row in navbarItems" :key="row.id" class="navbar-card" shadow="hover">
          <div class="card-header">
            <div class="drag-handle">
              <IconifyIcon icon="material-symbols:drag-indicator" />
            </div>
            <el-tag :type="row.nav_type === 'sys' ? 'info' : 'primary'" size="small">
              {{ formatType(row.type) }}
            </el-tag>
          </div>
          <div class="card-body">
            <div class="info-row">
              <span class="label">{{ t('admin.navbar.table.label') }}:</span>
              <span class="value">{{ row.label }}</span>
            </div>
            <div class="info-row">
              <span class="label">{{ t('admin.navbar.table.value') }}:</span>
              <span v-if="row.type === 'link'" class="value link-value">{{ row.value }}</span>
              <span v-else class="value page-series-value">{{ row.valueLabel }}</span>
            </div>
          </div>
          <div class="card-footer">
            <el-button size="small" @click="handleEdit(row)" v-if="row.nav_type !== 'sys'">
              <el-icon>
                <Edit />
              </el-icon> {{ t('admin.general.btn.edit') }}
            </el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)" v-if="row.nav_type !== 'sys'">
              <el-icon>
                <Delete />
              </el-icon> {{ t('admin.general.btn.delete') }}
            </el-button>
            <el-button size="small" disabled v-else>
              <el-icon>
                <Lock />
              </el-icon> 系统项
            </el-button>
          </div>
        </el-card>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="navbarItems.length === 0" class="empty-state">
      <div class="empty-state-icon">
        <component :is="getEmptyStateIcon()" />
      </div>
      <h3 class="empty-state-title">{{ getEmptyStateTitle() }}</h3>
      <p class="empty-state-description">{{ getEmptyStateDescription() }}</p>
    </div>

    <!-- Drawer Form -->
    <el-drawer v-model="drawerVisible"
      :title="`${isEditing ? t('admin.navbar.form.edit_title') : t('admin.navbar.form.add_title')}`" :size="drawerSize"
      direction="rtl" @close="closeDrawer">
      <el-form ref="formRef" :model="formData" :rules="formRules" :label-width="formLabelConfig.labelWidth"
        :label-position="formLabelConfig.labelPosition" class="navbar-form">
        <!-- Item Label -->
        <el-form-item :label="t('admin.navbar.form.label')" prop="label">
          <el-input v-model="formData.label" :placeholder="t('admin.navbar.form.label_placeholder')"
            class="form-input" />
        </el-form-item>

        <!-- Type Selection -->
        <el-form-item :label="t('admin.navbar.form.type')" prop="type">
          <el-select v-model="formData.type" :placeholder="t('admin.navbar.form.type_placeholder')" class="form-select"
            @change="handleTypeChange" :disabled="formData.nav_type == 'sys'">
            <el-option :label="t('admin.navbar.form.type_link')" value="link" />
            <el-option :label="t('admin.navbar.form.type_page')" value="page" />
            <el-option :label="t('admin.navbar.form.type_series')" value="series" />
            <el-option :label="t('admin.navbar.form.type_doc')" value="doc" />
          </el-select>
        </el-form-item>

        <!-- Dynamic Value Field -->
        <el-form-item :label="t('admin.navbar.form.value')" prop="value" :rules="valueRules">
          <!-- Link Type - URL Input -->
          <el-input v-if="formData.type === 'link'" v-model="formData.value"
            :placeholder="t('admin.navbar.form.value_placeholder')" class="form-input"
            :disabled="formData.nav_type == 'sys'" />

          <!-- Page Type - Dropdown -->
          <el-select v-else-if="formData.type === 'page'" v-model="formData.value"
            :placeholder="t('admin.navbar.form.page_placeholder')" class="form-select"
            :disabled="formData.nav_type == 'sys'">
            <el-option v-for="page in availablePages" :key="page.id" :label="page.title" :value="page.id" />
          </el-select>

          <!-- Series Type - Dropdown -->
          <el-select v-else-if="formData.type === 'series'" v-model="formData.value"
            :placeholder="t('admin.navbar.form.series_placeholder')" class="form-select"
            :disabled="formData.nav_type == 'sys'">
            <el-option v-for="series in availableSeries" :key="series.id" :label="series.name" :value="series.id" />
          </el-select>

          <!-- Doc Type - Dropdown -->
          <el-select v-else-if="formData.type === 'doc'" v-model="formData.value"
            :placeholder="t('admin.navbar.form.doc_placeholder')" class="form-select"
            :disabled="formData.nav_type == 'sys'">
            <el-option v-for="docBook in availableDocBooks" :key="docBook.id"
              :label="`${docBook.name} (${docBook.slug})`" :value="String(docBook.id)" />
          </el-select>
        </el-form-item>
      </el-form>

      <div class="drawer-actions">
        <el-button @click="closeDrawer">{{ t('admin.general.btn.cancel') }}</el-button>
        <el-button type="primary" @click="submitForm">
          {{ isEditing ? t('admin.general.btn.update') : t('admin.general.btn.create') }}
        </el-button>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, h, onMounted, computed, nextTick, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useMobileDetection } from '@/composables/useMobileDetection'
import {
  ElTable,
  ElTableColumn,
  ElButton,
  ElDropdown,
  ElDropdownMenu,
  ElDropdownItem,
  ElDrawer,
  ElForm,
  ElFormItem,
  ElInput,
  ElSelect,
  ElOption,
  ElIcon,
  ElMessage
} from 'element-plus'
import type { FormInstance, FormRules, FormItemRule } from 'element-plus'
import { Plus, More, Edit, Delete, Menu, Lock } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import Sortable from 'sortablejs'
import type { SortableEvent } from 'sortablejs'
import {
  getManageNavList,
  createNav,
  updateNav,
  updateNavSort,
  deleteNav
} from '@/api/services/nav'
import { getManagePageList } from '@/api/services/pages'
import { getManageSeriesList } from '@/api/services/series'
import { docBookApi } from '@/api/services/doc'
import IconifyIcon from '@/components/IconIfy.vue'

// Types
interface NavbarItem {
  id: string
  label: string
  nav_type: 'sys' | 'user'
  type: 'link' | 'page' | 'series' | 'doc'
  value: string
  valueLabel?: string
}

interface Page {
  id: string
  title: string
}

interface Series {
  id: string
  name: string
}

interface DocBook {
  id: number
  name: string
  slug: string
}

const { t } = useI18n()

// 移动端检测
const { isMobile } = useMobileDetection()

// State
const navbarItems = ref<NavbarItem[]>([])
let sortableInstance: Sortable | null = null

// 响应式抽屉宽度
const drawerSize = computed(() => isMobile.value ? '100%' : '50%')

// 响应式表单标签配置
const formLabelConfig = computed(() => ({
  labelWidth: isMobile.value ? 'auto' : '120px',
  labelPosition: (isMobile.value ? 'top' : 'right') as 'left' | 'right' | 'top'
}))

watch(
  navbarItems,
  () => {
    nextTick(() => {
      setSort()
    })
  },
  { immediate: true }
)

// Drag and drop initialization
const setSort = () => {
  nextTick(() => {
    const tableBody = navbarTable.value?.$el.querySelector('.el-table__body-wrapper tbody')
    if (!tableBody) return

    // Destroy existing instance if exists
    if (sortableInstance) {
      sortableInstance.destroy()
    }

    // Create new drag instance
    sortableInstance = new Sortable(tableBody, {
      handle: '.allow-drag',
      animation: 150,
      onEnd: (event: SortableEvent) => {
        const oldIdx = event.oldIndex ?? -1
        const newIdx = event.newIndex ?? -1
        if (oldIdx === -1 || newIdx === -1 || oldIdx === newIdx) return

        const newItems = [...navbarItems.value]
        const [movedItem] = newItems.splice(oldIdx, 1)
        newItems.splice(newIdx, 0, movedItem)
        navbarItems.value = newItems
        saveNavbarOrder(newItems.map((item) => item.id))
      }
    })
  })
}
const drawerVisible = ref(false)
const isEditing = ref(false)
const formRef = ref<FormInstance>()
const router = useRouter()
const navbarTable = ref<InstanceType<typeof ElTable>>()

// Form data
interface NavbarForm {
  id?: string
  label: string
  nav_type: '' | 'sys' | 'user'
  type: '' | 'link' | 'page' | 'series' | 'doc'
  value: string
}

const formData = reactive<NavbarForm>({
  id: undefined,
  label: '',
  nav_type: '',
  type: '',
  value: ''
})

// Mock data - would normally come from API
const availablePages = ref<Page[]>([])

const availableSeries = ref<Series[]>([])

const availableDocBooks = ref<DocBook[]>([])

// Get validation rules for value field based on type
const valueRules = computed((): FormItemRule[] => {
  if (formData.type === undefined) return []
  if (formData.nav_type == 'sys') return []

  const trigger: 'blur' | 'change' = formData.type! === 'link' ? 'blur' : 'change'
  const requiredRule: FormItemRule = {
    required: true,
    message: t('admin.navbar.validation.general'),
    trigger
  }
  const urlRule: FormItemRule | null =
    formData.type === 'link'
      ? {
        type: 'url' as const,
        required: true,
        message: t('admin.navbar.validation.link'),
        trigger: 'blur'
      }
      : null

  return [requiredRule, ...(urlRule ? [urlRule] : [])]
})

// Form validation rules
const formRules: FormRules<NavbarForm> = {
  label: [
    { required: true, message: t('admin.navbar.validation.label'), trigger: 'blur' },
    { max: 50, message: t('admin.navbar.validation.label_length'), trigger: 'blur' }
  ],
  type: [
    { required: true, message: t('admin.navbar.validation.type'), trigger: ['change', 'blur'] }
  ],
  value: valueRules.value
}

// Lifecycle
onMounted(() => {
  // In a real app, this would be replaced with API call
  loadNavbarItems()
  loadPageList()
  loadSeriesList()
  loadDocBookList()
  nextTick(() => {
    setSort()
  })
})

const saveNavbarOrder = async (ids: string[]) => {
  try {
    // 实际项目中替换为真实API调用
    // 示例: await api.navbar.updateOrder(ids)
    console.log('更新导航排序:', ids)
    updateNavSort(ids)
      .then(() => {
        ElMessage.success(t('admin.navbar.action.update.sort.success'))
        loadNavbarItems()
      })
      .catch(() => {
        ElMessage.error(t('admin.navbar.action.update.sort.error'))
        loadNavbarItems()
      })
  } catch (error) {
    ElMessage.error(t('admin.navbar.action.update.sort.error'))
    loadNavbarItems()
  }
}

// Methods
// 获取导航列表
const loadNavbarItems = async () => {
  try {
    const navList = await getManageNavList()
    console.log(navList)
    navbarItems.value = navList.data
  } catch (error) {
    console.error('加载导航列表失败:', error)
  }
}

// 获取页面列表
const loadPageList = async () => {
  try {
    const pageList = await getManagePageList()
    availablePages.value = pageList.data
  } catch (error) {
    console.error('加载页面列表失败:', error)
  }
}

// 获取系列列表
const loadSeriesList = async () => {
  try {
    const seriesList = await getManageSeriesList()
    availableSeries.value = seriesList.data
  } catch (error) {
    console.error('加载系列列表失败:', error)
  }
}

// 获取文档书列表
const loadDocBookList = async () => {
  try {
    const docBooksRes = await docBookApi.list({ skip: 0, limit: 100 })
    if (docBooksRes.code === 1 && docBooksRes.data) {
      availableDocBooks.value = docBooksRes.data
      console.log('共加载文档书:', docBooksRes.data.length)
    }
  } catch (error) {
    console.error('加载文档书列表失败:', error)
  }
}

const openDrawer = () => {
  resetForm()
  isEditing.value = false
  drawerVisible.value = true
  formData.type = 'link'
}

const closeDrawer = () => {
  drawerVisible.value = false
  setTimeout(() => resetForm(), 300)
}

const resetForm = () => {
  formData.id = undefined
  formData.label = ''
  formData.nav_type = ''
  formData.type = ''
  formData.value = ''
  formRef.value?.resetFields()
}

const handleEdit = (item: NavbarItem) => {
  isEditing.value = true
  formData.id = item.id
  formData.label = item.label
  formData.nav_type = item.nav_type
  formData.type = item.type
  formData.value = item.value
  drawerVisible.value = true
}

const handleDelete = (item: NavbarItem) => {
  deleteNav(Number(item.id))
    .then(() => {
      navbarItems.value = navbarItems.value.filter((i) => i.id !== item.id)
      ElMessage.success(t('admin.navbar.action.delete.success'))
      setSort()
    })
    .catch((err) => {
      console.error(t('admin.navbar.action.delete.error'), err)
      ElMessage.error(t('admin.navbar.action.delete.error'))
    })
}

const handleTypeChange = () => {
  formData.value = ''
}

const submitForm = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    if (!formData.type) {
      ElMessage.error(t('admin.navbar.validation.type'))
      return
    }

    if (isEditing.value && formData.id) {
      // Update existing item
      const index = navbarItems.value.findIndex((i) => i.id === formData.id)
      if (index !== -1) {
        const updatedItem = {
          ...navbarItems.value[index],
          id: Number(formData.id),
          label: formData.label,
          nav_type: formData.nav_type,
          type: formData.type!,
          value: formData.value
          //valueLabel: getValueLabel(formData.type!, formData.value)
        }
        updateNav(updatedItem)
          .then((res) => {
            const updatedItem2 = {
              id: res.data.id,
              label: res.data.label,
              nav_type: res.data.nav_type,
              type: res.data.type,
              value: res.data.value,
              valueLabel: getValueLabel(res.data.type!, res.data.value)
            }
            navbarItems.value.splice(index, 1, updatedItem2)
            ElMessage.success(t('admin.navbar.action.update.navbar.success'))
            setSort()
          })
          .catch((err) => {
            console.error(t('admin.navbar.action.update.navbar.error'), err)
            ElMessage.error(t('admin.navbar.action.update.navbar.error'))
          })
      }
    } else {
      // Create new item
      const newItem = {
        //id: Date.now().toString(),
        label: formData.label,
        type: formData.type!,
        value: formData.value
        //valueLabel: getValueLabel(formData.type!, formData.value)
      }
      createNav(newItem)
        .then((res) => {
          const newItem2 = {
            id: res.data.id,
            label: res.data.label,
            nav_type: res.data.nav_type,
            type: res.data.type,
            value: res.data.value,
            valueLabel: getValueLabel(res.data.type!, res.data.value)
          }
          navbarItems.value.push(newItem2)
          ElMessage.success(t('admin.navbar.action.create.navbar.success'))
          setSort()
        })
        .catch((err) => {
          console.error(t('admin.navbar.action.create.navbar.error'), err)
          ElMessage.error(t('admin.navbar.action.create.navbar.error'))
        })
    }

    closeDrawer()
  } catch (error) {
    // Validation failed
    console.error('Validation failed:', error)
  }
}

// Helper functions
const formatType = (type: string) => {
  return type.charAt(0).toUpperCase() + type.slice(1)
}

const getValueLabel = (type: string, value: string) => {
  if (type === 'page') {
    const page = availablePages.value.find((p) => p.id === value)
    return page?.title || value
  } else if (type === 'series') {
    const series = availableSeries.value.find((s) => s.id === value)
    return series?.name || value
  } else if (type === 'doc') {
    const docBook = availableDocBooks.value.find((d) => String(d.id) === value)
    return docBook ? `${docBook.name} (${docBook.slug})` : value
  }
  return ''
}

// Empty state methods
const getEmptyStateIcon = () => {
  return h(Menu, { class: 'empty-icon' })
}

const getEmptyStateTitle = () => {
  return t('admin.navbar.empty.title')
}

const getEmptyStateDescription = () => {
  return t('admin.navbar.empty.description')
}
</script>

<style scoped lang="scss">
.navbar-management-container {
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

.navbar-table-container {
  width: 100%;
  display: flex;
  justify-content: center;
}

.navbar-table {
  width: 80%;
  margin-bottom: 80px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

:global(.allow-drag) {
  cursor: move;
}

.action-button {
  padding: 0;
}

.link-value {
  color: #3b82f6;
  text-decoration: underline;
}

.page-series-value {
  color: #1f2937;
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

.add-button {
  padding: 10px 20px;
  font-size: 14px;
}

.navbar-form {
  margin-bottom: 30px;
}

.form-input,
.form-select {
  width: 100%;
}

.drawer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

@media screen and (max-width: 1080px) {
  .navbar-table {
    width: 100%;
  }
}

/* 移动端适配 */
@media (max-width: 767px) {
  .navbar-management-container {
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

  .add-button {
    width: 100%;
  }

  /* 导航卡片样式 */
  .navbar-cards {
    display: flex;
    flex-direction: column;
    gap: 12px;
    width: 100%;
  }

  .navbar-card {
    margin: 0;
    width: 100%;
  }

  .navbar-card .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    margin-bottom: 12px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--el-border-color-lighter);
  }

  .navbar-card .drag-handle {
    cursor: move;
    color: var(--el-text-color-secondary);
    font-size: 20px;
  }

  .navbar-card .card-body {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .navbar-card .info-row {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    font-size: 13px;
  }

  .navbar-card .info-row .label {
    color: var(--el-text-color-secondary);
    min-width: 60px;
    flex-shrink: 0;
  }

  .navbar-card .info-row .value {
    color: var(--el-text-color-regular);
    word-break: break-all;
    flex: 1;
  }

  .navbar-card .card-footer {
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid var(--el-border-color-lighter);
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }

  .navbar-card .card-footer .el-button {
    flex: 1;
    min-width: 80px;
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

  /* 抽屉表单优化 */
  .navbar-form :deep(.el-form-item__label) {
    text-align: left;
  }

  .navbar-form :deep(.el-input),
  .navbar-form :deep(.el-select) {
    width: 100%;
  }

  .drawer-actions {
    flex-direction: column;
  }

  .drawer-actions .el-button {
    width: 100%;
  }
}
</style>
