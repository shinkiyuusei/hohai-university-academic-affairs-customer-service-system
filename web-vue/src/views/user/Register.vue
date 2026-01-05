
<template>
  <transition name="page-slide" appear>
    <div class="register-container">
    <!-- 左侧：系统介绍区域 -->
    <div class="register-left">
      <div class="intro-content animate-intro">
        <!-- 系统标题区域 -->
        <div class="title-section">
          <h1 class="system-title">教务信息知识问答系统</h1>
          <p class="system-subtitle">基于GraphRAG技术的教务信息智能问答平台</p>
        </div>

        <!-- 优势介绍 -->
        <div class="advantages-section">
          <div class="advantage-item">
            <div class="advantage-icon">🌀</div>
            <div class="advantage-text">
              <h3>GraphRAG驱动</h3>
              <p>基于知识图谱的检索增强生成技术，提供智能化的教务信息知识问答</p>
            </div>
          </div>
          <div class="advantage-item">
            <div class="advantage-icon">🕸️</div>
            <div class="advantage-text">
              <h3>图谱可视化</h3>
              <p>交互式知识图谱展示，直观呈现教务信息的实体关系网络</p>
            </div>
          </div>
          <div class="advantage-item">
            <div class="advantage-icon">🎯</div>
            <div class="advantage-text">
              <h3>精准专业</h3>
              <p>结合领域文档与知识图谱，为教务相关问题提供准确可靠的答案</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧：注册表单区域 -->
    <div class="register-right">
      <div class="register-box animate-box">
        <div class="register-header">
          <!-- Logo和标题组合 -->
          <div class="title-with-logo">
            <img src="@/assets/logo.png" alt="系统Logo" class="logo-image" />
            <h2 class="register-title">加入我们</h2>
          </div>
          <p class="register-subtitle">创建您的账户开始体验基于GraphRAG的教务信息智能问答服务</p>
        </div>

        <el-form
          ref="registerFormRef"
          :model="registerForm"
          :rules="registerRules"
          label-width="0"
          size="large"
          class="register-form"
        >
          <div class="form-row">
            <el-form-item prop="username" class="form-item-half">
              <el-input
                v-model="registerForm.username"
                placeholder="用户名"
                prefix-icon="User"
                class="register-input"
              />
            </el-form-item>
            <el-form-item prop="realName" class="form-item-half">
              <el-input
                v-model="registerForm.realName"
                placeholder="真实姓名"
                prefix-icon="UserFilled"
                class="register-input"
              />
            </el-form-item>
          </div>

          <el-form-item prop="password">
            <el-input
              v-model="registerForm.password"
              type="password"
              placeholder="设置密码"
              prefix-icon="Lock"
              show-password
              class="register-input"
            />
          </el-form-item>

          <el-form-item prop="confirmPassword">
            <el-input
              v-model="registerForm.confirmPassword"
              type="password"
              placeholder="确认密码"
              prefix-icon="Lock"
              show-password
              class="register-input"
            />
          </el-form-item>

          <div class="form-row">
            <el-form-item prop="phone" class="form-item-half">
              <el-input
                v-model="registerForm.phone"
                placeholder="手机号码"
                prefix-icon="Phone"
                class="register-input"
              />
            </el-form-item>
            <el-form-item prop="email" class="form-item-half">
              <el-input
                v-model="registerForm.email"
                placeholder="邮箱地址"
                prefix-icon="Message"
                class="register-input"
              />
            </el-form-item>
          </div>

          <el-form-item>
            <el-button
              type="primary"
              :loading="loading"
              class="register-button"
              @click="handleRegister"
            >
              <span v-if="!loading">创建账户</span>
              <span v-else>注册中...</span>
            </el-button>
          </el-form-item>
        </el-form>

        <div class="register-footer">
          <div class="register-options">
            <span class="option-text">已有账户？</span>
            <router-link to="/login" class="login-link">
              立即登录
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
  </transition>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { FormInstance } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const router = useRouter()

// 注册表单
const registerForm = ref({
  username: '',
  password: '',
  confirmPassword: '',
  realName: '',
  phone: '',
  email: ''
})

// 表单校验规则
const validatePass2 = (rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.value.password) {
    callback(new Error('两次输入密码不一致!'))
  } else {
    callback()
  }
}

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度应在3-20个字符之间', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度应在6-20个字符之间', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validatePass2, trigger: 'blur' }
  ],
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
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}

const loading = ref(false)
const registerFormRef = ref<FormInstance>()

