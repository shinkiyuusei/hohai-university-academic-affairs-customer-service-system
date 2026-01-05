
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/user/Login.vue'),
    meta: {
      title: '登录',
      requiresAuth: false
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/user/Register.vue'),
    meta: {
      title: '注册',
      requiresAuth: false
    }
  },
  {
    path: '/',
    component: () => import('@/components/Layout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: {
          title: '首页',
          requiresAuth: true
        }
      },
      {
        path: 'qa',
        name: 'QAChat',
        component: () => import('@/views/QAChat.vue'),
        meta: {
          title: '智能问答',
          requiresAuth: true
        }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/user/Profile.vue'),
        meta: {
          title: '个人中心',
          requiresAuth: true
        }
      }
    ]
  },
  {
    path: '/admin',
    component: () => import('@/components/Layout.vue'),
    meta: {
      requiresAuth: true,
      requiresAdmin: true
    },
    children: [
      {
        path: '',
        name: 'Admin',
        component: () => import('@/views/admin/Dashboard.vue'),
        meta: {
          title: '管理控制台',
          requiresAuth: true,
          requiresAdmin: true
        }
      },
      {
        path: 'users',
        name: 'UserManagement',
        component: () => import('@/views/admin/UserManagement.vue'),
        meta: {
          title: '用户管理',
          requiresAuth: true,
          requiresAdmin: true
        }
      },
      {
        path: 'documents',
        name: 'DocumentManagement',
        component: () => import('@/views/admin/DocumentManagement.vue'),
        meta: {
          title: '文档管理',
          requiresAuth: true,
          requiresAdmin: true
        }
      },
      {
        path: 'knowledge-graph',
        name: 'KnowledgeGraphManagement',
        component: () => import('@/views/admin/KnowledgeGraphManagement.vue'),
        meta: {
          title: '知识图谱管理',
          requiresAuth: true,
          requiresAdmin: true
        }
      },
      {
        path: 'graph-visualization',
        name: 'KnowledgeGraphVisualization',
        component: () => import('@/views/admin/KnowledgeGraphVisualization.vue'),
        meta: {
          title: '图谱可视化',
          requiresAuth: true,
          requiresAdmin: true
        }
      },
      {
        path: 'academic-policy',
        name: 'AcademicPolicyManagement',
        component: () => import('@/views/admin/AcademicPolicyManagement.vue'),
        meta: {
          title: '教务政策管理',
          requiresAuth: true,
          requiresAdmin: true
        }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
// 导航守卫实现 - 基于用户权限进行路由拦截
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresAdmin = to.matched.some(record => record.meta.requiresAdmin)

  // 设置页面标题
  document.title = `${to.meta.title} - 河海大学教务知识图谱系统`

  if (requiresAuth) {
    if (!userStore.isLoggedIn()) {
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }

    if (requiresAdmin && !userStore.isAdmin()) {
      next({ name: 'Dashboard' })
      return
    }
  }

  next()
})

export default router
