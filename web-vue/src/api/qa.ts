/**
 * 智能问答API接口
 */
import request from './request'

/**
 * 对话历史消息
 */
export interface HistoryMessage {
  role: 'user' | 'assistant'
  content: string
}

/**
 * 智能问答请求参数
 */
export interface QARequest {
  question: string
  conversation_id: number  // 会话ID（必填）
  top_k?: number
  history?: HistoryMessage[]  // 对话历史（最近N轮）
}

/**
 * 植物病害图片信息
 */
export interface DiseaseImage {
  bucket: string
  objectKey: string
  url: string
}

/**
 * 植物病害基础信息匹配结果
 */
export interface DiseaseInfoMatch {
  id: number
  disease_code: string
  disease_name: string
  disease_name_en?: string
  pathogen_type?: string
  severity_level?: string
  affected_plants?: string[]
  distribution_area?: string[]
  occurrence_season?: string
  symptoms?: string
  prevention_methods?: string
  economic_loss?: number
  description?: string
  image_bucket?: string
  image_object_key?: string
  imageUrl?: string
  create_time?: string
  update_time?: string
}

/**
 * 植物病害案例匹配结果
 */
export interface DiseaseCaseMatch {
  id: number
  disease_id: number
  disease_name?: string
  disease_code?: string
  case_title: string
  case_date?: string
  location?: string
  plant_type?: string
  infection_area?: number
  severity_level?: string
  description?: string
  economic_loss?: number
  treatment_method?: string
  treatment_result?: string
  data_source?: string
  images?: DiseaseImage[]
  imageUrls?: DiseaseImage[]
  create_time?: string
  update_time?: string
}

export interface QAResponse {
  question: string
  answer: string
  related_entities: RelatedEntity[]  // 相关知识图谱实体
  graph_context?: string  // 知识图谱三元组上下文
  image_url?: string  // 图片URL（如果有上传图片）
  disease_info_matches?: DiseaseInfoMatch[]
  disease_case_matches?: DiseaseCaseMatch[]
  disease_info_context?: string
  disease_case_context?: string
  keywords?: string[]
}

/**
 * 知识图谱实体
 */
export interface RelatedEntity {
  name: string
  type: string
  properties?: any
}

/**
 * 会话信息
 */
export interface Conversation {
  id: number
  title: string
  user_id: number
  user_name: string
  create_time: string
  update_time: string
  message_count: number
}

/**
 * 会话列表响应
 */
export interface ConversationListResponse {
  list: Conversation[]
  total: number
}

/**
 * 会话消息
 */
export interface ConversationMessage {
  id: number
  conversation_id: number
  question: string
  answer: string
  related_entities: RelatedEntity[]  // 相关知识图谱实体
  graph_context?: string  // 知识图谱三元组上下文
  image_url?: string  // 图片URL（如果有上传图片）
  disease_info_matches?: DiseaseInfoMatch[]
  disease_case_matches?: DiseaseCaseMatch[]
  disease_info_context?: string
  disease_case_context?: string
  keywords?: string[]
  create_time: string
}

/**
 * 会话消息列表响应
 */
export interface ConversationMessageListResponse {
  list: ConversationMessage[]
  total: number
}

/**
 * 提交问题并获取答案（支持图片上传）
 */
export function askQuestion(data: QARequest, image?: File) {
  if (image) {
    // 如果有图片，使用 FormData
    const formData = new FormData()
    formData.append('question', data.question)
    formData.append('conversation_id', String(data.conversation_id))
    if (data.top_k) {
      formData.append('top_k', String(data.top_k))
    }
    if (data.history) {
      formData.append('history', JSON.stringify(data.history))
    }
    formData.append('image', image)

    return request.post<QAResponse>('/qa/ask', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  } else {
    // 纯文本问答，使用 JSON
    return request.post<QAResponse>('/qa/ask', data)
  }
}

/**
 * 获取会话列表（当前用户）
 */
export function getConversationList() {
  return request.get<ConversationListResponse>('/qa/conversation/list')
}

/**
 * 获取所有用户的会话列表（仅管理员）
 */
export function getAllConversations() {
  return request.get<ConversationListResponse>('/qa/conversation/all')
}

/**
 * 创建新会话
 */
export function createConversation(title?: string) {
  return request.post<{ conversation_id: number }>('/qa/conversation/create', { title })
}

/**
 * 删除会话
 */
export function deleteConversation(conversationId: number) {
  return request.delete(`/qa/conversation/${conversationId}`)
}

/**
 * 重命名会话
 */
export function renameConversation(conversationId: number, title: string) {
  return request.put(`/qa/conversation/${conversationId}/rename`, { title })
}

/**
 * 获取会话消息列表
 */
export function getConversationMessages(conversationId: number) {
  return request.get<ConversationMessageListResponse>(`/qa/conversation/${conversationId}/messages`)
}

/**
 * 清除会话的所有消息记录
 */
export function clearConversationMessages(conversationId: number) {
  return request.delete(`/qa/conversation/${conversationId}/messages`)
}

/**
 * 根据会话聊天记录自动生成标题
 */
export function generateConversationTitle(conversationId: number) {
  return request.post<{ title: string }>(`/qa/conversation/${conversationId}/generate-title`)
}
