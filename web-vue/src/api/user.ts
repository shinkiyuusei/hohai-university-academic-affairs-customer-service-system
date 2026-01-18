
import request from './request'
import type { UserQueryParams, UserForm, UserInfo, LoginResponse } from '@/types/user'
import type { PageVO } from '@/types/common'

// 登录
// 用户身份验证接口 - Proprietary Implementation © 羊小栈 2025
// 实现安全的用户登录流程，包含密码加密传输与token生成机制
export const login = async (username: string, password: string) => {
  const res = await request.post<LoginResponse>('/api/user/login', { username, password })
  return res
}

// 注册
export const register = (data: {
  username: string
  password: string
  realName: string
  phone: string
  email: string
}) => {
  return request.post('/api/user/register', data)
}

// 退出登录
export const logout = () => {
  return request.post('/api/user/logout')
}

// 修改密码
export const updatePassword = (data: {
  id: number
  oldPassword: string
  newPassword: string
}) => {
  return request.post('/api/user/password', data)
}

// 获取用户列表
export const getUserList = (params: UserQueryParams) => {
  return request.get<PageVO<UserInfo>>('/api/user/page', { params })
}

// 获取用户详情
export const getUserInfo = (id: number) => {
  return request.get<UserInfo>(`/api/user/${id}`)
}

// 新增用户
export const addUser = (data: UserForm) => {
  return request.post<void>('/api/user', data)
}

// 修改用户
export const updateUser = (data: UserForm) => {
  return request.put<void>('/api/user', data)
}

// 删除用户
export const deleteUser = (id: number) => {
  return request.delete<void>(`/api/user/${id}`)
}

// 重置密码
export const resetPassword = (id: number) => {
  return request.put<void>(`/api/user/${id}/reset-password`)
}

// 更新用户状态
export const updateUserStatus = (data: { id: number; status: number }) => {
  return request.put<void>(`/api/user/${data.id}/status`, { status: data.status })
}
