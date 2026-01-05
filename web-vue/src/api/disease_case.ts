
import request from './request'
import { keysToCamel, keysToSnake } from '@/utils/caseConvert'

// 植物病害案例图片接口定义
export interface CaseImage {
  bucket: string
  object_key: string  // 统一使用下划线命名（与后端一致）
}

// 植物病害案例接口类型定义
export interface DiseaseCase {
  id: number
  diseaseId: number
  diseaseName: string
  diseaseCode: string
  caseTitle: string
  caseDate: string
  location?: string
  plantType?: string
  infectionArea?: number
  severityLevel?: string
  description?: string
  economicLoss?: number
  treatmentMethod?: string
  treatmentResult?: string
  dataSource?: string
  images?: CaseImage[]
  createTime: string
  updateTime: string
}

export interface DiseaseCaseForm {
  id?: number | undefined
  diseaseId: number | undefined
  caseTitle: string
  caseDate: string | undefined
  location?: string | undefined
  plantType?: string | undefined
  infectionArea?: number | undefined
  severityLevel?: string | undefined
  description?: string | undefined
  economicLoss?: number | undefined
  treatmentMethod?: string | undefined
  treatmentResult?: string | undefined
  dataSource?: string | undefined
  images?: CaseImage[] | undefined
}

export interface UploadImagesResponse {
  images: CaseImage[]
}

export interface DiseaseCaseQueryParams {
  page?: number
  size?: number
  keyword?: string
  disease_id?: number
  plant_type?: string
  severity_level?: string
  location?: string
}

export interface DiseaseCaseListResponse {
  list: DiseaseCase[]
  total: number
  page: number
  size: number
}

export interface PlantTypeStat {
  plantType: string | null
  count: number
}

export interface SeverityLevelStat {
  severityLevel: string | null
  count: number
}

export interface DiseaseCaseAggregate {
  diseaseName: string | null
  caseCount: number
}

export interface DiseaseCaseStatistics {
  totalCases: number
  plantTypeStats: PlantTypeStat[]
  severityStats: SeverityLevelStat[]
  diseaseStats: DiseaseCaseAggregate[]
}

// 植物病害案例管理API
export const diseaseCaseApi = {
  // 创建植物病害案例
  create: (data: DiseaseCaseForm) => {
    return request.post<void>('/disease-case/create', keysToSnake(data))
  },

  // 获取植物病害案例列表
  getList: async (params: DiseaseCaseQueryParams) => {
    const res = await request.get('/disease-case/list', { params })
    return keysToCamel<DiseaseCaseListResponse>(res)
  },

  // 获取植物病害案例详情
  getDetail: async (id: number) => {
    const res = await request.get(`/disease-case/detail/${id}`)
    return keysToCamel<DiseaseCase>(res)
  },

  // 更新植物病害案例
  update: (id: number, data: DiseaseCaseForm) => {
    return request.put<void>(`/disease-case/update/${id}`, keysToSnake(data))
  },

  // 删除植物病害案例
  delete: (id: number) => {
    return request.delete<void>(`/disease-case/delete/${id}`)
  },

  // 获取植物病害案例统计信息
  getStatistics: async () => {
    const res = await request.get('/disease-case/statistics')
    return keysToCamel<DiseaseCaseStatistics>(res)
  },

  // 根据病害ID获取案例列表
  getCasesByDisease: async (diseaseId: number, params?: {
    page?: number
    size?: number
  }) => {
    const res = await request.get(`/disease-case/by-disease/${diseaseId}`, { params })
    return keysToCamel<DiseaseCaseListResponse>(res)
  },

  // 批量删除植物病害案例
  batchDelete: (ids: number[]) => {
    return request.delete<void>('/disease-case/batch-delete', { data: { ids } })
  },

  // 批量上传病害案例图片
  uploadImages: async (files: File[]) => {
    const formData = new FormData()
    files.forEach(file => {
      formData.append('files', file)
    })
    const res = await request.post('/disease-case/upload-images', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return keysToCamel<UploadImagesResponse>(res)
  }
}
