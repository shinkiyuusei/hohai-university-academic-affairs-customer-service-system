
import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, InternalAxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'

// 创建 axios 实例
const instance: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 120000,
})

// 请求拦截器
instance.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 从 localStorage 获取 token
    const userInfo = localStorage.getItem('userInfo')
    if (userInfo) {
      const { token } = JSON.parse(userInfo)
      if (token && config.headers) {
        // 添加 token 到请求头
        config.headers.Authorization = `Bearer ${token}`
      }
    }
    
    // 记录请求开始时间
    config.metadata = {
      startTime: Date.now()
    }
    
    // 记录请求日志
    console.log(`[Frontend Request] ${config.method?.toUpperCase()} ${config.url}`)
    if (config.data) {
      console.log(`[Request Data]`, config.data)
    }
    
    return config
  },
  (error) => {
    console.error(`[Frontend Request Error]`, error)
    return Promise.reject(error)
  }
)

// 响应拦截器
instance.interceptors.response.use(
  (response: AxiosResponse) => {
    // 计算响应时间
    if (response.config.metadata) {
      const responseTime = Date.now() - (response.config.metadata as any).startTime
      
      // 记录响应日志
      console.log(`[Frontend Response] ${response.config.method?.toUpperCase()} ${response.config.url} - ${response.status} (${responseTime}ms)`)
      if (response.data && response.config.responseType !== 'blob') {
        console.log(`[Response Data]`, response.data)
      }
    }

    // 如果是二进制数据，直接返回
    if (response.config.responseType === 'blob') {
      return response.data
    }

    const { code, msg, data } = response.data

    // 请求成功
    if (code === 200 || code === 0) {
      return data
    }

    // 登录过期
    if (code === 401) {
      // 直接清除本地状态，避免循环依赖
      localStorage.removeItem('userInfo')
      // 跳转到登录页
      window.location.href = '/login'
      return Promise.reject(new Error('登录已过期，请重新登录'))
    }

    // 显示错误信息
    const error = new Error(msg || '请求失败') as Error & { response?: any }
    error.response = response
    ElMessage.error(msg || '请求失败')
    return Promise.reject(error)
  },
  (error) => {
    // 计算响应时间
    if (error.config && error.config.metadata) {
      const responseTime = Date.now() - (error.config.metadata as any).startTime
      
      // 记录错误响应日志
      console.error(`[Frontend Response Error] ${error.config.method?.toUpperCase()} ${error.config.url} - ${error.response?.status || 'Network Error'} (${responseTime}ms)`)
    } else {
      console.error(`[Frontend Response Error] Network Error`)
    }
    
    // 处理网络错误
    let message = '网络请求失败，请检查网络连接'
    if (error.response) {
      const { status, data } = error.response
      switch (status) {
        case 400:
          message = data.msg || '请求参数错误'
          break
        case 401:
          message = '登录已过期，请重新登录'
          // 直接清除本地状态，避免循环依赖
          localStorage.removeItem('userInfo')
          // 跳转到登录页
          window.location.href = '/login'
          break
        case 403:
          message = '没有权限访问该资源'
          break
        case 404:
          message = '请求的资源不存在'
          break
        case 500:
          message = '服务器内部错误'
          break
        default:
          message = data.msg || '请求失败'
      }
    }
    if (!error.config?.silent) {
      ElMessage.error(message)
    }
    return Promise.reject(error)
  }
)

// 封装请求方法
const request = {
  get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return instance.get(url, config)
  },

  post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return instance.post(url, data, config)
  },

  put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return instance.put(url, data, config)
  },

  delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return instance.delete(url, config)
  },
}

export default request
