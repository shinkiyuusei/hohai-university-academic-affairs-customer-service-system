
<template>
  <div class="dashboard">
    <!-- 页面标题 -->
    <div class="dashboard-header">
      <h1 class="page-title">
        <el-icon class="title-icon"><Monitor /></el-icon>
        系统控制台
      </h1>
      <p class="page-subtitle">实时监控系统运行状态和数据统计</p>
    </div>

    <!-- 统计卡片区域 -->
    <div class="stats-grid">
      <div class="stat-card" v-loading="loading.stats">
        <div class="stat-icon users">
          <el-icon><User /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.totalUsers }}</div>
          <div class="stat-label">用户总数</div>
        </div>
      </div>

      <div class="stat-card" v-loading="loading.stats">
        <div class="stat-icon documents">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.totalDocuments }}</div>
          <div class="stat-label">文档总数</div>
        </div>
      </div>

      <div class="stat-card" v-loading="loading.stats">
        <div class="stat-icon graph">
          <el-icon><DataLine /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.totalGraphNodes }}</div>
          <div class="stat-label">图谱节点</div>
        </div>
      </div>



      <div class="stat-card" v-loading="loading.stats">
        <div class="stat-icon conversations">
          <el-icon><ChatDotRound /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.totalConversations }}</div>
          <div class="stat-label">问答会话</div>
        </div>
      </div>

      <div class="stat-card" v-loading="loading.stats">
        <div class="stat-icon diseases">
          <el-icon><Promotion /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.totalDiseases }}</div>
          <div class="stat-label">文档总数</div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-grid">
      <!-- 文档类型分布 -->
      <div class="chart-card">
        <div class="chart-header">
          <h3>文档类型分布</h3>
        </div>
        <div class="chart-content" v-loading="loading.documentTypeChart">
          <div ref="documentTypeChartRef" class="chart-container"></div>
        </div>
      </div>

      <!-- 用户注册趋势 -->
      <div class="chart-card">
        <div class="chart-header">
          <h3>用户注册趋势</h3>
        </div>
        <div class="chart-content" v-loading="loading.userTrendChart">
          <div ref="userTrendChartRef" class="chart-container"></div>
        </div>
      </div>



      <!-- 问答会话趋势 -->
      <div class="chart-card chart-card-full">
        <div class="chart-header">
          <h3>问答会话创建趋势</h3>
        </div>
        <div class="chart-content" v-loading="loading.conversationTrendChart">
          <div ref="conversationTrendChartRef" class="chart-container"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { User, DataLine, Monitor, Document, Tools, ChatDotRound, Promotion } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { getDashboardData } from '@/api/admin'
import { ElMessage } from 'element-plus'

// 扩展类型定义
interface DashboardData {
  stats: {
    totalUsers: number
    totalDocuments: number
    totalGraphNodes: number
    totalConversations: number
    totalDiseases: number
  }
  documentTypeStats: Array<{ file_type: string, count: number }>
  userTrendData: {
    months: string[]
    counts: number[]
  }

  conversationTrendData: {
    months: string[]
    counts: number[]
  }
}

// 统计数据
const stats = ref({
  totalUsers: 0,
  totalDocuments: 0,
  totalGraphNodes: 0,
  totalConversations: 0,
  totalDiseases: 0
})
// 加载状态
const loading = ref({
  stats: false,
  documentTypeChart: false,
  userTrendChart: false,

  conversationTrendChart: false
})

// 图表元素引用
const documentTypeChartRef = ref()
const userTrendChartRef = ref()

const conversationTrendChartRef = ref()

// 图表实例
let documentTypeChart: echarts.ECharts | null = null
let userTrendChart: echarts.ECharts | null = null

let conversationTrendChart: echarts.ECharts | null = null

// 仪表盘数据缓存
const dashboardDataCache = ref<DashboardData | null>(null)

// 获取统计数据
const loadStats = async () => {
  try {
    loading.value.stats = true

    const response = await getDashboardData()
    dashboardDataCache.value = response
    stats.value = response.stats

  } catch (error) {
    console.error('获取统计数据失败:', error)
    ElMessage.error('获取统计数据失败')
  } finally {
    loading.value.stats = false
  }
}

