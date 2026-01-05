<!-- 智能问答页面 -->


<template>
  <div class="qa-chat-container">
    <!-- 左侧会话列表 -->
    <div :class="['conversation-sidebar', { collapsed: sidebarCollapsed }]">
      <div class="sidebar-header">
        <span class="sidebar-title" v-show="!sidebarCollapsed">会话列表</span>
        <div class="header-actions">
          <el-button
            v-show="!sidebarCollapsed"
            type="primary"
            :icon="Plus"
            size="small"
            @click="handleCreateConversation"
            circle
            title="新建会话"
          />
          <el-button
            :icon="sidebarCollapsed ? DArrowRight : DArrowLeft"
            size="small"
            @click="toggleSidebar"
            circle
            title="折叠/展开"
          />
        </div>
      </div>

      <div class="conversation-list">
        <div
          v-for="conv in conversationList"
          :key="conv.id"
          :class="['conversation-item', { active: currentConversationId === conv.id }]"
          @click="handleSwitchConversation(conv.id)"
        >
          <div class="conversation-info">
            <div class="conversation-title">{{ conv.title }}</div>
            <div class="conversation-time">{{ formatTime(conv.update_time) }}</div>
          </div>
          <div class="conversation-actions">
            <el-icon @click.stop="handleRenameConversation(conv)" class="action-icon">
              <Edit />
            </el-icon>
            <el-icon @click.stop="handleDeleteConversation(conv.id)" class="action-icon">
              <Delete />
            </el-icon>
          </div>
        </div>

        <div v-if="!conversationList || conversationList.length === 0" class="empty-conversations">
          <el-icon><ChatDotRound /></el-icon>
          <p>暂无会话,点击右上角创建新会话</p>
        </div>
      </div>
    </div>

    <!-- 右侧聊天区域 -->
    <div class="chat-main">
      <el-card class="chat-card">
        <!-- 页面标题 -->
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <el-icon><ChatDotRound /></el-icon>
              {{ currentConversationTitle }}
            </span>
            <div v-if="currentConversationId && messages.length > 0" class="header-buttons">
              <el-button
                type="primary"
                :icon="Promotion"
                size="small"
                @click="handleGenerateTitle"
              >
                生成标题
              </el-button>
              <el-button
                type="danger"
                :icon="Delete"
                size="small"
                @click="handleClearMessages"
                plain
              >
                清除记录
              </el-button>
            </div>
          </div>
        </template>

        <!-- 聊天区域 -->
        <div class="chat-area">
          <!-- 欢迎提示 -->
          <div v-if="messages.length === 0" class="welcome-message">
            <el-icon class="welcome-icon"><ChatDotRound /></el-icon>
            <h3>欢迎使用河海大学校务智能问答系统</h3>
            <p>我可以基于校务知识图谱回答您的问题</p>
            <div class="example-questions">
              <p class="example-title">您可以问我:</p>
              <div class="example-question" @click="askExample('高数一教学安排有哪些?')">
                <el-icon><Document /></el-icon>
                <span>高数一教学安排有哪些?</span>
              </div>
              <div class="example-question" @click="askExample('校务处具体电话是多少?')">
                <el-icon><Document /></el-icon>
                <span>校务处具体电话是多少?</span>
              </div>
              <div class="example-question" @click="askExample('选修课选课时间具体是什么时候?')">
                <el-icon><Document /></el-icon>
                <span>选修课选课时间具体是什么时候?</span>
              </div>
            </div>
          </div>

          <!-- 对话消息列表 -->
          <div class="message-list" ref="messageListRef">
            <div
              v-for="(msg, index) in messages"
              :key="index"
              :class="['message-item', msg.type]"
            >
              <!-- 助手消息：头像在左，内容在右 -->
              <template v-if="msg.type === 'assistant'">
                <div class="message-avatar">
                  <el-avatar :size="32" :src="logoImage" style="background-color: #fff;">
                  </el-avatar>
                </div>
                <div class="message-content">
                <!-- 显示图片 -->
                <div v-if="msg.image_url" class="message-image">
                  <el-image
                    :src="msg.image_url"
                    fit="contain"
                    style="max-width: 300px; max-height: 300px; border-radius: 8px;"
                    :preview-src-list="[msg.image_url]"
                    preview-teleported
                  />
                </div>
                <div class="message-text" v-html="formatMessage(msg.content)"></div>
                <div
                  v-if="msg.keywords && msg.keywords.length"
                  class="keywords-section"
                >
                  <el-divider content-position="left">
                    <el-icon><Tickets /></el-icon>
                    关键词
                  </el-divider>
                  <div class="tag-list">
                    <el-tag
                      v-for="(keyword, keyIndex) in msg.keywords"
                      :key="`${keyword}-${keyIndex}`"
                      size="small"
                      effect="plain"
                    >
                      {{ keyword }}
                    </el-tag>
                  </div>
                </div>





                <!-- 显示相关图谱实体 -->
                <div v-if="msg.related_entities && msg.related_entities.length > 0" class="related-entities">
                  <el-divider content-position="left">
                    <el-icon><Connection /></el-icon>
                    相关知识图谱实体 ({{ msg.related_entities.length }})
                  </el-divider>
                  <div class="entity-tags">
                    <el-tag
                      v-for="(entity, entityIndex) in msg.related_entities.slice(0, 10)"
                      :key="entityIndex"
                      :type="getEntityTagType(entity.type)"
                      size="default"
                      class="entity-tag"
                      :title="`${entity.type}: ${entity.name}`"
                    >
                      <strong>{{ entity.type }}:</strong> {{ entity.name }}
                    </el-tag>
                  </div>
                </div>
                <!-- 显示知识图谱三元组上下文 -->
                <div v-if="msg.graph_context" class="graph-context">
                  <el-divider content-position="left">
                    <el-icon><Connection /></el-icon>
                    知识图谱关联关系
                  </el-divider>
                  <div class="context-content">
                    <pre>{{ msg.graph_context }}</pre>
                  </div>
                </div>
              </div>
              </template>

              <!-- 用户消息：内容在左，头像在右 -->
              <template v-else>
                <div class="message-content">
                  <!-- 显示图片 -->
                  <div v-if="msg.image_url" class="message-image">
                    <el-image
                      :src="msg.image_url"
                      fit="contain"
                      style="max-width: 300px; max-height: 300px; border-radius: 8px;"
                      :preview-src-list="[msg.image_url]"
                      preview-teleported
                    />
                  </div>
                  <div class="message-text" v-html="formatMessage(msg.content)"></div>
                </div>
                <div class="message-avatar">
                  <el-avatar :size="32" :src="userAvatar">
                    <el-icon v-if="!userAvatar"><User /></el-icon>
                  </el-avatar>
                </div>
              </template>
            </div>

            <!-- 加载提示 -->
            <div v-if="loading" class="message-item assistant loading">
              <div class="message-avatar">
                <el-avatar :size="32" :src="logoImage" style="background-color: #fff;">
                </el-avatar>
              </div>
              <div class="message-content">
                <div class="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="input-area">
          <!-- 图片预览 -->
          <div v-if="imagePreviewUrl" class="image-preview-container">
            <div class="image-preview">
              <img :src="imagePreviewUrl" alt="上传的图片" />
              <el-icon class="remove-image" @click="handleRemoveImage">
                <Delete />
              </el-icon>
            </div>
          </div>

          <el-input
            v-model="question"
            type="textarea"
            :rows="3"
            placeholder="请输入您的问题..."
            :disabled="loading || !currentConversationId"
            @keydown.enter.ctrl="handleAsk"
          />
          <div class="input-actions">
            <div class="left-actions">
              <input
                type="file"
                ref="imageInputRef"
                accept="image/*"
                style="display: none"
                @change="handleImageUpload"
              />
              <el-button
                :icon="Picture"
                size="small"
                :disabled="loading || !currentConversationId"
                @click="imageInputRef?.click()"
                title="上传图片"
              >
                上传图片
              </el-button>
            </div>
            <div class="right-actions">
              <span class="input-tip">{{ currentConversationId ? '按 Ctrl+Enter 发送' : '请先创建或选择会话' }}</span>
              <el-button
                type="success"
                :icon="Promotion"
                :loading="loading"
                :disabled="!question.trim() || !currentConversationId"
                @click="handleAsk"
              >
                {{ loading ? '思考中...' : '发送问题' }}
              </el-button>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 重命名对话框 -->
    <el-dialog
      v-model="showRenameDialog"
      title="重命名会话"
      width="400px"
      :close-on-click-modal="false"
    >
      <el-input
        v-model="renameTitle"
        placeholder="请输入新的会话名称"
        maxlength="50"
        show-word-limit
      />
      <template #footer>
        <el-button @click="showRenameDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmRename">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ChatDotRound,
  User,
  Document,
  Promotion,
  Plus,
  Edit,
  Delete,
  Picture,
  DArrowLeft,
  DArrowRight,
  Connection,
  Tickets
} from '@element-plus/icons-vue'
import {
  askQuestion,
  getConversationList,
  createConversation,
  deleteConversation,
  renameConversation,
  getConversationMessages,
  clearConversationMessages,
  generateConversationTitle,
  type Conversation,
  type ConversationMessage
} from '@/api/qa'
import { marked } from 'marked'
import { useUserStore } from '@/stores/user'
import logoImage from '@/assets/images/logo.png'
import { fileRequest } from '@/api/file_request'

