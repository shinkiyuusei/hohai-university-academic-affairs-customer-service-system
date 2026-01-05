"""
植物病害文档数据同步服务 - 从文档提取三元组并同步到Neo4j
"""
import logging
from typing import List, Dict, Any, Callable, Optional
from utils.db import db
from algo.knowledge_graph.neo4j_client import neo4j_client
from algo.knowledge_graph.triplet_extractor import create_triplet_extractor
from algo.knowledge_graph.task_manager import task_manager

logger = logging.getLogger(__name__)

class DiseaseDataSyncService:
    """植物病害数据同步服务"""

    def __init__(self):
        self.db = db
        self.neo4j_client = neo4j_client
        self.triplet_extractor = None

    def init_triplet_extractor(self, model_name: str = None):
        """
        初始化三元组提取器

        Args:
            model_name: 模型名称，如果为None则使用默认模型
        """
        self.triplet_extractor = create_triplet_extractor(model_name)
        if self.triplet_extractor:
            logger.info("三元组提取器初始化成功")
        else:
            logger.warning("三元组提取器初始化失败")

    def build_graph_incremental(self, task_id: str = None, document_ids: List[int] = None) -> Dict[str, Any]:
        """
        增量构建知识图谱（支持异步执行和进度跟踪）

        Args:
            task_id: 任务ID（用于进度跟踪，可选）
            document_ids: 要构建的文档ID列表（可选）
                         - 如果传入ID列表，则只构建指定的文档
                         - 如果为None，则构建所有 is_graph_built=0 的文档

        Returns:
            构建结果统计
        """
        def update_progress(progress: int, step: str, total_docs: int = None, processed: int = None, current: str = None):
            """更新进度（如果有task_id）"""
            if task_id:
                task_manager.update_task_progress(task_id, progress, step, total_docs, processed, current)

        try:
            update_progress(0, "初始化连接...")

            if not self.neo4j_client:
                return {
                    "success": False,
                    "message": "Neo4j未连接，请检查配置"
                }

            # 如果提取器未初始化，尝试用默认配置初始化
            if not self.triplet_extractor:
                self.init_triplet_extractor()
                if not self.triplet_extractor:
                    return {
                        "success": False,
                        "message": "三元组提取器未初始化，请检查LLM配置"
                    }

            logger.info("开始增量构建知识图谱")
            update_progress(5, "创建约束和索引...")

            # 创建约束和索引
            self.neo4j_client.create_constraints()

            update_progress(10, "查询待构建文档...")

            # 获取要构建的文档
            if document_ids:
                # 获取指定ID的文档
                placeholders = ",".join(["?" for _ in document_ids])
                query = f"SELECT id, title, content FROM document WHERE id IN ({placeholders})"
                documents = self.db.query(query, document_ids)
                documents = [dict(doc) for doc in documents]
                logger.info(f"获取到 {len(documents)} 个指定文档")
            else:
                # 获取所有未构建的文档
                query = "SELECT id, title, content FROM document WHERE is_graph_built = 0"
                documents = self.db.query(query)
                documents = [dict(doc) for doc in documents]
                logger.info(f"找到 {len(documents)} 个未构建的文档")

            if not documents:
                update_progress(100, "完成！没有需要构建的文档")
                return {
                    "success": True,
                    "message": "没有找到需要构建的文档",
                    "documents_processed": 0,
                    "documents_success": 0,
                    "documents_failed": 0,
                    "triplets_extracted": 0,
                    "nodes_created": 0,
                    "relationships_created": 0
                }

            total_docs = len(documents)
            update_progress(15, f"开始提取三元组（共{total_docs}个文档）...", total_docs=total_docs, processed=0)

            # 提取三元组
            all_triplets = []
            success_count = 0
            fail_count = 0
            processed_doc_ids = []  # 记录成功处理的文档ID

            for i, doc in enumerate(documents):
                try:
                    doc_id = doc.get("id")
                    doc_title = doc.get("title")
                    doc_content = doc.get("content", "")

                    # 计算进度：15%-75% 用于文档处理
                    progress = 15 + int((i / total_docs) * 60)
                    update_progress(progress, f"正在处理: {doc_title}", processed=i, current=doc_title)

                    if not doc_content or len(doc_content.strip()) < 10:
                        logger.warning(f"文档 {doc_id} 内容为空或过短，跳过")
                        fail_count += 1
                        continue

                    logger.info(f"处理文档 {i+1}/{total_docs}: {doc_title}")

                    # 提取三元组
                    triplets = self.triplet_extractor.extract_triplets(
                        document_content=doc_content,
                        document_id=doc_id,
                        document_title=doc_title
                    )

                    if triplets:
                        all_triplets.extend(triplets)
                        success_count += 1
                        processed_doc_ids.append(doc_id)  # 记录成功处理的文档
                        logger.info(f"文档 {doc_title} 提取了 {len(triplets)} 个三元组")
                    else:
                        fail_count += 1
                        logger.warning(f"文档 {doc_title} 未提取到三元组")

                except Exception as e:
                    logger.error(f"处理文档 {doc.get('id')} 失败: {str(e)}")
                    fail_count += 1

            update_progress(75, f"提取完成，共{len(all_triplets)}个三元组", processed=total_docs)

            # 批量创建三元组到Neo4j
            if all_triplets:
                update_progress(80, f"同步{len(all_triplets)}个三元组到Neo4j...")
                logger.info(f"开始将 {len(all_triplets)} 个三元组同步到Neo4j")
                create_stats = self.neo4j_client.create_triplets(all_triplets)
                logger.info(f"同步完成: {create_stats}")
            else:
                create_stats = {"nodes_created": 0, "relationships_created": 0}

            update_progress(90, "更新文档构建标志...")

            # 更新成功处理的文档的 is_graph_built 标志
            if processed_doc_ids:
                placeholders = ",".join(["?" for _ in processed_doc_ids])
                update_sql = f"UPDATE document SET is_graph_built = 1 WHERE id IN ({placeholders})"
                self.db.execute(update_sql, processed_doc_ids)
                logger.info(f"已更新 {len(processed_doc_ids)} 个文档的图谱构建标志")

            update_progress(95, "获取统计信息...")

            # 获取统计信息
            graph_stats = self.neo4j_client.get_statistics()

            result = {
                "success": True,
                "message": f"增量构建完成！成功: {success_count}, 失败: {fail_count}",
                "documents_processed": total_docs,
                "documents_success": success_count,
                "documents_failed": fail_count,
                "triplets_extracted": len(all_triplets),
                "nodes_created": create_stats.get("nodes_created", 0),
                "relationships_created": create_stats.get("relationships_created", 0),
                "graph_statistics": graph_stats
            }

            update_progress(100, "增量构建完成！")
            logger.info(f"增量构建结果: {result}")
            return result

        except Exception as e:
            logger.error(f"增量构建失败: {str(e)}")
            if task_id:
                task_manager.fail_task(task_id, str(e))
            return {
                "success": False,
                "message": f"增量构建失败: {str(e)}"
            }

    def rebuild_graph_full(self, task_id: str = None) -> Dict[str, Any]:
        """
        全量重建知识图谱（支持异步执行和进度跟踪）

        清空图谱并重新构建所有文档的知识图谱

        Args:
            task_id: 任务ID（用于进度跟踪，可选）

        Returns:
            构建结果统计
        """
        def update_progress(progress: int, step: str, total_docs: int = None, processed: int = None, current: str = None):
            """更新进度（如果有task_id）"""
            if task_id:
                task_manager.update_task_progress(task_id, progress, step, total_docs, processed, current)

        try:
            update_progress(0, "初始化连接...")

            if not self.neo4j_client:
                return {
                    "success": False,
                    "message": "Neo4j未连接，请检查配置"
                }

            # 如果提取器未初始化，尝试用默认配置初始化
            if not self.triplet_extractor:
                self.init_triplet_extractor()
                if not self.triplet_extractor:
                    return {
                        "success": False,
                        "message": "三元组提取器未初始化，请检查LLM配置"
                    }

            logger.info("开始全量重建知识图谱")
            update_progress(5, "清空图数据库...")

            # 清空图数据库
            self.neo4j_client.clear_database()
            logger.info("图数据库已清空")

            update_progress(10, "创建约束和索引...")

            # 创建约束和索引
            self.neo4j_client.create_constraints()

            update_progress(15, "查询所有文档...")

            # 获取所有文档
            query = "SELECT id, title, content FROM document"
            documents = self.db.query(query)
            documents = [dict(doc) for doc in documents]

            if not documents:
                update_progress(100, "完成！没有找到任何文档")
                return {
                    "success": True,
                    "message": "没有找到任何文档",
                    "documents_processed": 0,
                    "documents_success": 0,
                    "documents_failed": 0,
                    "triplets_extracted": 0,
                    "nodes_created": 0,
                    "relationships_created": 0
                }

            total_docs = len(documents)
            logger.info(f"找到 {total_docs} 个文档待重建")
            update_progress(20, f"开始提取三元组（共{total_docs}个文档）...", total_docs=total_docs, processed=0)

            # 提取三元组
            all_triplets = []
            success_count = 0
            fail_count = 0
            processed_doc_ids = []  # 记录成功处理的文档ID

            for i, doc in enumerate(documents):
                try:
                    doc_id = doc.get("id")
                    doc_title = doc.get("title")
                    doc_content = doc.get("content", "")

                    # 计算进度：20%-75% 用于文档处理
                    progress = 20 + int((i / total_docs) * 55)
                    update_progress(progress, f"正在处理: {doc_title}", processed=i, current=doc_title)

                    if not doc_content or len(doc_content.strip()) < 10:
                        logger.warning(f"文档 {doc_id} 内容为空或过短，跳过")
                        fail_count += 1
                        continue

                    logger.info(f"处理文档 {i+1}/{total_docs}: {doc_title}")

                    # 提取三元组
                    triplets = self.triplet_extractor.extract_triplets(
                        document_content=doc_content,
                        document_id=doc_id,
                        document_title=doc_title
                    )

                    if triplets:
                        all_triplets.extend(triplets)
                        success_count += 1
                        processed_doc_ids.append(doc_id)  # 记录成功处理的文档
                        logger.info(f"文档 {doc_title} 提取了 {len(triplets)} 个三元组")
                    else:
                        fail_count += 1
                        logger.warning(f"文档 {doc_title} 未提取到三元组")

                except Exception as e:
                    logger.error(f"处理文档 {doc.get('id')} 失败: {str(e)}")
                    fail_count += 1

            update_progress(75, f"提取完成，共{len(all_triplets)}个三元组", processed=total_docs)

            # 批量创建三元组到Neo4j
            if all_triplets:
                update_progress(80, f"同步{len(all_triplets)}个三元组到Neo4j...")
                logger.info(f"开始将 {len(all_triplets)} 个三元组同步到Neo4j")
                create_stats = self.neo4j_client.create_triplets(all_triplets)
                logger.info(f"同步完成: {create_stats}")
            else:
                create_stats = {"nodes_created": 0, "relationships_created": 0}

            update_progress(90, "更新文档构建标志...")

            # 更新成功处理的文档的 is_graph_built 标志
            if processed_doc_ids:
                placeholders = ",".join(["?" for _ in processed_doc_ids])
                update_sql = f"UPDATE document SET is_graph_built = 1 WHERE id IN ({placeholders})"
                self.db.execute(update_sql, processed_doc_ids)
                logger.info(f"已更新 {len(processed_doc_ids)} 个文档的图谱构建标志")

            update_progress(95, "获取统计信息...")

            # 获取统计信息
            graph_stats = self.neo4j_client.get_statistics()

            result = {
                "success": True,
                "message": f"全量重建完成！成功: {success_count}, 失败: {fail_count}",
                "documents_processed": total_docs,
                "documents_success": success_count,
                "documents_failed": fail_count,
                "triplets_extracted": len(all_triplets),
                "nodes_created": create_stats.get("nodes_created", 0),
                "relationships_created": create_stats.get("relationships_created", 0),
                "graph_statistics": graph_stats
            }

            update_progress(100, "全量重建完成！")
            logger.info(f"全量重建结果: {result}")
            return result

        except Exception as e:
            logger.error(f"全量重建失败: {str(e)}")
            if task_id:
                task_manager.fail_task(task_id, str(e))
            return {
                "success": False,
                "message": f"全量重建失败: {str(e)}"
            }

    def get_graph_statistics(self) -> Dict[str, Any]:
        """
        获取图数据库统计信息

        Returns:
            统计信息
        """
        try:
            if not self.neo4j_client:
                return {
                    "success": False,
                    "message": "Neo4j未连接"
                }

            stats = self.neo4j_client.get_statistics()
            return {
                "success": True,
                "statistics": stats
            }

        except Exception as e:
            logger.error(f"获取统计信息失败: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }

    def search_in_graph(self, keywords: List[str], limit: int = 20) -> Dict[str, Any]:
        """
        在知识图谱中搜索

        Args:
            keywords: 搜索关键词列表
            limit: 返回结果数量限制

        Returns:
            搜索结果
        """
        try:
            if not self.neo4j_client:
                return {
                    "success": False,
                    "message": "Neo4j未连接"
                }

            results = self.neo4j_client.search_entities(keywords, limit)
            return {
                "success": True,
                "results": results,
                "count": len(results)
            }

        except Exception as e:
            logger.error(f"图谱搜索失败: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }

    def get_entity_detail(self, entity_name: str, entity_type: str = None, depth: int = 1) -> Dict[str, Any]:
        """
        获取实体详情及其邻居

        Args:
            entity_name: 实体名称
            entity_type: 实体类型
            depth: 搜索深度

        Returns:
            实体详情
        """
        try:
            if not self.neo4j_client:
                return {
                    "success": False,
                    "message": "Neo4j未连接"
                }

            graph_data = self.neo4j_client.get_entity_neighbors(entity_name, entity_type, depth)
            return {
                "success": True,
                "data": graph_data
            }

        except Exception as e:
            logger.error(f"获取实体详情失败: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }

    def get_graph_visualization_data(self, limit: int = 100) -> Dict[str, Any]:
        """
        获取图谱可视化数据

        Args:
            limit: 节点数量限制

        Returns:
            可视化数据，包含节点和关系
        """
        try:
            if not self.neo4j_client:
                return {
                    "success": False,
                    "message": "Neo4j未连接"
                }

            # 获取所有节点（限制数量）
            nodes_query = f"""
            MATCH (n)
            RETURN id(n) as id, 
                   n.name as name,
                   labels(n)[0] as type, 
                   properties(n) as properties
            LIMIT {limit}
            """

            nodes_result = self.neo4j_client.execute_query(nodes_query)
            
            # 在Python端处理课程节点中文名称提取
            for node in nodes_result:
                if node['type'] == 'Course' and node['name'] and node['name'].isdigit() and len(node['name']) >= 6:
                    # 从description中提取中文课程名称
                    description = node['properties'].get('description', '')
                    if '《' in description and '》' in description:
                        start_pos = description.find('《') + 1
                        end_pos = description.find('》')
                        if start_pos < end_pos:
                            node['name'] = description[start_pos:end_pos]

            # 提取节点ID列表
            node_ids = [node['id'] for node in nodes_result] if nodes_result else []

            # 获取所有关系（只获取在节点限制范围内的关系）
            if node_ids:
                relationships_query = """
                MATCH (a)-[r]->(b)
                WHERE id(a) IN $nodeIds AND id(b) IN $nodeIds
                RETURN DISTINCT id(a) as source, id(b) as target, type(r) as type, properties(r) as properties
                """

                relationships_result = self.neo4j_client.execute_query(relationships_query, {'nodeIds': node_ids})
            else:
                relationships_result = []

            # 转换节点数据
            nodes = nodes_result if nodes_result else []

            # 转换关系数据（使用Cypher中的DISTINCT已经去重）
            relationships = relationships_result if relationships_result else []

            # 调试日志
            logger.info(f"=== 调试：数据库查询结果 ===")
            logger.info(f"查询到的节点数: {len(nodes)}")
            logger.info(f"查询到的关系数: {len(relationships)}")

            # 输出前3条关系作为样例
            if relationships:
                logger.info(f"关系样例（前3条）:")
                for i, rel in enumerate(relationships[:3]):
                    logger.info(f"  关系{i+1}: source={rel.get('source')}, target={rel.get('target')}, type={rel.get('type')}")

            # 检查是否有空值关系
            none_rels = [r for r in relationships if not r or r.get('source') is None or r.get('target') is None]
            if none_rels:
                logger.warning(f"发现 {len(none_rels)} 条空值关系，将被过滤")

            # 统计关系类型分布
            rel_type_count = {}
            for rel in relationships:
                if rel and rel.get('type'):
                    rel_type = rel.get('type')
                    rel_type_count[rel_type] = rel_type_count.get(rel_type, 0) + 1
            logger.info(f"关系类型分布: {rel_type_count}")

            # 统计每个节点的度
            degree_map = {}
            for rel in relationships:
                if rel and rel.get('source') is not None and rel.get('target') is not None:
                    source = rel['source']
                    target = rel['target']
                    degree_map[source] = degree_map.get(source, 0) + 1
                    degree_map[target] = degree_map.get(target, 0) + 1

            logger.info(f"度数统计 degree_map 大小: {len(degree_map)}")

            # 查找包含"病害"的节点并输出度数
            disease_nodes = [n for n in nodes if n and n.get('name') and '病害' in n.get('name')]
            if disease_nodes:
                logger.info(f"找到病害节点:")
                for node in disease_nodes:
                    node_id = node.get('id')
                    degree = degree_map.get(node_id, 0)
                    logger.info(f"  - {node.get('name')}: id={node_id}, degree={degree}")

            # 添加度信息到节点
            for node in nodes:
                if node:
                    node_id = node.get('id')
                    node['degree'] = degree_map.get(node_id, 0)

            return {
                "success": True,
                "data": {
                    "nodes": nodes,
                    "relationships": [r for r in relationships if r]  # 过滤掉None值
                }
            }

        except Exception as e:
            logger.error(f"获取可视化数据失败: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }

    def clear_graph(self) -> Dict[str, Any]:
        """
        清空知识图谱

        清空Neo4j图数据库，并重置所有文档的 is_graph_built 标志为 0

        Returns:
            操作结果
        """
        try:
            if not self.neo4j_client:
                return {
                    "success": False,
                    "message": "Neo4j未连接"
                }

            logger.info("开始清空知识图谱")

            # 清空Neo4j图数据库
            self.neo4j_client.clear_database()
            logger.info("Neo4j图数据库已清空")

            # 重置所有文档的 is_graph_built 标志
            self.db.execute("UPDATE document SET is_graph_built = 0")
            logger.info("已重置所有文档的图谱构建标志")

            return {
                "success": True,
                "message": "图谱已清空，所有文档标志已重置"
            }

        except Exception as e:
            logger.error(f"清空图谱失败: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }


# 创建全局实例
disease_data_sync_service = DiseaseDataSyncService()
