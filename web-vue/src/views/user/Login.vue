
<template>
  <transition name="page-slide" appear>
    <div class="login-container">
    <!-- 左侧：系统介绍区域 -->
    <div class="login-left">
      <div class="intro-content animate-intro">
        <!-- 系统标题区域 -->
        <div class="title-section">
          <h1 class="system-title">教务信息知识问答系统</h1>
          <p class="system-subtitle">基于GraphRAG技术的教务智能问答平台</p>
        </div>

        <!-- 功能特色 -->
        <div class="features-section">
          <div class="feature-item">
            <div class="feature-icon">🌀</div>
            <div class="feature-text">
              <h3>知识图谱</h3>
              <p>基于Neo4j构建教务信息领域知识图谱</p>
            </div>
          </div>
          <div class="feature-item">
            <div class="feature-icon">🕸️</div>
            <div class="feature-text">
              <h3>图谱可视化</h3>
              <p>交互式的知识图谱展示，支持节点搜索</p>
            </div>
          </div>
          <div class="feature-item">
            <div class="feature-icon">🤖</div>
            <div class="feature-text">
              <h3>智能问答</h3>
              <p>GraphRAG检索增强，提供精准的教务信息</p>
            </div>
          </div>
          <div class="feature-item">
            <div class="feature-icon">📄</div>
            <div class="feature-text">
              <h3>文档管理</h3>
              <p>支持多格式文档上传，自动提取实体关系</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧：登录表单区域 -->
    <div class="login-right">
      <div class="login-box animate-box">
        <div class="login-header">
          <!-- Logo和标题组合 -->
          <div class="title-with-logo">
            <img src="@/assets/logo.png" alt="系统Logo" class="logo-image" />
            <h2 class="login-title">欢迎回来</h2>
          </div>
          <p class="login-subtitle">请登录您的账户以继续使用系统</p>
        </div>

        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          label-width="0"
          size="large"
          class="login-form"
        >
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入用户名"
              prefix-icon="User"
              class="login-input"
            />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              prefix-icon="Lock"
              show-password
              class="login-input"
              @keyup.enter="handleLogin"
            />
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              :loading="loading"
              class="login-button"
              @click="handleLogin"
            >
              <span v-if="!loading">立即登录</span>
              <span v-else>登录中...</span>
            </el-button>
          </el-form-item>
        </el-form>

        <div class="login-footer">
          <div class="login-options">
            <span class="option-text">还没有账户？</span>
            <router-link to="/register" class="register-link">
              立即注册
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
import { useRoute, useRouter } from 'vue-router'

const userStore = useUserStore()
const route = useRoute()
const router = useRouter()

// 登录表单
const loginForm = ref({
  username: '',
  password: ''
})

// 表单校验规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度应在3-20个字符之间', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度应在6-20个字符之间', trigger: 'blur' }
  ]
}

const loading = ref(false)
const loginFormRef = ref<FormInstance>()

// 处理登录
const handleLogin = async () => {
  if (!loginFormRef.value) return

  try {
    await loginFormRef.value.validate()
    loading.value = true

    await userStore.login(loginForm.value.username, loginForm.value.password)

    // 如果有重定向地址，则跳转到重定向地址
    const redirect = route.query.redirect as string
    router.replace(redirect || '/')
  } catch (error) {
    console.error('登录失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  overflow: hidden;
}

/* 左侧系统介绍区域 */
.login-left {
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

.login-left::before {
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

/* 功能特色 */
.features-section {
  display: grid;
  gap: 24px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: rgba(0, 0, 0, 0.4);
  border-radius: 16px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  transition: all 0.2s ease;
}

.feature-item:hover {
  background: rgba(0, 0, 0, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.feature-icon {
  font-size: 32px;
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  flex-shrink: 0;
}

.feature-text h3 {
  font-size: 18px;
  margin: 0 0 4px 0;
  font-weight: 600;
}

.feature-text p {
  font-size: 14px;
  margin: 0;
  opacity: 0.8;
  line-height: 1.5;
}

/* 右侧登录表单区域 */
.login-right {
  width: 480px;
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
  box-sizing: border-box;
  box-shadow: -10px 0 50px rgba(0, 0, 0, 0.1);
}

.login-box {
  width: 100%;
  max-width: 360px;
}

/* Logo和标题组合 */
.title-with-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 8px;
}

.title-with-logo .logo-image {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  transition: transform 0.2s ease;
  flex-shrink: 0;
}

.title-with-logo .logo-image:hover {
  transform: scale(1.05);
}

.title-with-logo .login-title {
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

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-title {
  font-size: 28px;
  font-weight: 700;
  color: #2c3e50;
}

.login-subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
  line-height: 1.5;
}

.login-form {
  margin-bottom: 32px;
}

.login-input {
  margin-bottom: 4px;
}

.login-input :deep(.el-input__wrapper) {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
  padding: 12px 16px;
}

.login-input :deep(.el-input__wrapper:hover) {
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(82, 196, 26, 0.15);
}

.login-input :deep(.el-input__wrapper.is-focus) {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(82, 196, 26, 0.1);
}

.login-button {
  width: 100%;
  height: 48px;
  border-radius: 12px;
  background: var(--gradient-primary);
  border: none;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.5px;
  transition: all 0.2s ease;
  box-shadow: var(--shadow-md);
  color: white;
}

.login-button:hover {
  background: var(--gradient-light);
  transform: translateY(-2px);
  box-shadow: var(--shadow-hover);
}

.login-button:active {
  transform: translateY(0);
  box-shadow: var(--button-active-shadow);
}

.login-footer {
  text-align: center;
}

.login-options {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.option-text {
  color: #64748b;
  font-size: 14px;
}

.register-link {
  color: var(--link-color);
  text-decoration: none;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.2s ease;
}

.register-link:hover {
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
  .login-left {
    display: none;
  }

  .login-right {
    width: 100%;
  }
}

@media (max-width: 640px) {
  .login-right {
    padding: 32px 24px;
  }

  .login-title {
    font-size: 24px;
  }

  .login-subtitle {
    font-size: 13px;
  }
}
</style>
