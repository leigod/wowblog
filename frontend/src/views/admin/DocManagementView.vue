<template>
  <div class="doc-management">
    <div class="page-header">
      <div class="header-left">
        <el-button link @click="handleBack">
          <el-icon>
            <ArrowLeft />
          </el-icon> {{ t('admin.doc.back_to_list') }}
        </el-button>
        <h1>{{ docbook?.name }} - {{ t('admin.doc.title') }}</h1>
        <p v-if="docbook?.description">{{ docbook.description }}</p>
      </div>
      <div class="header-right">
        <el-button type="primary" icon="Plus" @click="handleCreate">
          {{ t('admin.doc.btn_create') }}
        </el-button>
      </div>
    </div>

    <!-- 状态标签 -->
    <el-tabs v-model="activeStatus" class="status-tabs" @tab-click="handleStatusChange">
      <el-tab-pane :label="t('admin.doc.status_tabs.all')" name="" />
      <el-tab-pane :label="t('admin.doc.status_tabs.published')" name="published" />
      <el-tab-pane :label="t('admin.doc.status_tabs.draft')" name="draft" />
      <el-tab-pane :label="t('admin.doc.status_tabs.hidden')" name="hidden" />
    </el-tabs>

    <!-- 操作栏 -->
    <div class="action-bar">
      <el-input v-model="searchKeyword" :placeholder="t('admin.doc.search_placeholder')" prefix-icon="Search"
        class="search-input" @input="handleSearch" />
      <el-select v-model="selectedParent" :placeholder="t('admin.doc.filter_parent_placeholder')" clearable
        class="filter-select">
        <el-option :label="t('admin.doc.filter_parent_all')" :value="0" />
        <el-option v-for="doc in flatDocList" :key="doc.id" :label="getIndentTitle(doc)" :value="doc.id" />
      </el-select>
    </div>

    <!-- 桌面端文档树形表格 -->
    <el-table v-if="!isMobile" :data="docs" class="docs-table" row-key="id"
      :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
      :header-cell-style="{ backgroundColor: '#fafafa', fontWeight: 600 }" v-loading="loading">
      <template #empty>
        <div class="empty-state">
          <el-icon class="empty-icon">
            <Document />
          </el-icon>
          <h3>{{ t('admin.doc.empty.title') }}</h3>
          <p>{{ t('admin.doc.empty.description') }}</p>
        </div>
      </template>

      <el-table-column prop="title" :label="t('admin.doc.table.title')" min-width="250">
        <template #default="scope">
          <span class="title-text">{{ scope.row.title }}</span>
          <el-tag v-if="scope.row.status === 'published'" type="success" size="small" style="margin-left: 8px;">
            {{ t('admin.doc.status.published') }}
          </el-tag>
          <el-tag v-else-if="scope.row.status === 'draft'" type="info" size="small" style="margin-left: 8px;">
            {{ t('admin.doc.status.draft') }}
          </el-tag>
          <el-tag v-else type="warning" size="small" style="margin-left: 8px;">{{ t('admin.doc.status.hidden')
            }}</el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="slug" :label="t('admin.doc.table.slug')" width="180">
        <template #default="scope">
          <span class="slug-text">/{{ scope.row.slug }}</span>
        </template>
      </el-table-column>

      <el-table-column prop="level" :label="t('admin.doc.table.level')" width="80" align="center">
        <template #default="scope">
          <el-tag size="small">{{ t('admin.doc.level_label') }}{{ scope.row.level }}</el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="sort_order" :label="t('admin.doc.table.sort_order')" width="80" align="center">
        <template #default="scope">
          {{ scope.row.sort_order }}
        </template>
      </el-table-column>

      <el-table-column prop="view_count" :label="t('admin.doc.table.view_count')" width="80" align="center">
        <template #default="scope">
          <span>{{ scope.row.view_count }}</span>
        </template>
      </el-table-column>

      <el-table-column prop="comment_count" :label="t('admin.doc.table.comment_count')" width="80" align="center">
        <template #default="scope">
          <span>{{ scope.row.comment_count }}</span>
        </template>
      </el-table-column>

      <el-table-column prop="updatetime" :label="t('admin.doc.table.update_time')" width="160">
        <template #default="scope">
          {{ formatDateTime(scope.row.updatetime) }}
        </template>
      </el-table-column>

      <el-table-column :label="t('admin.doc.table.actions')" width="200" fixed="right">
        <template #default="scope">
          <el-tooltip placement="bottom" :content="t('admin.doc.actions.view')">
            <el-button circle type="default" @click="handleView(scope.row)">
              <IconifyIcon icon="pepicons-pencil:open" width="20" height="20" stroke-width="0.1" />
            </el-button>
          </el-tooltip>

          <el-tooltip placement="bottom" :content="t('admin.doc.actions.edit')">
            <el-button circle type="default" @click="handleEdit(scope.row)">
              <el-icon>
                <Edit></Edit>
              </el-icon>
            </el-button>
          </el-tooltip>

          <el-tooltip placement="bottom" :content="t('admin.doc.actions.delete')">
            <el-button circle type="default" @click="handleDelete(scope.row)">
              <el-icon>
                <Delete></Delete>
              </el-icon>
            </el-button>
          </el-tooltip>
        </template>
      </el-table-column>
    </el-table>

    <!-- 移动端文档卡片布局 -->
    <div v-else class="docs-cards" v-loading="loading">
      <div v-if="docs.length === 0" class="empty-state">
        <el-icon class="empty-icon">
          <Document />
        </el-icon>
        <h3>{{ t('admin.doc.empty.title') }}</h3>
        <p>{{ t('admin.doc.empty.description') }}</p>
      </div>
      <template v-for="doc in docs" :key="doc.id">
        <el-card class="doc-card" shadow="hover">
          <div class="card-header">
            <div class="card-title">
              <div class="title-text">{{ doc.title }}</div>
              <el-tag v-if="doc.status === 'published'" type="success" size="small">
                {{ t('admin.doc.status.published') }}
              </el-tag>
              <el-tag v-else-if="doc.status === 'draft'" type="info" size="small">
                {{ t('admin.doc.status.draft') }}
              </el-tag>
              <el-tag v-else type="warning" size="small">{{ t('admin.doc.status.hidden') }}</el-tag>
            </div>
          </div>
          <div class="card-body">
            <div class="card-info-row">
              <span class="label">{{ t('admin.doc.table.slug') }}:</span>
              <span class="slug-text">/{{ doc.slug }}</span>
            </div>
            <div class="card-info-row">
              <span class="label">{{ t('admin.doc.table.level') }}:</span>
              <el-tag size="small">{{ t('admin.doc.level_label') }}{{ doc.level }}</el-tag>
            </div>
            <div class="card-info-row">
              <span class="label">{{ t('admin.doc.table.sort_order') }}:</span>
              <span>{{ doc.sort_order }}</span>
            </div>
            <div class="card-info-row">
              <span class="label">{{ t('admin.doc.table.view_count') }}:</span>
              <span>{{ doc.view_count }}</span>
            </div>
            <div class="card-info-row">
              <span class="label">{{ t('admin.doc.table.comment_count') }}:</span>
              <span>{{ doc.comment_count }}</span>
            </div>
            <div class="card-info-row">
              <span class="label">{{ t('admin.doc.table.update_time') }}:</span>
              <span class="time-text">{{ formatDateTime(doc.updatetime) }}</span>
            </div>
          </div>
          <div class="card-footer">
            <el-button size="small" @click="handleView(doc)">
              {{ t('admin.doc.actions.view') }}
            </el-button>
            <el-button size="small" type="primary" @click="handleEdit(doc)">
              {{ t('admin.doc.actions.edit') }}
            </el-button>
            <el-button size="small" type="danger" @click="handleDelete(doc)">
              {{ t('admin.doc.actions.delete') }}
            </el-button>
          </div>
        </el-card>
        <!-- 递归渲染子文档 -->
        <template v-if="doc.children && doc.children.length > 0">
          <template v-for="childDoc in doc.children" :key="childDoc.id">
            <el-card class="doc-card child-card" shadow="hover">
              <div class="card-header">
                <div class="card-title">
                  <div class="title-text">{{ '　'.repeat(childDoc.level - 1) }}{{ childDoc.title }}</div>
                  <el-tag v-if="childDoc.status === 'published'" type="success" size="small">
                    {{ t('admin.doc.status.published') }}
                  </el-tag>
                  <el-tag v-else-if="childDoc.status === 'draft'" type="info" size="small">
                    {{ t('admin.doc.status.draft') }}
                  </el-tag>
                  <el-tag v-else type="warning" size="small">{{ t('admin.doc.status.hidden') }}</el-tag>
                </div>
              </div>
              <div class="card-body">
                <div class="card-info-row">
                  <span class="label">{{ t('admin.doc.table.slug') }}:</span>
                  <span class="slug-text">/{{ childDoc.slug }}</span>
                </div>
                <div class="card-info-row">
                  <span class="label">{{ t('admin.doc.table.level') }}:</span>
                  <el-tag size="small">{{ t('admin.doc.level_label') }}{{ childDoc.level }}</el-tag>
                </div>
                <div class="card-info-row">
                  <span class="label">{{ t('admin.doc.table.sort_order') }}:</span>
                  <span>{{ childDoc.sort_order }}</span>
                </div>
                <div class="card-info-row">
                  <span class="label">{{ t('admin.doc.table.view_count') }}:</span>
                  <span>{{ childDoc.view_count }}</span>
                </div>
                <div class="card-info-row">
                  <span class="label">{{ t('admin.doc.table.comment_count') }}:</span>
                  <span>{{ childDoc.comment_count }}</span>
                </div>
                <div class="card-info-row">
                  <span class="label">{{ t('admin.doc.table.update_time') }}:</span>
                  <span class="time-text">{{ formatDateTime(childDoc.updatetime) }}</span>
                </div>
              </div>
              <div class="card-footer">
                <el-button size="small" @click="handleView(childDoc)">
                  {{ t('admin.doc.actions.view') }}
                </el-button>
                <el-button size="small" type="primary" @click="handleEdit(childDoc)">
                  {{ t('admin.doc.actions.edit') }}
                </el-button>
                <el-button size="small" type="danger" @click="handleDelete(childDoc)">
                  {{ t('admin.doc.actions.delete') }}
                </el-button>
              </div>
            </el-card>
          </template>
        </template>
      </template>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrapper">
      <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total"
        :page-sizes="[10, 20, 50, 100]" layout="total, sizes, prev, pager, next, jumper" @current-change="loadData"
        @size-change="loadData" />
    </div>

    <!-- 创建/编辑对话框 -->
    <el-dialog v-model="showEditDialog"
      :title="editingDoc ? t('admin.doc.dialog.edit_title') : t('admin.doc.dialog.create_title')"
      :width="isMobile ? '95%' : '900px'" :close-on-click-modal="false">
      <el-form ref="formRef" :model="formData" :rules="formRules" :label-width="isMobile ? 'auto' : '100px'"
        :label-position="isMobile ? 'top' : 'right'">
        <el-row :gutter="20">
          <el-col :span="isMobile ? 24 : 12">
            <el-form-item :label="t('admin.doc.dialog.form.title')" prop="title">
              <el-input v-model="formData.title" :placeholder="t('admin.doc.dialog.form.title_placeholder')" />
            </el-form-item>
          </el-col>
          <el-col :span="isMobile ? 24 : 12">
            <el-form-item :label="t('admin.doc.dialog.form.slug')" prop="slug">
              <el-input v-model="formData.slug" :placeholder="t('admin.doc.dialog.form.slug_placeholder')">
                <template #prepend>{{ docbook?.slug }}/</template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="isMobile ? 24 : 12">
            <el-form-item :label="t('admin.doc.dialog.form.parent')">
              <el-tree-select v-model="formData.parent_id" :data="docTreeData" :render-after-expand="false"
                :default-expand-all="true" :check-strictly="true" :props="{
                  label: 'label',
                  value: 'value',
                  children: 'children'
                }" :placeholder="t('admin.doc.parent_select_placeholder')" clearable />
            </el-form-item>
          </el-col>
          <el-col :span="isMobile ? 24 : 6">
            <el-form-item :label="t('admin.doc.dialog.form.sort_order')">
              <el-input-number v-model="formData.sort_order" :min="0" />
            </el-form-item>
          </el-col>
          <el-col :span="isMobile ? 24 : 6">
            <el-form-item :label="t('admin.doc.dialog.form.status')">
              <el-select v-model="formData.status" style="width: 100%">
                <el-option :label="t('admin.doc.status.draft')" value="draft" />
                <el-option :label="t('admin.doc.status.published')" value="published" />
                <el-option :label="t('admin.doc.status.hidden')" value="hidden" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item :label="t('admin.doc.dialog.form.excerpt')">
          <el-input v-model="formData.excerpt" type="textarea" :rows="2"
            :placeholder="t('admin.doc.dialog.form.excerpt_placeholder')" />
        </el-form-item>

        <el-form-item :label="t('admin.doc.dialog.form.content')">
          <MarkdownEditor v-model="formData.content" :placeholder="t('admin.doc.dialog.form.content_placeholder')" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showEditDialog = false">{{ t('admin.doc.dialog.btn_cancel') }}</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ t('admin.doc.dialog.btn_confirm') }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { ArrowLeft, Document, Edit } from '@element-plus/icons-vue'
