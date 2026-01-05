# MD5: c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6
"""
Copyright© 2025 羊羊小栈(GJQ)
Author: 羊羊小栈 | Time: 2025-10-13 14:30:00

原创作品 - 禁止二次销售!!系统视频、文档禁止二次发布！
违规者需立即停止侵权并按【羊羊小栈系统版权声明及保护条款】赔偿，承担法律责任。
"""

"""
知识图谱管理路由
"""
from flask import Blueprint, request
from algo.knowledge_graph.data_sync import disease_data_sync_service
from algo.knowledge_graph.graph_retriever import graph_retriever
from algo.knowledge_graph.task_manager import task_manager
from algo.knowledge_graph.config import NODE_NAMES, RELATIONSHIP_NAMES, NODE_TYPES, RELATIONSHIP_TYPES, NODE_COLORS, NEO4J_BROWSER_URL
from utils.response import success, error
from utils.jwt_util import token_required

kg_bp = Blueprint('knowledge_graph', __name__, url_prefix='/api/knowledge-graph')

@kg_bp.route('/build-incremental', methods=['POST'])
@token_required
def build_incremental():
    """
    增量构建知识图谱（异步）

    请求体：
    {
        "document_ids": [1, 2, 3]  // 可选，指定要构建的文档ID列表
                                   // 如果不传，则构建所有 is_graph_built=0 的文档
    }

    返回：
    {
        "task_id": "uuid"  // 任务ID，用于查询进度
    }
    """
    try:
        data = request.get_json() or {}
        document_ids = data.get('document_ids')

        # 创建任务
        task_id = task_manager.create_task('incremental')

        # 在后台线程中执行增量构建
        task_manager.run_async_task(
            task_id,
            disease_data_sync_service.build_graph_incremental,
            document_ids=document_ids
        )

        return success({'task_id': task_id}, '任务已启动，正在后台执行')

    except Exception as e:
        return error(f'启动增量构建失败: {str(e)}')

@kg_bp.route('/rebuild-full', methods=['POST'])
@token_required
def rebuild_full():
    """
    全量重建知识图谱（异步）

    清空图谱并重新构建所有文档的知识图谱
    无需请求参数

    返回：
    {
        "task_id": "uuid"  // 任务ID，用于查询进度
    }
    """
    try:
        # 创建任务
        task_id = task_manager.create_task('full')

        # 在后台线程中执行全量重建
        task_manager.run_async_task(
            task_id,
            disease_data_sync_service.rebuild_graph_full
        )

        return success({'task_id': task_id}, '任务已启动，正在后台执行')

    except Exception as e:
        return error(f'启动全量重建失败: {str(e)}')

@kg_bp.route('/build-status/<task_id>', methods=['GET'])
@token_required
def get_build_status(task_id):
    """
    查询构建任务状态和进度

    返回：
    {
        "task_id": "uuid",
        "task_type": "incremental" | "full",
        "status": "pending" | "running" | "completed" | "failed",
        "progress": 0-100,
        "current_step": "当前步骤描述",
        "total_documents": 10,
        "processed_documents": 5,
        "current_document": "当前处理的文档名",
        "result": {...},  // 完成后的结果
        "error": "错误信息"  // 失败时的错误
    }
    """
    try:
        task = task_manager.get_task(task_id)

        if not task:
            return error('任务不存在')

        return success(task.to_dict(), '获取任务状态成功')

    except Exception as e:
        return error(f'查询任务状态失败: {str(e)}')

@kg_bp.route('/statistics', methods=['GET'])
@token_required
def get_statistics():
    """获取知识图谱统计信息"""
    try:
        result = disease_data_sync_service.get_graph_statistics()

        if result.get('success'):
            return success(result.get('statistics'), '获取统计信息成功')
        else:
            return error(result.get('message'))

    except Exception as e:
        return error(f'获取统计失败: {str(e)}')

@kg_bp.route('/search', methods=['POST'])
@token_required
def search_graph():
    """
    在知识图谱中搜索实体

    请求体：
    {
        "keywords": ["稻瘟病", "小麦条锈病"],
        "limit": 20
    }
    """
    try:
        data = request.get_json()
        keywords = data.get('keywords', [])
        limit = data.get('limit', 20)

        if not keywords:
            return error('关键词不能为空')

        result = disease_data_sync_service.search_in_graph(keywords, limit)

        if result.get('success'):
            return success(result.get('results'), f'找到 {result.get("count", 0)} 个相关实体')
        else:
            return error(result.get('message'))

    except Exception as e:
        return error(f'搜索失败: {str(e)}')