// 初始化文档类型分布图表
const initDocumentTypeChart = async () => {
  try {
    loading.value.documentTypeChart = true

    // 确保有数据
    if (!dashboardDataCache.value) {
      await loadStats()
    }

    // 转换为图表数据格式
    const chartData = dashboardDataCache.value?.documentTypeStats.map(item => ({
      value: item.count,
      name: item.file_type?.toUpperCase() || 'UNKNOWN'
    })) || []

    // 为不同文档类型设置不同渐变色
    const colors = {
      'PDF': {
        start: '#fecaca',
        middle: '#fca5a5',
        end: '#f87171'
      },
      'DOCX': {
        start: '#a5f3fc',
        middle: '#67e8f9',
        end: '#22d3ee'
      },
      'DOC': {
        start: '#ddd6fe',
        middle: '#c4b5fd',
        end: '#a78bfa'
      },
      'TXT': {
        start: '#bbf7d0',
        middle: '#86efac',
        end: '#4ade80'
      },
      'UNKNOWN': {
        start: '#e2e8f0',
        middle: '#cbd5e1',
        end: '#94a3b8'
      }
    }

    const option = {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c}件 ({d}%)',
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        borderColor: 'rgba(0, 0, 0, 0.1)',
        borderWidth: 1,
        textStyle: {
          color: '#334155',
          fontSize: 13,
          fontWeight: 500
        },
        shadowBlur: 10,
        shadowColor: 'rgba(0, 0, 0, 0.1)'
      },
      legend: {
        orient: 'horizontal',
        bottom: '8%',
        left: 'center',
        textStyle: {
          color: '#64748b',
          fontSize: 13,
          fontWeight: 500
        },
        itemGap: 20,
        icon: 'circle',
        itemWidth: 12,
        itemHeight: 12
      },
      series: [
        {
          name: '文档类型',
          type: 'pie',
          radius: ['38%', '68%'],
          center: ['50%', '40%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 12,
            shadowBlur: 22,
            shadowColor: 'rgba(0, 0, 0, 0.12)',
            shadowOffsetY: 5
          },
          label: {
            show: true,
            position: 'outside',
            formatter: '{b}\n{c}件',
            fontSize: 12,
            fontWeight: 600,
            color: '#475569',
            distance: 12
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 14,
              fontWeight: 700,
              color: '#1e293b'
            },
            itemStyle: {
              shadowBlur: 30,
              shadowOffsetX: 0,
              shadowOffsetY: 8,
              shadowColor: 'rgba(0, 0, 0, 0.18)'
            },
            scale: true,
            scaleSize: 10
          },
          labelLine: {
            show: true,
            lineStyle: {
              color: '#cbd5e1',
              width: 2
            },
            length: 18,
            length2: 12
          },
          data: chartData.map(item => {
            const colorConfig = colors[item.name as keyof typeof colors] || colors.UNKNOWN;
            return {
              ...item,
              itemStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 1, 1, [
                  { offset: 0, color: colorConfig.start },
                  { offset: 0.5, color: colorConfig.middle },
                  { offset: 1, color: colorConfig.end }
                ]),
                borderRadius: 12,
                shadowBlur: 22,
                shadowColor: 'rgba(0, 0, 0, 0.12)',
                shadowOffsetY: 5
              }
            };
          })
        }
      ]
    }

    documentTypeChart = echarts.init(documentTypeChartRef.value)
    documentTypeChart.setOption(option)

  } catch (error) {
    console.error('初始化文档类型分布图表失败:', error)
  } finally {
    loading.value.documentTypeChart = false
  }
}

