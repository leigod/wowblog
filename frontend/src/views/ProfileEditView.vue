<template>
  <div class="profile-edit-container">
    <div class="page-header">
      <h1>{{ t('profile_edit.title') }}</h1>
      <p>{{ t('profile_edit.subtitle') }}</p>
    </div>

    <el-card class="profile-edit-card">
      <el-form ref="profileFormRef" :model="profileForm" :rules="formRules" label-width="140px" label-position="top"
        size="large" class="profile-form">
        <!-- 头像上传区域 -->
        <el-form-item>
          <el-upload v-model:file-list="avatarFileList" class="avatar-uploader" action="#" :show-file-list="false"
            :before-upload="beforeAvatarUpload" :on-success="handleAvatarSuccess">
            <div class="avatar-upload-item">
              <div class="avatar-container">
                <img :src="profileForm.avatarUrl" class="avatar" />
                <el-icon class="delete-icon" @click="handleDeleteAvatar">
                  <Delete />
                </el-icon>
              </div>
            </div>

            <div style="margin-left: 20px">
              <el-button type="primary" :icon="Picture" round size="large" class="avatar-uploader-icon">{{
                t('profile_edit.change_image') }}
              </el-button>
              <p class="avatar-hint">{{ t('profile_edit.avatar_hint') }}</p>
            </div>
          </el-upload>
        </el-form-item>

        <!-- 基本信息区域 -->
        <el-form-item :label="t('profile_edit.full_name')" prop="fullName">
          <el-input v-model="profileForm.fullName" :placeholder="t('profile_edit.full_name_placeholder')" maxlength="50"
            show-word-limit />
        </el-form-item>

        <el-form-item :label="t('profile_edit.tagline')" prop="tagline">
          <el-input v-model="profileForm.tagline" :placeholder="t('profile_edit.tagline_placeholder')" maxlength="100"
            show-word-limit />
        </el-form-item>

        <el-form-item :label="t('profile_edit.email')" prop="email">
          <el-input v-model="profileForm.email" :placeholder="t('profile_edit.email_placeholder')" type="email"
            maxlength="100" show-word-limit />
        </el-form-item>

        <el-form-item :label="t('profile_edit.mobile')" prop="mobile">
          <el-input v-model="profileForm.mobile" :placeholder="t('profile_edit.mobile_placeholder')" type="number"
            maxlength="11" show-word-limit />
        </el-form-item>
        <el-form-item :label="t('profile_edit.gender')" prop="gender">
          <el-radio-group v-model="profileForm.gender">
            <el-radio :value="0">{{ t('profile_edit.gender_female') }}</el-radio>
            <el-radio :value="1">{{ t('profile_edit.gender_male') }}</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item :label="t('profile_edit.location')" prop="location">
          <el-tree-select v-model="profileForm.location" :placeholder="t('profile_edit.location_placeholder')"
            :data="locationData" :props="{ label: 'label', value: 'label', children: 'children' }"
            :filter-node-method="filterLocation" filterable />
        </el-form-item>
        <el-form-item :label="t('profile_edit.birthday')" prop="birthday">
          <el-date-picker v-model="profileForm.birthday" type="date"
            :placeholder="t('profile_edit.birthday_placeholder')" style="width: 100%" />
        </el-form-item>
        <el-form-item :label="t('profile_edit.school')" prop="school">
          <el-input v-model="profileForm.school" :placeholder="t('profile_edit.school_placeholder')" type="text"
            maxlength="100" show-word-limit />
        </el-form-item>

        <!-- 关于我 -->
        <el-form-item :label="t('profile_edit.about_you')" class="social-title">
          <template #label>
            <span class="social-title">{{ t('profile_edit.about_you') }}</span>
          </template>
          <p class="form-title-hint">{{ t('profile_edit.about_hint') }}</p>
        </el-form-item>
        <el-form-item :label="t('profile_edit.profile_bio')" prop="about">
          <el-input v-model="profileForm.about" :placeholder="t('profile_edit.profile_bio_placeholder')" type="textarea"
            :rows="4" maxlength="500" show-word-limit />
        </el-form-item>

        <!-- 技能标签 -->
        <el-form-item :label="t('profile_edit.tech_stack')" prop="tags">
          <el-input-tag v-model="profileForm.tags" :placeholder="t('profile_edit.tech_stack_placeholder')" :max="20"
            @input="handleTagInput" />
          <el-card v-if="showTagsCard" style="
              width: 100%;
              min-height: 120px;
              max-height: 300px;
              overflow-y: auto;
              font-weight: 400;
              padding: 0;
              margin-top: 8px;
            " body-style="padding: 10px 0 10px 0" shadow="always">
            <div v-if="showTagsCardLoading"
              style="display: flex; justify-content: center; align-items: center; height: 120px">
              <svg class="circular" viewBox="0 0 50 50">
                <circle class="path" cx="25" cy="25" r="20" fill="none" />
              </svg>
            </div>
            <div v-for="tag in tagSuggestionsList" :key="tag.id" @click="handleSelectTag(tag.name, currentTagInputKey)"
              class="tag-list-item">
              {{ tag.name }}
            </div>
          </el-card>
          <p class="form-hint">{{ t('profile_edit.tech_stack_hint') }}</p>
        </el-form-item>

        <!-- 可用服务 -->
        <el-form-item :label="t('profile_edit.available_for')" prop="availableFor">
          <el-input v-model="profileForm.availableFor" :placeholder="t('profile_edit.available_for_placeholder')"
            type="textarea" :rows="3" maxlength="300" show-word-limit />
        </el-form-item>

        <!-- 社交媒体链接 -->
        <el-form-item :label="t('profile_edit.social_profiles')" class="social-title">
          <template #label>
            <span class="social-title">{{ t('profile_edit.social_profiles') }}</span>
          </template>
          <p class="form-title-hint">{{ t('profile_edit.social_hint') }}</p>
        </el-form-item>

        <el-form-item :label="t('profile_edit.wechat')">
          <el-input v-model="profileForm.social.wechat" :placeholder="t('profile_edit.wechat_placeholder')" />
        </el-form-item>
        <el-form-item :label="t('profile_edit.weibo')">
          <el-input v-model="profileForm.social.weibo" :placeholder="t('profile_edit.weibo_placeholder')" />
        </el-form-item>
        <el-form-item :label="t('profile_edit.douyin')">
          <el-input v-model="profileForm.social.douyin" :placeholder="t('profile_edit.douyin_placeholder')" />
        </el-form-item>
        <el-form-item :label="t('profile_edit.zhihu')">
          <el-input v-model="profileForm.social.zhihu" :placeholder="t('profile_edit.zhihu_placeholder')" />
        </el-form-item>
        <el-form-item :label="t('profile_edit.bilibili')">
          <el-input v-model="profileForm.social.bilibili" :placeholder="t('profile_edit.bilibili_placeholder')" />
        </el-form-item>
        <el-form-item :label="t('profile_edit.xiaohongshu')">
          <el-input v-model="profileForm.social.xiaohongshu" :placeholder="t('profile_edit.xiaohongshu_placeholder')" />
        </el-form-item>
        <el-form-item :label="t('profile_edit.gitee')">
          <el-input v-model="profileForm.social.gitee" :placeholder="t('profile_edit.gitee_placeholder')" />
        </el-form-item>

        <el-form-item :label="t('profile_edit.twitter')">
          <el-input v-model="profileForm.social.twitter" :placeholder="t('profile_edit.twitter_placeholder')" />
        </el-form-item>

        <el-form-item :label="t('profile_edit.instagram')">
          <el-input v-model="profileForm.social.instagram" :placeholder="t('profile_edit.instagram_placeholder')" />
        </el-form-item>

        <el-form-item :label="t('profile_edit.github')">
          <el-input v-model="profileForm.social.github" :placeholder="t('profile_edit.github_placeholder')" />
        </el-form-item>

        <el-form-item :label="t('profile_edit.linkedin')">
          <el-input v-model="profileForm.social.linkedin" :placeholder="t('profile_edit.linkedin_placeholder')" />
        </el-form-item>

        <el-form-item :label="t('profile_edit.dribbble')">
          <el-input v-model="profileForm.social.dribbble" :placeholder="t('profile_edit.dribbble_placeholder')" />
        </el-form-item>

        <el-form-item :label="t('profile_edit.website')">
          <el-input v-model="profileForm.social.website" :placeholder="t('profile_edit.website_placeholder')" />
        </el-form-item>

        <!-- 隐私设置 -->
        <el-form-item :label="t('profile_edit.privacy_settings')" class="social-title">
          <template #label>
            <span class="social-title">{{ t('profile_edit.privacy_settings') }}</span>
          </template>
          <p class="form-title-hint">{{ t('profile_edit.privacy_hint') }}</p>
        </el-form-item>

        <el-form-item :label="t('profile_edit.show_bookmarks')">
          <div style="width: 100%">
            <el-switch v-model="privacyForm.showBookmarks" :active-text="t('profile_edit.show')"
              :inactive-text="t('profile_edit.hide')" :active-value="1" :inactive-value="0" />
          </div>
          <p class="form-hint">{{ t('profile_edit.show_bookmarks_hint') }}</p>
        </el-form-item>

        <el-form-item :label="t('profile_edit.show_likes')">
          <div style="width: 100%">
            <el-switch v-model="privacyForm.showLikes" :active-text="t('profile_edit.show')"
              :inactive-text="t('profile_edit.hide')" :active-value="1" :inactive-value="0" />
          </div>
          <p class="form-hint">{{ t('profile_edit.show_likes_hint') }}</p>
        </el-form-item>

        <el-form-item :label="t('profile_edit.show_comments')">
          <div style="width: 100%">
            <el-switch v-model="privacyForm.showComments" :active-text="t('profile_edit.show')"
              :inactive-text="t('profile_edit.hide')" :active-value="1" :inactive-value="0" />
          </div>
          <p class="form-hint">{{ t('profile_edit.show_comments_hint') }}</p>
        </el-form-item>

        <el-form-item :label="t('profile_edit.show_views')">
          <div style="width: 100%">
            <el-switch v-model="privacyForm.showViews" :active-text="t('profile_edit.show')"
              :inactive-text="t('profile_edit.hide')" :active-value="1" :inactive-value="0" />
          </div>
          <p class="form-hint">{{ t('profile_edit.show_views_hint') }}</p>
        </el-form-item>

        <!-- 表单操作按钮 -->
        <el-form-item class="form-actions">
          <el-button type="default" @click="handleCancel">{{ t('profile_edit.cancel') }}</el-button>
          <el-button type="primary" @click="handleSubmit">{{ t('profile_edit.save_changes') }}</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAppStore } from '@/stores/app'