@kg_bp.route('/entity/<entity_name>', methods=['GET'])
@token_required
def get_entity_detail(entity_name):
    """
    获取实体详情及其邻居

    参数：
    - entity_name: 实体名称
    - entity_type: 实体类型（可选）
    - depth: 搜索深度（可选，默认1）
    """
    try:
        entity_type = request.args.get('entity_type')
        depth = int(request.args.get('depth', 1))

        result = disease_data_sync_service.get_entity_detail(
            entity_name=entity_name,
            entity_type=entity_type,
            depth=depth
        )

        if result.get('success'):
            return success(result.get('data'), '获取实体详情成功')
        else:
            return error(result.get('message'))

    except Exception as e:
        return error(f'获取实体详情失败: {str(e)}')

@kg_bp.route('/path', methods=['POST'])
@token_required
def find_entity_path():
    """
    查找两个实体之间的关系路径

    请求体：
    {
        "start_entity": "稻瘟病",
        "end_entity": "水稻",
        "max_depth": 3
    }
    """
    try:
        data = request.get_json()
        start_entity = data.get('start_entity')
        end_entity = data.get('end_entity')
        max_depth = data.get('max_depth', 3)

        if not start_entity or not end_entity:
            return error('起始实体和目标实体不能为空')

        result = graph_retriever.find_path_between_entities(
            start_entity=start_entity,
            end_entity=end_entity,
            max_depth=max_depth
        )

        if result.get('success'):
            return success(result.get('paths'), f'找到 {result.get("count", 0)} 条路径')
        else:
            return error(result.get('message'))

    except Exception as e:
        return error(f'查找路径失败: {str(e)}')

@kg_bp.route('/related/<entity_name>', methods=['GET'])
@token_required
def get_related_entities(entity_name):
    """
    获取与指定实体相关的其他实体

    参数：
    - entity_name: 实体名称
    - entity_type: 实体类型（可选）
    - depth: 搜索深度（可选，默认2）
    """
    try:
        entity_type = request.args.get('entity_type')
        depth = int(request.args.get('depth', 2))

        result = graph_retriever.find_related_entities(
            entity_name=entity_name,
            entity_type=entity_type,
            depth=depth
        )

        if result.get('success'):
            return success(result.get('data'), '获取相关实体成功')
        else:
            return error(result.get('message'))

    except Exception as e:
        return error(f'获取相关实体失败: {str(e)}')

@kg_bp.route('/visualization', methods=['GET'])
@token_required
def get_visualization_data():
    """
    获取图谱可视化数据

    参数：
    - limit: 节点数量限制（可选，默认100）
    """
    try:
        limit = int(request.args.get('limit', 100))

        result = disease_data_sync_service.get_graph_visualization_data(limit=limit)

        if result.get('success'):
            return success(result.get('data'), '获取可视化数据成功')
        else:
            return error(result.get('message'))

    except Exception as e:
        return error(f'获取可视化数据失败: {str(e)}')

@kg_bp.route('/clear', methods=['POST'])
@token_required
def clear_graph():
    """
    清空知识图谱
    """
    try:
        result = disease_data_sync_service.clear_graph()

        if result.get('success'):
            return success(None, '图谱已清空')
        else:
            return error(result.get('message'))

    except Exception as e:
        return error(f'清空图谱失败: {str(e)}')

@kg_bp.route('/config', methods=['GET'])
@token_required
def get_graph_config():
    """
    获取知识图谱配置（节点类型和关系类型的中文映射、节点颜色、Neo4j Browser URL）
    """
    try:
        config_data = {
            'nodeTypes': NODE_TYPES,
            'relationshipTypes': RELATIONSHIP_TYPES,
            'nodeNames': NODE_NAMES,
            'relationshipNames': RELATIONSHIP_NAMES,
            'nodeColors': NODE_COLORS,
            'neo4jBrowserUrl': NEO4J_BROWSER_URL
        }
        return success(config_data, '获取配置成功')
    except Exception as e:
        return error(f'获取配置失败: {str(e)}')
