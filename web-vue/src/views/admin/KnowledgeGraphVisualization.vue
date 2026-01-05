<!--
【版权提示】2025 © 羊羊小栈(GJQ)
识别码＝KGZ-77FB07 · Author: Y·羊小栈 · 发布：18:00:00 / 2025.10.13
原创作品—禁止二销；配套视频、文档亦禁止转载。
违者请立即停止，并依《羊羊小栈系统版权声明及保护条款》承担法律责任。
-->

<template>
  <div class="kg-visualization" ref="visualizationContainer">
    <el-card class="control-card">
      <template #header>
        <div class="card-header">
          <span>植物病害知识图谱可视化</span>
          <div class="header-controls">
            <el-button type="primary" @click="loadGraphData" :loading="loading">
              <el-icon><Refresh /></el-icon>
              刷新图谱
            </el-button>
            <el-button type="info" @click="resetLayout">
              <el-icon><Refresh /></el-icon>
              重置布局
            </el-button>
            <el-button type="warning" @click="openNeo4jBrowser" v-if="neo4jBrowserUrl">
              <el-icon><Link /></el-icon>
              Neo4j Browser
            </el-button>
            <el-button type="success" @click="toggleFullscreen">
              <el-icon><FullScreen v-if="!isFullscreen" /><Close v-else /></el-icon>
              {{ isFullscreen ? '退出全屏' : '全屏' }}
            </el-button>
          </div>
        </div>
      </template>

      <!-- 控制面板 -->
      <div class="control-panel">
        <!-- 搜索框 -->
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="搜索节点:">
              <el-input
                v-model="searchKeyword"
                placeholder="输入节点名称搜索，将展示该节点及其周围1层的关系"
                clearable
                @keyup.enter="handleSearchNodes"
                style="width: 100%"
              >
                <template #append>
                  <el-button @click="handleSearchNodes" :loading="searching">
                    <el-icon><Search /></el-icon>
                    搜索
                  </el-button>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 搜索结果提示 -->
        <el-alert
          v-if="searchMode"
          title="当前为搜索模式"
          type="info"
          :closable="false"
          show-icon
          style="margin-bottom: 15px"
        >
          <template #default>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>正在展示关键词"{{ searchKeyword }}"的搜索结果及其邻居节点</span>
              <el-button size="small" @click="clearSearch">清除搜索，恢复完整图谱</el-button>
            </div>
          </template>
        </el-alert>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="节点类型过滤:">
              <el-checkbox-group v-model="selectedNodeTypes" @change="filterNodes">
                <el-checkbox label="AcademicPolicy">教务政策</el-checkbox>
                <el-checkbox label="Course">课程</el-checkbox>
                <el-checkbox label="Student">学生</el-checkbox>
                <el-checkbox label="Teacher">教师</el-checkbox>
                <el-checkbox label="Major">专业</el-checkbox>
                <el-checkbox label="Schedule">课表</el-checkbox>
                <el-checkbox label="Requirement">要求规定</el-checkbox>
                <el-checkbox label="Procedure">流程</el-checkbox>
                <el-checkbox label="Document">文档</el-checkbox>
                <el-checkbox label="TimePoint">时间点</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="关系类型过滤:">
              <el-checkbox-group v-model="selectedRelationTypes" @change="filterRelations">
                <el-checkbox label="APPLIES_TO">适用于</el-checkbox>
                <el-checkbox label="REQUIRES">要求</el-checkbox>
                <el-checkbox label="BELONGS_TO">属于专业</el-checkbox>
                <el-checkbox label="TAUGHT_BY">由教师教授</el-checkbox>
                <el-checkbox label="FOLLOWS">遵循流程</el-checkbox>
                <el-checkbox label="MEETS_REQUIREMENT">满足要求</el-checkbox>
                <el-checkbox label="SCHEDULED_AT">安排在时间</el-checkbox>
                <el-checkbox label="RELATED_TO">相关于</el-checkbox>
                <el-checkbox label="DOCUMENTED_IN">记录于文档</el-checkbox>
                <el-checkbox label="PREREQUISITE_OF">是...的先修课</el-checkbox>
                <el-checkbox label="EQUIVALENT_TO">等价于</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="布局设置:">
              <el-select v-model="layoutType" @change="updateLayout" style="width: 100%">
                <el-option label="力导向布局" value="force" />
                <el-option label="环形布局" value="circular" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="显示数量限制:">
              <el-input-number
                v-model="nodeLimit"
                :min="10"
                :max="500"
                @change="handleNodeLimitChange"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <!-- 图谱可视化区域 -->
    <el-card class="chart-card">
      <div
        ref="chartContainer"
        class="chart-container"
        v-loading="loading"
        element-loading-text="加载图谱数据中..."
      ></div>
    </el-card>

    <!-- 节点详情面板 -->
    <el-drawer
      v-model="detailDrawerVisible"
      title="节点详情"
      direction="rtl"
      size="400px"
    >
      <div v-if="selectedNodeDetail" class="node-detail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="节点类型">
            <el-tag :type="getNodeTypeColor(selectedNodeDetail.originalCategory)">
              {{ getNodeTypeName(selectedNodeDetail.originalCategory) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="节点名称">
            {{ selectedNodeDetail.name }}
          </el-descriptions-item>
          <el-descriptions-item label="节点ID">
            {{ selectedNodeDetail.id }}
          </el-descriptions-item>
          <el-descriptions-item label="连接数">
            {{ selectedNodeDetail.value || 0 }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 节点属性 -->
        <div class="node-properties" v-if="selectedNodeDetail.properties && Object.keys(selectedNodeDetail.properties).length > 0">
          <h4>节点属性</h4>
          <el-table :data="Object.entries(selectedNodeDetail.properties)" size="small" border>
            <el-table-column prop="0" label="属性名" width="120" />
            <el-table-column prop="1" label="属性值" />
          </el-table>
        </div>

        <!-- 相关连接 -->
        <div class="node-connections" v-if="selectedNodeDetail.connections && selectedNodeDetail.connections.length > 0">
          <h4>相关连接</h4>
          <el-tag
            v-for="conn in selectedNodeDetail.connections.slice(0, 10)"
            :key="conn"
            style="margin: 2px"
            size="small"
          >
            {{ conn }}
          </el-tag>
          <span v-if="selectedNodeDetail.connections.length > 10">
            等{{ selectedNodeDetail.connections.length - 10 }}个连接...
          </span>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, FullScreen, Close, Link, Search } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { getGraphVisualizationData, getGraphConfig, searchGraphEntities, getEntityDetail } from '@/api/knowledge_graph'

// 图表实例
const chartContainer = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null

// 容器引用
const visualizationContainer = ref<HTMLElement>()

// 全屏状态
const isFullscreen = ref(false)

// Neo4j Browser URL
const neo4jBrowserUrl = ref<string>('')

// 数据状态
const loading = ref(false)
const graphData = ref<any>({ nodes: [], links: [] })
const originalGraphData = ref<any>({ nodes: [], links: [] })
const fullGraphData = ref<any>({ nodes: [], links: [] }) // 保存完整的原始数据，不被搜索修改

// 搜索状态
const searchKeyword = ref('')
const searching = ref(false)
const searchMode = ref(false)

const resetSearchState = () => {
  searchKeyword.value = ''
  searchMode.value = false
}

// 控制状态
const selectedNodeTypes = ref([
  'AcademicPolicy', 'Course', 'Student', 'Teacher',
  'Major', 'Schedule', 'Requirement', 'Procedure',
  'Document', 'TimePoint'
])
// 作者標識：羊.羊.小.棧（Y.Y.）
const selectedRelationTypes = ref([
  'APPLIES_TO', 'REQUIRES', 'BELONGS_TO', 'TAUGHT_BY',
  'FOLLOWS', 'MEETS_REQUIREMENT', 'SCHEDULED_AT', 'RELATED_TO',
  'DOCUMENTED_IN', 'PREREQUISITE_OF', 'EQUIVALENT_TO'
])
const layoutType = ref('force')
const nodeLimit = ref(100)

// 详情面板
const detailDrawerVisible = ref(false)
const selectedNodeDetail = ref<any>(null)

// 从后端获取的配置
const nodeTypeNames = ref<Record<string, string>>({})
const relationshipTypeNames = ref<Record<string, string>>({})
const nodeColors = ref<Record<string, string>>({})

// 默认节点颜色配置（备用）
const defaultNodeColors: Record<string, string> = {
  PlantDisease: '#ee6666',
  Plant: '#91cc75',
  Pathogen: '#fc8452',
  Symptom: '#fac858',
  Prevention: '#5470c6',
  Location: '#73c0de',
  Season: '#ea7ccc',
  Environment: '#3ba272',
  AcademicPolicy: '#ee6666',
  Course: '#91cc75',
  Student: '#fc8452',
  Teacher: '#fac858',
  Major: '#5470c6',
  Schedule: '#73c0de',
  Requirement: '#ea7ccc',
  Procedure: '#3ba272',
  Document: '#9a60b4',
  TimePoint: '#ca8622'
}

// 默认节点类型名称映射（备用）
const defaultNodeTypeNames: Record<string, string> = {
  PlantDisease: '植物病害',
  Plant: '植物',
  Pathogen: '病原体',
  Symptom: '症状',
  Prevention: '防治措施',
  Location: '地点',
  Season: '季节',
  Environment: '环境因素',
  Document: '文档',
  TimePoint: '时间点',
  AcademicPolicy: '教务政策',
  Course: '课程',
  Student: '学生',
  Teacher: '教师',
  Major: '专业',
  Schedule: '课表',
  Requirement: '要求规定',
  Procedure: '流程'
}

// 默认关系类型名称映射（备用）
const defaultRelationshipTypeNames: Record<string, string> = {
  APPLIES_TO: '适用于',
  REQUIRES: '要求',
  BELONGS_TO: '属于专业',
  TAUGHT_BY: '由教师教授',
  FOLLOWS: '遵循流程',
  MEETS_REQUIREMENT: '满足要求',
  SCHEDULED_AT: '安排在时间',
  RELATED_TO: '相关于',
  DOCUMENTED_IN: '记录于文档',
  PREREQUISITE_OF: '是...的先修课',
  EQUIVALENT_TO: '等价于'
}

// 获取节点类型颜色
const getNodeTypeColor = (category: string): string => {
  const colorMap: Record<string, string> = {
    PlantDisease: 'danger',
    Plant: 'success',
    Pathogen: 'warning',
    Symptom: 'warning',
    Prevention: 'primary',
    Location: 'info',
    Season: 'danger',
    Environment: 'success',
    Document: 'info',
    TimePoint: 'warning',
    AcademicPolicy: 'danger',
    Course: 'success',
    Student: 'warning',
    Teacher: 'warning',
    Major: 'primary',
    Schedule: 'info',
    Requirement: 'danger',
    Procedure: 'success'
  }
  return colorMap[category] || 'info'
}

// 获取节点类型名称
const getNodeTypeName = (category: string): string => {
  return nodeTypeNames.value[category] || defaultNodeTypeNames[category] || category
}

// 获取关系类型中文名称
const getRelationTypeName = (relationType: string): string => {
  return relationshipTypeNames.value[relationType] || defaultRelationshipTypeNames[relationType] || relationType
}

// 获取节点颜色
const getNodeColor = (nodeType: string): string => {
  return nodeColors.value[nodeType] || defaultNodeColors[nodeType] || '#5470c6'
}

// 加载图谱配置
const loadGraphConfig = async () => {
  try {
    const config = await getGraphConfig()
    nodeTypeNames.value = config.nodeNames || {}
    relationshipTypeNames.value = config.relationshipNames || {}
    nodeColors.value = config.nodeColors || {}
    neo4jBrowserUrl.value = config.neo4jBrowserUrl || ''
  } catch (error: any) {
    console.error('获取图谱配置失败:', error)
    // 使用默认配置
    nodeTypeNames.value = defaultNodeTypeNames
    relationshipTypeNames.value = defaultRelationshipTypeNames
    nodeColors.value = defaultNodeColors
  }
}

// 打开 Neo4j Browser
const openNeo4jBrowser = () => {
  if (neo4jBrowserUrl.value) {
    window.open(neo4jBrowserUrl.value, '_blank', 'noopener,noreferrer')
    ElMessage.success('已在新标签页打开 Neo4j Browser')
  } else {
    ElMessage.warning('Neo4j Browser URL 未配置')
  }
}

// 加载图谱数据
const loadGraphData = async () => {
  loading.value = true
  try {
    const data = await getGraphVisualizationData({ limit: nodeLimit.value })

    console.log('=== 调试：后端返回的数据 ===')
    console.log('节点数量:', data.nodes.length)
    console.log('关系数量:', data.relationships.length)

    // 查找病害节点并输出度数
    const diseaseNodes = data.nodes.filter((n: any) => n.name && n.name.includes('病害'))
    if (diseaseNodes.length > 0) {
      console.log('病害节点信息:')
      diseaseNodes.forEach((node: any) => {
        console.log(`  - ${node.name}: id=${node.id}, degree=${node.degree}`)
      })
    }

    // 转换数据格式
    const transformedData = {
      nodes: data.nodes.map((node: any) => ({
        id: node.id,
        name: node.name,
        category: node.type,
        value: node.degree || 0,  // 使用0作为默认值，而不是1
        properties: node.properties || {}
      })),
      links: data.relationships.map((rel: any) => ({
        source: rel.source,
        target: rel.target,
        category: rel.type,
        name: rel.type
      }))
    }

    // 保存到完整数据和当前工作数据
    fullGraphData.value = JSON.parse(JSON.stringify(transformedData)) // 深拷贝
    originalGraphData.value = transformedData

    console.log('转换后的originalGraphData:', {
      nodesCount: originalGraphData.value.nodes.length,
      linksCount: originalGraphData.value.links.length,
      diseaseNodes: originalGraphData.value.nodes.filter((n: any) => n.name && n.name.includes('病害'))
    })

    resetSearchState()

    // 应用节点限制和过滤，确保界面展示符合最新限制
    filterNodes()

    // 检查是否有孤立的边（端点节点不存在）
    const nodeIdSet = new Set(transformedData.nodes.map((n: any) => n.id))
    const orphanLinks = transformedData.links.filter((link: any) =>
      !nodeIdSet.has(link.source) || !nodeIdSet.has(link.target)
    )
    if (orphanLinks.length > 0) {
      console.warn(`发现 ${orphanLinks.length} 条孤立的边（端点节点不存在）:`)
      orphanLinks.forEach((link: any) => {
        console.warn(`  - ${link.category} (${link.source} -> ${link.target})`)
      })
    }

    // 检查自环边（节点指向自己）
    const selfLoopLinks = transformedData.links.filter((link: any) => link.source === link.target)
    if (selfLoopLinks.length > 0) {
      console.info(`发现 ${selfLoopLinks.length} 条自环边（节点指向自己）:`)
      selfLoopLinks.forEach((link: any) => {
        const node = transformedData.nodes.find((n: any) => n.id === link.source)
        console.info(`  - ${link.category}: ${node?.name} -> ${node?.name}`)
      })
    }

    // 检查重复边（相同source和target的边）
    const edgeMap = new Map<string, number>()
    transformedData.links.forEach((link: any) => {
      const key = `${link.source}-${link.target}`
      edgeMap.set(key, (edgeMap.get(key) || 0) + 1)
    })
    const duplicateEdges = Array.from(edgeMap.entries()).filter(([_, count]) => count > 1)
    if (duplicateEdges.length > 0) {
      console.info(`发现 ${duplicateEdges.length} 组重复边（相同source和target）:`)
      duplicateEdges.forEach(([key, count]) => {
        console.info(`  - ${key}: ${count} 条边`)
      })
    }

    // 应用当前的过滤条件
    filterNodes()

    ElMessage.success(`图谱数据加载成功：${data.nodes.length} 个节点，${data.relationships.length} 条边`)
  } catch (error: any) {
    ElMessage.error(`加载图谱数据失败: ${error.message}`)
  } finally {
    loading.value = false
  }
}

// 搜索节点（在前端已有数据中筛选）
const handleSearchNodes = () => {
  // Original content guard · 羊羊小栈版权所有 · 未授权禁止二次封装。
  if (!searchKeyword.value.trim()) {
    ElMessage.warning('请输入搜索关键词')
    return
  }

  const keyword = searchKeyword.value.trim().toLowerCase()

  // 在完整的原始图数据中搜索匹配的节点（而不是当前的originalGraphData）
  const matchedNodes = fullGraphData.value.nodes.filter((node: any) =>
    node.name && node.name.toLowerCase().includes(keyword)
  )

  if (matchedNodes.length === 0) {
    ElMessage.info('未找到匹配的节点')
    return
  }

  // 获取匹配节点的ID集合
  const matchedNodeIds = new Set(matchedNodes.map((node: any) => node.id))

  // 找出所有与匹配节点相关的边（1层邻居）
  const relatedLinks = fullGraphData.value.links.filter((link: any) =>
    matchedNodeIds.has(link.source) || matchedNodeIds.has(link.target)
  )

  // 从相关的边中提取所有涉及的节点ID（包括邻居节点）
  const allRelatedNodeIds = new Set<any>()
  relatedLinks.forEach((link: any) => {
    allRelatedNodeIds.add(link.source)
    allRelatedNodeIds.add(link.target)
  })

  // 获取所有相关的节点
  const relatedNodes = fullGraphData.value.nodes.filter((node: any) =>
    allRelatedNodeIds.has(node.id)
  )

  ElMessage.success(`找到 ${matchedNodes.length} 个匹配节点，展示其 ${relatedNodes.length} 个相关节点和 ${relatedLinks.length} 条关系`)

  // 更新工作数据为搜索结果（不修改fullGraphData）
  originalGraphData.value = {
    nodes: relatedNodes,
    links: relatedLinks
  }

  // 标记为搜索模式
  searchMode.value = true

  // 应用过滤条件并重新渲染
  filterNodes()
}

// 清除搜索，恢复完整图谱
const clearSearch = () => {
  resetSearchState()
  // 从fullGraphData恢复完整图谱数据（不需要重新加载）
  originalGraphData.value = JSON.parse(JSON.stringify(fullGraphData.value)) // 深拷贝
  filterNodes()
  ElMessage.info('已恢复完整图谱视图')
}

const handleNodeLimitChange = async () => {
  resetSearchState()
  await loadGraphData()
}

// 过滤节点
const filterNodes = () => {
  console.log('=== filterNodes 开始 ===')
  console.log('originalGraphData:', {
    nodes: originalGraphData.value.nodes.length,
    links: originalGraphData.value.links.length
  })

  const filteredNodes = originalGraphData.value.nodes.filter((node: any) =>
    selectedNodeTypes.value.includes(node.category)
  ).slice(0, nodeLimit.value)

  console.log('过滤后的节点数:', filteredNodes.length)

  // 创建节点ID集合（统一使用字符串进行比较）
  const nodeIdSet = new Set()
  filteredNodes.forEach((node: any) => {
    nodeIdSet.add(String(node.id))
  })

  // 过滤边（统一使用字符串比较）
  // 先统计哪些边被过滤掉了
  const filteredOutLinks: any[] = []
  const filteredLinks = originalGraphData.value.links.filter((link: any) => {
    const hasSource = nodeIdSet.has(String(link.source))
    const hasTarget = nodeIdSet.has(String(link.target))
    const hasRelType = selectedRelationTypes.value.includes(link.category)

    const passes = hasSource && hasTarget && hasRelType

    if (!passes) {
      filteredOutLinks.push({
        link,
        reason: !hasSource ? '源节点被过滤' : !hasTarget ? '目标节点被过滤' : '关系类型被过滤'
      })
    }

    return passes
  })

  console.log('过滤后的边数:', filteredLinks.length)
  console.log('被过滤掉的边数:', filteredOutLinks.length)

  if (filteredOutLinks.length > 0 && filteredOutLinks.length <= 5) {
    console.log('被过滤掉的边详情:')
    filteredOutLinks.forEach((item: any) => {
      console.log(`  - ${item.link.category} (${item.link.source} -> ${item.link.target}): ${item.reason}`)
    })
  }

  // 重新计算过滤后每个节点的实际连接数
  const nodeDegreeMap = new Map<string, number>()

  // 统计每条边涉及的节点度数（统一使用字符串作为key）
  filteredLinks.forEach((link: any) => {
    const sourceKey = String(link.source)
    const targetKey = String(link.target)

    nodeDegreeMap.set(sourceKey, (nodeDegreeMap.get(sourceKey) || 0) + 1)
    nodeDegreeMap.set(targetKey, (nodeDegreeMap.get(targetKey) || 0) + 1)
  })

  console.log('nodeDegreeMap 大小:', nodeDegreeMap.size)

  // 查找病害节点并输出度数
  const diseaseNodes = filteredNodes.filter((n: any) => n.name && n.name.includes('病害'))
  if (diseaseNodes.length > 0) {
    console.log('病害节点度数计算:')
    diseaseNodes.forEach((node: any) => {
      const nodeKey = String(node.id)
      const degree = nodeDegreeMap.get(nodeKey) || 0
      console.log(`  - ${node.name}: id=${node.id}, key=${nodeKey}, degree=${degree}`)
    })
  }

  // 更新节点的value字段为过滤后的实际连接数
  const nodesWithUpdatedDegree = filteredNodes.map((node: any) => {
    const nodeKey = String(node.id)
    const degree = nodeDegreeMap.get(nodeKey) || 0
    return {
      ...node,
      value: degree  // 使用过滤后的实际连接数
    }
  })

  graphData.value = {
    nodes: nodesWithUpdatedDegree,
    links: filteredLinks
  }

  renderChart()
}

// 过滤关系
const filterRelations = () => {
  filterNodes() // 重新过滤会同时应用关系过滤
}

// 更新布局
const updateLayout = () => {
  renderChart()
}

// 重置布局
const resetLayout = () => {
  if (chartInstance) {
    chartInstance.dispatchAction({ type: 'restore' })
  }
}

// 切换全屏
const toggleFullscreen = () => {
  if (!visualizationContainer.value) return

  if (!isFullscreen.value) {
    // 进入全屏
    const element = visualizationContainer.value
    if (element.requestFullscreen) {
      element.requestFullscreen()
    } else if ((element as any).webkitRequestFullscreen) {
      (element as any).webkitRequestFullscreen()
    } else if ((element as any).mozRequestFullScreen) {
      (element as any).mozRequestFullScreen()
    } else if ((element as any).msRequestFullscreen) {
      (element as any).msRequestFullscreen()
    }
  } else {
    // 退出全屏
    if (document.exitFullscreen) {
      document.exitFullscreen()
    } else if ((document as any).webkitExitFullscreen) {
      (document as any).webkitExitFullscreen()
    } else if ((document as any).mozCancelFullScreen) {
      (document as any).mozCancelFullScreen()
    } else if ((document as any).msExitFullscreen) {
      (document as any).msExitFullscreen()
    }
  }
}

// 监听全屏状态变化
const handleFullscreenChange = () => {
  isFullscreen.value = !!(
    document.fullscreenElement ||
    (document as any).webkitFullscreenElement ||
    (document as any).mozFullScreenElement ||
    (document as any).msFullscreenElement
  )

  // 全屏状态改变后，调整图表大小
  setTimeout(() => {
    if (chartInstance) {
      chartInstance.resize()
    }
  }, 300)
}

const renderChart = () => {
  if (!chartContainer.value) return

  // 每次重建实例，避免 chartInstance 为 null 时 setOption 失效
  if (chartInstance) {
    chartInstance.dispose()
  }
  chartInstance = echarts.init(chartContainer.value)

  // 保证节点有 category，确保与图例匹配
  // 将节点ID转换为字符串，因为ECharts graph需要字符串类型的ID
  const nodes = graphData.value.nodes.map((node: any) => {
    const originalCategory = node.category || 'Unknown'
    const chineseName = getNodeTypeName(originalCategory)
    return {
      ...node,
      id: String(node.id), // 转换为字符串
      name: node.name,
      category: chineseName, // 转换为中文名称，用于图例匹配
      originalCategory: originalCategory, // 保留原始类型
      symbolSize: Math.max(10, Math.min(40, (node.value || 1) * 3)),
      itemStyle: { color: getNodeColor(originalCategory) } // 使用后端配置的颜色
    }
  })

  // 创建节点ID到节点信息的映射
  const nodeIdMap = new Map<string, any>()
  nodes.forEach(node => {
    nodeIdMap.set(node.id, node)
  })

  // 创建节点ID集合，用于验证边的有效性（使用字符串ID）
  const nodeIdSet = new Set(nodes.map(n => n.id))

  console.log('=== renderChart 边过滤 ===')
  console.log('graphData.value.links 数量:', graphData.value.links.length)
  console.log('nodes 数量:', nodes.length)
  console.log('nodeIdSet 大小:', nodeIdSet.size)

  // 保证关系有 source/target，并过滤掉无效的边
  // 将source和target也转换为字符串
  const filteredOutInRender: any[] = []
  const validLinks = graphData.value.links
    .filter((link: any) => {
      const sourceStr = String(link.source)
      const targetStr = String(link.target)
      const hasSource = nodeIdSet.has(sourceStr)
      const hasTarget = nodeIdSet.has(targetStr)
      const isValid = hasSource && hasTarget

      if (!isValid) {
        filteredOutInRender.push({
          link,
          reason: !hasSource ? `源节点${sourceStr}不存在` : `目标节点${targetStr}不存在`
        })
      }

      return isValid
    })

  // 检测重复边并为它们设置不同的曲率
  const edgeCountMap = new Map<string, number>()
  const edgeIndexMap = new Map<string, number>()

  validLinks.forEach((link: any) => {
    const key = `${link.source}-${link.target}`
    edgeCountMap.set(key, (edgeCountMap.get(key) || 0) + 1)
  })

  const links = validLinks.map((link: any) => {
    const sourceStr = String(link.source)
    const targetStr = String(link.target)
    const key = `${sourceStr}-${targetStr}`

    // 获取当前边是该组的第几条
    const currentIndex = edgeIndexMap.get(key) || 0
    edgeIndexMap.set(key, currentIndex + 1)

    const totalCount = edgeCountMap.get(key) || 1

    // 如果有重复边，为每条边设置不同的曲率
    let curveness = 0
    if (totalCount > 1) {
      // 为多条边分配曲率：0.2, 0.4, 0.6...
      curveness = 0.2 + currentIndex * 0.2
    }

    return {
      source: sourceStr, // 转换为字符串
      target: targetStr, // 转换为字符串
      value: link.category,
      name: link.name || link.category,
      relationChinese: getRelationTypeName(link.category), // 添加中文关系名称
      isDuplicate: totalCount > 1, // 标记是否为重复边
      duplicateIndex: currentIndex + 1, // 第几条重复边
      duplicateTotal: totalCount, // 总共有几条重复边
      lineStyle: totalCount > 1 ? {
        curveness: curveness,
        color: '#999',
        width: 1.5
      } : undefined
    }
  })

  console.log('renderChart 后的 links 数量:', links.length)
  console.log('renderChart 中被过滤掉的边数:', filteredOutInRender.length)

  if (filteredOutInRender.length > 0) {
    console.warn('renderChart 中被过滤掉的边:')
    filteredOutInRender.forEach((item: any) => {
      console.warn(`  - ${item.link.category} (${item.link.source} -> ${item.link.target}): ${item.reason}`)
    })
  }

  // 构造分类（categories），确保包含所有节点类型并使用正确的颜色
  const allNodeTypes = [
    'PlantDisease', 'Plant', 'Pathogen', 'Symptom',
    'Prevention', 'Location', 'Season', 'Environment',
    'Document', 'TimePoint'
  ]

  // 使用所有定义的节点类型
  const categories = allNodeTypes.map(nodeType => ({
    name: getNodeTypeName(nodeType), // 使用中文名称
    itemStyle: { color: getNodeColor(nodeType) } // 使用后端配置的颜色
  }))

  const option = {
    title: {
      text: '植物病害知识图谱',
      subtext: `节点数: ${nodes.length}, 关系数: ${links.length}`,
      left: 'center',
      textStyle: {
        fontSize: 20,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        if (params.dataType === 'node') {
          return `
            <div style="padding: 8px;">
              <b>${params.data.name}</b><br/>
              类型: ${params.data.category}<br/>
              连接数: ${params.data.value || 0}
            </div>
          `
        } else if (params.dataType === 'edge') {
          // 获取源节点和目标节点的名称
          const sourceNode = nodeIdMap.get(params.data.source)
          const targetNode = nodeIdMap.get(params.data.target)
          const sourceName = sourceNode ? sourceNode.name : params.data.source
          const targetName = targetNode ? targetNode.name : params.data.target
          const relationName = params.data.relationChinese || params.data.name

          let duplicateInfo = ''
          if (params.data.isDuplicate) {
            duplicateInfo = `<br/><span style="color: #f56c6c; font-size: 11px;">重复边 ${params.data.duplicateIndex}/${params.data.duplicateTotal}</span>`
          }

          return `
            <div style="padding: 8px;">
              <b>${sourceName}</b> → <b>${targetName}</b><br/>
              关系: ${relationName}${duplicateInfo}
            </div>
          `
        }
        return ''
      }
    },
    legend: {
      data: categories.map(c => c.name), // 必须和 categories[].name 对应
      bottom: 10,
      type: 'scroll', // 避免分类太多挤不下
      orient: 'horizontal'
    },
    series: [
      {
        type: 'graph',
        layout: layoutType.value,
        data: nodes,
        links,
        categories,
        roam: true,
        draggable: true,
        edgeSymbol: ['none', 'arrow'],
        edgeSymbolSize: 6,
        label: {
          show: true,
          position: 'right',
          formatter: '{b}',
          fontSize: 11
        },
        edgeLabel: {
          show: false,
          fontSize: 10,
          formatter: (params: any) => params.data.value || ''
        },
        lineStyle: {
          color: '#ccc',
          width: 1,
          opacity: 0.6,
          curveness: 0.1 // 默认曲率，重复边会有更高的曲率
        },
        emphasis: {
          focus: 'adjacency',
          label: {
            fontSize: 14,
            fontWeight: 'bold'
          },
          lineStyle: {
            width: 2.5,
            opacity: 1,
            color: '#666'
          }
        },
        force: {
          repulsion: 300,
          gravity: 0.15,
          edgeLength: 120,
          layoutAnimation: true
        }
      }
    ]
  }

  chartInstance.setOption(option)
  chartInstance.resize()

  // 添加点击事件
  chartInstance.on('click', (params: any) => {
    if (params.dataType === 'node') {
      selectedNodeDetail.value = {
        ...params.data,
        properties: params.data.properties || {},
        connections: graphData.value.links
          .filter((link: any) => link.source === params.data.id || link.target === params.data.id)
          .map((link: any) => link.source === params.data.id ? link.target : link.source)
      }
      detailDrawerVisible.value = true
    }
  })
}

// 初始化图表
const initChart = () => {
  if (chartContainer.value) {
    if (chartInstance) {
      chartInstance.dispose()
    }
    chartInstance = echarts.init(chartContainer.value)
  }

  window.addEventListener('resize', () => chartInstance?.resize())
}

onMounted(async () => {
  await nextTick()
  // 先加载配置，再加载数据
  await loadGraphConfig()
  setTimeout(() => {
    initChart()
    loadGraphData()
  }, 50)

  // 添加全屏状态监听
  document.addEventListener('fullscreenchange', handleFullscreenChange)
  document.addEventListener('webkitfullscreenchange', handleFullscreenChange)
  document.addEventListener('mozfullscreenchange', handleFullscreenChange)
  document.addEventListener('msfullscreenchange', handleFullscreenChange)
})

onUnmounted(() => {
  // 移除全屏状态监听
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
  document.removeEventListener('webkitfullscreenchange', handleFullscreenChange)
  document.removeEventListener('mozfullscreenchange', handleFullscreenChange)
  document.removeEventListener('msfullscreenchange', handleFullscreenChange)
})
</script>

<style scoped>
.kg-visualization {
  padding: 0;
  position: relative;
}

/* 全屏模式样式 */
.kg-visualization:fullscreen {
  background: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}

.kg-visualization:-webkit-full-screen {
  background: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}

.kg-visualization:-moz-full-screen {
  background: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}

.kg-visualization:-ms-fullscreen {
  background: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}

/* 全屏模式下的图表容器 */
.kg-visualization:fullscreen .chart-container,
.kg-visualization:-webkit-full-screen .chart-container,
.kg-visualization:-moz-full-screen .chart-container,
.kg-visualization:-ms-fullscreen .chart-container {
  height: calc(100vh - 280px) !important;
}

.control-card {
  margin-bottom: 24px;
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
}

.header-controls {
  display: flex;
  gap: 10px;
}

.control-panel {
  padding: 10px 0;
}

.chart-card {
  position: relative;
  border-radius: 12px;
}

.chart-container {
  width: 100%;
  height: 700px;
  background: #fff;
  transition: height 0.3s ease;
}

.node-detail {
  padding: 20px;
}

.node-properties,
.node-connections {
  margin-top: 20px;
}

.node-properties h4,
.node-connections h4 {
  margin-bottom: 10px;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

:deep(.el-drawer__header) {
  margin-bottom: 20px;
  padding: 20px;
  border-bottom: 1px solid #ebeef5;
}

:deep(.el-form-item) {
  margin-bottom: 15px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #606266;
}

:deep(.el-checkbox-group) {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

:deep(.el-checkbox) {
  margin-right: 0;
}

@media (max-width: 768px) {
  .chart-container {
    height: 500px;
  }

  .control-panel .el-col {
    margin-bottom: 15px;
  }
}
</style>