import {
  ElForm,
  ElFormItem,
  ElInput,
  ElUpload,
  ElButton,
  ElIcon,
  ElMessage
} from 'element-plus'
import { Picture } from '@element-plus/icons-vue'
import type { FormInstance, UploadProps } from 'element-plus'
import worldAreaData from '@/data/world-area.json'
import {
  updateUserInfo,
  updateUserAvatar,
  getUserByUsername
} from '@/api/services/user'
import { searchTagsFrontend } from '@/api/services/tags'
import { getUserPrivacy, updateUserPrivacy } from '@/api/services/user'
import { generateLetterAvatar } from '@/utils/avatarUtils'

// 定义表单数据接口
interface ProfileForm {
  avatarUrl: string
  fullName: string
  tagline: string
  email: string
  mobile: string
  gender: number
  location: string
  birthday: Date | null
  school: string
  about: string
  tags: string[]
  availableFor: string
  social: {
    weibo: string
    xiaohongshu: string
    gitee: string
    wechat: string
    zhihu: string
    douyin: string
    bilibili: string
    twitter: string
    instagram: string
    github: string
    linkedin: string
    dribbble: string
    website: string
  }
}

const { t } = useI18n()
const appStore = useAppStore()
// 状态定义
const profileFormRef = ref<FormInstance>()
const router = useRouter()
const avatarFileList = ref<any[]>([])

