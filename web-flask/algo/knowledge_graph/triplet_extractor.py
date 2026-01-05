
"""
基于LLM的三元组提取服务
从植物病害文档中提取知识图谱三元组
"""
import json
import logging
from typing import List, Dict, Any, Optional
from algo.llm.text_analysis import TextAnalysis
from algo.llm.config import MODEL_CONFIGS, DEFAULT_MODEL
from algo.knowledge_graph.config import NODE_TYPES, RELATIONSHIP_TYPES, NODE_NAMES, RELATIONSHIP_NAMES

logger = logging.getLogger(__name__)

class TripletExtractor:
    """三元组提取器"""

    def __init__(self, model_name: str = DEFAULT_MODEL):
        """
        初始化三元组提取器

        Args:
            model_name: 使用的模型名称，默认使用配置中的默认模型
        """
        self.text_analyzer = TextAnalysis(model_name=model_name)
        self.model_name = model_name

    def extract_triplets(self, document_content: str, document_id: int = None, document_title: str = None, chunk_size: int = 512) -> List[Dict[str, Any]]:
        """
        从文档内容中提取三元组（支持长文档切片）

        Args:
            document_content: 文档内容
            document_id: 文档ID
            document_title: 文档标题
            chunk_size: 每个切片的字符数，默认512字符

        Returns:
            三元组列表，格式: [{"head": "实体1", "head_type": "类型", "relation": "关系", "tail": "实体2", "tail_type": "类型", "properties": {...}}, ...]
        """
        try:
            all_triplets = []

            # 判断是否需要切片
            if len(document_content) <= chunk_size:
                # 文档较短，直接提取
                logger.info(f"文档长度: {len(document_content)} 字符，直接提取")
                all_triplets = self._extract_from_chunk(document_content)
            else:
                # 文档较长，进行切片处理
                chunks = self._split_document(document_content, chunk_size)
                logger.info(f"文档长度: {len(document_content)} 字符，切分为 {len(chunks)} 个片段")

                for i, chunk in enumerate(chunks):
                    logger.info(f"处理片段 {i+1}/{len(chunks)}，长度: {len(chunk)} 字符")
                    chunk_triplets = self._extract_from_chunk(chunk)
                    all_triplets.extend(chunk_triplets)
                    logger.info(f"片段 {i+1} 提取了 {len(chunk_triplets)} 个三元组")

            # 去重（同一文档中可能有重复的三元组）
            all_triplets = self._deduplicate_triplets(all_triplets)
            content_triplets_count = len(all_triplets)

            # 后处理：添加文档关联关系
            if document_id and document_title:
                all_triplets = self._add_document_relationships(all_triplets, document_id, document_title)
                document_relations_count = len(all_triplets) - content_triplets_count
                logger.info(f"添加了 {document_relations_count} 个文档关联关系")

            logger.info(f"成功提取 {len(all_triplets)} 个三元组（内容三元组: {content_triplets_count}, 文档关联: {len(all_triplets) - content_triplets_count}）")
            return all_triplets

        except Exception as e:
            logger.error(f"提取三元组失败: {str(e)}")
            return []

    def _split_document(self, content: str, chunk_size: int) -> List[str]:
        """
        智能切分文档，尽量按句子边界切分

        Args:
            content: 文档内容
            chunk_size: 每个切片的目标大小

        Returns:
            切片列表
        """
        chunks = []
        # 按段落分割
        paragraphs = content.split('\n\n')

        current_chunk = ""
        for para in paragraphs:
            # 如果单个段落就超过chunk_size，需要进一步切分
            if len(para) > chunk_size:
                # 先保存当前chunk
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""

                # 按句子切分长段落
                sentences = para.replace('。', '。\n').replace('！', '！\n').replace('？', '？\n').split('\n')
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) > chunk_size:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence
                    else:
                        current_chunk += sentence
            else:
                # 判断是否超过chunk_size
                if len(current_chunk) + len(para) > chunk_size:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = para
                else:
                    current_chunk += '\n\n' + para if current_chunk else para

        # 添加最后一个chunk
        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _extract_from_chunk(self, chunk_content: str) -> List[Dict[str, Any]]:
        """
        从单个切片中提取三元组

        Args:
            chunk_content: 切片内容

        Returns:
            三元组列表
        """
        try:
            # 构建提示词
            prompt = self._build_extraction_prompt(chunk_content)
            system_prompt = """你是一个专业的教务信息领域知识抽取专家。
请严格按照要求提取知识图谱三元组，并以JSON格式返回。
【重要】必须严格使用指定的节点类型和关系类型，不得创造新的类型。
【重要】如果某个实体不属于任何预定义类型，请跳过该实体。"""

            # 调用LLM
            response = self.text_analyzer.send_message(
                message=prompt,
                system_prompt=system_prompt
            )

            if not response.get('success'):
                logger.error(f"LLM调用失败: {response.get('error')}")
                return []

            # 解析结果
            result_text = response.get('result', '{}')
            # 尝试提取JSON部分（处理可能包含其他文本的情况）
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0].strip()

            result = json.loads(result_text)
            triplets = result.get("triplets", [])

            return triplets

        except Exception as e:
            logger.error(f"从切片提取三元组失败: {str(e)}")
            return []

    def _deduplicate_triplets(self, triplets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        去除重复的三元组

        Args:
            triplets: 三元组列表

        Returns:
            去重后的三元组列表
        """
        seen = set()
        unique_triplets = []

        for triplet in triplets:
            # 使用头实体、关系、尾实体作为唯一标识
            key = (triplet.get("head"), triplet.get("relation"), triplet.get("tail"))
            if key not in seen:
                seen.add(key)
                unique_triplets.append(triplet)

        logger.info(f"去重前: {len(triplets)} 个三元组，去重后: {len(unique_triplets)} 个三元组")
        return unique_triplets

    def _build_extraction_prompt(self, document_content: str) -> str:
        """构建教务信息提取提示词"""
        from algo.knowledge_graph.config import NODE_PROPERTIES

        # 节点类型说明
        node_types_desc = "\n".join([f"- {nt} ({NODE_NAMES.get(nt, nt)})" for nt in NODE_TYPES])

        # 关系类型说明
        rel_types_desc = "\n".join([f"- {rt} ({RELATIONSHIP_NAMES.get(rt, rt)})" for rt in RELATIONSHIP_TYPES])

        # 节点类型和属性说明
        node_props_desc = []
        for node_type in NODE_TYPES:
            cn_name = NODE_NAMES.get(node_type, node_type)
            props = NODE_PROPERTIES.get(node_type, [])
            if props:
                props_str = ", ".join(props)
                node_props_desc.append(f"- {node_type}（{cn_name}）: {props_str}")
            else:
                node_props_desc.append(f"- {node_type}（{cn_name}）: name")
        node_props_text = "\n".join(node_props_desc)

        prompt = f"""你是教务信息领域的知识抽取专家。请从以下文档中提取知识图谱三元组，并为实体添加详细的描述信息。

    **【严格约束】只能使用以下预定义的节点类型，不得使用其他类型：**
    {node_types_desc}

    **【严格约束】只能使用以下预定义的关系类型，不得使用其他类型：**
    {rel_types_desc}

    **提取规则：**
    1. 只提取与教务信息相关的实体和关系
    2. 实体名称要准确、具体，避免过于宽泛
    3. **head_type 和 tail_type 必须严格从上述节点类型列表中选择，不得使用任何其他节点类型**
    4. **relation 必须严格从上述关系类型列表中选择，绝对不允许自创关系类型（如 INCLUDES、CONTAINS、HAS、BELONGS_TO、IS_PART_OF 等都是禁止的）**
    5. 每个三元组包含：头实体、头实体类型、关系、尾实体、尾实体类型
    6. **【非常重要】尽可能为实体添加 description 属性**，description 中应包含该实体的详细描述信息
    7. 如果某个实体不属于任何预定义类型，则跳过该实体
    8. 如果某个关系不属于任何预定义类型，则跳过该三元组

    **节点属性说明：**
    所有节点类型统一使用以下两个属性：
    - **name**: 实体名称（必填，会自动从 head 和 tail 字段设置）
    - **description**: 实体的详细描述（可选但强烈建议填写）

    description 字段应包含：
    - 实体的详细信息、特征、数值等
    - 例如政策的适用范围、生效时间等
    - 例如课程的学分、学时、授课对象等
    - 例如专业的要求、培养目标等
    - 例如流程的步骤、时限、负责人等
    - 任何与该实体相关的描述性文本

    **属性提取示例（请认真参考）：**

    示例1 - 课程实体：
    文档："高等数学是理工科专业的必修课程，共5学分，每周4学时，主要面向大一学生开设。"
    提取：
    {{
      "head": "高等数学",
      "head_type": "Course",
      "relation": "BELONGS_TO",
      "tail": "理工科专业",
      "tail_type": "Major",
      "properties": {{
        "head_description": "理工科专业的必修课程，共5学分，每周4学时，主要面向大一学生开设",
        "tail_description": "包含理工科相关专业的学科类别"
      }}
    }}

    示例2 - 政策实体：
    文档："学校规定本科生必须修满160学分方可毕业，该政策自2023年9月1日起执行。"
    提取：
    {{
      "head": "本科生毕业学分要求",
      "head_type": "AcademicPolicy",
      "relation": "APPLIES_TO",
      "tail": "本科生",
      "tail_type": "Student",
      "properties": {{
        "head_description": "规定本科生必须修满160学分方可毕业，该政策自2023年9月1日起执行",
        "tail_description": "正在攻读学士学位的学生"
      }}
    }}

    示例3 - 流程实体：
    文档："学生选课需先完成网上预选，然后缴费确认，最后打印课表。"
    提取：
    {{
      "head": "学生选课",
      "head_type": "Procedure",
      "relation": "FOLLOWS",
      "tail": "网上预选",
      "tail_type": "Procedure",
      "properties": {{
        "head_description": "学生进行课程选择的完整流程",
        "tail_description": "选课流程的第一步，学生在网上选择意向课程"
      }}
    }}

    示例4 - 要求实体：
    文档："申请转专业学生需已修课程平均绩点不低于2.5，且无不及格记录。"
    提取：
    {{
      "head": "转专业申请",
      "head_type": "Procedure",
      "relation": "MEETS_REQUIREMENT",
      "tail": "平均绩点不低于2.5",
      "tail_type": "Requirement",
      "properties": {{
        "head_description": "学生申请转换专业的流程",
        "tail_description": "申请转专业学生需已修课程平均绩点不低于2.5，且无不及格记录"
      }}
    }}

    **文档内容：**
    {document_content}

    **输出格式要求（严格遵守JSON格式）：**
    {{
      "triplets": [
        {{
          "head": "实体名称",
          "head_type": "节点类型",
          "relation": "关系类型",
          "tail": "实体名称",
          "tail_type": "节点类型",
          "properties": {{
            "head_description": "头实体的详细描述",
            "tail_description": "尾实体的详细描述"
          }}
        }}
      ]
    }}

    **【重要提示】：**
    1. properties 字段中应包含 head_description 和 tail_description 两个字段
    2. **强烈建议为头实体和尾实体都添加 description**，将文档中与该实体相关的所有描述性信息都写入
    3. description 应该是完整的、信息丰富的句子或短语，包含数值、时间、等级等详细信息
    4. 如果文档中没有某个实体的描述信息，可以省略对应的 description 字段，或写一个简短的基本描述
    5. 属性值保留原文中的中文描述，保持准确性
    6. name 属性会自动从 head 和 tail 字段设置，不需要在 properties 中重复添加

    **【最后强调】：**
    - head_type 和 tail_type 只能从预定义的10种节点类型中选择
    - relation 只能从预定义的11种关系类型中选择
    - 绝对不允许使用未列出的节点类型或关系类型
    - 如果提取的三元组包含未定义的类型，该三元组将被系统自动丢弃

    请严格按照上述要求提取，特别注意：
    1. 为头实体和尾实体都添加详细的 description
    2. 保持 JSON 格式正确
    3. description 中包含尽可能多的有用信息
    4. **严格使用预定义的节点类型和关系类型**

    开始提取："""

        return prompt

    def _add_document_relationships(self, triplets: List[Dict], document_id: int, document_title: str) -> List[Dict]:
        """
        为提取的实体添加与文档的关联关系

        Args:
            triplets: 三元组列表
            document_id: 文档ID
            document_title: 文档标题

        Returns:
            增强后的三元组列表
        """
        # 收集所有唯一实体
        entities = set()
        for triplet in triplets:
            entities.add((triplet["head"], triplet["head_type"]))
            entities.add((triplet["tail"], triplet["tail_type"]))

        # 为每个实体添加文档关联
        document_triplets = []
        for entity_name, entity_type in entities:
            document_triplets.append({
                "head": entity_name,
                "head_type": entity_type,
                "relation": "DOCUMENTED_IN",
                "tail": document_title,
                "tail_type": "Document",
                "properties": {
                    "head_description": "",
                    "tail_description": f"文档ID: {document_id}, 标题: {document_title}"
                }
            })

        # 合并原始三元组和文档关联三元组
        return triplets + document_triplets

    def extract_triplets_batch(self, documents: List[Dict[str, Any]], batch_size: int = 5) -> Dict[int, List[Dict]]:
        """
        批量提取多个文档的三元组

        Args:
            documents: 文档列表，每个文档包含 id, title, content
            batch_size: 批处理大小

        Returns:
            文档ID到三元组列表的映射
        """
        results = {}

        for i, doc in enumerate(documents):
            try:
                doc_id = doc.get("id")
                doc_title = doc.get("title")
                doc_content = doc.get("content", "")

                if not doc_content:
                    logger.warning(f"文档 {doc_id} 内容为空，跳过")
                    continue

                logger.info(f"处理文档 {i+1}/{len(documents)}: {doc_title}")

                triplets = self.extract_triplets(doc_content, doc_id, doc_title)
                results[doc_id] = triplets

            except Exception as e:
                logger.error(f"处理文档 {doc.get('id')} 失败: {str(e)}")
                results[doc.get("id")] = []

        return results


def create_triplet_extractor(model_name: str = None) -> Optional[TripletExtractor]:
    """
    创建三元组提取器实例

    Args:
        model_name: 模型名称，如果为None则使用默认模型

    Returns:
        三元组提取器实例
    """
    try:
        model_name = model_name or DEFAULT_MODEL
        if model_name not in MODEL_CONFIGS:
            logger.warning(f"不支持的模型: {model_name}，使用默认模型: {DEFAULT_MODEL}")
            model_name = DEFAULT_MODEL

        return TripletExtractor(model_name=model_name)
    except Exception as e:
        logger.error(f"创建三元组提取器失败: {str(e)}")
        return None
