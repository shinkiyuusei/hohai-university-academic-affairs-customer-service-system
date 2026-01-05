

<template>
  <div class="knowledge-graph-management">
    <div class="page-header">
      <h1 class="page-title">
        <el-icon class="title-icon"><Connection /></el-icon>
        知识图谱管理
      </h1>
      <p class="page-subtitle">
        管理植物病害知识图谱，同步文档数据到Neo4j图数据库
      </p>
    </div>

    <!-- 统计信息 -->
    <div class="statistics-cards">
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon node-icon">
            <el-icon><Operation /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">节点数量</div>
            <div class="stat-value">{{ statistics.nodeCount || 0 }}</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon relation-icon">
            <el-icon><Connection /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">关系数量</div>
            <div class="stat-value">{{ statistics.relationshipCount || 0 }}</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon type-icon">
            <el-icon><Collection /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">节点类型</div>
            <div class="stat-value">{{ statistics.nodeTypes?.length || 0 }}</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon entity-icon">
            <el-icon><DataLine /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">关系类型</div>
            <div class="stat-value">{{ statistics.relationshipTypes?.length || 0 }}</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <div class="left-actions">
        <el-button
          type="success"
          @click="handleIncrementalBuild"
          :loading="syncing"
          :disabled="isBuilding"
        >
          <el-icon><Refresh /></el-icon>
          增量构建图谱
        </el-button>
        <el-button
          type="primary"
          @click="handleFullRebuild"
          :loading="syncing"
          :disabled="isBuilding"
        >
          <el-icon><Refresh /></el-icon>
          全量重建图谱
        </el-button>
        <el-button
          type="danger"
          @click="handleClearGraph"
          :loading="syncing"
          :disabled="isBuilding"
        >
          <el-icon><Delete /></el-icon>
          清空图谱
        </el-button>
        <el-button @click="loadStatistics" :disabled="isBuilding">
          <el-icon><RefreshRight /></el-icon>
          刷新统计
        </el-button>
      </div>
      <div class="right-actions">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索图谱实体"
          style="width: 300px"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #append>
            <el-button @click="handleSearch">
              <el-icon><Search /></el-icon>
            </el-button>
          </template>
        </el-input>
      </div>
    </div>

    <!-- 构建进度持久化显示 -->
    <el-card v-if="isBuilding" class="progress-card">
      <div class="progress-header">
        <div class="progress-title">
          <el-icon class="rotating-icon"><Loading /></el-icon>
          <span>{{ buildStatus === 'running' ? '正在构建知识图谱' : '构建任务进行中' }}</span>
        </div>
        <el-button
          size="small"
          text
          @click="showProgressDialog = true"
        >
          查看详情
        </el-button>
      </div>

      <el-progress
        :percentage="buildProgress"
        :status="buildStatus === 'failed' ? 'exception' : undefined"
        :stroke-width="12"
      >
        <template #default="{ percentage }">
          <span class="progress-text">{{ percentage }}%</span>
        </template>
      </el-progress>

      <div class="progress-info">
        <span class="info-text">{{ buildStep }}</span>
        <span v-if="totalDocuments > 0" class="info-detail">
          {{ processedDocuments }} / {{ totalDocuments }} 个文档
        </span>
      </div>
    </el-card>

    <!-- 搜索结果 -->
    <el-card v-if="searchResults.length > 0" class="search-results">
      <template #header>
        <div class="card-header">
          <span>搜索结果（共 {{ searchResults.length }} 个实体）</span>
          <el-button text @click="handleClearSearch">清空并恢复完整视图</el-button>
        </div>
      </template>
      <div class="entity-list">
        <div
          v-for="entity in searchResults"
          :key="entity.id"
          class="entity-item"
          @click="viewEntityDetail(entity)"
        >
          <div class="entity-header">
            <el-tag :type="getEntityTypeColor(entity.type)">{{ entity.type }}</el-tag>
            <span class="entity-name">{{ entity.name }}</span>
          </div>
          <div v-if="entity.properties" class="entity-props">
            <span v-for="(value, key) in entity.properties" :key="key" class="prop-item">
              <strong>{{ key }}:</strong> {{ value }}
            </span>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 节点类型说明 -->
    <el-card class="info-card">
      <template #header>
        <div class="card-header">
          <el-icon><InfoFilled /></el-icon>
          <span>知识图谱结构说明</span>
        </div>
      </template>
      <div class="node-types">
        <h4>节点类型</h4>
        <el-tag
          v-for="type in nodeTypes"
          :key="type"
          class="type-tag"
          :type="getNodeCount(type) > 0 ? 'primary' : 'info'"
        >
          {{ getNodeTypeName(type) }} ({{ getNodeCount(type) }})
        </el-tag>

        <h4 style="margin-top: 20px">关系类型</h4>
        <el-tag
          v-for="type in relationshipTypes"
          :key="type"
          class="type-tag"
          :type="getRelationCount(type) > 0 ? 'success' : 'info'"
        >
          {{ getRelationTypeName(type) }} ({{ getRelationCount(type) }})
        </el-tag>
      </div>
    </el-card>

    <!-- 构建进度对话框 -->
    <el-dialog
      v-model="showProgressDialog"
      title="知识图谱构建进度"
      width="600px"
      :close-on-click-modal="false"
      :show-close="false"
    >
      <div class="progress-content">
        <!-- 进度条 -->
        <el-progress
          :percentage="buildProgress"
          :status="buildStatus === 'failed' ? 'exception' : undefined"
          :stroke-width="20"
        />

        <!-- 当前步骤 -->
        <div class="progress-step">
          <el-icon class="step-icon"><Loading /></el-icon>
          <span>{{ buildStep }}</span>
        </div>

        <!-- 文档处理进度 -->
        <div v-if="totalDocuments > 0" class="progress-details">
          <div class="detail-item">
            <span class="label">总文档数：</span>
            <span class="value">{{ totalDocuments }}</span>
          </div>
          <div class="detail-item">
            <span class="label">已处理：</span>
            <span class="value">{{ processedDocuments }}</span>
          </div>
          <div v-if="currentDocument" class="detail-item">
            <span class="label">当前文档：</span>
            <span class="value">{{ currentDocument }}</span>
          </div>
        </div>

        <!-- 提示信息 -->
        <el-alert
          title="提示"
          type="info"
          :closable="false"
          show-icon
        >
          构建过程可能需要较长时间，请耐心等待。您可以关闭此对话框，任务将继续在后台执行。
        </el-alert>
      </div>

      <template #footer>
        <el-button @click="handleCloseProgressDialog">后台运行</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Connection, Operation, Collection, DataLine,
  Refresh, Delete, RefreshRight, Search, InfoFilled, Loading
} from '@element-plus/icons-vue'
import {
  getGraphStatistics,
  buildGraphIncremental,
  rebuildGraphFull,
  getBuildStatus,
  searchGraphEntities,
  getEntityDetail,
  clearGraph
} from '@/api/knowledge_graph'