import { docApi, docBookApi, type Doc, type DocBook, type DocCreate, type DocUpdate, type DocStatus } from '@/api'
import MarkdownEditor from '@/components/MarkdownEditor.vue'
import { useMobileDetection } from '@/composables/useMobileDetection'
import IconifyIcon from '@/components/IconIfy.vue'

const router = useRouter()
const route = useRoute()
const { t } = useI18n()
const { isMobile } = useMobileDetection()

const docbookId = computed(() => parseInt(route.params.docbookId as string))

// 状态
const loading = ref(false)
const docbook = ref<DocBook | null>(null)
const docs = ref<Doc[]>([])
const flatDocList = ref<Doc[]>([])
const docTreeData = ref<any[]>([
  { value: 0, label: t('admin.doc.top_level_doc'), children: [] }
])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(50)
const searchKeyword = ref('')
const activeStatus = ref<DocStatus | ''>('')
const selectedParent = ref<number | null>(null)

const showEditDialog = ref(false)
const editingDoc = ref<Doc | null>(null)
const submitting = ref(false)

const formRef = ref<FormInstance>()
const formData = reactive<Omit<DocCreate, 'content' | 'excerpt'> & { content: string; excerpt: string }>({
  docbook_id: docbookId.value,
  title: '',
  slug: '',
  content: '',
  excerpt: '',
  parent_id: 0,
  sort_order: 0,
  status: 'draft'
})

