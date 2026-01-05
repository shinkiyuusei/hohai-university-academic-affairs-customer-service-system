
/**
 * 知识图谱相关API
 */
import request from './request'

/**
 * 获取知识图谱统计信息
 */
export function getGraphStatistics() {
  return request.get('/knowledge-graph/statistics')
}

/**
 * 增量构建知识图谱（异步）
 * @param document_ids 文档ID列表（可选）
 *                     - 如果传入ID列表，则只构建指定的文档
 *                     - 如果不传，则构建所有 is_graph_built=0 的文档
 * @returns { task_id: string } 任务ID，用于查询进度
 */
export function buildGraphIncremental(data?: {
  document_ids?: number[]
}) {
  return request.post('/knowledge-graph/build-incremental', data || {})
}

/**
 * 全量重建知识图谱（异步）
 *
 * 清空图谱并重新构建所有文档的知识图谱
 * 无需参数
 * @returns { task_id: string } 任务ID，用于查询进度
 */
export function rebuildGraphFull() {
  return request.post('/knowledge-graph/rebuild-full')
}

/**
 * 查询构建任务状态和进度
 * @param taskId 任务ID
 */
export function getBuildStatus(taskId: string) {
  return request.get(`/knowledge-graph/build-status/${taskId}`)
}

/**
 * 在知识图谱中搜索实体
 * @param keywords 搜索关键词列表
 * @param limit 返回结果数量限制
 */
export function searchGraphEntities(data: {
  keywords: string[]
  limit?: number
}) {
  return request.post('/knowledge-graph/search', data)
}

/**
 * 获取实体详情
 * @param entityName 实体名称
 * @param entityType 实体类型（可选）
 * @param depth 搜索深度（可选）
 */
export function getEntityDetail(
  entityName: string,
  params?: {
    entity_type?: string
    depth?: number
  }
) {
  return request.get(`/knowledge-graph/entity/${entityName}`, { params })
}

/**
 * 查找两个实体之间的关系路径
 * @param startEntity 起始实体
 * @param endEntity 目标实体
 * @param maxDepth 最大搜索深度
 */
export function findEntityPath(data: {
  start_entity: string
  end_entity: string
  max_depth?: number
}) {
  return request.post('/knowledge-graph/path', data)
}

/**
 * 获取与指定实体相关的其他实体
 * @param entityName 实体名称
 * @param entityType 实体类型（可选）
 * @param depth 搜索深度（可选）
 */
export function getRelatedEntities(
  entityName: string,
  params?: {
    entity_type?: string
    depth?: number
  }
) {
  return request.get(`/knowledge-graph/related/${entityName}`, { params })
}

/**
 * 获取图谱可视化数据
 * @param limit 节点数量限制
 */
export function getGraphVisualizationData(params?: {
  limit?: number
}) {
  return request.get('/knowledge-graph/visualization', { params })
}

/**
 * 清空知识图谱
 */
export function clearGraph() {
  return request.post('/knowledge-graph/clear')
}

/**
 * 获取知识图谱配置（节点类型和关系类型的中文映射）
 */
export function getGraphConfig() {
  return request.get('/knowledge-graph/config')
}
