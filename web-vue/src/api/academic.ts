import request from '@/utils/request'

// 教务政策相关API
export const academicPolicyApi = {
  // 获取政策列表
  getList: (params: any) => {
    return request.get<any>('/admin/academic-policies', params)
  },

  // 获取政策详情
  getDetail: (id: number) => {
    return request.get<any>(`/admin/academic-policies/${id}`)
  },

  // 创建政策
  create: (data: any) => {
    return request.post<any>('/admin/academic-policies', data)
  },

  // 更新政策
  update: (id: number, data: any) => {
    return request.put<any>(`/admin/academic-policies/${id}`, data)
  },

  // 删除政策
  delete: (id: number) => {
    return request.delete<any>(`/admin/academic-policies/${id}`)
  }
}

// 教务案例相关API
export const academicCaseApi = {
  // 获取案例列表
  getList: (params: any) => {
    return request.get<any>('/admin/academic-cases', params)
  },

  // 获取案例详情
  getDetail: (id: number) => {
    return request.get<any>(`/admin/academic-cases/${id}`)
  },

  // 创建案例
  create: (data: any) => {
    return request.post<any>('/admin/academic-cases', data)
  },

  // 更新案例
  update: (id: number, data: any) => {
    return request.put<any>(`/admin/academic-cases/${id}`, data)
  },

  // 删除案例
  delete: (id: number) => {
    return request.delete<any>(`/admin/academic-cases/${id}`)
  }
}
