

<template>
  <div class="profile">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">个人中心</h1>
      <p class="page-description">管理您的个人信息和账户设置</p>
    </div>

    <el-row :gutter="24">
      <!-- 个人信息卡片 -->
      <el-col :span="12">
        <el-card class="profile-card" shadow="never">
          <template #header>
            <div class="card-header">
              <div class="header-info">
                <span class="header-title">个人信息</span>
                <span class="header-subtitle">查看和编辑您的基本信息</span>
              </div>
              <el-button
                type="primary"
                plain
                @click="handleEdit"
                class="edit-btn"
              >
                <el-icon><Edit /></el-icon>
                编辑资料
              </el-button>
            </div>
          </template>
          <div class="profile-info">
            <div class="avatar-wrapper">
              <el-avatar
                :size="100"
                :src="userInfo?.avatarUrl"
              />
              <el-upload
                class="avatar-uploader"
                :auto-upload="false"
                :show-file-list="false"
                :on-change="handleAvatarChange"
                :before-upload="beforeAvatarUpload"
              >
                <el-button
                  type="primary"
                  link
                  class="change-avatar"
                >
                  <el-icon><Camera /></el-icon>
                  更换头像
                </el-button>
              </el-upload>
            </div>
            <div class="info-list">
              <div class="info-item">
                <span class="label">用户名：</span>
                <span class="value">{{ userInfo?.username }}</span>
              </div>
              <div class="info-item">
                <span class="label">真实姓名：</span>
                <span class="value">{{ userInfo?.realName }}</span>
              </div>
              <div class="info-item">
                <span class="label">手机号：</span>
                <span class="value">{{ userInfo?.phone }}</span>
              </div>
              <div class="info-item">
                <span class="label">邮箱：</span>
                <span class="value">{{ userInfo?.email }}</span>
              </div>
              <div class="info-item">
                <span class="label">角色：</span>
                <el-tag :type="userInfo?.role === 1 ? 'danger' : 'info'" size="small">
                  {{ userInfo?.role === 1 ? '管理员' : '普通用户' }}
                </el-tag>
              </div>
              <div class="info-item">
                <span class="label">状态：</span>
                <el-tag :type="userInfo?.status === 1 ? 'success' : 'danger'" size="small">
                  {{ userInfo?.status === 1 ? '正常' : '禁用' }}
                </el-tag>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 修改密码卡片 -->
      <el-col :span="12">
        <el-card class="password-card" shadow="never">
          <template #header>
            <div class="card-header">
              <div class="header-info">
                <span class="header-title">安全设置</span>
                <span class="header-subtitle">修改您的登录密码</span>
              </div>
              <el-icon class="header-icon"><Lock /></el-icon>
            </div>
          </template>
          <el-form
            ref="passwordFormRef"
            :model="passwordForm"
            :rules="passwordRules"
            label-width="100px"
            status-icon
          >
            <el-form-item label="原密码" prop="oldPassword">
              <el-input
                v-model="passwordForm.oldPassword"
                type="password"
                show-password
                placeholder="请输入原密码"
              />
            </el-form-item>
            <el-form-item label="新密码" prop="newPassword">
              <el-input
                v-model="passwordForm.newPassword"
                type="password"
                show-password
                placeholder="请输入新密码"
              />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input
                v-model="passwordForm.confirmPassword"
                type="password"
                show-password
                placeholder="请确认新密码"
              />
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                :loading="passwordLoading"
                @click="handleChangePassword"
              >
                <el-icon><Check /></el-icon>
                修改密码
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>

    <!-- 编辑个人信息对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑个人信息"
      width="500px"
      destroy-on-close
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="editRules"
        label-width="100px"
        status-icon
      >
        <el-form-item label="真实姓名" prop="realName">
          <el-input
            v-model="editForm.realName"
            placeholder="请输入真实姓名"
          />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input
            v-model="editForm.phone"
            placeholder="请输入手机号"
          />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="editForm.email"
            placeholder="请输入邮箱"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            :loading="editLoading"
            @click="handleSaveEdit"
          >
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { FormInstance, UploadProps, FormItemRule } from 'element-plus'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { updateUser } from '@/api/user'
import { fileRequest } from '@/api/file_request'
import type { UpdateUserParams } from '@/types/user'
import { Edit, Camera, Lock, Check } from '@element-plus/icons-vue'