// 统计信息
const statistics = ref<any>({})
const syncing = ref(false)

// 构建进度相关
const isBuilding = ref(false)  // 是否正在构建（用于禁用按钮和显示持久化进度）
const showProgressDialog = ref(false)
const currentTaskId = ref('')
const buildProgress = ref(0)
const buildStatus = ref('')
const buildStep = ref('')
const totalDocuments = ref(0)
const processedDocuments = ref(0)
const currentDocument = ref('')
let progressTimer: any = null

// localStorage 键名
const TASK_STORAGE_KEY = 'kg_build_task'
const searchKeyword = ref('')
const searchResults = ref<any[]>([])

// 节点类型和关系类型（从后端配置获取）
const nodeTypes = ref([
  'AcademicPolicy', 'Course', 'Student', 'Teacher',
  'Major', 'Schedule', 'Requirement', 'Procedure',
  'Document', 'TimePoint'
])

const relationshipTypes = ref([
    'APPLIES_TO', 'REQUIRES', 'BELONGS_TO', 'TAUGHT_BY',
    'FOLLOWS', 'MEETS_REQUIREMENT', 'SCHEDULED_AT', 'RELATED_TO',
    'DOCUMENTED_IN', 'PREREQUISITE_OF', 'EQUIVALENT_TO'
  ])

