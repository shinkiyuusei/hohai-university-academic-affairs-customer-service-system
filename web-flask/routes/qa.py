
"""
智能问答路由
基于GraphRAG（图检索增强生成）技术，结合Neo4j知识图谱和通义千问LLM
"""
import logging
from flask import Blueprint, request, g
from werkzeug.utils import secure_filename
from algo.knowledge_graph.graph_retriever import graph_retriever
from algo.llm.text_analysis import TextAnalysis
# from algo.llm.image_understanding import image_understanding
from clients.file_client import file_client
# from services.plant_disease_service import plant_disease_service
# from services.disease_case_service import disease_case_service
# 暂时注释掉植物病害服务，替换为教务咨询服务
from services.academic_info_service import academic_info_service
from services.academic_case_service import academic_case_service
from utils.response import success, error
from utils.db import db
from utils.jwt_util import token_required
from utils.security_utils import get_current_user, is_admin
from config import TEMP_DIR
import os
# import cv2
# import numpy as np
import re
import json
import uuid
from typing import List, Dict, Any

# 配置日志
logger = logging.getLogger(__name__)

qa_bp = Blueprint('qa', __name__, url_prefix='/api/qa')
# 防篡改锚点·YángYáng小栈原创 2025，未经书面授权，请勿复制。🛡️

# ==================== 全局配置 ====================
# 问答模块图片存储桶名称（用于存储问答历史中引用的图片快照）
QA_IMAGES_BUCKET = 'qa-history-images'


def _truncate_text(text: str, length: int = 120) -> str:
    if not text:
        return ''
    text = str(text).strip()
    return text if len(text) <= length else text[:length] + '...'


def _format_datetime(value) -> str:
    if not value:
        return '未知'
    value_str = str(value).strip()
    if not value_str:
        return '未知'
    return value_str[:16]


def _delete_qa_images_from_records(qa_records: List[Dict[str, Any]]) -> None:
    """
    删除问答记录中转存的图片

    Args:
        qa_records: 问答历史记录列表
    """
    deleted_count = 0
    failed_count = 0
    skipped_count = 0

    logger.debug(f"[调试] 开始处理 {len(qa_records)} 条问答记录")

    for record in qa_records:
        # 1. 删除用户上传的问题图片
        if record.get('image_bucket') and record.get('image_object_key'):
            logger.debug(f"[调试] 用户上传图片 - bucket: {record['image_bucket']}, 期望bucket: {QA_IMAGES_BUCKET}")
            # 只删除转存到QA_IMAGES_BUCKET的图片
            if record['image_bucket'] == QA_IMAGES_BUCKET:
                try:
                    logger.info(f"[图片删除] 删除用户上传图片: {record['image_bucket']}/{record['image_object_key']}")
                    file_client.delete(record['image_bucket'], record['image_object_key'])
                    deleted_count += 1
                except Exception as e:
                    logger.warning(f"[警告] 删除用户上传图片失败: {str(e)}")
                    failed_count += 1
            else:
                logger.info(f"[跳过] 用户上传图片不在QA存储桶中: {record['image_bucket']}/{record['image_object_key']}")
                skipped_count += 1

        # 2. 删除教务信息中转存的图片
        if record.get('disease_info_matches'):
            try:
                academic_info_matches = json.loads(record['disease_info_matches'])
                logger.debug(f"[调试] academic_info_matches解析成功，共 {len(academic_info_matches) if isinstance(academic_info_matches, list) else 0} 条")
                if isinstance(academic_info_matches, list):
                    for idx, academic_info in enumerate(academic_info_matches):
                        if not isinstance(academic_info, dict):
                            continue

                        bucket = academic_info.get('image_bucket')
                        object_key = academic_info.get('image_object_key')

                        logger.debug(f"[调试] 教务信息[{idx}] - bucket: {bucket}, 期望bucket: {QA_IMAGES_BUCKET}")

                        # 只删除转存到QA_IMAGES_BUCKET的图片
                        if bucket == QA_IMAGES_BUCKET and object_key:
                            try:
                                logger.info(f"[图片删除] 删除教务信息图片: {bucket}/{object_key}")
                                file_client.delete(bucket, object_key)
                                deleted_count += 1
                            except Exception as e:
                                logger.warning(f"[警告] 删除教务信息图片失败: {str(e)}")
                                failed_count += 1
                        elif bucket and object_key:
                            logger.info(f"[跳过] 教务信息图片不在QA存储桶中: {bucket}/{object_key}")
                            skipped_count += 1
            except Exception as e:
                logger.warning(f"[警告] 解析academic_info_matches失败: {str(e)}")

        # 3. 删除教务案例中转存的图片
        if record.get('disease_case_matches'):
            try:
                academic_case_matches = json.loads(record['disease_case_matches'])
                logger.debug(f"[调试] academic_case_matches解析成功，共 {len(academic_case_matches) if isinstance(academic_case_matches, list) else 0} 条")
                if isinstance(academic_case_matches, list):
                    for case_idx, case in enumerate(academic_case_matches):
                        if not isinstance(case, dict):
                            continue

                        images = case.get('images', [])
                        logger.debug(f"[调试] 教务案例[{case_idx}] '{case.get('case_title')}' - {len(images) if isinstance(images, list) else 0} 张图片")
                        if isinstance(images, list):
                            for img_idx, img in enumerate(images):
                                if not isinstance(img, dict):
                                    continue

                                bucket = img.get('bucket')
                                object_key = img.get('object_key')

                                logger.debug(f"[调试] 案例图片[{img_idx}] - bucket: {bucket}, 期望bucket: {QA_IMAGES_BUCKET}")

                                # 只删除转存到QA_IMAGES_BUCKET的图片
                                if bucket == QA_IMAGES_BUCKET and object_key:
                                    try:
                                        logger.info(f"[图片删除] 删除教务案例图片: {bucket}/{object_key}")
                                        file_client.delete(bucket, object_key)
                                        deleted_count += 1
                                    except Exception as e:
                                        logger.warning(f"[警告] 删除教务案例图片失败: {str(e)}")
                                        failed_count += 1
                                elif bucket and object_key:
                                    logger.info(f"[跳过] 教务案例图片不在QA存储桶中: {bucket}/{object_key}")
                                    skipped_count += 1
            except Exception as e:
                logger.warning(f"[警告] 解析academic_case_matches失败: {str(e)}")

    logger.info(f"[图片删除完成] 成功删除 {deleted_count} 张，失败 {failed_count} 张，跳过 {skipped_count} 张")