const userStore = useUserStore()

// 用户信息
const userInfo = computed(() => userStore.userInfo)

// 修改密码表单
const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 修改密码表单校验规则
const validatePass2 = (rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== passwordForm.value.newPassword) {
    callback(new Error('两次输入密码不一致!'))
  } else {
    callback()
  }
}

const passwordRules = {
  oldPassword: [
    { required: true, message: '请输入原密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度应在6-20个字符之间', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度应在6-20个字符之间', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validatePass2, trigger: 'blur' }
  ]
}

const passwordLoading = ref(false)
const passwordFormRef = ref<FormInstance>()

// 处理修改密码
const handleChangePassword = async () => {
  if (!passwordFormRef.value) return

  try {
    await passwordFormRef.value.validate()
    passwordLoading.value = true

    await userStore.changePassword({
      id: userInfo.value?.id as number,
      oldPassword: passwordForm.value.oldPassword,
      newPassword: passwordForm.value.newPassword
    })

    ElMessage.success('密码修改成功')
    passwordForm.value = {
      oldPassword: '',
      newPassword: '',
      confirmPassword: ''
    }
  } catch (error) {
    console.error('修改密码失败:', error)
  } finally {
    passwordLoading.value = false
  }
}

// 编辑表单
const editForm = ref({
  realName: '',
  phone: '',
  email: ''
})

// 编辑表单校验规则
const editRules = {
  realName: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '真实姓名长度应在2-20个字符之间', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/, message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
} satisfies Record<string, FormItemRule[]>

const editDialogVisible = ref(false)
const editLoading = ref(false)
const editFormRef = ref<FormInstance>()

// 处理编辑
const handleEdit = () => {
  editForm.value = {
    realName: userInfo.value?.realName || '',
    phone: userInfo.value?.phone || '',
    email: userInfo.value?.email || ''
  }
  editDialogVisible.value = true
}

// 处理保存编辑
const handleSaveEdit = async () => {
  if (!editFormRef.value) return

  try {
    await editFormRef.value.validate()
    editLoading.value = true

    await updateUser({
      id: userInfo.value?.id as number,
      realName: editForm.value.realName,
      phone: editForm.value.phone,
      email: editForm.value.email,
      role: userInfo.value?.role as number,
      status: userInfo.value?.status as number
    })

    // 更新本地用户信息
    const storedUserInfo = localStorage.getItem('userInfo')
    if (storedUserInfo) {
      const data = JSON.parse(storedUserInfo)
      data.userInfo = {
        ...data.userInfo,
        realName: editForm.value.realName,
        phone: editForm.value.phone,
        email: editForm.value.email
      }
      localStorage.setItem('userInfo', JSON.stringify(data))
      userStore.initUserInfo()
    }

    ElMessage.success('个人信息修改成功')
    editDialogVisible.value = false
  } catch (error) {
    console.error('修改个人信息失败:', error)
  } finally {
    editLoading.value = false
  }
}

// 处理头像上传前的验证
const beforeAvatarUpload: UploadProps['beforeUpload'] = (file) => {
  const isJPG = file.type === 'image/jpeg'
  const isPNG = file.type === 'image/png'
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isJPG && !isPNG) {
    ElMessage.error('头像只能是 JPG 或 PNG 格式!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('头像大小不能超过 2MB!')
    return false
  }
  return true
}

// 处理头像文件改变
const handleAvatarChange: UploadProps['onChange'] = async (uploadFile) => {
  if (!uploadFile.raw) return

  try {
    // 上传文件到文件服务
    const { bucket, objectKey } = await fileRequest.upload('avatars', uploadFile.raw)

    // 更新用户头像
    const updateParams: UpdateUserParams = {
      id: userInfo.value?.id as number,
      avatarBucket: bucket,
      avatarObjectKey: objectKey
    }
    await updateUser(updateParams)

    // 更新本地用户信息
    const storedUserInfo = localStorage.getItem('userInfo')
    if (storedUserInfo) {
      const data = JSON.parse(storedUserInfo)
      data.userInfo = {
        ...data.userInfo,
        avatarBucket: bucket,
        avatarObjectKey: objectKey,
        avatarUrl: fileRequest.getFileUrl(bucket, objectKey)
      }
      localStorage.setItem('userInfo', JSON.stringify(data))
      userStore.initUserInfo()
    }

    ElMessage.success('头像更新成功')
  } catch (error) {
    console.error('头像上传失败:', error)
    ElMessage.error('头像上传失败')
  }
}
</script>

<style scoped>
.profile {
  padding: 32px;
  min-height: calc(100vh - 140px);
  background: linear-gradient(135deg, #f1f5f9 0%, #ffffff 25%, #f8fafc 50%, #ffffff 75%, #f1f5f9 100%);
  position: relative;
}

.profile::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background:
    radial-gradient(circle at 20% 20%, rgba(82, 196, 26, 0.03) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(82, 196, 26, 0.04) 0%, transparent 50%);
  pointer-events: none;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
  position: relative;
  z-index: 1;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 12px 0;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.page-description {
  font-size: 16px;
  color: #64748b;
  margin: 0;
  font-weight: 400;
  line-height: 1.6;
}

.profile-card,
.password-card {
  height: 100%;
  transition: all 0.3s ease;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  backdrop-filter: blur(10px);
  position: relative;
  z-index: 1;
}

.profile-card:hover,
.password-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  border-color: #cbd5e1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 0;
}

.header-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.header-title {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.4;
}

.header-subtitle {
  font-size: 14px;
  color: #64748b;
  font-weight: 400;
}

.header-icon {
  font-size: 20px;
  color: var(--primary-color);
}

.edit-btn {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.2s ease;
  color: #ffffff !important;
}

.edit-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(82, 196, 26, 0.3);
}