// 保存任务到 localStorage
const saveTaskToStorage = (taskId: string, taskType: string) => {
  const taskInfo = {
    task_id: taskId,
    task_type: taskType,
    start_time: Date.now()
  }
  localStorage.setItem(TASK_STORAGE_KEY, JSON.stringify(taskInfo))
}

// 从 localStorage 获取任务
const getTaskFromStorage = () => {
  const taskStr = localStorage.getItem(TASK_STORAGE_KEY)
  if (!taskStr) return null
  try {
    return JSON.parse(taskStr)
  } catch {
    return null
  }
}

// 清除 localStorage 中的任务
const clearTaskFromStorage = () => {
  localStorage.removeItem(TASK_STORAGE_KEY)
}

// 加载统计信息
const loadStatistics = async () => {
  try {
    const data = await getGraphStatistics()
    statistics.value = data
  } catch (error: any) {
    ElMessage.error(error.message || '获取统计信息失败')
  }
}

// 查询任务进度
const checkProgress = async () => {
  if (!currentTaskId.value) return

  try {
    const taskInfo = await getBuildStatus(currentTaskId.value)

    buildProgress.value = taskInfo.progress || 0
    buildStatus.value = taskInfo.status
    buildStep.value = taskInfo.current_step || ''
    totalDocuments.value = taskInfo.total_documents || 0
    processedDocuments.value = taskInfo.processed_documents || 0
    currentDocument.value = taskInfo.current_document || ''

    // 如果任务完成或失败，停止轮询
    if (taskInfo.status === 'completed') {
      stopProgressPolling()
      clearTaskFromStorage()  // 清除持久化的任务信息
      showProgressDialog.value = false
      syncing.value = false
      isBuilding.value = false  // 恢复按钮可用

      const result = taskInfo.result
      if (result) {
        ElMessage.success({
          message: `构建完成！处理 ${result.documents_processed} 个文档，提取 ${result.triplets_extracted} 个三元组，创建 ${result.nodes_created} 个节点，${result.relationships_created} 个关系`,
          duration: 5000
        })
      } else {
        ElMessage.success('构建完成！')
      }

      // 刷新统计信息
      await loadStatistics()
    } else if (taskInfo.status === 'failed') {
      stopProgressPolling()
      clearTaskFromStorage()  // 清除持久化的任务信息
      showProgressDialog.value = false
      syncing.value = false
      isBuilding.value = false  // 恢复按钮可用
      ElMessage.error(taskInfo.error || '构建失败')
    }
  } catch (error: any) {
    console.error('查询进度失败:', error)
  }
}

// 开始轮询进度
const startProgressPolling = () => {
  // 立即查询一次
  checkProgress()
  // 每秒查询一次
  progressTimer = setInterval(checkProgress, 1000)
}

// 停止轮询进度
const stopProgressPolling = () => {
  if (progressTimer) {
    clearInterval(progressTimer)
    progressTimer = null
  }
}