// 初始化用户趋势图表
const initUserTrendChart = async () => {
  try {
    loading.value.userTrendChart = true

    // 确保有数据
    if (!dashboardDataCache.value) {
      await loadStats()
    }

    const { months, counts } = dashboardDataCache.value?.userTrendData || { months: [], counts: [] }

    const option = {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross',
          crossStyle: {
            color: '#cbd5e1',
            width: 1,
            type: 'dashed'
          }
        },
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        borderColor: 'rgba(0, 0, 0, 0.1)',
        borderWidth: 1,
        textStyle: {
          color: '#334155',
          fontSize: 13,
          fontWeight: 500
        },
        shadowBlur: 15,
        shadowColor: 'rgba(0, 0, 0, 0.1)',
        padding: [12, 16]
      },
      grid: {
        left: '5%',
        right: '5%',
        bottom: '10%',
        top: '8%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: months,
        axisLine: {
          lineStyle: {
            color: '#e2e8f0',
            width: 2
          }
        },
        axisTick: {
          show: false
        },
        axisLabel: {
          color: '#64748b',
          fontSize: 12,
          fontWeight: 500,
          margin: 12
        }
      },
      yAxis: {
        type: 'value',
        splitLine: {
          lineStyle: {
            color: '#f1f5f9',
            width: 1,
            type: 'dashed'
          }
        },
        axisLine: {
          show: false
        },
        axisTick: {
          show: false
        },
        axisLabel: {
          color: '#64748b',
          fontSize: 12,
          fontWeight: 500
        }
      },
      series: [
        {
          name: '新增用户数',
          type: 'line',
          smooth: true,
          symbol: 'circle',
          symbolSize: 8,
          lineStyle: {
            width: 4,
            color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
              { offset: 0, color: '#95de64' },
              { offset: 1, color: '#52c41a' }
            ]),
            shadowBlur: 10,
            shadowColor: 'rgba(82, 196, 26, 0.3)',
            shadowOffsetY: 3
          },
          itemStyle: {
            color: '#fff',
            borderColor: '#52c41a',
            borderWidth: 3,
            shadowBlur: 8,
            shadowColor: 'rgba(82, 196, 26, 0.4)'
          },
          areaStyle: {
            opacity: 0.5,
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              {
                offset: 0,
                color: 'rgba(149, 222, 100, 0.6)'
              },
              {
                offset: 0.7,
                color: 'rgba(82, 196, 26, 0.3)'
              },
              {
                offset: 1,
                color: 'rgba(82, 196, 26, 0.1)'
              }
            ]),
            shadowBlur: 20,
            shadowColor: 'rgba(82, 196, 26, 0.1)',
            shadowOffsetY: 10
          },
          emphasis: {
            focus: 'series',
            itemStyle: {
              color: '#fff',
              borderColor: '#73d13d',
              borderWidth: 4,
              shadowBlur: 15,
              shadowColor: 'rgba(115, 209, 61, 0.6)'
            },
            lineStyle: {
              width: 5,
              shadowBlur: 15,
              shadowColor: 'rgba(82, 196, 26, 0.5)'
            }
          },
          data: counts
        }
      ]
    }

    userTrendChart = echarts.init(userTrendChartRef.value)
    userTrendChart.setOption(option)

  } catch (error) {
    console.error('初始化用户趋势图表失败:', error)
  } finally {
    loading.value.userTrendChart = false
  }
}



// 初始化问答会话趋势图表
const initConversationTrendChart = async () => {
  try {
    loading.value.conversationTrendChart = true

    // 确保有数据
    if (!dashboardDataCache.value) {
      await loadStats()
    }

    // 从缓存获取会话趋势数据
    const { months, counts } = dashboardDataCache.value?.conversationTrendData || { months: [], counts: [] }

    const option = {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross',
          crossStyle: {
            color: '#cbd5e1',
            width: 1,
            type: 'dashed'
          }
        },
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        borderColor: 'rgba(0, 0, 0, 0.1)',
        borderWidth: 1,
        textStyle: {
          color: '#334155',
          fontSize: 13,
          fontWeight: 500
        },
        shadowBlur: 15,
        shadowColor: 'rgba(0, 0, 0, 0.1)',
        padding: [12, 16]
      },
      grid: {
        left: '5%',
        right: '5%',
        bottom: '10%',
        top: '8%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: months,
        axisLine: {
          lineStyle: {
            color: '#e2e8f0',
            width: 2
          }
        },
        axisTick: {
          show: false
        },
        axisLabel: {
          color: '#64748b',
          fontSize: 12,
          fontWeight: 500,
          margin: 12
        }
      },
      yAxis: {
        type: 'value',
        splitLine: {
          lineStyle: {
            color: '#f1f5f9',
            width: 1,
            type: 'dashed'
          }
        },
        axisLine: {
          show: false
        },
        axisTick: {
          show: false
        },
        axisLabel: {
          color: '#64748b',
          fontSize: 12,
          fontWeight: 500
        }
      },
      series: [
        {
          name: '新增会话数',
          type: 'line',
          smooth: true,
          symbol: 'circle',
          symbolSize: 8,
          lineStyle: {
            width: 4,
            color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
              { offset: 0, color: '#b7eb8f' },
              { offset: 1, color: '#73d13d' }
            ]),
            shadowBlur: 10,
            shadowColor: 'rgba(115, 209, 61, 0.3)',
            shadowOffsetY: 3
          },
          itemStyle: {
            color: '#fff',
            borderColor: '#73d13d',
            borderWidth: 3,
            shadowBlur: 8,
            shadowColor: 'rgba(115, 209, 61, 0.4)'
          },
          areaStyle: {
            opacity: 0.5,
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              {
                offset: 0,
                color: 'rgba(183, 235, 143, 0.6)'
              },
              {
                offset: 0.7,
                color: 'rgba(115, 209, 61, 0.3)'
              },
              {
                offset: 1,
                color: 'rgba(115, 209, 61, 0.1)'
              }
            ]),
            shadowBlur: 20,
            shadowColor: 'rgba(115, 209, 61, 0.1)',
            shadowOffsetY: 10
          },
          emphasis: {
            focus: 'series',
            itemStyle: {
              color: '#fff',
              borderColor: '#95de64',
              borderWidth: 4,
              shadowBlur: 15,
              shadowColor: 'rgba(149, 222, 100, 0.6)'
            },
            lineStyle: {
              width: 5,
              shadowBlur: 15,
              shadowColor: 'rgba(115, 209, 61, 0.5)'
            }
          },
          data: counts
        }
      ]
    }

    conversationTrendChart = echarts.init(conversationTrendChartRef.value)
    conversationTrendChart.setOption(option)

  } catch (error) {
    console.error('初始化问答会话趋势图表失败:', error)
  } finally {
    loading.value.conversationTrendChart = false
  }
}