.profile-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px;
}

.avatar-wrapper {
  position: relative;
  margin-bottom: 32px;
  text-align: center;
}

.change-avatar {
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #ffffff !important;
  transition: all 0.2s ease;
}

.change-avatar:hover {
  color: #ffffff !important;
  transform: translateY(-1px);
}

.info-list {
  width: 100%;
  max-width: 400px;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px 20px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.8) 0%, rgba(248, 250, 252, 0.8) 100%);
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
}

.info-item:hover {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-color: #cbd5e1;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.info-item .label {
  width: 100px;
  color: #64748b;
  font-weight: 600;
  font-size: 14px;
}

.info-item .value {
  color: #1e293b;
  flex: 1;
  font-weight: 500;
  font-size: 14px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* Element Plus组件样式覆盖 */
:deep(.el-card__header) {
  padding: 0;
  border-bottom: 1px solid #e2e8f0;
}

:deep(.el-card__body) {
  padding: 0;
}

:deep(.el-form) {
  padding: 24px;
}

:deep(.el-form-item) {
  margin-bottom: 24px;
}

:deep(.el-form-item__label) {
  color: #374151;
  font-weight: 600;
  font-size: 14px;
  line-height: 1.5;
}

:deep(.el-form-item__content) {
  flex-wrap: nowrap;
}

:deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px #d1d5db inset;
  border-radius: 8px;
  transition: all 0.2s ease;
  background-color: #ffffff;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--primary-color) inset;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(82, 196, 26, 0.2) inset;
}

:deep(.el-button) {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.2s ease;
}

:deep(.el-button--primary) {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  background: var(--gradient-primary);
  border-color: transparent;
}

:deep(.el-button--primary:hover) {
  background: var(--gradient-light);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(82, 196, 26, 0.4);
}

:deep(.el-avatar) {
  border: 3px solid #e2e8f0;
  transition: all 0.3s ease;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

:deep(.el-avatar:hover) {
  border-color: var(--primary-color);
  box-shadow: 0 6px 24px rgba(82, 196, 26, 0.2);
}

:deep(.el-tag) {
  border-radius: 6px;
  font-weight: 500;
  border: none;
}

:deep(.el-tag--success) {
  background: var(--gradient-primary);
  color: #ffffff;
}

:deep(.el-tag--danger) {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: #ffffff;
}

:deep(.el-tag--info) {
  background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
  color: #ffffff;
}

:deep(.el-dialog) {
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

:deep(.el-dialog__header) {
  padding: 24px 24px 16px;
  border-bottom: 1px solid #e2e8f0;
}

:deep(.el-dialog__title) {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
}

:deep(.el-dialog__body) {
  padding: 24px;
}

:deep(.el-dialog__footer) {
  padding: 16px 24px 24px;
  border-top: 1px solid #e2e8f0;
}
</style>