// 获取用户信息
const userStore = useUserStore()
const userAvatar = computed(() => userStore.userInfo?.avatarUrl || '')

// 消息类型定义
interface Message {
  type: 'user' | 'assistant'
  content: string
  related_entities?: RelatedEntity[]  // 相关知识图谱实体
  graph_context?: string  // 知识图谱三元组上下文
  image_url?: string  // 图片URL
  keywords?: string[]
}

// 知识图谱实体类型
interface RelatedEntity {
  name: string
  type: string
  properties?: any
}

// 响应式数据
const question = ref('')
const messages = ref<Message[]>([])
const loading = ref(false)
const messageListRef = ref<HTMLElement>()
const uploadedImage = ref<File | null>(null)  // 上传的图片文件
const imagePreviewUrl = ref<string>('')  // 图片预览URL
const imageInputRef = ref<HTMLInputElement>()  // 图片input引用

// 会话相关
const conversationList = ref<Conversation[]>([])
const currentConversationId = ref<number | null>(null)
const showRenameDialog = ref(false)
const renameTitle = ref('')
const renamingConversationId = ref<number | null>(null)
const sidebarCollapsed = ref(false) // 侧边栏折叠状态

// 切换侧边栏折叠状态
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

// 当前会话标题
const currentConversationTitle = computed(() => {
  if (!conversationList.value) return '教务智能问答'
  const conv = conversationList.value.find(c => c.id === currentConversationId.value)
  return conv ? conv.title : '教务智能问答'
})



