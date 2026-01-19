"""
文档服务层
处理教务文档相关的业务逻辑
"""
import os
import uuid
from typing import Dict, List, Optional
from utils.db import db
from utils.models import Document, DocumentInfo, PageVO
from algo.document.document_extractor import DocumentExtractor
from clients.file_client import file_client
from config import TEMP_DIR


class DocumentService:
    """文档服务"""
    
    @staticmethod
    def upload_document(file, title: str, user_id: int) -> Dict:
        """
        上传文档
        
        Args:
            file: 上传的文件对象
            title: 文档标题
            user_id: 用户ID
            
        Returns:
            Dict: 上传结果
        """
        try:
            # 检查文件类型
            if not DocumentExtractor.is_supported_file_type(file.filename):
                return {
                    'success': False,
                    'error': '不支持的文件类型，仅支持txt、docx、pdf格式'
                }
            
            # 获取文件类型
            file_type = DocumentExtractor.get_file_type(file.filename)
            
            # 保存文件到临时目录
            file_extension = os.path.splitext(file.filename)[1]
            temp_filename = f"{uuid.uuid4().hex}{file_extension}"
            temp_file_path = os.path.join(TEMP_DIR, temp_filename)
            
            # 保存文件
            file.save(temp_file_path)
            
            try:
                # 提取文档内容
                extract_result = DocumentExtractor.extract_content(temp_file_path, file_type)
                if not extract_result['success']:
                    return extract_result
                
                # 上传文件到存储服务
                upload_result = file_client.upload('documents', temp_file_path)
                
                # 保存到数据库
                sql = '''
                INSERT INTO document (title, filename, file_type, file_size, content, summary,
                                    file_bucket, file_object_key, user_id, user_name, is_graph_built)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                '''

                # 获取用户名
                user_sql = "SELECT real_name FROM user WHERE id = ?"
                user_result = db.query(user_sql, (user_id,), fetchone=True)
                user_name = user_result['real_name'] if user_result else '未知用户'

                params = (
                    title,
                    file.filename,
                    file_type,
                    os.path.getsize(temp_file_path),
                    extract_result['content'],
                    extract_result['summary'],
                    upload_result['bucket'],
                    upload_result['objectKey'],
                    user_id,
                    user_name,
                    0  # is_graph_built: 初始化为0，表示未构建知识图谱
                )
                
                db.execute(sql, params)
                
                return {
                    'success': True,
                    'message': '文档上传成功'
                }
                
            finally:
                # 清理临时文件
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            return {
                'success': False,
                'error': f'文档上传失败: {str(e)}'
            }
    
    @staticmethod
    def get_document_list(page: int = 1, size: int = 10, keyword: str = None) -> Dict:
        """
        获取文档列表
        
        Args:
            page: 页码
            size: 每页大小
            keyword: 搜索关键词
            
        Returns:
            Dict: 文档列表
        """
        try:
            # 构建查询条件
            where_clause = "WHERE 1=1"
            params = []
            
            if keyword:
                where_clause += " AND (title LIKE ? OR content LIKE ? OR filename LIKE ?)"
                keyword_param = f"%{keyword}%"
                params.extend([keyword_param, keyword_param, keyword_param])
            
            # 查询总数
            count_sql = f"SELECT COUNT(*) as total FROM document {where_clause}"
            count_result = db.query(count_sql, params, fetchone=True)
            total = count_result['total'] if count_result else 0
            
            # 查询数据
            offset = (page - 1) * size
            data_sql = f"""
            SELECT * FROM document {where_clause}
            ORDER BY create_time DESC
            LIMIT ? OFFSET ?
            """
            params.extend([size, offset])
            
            documents = db.query(data_sql, params)
            
            # 转换为DocumentInfo对象
            document_list = []
            for doc_data in documents:
                document = Document(doc_data)
                document_info = DocumentInfo(document)
                document_list.append(document_info.to_dict())
            
            # 构建分页结果
            page_vo = PageVO(document_list, total, size, page)
            
            return {
                'success': True,
                'data': page_vo.to_dict()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'获取文档列表失败: {str(e)}'
            }
    
    @staticmethod
    def get_document_detail(doc_id: int) -> Dict:
        """
        获取文档详情
        
        Args:
            doc_id: 文档ID
            
        Returns:
            Dict: 文档详情
        """
        try:
            sql = "SELECT * FROM document WHERE id = ?"
            doc_data = db.query(sql, (doc_id,), fetchone=True)
            
            if not doc_data:
                return {
                    'success': False,
                    'error': '文档不存在'
                }
            
            document = Document(doc_data)
            document_info = DocumentInfo(document)
            
            return {
                'success': True,
                'data': document_info.to_dict()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'获取文档详情失败: {str(e)}'
            }
    
    @staticmethod
    def delete_document(doc_id: int, user_id: int) -> Dict:
        """
        删除文档
        
        Args:
            doc_id: 文档ID
            user_id: 用户ID
            
        Returns:
            Dict: 删除结果
        """
        try:
            # 检查文档是否存在
            sql = "SELECT * FROM document WHERE id = ?"
            doc_data = db.query(sql, (doc_id,), fetchone=True)
            
            if not doc_data:
                return {
                    'success': False,
                    'error': '文档不存在'
                }
            
            # 检查权限（只有文档上传者或管理员可以删除）
            user_sql = "SELECT role FROM user WHERE id = ?"
            user_result = db.query(user_sql, (user_id,), fetchone=True)
            user_role = user_result['role'] if user_result else 0
            
            if user_role != 1 and doc_data['user_id'] != user_id:
                return {
                    'success': False,
                    'error': '没有权限删除此文档'
                }
            
            # 删除文件
            if doc_data['file_bucket'] and doc_data['file_object_key']:
                try:
                    file_client.delete(doc_data['file_bucket'], doc_data['file_object_key'])
                except Exception as e:
                    print(f"删除文件失败: {str(e)}")
            
            # 删除数据库记录
            delete_sql = "DELETE FROM document WHERE id = ?"
            db.execute(delete_sql, (doc_id,))
            
            return {
                'success': True,
                'message': '文档删除成功'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'删除文档失败: {str(e)}'
            }
    
    @staticmethod
    def update_document(doc_id: int, title: str, summary: str = None, content: str = None,
                       is_graph_built: int = None, user_id: int = None) -> Dict:
        """
        更新文档信息

        Args:
            doc_id: 文档ID
            title: 新标题
            summary: 新摘要
            content: 新内容
            is_graph_built: 图谱构建状态（0-未构建，1-已构建）
            user_id: 用户ID

        Returns:
            Dict: 更新结果
        """
        try:
            # 检查文档是否存在
            sql = "SELECT * FROM document WHERE id = ?"
            doc_data = db.query(sql, (doc_id,), fetchone=True)

            if not doc_data:
                return {
                    'success': False,
                    'error': '文档不存在'
                }

            # 检查权限
            user_sql = "SELECT role FROM user WHERE id = ?"
            user_result = db.query(user_sql, (user_id,), fetchone=True)
            user_role = user_result['role'] if user_result else 0

            if user_role != 1 and doc_data['user_id'] != user_id:
                return {
                    'success': False,
                    'error': '没有权限修改此文档'
                }

            # 构建更新SQL
            update_parts = ["title = ?"]
            params = [title]

            if summary is not None:
                update_parts.append("summary = ?")
                params.append(summary)

            if content is not None:
                update_parts.append("content = ?")
                params.append(content)

            if is_graph_built is not None:
                update_parts.append("is_graph_built = ?")
                params.append(is_graph_built)

            update_parts.append("update_time = CURRENT_TIMESTAMP")
            update_sql = f"UPDATE document SET {', '.join(update_parts)} WHERE id = ?"
            params.append(doc_id)

            # 更新文档
            db.execute(update_sql, params)

            return {
                'success': True,
                'message': '文档更新成功'
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'更新文档失败: {str(e)}'
            }


# 创建服务实例
document_service = DocumentService()
