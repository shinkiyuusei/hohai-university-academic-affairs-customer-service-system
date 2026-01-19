import request from '@/api/request'

// 控制台数据类型定义
export interface DashboardStats {
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

/**
 * 获取控制台仪表板数据
 */
export const getDashboardData = () => {
  return request.get<DashboardStats>('/api/admin/dashboard')
}