// 获取实体标签类型
const getEntityTagType = (type: string) => {
  const typeMap: any = {
    'Typhoon': 'danger',
    'Location': 'warning',
    'DisasterType': 'danger',
    'Damage': 'danger',
    'PreventiveMeasure': 'success',
    'RescueAction': 'primary',
    'Organization': 'info',
    'Document': '',
    'TimePoint': 'warning'
  }
  return typeMap[type] || ''
}

// 格式化时间
const formatTime = (timeStr: string) => {
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  // 小于1分钟
  if (diff < 60000) {
    return '刚刚'
  }
  // 小于1小时
  if (diff < 3600000) {
    return `${Math.floor(diff / 60000)}分钟前`
  }
  // 小于1天
  if (diff < 86400000) {
    return `${Math.floor(diff / 3600000)}小时前`
  }
  // 大于1天
  return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
}

// 格式化消息(支持Markdown)
const formatMessage = (text: string) => {
  return marked(text, { breaks: true })
}

const formatDateTime = (value?: string) => {
  if (!value) return '未知'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}`
}

const formatAreas = (areas?: string[] | string) => {
  if (!areas) return '暂无数据'
  if (Array.isArray(areas)) {
    if (areas.length === 0) return '暂无数据'
    return areas.join('、')
  }
  return areas
}

const formatNumber = (value?: number | null, unit = '') => {
  if (value === null || value === undefined) return '暂无数据'
  return unit ? `${value}${unit}` : String(value)
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight
    }
  })
}

// 加载会话列表
const loadConversationList = async () => {
  try {
    const response = await getConversationList()
    conversationList.value = response.list

    // 如果有会话但没有选中,自动选中第一个
    if (conversationList.value.length > 0 && !currentConversationId.value) {
      await handleSwitchConversation(conversationList.value[0].id)
    }
  } catch (error: any) {
    ElMessage.error(error.message || '加载会话列表失败')
  }
}

// 创建新会话
const handleCreateConversation = async () => {
  try {
    const response = await createConversation()

    // 先设置当前会话ID和清空消息
    currentConversationId.value = response.conversation_id
    messages.value = []

    // 然后重新加载会话列表
    await loadConversationList()

    ElMessage.success('创建会话成功')
  } catch (error: any) {
    ElMessage.error(error.message || '创建会话失败')
  }
}

// 切换会话
const handleSwitchConversation = async (conversationId: number) => {
  if (currentConversationId.value === conversationId) return

  currentConversationId.value = conversationId
  messages.value = []

  try {
    const response = await getConversationMessages(conversationId)

    // 转换消息格式
      response.list.forEach((msg: ConversationMessage) => {
        messages.value.push({
          type: 'user',
          content: msg.question,
          image_url: msg.image_url  // 加载历史图片
        })

        messages.value.push({
          type: 'assistant',
          content: msg.answer,
          related_entities: msg.related_entities,
          graph_context: msg.graph_context,
          keywords: msg.keywords || []
        })
      })

    scrollToBottom()
  } catch (error: any) {
    ElMessage.error(error.message || '加载会话消息失败')
  }
}

// 删除会话
const handleDeleteConversation = async (conversationId: number) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个会话吗?删除后将无法恢复!',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    await deleteConversation(conversationId)

    // 如果删除的是当前会话,清空消息列表
    if (currentConversationId.value === conversationId) {
      currentConversationId.value = null
      messages.value = []
    }

    await loadConversationList()
    ElMessage.success('删除会话成功')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除会话失败')
    }
  }
}

// 重命名会话
const handleRenameConversation = (conv: Conversation) => {
  renamingConversationId.value = conv.id
  renameTitle.value = conv.title
  showRenameDialog.value = true
}

// 确认重命名
const confirmRename = async () => {
  if (!renameTitle.value.trim()) {
    ElMessage.warning('会话名称不能为空')
    return
  }

  if (!renamingConversationId.value) return

  try {
    await renameConversation(renamingConversationId.value, renameTitle.value)
    await loadConversationList()
    showRenameDialog.value = false
    ElMessage.success('重命名成功')
  } catch (error: any) {
    ElMessage.error(error.message || '重命名失败')
  }
}

// 清除当前会话的所有消息记录
// 生成会话标题
const handleGenerateTitle = async () => {
  if (!currentConversationId.value) return

  try {
    const loadingMsg = ElMessage({
      message: '正在生成标题...',
      type: 'info',
      duration: 0
    })

    const result = await generateConversationTitle(currentConversationId.value)

    loadingMsg.close()

    // 刷新会话列表以显示新标题
    await loadConversationList()

    ElMessage.success(`标题生成成功: ${result.title}`)
  } catch (error: any) {
    ElMessage.error(error.message || '生成标题失败')
  }
}

const handleClearMessages = async () => {
  if (!currentConversationId.value) return

  try {
    await ElMessageBox.confirm(
      '确定要清除当前会话的所有消息记录吗?清除后将无法恢复!',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    await clearConversationMessages(currentConversationId.value)

    // 清空前端显示的消息
    messages.value = []

    ElMessage.success('清除成功')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '清除失败')
    }
  }
}

// 点击示例问题
const askExample = (exampleQuestion: string) => {
  question.value = exampleQuestion
  handleAsk()
}

// 处理图片上传
const handleImageUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]

  if (!file) {
    console.log('[图片上传] 未选择文件')
    return
  }

  console.log('[图片上传] 选择了文件:', file.name, file.type, file.size)

  // 检查文件类型
  if (!file.type.startsWith('image/')) {
    ElMessage.error('请上传图片文件')
    // 重置input
    target.value = ''
    return
  }

  // 检查文件大小(限制10MB)
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过10MB')
    // 重置input
    target.value = ''
    return
  }

  // 清除之前的预览URL
  if (imagePreviewUrl.value) {
    URL.revokeObjectURL(imagePreviewUrl.value)
  }

  // 设置新的图片
  uploadedImage.value = file
  imagePreviewUrl.value = URL.createObjectURL(file)
  console.log('[图片上传] 预览URL生成:', imagePreviewUrl.value)

  // 重置input，允许重新上传同一文件
  target.value = ''
}

// 移除上传的图片
const handleRemoveImage = () => {
  console.log('[图片上传] 移除图片')
  if (imagePreviewUrl.value) {
    URL.revokeObjectURL(imagePreviewUrl.value)
  }
  uploadedImage.value = null
  imagePreviewUrl.value = ''

  // 同时清空input元素
  if (imageInputRef.value) {
    imageInputRef.value.value = ''
  }
}

// 发送问题
const handleAsk = async () => {
  const q = question.value.trim()
  if (!q || loading.value || !currentConversationId.value) return

  // 保存图片引用（发送后要清空）
  const imageToSend = uploadedImage.value
  const imagePreview = imagePreviewUrl.value

  // 添加用户消息（暂不设置图片URL，等服务器返回后再设置）
  const userMessageIndex = messages.value.length
  messages.value.push({
    type: 'user',
    content: q,
    image_url: imagePreview || undefined  // 先用blob URL临时显示
  })

  // 清空输入框、文件引用和预览（输入区域不再显示）
  question.value = ''
  uploadedImage.value = null
  imagePreviewUrl.value = ''  // 立即隐藏输入区域的预览
  // 清空input元素
  if (imageInputRef.value) {
    imageInputRef.value.value = ''
  }

  // 滚动到底部
  scrollToBottom()

  // 开始加载
  loading.value = true

  try {
    // 构建对话历史(最近3轮,即6条消息)
    const history = messages.value
      .slice(0, -1)  // 排除刚添加的用户消息
      .slice(-6)  // 取最后6条消息(3轮对话)
      .map(msg => ({
        role: (msg.type === 'user' ? 'user' : 'assistant') as 'user' | 'assistant',
        content: msg.content
      }))

    const response = await askQuestion({
      question: q,
      conversation_id: currentConversationId.value,
      top_k: 7,
      history: history
    }, imageToSend || undefined)

    // 更新用户消息的图片URL为服务器返回的URL
    if (response.image_url) {
      // 先释放旧的blob URL
      if (imagePreview) {
        URL.revokeObjectURL(imagePreview)
      }
      // 更新为服务器返回的真实URL
      messages.value[userMessageIndex].image_url = response.image_url
    }

    // 添加助手回复
    messages.value.push({
      type: 'assistant',
      content: response.answer,
      related_entities: response.related_entities || [],
      graph_context: response.graph_context,
      diseaseInfoMatches: response.disease_info_matches || [],
      diseaseCaseMatches: response.disease_case_matches || [],
      diseaseInfoContext: response.disease_info_context || '',
      diseaseCaseContext: response.disease_case_context || '',
      keywords: response.keywords || []
    })

    // 滚动到底部
    scrollToBottom()

    // 重新加载会话列表(更新时间)
    await loadConversationList()

  } catch (error: any) {
    ElMessage.error(error.message || '提问失败,请重试')
    // 移除用户消息
    messages.value.pop()
    // 清理blob URL
    if (imagePreview) {
      URL.revokeObjectURL(imagePreview)
    }
  } finally {
    loading.value = false
  }
}

// 截断文本
const truncateText = (text: string, maxLength: number) => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

// 页面加载时
onMounted(() => {
  loadConversationList()
})
</script>

<style scoped lang="scss">
.qa-chat-container {
  height: 100%;
  display: flex;
  gap: 0;

  .conversation-sidebar {
    width: 280px;
    background: #f5f7fa;
    border-right: 1px solid #e4e7ed;
    display: flex;
    flex-direction: column;
    position: relative;
    transition: width 0.3s ease;

    &.collapsed {
      width: 60px;

      .conversation-list {
        opacity: 0;
        pointer-events: none;
      }
    }

    .sidebar-header {
      padding: 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid #e4e7ed;

      .sidebar-title {
        font-size: 16px;
        font-weight: 600;
        color: #303133;
      }

      .header-actions {
        display: flex;
        gap: 8px;
        align-items: center;
      }
    }

    .conversation-list {
      flex: 1;
      overflow-y: auto;
      padding: 12px;
      transition: opacity 0.3s ease;

      .conversation-item {
        padding: 12px;
        margin-bottom: 8px;
        background: white;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s;
        display: flex;
        justify-content: space-between;
        align-items: center;

        &:hover {
          background: var(--chat-hover-bg);
          transform: translateX(4px);

          .conversation-actions {
            opacity: 1;
          }
        }

        &.active {
          background: linear-gradient(135deg, #f6ffed 0%, #d9f7be 100%);
          box-shadow: 0 2px 8px rgba(82, 196, 26, 0.1);

          .conversation-title {
            color: var(--primary-color);
            font-weight: 600;
          }

          .conversation-time {
            color: var(--primary-light);
          }

          .conversation-actions {
            opacity: 1;

            .action-icon {
              color: var(--primary-color);

              &:hover {
                color: var(--primary-light);
              }
            }
          }
        }

        .conversation-info {
          flex: 1;
          min-width: 0;

          .conversation-title {
            font-size: 14px;
            font-weight: 500;
            color: #303133;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            margin-bottom: 4px;
          }

          .conversation-time {
            font-size: 12px;
            color: #909399;
          }
        }

        .conversation-actions {
          display: flex;
          gap: 8px;
          opacity: 0;
          transition: opacity 0.3s;

          .action-icon {
            font-size: 16px;
            color: #606266;
            cursor: pointer;
            transition: color 0.3s;

            &:hover {
              color: #409eff;
            }
          }
        }
      }

      .empty-conversations {
        text-align: center;
        padding: 60px 20px;
        color: #909399;

        .el-icon {
          font-size: 48px;
          margin-bottom: 16px;
        }

        p {
          font-size: 14px;
          margin: 0;
        }
      }
    }
  }

  .chat-main {
    flex: 1;
    padding: 0 20px 20px 20px;
    overflow: hidden;

    .chat-card {
      height: calc(100vh - 120px);
      display: flex;
      flex-direction: column;

      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;

        .card-title {
          font-size: 18px;
          font-weight: 600;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .header-buttons {
          display: flex;
          gap: 8px;
          align-items: center;
        }
      }

      :deep(.el-card__body) {
        flex: 1;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        padding: 0;
      }
    }

    .chat-area {
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;

      .welcome-message {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 60px 20px;
        text-align: center;

        .welcome-icon {
          font-size: 32px;
          color: var(--primary-color);
          margin-bottom: 20px;
        }

        h3 {
          font-size: 24px;
          color: #303133;
          margin: 0 0 10px 0;
        }

        p {
          font-size: 14px;
          color: #909399;
          margin: 0 0 40px 0;
        }

        .example-questions {
          max-width: 600px;
          width: 100%;

          .example-title {
            font-size: 14px;
            color: #606266;
            margin-bottom: 16px;
            font-weight: 500;
          }

          .example-question {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 14px 20px;
            margin-bottom: 12px;
            background: #f5f7fa;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
            text-align: left;

            &:hover {
              background: #ecf5ff;
              color: #409eff;
              transform: translateY(-2px);
              box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
            }

            .el-icon {
              font-size: 18px;
            }

            span {
              font-size: 14px;
            }
          }
        }
      }

      .message-list {
        flex: 1;
        overflow-y: auto;
        padding: 20px;

        .message-item {
          display: flex;
          gap: 12px;
          margin-bottom: 24px;

          &.user {
            justify-content: flex-end;

            .message-content {
              background: var(--chat-user-bg);
              color: white;
            }
          }

          &.assistant {
            justify-content: flex-start;

            .message-content {
              background: #f5f7fa;
              color: #303133;
            }
          }

          .message-avatar {
            flex-shrink: 0;
          }

          .message-content {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 8px;
            line-height: 1.6;

            .message-image {
              margin-bottom: 12px;

              :deep(.el-image) {
                cursor: pointer;
              }
            }

            .message-text {
              :deep(p) {
                margin: 0 0 8px 0;
                &:last-child {
                  margin-bottom: 0;
                }
              }

              :deep(code) {
                background: rgba(0, 0, 0, 0.05);
                padding: 2px 6px;
                border-radius: 3px;
              }

              :deep(pre) {
                background: rgba(0, 0, 0, 0.05);
                padding: 12px;
                border-radius: 6px;
                overflow-x: auto;
              }
            }

            .keywords-section,
            .disease-info-section,
            .disease-case-section {
              margin-top: 16px;
            }

            .tag-list {
              display: flex;
              flex-wrap: wrap;
              gap: 8px;
            }

            .info-card {
              border: 1px solid #ebeef5;
              border-radius: 8px;
              padding: 12px 14px;
              background: #f9fafc;
              margin-top: 12px;

              .info-card__header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 8px;

                .info-card__title {
                  font-weight: 600;
                  color: #303133;
                }
              }

              .info-card__image {
                margin: 8px 0;

                :deep(.el-image) {
                  cursor: pointer;
                  border: 1px solid #e4e7ed;
                  transition: all 0.3s;

                  &:hover {
                    border-color: var(--primary-color);
                    transform: scale(1.02);
                  }
                }
              }

              .info-card__images {
                margin: 8px 0;
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                align-content: flex-start;
                max-height: 280px;
                overflow-y: auto;

                :deep(.el-image) {
                  cursor: pointer;
                  border: 1px solid #e4e7ed;
                  transition: all 0.3s;

                  &:hover {
                    border-color: var(--primary-color);
                    transform: scale(1.05);
                  }
                }
              }

              .info-card__meta {
                display: flex;
                flex-wrap: wrap;
                gap: 12px;
                font-size: 13px;
                color: #606266;
                margin-bottom: 6px;

                strong {
                  color: #303133;
                }
              }

              .info-card__desc {
                font-size: 13px;
                color: #4a4a4a;
                line-height: 1.6;
                margin-bottom: 6px;
              }
            }

            .related-entities {
              margin-top: 16px;

              .entity-tags {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin-top: 8px;

                .entity-tag {
                  cursor: default;
                  font-size: 13px;
                  max-width: 280px;
                  display: inline-flex;
                  align-items: center;

                  :deep(.el-tag__content) {
                    max-width: 100%;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                    display: flex;
                    align-items: center;
                  }
                }
              }
            }

            .graph-context {
              margin-top: 16px;

              .context-content {
                background: rgba(0, 0, 0, 0.02);
                border: 1px solid #e4e7ed;
                border-radius: 6px;
                padding: 12px;
                margin-top: 8px;
                max-height: 300px;
                overflow-y: auto;

                pre {
                  margin: 0;
                  font-size: 13px;
                  line-height: 1.8;
                  color: #606266;
                  font-family: 'Courier New', Courier, monospace;
                  white-space: pre-wrap;
                  word-wrap: break-word;
                }
              }
            }
          }

          &.loading {
            .message-content {
              padding: 20px;

              .typing-indicator {
                display: flex;
                gap: 6px;

                span {
                  width: 8px;
                  height: 8px;
                  border-radius: 50%;
                  background: var(--primary-color);
                  animation: typing 1.4s infinite;

                  &:nth-child(2) {
                    animation-delay: 0.2s;
                  }

                  &:nth-child(3) {
                    animation-delay: 0.4s;
                  }
                }
              }
            }
          }
        }
      }
    }

    .input-area {
      border-top: 1px solid #ebeef5;
      padding: 20px;

      .image-preview-container {
        margin-bottom: 12px;

        .image-preview {
          position: relative;
          display: inline-block;
          border: 1px solid #dcdfe6;
          border-radius: 8px;
          overflow: hidden;

          img {
            display: block;
            max-width: 200px;
            max-height: 200px;
            object-fit: contain;
          }

          .remove-image {
            position: absolute;
            top: 8px;
            right: 8px;
            width: 24px;
            height: 24px;
            background: rgba(0, 0, 0, 0.6);
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s;

            &:hover {
              background: rgba(0, 0, 0, 0.8);
            }
          }
        }
      }

      .input-actions {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 12px;

        .left-actions {
          display: flex;
          gap: 8px;
        }

        .right-actions {
          display: flex;
          gap: 12px;
          align-items: center;
        }

        .input-tip {
          font-size: 12px;
          color: #909399;
        }
      }
    }
  }
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-10px);
  }
}
</style>