const formRules: FormRules = {
  title: [
    { required: true, message: t('admin.doc.validation.title_required'), trigger: 'blur' },
    { max: 255, message: t('admin.doc.validation.title_too_long'), trigger: 'blur' }
  ],
  slug: [
    { required: true, message: t('admin.doc.validation.slug_required'), trigger: 'blur' },
    { max: 255, message: t('admin.doc.validation.slug_too_long'), trigger: 'blur' },
    { pattern: /^[a-z0-9-]+$/, message: t('admin.doc.validation.slug_invalid'), trigger: 'blur' }
  ]
}

// 格式化时间
const formatDateTime = (timestamp: number) => {
  const date = new Date(timestamp * 1000)
  return date.toLocaleString('zh-CN')
}

// 获取缩进标题
const getIndentTitle = (doc: Doc) => {
  return '  '.repeat(doc.level - 1) + doc.title
}

// 构建树形选择器数据（直接使用 API 返回的树形结构）
const buildDocTreeData = (treeNodes: any[]) => {
  console.log('buildDocTreeData input:', treeNodes)

  const convertToTreeSelect = (nodes: any[]): any[] => {
    if (!nodes || nodes.length === 0) return []
    return nodes.map(node => ({
      value: node.id,
      label: node.title,
      children: node.children && node.children.length > 0
        ? convertToTreeSelect(node.children)
        : undefined
    }))
  }

  const tree = convertToTreeSelect(treeNodes)
  docTreeData.value = [
    { value: 0, label: t('admin.doc.top_level_doc'), children: [] },
    ...tree
  ]
  console.log('docTreeData after build:', JSON.stringify(docTreeData.value, null, 2))
}


