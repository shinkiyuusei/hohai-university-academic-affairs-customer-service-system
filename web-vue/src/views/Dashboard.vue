<!-- MD5: auto_generated -->
<!-- 仪表盘页面 -->

<template>
  <div class="dashboard">
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <div class="welcome-content">
        <div class="welcome-text">
          <h1 class="welcome-title">
            <img src="@/assets/images/logo.png" alt="Logo" class="welcome-logo" />
            欢迎使用教务信息知识图谱系统
          </h1>
          <p class="welcome-subtitle">您好，{{ userInfo?.realName || userInfo?.username }}</p>
          <p class="welcome-description">
            专业的教务信息管理平台，致力于通过先进的GraphRAG技术提供精准的教务知识检索，
            结合知识图谱和信息文档，为教务管理提供专业的技术支持和解决方案。
          </p>
          <div class="welcome-stats">
            <div class="stat-item">
              <span class="stat-number">{{ todayDate }}</span>
              <span class="stat-label">今日日期</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">{{ isAdmin ? '管理员' : '用户' }}</span>
              <span class="stat-label">当前身份</span>
            </div>
          </div>
        </div>
        <div class="welcome-illustration">
          <div class="illustration-circle">
            <div class="background-image"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 功能介绍 -->
    <div class="features-section">
      <div class="section-header">
        <h2>核心功能</h2>
        <p>探索我们为教务信息检索提供的专业智能工具</p>
      </div>

      <div class="feature-cards" :class="{ 'two-cards': !isAdmin }">
        <div class="feature-card" @click="goToQA">
          <div class="card-icon qa-icon">
            <el-icon size="32"><ChatDotRound /></el-icon>
          </div>
          <h3>智能问答</h3>
          <p>基于GraphRAG技术的智能问答系统，快速检索知识图谱和教务文档，为您提供精准的教务信息和防治方案。</p>
          <div class="card-footer">
            <span class="action-text">开始咨询</span>
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>

        <div v-if="isAdmin" class="feature-card" @click="goToDocuments">
          <div class="card-icon doc-icon">
            <el-icon size="32"><Document /></el-icon>
          </div>
          <h3>文档管理</h3>
          <p>管理教务政策相关文档，支持文档上传、知识提取，建立完整的教务资料体系，便于知识积累和查询。</p>
          <div class="card-footer">
            <span class="action-text">管理文档</span>
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>

        <div class="feature-card" @click="goToProfile">
          <div class="card-icon profile-icon">
            <el-icon size="32"><Setting /></el-icon>
          </div>
          <h3>个人中心</h3>
          <p>管理个人信息、账户设置，查看使用记录，个性化定制您的使用体验，让系统更好地为您服务。</p>
          <div class="card-footer">
            <span class="action-text">进入设置</span>
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
      </div>
    </div>

    <!-- 系统优势 -->
    <div class="advantages-section">
      <div class="section-header">
        <h2>系统优势</h2>
        <p>为什么选择我们的专业平台</p>
      </div>

      <div class="advantages-grid">
        <div class="advantage-item">
          <div class="advantage-icon">
            <div class="icon-bg ai-bg">🤖</div>
          </div>
          <h4>AI智能检索</h4>
          <p>采用BGE向量模型和FAISS检索技术，确保知识检索的准确性和高效性</p>
        </div>

        <div class="advantage-item">
          <div class="advantage-icon">
            <div class="icon-bg case-bg">📋</div>
          </div>
          <h4>案例库支持</h4>
          <p>整合历史教学案例，提供实际教学进度预案，加快教务教学的效率</p>
        </div>

        <div class="advantage-item">
          <div class="advantage-icon">
            <div class="icon-bg professional-bg">🌱</div>
          </div>
          <h4>专业可靠</h4>
          <p>基于教学背景，基于知识图谱进行智能问答，提供专业、可靠、高效、精准的教务知识检索</p>
        </div>

        <div class="advantage-item">
          <div class="advantage-icon">
            <div class="icon-bg easy-bg">⚡</div>
          </div>
          <h4>快速响应</h4>
          <p>秒级响应查询，快速定位问题，提高维修效率和质量</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ChatDotRound, Document, Setting, ArrowRight } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

// 用户信息
const userInfo = computed(() => userStore.userInfo)

// 是否是管理员
const isAdmin = computed(() => userStore.isAdmin())

// 今日日期
const todayDate = new Date().toLocaleDateString('zh-CN', {
  month: '2-digit',
  day: '2-digit'
})

// 跳转到智能问答页面
const goToQA = () => {
  router.push('/qa')
}

// 跳转到文档管理页面
const goToDocuments = () => {
  if (isAdmin.value) {
    router.push('/admin/documents')
  } else {
    router.push('/qa')
  }
}

// 跳转到个人中心
const goToProfile = () => {
  router.push('/profile')
}
</script>

<style scoped lang="scss">
.dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #ffffff 50%, #f1f5f9 100%);
  position: relative;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background:
      radial-gradient(circle at 10% 20%, rgba(82, 196, 26, 0.03) 0%, transparent 50%),
      radial-gradient(circle at 90% 80%, rgba(82, 196, 26, 0.04) 0%, transparent 50%);
    pointer-events: none;
  }
}