def _copy_images_to_qa_storage(academic_info_matches: List[Dict[str, Any]],
                                academic_case_matches: List[Dict[str, Any]]) -> tuple:
    """
    将教务信息和案例中的图片转存到问答历史图片存储桶

    Args:
        academic_info_matches: 教务信息列表
        academic_case_matches: 教务案例列表

    Returns:
        tuple: (更新后的教务信息列表, 更新后的案例列表)
    """
    # 转存教务信息图片
    for academic_info in academic_info_matches:
        if academic_info.get('image_bucket') and academic_info.get('image_object_key'):
            try:
                logger.info(f"[图片转存] 转存教务信息图片: {academic_info.get('name')}")

                # 下载原图片内容
                image_content = file_client.get(
                    academic_info['image_bucket'],
                    academic_info['image_object_key']
                )

                # 创建临时文件
                original_filename = academic_info['image_object_key'].split('/')[-1]
                file_ext = os.path.splitext(original_filename)[1] or '.jpg'
                temp_filename = f"qa_academic_{uuid.uuid4().hex}{file_ext}"
                temp_path = os.path.join(TEMP_DIR, temp_filename)

                # 保存到临时文件
                with open(temp_path, 'wb') as f:
                    f.write(image_content)

                try:
                    # 上传到问答历史图片存储桶
                    upload_result = file_client.upload(QA_IMAGES_BUCKET, temp_path, is_cache=False)

                    # 更新图片信息
                    academic_info['image_bucket'] = upload_result['bucket']
                    academic_info['image_object_key'] = upload_result['objectKey']
                    academic_info['imageUrl'] = upload_result['url']

                    logger.info(f"[图片转存] 教务信息图片转存成功: {upload_result['url']}")
                finally:
                    # 删除临时文件
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

            except Exception as e:
                logger.error(f"[错误] 教务信息图片转存失败，清空图片信息: {str(e)}")
                # 转存失败则清空图片字段
                academic_info['image_bucket'] = None
                academic_info['image_object_key'] = None
                academic_info['imageUrl'] = None

    # 转存教务案例图片
    for case in academic_case_matches:
        images_field = case.get('images')

        # 兼容字符串存储的场景
        if isinstance(images_field, str):
            try:
                images_field = json.loads(images_field)
            except Exception:
                images_field = []

        if not isinstance(images_field, list) or not images_field:
            case['images'] = []
            continue

        try:
            new_images = []

            for img in images_field:
                if not isinstance(img, dict):
                    continue

                bucket = img.get('bucket')
                object_key = img.get('object_key') or img.get('objectKey')

                if not bucket or not object_key:
                    continue

                try:
                    logger.info(f"[图片转存] 转存案例图片: {case.get('case_title')} - 原bucket: {bucket}, 原object_key: {object_key}")

                    # 下载原图片内容
                    image_content = file_client.get(bucket, object_key)
                    logger.debug(f"[图片转存] 图片下载成功，大小: {len(image_content)} bytes")

                    # 创建临时文件
                    original_filename = object_key.split('/')[-1]
                    file_ext = os.path.splitext(original_filename)[1] or '.jpg'
                    temp_filename = f"qa_case_{uuid.uuid4().hex}{file_ext}"
                    temp_path = os.path.join(TEMP_DIR, temp_filename)

                    # 保存到临时文件
                    with open(temp_path, 'wb') as f:
                        f.write(image_content)

                    try:
                        # 上传到问答历史图片存储桶
                        upload_result = file_client.upload(QA_IMAGES_BUCKET, temp_path, is_cache=False)

                        # 添加新的图片信息（只保留bucket和object_key，不包含url）
                        new_images.append({
                            'bucket': upload_result['bucket'],
                            'object_key': upload_result['objectKey']
                        })

                        logger.info(f"[图片转存] 案例图片转存成功")
                        logger.debug(f"  新bucket: {upload_result['bucket']}, 新object_key: {upload_result['objectKey']}")
                    finally:
                        # 删除临时文件
                        if os.path.exists(temp_path):
                            os.remove(temp_path)

                except Exception as e:
                    logger.error(f"[错误] 案例图片转存失败，跳过该图片: {str(e)}")
                    logger.error(f"  失败的图片: bucket={bucket}, object_key={object_key}")
                    # 转存失败直接跳过，不添加到结果中
                    continue

            # 更新案例的图片信息（不再包含imageUrls）
            case['images'] = new_images
            logger.info(f"[图片转存] 案例 '{case.get('case_title')}' 处理完成，共 {len(new_images)} 张图片")
            logger.debug(f"  images: {json.dumps(new_images, ensure_ascii=False)}")

        except Exception as e:
            logger.error(f"[错误] 案例图片列表处理失败，清空图片信息: {str(e)}")
            import traceback
            traceback.print_exc()
            # 处理失败则清空图片数据
            case['images'] = []

    return academic_info_matches, academic_case_matches


# 更新上下文构建逻辑
def build_academic_info_context(academic_matches: List[Dict]) -> str:
    """构建教务信息上下文"""
    if not academic_matches:
        return ""

    context_parts = ["教务相关信息："]
    for match in academic_matches[:3]:  # 限制匹配数量
        context_parts.append(f"- {match.get('name', '')}: {match.get('description', '')}")

    return "\n".join(context_parts)