// 增量构建图谱
const handleIncrementalBuild = () => {
  ElMessageBox.confirm(
    '此操作将构建所有未构建图谱的文档，不会清空现有图谱数据，是否继续？',
    '增量构建知识图谱',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info',
    }
  ).then(async () => {
    syncing.value = true
    isBuilding.value = true  // 设置构建状态，禁用按钮并显示持久化进度
    try {
      const result = await buildGraphIncremental()
      currentTaskId.value = result.task_id

      // 保存任务到 localStorage
      saveTaskToStorage(result.task_id, 'incremental')

      // 初始化进度信息
      buildProgress.value = 0
      buildStatus.value = 'running'
      buildStep.value = '任务已启动...'
      totalDocuments.value = 0
      processedDocuments.value = 0
      currentDocument.value = ''

      // 显示进度对话框
      showProgressDialog.value = true

      // 开始轮询进度
      startProgressPolling()

      ElMessage.info('任务已启动，正在后台执行')
    } catch (error: any) {
      syncing.value = false
      isBuilding.value = false
      ElMessage.error(error.message || '启动增量构建失败')
    }
  }).catch(() => {
    // 取消操作
  })
}

// 全量重建图谱
const handleFullRebuild = () => {
  ElMessageBox.confirm(
    '此操作将清空现有图谱数据并重新构建所有文档的知识图谱，是否继续？',
    '全量重建知识图谱',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    syncing.value = true
    isBuilding.value = true  // 设置构建状态，禁用按钮并显示持久化进度
    try {
      const result = await rebuildGraphFull()
      currentTaskId.value = result.task_id

      // 保存任务到 localStorage
      saveTaskToStorage(result.task_id, 'full')

      // 初始化进度信息
      buildProgress.value = 0
      buildStatus.value = 'running'
      buildStep.value = '任务已启动...'
      totalDocuments.value = 0
      processedDocuments.value = 0
      currentDocument.value = ''

      // 显示进度对话框
      showProgressDialog.value = true

      // 开始轮询进度
      startProgressPolling()

      ElMessage.info('任务已启动，正在后台执行')
    } catch (error: any) {
      syncing.value = false
      isBuilding.value = false
      ElMessage.error(error.message || '启动全量重建失败')
    }
  }).catch(() => {
    // 取消操作
  })
}

// 关闭进度对话框时停止轮询
const handleCloseProgressDialog = () => {
  showProgressDialog.value = false
}

// 清空图谱
const handleClearGraph = () => {
  ElMessageBox.confirm(
    '此操作将清空所有图谱数据，并重置所有文档的构建标志。清空后，增量构建将重新处理所有文档。是否继续？',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    syncing.value = true
    try {
      // 调用清空图谱接口
      await clearGraph()
      ElMessage.success('图谱已清空，所有文档标志已重置')
      // 刷新统计信息
      await loadStatistics()
    } catch (error: any) {
      ElMessage.error(error.message || '清空图谱失败')
    } finally {
      syncing.value = false
    }
  }).catch(() => {
    // 取消操作
  })
}

// 搜索实体
const handleSearch = async () => {
  if (!searchKeyword.value.trim()) {
    ElMessage.warning('请输入搜索关键词')
    return
  }

  try {
    syncing.value = true

    // 搜索实体
    const data = await searchGraphEntities({
      keywords: [searchKeyword.value.trim()],
      limit: 20
    })

    searchResults.value = data || []

    if (searchResults.value.length === 0) {
      ElMessage.info('未找到相关实体')
    } else {
      ElMessage.success(`找到 ${searchResults.value.length} 个相关实体`)
    }
  } catch (error: any) {
    ElMessage.error(error.message || '搜索失败')
  } finally {
    syncing.value = false
  }
}

// 清空搜索结果
const handleClearSearch = () => {
  searchResults.value = []
  searchKeyword.value = ''
  ElMessage.info('已清空搜索结果')
}