// 欢迎区域
.welcome-section {
  padding: 48px 0 64px;
  position: relative;
  z-index: 1;

  .welcome-content {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 24px;
    display: grid;
    grid-template-columns: 1fr 300px;
    gap: 48px;
    align-items: center;
  }

  .welcome-text {
    .welcome-title {
      font-size: 2.5rem;
      font-weight: 700;
      color: #1e293b;
      margin: 0 0 16px 0;
      display: flex;
      align-items: center;
      gap: 16px;

      .welcome-logo {
        width: 48px;
        height: 48px;
        border-radius: 12px;
      }
    }

    .welcome-subtitle {
      font-size: 1.25rem;
      color: var(--primary-color);
      margin: 0 0 20px 0;
      font-weight: 500;
    }

    .welcome-description {
      font-size: 1.1rem;
      color: #64748b;
      line-height: 1.7;
      margin: 0 0 32px 0;
      max-width: 600px;
    }

    .welcome-stats {
      display: flex;
      gap: 32px;

      .stat-item {
        text-align: center;

        .stat-number {
          display: block;
          font-size: 1.5rem;
          font-weight: 700;
          color: #1e293b;
          margin-bottom: 4px;
        }

        .stat-label {
          font-size: 0.875rem;
          color: #64748b;
          font-weight: 500;
        }
      }
    }
  }

  .welcome-illustration {
    display: flex;
    justify-content: center;
    align-items: center;

    .illustration-circle {
      width: 240px;
      height: 240px;
      border-radius: 50%;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
      position: relative;
      overflow: hidden;
      border: 3px solid #ffffff;

      .background-image {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: url('@/assets/images/login-bg.jpg');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
      }
    }
  }
}

// 功能介绍区域
.features-section {
  padding: 64px 0;
  position: relative;
  z-index: 1;

  .section-header {
    text-align: center;
    max-width: 600px;
    margin: 0 auto 48px;
    padding: 0 24px;

    h2 {
      font-size: 2.25rem;
      font-weight: 700;
      color: #1e293b;
      margin: 0 0 16px 0;
    }

    p {
      font-size: 1.125rem;
      color: #64748b;
      margin: 0;
      line-height: 1.6;
    }
  }

  .feature-cards {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 24px;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 24px;

    &.two-cards {
      max-width: 800px;
    }
  }

  .feature-card {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(10px);
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 32px;
    cursor: pointer;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;

    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 4px;
      background: var(--gradient-primary);
      transform: scaleX(0);
      transition: transform 0.3s ease;
    }

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 12px 40px rgba(0, 0, 0, 0.1);
      border-color: #cbd5e1;

      &::before {
        transform: scaleX(1);
      }

      .card-icon {
        transform: scale(1.1);
      }
    }

    .card-icon {
      width: 64px;
      height: 64px;
      border-radius: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 20px;
      transition: transform 0.3s ease;

      &.qa-icon {
        background: var(--gradient-primary);
        color: white;
      }

      &.doc-icon {
        background: linear-gradient(135deg, #52c41a, #389e0d);
        color: white;
      }

      &.profile-icon {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white;
      }
    }

    h3 {
      font-size: 1.25rem;
      font-weight: 600;
      color: #1e293b;
      margin: 0 0 12px 0;
    }

    p {
      color: #64748b;
      line-height: 1.6;
      margin: 0 0 24px 0;
      font-size: 0.95rem;
    }

    .card-footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      color: var(--primary-color);
      font-weight: 500;
      font-size: 0.9rem;

      .action-text {
        margin-right: 8px;
      }
    }
  }
}

// 系统优势区域
.advantages-section {
  padding: 64px 0;
  background: rgba(255, 255, 255, 0.5);
  position: relative;
  z-index: 1;

  .section-header {
    text-align: center;
    max-width: 600px;
    margin: 0 auto 48px;
    padding: 0 24px;

    h2 {
      font-size: 2.25rem;
      font-weight: 700;
      color: #1e293b;
      margin: 0 0 16px 0;
    }

    p {
      font-size: 1.125rem;
      color: #64748b;
      margin: 0;
      line-height: 1.6;
    }
  }

  .advantages-grid {
    max-width: 1000px;
    margin: 0 auto;
    padding: 0 24px;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 32px;
  }

  .advantage-item {
    text-align: center;

    .advantage-icon {
      margin-bottom: 20px;

      .icon-bg {
        width: 80px;
        height: 80px;
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        margin: 0 auto;

        &.ai-bg {
          background: var(--gradient-primary);
        }

        &.case-bg {
          background: linear-gradient(135deg, #52c41a, #389e0d);
        }

        &.professional-bg {
          background: linear-gradient(135deg, #73d13d, #52c41a);
        }

        &.easy-bg {
          background: linear-gradient(135deg, #f59e0b, #d97706);
        }
      }
    }

    h4 {
      font-size: 1.125rem;
      font-weight: 600;
      color: #1e293b;
      margin: 0 0 12px 0;
    }

    p {
      color: #64748b;
      line-height: 1.6;
      margin: 0;
      font-size: 0.95rem;
    }
  }
}

// 响应式设计
@media (max-width: 1024px) {
  .welcome-section .welcome-content {
    grid-template-columns: 1fr;
    text-align: center;
    gap: 32px;
  }

  .welcome-section .welcome-title {
    font-size: 2rem;
  }

  .features-section .feature-cards {
    grid-template-columns: 1fr;
    max-width: 500px;
  }

  .advantages-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .welcome-section .welcome-title {
    font-size: 1.75rem;
    flex-direction: column;
    gap: 12px;
  }

  .welcome-section .welcome-stats {
    justify-content: center;
  }

  .advantages-grid {
    grid-template-columns: 1fr;
  }

  .section-header h2 {
    font-size: 1.75rem;
  }
}
</style>