def build_academic_case_context(academic_case_matches: List[Dict]) -> str:
    """构建教务案例上下文"""
    if not academic_case_matches:
        return ""

    context_parts = ["相关教务案例："]
    for match in academic_case_matches[:2]:
        context_parts.append(
            f"- {match.get('case_title', '')} "
            f"({match.get('case_date', '')}): {match.get('description', '')}"
        )

    return "\n".join(context_parts)




@qa_bp.route('/conversation/list', methods=['GET'])
@token_required
def get_conversation_list():
    """
    获取会话列表

    Response:
        {
            "code": 200,
            "message": "获取成功",
            "data": [
                {
                    "id": 1,
                    "title": "发动机维护咨询",
                    "create_time": "2025-01-01 10:00:00",
                    "update_time": "2025-01-01 11:00:00",
                    "message_count": 5
                }
            ]
        }
    """
    try:
        user = get_current_user()
        user_id = user.id

        # 查询用户的所有会话
        sql = """
        SELECT
            c.id, c.title, c.create_time, c.update_time,
            COUNT(q.id) as message_count
        FROM conversation c
        LEFT JOIN qa_history q ON c.id = q.conversation_id
        WHERE c.user_id = ?
        GROUP BY c.id
        ORDER BY c.update_time DESC
        """

        conversations = db.query(sql, (user_id,))

        return success({
            'list': conversations,
            'total': len(conversations)
        }, '获取会话列表成功')

    except Exception as e:
        logger.error(f"[错误] 获取会话列表失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return error(f'获取会话列表失败: {str(e)}')


@qa_bp.route('/conversation/all', methods=['GET'])
@token_required
def get_all_conversations():
    """
    获取所有用户的会话列表（仅管理员）
    用于管理后台统计

    Response:
        {
            "code": 200,
            "message": "获取成功",
            "data": {
                "list": [...],
                "total": 100
            }
        }
    """
    try:
        # 验证是否为管理员
        if not is_admin():
            return error('权限不足，仅管理员可访问', 403)

        # 查询所有会话
        sql = """
        SELECT
            c.id, c.title, c.user_id, c.user_name, c.create_time, c.update_time,
            COUNT(q.id) as message_count
        FROM conversation c
        LEFT JOIN qa_history q ON c.id = q.conversation_id
        GROUP BY c.id
        ORDER BY c.update_time DESC
        """

        conversations = db.query(sql)

        return success({
            'list': conversations,
            'total': len(conversations)
        }, '获取所有会话列表成功')

    except Exception as e:
        logger.error(f"[错误] 获取所有会话列表失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return error(f'获取所有会话列表失败: {str(e)}')


@qa_bp.route('/conversation/create', methods=['POST'])
@token_required
def create_conversation():
    """
    创建新会话

    Request Body:
        {
            "title": "会话标题"  # 可选，默认为"新会话"
        }

    Response:
        {
            "code": 200,
            "message": "创建成功",
            "data": {
                "id": 1,
                "title": "新会话"
            }
        }
    """
    try:
        user = get_current_user()
        user_id = user.id
        user_name = user.username

        data = request.get_json() or {}
        title = data.get('title', '新会话').strip()

        if not title:
            title = '新会话'

        # 创建会话
        sql = """
        INSERT INTO conversation (title, user_id, user_name)
        VALUES (?, ?, ?)
        """

        db.execute(sql, (title, user_id, user_name))

        # 获取新创建的会话ID
        conversation_id = db.query("SELECT last_insert_rowid() as id", fetchone=True)['id']

        return success({
            'conversation_id': conversation_id,
            'title': title
        }, '创建会话成功')

    except Exception as e:
        logger.error(f"[错误] 创建会话失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return error(f'创建会话失败: {str(e)}')


@qa_bp.route('/conversation/<int:conversation_id>', methods=['DELETE'])
@token_required
def delete_conversation(conversation_id):
    """
    删除会话（会级联删除会话中的所有消息）

    Response:
        {
            "code": 200,
            "message": "删除成功"
        }
    """
    try:
        user = get_current_user()
        user_id = user.id

        # 检查会话是否存在且属于当前用户
        check_sql = "SELECT user_id FROM conversation WHERE id = ?"
        conversation = db.query(check_sql, (conversation_id,), fetchone=True)

        if not conversation:
            return error('会话不存在')

        if not is_admin() and conversation['user_id'] != user_id:
            return error('无权删除此会话')

        # 第一步：查询会话中的所有问答记录（用于删除图片）
        query_sql = """
        SELECT id, image_bucket, image_object_key, disease_info_matches, disease_case_matches
        FROM qa_history
        WHERE conversation_id = ?
        """
        qa_records = db.query(query_sql, (conversation_id,))

        # 第二步：删除转存的图片
        if qa_records:
            logger.info(f"[删除会话] 会话{conversation_id}包含{len(qa_records)}条记录，开始删除转存图片")
            _delete_qa_images_from_records(qa_records)
        else:
            logger.info(f"[删除会话] 会话{conversation_id}没有问答记录")

        # 第三步：删除数据库记录
        db.execute("DELETE FROM qa_history WHERE conversation_id = ?", (conversation_id,))
        delete_sql = "DELETE FROM conversation WHERE id = ?"
        db.execute(delete_sql, (conversation_id,))

        return success(None, '删除会话成功')

    except Exception as e:
        logger.error(f"[错误] 删除会话失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return error(f'删除会话失败: {str(e)}')


@qa_bp.route('/conversation/<int:conversation_id>/rename', methods=['PUT'])
@token_required
def rename_conversation(conversation_id):
    """
    重命名会话

    Request Body:
        {
            "title": "新标题"
        }

    Response:
        {
            "code": 200,
            "message": "重命名成功"
        }
    """
    try:
        user = get_current_user()
        user_id = user.id

        data = request.get_json()
        if not data or not data.get('title'):
            return error('请提供新标题')

        title = data.get('title').strip()
        if not title:
            return error('标题不能为空')

        # 检查会话是否存在且属于当前用户
        check_sql = "SELECT user_id FROM conversation WHERE id = ?"
        conversation = db.query(check_sql, (conversation_id,), fetchone=True)

        if not conversation:
            return error('会话不存在')

        if not is_admin() and conversation['user_id'] != user_id:
            return error('无权修改此会话')

        # 更新会话标题
        update_sql = """
        UPDATE conversation
        SET title = ?, update_time = CURRENT_TIMESTAMP
        WHERE id = ?
        """
        db.execute(update_sql, (title, conversation_id))

        return success(None, '重命名成功')

    except Exception as e:
        logger.error(f"[错误] 重命名会话失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return error(f'重命名会话失败: {str(e)}')


@qa_bp.route('/conversation/<int:conversation_id>/messages', methods=['GET'])
@token_required
def get_conversation_messages(conversation_id):
    """
    获取会话中的所有消息

    Response:
        {
            "code": 200,
            "message": "获取成功",
            "data": [
                {
                    "id": 1,
                    "question": "问题",
                    "answer": "答案",
                    "related_entities": [],
                    "create_time": "2025-01-01 10:00:00"
                }
            ]
        }
    """
    try:
        user = get_current_user()
        user_id = user.id

        # 检查会话是否存在且属于当前用户
        check_sql = "SELECT user_id FROM conversation WHERE id = ?"
        conversation = db.query(check_sql, (conversation_id,), fetchone=True)

        if not conversation:
            return error('会话不存在')

        if not is_admin() and conversation['user_id'] != user_id:
            return error('无权访问此会话')

        # 获取会话中的所有消息
        messages_sql = """
        SELECT id, question, answer, related_entities, graph_context,
               disease_info_matches, disease_case_matches, keywords,
               image_url, create_time
        FROM qa_history
        WHERE conversation_id = ?
        ORDER BY create_time ASC
        """

        messages = db.query(messages_sql, (conversation_id,))

        # 解析 JSON字段
        for msg in messages:
            try:
                related_entities_str = msg.get('related_entities', '[]')
                msg['related_entities'] = json.loads(related_entities_str) if related_entities_str else []
            except:
                msg['related_entities'] = []

            try:
                info_str = msg.get('disease_info_matches', '[]')
                msg['academic_info_matches'] = json.loads(info_str) if info_str else []
            except:
                msg['academic_info_matches'] = []

            try:
                case_str = msg.get('disease_case_matches', '[]')
                msg['academic_case_matches'] = json.loads(case_str) if case_str else []
            except:
                msg['academic_case_matches'] = []

            try:
                keywords_str = msg.get('keywords', '[]')
                parsed_keywords = json.loads(keywords_str) if keywords_str else []
                msg['keywords'] = parsed_keywords if isinstance(parsed_keywords, list) else []
            except:
                msg['keywords'] = []

            # graph_context 已经是字符串，无需解析
            if not msg.get('graph_context'):
                msg['graph_context'] = ''
            if msg['academic_info_matches']:
                msg['academic_info_context'] = build_academic_info_context(msg['academic_info_matches'])
            else:
                msg['academic_info_context'] = ''

            if msg['academic_case_matches']:
                msg['academic_case_context'] = build_academic_case_context(msg['academic_case_matches'])
            else:
                msg['academic_case_context'] = ''

        return success({
            'list': messages,
            'total': len(messages)
        }, '获取消息成功')

    except Exception as e:
        logger.error(f"[错误] 获取会话消息失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return error(f'获取会话消息失败: {str(e)}')


@qa_bp.route('/conversation/<int:conversation_id>/messages', methods=['DELETE'])
@token_required
def clear_conversation_messages(conversation_id):
    """
    清除会话的所有消息记录

    Response:
        {
            "code": 200,
            "message": "清除成功"
        }
    """
    try:
        user = get_current_user()
        user_id = user.id

        # 检查会话是否存在且属于当前用户
        check_sql = "SELECT user_id FROM conversation WHERE id = ?"
        conversation = db.query(check_sql, (conversation_id,), fetchone=True)

        if not conversation:
            return error('会话不存在')

        if not is_admin() and conversation['user_id'] != user_id:
            return error('无权清除此会话的消息')

        # 第一步：查询会话中的所有问答记录（用于删除图片）
        query_sql = """
        SELECT id, image_bucket, image_object_key, disease_info_matches, disease_case_matches
        FROM qa_history
        WHERE conversation_id = ?
        """
        qa_records = db.query(query_sql, (conversation_id,))

        # 第二步：删除转存的图片
        if qa_records:
            logger.info(f"[清除消息] 会话{conversation_id}包含{len(qa_records)}条记录，开始删除转存图片")
            _delete_qa_images_from_records(qa_records)
        else:
            logger.info(f"[清除消息] 会话{conversation_id}没有问答记录")

        # 第三步：删除数据库记录
        delete_sql = "DELETE FROM qa_history WHERE conversation_id = ?"
        deleted_count = db.execute(delete_sql, (conversation_id,))

        logger.info(f"[清除成功] 会话{conversation_id}共清除{deleted_count}条消息")
        return success(None, f'清除成功,共删除{deleted_count}条消息')

    except Exception as e:
        logger.error(f"[错误] 清除会话消息失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return error(f'清除会话消息失败: {str(e)}')


@qa_bp.route('/conversation/<int:conversation_id>/generate-title', methods=['POST'])
@token_required
def generate_conversation_title(conversation_id):
    """
    根据会话聊天记录自动生成标题

    Response:
        {
            "code": 200,
            "message": "标题生成成功",
            "data": {
                "title": "生成的标题"
            }
        }
    """
    try:
        user = get_current_user()
        user_id = user.id

        # 检查会话是否存在且属于当前用户
        check_sql = "SELECT user_id, title FROM conversation WHERE id = ?"
        conversation = db.query(check_sql, (conversation_id,), fetchone=True)

        if not conversation:
            return error('会话不存在')

        if not is_admin() and conversation['user_id'] != user_id:
            return error('无权修改此会话')

        # 获取该会话的最近几条消息（最多3轮对话，即6条消息）
        messages_sql = """
        SELECT question, answer
        FROM qa_history
        WHERE conversation_id = ?
        ORDER BY create_time ASC
        LIMIT 6
        """
        messages = db.query(messages_sql, (conversation_id,))

        if not messages or len(messages) == 0:
            return error('会话没有消息记录，无法生成标题')

        # 构建对话内容用于生成标题
        conversation_context = []
        for msg in messages:
            conversation_context.append(f"用户: {msg['question']}")
            conversation_context.append(f"AI: {msg['answer'][:200]}")  # 限制长度

        context_text = "\n".join(conversation_context)

        # 使用LLM生成标题
        logger.info(f"[标题生成] 开始为会话{conversation_id}生成标题...")

        title_prompt = f"""请根据以下对话内容，生成一个简洁的会话标题（8-15字）。

对话内容：
{context_text}

要求：
1. 标题要简洁明了，8-15个字
2. 能够准确概括对话的核心主题
3. 只输出标题内容，不要有任何其他说明文字
4. 不要包含"会话"、"对话"等词语

标题："""

        llm = TextAnalysis()
        title_result = llm.send_message(title_prompt, "你是一个专业的标题生成助手。")

        if not title_result.get('success'):
            return error(f"标题生成失败: {title_result.get('error', '未知错误')}")

        generated_title = title_result.get('result', '').strip()

        # 清理标题（移除可能的引号、冒号等）
        generated_title = generated_title.replace('"', '').replace("'", '').replace(':', '').replace('：', '')

        # 限制标题长度
        if len(generated_title) > 30:
            generated_title = generated_title[:30]

        if not generated_title:
            return error('生成的标题为空，请重试')

        # 更新会话标题
        update_sql = "UPDATE conversation SET title = ?, update_time = CURRENT_TIMESTAMP WHERE id = ?"
        db.execute(update_sql, (generated_title, conversation_id))

        logger.info(f"[标题生成] 成功为会话{conversation_id}生成标题: {generated_title}")

        return success({'title': generated_title}, '标题生成成功')

    except Exception as e:
        logger.error(f"[错误] 生成会话标题失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return error(f'生成会话标题失败: {str(e)}')


@qa_bp.route('/ask', methods=['POST'])
@token_required
def ask_question():
    """
    智能问答接口（支持多轮对话+会话管理+知识图谱检索）

    Request Body:
        {
            "question": "用户问题",
            "conversation_id": 1,  # 必填，所属会话ID
            "top_k": 10,  # 可选，检索的相关实体数量，默认10
            "history": [  # 可选，对话历史（最近N轮）
                {"role": "user", "content": "之前的问题"},
                {"role": "assistant", "content": "之前的回答"}
            ]
        }

    Response:
        {
            "code": 200,
            "message": "回答成功",
            "data": {
                "question": "用户问题",
                "answer": "AI生成的答案",
                "related_entities": [...]  // 相关知识图谱实体列表
                "graph_context": "..."  // 图谱上下文信息
            }
        }
    """
    try:
        import time
        # 记录请求开始时间
        start_time = time.time()
        
        # 获取当前用户信息
        user = get_current_user()
        user_id = user.id
        user_name = user.username
        
        # 判断请求类型(form-data或json)
        if request.content_type and 'multipart/form-data' in request.content_type:
            # 表单数据(包含图片)
            question = request.form.get('question', '').strip()
            conversation_id = request.form.get('conversation_id')
            if conversation_id:
                conversation_id = int(conversation_id)
            top_k = int(request.form.get('top_k', 10))

            # 解析history
            history_str = request.form.get('history', '[]')
            history = json.loads(history_str) if history_str else []

            # 获取图片文件
            image_file = request.files.get('image')
        else:
            # JSON数据(纯文字)
            data = request.get_json()
            question = data.get('question', '').strip()
            conversation_id = data.get('conversation_id')
            top_k = data.get('top_k', 10)
            history = data.get('history', [])
            image_file = None

        # 记录请求信息
        logger.info(f"[请求] 用户 {user_id} 发起聊天请求，问题：{question[:100]}...")

        # 参数校验
        if not question:
            return error('问题不能为空')

        if not conversation_id:
            return error('conversation_id不能为空')

        if top_k < 1 or top_k > 20:
            return error('top_k参数必须在1-20之间')

        # 校验历史记录格式
        if history and not isinstance(history, list):
            return error('history参数必须是数组')

        # 检查会话是否存在且属于当前用户
        check_sql = "SELECT user_id FROM conversation WHERE id = ?"
        conversation = db.query(check_sql, (conversation_id,), fetchone=True)

        if not conversation:
            return error('会话不存在')

        if conversation['user_id'] != user_id:
            return error('无权访问此会话')

        # 处理图片(如果有)
        image_analysis_result = None
        image_bucket = None
        image_object_key = None
        image_url = None

        if image_file:
            logger.info(f"[图片] 接收到图片: {image_file.filename}")

            # 保存临时文件
            filename = secure_filename(image_file.filename)
            temp_path = os.path.join(TEMP_DIR, filename)
            image_file.save(temp_path)

            try:
                # 读取图片
                # image_np = cv2.imread(temp_path)
                # if image_np is None:
                #     return error('图片格式不支持或文件损坏')

                # 暂时注释图片分析功能
                # print(f"[图片理解] 开始分析图片")
                # prompt = f"请详细分析这张教务相关图片，描述你看到的内容、包含的信息等，并结合用户问题给出初步判断。\n\n用户问题：{question}"
                # analysis = image_understanding.analyze_image(image_np, prompt)

                # if not analysis['success']:
                #     return error(f'图片分析失败: {analysis.get("error", "未知错误")}')

                # image_analysis_result = analysis['result']
                # print(f"[图片理解] 分析结果: {image_analysis_result[:200]}...")
                image_analysis_result = "[图片分析功能暂不可用]"

                # 上传图片到文件服务器
                logger.info(f"[文件上传] 上传图片到文件服务器")
                upload_result = file_client.upload(QA_IMAGES_BUCKET, temp_path, is_cache=False)
                image_bucket = upload_result['bucket']
                image_object_key = upload_result['objectKey']
                image_url = upload_result['url']
                logger.info(f"[文件上传] 图片URL: {image_url}")
            except Exception as e:
                logger.error(f"[错误] 图片处理失败: {str(e)}")
                import traceback
                traceback.print_exc()
                return error(f'图片处理失败: {str(e)}')
            finally:
                # 删除临时文件
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        # 第一步：判断是否需要RAG检索
        # 智能意图识别模块 - 羊小栈 Original Algorithm © 2025
        # 基于上下文分析的RAG检索决策系统，优化查询效率与响应准确度
        # 如果上传了图片，跳过RAG检索，直接使用图片理解结果
        if image_analysis_result:
            logger.info("[图片问答] 检测到图片上传，跳过RAG检索，直接使用图片理解")
            need_rag = False
        else:
            # 意图识别：判断是否需要RAG检索
            logger.info(f"[意图识别] 问题: {question}")

            # 在意图识别部分更新提示词
            intent_prompt = f"""请判断用户的问题是否需要查询教务知识图谱来回答。

            用户问题：{question}

            判断标准：
            1. 如果是打招呼、闲聊、感谢等日常对话，输出：NO
            2. 如果是询问教务政策、课程信息、选课指导、学分认定等，输出：YES
            3. 如果是询问专业要求、培养方案、考试安排等，输出：YES
            4. 如果是询问转专业补修、考试成绩复核流程、职称晋升听课等，输出：YES
            5. 如果用户明确要求检索知识、查询图谱、搜索资料等，输出：YES

            只输出 YES 或 NO，不要有其他内容。"""

            llm = TextAnalysis()
            intent_result = llm.send_message(intent_prompt, "你是一个专业的意图识别助手，只输出YES或NO。")

            need_rag = "YES" in intent_result.get('result', '').upper()
            logger.info(f"[意图识别] 是否需要RAG检索: {need_rag}")

        # 第二步：根据意图决定是否进行GraphRAG检索
        graph_context = ""
        graph_entities = []
        keywords = []
        academic_info_matches = []
        academic_case_matches = []
        academic_info_context = ""
        academic_case_context = ""

        if need_rag:
            # 使用知识图谱检索相关知识
            logger.info(f"[图谱检索] 问题: {question}")

            retrieval_result = graph_retriever.retrieve_for_question(question, top_k=top_k, history=history)

            if retrieval_result.get('success'):
                graph_context = retrieval_result.get('context', '')
                graph_entities = retrieval_result.get('entities', [])
                keywords = retrieval_result.get('keywords', [])
                entity_count = retrieval_result.get('entity_count', 0)

                if entity_count > 0:
                    logger.info(f"[图谱检索成功] 检索到 {entity_count} 个相关实体")
                else:
                    logger.info("[图谱检索] 未找到相关实体")

                if keywords:
                    logger.info(f"[关键字] 从问题中提取的关键词: {keywords}")

                    # 调用教务信息服务进行关键词检索
                    info_search = academic_info_service.search_by_keywords(keywords, limit=3)
                    if info_search.get('success'):
                        academic_info_matches = info_search.get('data', [])
                        if academic_info_matches:
                            academic_info_context = build_academic_info_context(academic_info_matches)
                            logger.info(f"[关键词检索] 匹配到 {len(academic_info_matches)} 条教务信息")
                    else:
                        logger.error(f"[关键词检索] 教务信息检索失败: {info_search.get('error')}")
                        academic_info_matches = []
                        academic_info_context = ""

                    # 调用教务案例服务进行关键词检索
                    case_search = academic_case_service.search_by_keywords(keywords, limit=3)
                    if case_search.get('success'):
                        academic_case_matches = case_search.get('data', [])
                        if academic_case_matches:
                            academic_case_context = build_academic_case_context(academic_case_matches)
                            logger.info(f"[关键词检索] 匹配到 {len(academic_case_matches)} 条教务案例信息")
                    else:
                        logger.error(f"[关键词检索] 教务案例检索失败: {case_search.get('error')}")
                        academic_case_matches = []
                        academic_case_context = ""
            else:
                logger.error(f"[图谱检索失败] {retrieval_result.get('message', '未知错误')}")
                # 图谱检索失败不影响主流程，继续执行
        else:
            # 不需要RAG检索，直接回答
            logger.info("[意图识别] 判定为日常对话，不进行GraphRAG检索")

        # 第三步：构建提示词
        # 构建对话历史上下文
        history_context = ""
        if history:
            history_parts = []
            for msg in history[-6:]:  # 只保留最近3轮对话（6条消息）
                role = msg.get('role', '')
                content = msg.get('content', '')
                if role == 'user':
                    history_parts.append(f"用户: {content}")
                elif role == 'assistant':
                    history_parts.append(f"助手: {content}")

            if history_parts:
                history_context = "\n\n【对话历史】\n" + "\n".join(history_parts) + "\n"

        # 根据是否需要GraphRAG检索，构建不同的提示词
        context_parts = []
        if image_analysis_result:
            context_parts.append(f"【图片分析】\n{image_analysis_result}")
        if graph_context:
            context_parts.append("【知识图谱信息】\n" + graph_context)
        if academic_info_context:
            context_parts.append(academic_info_context)
        if academic_case_context:
            context_parts.append(academic_case_context)

        combined_context = "\n\n".join(context_parts)

        if combined_context:
            source_labels = []
            if graph_context:
                source_labels.append("知识图谱信息")
            if academic_info_context:
                source_labels.append("教务基础信息")
            if academic_case_context:
                source_labels.append("教务案例信息")
            if image_analysis_result:
                source_labels.append("图片分析结果")

            sources_note = "、".join(source_labels) if source_labels else "补充资料"

            system_prompt = f"""你是一个专业的教务咨询知识助手。请基于以下{sources_note}和对话历史，准确回答用户的问题。
{history_context}
检索到的相关内容：
{combined_context}

回答要求：
1. 如果用户问题涉及代词（如"它"、"这个"、"那个"等），请结合对话历史理解指代内容
2. 充分利用提供的结构化信息（知识图谱、政策文件、课程信息等），不要遗漏关键事实
3. 回答必须严格基于提供的资料，不得编造信息；若资料不足，请明确说明
4. 如有图片分析结果，请结合图片中的信息进行分析
5. 引用内容时，请注明来源（例如关联的政策名称、课程代码或知识图谱实体）
6. 回答要准确、专业、简洁，优先使用教务行业术语和标准
7. 如果涉及政策名称、时间、流程步骤等结构化信息，请清晰地组织答案"""
        else:
            # 无检索结果（日常对话或仅图片分析），构建通用提示词
            if image_analysis_result:
                # 有图片但无GraphRAG检索
                system_prompt = f"""你是一个专业的教务咨询智能助手。请基于以下图片分析结果和对话历史，回答用户的问题。
{history_context}
【图片分析】
{image_analysis_result}

回答要求：
1. 充分结合图片分析结果给出专业的教务相关解答和建议
2. 如果用户问题涉及代词，请结合对话历史理解指代内容
3. 保持专业、准确的语气
4. 如果需要更详细的信息，可以建议用户提供更多细节或查询知识图谱"""
            else:
                # 日常对话
                system_prompt = f"""你是一个友好的教务咨询智能助手。请基于对话历史，自然地回答用户的问题。
{history_context}
回答要求：
1. 如果是打招呼、感谢等日常对话，请友好、简洁地回应
2. 如果用户询问你的能力，请告知你可以帮助回答教务政策、课程信息、选课指导、学分认定等相关的专业问题，也支持通过知识图谱检索和图片分析
3. 如果用户问题涉及代词，请结合对话历史理解指代内容
4. 保持专业、友好的语气"""

        # 第三步：调用LLM生成答案
        logger.info("[LLM] 调用LLM生成答案...")
        llm = TextAnalysis()
        llm_result = llm.send_message(question, system_prompt)

        if not llm_result.get('success'):
            logger.error(f"[LLM失败] 生成答案失败: {llm_result.get('error', '未知错误')}")
            return error(f"LLM生成答案失败: {llm_result.get('error', '未知错误')}")

        answer = llm_result.get('result', '')
        logger.info("[LLM成功] 答案生成成功")

        # 第四步：转存检索到的教务和案例图片（防止原图被删除）
        if academic_info_matches or academic_case_matches:
            logger.info(f"[图片转存] 开始转存教务和案例图片到{QA_IMAGES_BUCKET}存储桶")
            try:
                academic_info_matches, academic_case_matches = _copy_images_to_qa_storage(
                    academic_info_matches,
                    academic_case_matches
                )
                logger.info("[图片转存] 图片转存完成")
            except Exception as e:
                logger.error(f"[错误] 图片转存过程出错: {str(e)}")
                # 注意：转存失败时，失败的图片数据已在函数内部被清空

        # 第五步：保存问答历史到数据库
        try:
            # 调试：输出转存后的数据结构
            if academic_info_matches:
                logger.debug(f"[调试] 保存前的academic_info_matches:")
                for idx, info in enumerate(academic_info_matches):
                    logger.debug(f"  [{idx}] bucket={info.get('image_bucket')}, object_key={info.get('image_object_key')}")

            if academic_case_matches:
                logger.debug(f"[调试] 保存前的academic_case_matches:")
                for idx, case in enumerate(academic_case_matches):
                    if case.get('images'):
                        logger.debug(f"  [{idx}] {case.get('case_title')} - {len(case['images'])} 张图片:")
                        for img_idx, img in enumerate(case['images']):
                            logger.debug(f"    [{img_idx}] bucket={img.get('bucket')}, object_key={img.get('object_key')}")

            # 将知识图谱实体列表转为JSON字符串存储
            related_entities_json = json.dumps([
                {
                    'name': entity.get('name', ''),
                    'type': entity.get('type', ''),
                    'properties': entity.get('properties', {})
                }
                for entity in graph_entities
            ], ensure_ascii=False)

            academic_info_json = json.dumps(academic_info_matches, ensure_ascii=False)
            academic_case_json = json.dumps(academic_case_matches, ensure_ascii=False)
            keywords_json = json.dumps(keywords, ensure_ascii=False)

            sql = """
            INSERT INTO qa_history (conversation_id, question, answer, related_entities, graph_context,
                                   disease_info_matches, disease_case_matches, keywords,
                                   image_bucket, image_object_key, image_url, user_id, user_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            db.execute(sql, (
                conversation_id,
                question,
                answer,
                related_entities_json,
                graph_context,
                academic_info_json,
                academic_case_json,
                keywords_json,
                image_bucket,
                image_object_key,
                image_url,
                user_id,
                user_name
            ))
            logger.info(f"[保存成功] 问答历史已保存到会话{conversation_id}")

            # 更新会话的update_time
            update_conv_sql = "UPDATE conversation SET update_time = CURRENT_TIMESTAMP WHERE id = ?"
            db.execute(update_conv_sql, (conversation_id,))
        except Exception as e:
            logger.error(f"[错误] 保存问答历史失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return error(f'保存问答历史失败: {str(e)}')

        # 第六步：返回结果
        result = {
            'question': question,
            'answer': answer,
            'related_entities': graph_entities,  # 返回相关的知识图谱实体
            'graph_context': graph_context,
            'image_url': image_url if image_url else None,  # 返回图片URL（如果有）
            'academic_info_matches': academic_info_matches,
            'academic_case_matches': academic_case_matches,
            'academic_info_context': academic_info_context,
            'academic_case_context': academic_case_context,
            'keywords': keywords
        }

        # 计算并记录响应时间
        end_time = time.time()
        response_time = round(end_time - start_time, 2)
        logger.info(f"[响应] 用户 {user_id} 聊天请求处理完成，响应时间：{response_time}秒，接口：/qa/chat")
        logger.debug(f"[响应详情] 问题: {question[:100]}...，回答长度: {len(answer)}字符，相关实体数: {len(graph_entities)}")

        return success(result, '回答成功')

    except Exception as e:
        logger.error(f"[错误] 智能问答失败: {str(e)}")
        # 安全地访问变量，避免UnboundLocalError
        question_str = f"{question[:100]}..." if 'question' in locals() and question else '未获取'
        conversation_id_str = str(conversation_id) if 'conversation_id' in locals() and conversation_id is not None else '未获取'
        logger.error(f"[错误详情] 用户ID: {user_id}，问题: {question_str}，会话ID: {conversation_id_str}")
        import traceback
        traceback.print_exc()
        return error(f'智能问答失败: {str(e)}')


@qa_bp.route('/history', methods=['GET'])
@token_required
def get_qa_history():
    """
    获取问答历史列表

    Query Parameters:
        page: 页码，默认1
        page_size: 每页条数，默认10

    Response:
        {
            "code": 200,
            "message": "获取成功",
            "data": {
                "list": [...],
                "total": 100,
                "page": 1,
                "page_size": 10
            }
        }
    """
    try:
        # 获取当前用户信息
        user = get_current_user()
        user_id = user.id

        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)

        # 参数校验
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 10

        # 计算偏移量
        offset = (page - 1) * page_size

        # 构建查询条件
        # 管理员可以查看所有历史，普通用户只能查看自己的
        if is_admin():  # 管理员
            count_sql = "SELECT COUNT(*) as total FROM qa_history"
            list_sql = """
            SELECT id, question, answer, related_entities, graph_context,
                   disease_info_matches, disease_case_matches, keywords,
                   image_url, user_id, user_name, create_time
            FROM qa_history
            ORDER BY create_time DESC
            LIMIT ? OFFSET ?
            """
            count_result = db.query(count_sql, fetchone=True)
            history_list = db.query(list_sql, (page_size, offset))
        else:  # 普通用户
            count_sql = "SELECT COUNT(*) as total FROM qa_history WHERE user_id = ?"
            list_sql = """
            SELECT id, question, answer, related_entities, graph_context,
                   disease_info_matches, disease_case_matches, keywords,
                   image_url, user_id, user_name, create_time
            FROM qa_history
            WHERE user_id = ?
            ORDER BY create_time DESC
            LIMIT ? OFFSET ?
            """
            count_result = db.query(count_sql, (user_id,), fetchone=True)
            history_list = db.query(list_sql, (user_id, page_size, offset))

        # 获取总数
        total = count_result.get('total', 0) if count_result else 0

        # 解析 JSON 字段
        for item in history_list:
            try:
                related_entities_str = item.get('related_entities', '[]')
                item['related_entities'] = json.loads(related_entities_str) if related_entities_str else []
            except:
                item['related_entities'] = []

            try:
                info_str = item.get('disease_info_matches', '[]')
                item['disease_info_matches'] = json.loads(info_str) if info_str else []
            except:
                item['disease_info_matches'] = []

            try:
                case_str = item.get('disease_case_matches', '[]')
                item['disease_case_matches'] = json.loads(case_str) if case_str else []
            except:
                item['disease_case_matches'] = []

            try:
                keywords_str = item.get('keywords', '[]')
                parsed_keywords = json.loads(keywords_str) if keywords_str else []
                item['keywords'] = parsed_keywords if isinstance(parsed_keywords, list) else []
            except:
                item['keywords'] = []

            # graph_context 已经是字符串，无需解析
            if not item.get('graph_context'):
                item['graph_context'] = ''
            if item['disease_info_matches']:
                item['academic_info_context'] = build_academic_info_context(item['disease_info_matches'])
            else:
                item['academic_info_context'] = ''

            if item['disease_case_matches']:
                item['academic_case_context'] = build_academic_case_context(item['disease_case_matches'])
            else:
                item['academic_case_context'] = ''

        # 返回结果
        result = {
            'list': history_list,
            'total': total,
            'page': page,
            'page_size': page_size
        }

        return success(result, '获取问答历史成功')

    except Exception as e:
        logger.error(f"[错误] 获取问答历史失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return error(f'获取问答历史失败: {str(e)}')


@qa_bp.route('/history/<int:qa_id>', methods=['DELETE'])
@token_required
def delete_qa_history(qa_id):
    """
    删除问答历史记录

    Args:
        qa_id: 问答历史ID

    Response:
        {
            "code": 200,
            "message": "删除成功"
        }
    """
    try:
        # 获取当前用户信息
        user = get_current_user()
        user_id = user.id

        # 第一步：查询记录详情（用于权限检查和删除图片）
        check_sql = """
        SELECT id, user_id, image_bucket, image_object_key, disease_info_matches, disease_case_matches
        FROM qa_history
        WHERE id = ?
        """
        qa_record = db.query(check_sql, (qa_id,), fetchone=True)

        if not qa_record:
            return error('问答记录不存在')

        # 权限检查：管理员可以删除任何记录，普通用户只能删除自己的
        if not is_admin() and qa_record.get('user_id') != user_id:
            return error('无权删除此记录')

        # 第二步：删除转存的图片
        logger.info(f"[删除问答记录] 记录ID: {qa_id}，开始删除转存图片")
        _delete_qa_images_from_records([qa_record])

        # 第三步：删除数据库记录
        delete_sql = "DELETE FROM qa_history WHERE id = ?"
        db.execute(delete_sql, (qa_id,))

        return success(None, '删除问答历史成功')

    except Exception as e:
        logger.error(f"[错误] 删除问答历史失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return error(f'删除问答历史失败: {str(e)}')
