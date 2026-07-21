<template>
  <div class="member-management-container">
    <div class="page-header">
      <h1>{{ t('admin.members.title') }}</h1>
      <p>{{ t('admin.members.title_info') }}</p>
    </div>

    <el-divider></el-divider>

    <div class="manage-members-section">
      <div class="section-header">
        <h2 class="section-title">{{ t('admin.members.section.manage_members') }}</h2>
        <div class="header-actions">
          <el-button type="default" class="role-definition-btn" @click="handleRoleDefinitionClick">{{
            t('admin.members.btn.role_definition') }}</el-button>
          <el-button type="primary" class="invite-member-btn" @click="inviteDrawerVisible = true">
            <el-icon>
              <UserFilled />
            </el-icon> {{ t('admin.members.btn.invite_member') }}
          </el-button>
          <el-button type="primary" class="invite-member-btn" @click="handleAddMemberClick">
            <el-icon>
              <Plus />
            </el-icon>
            {{ t('admin.members.btn.add_member') }}
          </el-button>
        </div>
      </div>

      <div class="tabs-container">
        <el-tabs v-model="activeTab" type="border-card">
          <el-tab-pane :label="t('admin.members.tabs.team_members', { count: filteredMembers.length })" name="teamMembers">
            <div class="search-container">
              <el-input v-model="searchKeyword" :placeholder="t('admin.members.search.placeholder')" clearable
                class="search-input">
                <template #prefix>
                  <el-icon>
                    <Search />
                  </el-icon>
                </template>
              </el-input>
            </div>

            <div class="members-table-container">
              <!-- 桌面端表格 -->
              <el-table v-if="!isMobile" :data="filteredMembers" class="members-table" border>
                <el-table-column prop="name" :label="t('admin.members.table.name')" width="250">
                  <template #default="{ row }">
                    <div class="member-info">
                      <img :src="row.avatar" alt="Avatar" class="member-avatar" />
                      <div class="member-details">
                        <div class="member-name">{{ row.name }}</div>
                        <div class="member-email">@{{ row.username }}</div>
                      </div>
                    </div>
                  </template>
                </el-table-column>

                <el-table-column prop="role" :label="t('admin.members.table.role')" width="150">
                  <template #default="{ row }">
                    <el-tag :class="`role-tag role-${row.role.toLowerCase()}`">
                      {{ t('admin.members.roles.' + row.role.toLowerCase() + '.name') }}
                    </el-tag>
                  </template>
                </el-table-column>

                <el-table-column prop="visibility" :label="t('admin.members.table.visibility')" width="150">
                  <template #default="{ row }">
                    <el-select v-model="row.visibility" size="small" @change="handleVisibilityChange(row)">
                      <el-option :label="t('admin.members.visibility.public')" value="Public"></el-option>
                      <el-option :label="t('admin.members.visibility.private')" value="Private"></el-option>
                    </el-select>
                  </template>
                </el-table-column>

                <el-table-column prop="status" :label="t('admin.members.table.status')" width="150">
                  <template #default="{ row }">
                    <el-select v-model="row.status" size="small" @change="handleStatusChange(row)">
                      <el-option :label="t('admin.members.status.normal')" value="normal"></el-option>
                      <el-option :label="t('admin.members.status.block')" value="block"></el-option>
                    </el-select>
                  </template>
                </el-table-column>

                <el-table-column :label="t('admin.members.table.actions')" width="100" fixed="right">
                  <template #default="{ row }">
                    <el-dropdown trigger="click" @command="handleDropdownCommand(row, $event)">
                      <el-button link type="primary" size="large" class="more-actions-btn" circle>
                        <el-icon>
                          <More />
                        </el-icon>
                      </el-button>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item command="viewRole"><span
                              style="margin-left: -2px; margin-right: 2px; line-height: 12px">
                              <IconifyIcon icon="pepicons-pencil:open" width="20" height="20" stroke-width="0.1" />
                            </span>
                            {{ t('admin.general.btn.view') }}
                          </el-dropdown-item>
                          <el-dropdown-item command="editRole" v-if="row.id != 1"><el-icon>
                              <Edit />
                            </el-icon>
                            {{ t('admin.general.btn.edit') }}</el-dropdown-item>
                          <el-dropdown-item command="deleteRole" v-if="row.id != 1"><el-icon>
                              <Delete />
                            </el-icon>
                            {{ t('admin.general.btn.delete') }}</el-dropdown-item>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </template>
                </el-table-column>
              </el-table>

              <!-- 移动端卡片布局 -->
              <div v-else class="members-cards-container">
                <div v-for="member in filteredMembers" :key="member.id" class="member-card">
                  <div class="member-card-header">
                    <img :src="member.avatar" alt="Avatar" class="member-card-avatar" />
                    <div class="member-card-info">
                      <div class="member-card-name">{{ member.name }}</div>
                      <div class="member-card-email">@{{ member.username }}</div>
                    </div>
                  </div>
                  <div class="member-card-body">
                    <div class="member-card-row">
                      <span class="member-card-label">{{ t('admin.members.table.role') }}:</span>
                      <el-tag :class="`role-tag role-${member.role.toLowerCase()}`" size="small">
                        {{ t('admin.members.roles.' + member.role.toLowerCase() + '.name') }}
                      </el-tag>
                    </div>
                    <div class="member-card-row">
                      <span class="member-card-label">{{ t('admin.members.table.visibility') }}:</span>
                      <el-select v-model="member.visibility" size="small" @change="handleVisibilityChange(member)">
                        <el-option :label="t('admin.members.visibility.public')" value="Public"></el-option>
                        <el-option :label="t('admin.members.visibility.private')" value="Private"></el-option>
                      </el-select>
                    </div>
                    <div class="member-card-row">
                      <span class="member-card-label">{{ t('admin.members.table.status') }}:</span>
                      <el-select v-model="member.status" size="small" @change="handleStatusChange(member)">
                        <el-option :label="t('admin.members.status.normal')" value="normal"></el-option>
                        <el-option :label="t('admin.members.status.block')" value="block"></el-option>
                      </el-select>
                    </div>
                  </div>
                  <div class="member-card-footer">
                    <el-button size="small" @click="handleDropdownCommand(member, 'viewRole')">
                      <el-icon><IconifyIcon icon="pepicons-pencil:open" width="16" height="16" stroke-width="0.1" /></el-icon>
                      {{ t('admin.general.btn.view') }}
                    </el-button>
                    <el-button v-if="member.id != 1" size="small" @click="handleDropdownCommand(member, 'editRole')">
                      <el-icon><Edit /></el-icon>
                      {{ t('admin.general.btn.edit') }}
                    </el-button>
                    <el-button v-if="member.id != 1" size="small" type="danger" @click="handleDropdownCommand(member, 'deleteRole')">
                      <el-icon><Delete /></el-icon>
                      {{ t('admin.general.btn.delete') }}
                    </el-button>
                  </div>
                </div>
                <el-empty v-if="members.length === 0" />
              </div>
            </div>
          </el-tab-pane>
          <el-tab-pane :label="t('admin.members.tabs.pending_invites', { count: pendingCount })" name="pendingInvites">
            <div v-loading="loadingInvitations" class="invitations-container">
              <!-- 桌面端表格 -->
              <el-table v-if="!isMobile" :data="invitations" border>
                <el-table-column prop="email" :label="t('admin.members.invite.email_label')" width="250" />
                <el-table-column prop="role" :label="t('admin.members.form.role')" width="150">
                  <template #default="{ row }">
                    <el-tag :class="`role-tag role-${row.role.toLowerCase()}`">
                      {{ t(`admin.members.roles.${row.role.toLowerCase()}.name`) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="language" :label="t('admin.members.invite.language_label')" width="120">
                  <template #default="{ row }">
                    {{ row.language === 'zh-CN' ? '中文' : 'English' }}
                  </template>
                </el-table-column>
                <el-table-column prop="status" :label="t('admin.members.table.status')" width="120">
                  <template #default="{ row }">
                    <el-tag :type="getStatusType(row.status)">
                      {{ t(`admin.members.invite.status.${row.status.toLowerCase()}`) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="created_at" :label="t('admin.members.invite.created_at')" width="180">
                  <template #default="{ row }">
                    {{ formatDate(row.created_at) }}
                  </template>
                </el-table-column>
                <el-table-column prop="expires_at" :label="t('admin.members.invite.expires_at')" width="180">
                  <template #default="{ row }">
                    {{ formatDate(row.expires_at) }}
                  </template>
                </el-table-column>
                <el-table-column :label="t('admin.members.table.actions')" width="120" fixed="right">
                  <template #default="{ row }">
                    <div class="action-buttons">
                      <el-tooltip content="重新发送" placement="top">
                        <el-button v-if="row.status === 'pending'" circle @click="handleResendInvitation(row)">
                          <el-icon>
                            <Promotion />
                          </el-icon>
                        </el-button>
                      </el-tooltip>
                      <el-tooltip content="取消邀请" placement="top">
                        <el-button v-if="row.status === 'pending'" circle @click="handleCancelInvitation(row)">
                          <el-icon>
                            <Close />
                          </el-icon>
                        </el-button>
                      </el-tooltip>
                    </div>
                  </template>
                </el-table-column>
              </el-table>

              <!-- 移动端卡片布局 -->
              <div v-else class="invitations-cards-container">
                <div v-for="invitation in invitations" :key="invitation.id" class="invitation-card">
                  <div class="invitation-card-header">
                    <div class="invitation-card-email">{{ invitation.email }}</div>
                    <el-tag :type="getStatusType(invitation.status)" size="small">
                      {{ t(`admin.members.invite.status.${invitation.status.toLowerCase()}`) }}
                    </el-tag>
                  </div>
                  <div class="invitation-card-body">
                    <div class="invitation-card-row">
                      <span class="invitation-card-label">{{ t('admin.members.form.role') }}:</span>
                      <el-tag :class="`role-tag role-${invitation.role.toLowerCase()}`" size="small">
                        {{ t(`admin.members.roles.${invitation.role.toLowerCase()}.name`) }}
                      </el-tag>
                    </div>
                    <div class="invitation-card-row">
                      <span class="invitation-card-label">{{ t('admin.members.invite.language_label') }}:</span>
                      <span>{{ invitation.language === 'zh-CN' ? '中文' : 'English' }}</span>
                    </div>
                    <div class="invitation-card-row">
                      <span class="invitation-card-label">{{ t('admin.members.invite.created_at') }}:</span>
                      <span class="invitation-card-date">{{ formatDate(invitation.created_at) }}</span>
                    </div>
                    <div class="invitation-card-row">
                      <span class="invitation-card-label">{{ t('admin.members.invite.expires_at') }}:</span>
                      <span class="invitation-card-date">{{ formatDate(invitation.expires_at) }}</span>
                    </div>
                  </div>
                  <div class="invitation-card-footer" v-if="invitation.status === 'pending'">
                    <el-button size="small" @click="handleResendInvitation(invitation)">
                      <el-icon><Promotion /></el-icon>
                      {{ t('admin.members.invite.resend') }}
                    </el-button>
                    <el-button size="small" type="danger" @click="handleCancelInvitation(invitation)">
                      <el-icon><Close /></el-icon>
                      {{ t('admin.members.invite.cancel') }}
                    </el-button>
                  </div>
                </div>
                <el-empty v-if="!loadingInvitations && invitations.length === 0" />
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>

      <!-- 右侧抽屉面板，用于显示成员详情 -->
      <el-drawer v-model="drawerVisible" :size="isMobile ? '100%' : '30%'" placement="right" :title="t('admin.members.drawer.member_details')"
        :before-close="handleDrawerClose">
        <div v-if="selectedMember" class="member-detail-content">
          <div class="member-avatar-large">
            <img :src="selectedMember.avatar" alt="Avatar" />
          </div>
          <h3 class="member-name-large">{{ selectedMember.name }}</h3>
          <p class="member-email-large">@{{ selectedMember.username }}</p>

          <div class="detail-section">
            <h4>{{ t('admin.members.detail_section.role') }}</h4>
            <el-tag :class="`role-tag role-${selectedMember.role.toLowerCase()}`" size="large">
              {{ selectedMember.role }}
            </el-tag>
          </div>

          <div class="detail-section">
            <h4>{{ t('admin.members.detail_section.visibility') }}</h4>
            <span class="visibility-text">{{ selectedMember.visibility }}</span>
          </div>

          <div class="detail-section">
            <h4>{{ t('admin.members.detail_section.permissions') }}</h4>
            <div class="permissions-list">
              <div class="permission-item" v-for="perm in selectedMember.permissions" :key="perm">
                <el-icon>
                  <Check />
                </el-icon>
                <span>{{ perm }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-drawer>

      <!-- 角色定义抽屉面板 -->
      <el-drawer v-model="roleDefinitionDrawerVisible" :size="isMobile ? '100%' : '30%'" placement="right"
        :title="t('admin.members.drawer.role_definition')" :before-close="handleRoleDefinitionDrawerClose">
        <div class="role-definition-content">
          <div v-for="role in roles" :key="role.index" class="role-card">
            <div class="role-card-header">
              <div class="role-icon" :style="{ backgroundColor: role.color }">
                <i :class="role.icon"></i>
              </div>
              <h4 class="role-name">{{ role.name }}</h4>
            </div>
            <p class="role-description">{{ role.description }}</p>
            <div class="role-permissions">
              <span v-for="(permission, index) in role.permissions" :key="index" class="permission-badge">
                {{ permission }}
              </span>
            </div>
          </div>
        </div>
      </el-drawer>

      <!-- 添加成员抽屉 -->
      <el-drawer v-model="addMemberDrawerVisible" :title="isEditing ? t('admin.members.drawer.edit_title') : t('admin.members.drawer.create_title')
        " :before-close="handleAddMemberDrawerClose" :size="isMobile ? '100%' : '30%'">
        <div class="add-member-content">
          <el-form :model="newMemberForm" :rules="formRules" ref="memberFormRef" label-width="100px"
            label-position="top" size="large">
            <el-form-item :label="t('admin.members.form.username')" prop="username">
              <el-input v-model="newMemberForm.username" :placeholder="t('admin.members.form.username_placeholder')" />
            </el-form-item>

            <el-form-item :label="t('admin.members.form.full_name')" prop="fullName">
              <el-input v-model="newMemberForm.fullName" :placeholder="t('admin.members.form.full_name_placeholder')" />
            </el-form-item>

            <el-form-item :label="t('admin.members.form.profile_image')">
              <el-upload class="avatar-uploader" :show-file-list="false" accept="image/*"
                :http-request="handleCustomUpload" :before-upload="beforeUpload" :on-success="handleUploadSuccess"
                :on-error="handleUploadError">
                <template v-if="newMemberForm.profileImage">
                  <div class="cover-image-wrapper">
                    <img :src="newMemberForm.profileImage" alt="Profile Image" class="avatar" />
                    <el-button :icon="Delete" class="delete-cover-btn" @click="removeImage" />
                  </div>
                </template>
                <!-- <img
                  v-if="newMemberForm.profileImage"
                  :src="newMemberForm.profileImage"
                  class="avatar"
                /> -->
                <!-- <i v-else class="el-icon-plus avatar-uploader-icon"></i> -->
                <div v-else class="avatar-uploader-icon">
                  <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                </div>
              </el-upload>
            </el-form-item>

            <el-form-item :label="t('admin.members.form.gender')">
              <el-radio-group v-model="newMemberForm.gender">
                <el-radio label="male" value="male">{{ t('admin.members.gender.male') }}</el-radio>
                <el-radio label="female" value="female">{{
                  t('admin.members.gender.female')
                  }}</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item :label="t('admin.members.form.email')" prop="email">
              <el-input v-model="newMemberForm.email" :placeholder="t('admin.members.form.email_placeholder')" />
            </el-form-item>

            <el-form-item :label="t('admin.members.form.mobile')" prop="mobile">
              <el-input v-model="newMemberForm.mobile" :placeholder="t('admin.members.form.mobile_placeholder')" />
            </el-form-item>

            <el-form-item :label="t('admin.members.form.role')">
              <el-select v-model="newMemberForm.role" :placeholder="t('admin.members.form.role_placeholder')">
                <el-option v-for="role in roles" :key="role.index" :label="role.name" :value="role.index" />
              </el-select>
            </el-form-item>

            <el-form-item>
              <div style="display: flex; gap: 10px; justify-content: flex-end">
                <el-button @click="
                  handleAddMemberDrawerClose(() => {
                    addMemberDrawerVisible = false
                  })
                  " type="default">
                  {{ t('admin.general.btn.cancel') }}
                </el-button>
                <el-button @click="handleMemberSubmit" type="primary">
                  {{ isEditing ? t('admin.members.btn.update') : t('admin.members.btn.add') }}
                </el-button>
              </div>
            </el-form-item>
          </el-form>
        </div>
      </el-drawer>

      <!-- 邀请成员抽屉 -->
      <InviteDrawer v-model="inviteDrawerVisible" @success="handleInviteSuccess" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Search, UserFilled, More, Check, Plus, Delete, Promotion, Close, Edit } from '@element-plus/icons-vue'
import IconifyIcon from '@/components/IconIfy.vue'
import InviteDrawer from '@/components/InviteDrawer.vue'
import { useMobileDetection } from '@/composables/useMobileDetection'
import {
  ElTable,
  ElTableColumn,
  ElInput,
  ElButton,
  ElIcon,
  ElDropdown,
  ElDropdownMenu,
  ElDropdownItem,
  ElTag,
  ElSelect,
  ElOption,
  ElTabs,
  ElTabPane,
  ElDivider,
  ElDrawer,
  ElForm,
  ElFormItem,
  ElUpload,
  ElRadioGroup,
  ElRadio,
  ElMessage,
  ElMessageBox,
  ElEmpty
} from 'element-plus'
import {
  getManageMemberList,
  addManageMember,
  updateMemberVisible,
  updateMemberStatus,
  deleteMember,
  getMemberInfo,
  updateMember
} from '@/api/services/member'
import { uploadFile } from '@/api/services/common'
import {
  getInvitationList,
  resendInvitationEmail,
  cancelInvitation
} from '@/api/services/memberInvitations'

const { t } = useI18n()
const { isMobile, isDesktop } = useMobileDetection()

// 模拟成员数据
interface Member {
  id: number
  name: string
  username: string
  email: string
  avatar: string
  role: string
  status: string
  visibility: string
  permissions: string[]
}

// 角色定义接口
interface Role {
  index: string
  name: string
  description: string
  permissions: string[]
  color: string
  icon: string
}

const members = ref<Member[]>([])
const isEditing = ref(false)

// 角色定义数据（使用计算属性从i18n获取角色信息）
const roles = ref([
  {
    index: 'Admin',
    name: t('admin.members.roles.admin.name'),
    description: t('admin.members.roles.admin.description'),
    permissions: [
      t('admin.members.roles.admin.permissions1'),
      t('admin.members.roles.admin.permissions2'),
      t('admin.members.roles.admin.permissions3'),
      t('admin.members.roles.admin.permissions4')
    ],
    color: '#d97706',
    icon: 'el-icon-star-on'
  },
  {
    index: 'Editor',
    name: t('admin.members.roles.editor.name'),
    description: t('admin.members.roles.editor.description'),
    permissions: [
      t('admin.members.roles.editor.permissions1'),
      t('admin.members.roles.editor.permissions2'),
      t('admin.members.roles.editor.permissions3'),
      t('admin.members.roles.editor.permissions4')
    ],
    color: '#10b981',
    icon: 'el-icon-check'
  },
  {
    index: 'Author',
    name: t('admin.members.roles.author.name'),
    description: t('admin.members.roles.author.description'),
    permissions: [
      t('admin.members.roles.author.permissions1'),
      t('admin.members.roles.author.permissions2'),
      t('admin.members.roles.author.permissions3'),
      t('admin.members.roles.author.permissions4')
    ],
    color: '#8b5cf6',
    icon: 'el-icon-edit'
  },
  {
    index: 'Contributor',
    name: t('admin.members.roles.contributor.name'),
    description: t('admin.members.roles.contributor.description'),
    permissions: [
      t('admin.members.roles.contributor.permissions1'),
      t('admin.members.roles.contributor.permissions2'),
      t('admin.members.roles.contributor.permissions3'),
      t('admin.members.roles.contributor.permissions4')
    ],
    color: '#3b82f6',
    icon: 'el-icon-user'
  }
])

const searchKeyword = ref('')
const activeTab = ref('teamMembers')
const drawerVisible = ref(false)
const selectedMember = ref<Member | null>(null)
const roleDefinitionDrawerVisible = ref(false)
const addMemberDrawerVisible = ref(false)
const memberFormRef = ref()

// 计算过滤后的成员列表
const filteredMembers = computed(() => {
  if (!searchKeyword.value) {
    return members.value
  }
  const keyword = searchKeyword.value.toLowerCase()
  return members.value.filter(member => {
    const name = member.name || ''
    const username = member.username || ''
    const email = member.email || ''
    return (
      name.toLowerCase().includes(keyword) ||
      username.toLowerCase().includes(keyword) ||
      email.toLowerCase().includes(keyword)
    )
  })
})

// 邀请相关状态
const inviteDrawerVisible = ref(false)
const invitations = ref<any[]>([])
const loadingInvitations = ref(false)

// 新成员表单数据
const newMemberForm = ref({
  id: 0,
  username: '',
  fullName: '',
  profileImage: '',
  gender: 'male',
  email: '',
  mobile: '',
  role: t('admin.members.roles.contributor.name')
})

// 表单验证规则
const formRules = {
  username: [
    { required: true, message: t('admin.members.validations.username_required'), trigger: 'blur' },
    { min: 3, max: 20, message: t('admin.members.validations.username_length'), trigger: 'blur' }
  ],
  fullName: [
    { required: true, message: t('admin.members.validations.full_name_required'), trigger: 'blur' },
    { min: 3, max: 20, message: t('admin.members.validations.full_name_length'), trigger: 'blur' }
  ],
  email: [
    {
      pattern: /^[a-z0-9-]+@[a-z0-9-]+\.[a-z0-9-]+$/,
      message: t('admin.members.validations.invalid_email'),
      trigger: 'blur'
    }
  ],
  mobile: [
    { min: 11, max: 11, message: t('admin.members.validations.mobile_length'), trigger: 'blur' },
    {
      pattern: /^1[3456789]\d{9}$/,
      message: t('admin.members.validations.invalid_mobile'),
      trigger: 'blur'
    }
  ]
}

onMounted(() => {
  loadMemberList()
})

// 获取管理成员列表
const loadMemberList = async () => {
  try {
    const res = await getManageMemberList()
    if (res.code === 1) {
      const membersData = res.data

      membersData.forEach((item: any) => {
        // 根据角色名获取对应语言的角色名称
        let roleName = item.role
        // if (item.role === 'Admin') roleName = t('admin.members.roles.admin.name')
        // else if (item.role === 'Editor') roleName = t('admin.members.roles.editor.name')
        // else if (item.role === 'Contributor') roleName = t('admin.members.roles.contributor.name')

        members.value.push({
          id: item.id,
          name: item.full_name,
          username: item.username,
          email: item.email,
          avatar: item.profile_image ? item.profile_image : '/src/assets/avatar.png',
          role: roleName,
          status:
            item.status === 'normal'
              ? t('admin.members.status.normal')
              : t('admin.members.status.block'),
          visibility:
            item.visibility === 'Public'
              ? t('admin.members.visibility.public')
              : t('admin.members.visibility.private'),
          permissions: getPermissionsByRole(item.role)
        })
      })
      console.log('members:')
      console.log(members.value)
    }
  } catch (error) {
    ElMessage.error(t('admin.members.message.get_members_error'))
  }
}

// 处理下拉菜单命令
const handleDropdownCommand = (member: Member, command: string) => {
  if (command === 'viewRole') {
    selectedMember.value = member
    console.log('selectmember:')
    console.log(member)
    drawerVisible.value = true
  } else if (command === 'deleteRole') {
    ElMessageBox.confirm(t('admin.members.message.delete_confirm'))
      .then(async () => {
        try {
          const res = await deleteMember(member.id.toString())
          if (res.code === 1) {
            ElMessage.success(t('admin.members.message.delete_success'))
            // 刷新成员列表
            members.value = members.value.filter((m) => m.id !== member.id)
            // loadMemberList()
          } else {
            ElMessage.error(res.msg)
          }
        } catch (error) {
          ElMessage.error(t('admin.members.message.delete_error'))
        }
      })
      .catch(() => {
        ElMessage.error(t('admin.members.message.delete_error'))
      })
  } else if (command === 'editRole') {
    // 编辑成员
    isEditing.value = true
    // 加载成员信息
    getMemberInfo(member.id.toString()).then((res) => {
      if (res.code === 1) {
        newMemberForm.value = {
          id: res.data.id,
          username: res.data.username,
          fullName: res.data.full_name,
          profileImage: res.data.profile_image,
          gender: res.data.gender === 1 ? 'male' : 'female',
          email: res.data.email,
          mobile: res.data.mobile,
          role: res.data.role
        }
      }
    })
    addMemberDrawerVisible.value = true
  }
}

// 处理抽屉关闭
const handleDrawerClose = (done: () => void) => {
  done()
  // 可以在这里添加一些清理逻辑
}

// 处理角色定义按钮点击
const handleRoleDefinitionClick = () => {
  roleDefinitionDrawerVisible.value = true
}

// 处理角色定义抽屉关闭
const handleRoleDefinitionDrawerClose = (done: () => void) => {
  done()
}

// 处理添加成员按钮点击
const handleAddMemberClick = () => {
  addMemberDrawerVisible.value = true
}

// 处理添加成员抽屉关闭
const handleAddMemberDrawerClose = (done: () => void) => {
  // 重置表单
  newMemberForm.value = {
    id: 0,
    username: '',
    fullName: '',
    profileImage: '',
    gender: 'male',
    email: '',
    mobile: '',
    role: 'Contributor'
  }
  done()
}

// 处理添加成员表单提交
const handleMemberSubmit = () => {
  // 在实际应用中，这里应该有表单验证逻辑
  // 简单的前端验证
  if (!newMemberForm.value.username || !newMemberForm.value.fullName) {
    ElMessage.error(t('admin.members.validation.username_and_full_name_required'))
    return
  }

  // 创建新成员对象
  const newMember: Member = {
    id: newMemberForm.value.id,
    name: newMemberForm.value.fullName,
    username: newMemberForm.value.username,
    email: newMemberForm.value.email,
    avatar:
      newMemberForm.value.profileImage ||
      `https://picsum.photos/id/${members.value.length + 2}/200`,
    role: newMemberForm.value.role,
    status: 'normal',
    visibility: 'Private',
    permissions: getPermissionsByRole(newMemberForm.value.role)
  }

  const reqData = {
    username: newMemberForm.value.username,
    full_name: newMemberForm.value.fullName,
    profile_image: newMemberForm.value.profileImage,
    gender: newMemberForm.value.gender === 'male' ? 1 : 0,
    email: newMemberForm.value.email,
    mobile: newMemberForm.value.mobile,
    role: newMemberForm.value.role,
    visibility: 'Private'
  }

  if (isEditing.value) {
    // 更新成员
    updateMember(newMemberForm.value.id.toString(), reqData).then((res) => {
      if (res.code === 1) {
        // 更新成员列表
        const index = members.value.findIndex((m) => m.id === newMemberForm.value.id)
        if (index !== -1) {
          members.value[index] = { ...members.value[index], ...reqData }
        }
        ElMessage.success(t('admin.members.message.update_success'))
        isEditing.value = false
        // 关闭抽屉并重置表单
        handleAddMemberDrawerClose(() => {
          addMemberDrawerVisible.value = false
        })
      } else {
        ElMessage.error(res.msg)
      }
    })
  } else {
    // 添加新成员
    addManageMember(reqData)
      .then((res) => {
        if (res.code === 1) {
          // 添加到成员列表
          members.value.push(newMember)

          // 显示成功消息
          ElMessage.success(t('admin.members.message.add_success'))
        }
      })
      .catch((err) => {
        ElMessage.error(err.msg || t('admin.members.message.add_error'))
      })
    // 关闭抽屉并重置表单
    handleAddMemberDrawerClose(() => {
      addMemberDrawerVisible.value = false
    })
  }
}

// 根据角色获取权限列表
const getPermissionsByRole = (role: string): string[] => {
  const roleObj = roles.value.find((r) => r.index === role)
  if (roleObj) {
    return roleObj.permissions
  }
  return []
}

/**
 * 处理公开状态改变
 * @param member 成员
 */
const handleVisibilityChange = async (member: Member) => {
  try {
    const res = await updateMemberVisible(member.id.toString(), member.visibility)
    if (res.code === 1) {
      ElMessage.success(t('admin.members.message.update_visibility_success', { name: member.name }))
    } else {
      ElMessage.error(t('admin.members.message.update_visibility_error', { name: member.name }))
    }
  } catch (error) {
    ElMessage.error(t('admin.members.message.update_visibility_error', { name: member.name }))
  }
}

/**
 * 处理禁用状态
 * @param member 成员
 */
const handleStatusChange = async (member: Member) => {
  try {
    const res = await updateMemberStatus(member.id.toString(), member.status)
    if (res.code === 1) {
      ElMessage.success(t('admin.members.message.update_status_success', { name: member.name }))
    } else {
      ElMessage.error(t('admin.members.message.update_status_error', { name: member.name }))
    }
  } catch (error) {
    ElMessage.error(t('admin.members.message.update_status_error', { name: member.name }))
  }
}

// 上传进度
const uploadProgress = ref(0)
const isUploading = ref(false)

// 上传前验证
const beforeUpload = (file: File) => {
  const isJPG = file.type === 'image/jpeg' || file.type === 'image/png'
  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isJPG) {
    ElMessage.error(t('admin.tags.drawer.form.uploaderror.format'))
    return false
  }
  if (!isLt2M) {
    ElMessage.error(t('admin.tags.drawer.form.uploaderror.size'))
    return false
  }
  return true
}

// 上传OG图片文件
const handleCustomUpload = async (options: any) => {
  isUploading.value = true
  uploadProgress.value = 0

  try {
    const res = await uploadFile({
      file: options.file,
      onProgress: (progressEvent) => {
        if (progressEvent.total > 0) {
          const percent = Math.round((progressEvent.loaded / progressEvent.total) * 100)
          uploadProgress.value = percent
          options.onProgress({ percent })
        }
      }
    })

    if (res.code === 1) {
      options.onSuccess(res.data)
    } else {
      options.onError(new Error(res.msg || t('admin.tags.drawer.form.uploaderror.default')))
    }
  } catch (error) {
    options.onError(error)
  } finally {
    isUploading.value = false
  }
}

// 发布文章上传OG图片成功处理
const handleUploadSuccess = (response: any, file: any) => {
  //publishForm.customOGImage = URL.createObjectURL(file.raw)
  newMemberForm.value.profileImage = response.full_url
  ElMessage.success(t('admin.tags.drawer.form.uploadsuccess'))
}

// 上传失败处理
const handleUploadError = (error: any) => {
  ElMessage.error(t('admin.tags.drawer.form.uploaderror.default'))
  isUploading.value = false
}

// 移除封面图片
const removeImage = () => {
  newMemberForm.value.profileImage = ''
}

// 邀请相关方法
const handleInviteSuccess = () => {
  loadInvitations()
  // 如果当前不在邀请 tab，切换过去
  if (activeTab.value !== 'pendingInvites') {
    activeTab.value = 'pendingInvites'
  }
}

const loadInvitations = async () => {
  loadingInvitations.value = true
  try {
    const res = await getInvitationList()
    if (res.code === 1) {
      invitations.value = res.invitations || []
    }
  } catch (error) {
    ElMessage.error(t('admin.members.message.load_invitations_error'))
  } finally {
    loadingInvitations.value = false
  }
}

const handleResendInvitation = async (invitation: any) => {
  try {
    const res = await resendInvitationEmail(invitation.id)
    if (res.code === 1) {
      ElMessage.success(t('admin.members.message.resend_success'))
    } else {
      ElMessage.error(res.msg || t('admin.members.message.resend_error'))
    }
  } catch (error: any) {
    // 显示更详细的错误信息
    console.error('重新发送邮件失败:', error)
    const errorMsg = error?.response?.data?.msg || error?.message || t('admin.members.message.resend_error')
    ElMessage.error(errorMsg)
  }
}

const handleCancelInvitation = async (invitation: any) => {
  ElMessageBox.confirm(t('admin.members.message.cancel_invite_confirm'))
    .then(async () => {
      try {
        const res = await cancelInvitation(invitation.id)
        if (res.code === 1) {
          ElMessage.success(t('admin.members.message.cancel_success'))
          // 从列表中移除或更新状态
          const index = invitations.value.findIndex((i) => i.id === invitation.id)
          if (index !== -1) {
            invitations.value[index].status = 'Cancelled'
          }
        } else {
          ElMessage.error(res.msg || t('admin.members.message.cancel_error'))
        }
      } catch (error) {
        ElMessage.error(t('admin.members.message.cancel_error'))
      }
    })
    .catch(() => { })
}

const getStatusType = (status: string) => {
  const statusMap: Record<string, any> = {
    pending: 'warning',
    accepted: 'success',
    cancelled: 'info',
    expired: 'danger'
  }
  return statusMap[status] || 'info'
}

const formatDate = (timestamp: number) => {
  if (!timestamp) return '-'
  // Unix 时间戳（秒）转换为毫秒
  return new Date(timestamp * 1000).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 监听 tab 切换，加载邀请列表
watch(activeTab, (newTab) => {
  if (newTab === 'pendingInvites') {
    loadInvitations()
  }
})

// 待处理邀请数量
const pendingCount = computed(() => {
  return invitations.value.filter((i) => i.status === 'pending').length
})
</script>

<style scoped>
.member-management-container {
  padding: 24px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 2rem;
  font-weight: 600;
  color: var(--wy-section-title-color);
}

.page-header p {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
}

.manage-members-section {
  margin-top: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--wy-section-title-color);
}

.header-actions {
  display: flex;
  gap: 12px;
}

.role-definition-btn {
  border-color: #d9d9d9;
}

.invite-member-btn {
  background-color: #3b82f6;
  border-color: #3b82f6;
}

.tabs-container {
  margin-bottom: 20px;
}

.search-container {
  margin-bottom: 20px;
}

.search-input {
  width: 100%;
  max-width: 400px;
}

.members-table-container {
  background-color: #fff;
  border-radius: 8px;
  overflow: hidden;
}

.members-table {
  width: 100%;
}

.member-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.member-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.member-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.member-name {
  font-weight: 500;
  color: #333;
}

.member-email {
  font-size: 12px;
  color: #666;
}

.role-tag {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 12px;
}

.role-admin {
  background-color: #fef3c7;
  color: #d97706;
  border-color: #fef3c7;
}

.role-editor {
  background-color: #dffdee;
  color: #08a360;
  border-color: #c7fed9;
}

.more-actions-btn {
  padding: 6px;
  margin: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s ease;
}

.more-actions-btn:hover {
  background-color: #f0f0f0;
}

/* 抽屉内容样式 */
.member-detail-content {
  padding: 20px;
}

.member-avatar-large {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.member-avatar-large img {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
}

.member-name-large {
  text-align: center;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.member-email-large {
  text-align: center;
  color: #666;
  margin-bottom: 30px;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section h4 {
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 12px 0;
  color: #333;
}

.visibility-text {
  font-size: 14px;
  color: #666;
}

.permissions-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.permission-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #333;
}

.permission-item .el-icon {
  color: #10b981;
}

/* 角色定义抽屉样式 */
.role-definition-content {
  padding: 20px;
}

.role-card {
  background-color: #f8fafc;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}

.role-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.role-card-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  gap: 12px;
}

.role-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
}

.role-name {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.role-description {
  font-size: 14px;
  color: #6b7280;
  margin: 0 0 12px 0;
}

.role-permissions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.permission-badge {
  background-color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  color: #374151;
  border: 1px solid #e5e7eb;
}

/* 添加成员抽屉样式 */
.add-member-content {
  padding: 20px;
}

.avatar-uploader {
  display: flex;
  justify-content: center;
}

.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid #e5e7eb;
}

.avatar-uploader-icon {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  border: 1px dashed #d9d9d9;
  background-color: #fafafa;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: #999;
}

.cover-image-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 15px;
  width: 120px;
  height: 120px;
}

.delete-cover-btn {
  position: absolute;
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
}

.delete-cover-btn:hover {
  position: absolute;
  background-color: rgba(0, 0, 0, 0.8);
  color: white;
}

.add-member-form-item {
  margin-bottom: 20px;
}

.invitations-container {
  background-color: #fff;
  border-radius: 8px;
  overflow: hidden;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
}

/* 移动端样式 */
@media (max-width: 767px) {
  .member-management-container {
    padding: 12px;
  }

  .page-header h1 {
    font-size: 1.5rem;
  }

  .section-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .section-title {
    text-align: center;
  }

  .header-actions {
    flex-direction: column;
    gap: 8px;
  }

  .header-actions .el-button {
    width: 100%;
  }

  .search-input {
    max-width: 100%;
  }

  /* 成员卡片样式 */
  .members-cards-container {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .member-card {
    background-color: #fff;
    border-radius: 8px;
    padding: 12px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .member-card-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
    padding-bottom: 12px;
    border-bottom: 1px solid #e5e7eb;
  }

  .member-card-avatar {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    object-fit: cover;
  }

  .member-card-info {
    flex: 1;
  }

  .member-card-name {
    font-weight: 500;
    font-size: 14px;
    color: #333;
    margin-bottom: 2px;
  }

  .member-card-email {
    font-size: 12px;
    color: #666;
  }

  .member-card-body {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 12px;
  }

  .member-card-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 13px;
  }

  .member-card-label {
    color: #666;
    font-size: 12px;
  }

  .member-card-footer {
    display: flex;
    gap: 8px;
    padding-top: 8px;
    border-top: 1px solid #e5e7eb;
  }

  .member-card-footer .el-button {
    flex: 1;
  }

  /* 邀请卡片样式 */
  .invitations-cards-container {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .invitation-card {
    background-color: #fff;
    border-radius: 8px;
    padding: 12px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .invitation-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #e5e7eb;
  }

  .invitation-card-email {
    font-weight: 500;
    font-size: 14px;
    color: #333;
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .invitation-card-body {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 12px;
  }

  .invitation-card-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 13px;
  }

  .invitation-card-label {
    color: #666;
    font-size: 12px;
  }

  .invitation-card-date {
    font-size: 12px;
    color: #999;
  }

  .invitation-card-footer {
    display: flex;
    gap: 8px;
    padding-top: 8px;
    border-top: 1px solid #e5e7eb;
  }

  .invitation-card-footer .el-button {
    flex: 1;
  }

  /* 抽屉移动端优化 */
  .member-detail-content {
    padding: 16px;
  }

  .role-definition-content {
    padding: 16px;
  }

  .add-member-content {
    padding: 16px;
  }

  /* 角色卡片移动端 */
  .role-card {
    margin-bottom: 12px;
  }
}
</style>