// 查看实体详情
const viewEntityDetail = async (entity: any) => {
  try {
    const data = await getEntityDetail(entity.name, {
      entity_type: entity.type,
      depth: 1
    })

    // 构建属性信息
    let propsHtml = ''
    if (entity.properties && Object.keys(entity.properties).length > 0) {
      propsHtml = '<h4>属性信息：</h4><ul>'
      for (const [key, value] of Object.entries(entity.properties)) {
        propsHtml += `<li><strong>${key}:</strong> ${value}</li>`
      }
      propsHtml += '</ul>'
    }

    // 显示基本信息
    ElMessageBox.alert(
      `<div style="max-height: 500px; overflow-y: auto;">
        <h3>${entity.name}</h3>
        <p><strong>类型:</strong> ${getNodeTypeName(entity.type)} (${entity.type})</p>
        <p><strong>邻居节点数量:</strong> ${data.nodes?.length || 0}</p>
        <p><strong>关系数量:</strong> ${data.relationships?.length || 0}</p>
        ${propsHtml}
        <div style="margin-top: 20px; padding: 12px; background: #f0f9ff; border-left: 4px solid #3b82f6; border-radius: 4px;">
          <p style="margin: 0; color: #1e40af;">
            <strong>💡 提示：</strong>如需查看图形化的节点关系，请前往"知识图谱可视化"页面，在搜索框中输入"${entity.name}"进行搜索。
          </p>
        </div>
      </div>`,
      '实体详情',
      {
        dangerouslyUseHTMLString: true,
        confirmButtonText: '关闭'
      }
    )
  } catch (error: any) {
    ElMessage.error(error.message || '获取实体详情失败')
  }
}

// 获取实体类型颜色
const getEntityTypeColor = (type: string) => {
  const colorMap: any = {
    'PlantDisease': 'danger',
    'Plant': 'success',
    'Pathogen': 'warning',
    'Symptom': 'warning',
    'Prevention': 'primary',
    'Location': 'info',
    'Season': 'danger',
    'Environment': 'success',
    'Document': 'info',
    'TimePoint': 'warning'
  }
  return colorMap[type] || 'info'
}

// 获取节点类型的数量
const getNodeCount = (type: string) => {
  const key = `${type.toLowerCase()}_count`
  return statistics.value[key] || 0
}

// 获取关系类型的数量
const getRelationCount = (type: string) => {
  const key = `${type.toLowerCase()}_count`
  return statistics.value[key] || 0
}

// 节点类型中文名称映射
const nodeTypeNameMap: Record<string, string> = {
  'PlantDisease': '植物病害',
  'Plant': '植物',
  'Pathogen': '病原体',
  'Symptom': '症状',
  'Prevention': '防治措施',
  'Location': '地点',
  'Season': '季节',
  'Environment': '环境因素',
  'Document': '文档',
  'TimePoint': '时间点',
  'AcademicPolicy': '教务政策',
  'Course': '课程',
  'Student': '学生',
  'Teacher': '教师',
  'Major': '专业',
  'Schedule': '课表',
  'Requirement': '要求规定',
  'Procedure': '流程'
}

// 关系类型中文名称映射
const relationTypeNameMap: Record<string, string> = {
  'AFFECTS': '影响',
  'CAUSED_BY': '由...引起',
  'SHOWS_SYMPTOM': '表现症状',
  'OCCURS_IN': '发生于',
  'PREVENTED_BY': '被预防',
  'TREATED_BY': '被治疗',
  'OCCURS_AT': '发生时间',
  'FAVORED_BY': '受...促进',
  'DOCUMENTED_IN': '记录于',
  'LOCATED_IN': '位于',
  'RELATED_TO': '相关',
  'APPLIES_TO': '适用于',
  'REQUIRES': '要求',
  'BELONGS_TO': '属于',
  'TAUGHT_BY': '由...教授',
  'FOLLOWS': '遵循',
  'MEETS_REQUIREMENT': '满足要求',
  'SCHEDULED_AT': '安排在',
  'PREREQUISITE_OF': '先修课程',
  'EQUIVALENT_TO': '等价于'
}

// 获取节点类型中文名称
const getNodeTypeName = (type: string) => {
  return nodeTypeNameMap[type] || type
}

// 获取关系类型中文名称
const getRelationTypeName = (type: string) => {
  return relationTypeNameMap[type] || type
}