// 构建树形结构
const buildTree = (flatList: Doc[]): Doc[] => {
  const map = new Map<number, Doc>()
  const roots: Doc[] = []

  // 先创建所有节点的副本
  flatList.forEach(doc => {
    map.set(doc.id, { ...doc, children: [] })
  })

  // 构建树
  flatList.forEach(doc => {
    const node = map.get(doc.id)!
    if (doc.parent_id === 0 || !map.has(doc.parent_id)) {
      roots.push(node)
    } else {
      const parent = map.get(doc.parent_id)!
      if (!parent.children) parent.children = []
      parent.children.push(node)
    }
  })

  return roots
}

// 加载文档书
const loadDocBook = async () => {
  try {
    const response = await docBookApi.getById(docbookId.value)
    if (response.data) {
      docbook.value = response.data
    } else {
      ElMessage.error(t('admin.doc.message.docbook_not_found'))
      handleBack()
    }
  } catch (error) {
    ElMessage.error(t('admin.doc.message.load_docbook_failed'))
    handleBack()
  }
}

// 加载文档列表
const loadData = async () => {
  if (!docbookId.value) return

  loading.value = true
  try {
    // 获取文档树用于筛选（无分页限制，包含草稿状态）
    const treeResponse = await docApi.getTree(docbookId.value, true)
    console.log('treeResponse:', treeResponse)
    if (treeResponse.data) {
      console.log('treeResponse.data:', treeResponse.data)
      // 展平树形结构
      const flatten = (nodes: any[]): any[] => {
        const result: any[] = []
        nodes.forEach(node => {
          result.push(node)
          if (node.children && node.children.length > 0) {
            result.push(...flatten(node.children))
          }
        })
        return result
      }
      flatDocList.value = flatten(treeResponse.data)
      // 构建树形选择器数据（直接使用原始树形数据）
      buildDocTreeData(treeResponse.data)
    } else {
      console.warn('treeResponse.data is empty')
    }

    // 获取当前页文档
    const response = await docApi.list({
      docbook_id: docbookId.value,
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
      keyword: searchKeyword.value,
      status: activeStatus.value || undefined
    })

    if (response.data) {
      // 构建树形结构
      docs.value = buildTree(response.data)

      // 获取总数
      const countRes = await docApi.count({
        docbook_id: docbookId.value,
        keyword: searchKeyword.value,
        status: activeStatus.value || undefined
      })
      if (countRes.data) {
        total.value = countRes.data.total
      }
    }
  } catch (error) {
    ElMessage.error(t('admin.doc.message.load_failed'))
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  loadData()
}

// 状态切换
const handleStatusChange = () => {
  currentPage.value = 1
  loadData()
}

// 返回
const handleBack = () => {
  router.push({ name: 'admin-docbooks' })
}

// 创建
const handleCreate = () => {
  console.log('handleCreate - docTreeData:', docTreeData.value)
  console.log('handleCreate - flatDocList:', flatDocList.value)
  editingDoc.value = null
  Object.assign(formData, {
    docbook_id: docbookId.value,
    title: '',
    slug: '',
    content: '',
    excerpt: '',
    parent_id: 0,
    sort_order: 0,
    status: 'draft'
  })
  showEditDialog.value = true
}

// 编辑
const handleEdit = (doc: Doc) => {
  editingDoc.value = doc
  Object.assign(formData, {
    docbook_id: doc.docbook_id,
    title: doc.title,
    slug: doc.slug,
    content: doc.content || '',
    excerpt: doc.excerpt || '',
    parent_id: doc.parent_id,
    sort_order: doc.sort_order,
    status: doc.status
  })
  showEditDialog.value = true
  // 等待 DOM 更新后清除表单验证状态
  nextTick(() => {
    formRef.value?.clearValidate()
  })
}

// 查看
const handleView = (doc: Doc) => {
  const url = `/docs/${docbook.value?.slug}/${doc.slug}`
  window.open(url, '_blank')
}

// 删除
const handleDelete = async (doc: Doc) => {
  try {
    const hasChildren = doc.children?.length ? t('admin.doc.confirm_delete.has_children') : ''
    await ElMessageBox.confirm(
      t('admin.doc.confirm_delete.message', { title: doc.title, hasChildren }),
      t('admin.doc.confirm_delete.title'),
      {
        type: 'warning',
        confirmButtonText: t('admin.doc.confirm_delete.confirm_btn'),
        cancelButtonText: t('admin.doc.confirm_delete.cancel_btn')
      }
    )

    await docApi.delete(doc.id)
    ElMessage.success(t('admin.doc.message.delete_success'))
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(t('admin.doc.message.delete_failed'))
    }
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
  } catch {
    return
  }

  submitting.value = true
  try {
    console.log('提交表单数据:', JSON.parse(JSON.stringify(formData)))
    if (editingDoc.value) {
      const updateData: DocUpdate = {
        title: formData.title,
        slug: formData.slug,
        content: formData.content,
        excerpt: formData.excerpt,
        parent_id: formData.parent_id,
        sort_order: formData.sort_order,
        status: formData.status
      }
      console.log('更新数据:', updateData)
      const result = await docApi.update(editingDoc.value.id, updateData)
      console.log('更新结果:', result)
      ElMessage.success(t('admin.doc.message.update_success'))
    } else {
      const createData = { ...formData }
      console.log('创建数据:', createData)
      const result = await docApi.create(createData)
      console.log('创建结果:', result)
      ElMessage.success(t('admin.doc.message.create_success'))
    }
    showEditDialog.value = false
    await loadData()
    console.log('重新加载数据完成')
  } catch (error: any) {
    console.error('提交错误:', error)
    ElMessage.error(error.response?.data?.detail || t('admin.doc.message.operation_failed'))
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  await loadDocBook()
  loadData()
})