// 标签联想相关状态
const tagSuggestionsList = ref<any[]>([])
const showTagsCard = ref(false)
const showTagsCardLoading = ref(false)
const currentTagInputKey = ref('')

// 表单数据
const profileForm = reactive<ProfileForm>({
  avatarUrl: '',
  email: '',
  mobile: '',
  gender: 0,
  fullName: '',
  tagline: '',
  location: '',
  birthday: null,
  school: '',
  about: '',
  tags: [],
  availableFor: '',
  social: {
    weibo: '',
    xiaohongshu: '',
    gitee: '',
    wechat: '',
    zhihu: '',
    douyin: '',
    bilibili: '',
    twitter: '',
    instagram: '',
    github: '',
    linkedin: '',
    dribbble: '',
    website: ''
  }
})

// 隐私设置表单
const privacyForm = reactive({
  showBookmarks: 1,
  showLikes: 1,
  showComments: 1,
  showViews: 1
})

// 表单验证规则接口
// interface FormRules {
//   fullName?: Array<{
//     required?: boolean
//     message?: string
//     trigger?: string
//     min?: number
//     max?: number
//   }>
//   tagline?: Array<{
//     required?: boolean
//     message?: string
//     trigger?: string
//     max?: number
//   }>
//   about?: Array<{
//     max?: number
//     message?: string
//     trigger?: string
//   }>
//   tags?: Array<{
//     max?: number
//     message?: string
//     trigger?: string
//   }>
//   availableFor?: Array<{
//     max?: number
//     message?: string
//     trigger?: string
//   }>
//   email?: Array<{
//     message?: string
//     trigger?: string
//     required?: boolean
//   }>
//   mobile?: Array<{
//     pattern?: RegExp
//     message?: string
//     trigger?: string
//     required?: boolean
//   }>
// }

