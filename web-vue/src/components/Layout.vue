
<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '200px'" class="aside">
      <div class="logo" :class="{ 'logo-collapse': isCollapse }">
        <img src="@/assets/images/logo.png" alt="logo" />
        <span v-show="!isCollapse">河海大学校务知识系统</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="menu"
        :router="true"
        :collapse="isCollapse"
        background-color="transparent"
        text-color="#64748b"
        active-text-color="#52c41a"
      >
        <!-- 普通用户菜单 -->
        <template v-if="!isAdmin">
          <el-menu-item index="/dashboard">
            <el-icon><Monitor /></el-icon>
            <template #title>首页</template>
          </el-menu-item>
          <el-menu-item index="/qa">
            <el-icon><ChatDotRound /></el-icon>
            <template #title>智能问答</template>
          </el-menu-item>
          <el-menu-item index="/profile">
            <el-icon><User /></el-icon>
            <template #title>个人中心</template>
          </el-menu-item>
        </template>

        <!-- 管理员菜单 -->
        <template v-else>
          <el-menu-item index="/admin">
            <el-icon><Monitor /></el-icon>
            <template #title>控制台</template>
          </el-menu-item>
          <el-menu-item index="/qa">
            <el-icon><ChatDotRound /></el-icon>
            <template #title>智能问答</template>
          </el-menu-item>
          <el-menu-item index="/admin/users">
            <el-icon><User /></el-icon>
            <template #title>用户管理</template>
          </el-menu-item>
          <el-menu-item index="/admin/documents">
            <el-icon><Document /></el-icon>
            <template #title>文档管理</template>
          </el-menu-item>
          <el-menu-item index="/admin/knowledge-graph">
            <el-icon><Connection /></el-icon>
            <template #title>图谱管理</template>
          </el-menu-item>
          <el-menu-item index="/admin/graph-visualization">
            <el-icon><Connection /></el-icon>
            <template #title>图谱可视化</template>
          </el-menu-item>
          <el-menu-item index="/admin/plant-disease">
            <el-icon><Grape /></el-icon>
            <template #title>植物病害</template>
          </el-menu-item>
          <el-menu-item index="/admin/disease-case">
            <el-icon><WarningFilled /></el-icon>
            <template #title>病害案例</template>
          </el-menu-item>
        </template>
      </el-menu>
    </el-aside>

    <!-- 主要内容区 -->
    <el-container>
      <!-- 头部 -->
      <el-header class="header">
        <div class="header-left">
          <el-icon
            class="collapse-btn"
            @click="toggleCollapse"
          >
            <Fold v-if="!isCollapse" />
            <Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ route.meta.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <AlgoHealthCheck class="health-check" />
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="32" :src="userInfo?.avatarUrl" />
              <span>{{ userInfo?.username }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 内容区 -->
      <el-main class="main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { Monitor, User, Fold, Expand, Document, ChatDotRound, Connection, Grape, WarningFilled } from '@element-plus/icons-vue'
import AlgoHealthCheck from './AlgoHealthCheck.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 计算当前激活的菜单项
const activeMenu = computed(() => route.path)

// 用户信息
const userInfo = computed(() => userStore.userInfo)

// 是否是管理员
const isAdmin = computed(() => userStore.isAdmin())

// 侧边栏折叠状态
const isCollapse = ref(false)

// 切换侧边栏折叠状态
const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

// 处理下拉菜单命令
const handleCommand = (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'logout':
      userStore.logout()
      break
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
  overflow: hidden;
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
}

.aside {
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 50%, #f1f5f9 100%);
  border-right: 1px solid #e2e8f0;
  transition: width 0.3s;
  overflow: hidden;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.08);
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 16px;
  color: #1e293b;
  transition: all 0.3s;
  overflow: hidden;
  white-space: nowrap;
  border-bottom: 1px solid #e2e8f0;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  font-weight: 600;
  font-size: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.logo-collapse {
  padding: 0 16px;
}

.logo img {
  width: 32px;
  height: 32px;
  margin-right: 10px;
  flex-shrink: 0;
  border-radius: 6px;
  display: block;
}

.logo span {
  display: inline-block;
  line-height: 32px;
  vertical-align: middle;
}

.menu {
  border-right: none;
  background-color: transparent;
  padding: 8px;
}

.menu:not(.el-menu--collapse) {
  width: 200px;
}

:deep(.el-menu--collapse) {
  width: 64px;
}

:deep(.el-menu-item) {
  margin: 4px 0;
  border-radius: 8px;
  transition: all 0.2s ease;
  background: rgba(255, 255, 255, 0.3);
  border: 1px solid transparent;

  &.is-active {
    background: var(--gradient-primary);
    color: #ffffff !important;
    border-color: rgba(255, 255, 255, 0.2);
    box-shadow: 0 2px 8px rgba(82, 196, 26, 0.3);

    .el-icon {
      color: #ffffff !important;
    }
  }

  &:hover:not(.is-active) {
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    color: var(--primary-color);
    border-color: #e2e8f0;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);

    .el-icon {
      color: var(--primary-color);
    }
  }

  .el-icon {
    color: #64748b;
    transition: color 0.2s ease;
  }
}

.header {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 50%, #f1f5f9 100%);
  border-bottom: 1px solid #cbd5e1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  flex-shrink: 0;
  height: 64px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(10px);
}

.header-left {
  display: flex;
  align-items: center;
}

.collapse-btn {
  font-size: 18px;
  cursor: pointer;
  margin-right: 20px;
  transition: all 0.2s ease;
  color: #64748b;
  padding: 8px;
  border-radius: 6px;

  &:hover {
    background-color: #f1f5f9;
    color: var(--primary-color);
    transform: scale(1.1);
  }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.health-check {
  margin-right: 8px;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 8px;
  transition: all 0.2s ease;
  color: #1e293b;
  font-weight: 500;

  &:hover {
    background-color: #f1f5f9;
  }
}

.user-info span {
  margin-left: 10px;
  font-size: 14px;
}

:deep(.el-avatar) {
  border: 2px solid #e2e8f0;
  transition: border-color 0.2s ease;
}

.user-info:hover :deep(.el-avatar) {
  border-color: var(--primary-color);
}

.main {
  background: linear-gradient(135deg, #f1f5f9 0%, #ffffff 25%, #f8fafc 50%, #ffffff 75%, #f1f5f9 100%);
  padding: 24px;
  overflow-y: auto;
  height: calc(100vh - 64px);
  position: relative;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background:
      radial-gradient(circle at 20% 20%, rgba(82, 196, 26, 0.02) 0%, transparent 50%),
      radial-gradient(circle at 80% 80%, rgba(82, 196, 26, 0.03) 0%, transparent 50%);
    pointer-events: none;
  }
}

/* 面包屑样式 */
:deep(.el-breadcrumb) {
  .el-breadcrumb__item {
    .el-breadcrumb__inner {
      color: #64748b;
      font-weight: 400;

      &:hover {
        color: var(--primary-color);
      }
    }

    &:last-child .el-breadcrumb__inner {
      color: #1e293b;
      font-weight: 500;
    }
  }

  .el-breadcrumb__separator {
    color: #94a3b8;
  }
}

/* 下拉菜单样式 */
:deep(.el-dropdown-menu) {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);

  .el-dropdown-menu__item {
    color: #64748b;
    transition: all 0.2s ease;

    &:hover {
      background-color: #f1f5f9;
      color: var(--primary-color);
    }
  }
}

/* 路由过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