// 监听 parent_id 变化
watch(() => formData.parent_id, (newVal) => {
  console.log('parent_id changed to:', newVal, 'type:', typeof newVal)
})
</script>

<style scoped>
.doc-management {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.header-left h1 {
  margin: 8px 0;
  font-size: 24px;
}

.header-left p {
  margin: 0;
  color: var(--el-text-color-secondary);
}

.status-tabs {
  margin-bottom: 16px;
}

.action-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.search-input {
  flex: 1;
  max-width: 300px;
}

.filter-select {
  width: 200px;
}

.docs-table {
  margin-bottom: 20px;
}

.title-text {
  font-weight: 500;
}

.slug-text {
  font-family: monospace;
  color: var(--el-text-color-secondary);
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  color: var(--el-text-color-placeholder);
  margin-bottom: 16px;
}

.empty-state h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
}

.empty-state p {
  margin: 0;
  color: var(--el-text-color-secondary);
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
}

/* 移动端样式 */
@media (max-width: 767px) {
  .doc-management {
    padding: 12px;
  }

  .page-header {
    flex-direction: column;
    gap: 12px;
  }

  .header-left h1 {
    font-size: 18px;
    margin: 4px 0;
  }

  .header-left p {
    font-size: 12px;
  }

  .header-right .el-button {
    width: 100%;
  }

  .status-tabs {
    margin-bottom: 12px;
  }

  .action-bar {
    flex-direction: column;
    gap: 8px;
  }

  .search-input {
    max-width: 100%;
  }

  .filter-select {
    width: 100%;
  }

  /* 卡片布局样式 */
  .docs-cards {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-bottom: 20px;
  }

  .doc-card {
    margin: 0;
  }

  .child-card {
    margin-left: 16px;
  }

  .doc-card .card-header {
    margin-bottom: 12px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--el-border-color-lighter);
  }

  .card-title {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }

  .card-title .title-text {
    font-weight: 500;
    font-size: 14px;
  }

  .card-body {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 12px;
  }

  .card-info-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 13px;
  }

  .card-info-row .label {
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }

  .card-info-row .slug-text {
    font-family: monospace;
    font-size: 11px;
    color: var(--el-text-color-secondary);
  }

  .card-info-row .time-text {
    font-size: 11px;
    color: var(--el-text-color-placeholder);
  }

  .card-footer {
    display: flex;
    gap: 8px;
    padding-top: 12px;
    border-top: 1px solid var(--el-border-color-lighter);
  }

  .card-footer .el-button {
    flex: 1;
  }

  /* 空状态优化 */
  .empty-state {
    padding: 40px 16px;
  }

  .empty-icon {
    font-size: 48px;
  }

  .empty-state h3 {
    font-size: 14px;
  }

  .empty-state p {
    font-size: 12px;
  }

  /* 分页优化 */
  .pagination-wrapper {
    flex-wrap: wrap;
  }

  .pagination-wrapper :deep(.el-pagination) {
    flex-wrap: wrap;
    justify-content: center;
  }

  /* 对话框表单优化 */
  .el-dialog :deep(.el-form-item__content) {
    width: 100% !important;
  }

  .el-dialog :deep(.el-input-number) {
    width: 100%;
  }

  .el-dialog :deep(.el-select) {
    width: 100%;
  }

  .el-dialog :deep(.el-tree-select) {
    width: 100%;
  }
}
</style>