// 表单验证规则
const formRules = reactive<any>({
  fullName: [
    { required: true, message: t('profile_edit.full_name_placeholder'), trigger: 'blur' },
    { min: 2, max: 50, message: t('profile_edit.name_too_short'), trigger: 'blur' }
  ],
  tagline: [{ max: 100, message: t('profile_edit.tagline_too_long'), trigger: 'blur' }],
  about: [{ max: 500, message: t('profile_edit.bio_too_long'), trigger: 'blur' }],
  availableFor: [{ max: 300, message: t('profile_edit.available_too_long'), trigger: 'blur' }],
  email: [{ type: 'email', message: t('profile_edit.invalid_email'), trigger: 'blur', required: false }],
  mobile: [
    { pattern: /^1[3-9]\d{9}$/, message: t('profile_edit.invalid_phone'), trigger: 'blur', required: false }
  ]
})

// 世界地区数据（从JSON文件加载，包含国家层级）
const locationData = ref<any[]>([])

// 加载行政区划数据
const loadLocationData = () => {
  locationData.value = worldAreaData as any[]
}

const filterLocation = (queryString: string, data: any) => {
  if (!queryString) return true
  return data.label.includes(queryString)
}

function getParentValues(obj: Array<any>, targetLabel: string) {
  let stack: Array<any> = []
  let going = true
  let walker = (obj: any[], targetLabel: string) => {
    obj.forEach((item) => {
      if (!going) return
      stack.push(item.label)
      if (item.label === targetLabel) {
        going = false
      } else if (item.children) {
        walker(item.children, targetLabel)
      } else {
        stack.pop()
      }
    })
    if (going) stack.pop()
  }
  walker(obj, targetLabel)
  return stack.join('，')
}

const getNodePath = (selectedLabel: string) => {
  if (!selectedLabel) return ''
  return getParentValues(locationData.value, selectedLabel)
}

// 生命周期钩子
onMounted(() => {
  // 加载行政区划数据
  loadLocationData()
  // 加载用户数据
  loadUserData()
})

// 加载用户数据
const loadUserData = async () => {
  // 检查用户是否已登录
  if (!appStore.token || !appStore.userInfo?.username) {
    console.warn('用户未登录，重定向到登录页')
    ElMessage.warning(t('profile_edit.please_login'))
    router.push('/login')
    return
  }

  try {
    const res = await getUserByUsername(appStore.userInfo.username)
    const userData = res.data

    // 填充表单数据
    profileForm.fullName = userData.full_name || ''
    profileForm.tagline = userData.profile_tagline || ''
    profileForm.email = userData.email || ''
    profileForm.mobile = userData.mobile || ''

    // 处理location：如果是完整路径（包含逗号），提取最后一部分作为树选择器的值
    if (userData.location) {
      if (userData.location.includes('，') || userData.location.includes(',')) {
        // 提取路径的最后一部分
        const parts = userData.location.split(/[,，]/)
        profileForm.location = parts[parts.length - 1].trim()
      } else {
        profileForm.location = userData.location
      }
    } else {
      profileForm.location = ''
    }

    profileForm.gender = (userData.gender as number) ?? 0
    // 将时间戳转换为 Date 对象
    if (userData.birthday) {
      profileForm.birthday = new Date(userData.birthday * 1000)
    } else {
      profileForm.birthday = null
    }
    profileForm.school = userData.school || ''
    profileForm.about = userData.profile_bio || ''
    profileForm.tags = userData.tech_stack || []
    profileForm.availableFor =
      typeof userData.available_for === 'string'
        ? userData.available_for
        : userData.available_for?.join(', ') || ''
    profileForm.social = {
      weibo: userData.social_profiles?.weibo || '',
      xiaohongshu: userData.social_profiles?.xiaohongshu || '',
      gitee: userData.social_profiles?.gitee || '',
      wechat: userData.social_profiles?.wechat || '',
      zhihu: userData.social_profiles?.zhihu || '',
      douyin: userData.social_profiles?.douyin || '',
      bilibili: userData.social_profiles?.bilibili || '',
      twitter: userData.social_profiles?.twitter || '',
      instagram: userData.social_profiles?.instagram || '',
      github: userData.social_profiles?.github || '',
      linkedin: userData.social_profiles?.linkedin || '',
      dribbble: userData.social_profiles?.dribbble || '',
      website: userData.social_profiles?.website || ''
    }
    profileForm.avatarUrl =
      userData.profile_image || generateLetterAvatar(userData.full_name || userData.username)

    // 加载隐私设置（仅在用户已登录时）
    try {
      const privacyRes = await getUserPrivacy()
      const privacyData = privacyRes.data
      privacyForm.showBookmarks = privacyData.privacy_show_bookmarks ?? 1
      privacyForm.showLikes = privacyData.privacy_show_likes ?? 1
      privacyForm.showComments = privacyData.privacy_show_comments ?? 1
      privacyForm.showViews = privacyData.privacy_show_views ?? 1
    } catch (error) {
      // 静默处理错误，使用默认值
      console.warn('隐私设置加载失败，使用默认值:', error)
      // 保持默认值 (1 = 显示)
    }
  } catch (error) {
    console.error('加载用户数据失败:', error)
    ElMessage.error(t('profile_edit.load_failed'))
  }
}

