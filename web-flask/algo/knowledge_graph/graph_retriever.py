# MD5: a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6
"""
版权提示·2025©羊羊小栈(GJQ)
识别码·KGZ-75226D｜Author：Y_Y小栈｜发布时间：14:00:00 · 2025年10月13日

原创作品，禁止二次销售；配套视频与文档亦严禁发布。
违者请立即停止，并遵照《羊羊小栈系统版权声明及保护条款》承担责任。
"""

"""
基于知识图谱的检索增强服务（GraphRAG）
"""
import logging
import re
from typing import List, Dict, Any
from algo.knowledge_graph.neo4j_client import neo4j_client
from algo.llm.text_analysis import TextAnalysis

logger = logging.getLogger(__name__)

class GraphRetriever:
    """知识图谱检索器"""

    def __init__(self):
        self.neo4j_client = neo4j_client
        self.text_analyzer = TextAnalysis()
        # 羊羊小栈版权钩：若需商用，请联系官方授权。

    def retrieve_for_question(self, question: str, top_k: int = 10, history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        为问题检索相关的图谱知识

        Args:
            question: 用户问题
            top_k: 返回的实体数量限制

        Returns:
            检索结果，包含实体、关系、路径等信息
        """
        try:
            if not self.neo4j_client:
                return {
                    "success": False,
                    "message": "Neo4j未连接"
                }

            # 1. 提取问题中的关键词
            keywords = self._extract_keywords(question, history)
            logger.info(f"从问题中提取关键词: {keywords}")

            # 2. 在图谱中搜索相关实体
            entities = self.neo4j_client.search_entities(keywords, limit=top_k)
            logger.info(f"[图谱检索] 找到 {len(entities)} 个相关实体")
            if entities:
                logger.debug(f"[图谱检索] 实体详情: {[{'type': e.get('type'), 'name': e.get('name')} for e in entities[:5]]}")

            # 3. 扩展实体的邻居信息
            # 根据 top_k 参数决定扩展多少个实体，确保不会遗漏重要实体
            expand_limit = min(len(entities), top_k)
            expanded_knowledge = []
            for entity in entities[:expand_limit]:  # 扩展 top_k 个最相关的实体
                entity_name = entity.get('name')
                entity_type = entity.get('type')
                logger.info(f"[实体扩展] 获取 {entity_type} 类型实体 '{entity_name}' 的邻居信息")

                # 获取实体的邻居
                neighbors = self.neo4j_client.get_entity_neighbors(
                    entity_name=entity_name,
                    entity_type=entity_type,
                    depth=1
                )
                
                node_count = len(neighbors.get('nodes', []))
                rel_count = len(neighbors.get('relationships', []))
                logger.info(f"[实体扩展] 实体 '{entity_name}' 有 {node_count} 个邻居节点和 {rel_count} 个关系")

                expanded_knowledge.append({
                    "entity": entity,
                    "neighbors": neighbors
                })

            # 4. 生成知识上下文
            context = self._build_context_from_graph(expanded_knowledge)
            logger.info(f"[上下文生成] 生成知识图谱上下文，长度: {len(context) if context else 0} 字符")

            return {
                "success": True,
                "keywords": keywords,
                "entities": entities,
                "expanded_knowledge": expanded_knowledge,
                "context": context,
                "entity_count": len(entities)
            }

        except Exception as e:
            logger.error(f"图谱检索失败: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }

    def _extract_keywords(self, question: str, history: List[Dict[str, Any]] = None) -> List[str]:
        """
        从问题中提取关键词

        Args:
            question: 用户问题

        Returns:
            关键词列表
        """
        logger.info(f"[关键词提取] 开始提取问题关键词: {question[:100]}...")
        history_pairs = []
        if history:
            logger.debug(f"[关键词提取] 处理对话历史，共 {len(history)} 条记录")
            for msg in history:
                try:
                    role = (msg or {}).get('role', '').lower()
                    content = (msg or {}).get('content', '').strip()
                except AttributeError:
                    continue
                if role in ('user', 'assistant') and content:
                    history_pairs.append((role, content))
            history_pairs = history_pairs[-6:]
            logger.debug(f"[关键词提取] 保留最近 {len(history_pairs)} 条有效对话历史")

        combined_text = question
        if history_pairs:
            combined_text = question + "\n" + "\n".join(content for _, content in history_pairs)

        history_section = ""
        if history_pairs:
            history_items = "\n".join(
                f"- {'用户' if role == 'user' else '助手'}: {content}"
                for role, content in history_pairs
            )
            history_section = f"\n对话历史（按时间顺序）：\n{history_items}\n"

        try:
            logger.info(f"[关键词提取] 使用LLM提取关键词")
            # 使用LLM提取关键词
            prompt = f"""
请直接从下列问题原文中挑选教务相关的关键词。
要求：
1. 关键词必须在问题中出现，并且是专有名词或名词短语（如课程名称、专业名称、政策名称、流程名称等）；
2. 不要生成问题中未出现的新词，也不要输出泛化词（如"影响""情况""问题""如何"等）；
3. 使用中文逗号分隔，数量不超过6个，不附加任何说明文字。

{history_section}
问题：{question}

关键词："""

            system_prompt = "你是教务领域的关键词提取助手，请结合近期对话上下文判断代词指代，只返回原文中出现的关键名词。"

            response = self.text_analyzer.send_message(
                message=prompt,
                system_prompt=system_prompt
            )

            if response.get('success'):
                result = response.get('result', '').strip()
                logger.debug(f"[关键词提取] LLM原始输出: {result}")

                if not result:
                    logger.info(f"[关键词提取] LLM未提取到关键词，使用备用方法")
                    return self._simple_keyword_extract(combined_text)

                candidate_line = result
                lines = [line.strip() for line in result.splitlines() if line.strip()]
                if lines:
                    candidate_line = lines[-1]

                for prefix in ['关键词：', '关键词:', 'Keywords:', 'keywords:', 'Keyword:', 'keyword:']:
                    if candidate_line.startswith(prefix):
                        candidate_line = candidate_line[len(prefix):].strip()
                        break

                raw_keywords = [kw.strip() for kw in re.split(r'[，,]', candidate_line) if kw.strip()]
                logger.debug(f"[关键词提取] 原始关键词列表: {raw_keywords}")
                filtered_keywords = self._filter_keywords(raw_keywords, combined_text)
                logger.info(f"[关键词提取] 提取完成，共 {len(filtered_keywords)} 个关键词: {filtered_keywords}")
                return filtered_keywords
            else:
                # 如果LLM失败，使用简单分词
                logger.warning(f"[关键词提取] LLM提取失败，使用备用方法: {response.get('error', '未知错误')}")
                return self._simple_keyword_extract(combined_text)

        except Exception as e:
            logger.error(f"[关键词提取] 失败: {str(e)}")
            return self._simple_keyword_extract(combined_text or question)

    def _simple_keyword_extract(self, source_text: str) -> List[str]:
        """简单的关键词提取（备用方案）"""
        # 尝试从问题中提取长度大于1的连续中文/数字字符串
        candidates = re.findall('[\u4e00-\u9fa5A-Za-z0-9]{2,}', source_text)
        return self._filter_keywords(candidates, source_text)

    def _filter_keywords(self, keywords: List[str], source_text: str) -> List[str]:
        """过滤并去重关键词，只保留来自问题原文的有效名词短语"""
        if not keywords:
            return []

        stop_words = {
            '影响', '情况', '问题', '如何', '需要', '哪些', '什么', '方式', '措施', '那些',
            '程度', '表现', '发展', '趋势', '变化', '造成', '关于', '请', '输出', '返回', '回答', '仅', '只返回', '主要'
        }

        # 预处理问题文本，移除常见标点用于匹配
        normalized_source = re.sub(r'[\s，,。！？?；;：:、（）()“”"\'-]', '', source_text)

        cleaned = []
        seen = set()

        for kw in keywords:
            keyword = (kw or '').strip()
            if not keyword:
                continue
            if len(keyword) < 2:
                continue
            if keyword in stop_words:
                continue

            normalized_kw = re.sub(r'[\s，,。！？?；;：:、（）()“”"\'-]', '', keyword)
            if not normalized_kw:
                continue

            if normalized_kw not in normalized_source:
                continue

            if keyword in seen:
                continue

            cleaned.append(keyword)
            seen.add(keyword)

            if len(cleaned) >= 3:
                break

        return cleaned

    def _build_context_from_graph(self, expanded_knowledge: List[Dict]) -> str:
        """
        从图谱知识构建上下文文本（生成完整的三元组自然语言描述）

        Args:
            expanded_knowledge: 扩展的知识信息

        Returns:
            上下文文本
        """
        from algo.knowledge_graph.config import NODE_NAMES, RELATIONSHIP_NAMES

        context_parts = []
        seen_triples = set()  # 避免重复的三元组

        for item in expanded_knowledge:
            entity = item.get('entity', {})
            neighbors = item.get('neighbors', {})

            entity_name = entity.get('name')
            entity_type = entity.get('type')
            entity_properties = entity.get('properties', {})

            # 1. 添加实体基本信息（中文类型名称）
            entity_type_cn = NODE_NAMES.get(entity_type, entity_type)
            entity_desc = f"【{entity_type_cn}】{entity_name}"

            # 添加实体的 description 属性（如果有）
            if entity_properties and 'description' in entity_properties:
                description = entity_properties['description']
                if description:
                    # 如果描述太长，截断显示
                    if len(description) > 100:
                        description = description[:100] + "..."
                    entity_desc += f"\n  描述: {description}"

            context_parts.append(entity_desc)

            # 2. 构建完整的三元组自然语言描述
            relationships = neighbors.get('relationships', [])

            if relationships:
                triples = []
                for rel in relationships[:10]:  # 最多显示10个关系
                    rel_type = rel.get('type', '')
                    source = rel.get('source', '')
                    target = rel.get('target', '')
                    source_type = rel.get('source_type', '')
                    target_type = rel.get('target_type', '')

                    # 避免重复
                    triple_key = f"{source}|{rel_type}|{target}"
                    if triple_key in seen_triples:
                        continue
                    seen_triples.add(triple_key)

                    # 获取关系的中文名称
                    rel_type_cn = RELATIONSHIP_NAMES.get(rel_type, rel_type)

                    # 构建自然语言三元组
                    # 格式: "主语(类型) + 谓语 + 宾语(类型)"
                    source_type_cn = NODE_NAMES.get(source_type, source_type)
                    target_type_cn = NODE_NAMES.get(target_type, target_type)

                    triple_text = f"{source}({source_type_cn}){rel_type_cn}{target}({target_type_cn})"
                    triples.append(f"  • {triple_text}")

                if triples:
                    context_parts.append("关联关系：")
                    context_parts.extend(triples)

            context_parts.append("")  # 实体之间添加空行

        return "\n".join(context_parts)

    def find_related_entities(self, entity_name: str, entity_type: str = None, depth: int = 2) -> Dict[str, Any]:
        """
        查找与指定实体相关的其他实体

        Args:
            entity_name: 实体名称
            entity_type: 实体类型
            depth: 搜索深度

        Returns:
            相关实体信息
        """
        try:
            if not self.neo4j_client:
                return {
                    "success": False,
                    "message": "Neo4j未连接"
                }

            graph_data = self.neo4j_client.get_entity_neighbors(
                entity_name=entity_name,
                entity_type=entity_type,
                depth=depth
            )

            return {
                "success": True,
                "data": graph_data
            }

        except Exception as e:
            logger.error(f"查找相关实体失败: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }

    def find_path_between_entities(self, start_entity: str, end_entity: str, max_depth: int = 3) -> Dict[str, Any]:
        """
        查找两个实体之间的关系路径

        Args:
            start_entity: 起始实体名称
            end_entity: 目标实体名称
            max_depth: 最大搜索深度

        Returns:
            路径信息
        """
        try:
            if not self.neo4j_client:
                return {
                    "success": False,
                    "message": "Neo4j未连接"
                }

            paths = self.neo4j_client.find_paths(
                start_entity=start_entity,
                end_entity=end_entity,
                max_depth=max_depth
            )

            return {
                "success": True,
                "paths": paths,
                "count": len(paths)
            }

        except Exception as e:
            logger.error(f"查找路径失败: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }


# 创建全局实例
graph_retriever = GraphRetriever()