// 处理注册
const handleRegister = async () => {
  if (!registerFormRef.value) return

  try {
    await registerFormRef.value.validate()
    loading.value = true

    const { confirmPassword, ...registerData } = registerForm.value
    await userStore.register(registerData)

    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch (error) {
    console.error('注册失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  height: 100vh;
  display: flex;
  overflow: hidden;
}

/* 左侧系统介绍区域 */
.register-left {
  flex: 1;
  background: url('@/assets/images/login-bg.jpg') no-repeat center center;
  background-size: cover;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
  box-sizing: border-box;
}

.register-left::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 1;
}

.intro-content {
  position: relative;
  z-index: 2;
  color: white;
  max-width: 500px;
  width: 100%;
}

/* 标题区域 */
.title-section {
  text-align: center;
  margin-bottom: 60px;
}

.system-title {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 12px 0;
  background: linear-gradient(45deg, #fff, #e3f2fd);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.system-subtitle {
  font-size: 16px;
  margin: 0;
  opacity: 0.9;
  font-weight: 300;
}

/* 优势介绍 */
.advantages-section {
  display: grid;
  gap: 24px;
}

.advantage-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px;
  background: rgba(0, 0, 0, 0.4);
  border-radius: 16px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  transition: all 0.2s ease;
}

.advantage-item:hover {
  background: rgba(0, 0, 0, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.advantage-icon {
  font-size: 28px;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  flex-shrink: 0;
}

.advantage-text h3 {
  font-size: 16px;
  margin: 0 0 6px 0;
  font-weight: 600;
}

.advantage-text p {
  font-size: 13px;
  margin: 0;
  opacity: 0.85;
  line-height: 1.5;
}

/* 右侧注册表单区域 */
.register-right {
  width: 500px;
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  box-sizing: border-box;
  box-shadow: -10px 0 50px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
}

.register-box {
  width: 100%;
  max-width: 420px;
}

/* Logo和标题组合 */
.title-with-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 8px;
}

.title-with-logo .logo-image {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  transition: transform 0.2s ease;
  flex-shrink: 0;
}

.title-with-logo .logo-image:hover {
  transform: scale(1.05);
}

.title-with-logo .register-title {
  margin: 0;
}

.animate-box {
  animation: slideInRight 0.35s cubic-bezier(0.25, 0.8, 0.25, 1) 0.1s both;
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.animate-intro {
  animation: slideInLeft 0.35s cubic-bezier(0.25, 0.8, 0.25, 1) both;
}

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.register-header {
  text-align: center;
  margin-bottom: 32px;
}

.register-title {
  font-size: 28px;
  font-weight: 700;
  color: #2c3e50;
}

.register-subtitle {
  font-size: 13px;
  color: #64748b;
  margin: 0;
  line-height: 1.5;
}

.register-form {
  margin-bottom: 24px;
}

.form-row {
  display: flex;
  gap: 12px;
  margin-bottom: 4px;
}

.form-item-half {
  flex: 1;
}

.register-input {
  margin-bottom: 4px;
}

.register-input :deep(.el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
  padding: 10px 14px;
}

.register-input :deep(.el-input__wrapper:hover) {
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(82, 196, 26, 0.15);
}

.register-input :deep(.el-input__wrapper.is-focus) {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(82, 196, 26, 0.1);
}

.register-button {
  width: 100%;
  height: 46px;
  border-radius: 10px;
  background: var(--gradient-primary);
  border: none;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.5px;
  transition: all 0.2s ease;
  box-shadow: var(--shadow-md);
  margin-top: 12px;
  color: white;
}

.register-button:hover {
  background: var(--gradient-light);
  transform: translateY(-2px);
  box-shadow: var(--shadow-hover);
}

.register-button:active {
  transform: translateY(0);
  box-shadow: var(--button-active-shadow);
}

.register-footer {
  text-align: center;
}

.register-options {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.option-text {
  color: #64748b;
  font-size: 14px;
}

.login-link {
  color: var(--link-color);
  text-decoration: none;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.2s ease;
}

.login-link:hover {
  color: var(--link-hover-color);
  text-decoration: underline;
}

/* 页面切换动画 */
.page-slide-enter-active,
.page-slide-leave-active {
  transition: all 0.25s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.page-slide-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.page-slide-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .register-left {
    display: none;
  }

  .register-right {
    width: 100%;
  }
}

@media (max-width: 640px) {
  .register-right {
    padding: 32px 24px;
  }

  .register-title {
    font-size: 24px;
  }

  .register-subtitle {
    font-size: 12px;
  }

  .form-row {
    flex-direction: column;
    gap: 0;
  }

  .form-item-half {
    width: 100%;
  }
}
</style>