// 头像上传前的校验
const beforeAvatarUpload: UploadProps['beforeUpload'] = (rawFile) => {
  if (!rawFile.type.match('image/(jpeg|png)')) {
    ElMessage.error(t('profile_edit.only_jpg_png'))
    return false
  }
  if (rawFile.size / 1024 / 1024 > 2) {
    ElMessage.error(t('profile_edit.file_too_large'))
    return false
  }
  return true
}

// 头像上传成功处理
const handleAvatarSuccess = async (response: any, file: any) => {
  try {
    // 调用API上传头像
    const uploadResponse = await updateUserAvatar(file)
    // 使用后端返回的头像URL
    profileForm.avatarUrl = uploadResponse.avatarUrl || URL.createObjectURL(file)
    ElMessage.success(t('profile_edit.avatar_upload_success'))
  } catch (error) {
    console.error('头像上传失败:', error)
    ElMessage.error(t('profile_edit.avatar_upload_failed'))
  }
}

const handleDeleteAvatar = () => {
  profileForm.avatarUrl = ''
  // 在实际应用中，这里会调用后端API删除头像
  ElMessage.success(t('profile_edit.avatar_deleted'))
}

// 提交表单
const handleSubmit = async () => {
  if (!profileFormRef.value) return

  try {
    // 表单验证
    await profileFormRef.value.validate()

    // 将位置ID转换为完整路径名称
    let locationLabel = profileForm.location
    if (locationLabel) {
      locationLabel = getNodePath(locationLabel)
    }

    // 准备提交的数据，匹配后端 UserProfileUpdate schema
    const submitData = {
      full_name: profileForm.fullName,
      profile_tagline: profileForm.tagline,
      email: profileForm.email,
      mobile: profileForm.mobile,
      gender: profileForm.gender,
      location: locationLabel,
      birthday: profileForm.birthday ? profileForm.birthday.toISOString() : null,
      school: profileForm.school,
      profile_bio: profileForm.about,
      tech_stack: profileForm.tags,
      available_for: profileForm.availableFor,
      social_profiles: profileForm.social,
      profile_image: profileForm.avatarUrl
    }

    // 调用API提交表单数据
    await updateUserInfo(submitData)

    // 更新隐私设置
    try {
      await updateUserPrivacy({
        privacy_show_bookmarks: privacyForm.showBookmarks,
        privacy_show_likes: privacyForm.showLikes,
        privacy_show_comments: privacyForm.showComments,
        privacy_show_views: privacyForm.showViews
      })
    } catch (error) {
      console.error('隐私设置更新失败:', error)
    }

    ElMessage.success(t('profile_edit.save_success'))
    router.push(`/profile/${appStore.userInfo.username}`)
  } catch (error) {
    console.error('表单验证失败或提交失败:', error)
    ElMessage.error(t('profile_edit.save_failed'))
  }
}

// 取消编辑
const handleCancel = () => {
  router.push(`/profile/${appStore.userInfo.username}`)
}