// 窗口大小改变时重新绘制图表
const handleResize = () => {
  documentTypeChart?.resize()
  userTrendChart?.resize()

  conversationTrendChart?.resize()
}

// 初始化所有数据
const initDashboard = async () => {
  await loadStats()
  await Promise.all([
    initDocumentTypeChart(),
    initUserTrendChart(),

    initConversationTrendChart()
  ])
}

onMounted(() => {
  initDashboard()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  documentTypeChart?.dispose()
  userTrendChart?.dispose()

  conversationTrendChart?.dispose()
})
</script>

<style scoped>
.dashboard {
  padding: 24px;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}

/* 页面标题 */
.dashboard-header {
  margin-bottom: 32px;
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-icon {
  font-size: 32px;
  color: var(--primary-color);
}

.page-subtitle {
  color: #64748b;
  margin: 0;
  font-size: 15px;
  line-height: 1.5;
}

/* 统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  gap: 20px;
  transition: all 0.3s ease;
  border: 1px solid #e2e8f0;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
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
  flex-shrink: 0;
}

.stat-icon.users {
  background: linear-gradient(135deg, #52c41a 0%, #389e0d 100%);
}

.stat-icon.documents {
  background: linear-gradient(135deg, #73d13d 0%, #52c41a 100%);
}

.stat-icon.graph {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-icon.cases {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.conversations {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.stat-icon.diseases {
  background: linear-gradient(135deg, #30cfd0 0%, #330867 100%);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 4px;
  line-height: 1;
}

.stat-label {
  color: #64748b;
  font-size: 14px;
  font-weight: 500;
}

/* 图表网格 */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
  gap: 24px;
}

.chart-card {
  background: linear-gradient(135deg, #ffffff 0%, #fafbfc 100%);
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08), 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(226, 232, 240, 0.6);
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.chart-card-full {
  grid-column: 1 / -1;
}

.chart-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--gradient-primary);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.chart-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12), 0 4px 8px rgba(0, 0, 0, 0.08);
}

.chart-card:hover::before {
  opacity: 1;
}

.chart-header {
  padding: 24px 28px 16px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.9) 100%);
  border-bottom: 1px solid rgba(241, 245, 249, 0.8);
  position: relative;
}

.chart-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  letter-spacing: -0.025em;
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
}

.chart-header h3::before {
  content: '';
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--gradient-primary);
  flex-shrink: 0;
}

.chart-content {
  padding: 24px 28px 28px;
  min-height: 240px;
  background: rgba(255, 255, 255, 0.6);
}

.chart-container {
  width: 100%;
  height: 320px;
  border-radius: 8px;
  position: relative;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dashboard {
    padding: 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .charts-grid {
    grid-template-columns: 1fr;
  }

  .chart-container {
    height: 250px;
  }
}
</style>