// 恢复正在进行的任务
const restoreOngoingTask = async () => {
  const savedTask = getTaskFromStorage()
  if (!savedTask) return

  try {
    // 查询任务状态
    const taskInfo = await getBuildStatus(savedTask.task_id)

    // 如果任务还在运行，恢复状态
    if (taskInfo.status === 'running' || taskInfo.status === 'pending') {
      currentTaskId.value = savedTask.task_id
      isBuilding.value = true
      buildProgress.value = taskInfo.progress || 0
      buildStatus.value = taskInfo.status
      buildStep.value = taskInfo.current_step || '正在恢复任务状态...'
      totalDocuments.value = taskInfo.total_documents || 0
      processedDocuments.value = taskInfo.processed_documents || 0
      currentDocument.value = taskInfo.current_document || ''

      // 开始轮询进度
      startProgressPolling()

      ElMessage.info({
        message: `检测到正在进行的${savedTask.task_type === 'incremental' ? '增量构建' : '全量重建'}任务，已自动恢复进度显示`,
        duration: 3000
      })
    } else {
      // 任务已完成或失败，清除存储
      clearTaskFromStorage()
    }
  } catch (error: any) {
    console.error('恢复任务失败:', error)
    // 如果查询失败，清除存储
    clearTaskFromStorage()
  }
}

onMounted(() => {
  loadStatistics()
  // 尝试恢复正在进行的任务
  restoreOngoingTask()
})
</script>

<style scoped>
.knowledge-graph-management {
  padding: 0;
}

.page-header {
  margin-bottom: 24px;
  padding: 24px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-icon {
  font-size: 28px;
  color: #3b82f6;
}

.page-subtitle {
  color: #64748b;
  margin: 0;
  font-size: 14px;
}

/* 统计卡片 */
.statistics-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 12px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.node-icon {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
}

.relation-icon {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.type-icon {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.entity-icon {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

/* 操作栏 */
.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.left-actions,
.right-actions {
  display: flex;
  gap: 12px;
}

/* 搜索结果 */
.search-results {
  margin-bottom: 24px;
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.entity-list {
  display: grid;
  gap: 12px;
}

.entity-item {
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.entity-item:hover {
  background: #f1f5f9;
  transform: translateX(4px);
}

.entity-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.entity-name {
  font-weight: 600;
  color: #1e293b;
}

.entity-props {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  font-size: 13px;
  color: #64748b;
}

.prop-item {
  background: white;
  padding: 4px 8px;
  border-radius: 4px;
}

/* 信息卡片 */
.info-card {
  border-radius: 12px;
}

.node-types h4 {
  color: #1e293b;
  margin: 0 0 12px 0;
  font-size: 16px;
}

.type-tag {
  margin-right: 8px;
  margin-bottom: 8px;
}

/* 构建进度对话框样式 */
.progress-content {
  padding: 20px 0;
}

.progress-step {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 20px 0;
  font-size: 16px;
  color: #409eff;
  font-weight: 500;
}

.step-icon {
  margin-right: 8px;
  animation: rotate 2s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.progress-details {
  margin: 20px 0;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  margin: 8px 0;
  font-size: 14px;
}

.detail-item .label {
  color: #606266;
  font-weight: 500;
}

.detail-item .value {
  color: #303133;
  font-weight: 600;
}

/* 持久化进度卡片样式 */
.progress-card {
  margin-bottom: 24px;
  border-radius: 12px;
  border-left: 4px solid #409eff;
  background: linear-gradient(135deg, #f0f9ff 0%, #ffffff 100%);
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.1);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.progress-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.rotating-icon {
  font-size: 20px;
  color: #409eff;
  animation: rotate 2s linear infinite;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  font-size: 14px;
  color: #64748b;
}

.info-text {
  font-weight: 500;
  color: #475569;
}

.info-detail {
  font-weight: 600;
  color: #409eff;
}

.progress-text {
  font-size: 14px;
  font-weight: 600;
  color: #409eff;
}
</style>
