
import request from './request'

// 文档管理API
export const documentApi = {
  // 上传文档
  upload: (data: FormData) => {
    return request.post('/document/upload', data, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 获取文档列表
  getList: (params: {
    page?: number
    size?: number
    keyword?: string
  }) => {
    return request.get('/document/list', { params })
  },

  // 获取文档详情
  getDetail: (id: number) => {
    return request.get(`/document/detail/${id}`)
  },

  // 删除文档
  delete: (id: number) => {
    return request.delete(`/document/delete/${id}`)
  },

  // 更新文档
  update: (id: number, data: {
    title: string
    summary?: string
    content?: string
  }) => {
    return request.put(`/document/update/${id}`, data)
  },

  // 使用本地Qwen模型生成文档摘要
  generateSummary: (content: string) => {
    return request.post('/document/generate-summary', { content })
  }
}
