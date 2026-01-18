
import request from './request'
import { keysToCamel, keysToSnake } from '@/utils/caseConvert'

// 教务政策信息接口类型定义
export interface AcademicPolicy {
  id: number
  policyCode: string
  policyName: string
  policyType?: string
  content?: string
  summary?: string
  effectiveDate?: string
  status?: string
  description?: string
  createTime: string
  updateTime: string
}

export interface AcademicPolicyForm {
  id?: number | undefined
  policyCode: string
  policyName: string
  policyType?: string | undefined
  content?: string | undefined
  summary?: string | undefined
  effectiveDate?: string | undefined
  status?: string | undefined
  description?: string | undefined
}

export interface AcademicPolicyQueryParams {
  page?: number
  size?: number
  keyword?: string
}

export interface AcademicPolicyListResponse {
  list: AcademicPolicy[]
  total: number
  page: number
  size: number
}

export interface AcademicPolicyOption {
  value: number
  label: string
}

// 教务政策信息管理API
export const academicPolicyApi = {
  // 创建教务政策信息
  create: (data: AcademicPolicyForm) => {
    return request.post<void>('/api/academic-policy/create', keysToSnake(data))
  },

  // 获取教务政策信息列表
  getList: async (params: AcademicPolicyQueryParams) => {
    const res = await request.get('/api/academic-policy/list', { params })
    return keysToCamel<AcademicPolicyListResponse>(res)
  },

  // 获取教务政策信息详情
  getDetail: async (id: number) => {
    const res = await request.get(`/api/academic-policy/detail/${id}`)
    return keysToCamel<AcademicPolicy>(res)
  },

  // 更新教务政策信息
  update: (id: number, data: AcademicPolicyForm) => {
    return request.put<void>(`/api/academic-policy/update/${id}`, keysToSnake(data))
  },

  // 删除教务政策信息
  delete: (id: number) => {
    return request.delete<void>(`/api/academic-policy/delete/${id}`)
  },

  // 获取教务政策选项列表（用于下拉选择）
  getOptions: () => {
    return request.get<AcademicPolicyOption[]>('/api/academic-policy/options')
  }
}
