
"""
Neo4j图数据库客户端 - 植物病害知识图谱版本
"""
from neo4j import GraphDatabase
import logging
from typing import List, Dict, Optional, Any
from algo.knowledge_graph.config import (
    NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD,
    NODE_TYPES, RELATIONSHIP_TYPES
)

logger = logging.getLogger(__name__)

class Neo4jClient:
    """Neo4j数据库客户端 - 植物病害领域"""

    def __init__(self, uri: str = NEO4J_URI, user: str = NEO4J_USER, password: str = NEO4J_PASSWORD):
        """
        初始化Neo4j客户端

        Args:
            uri: Neo4j数据库连接地址
            user: 用户名
            password: 密码
        """
        self.driver = None
        max_retries = 5
        retry_delay = 10  # 秒
        
        for attempt in range(max_retries):
            try:
                self.driver = GraphDatabase.driver(uri, auth=(user, password))
                # 测试连接
                self.driver.verify_connectivity()
                logger.info("Neo4j连接成功")
                break
            except Exception as e:
                logger.warning(f"Neo4j连接失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    logger.info(f"等待 {retry_delay} 秒后重试...")
                    import time
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 指数退避
                else:
                    logger.error(f"Neo4j连接最终失败: {str(e)}")
                    raise

    def close(self):
        """关闭数据库连接"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j连接已关闭")

    def execute_query(self, query: str, parameters: Optional[Dict] = None) -> List[Dict]:
        """
        执行Cypher查询

        Args:
            query: Cypher查询语句
            parameters: 查询参数

        Returns:
            查询结果列表
        """
        try:
            with self.driver.session() as session:
                # 记录查询信息（简化版，避免记录敏感信息）
                query_type = query.strip().split()[0].upper() if query.strip() else "UNKNOWN"
                logger.debug(f"[Neo4j查询] 类型: {query_type}, 参数: {parameters}")
                
                result = session.run(query, parameters or {})
                data = [record.data() for record in result]
                
                logger.debug(f"[Neo4j查询] 返回 {len(data)} 条记录")
                return data
        except Exception as e:
            logger.error(f"[Neo4j查询错误] 查询类型: {query.strip().split()[0].upper() if query.strip() else 'UNKNOWN'}, 错误: {str(e)}")
            raise

    def clear_database(self):
        """清空数据库"""
        query = "MATCH (n) DETACH DELETE n"
        self.execute_query(query)
        logger.info("图数据库已清空")

    def create_constraints(self):
        """创建约束和索引"""
        constraints = []

        # 为每种节点类型创建唯一性约束和索引
        for node_type in NODE_TYPES:
            # 唯一性约束（基于name属性）
            constraint_query = f"CREATE CONSTRAINT {node_type.lower()}_name IF NOT EXISTS FOR (n:{node_type}) REQUIRE n.name IS UNIQUE"
            constraints.append(constraint_query)

            # 名称索引
            index_query = f"CREATE INDEX {node_type.lower()}_name_idx IF NOT EXISTS FOR (n:{node_type}) ON (n.name)"
            constraints.append(index_query)

        for constraint in constraints:
            try:
                self.execute_query(constraint)
            except Exception as e:
                logger.debug(f"约束创建跳过（可能已存在）: {e}")

        logger.info("约束和索引创建完成")

    def create_triplets(self, triplets: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        批量创建三元组（节点和关系）

        Args:
            triplets: 三元组列表，格式:
                [{
                    "head": "实体名称",
                    "head_type": "节点类型",
                    "relation": "关系类型",
                    "tail": "实体名称",
                    "tail_type": "节点类型",
                    "properties": {
                        "head_description": "头实体描述",
                        "tail_description": "尾实体描述"
                    }
                }, ...]

        Returns:
            统计信息
        """
        if not triplets:
            return {"nodes_created": 0, "relationships_created": 0}

        nodes_created = 0
        relationships_created = 0

        for triplet in triplets:
            try:
                head_name = triplet.get("head")
                head_type = triplet.get("head_type")
                relation = triplet.get("relation")
                tail_name = triplet.get("tail")
                tail_type = triplet.get("tail_type")
                properties = triplet.get("properties", {})

                # 验证节点类型和关系类型
                if head_type not in NODE_TYPES or tail_type not in NODE_TYPES:
                    logger.warning(f"跳过无效节点类型: {head_type} -> {tail_type}")
                    continue

                if relation not in RELATIONSHIP_TYPES:
                    logger.warning(f"跳过无效关系类型: {relation}")
                    continue

                # 提取头实体和尾实体的 description
                head_description = properties.get("head_description", "")
                tail_description = properties.get("tail_description", "")

                # 创建头节点（添加 description）
                head_props = {"name": head_name}
                if head_description:
                    head_props["description"] = head_description
                self._create_node(head_type, head_props)
                nodes_created += 1

                # 创建尾节点（添加 description）
                tail_props = {"name": tail_name}
                if tail_description:
                    tail_props["description"] = tail_description
                self._create_node(tail_type, tail_props)
                nodes_created += 1

                # 创建关系（不再需要关系属性）
                self._create_relationship(head_name, head_type, relation, tail_name, tail_type, {})
                relationships_created += 1

            except Exception as e:
                logger.error(f"创建三元组失败: {triplet}, 错误: {str(e)}")

        logger.info(f"批量创建完成: 节点 {nodes_created}, 关系 {relationships_created}")
        return {"nodes_created": nodes_created, "relationships_created": relationships_created}

    def _create_node(self, node_type: str, properties: Dict[str, Any]):
        """创建单个节点"""
        node_name = properties.get('name', '未知节点')
        logger.debug(f"[节点创建] 创建节点: {node_type}({node_name})")
        
        # 构建属性字符串
        props_str = ", ".join([f"n.{key} = ${key}" for key in properties.keys()])

        query = f"""
        MERGE (n:{node_type} {{name: $name}})
        SET {props_str}
        """

        self.execute_query(query, properties)

    def _create_relationship(self, head_name: str, head_type: str, relation: str,
                           tail_name: str, tail_type: str, properties: Dict[str, Any]):
        """创建单个关系"""
        logger.debug(f"[关系创建] 创建关系: {head_type}({head_name})-{relation}->{tail_type}({tail_name})")
        
        # 构建属性字符串
        if properties:
            props_str = "{" + ", ".join([f"{key}: ${key}" for key in properties.keys()]) + "}"
        else:
            props_str = ""

        query = f"""
        MATCH (h:{head_type} {{name: $head_name}})
        MATCH (t:{tail_type} {{name: $tail_name}})
        MERGE (h)-[r:{relation} {props_str}]->(t)
        """

        params = {
            "head_name": head_name,
            "tail_name": tail_name,
            **properties
        }

        self.execute_query(query, params)

    def get_statistics(self) -> Dict[str, Any]:
        """获取图数据库统计信息"""
        stats = {}

        # 收集有数据的节点类型和关系类型
        node_types_with_data = []
        relationship_types_with_data = []

        # 节点统计
        for node_type in NODE_TYPES:
            query = f"MATCH (n:{node_type}) RETURN count(n) as count"
            result = self.execute_query(query)
            count = result[0]["count"] if result else 0
            stats[f"{node_type.lower()}_count"] = count
            if count > 0:
                node_types_with_data.append(node_type)

        # 关系统计
        for rel_type in RELATIONSHIP_TYPES:
            query = f"MATCH ()-[r:{rel_type}]->() RETURN count(r) as count"
            result = self.execute_query(query)
            count = result[0]["count"] if result else 0
            stats[f"{rel_type.lower()}_count"] = count
            if count > 0:
                relationship_types_with_data.append(rel_type)

        # 总计
        total_nodes_query = "MATCH (n) RETURN count(n) as count"
        total_rels_query = "MATCH ()-[r]->() RETURN count(r) as count"

        total_nodes = self.execute_query(total_nodes_query)[0]["count"]
        total_relationships = self.execute_query(total_rels_query)[0]["count"]

        # 添加前端需要的字段
        stats["nodeCount"] = total_nodes
        stats["relationshipCount"] = total_relationships
        stats["nodeTypes"] = node_types_with_data
        stats["relationshipTypes"] = relationship_types_with_data

        # 保留原有字段以兼容
        stats["total_nodes"] = total_nodes
        stats["total_relationships"] = total_relationships

        return stats

    def search_entities(self, keywords: List[str], limit: int = 20) -> List[Dict]:
        """
        根据关键词搜索实体

        Args:
            keywords: 搜索关键词列表
            limit: 返回结果数量限制

        Returns:
            匹配的实体列表
        """
        if not keywords:
            logger.info("[实体搜索] 未提供关键词，返回空结果")
            return []

        # 实体类型优先级（数字越小优先级越高）
        type_priority = {
            'Major': 1,
            'Course': 2,
            'AcademicPolicy': 3,
            'Requirement': 4,
            'Procedure': 5,
            'Teacher': 6,
            'Student': 7,
            'Schedule': 8,
            'TimePoint': 9,
            'Document': 10
        }

        # 构建搜索条件
        exact_match_conditions = []
        contains_match_conditions = []
        
        for i, keyword in enumerate(keywords):
            exact_match_conditions.append(f"n.name = $keyword{i}")
            contains_match_conditions.append(f"n.name CONTAINS $keyword{i}")

        # 组合条件：优先精确匹配，然后包含匹配
        match_condition = " OR ".join(exact_match_conditions + contains_match_conditions)

        # 构建实体类型优先级的CASE语句
        type_priority_case = []
        for t, p in type_priority.items():
            type_priority_case.append(f"WHEN labels(n)[0] = '{t}' THEN {p}")
        type_priority_case = '\n                 '.join(type_priority_case)
        
        query = f"""
        MATCH (n)
        WHERE {match_condition}
        WITH n, 
             n.name as name, 
             properties(n) as properties,
             // 计算匹配度得分
             CASE 
                 // 精确匹配得分
                 WHEN {' OR '.join(exact_match_conditions)} THEN 2
                 // 包含匹配得分
                 ELSE 1
             END as match_score,
             // 实体类型优先级得分
             CASE 
                 {type_priority_case}
                 ELSE 99
             END as type_score,
             // 实体连接度数（度数越高越重要）
             SIZE([(n)--() | 1]) as degree_score
        // 根据匹配度、类型优先级和度数排序
        ORDER BY match_score DESC, type_score ASC, degree_score DESC, name
        RETURN labels(n)[0] as type, name, properties
        LIMIT $limit
        """

        parameters = {"limit": limit}
        for i, keyword in enumerate(keywords):
            parameters[f"keyword{i}"] = keyword

        results = self.execute_query(query, parameters)
        logger.info(f"[实体搜索] 关键词: {keywords}, 找到 {len(results)} 个匹配实体")
        if results:
            logger.debug(f"[实体搜索] 前5个实体: {[(r.get('type'), r.get('name')) for r in results[:5]]}")
        return results

    def get_entity_neighbors(self, entity_name: str, entity_type: str = None, depth: int = 1) -> Dict:
        """
        获取实体的邻居节点和关系

        Args:
            entity_name: 实体名称
            entity_type: 实体类型（可选）
            depth: 搜索深度

        Returns:
            包含节点和关系的图数据
        """
        logger.info(f"[实体邻居获取] 获取实体 '{entity_name}'{f'({entity_type})' if entity_type else ''} 的邻居信息，深度: {depth}")
        # 构建类型条件
        type_condition = f":{entity_type}" if entity_type else ""

        query = f"""
        MATCH path = (n{type_condition} {{name: $entity_name}})-[*1..{depth}]-(m)
        WITH n,
             collect(DISTINCT m) as neighbors,
             reduce(rels = [], p in collect(relationships(path)) | rels + p) as all_rels
        UNWIND all_rels as r
        WITH n, neighbors, collect(DISTINCT {{
            type: type(r),
            source: startNode(r).name,
            target: endNode(r).name,
            source_type: labels(startNode(r))[0],
            target_type: labels(endNode(r))[0],
            properties: properties(r)
        }}) as relationships
        RETURN
            [{{type: labels(n)[0], name: n.name, properties: properties(n)}}] +
            [m IN neighbors | {{type: labels(m)[0], name: m.name, properties: properties(m)}}] as nodes,
            relationships
        """

        result = self.execute_query(query, {"entity_name": entity_name})

        if not result:
            logger.info(f"[实体邻居获取] 未找到实体 '{entity_name}'{f'({entity_type})' if entity_type else ''} 的邻居信息")
            return {"nodes": [], "relationships": []}

        nodes = result[0].get("nodes", [])
        relationships = result[0].get("relationships", [])
        logger.info(f"[实体邻居获取] 成功获取实体 '{entity_name}' 的邻居信息：{len(nodes)} 个节点，{len(relationships)} 个关系")
        if nodes:
            logger.debug(f"[实体邻居获取] 邻居节点类型统计：{dict((n['type'], sum(1 for node in nodes if node['type'] == n['type'])) for n in nodes)}")

        return {
            "nodes": nodes,
            "relationships": relationships
        }

    def find_paths(self, start_entity: str, end_entity: str, max_depth: int = 3) -> List[Dict]:
        """
        查找两个实体之间的路径

        Args:
            start_entity: 起始实体名称
            end_entity: 目标实体名称
            max_depth: 最大搜索深度

        Returns:
            路径列表
        """
        query = f"""
        MATCH path = (start {{name: $start_entity}})-[*1..{max_depth}]-(end {{name: $end_entity}})
        WITH path, length(path) as pathLength
        RETURN [node IN nodes(path) | {{type: labels(node)[0], name: node.name}}] as nodes,
               [rel IN relationships(path) | type(rel)] as relationships,
               pathLength
        ORDER BY pathLength
        LIMIT 5
        """

        results = self.execute_query(query, {
            "start_entity": start_entity,
            "end_entity": end_entity
        })

        return results


# 创建全局实例
try:
    neo4j_client = Neo4jClient()
except Exception as e:
    logger.warning(f"无法创建Neo4j全局实例: {str(e)}")
    neo4j_client = None