// 标签联想输入处理
const handleTagInput = (input: string) => {
  currentTagInputKey.value = input
  if (input.length === 0) {
    tagSuggestionsList.value = []
    showTagsCard.value = false
    showTagsCardLoading.value = false
    return
  }
  showTagsCard.value = true
  showTagsCardLoading.value = true
  getTagSuggestions(input)
}

// 获取标签建议
const getTagSuggestions = async (input: string) => {
  try {
    const res = await searchTagsFrontend(input)
    if (res.code === 1) {
      showTagsCardLoading.value = false
      tagSuggestionsList.value = res.data
    }
  } catch (error) {
    console.error('获取标签建议失败:', error)
    tagSuggestionsList.value = []
    showTagsCard.value = false
    showTagsCardLoading.value = false
  }
}

// 选择标签
const handleSelectTag = (tag: string, input: string) => {
  // 先移除输入的临时文本，再添加选择的标签
  profileForm.tags = profileForm.tags.filter((t: string) => t !== input)
  if (!profileForm.tags.includes(tag)) {
    profileForm.tags.push(tag)
  }
  tagSuggestionsList.value = []
  showTagsCard.value = false
}
</script>

<style scoped lang="scss">
.profile-edit-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
  text-align: center;

  h1 {
    margin: 0 0 10px 0;
    font-size: 28px;
    font-weight: 600;
  }

  p {
    margin: 0;
    color: #666;
    font-size: 16px;
  }
}

.profile-edit-card {
  padding: 30px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.avatar-upload-item {
  display: flex;
  flex-direction: column;
  align-items: center;

  .avatar-uploader {
    border: 1px dashed #d9d9d9;
    border-radius: 50%;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    transition: all 0.3s;
    padding: 0;

    div {
      padding: 0;
    }

    &:hover {
      border-color: #409eff;
    }
  }

  .avatar-container {
    position: relative;
    width: 100%;
    height: 100%;
  }

  .delete-icon {
    position: absolute;
    top: 72px;
    right: 72px;
    background-color: #fff;
    border-radius: 50%;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    cursor: pointer;
    opacity: 0;
    transition: opacity 0.3s;
  }

  .avatar-container:hover .delete-icon {
    opacity: 1;
  }

  .avatar {
    width: 178px;
    height: 178px;
    display: block;
    object-fit: cover;
    border-radius: 50%;

    &:hover {
      border: 1px dashed #409eff;
    }
  }

  .avatar-uploader-icon-wrapper {
    margin-left: 20px;
  }

  .avatar-uploader-icon {
    font-size: 28px;
    color: #8c8c8c;
    width: 178px;
    height: 178px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #f5f5f5;
  }

  .avatar-hint {
    margin: 10px 0 0 0;
    color: #888;
    font-size: 14px;
  }
}

.profile-form {
  .form-hint {
    margin: 5px 0 0 0;
    color: #888;
    font-size: 12px;
  }

  .form-title-hint {
    margin: -1rem 0 0 0;
    color: #888;
    font-size: 12px;
  }

  .social-title {
    padding-bottom: 0;
    font-weight: 600;
    font-size: 1.5rem;
    margin-top: 2rem;

    .el-form-item__content {
      margin-left: 0 !important;
    }
  }

  // 隐私设置样式
  .el-divider {
    margin: 40px 0 20px 0;

    h3 {
      margin: 0;
      font-size: 18px;
      font-weight: 600;
      color: #333;
    }
  }

  // 隐私设置的表单项
  .el-form-item {
    .el-form-item__content {
      flex-direction: column;
      align-items: flex-start;

      .el-switch {
        margin-bottom: 5px;
      }

      .form-hint {
        margin-left: 0;
        line-height: 1.5;
      }
    }
  }
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 40px;
}

// 标签列表样式
.tag-list-item {
  padding: 8px 16px;
  cursor: pointer;
  transition: background-color 0.2s;

  &:hover {
    background-color: var(--el-fill-color-light);
  }
}

// 加载动画
.circular {
  display: inline;
  width: 30px;
  height: 30px;
  animation: loading-rotate 2s linear infinite;

  .path {
    animation: loading-dash 1.5s ease-in-out infinite;
    stroke-dasharray: 90, 150;
    stroke-dashoffset: 0;
    stroke-width: 2;
    stroke: var(--el-color-primary);
    stroke-linecap: round;
  }
}

@keyframes loading-rotate {
  100% {
    transform: rotate(360deg);
  }
}

@keyframes loading-dash {
  0% {
    stroke-dasharray: 1, 200;
    stroke-dashoffset: 0;
  }

  50% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -40px;
  }

  100% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -120px;
  }
}
</style>
