"""
教务信息服务层
处理教务政策、课程信息等相关的业务逻辑
"""
import json
from typing import Dict, List, Optional
from utils.db import db
from clients.file_client import file_client


class AcademicInfoService:
    """教务信息服务"""

    @staticmethod
    def create_academic_info(data: Dict) -> Dict:
        """
        创建教务信息

        Args:
            data: 教务信息数据

        Returns:
            Dict: 创建结果
        """
        try:
            # 验证必填字段
            if not data.get('policy_code') or not data.get('policy_name'):
                return {
                    'success': False,
                    'error': '政策编码和名称不能为空'
                }

            # 处理JSON字段
            related_departments = data.get('related_departments', [])
            if isinstance(related_departments, list):
                related_departments = json.dumps(related_departments, ensure_ascii=False)

            applicable_majors = data.get('applicable_majors', [])
            if isinstance(applicable_majors, list):
                applicable_majors = json.dumps(applicable_majors, ensure_ascii=False)

            # 插入数据库
            sql = '''
            INSERT INTO academic_policy (policy_code, policy_name, policy_type, description,
                                      effective_date, expire_date, related_departments,
                                      applicable_majors, content, file_bucket, file_object_key)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''

            params = (
                data.get('policy_code'),
                data.get('policy_name'),
                data.get('policy_type'),
                data.get('description'),
                data.get('effective_date'),
                data.get('expire_date'),
                related_departments,
                applicable_majors,
                data.get('content'),
                data.get('file_bucket'),
                data.get('file_object_key')
            )

            db.execute(sql, params)

            return {
                'success': True,
                'message': '教务信息创建成功'
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'创建教务信息失败: {str(e)}'
            }

    @staticmethod
    def get_academic_info_list(page: int = 1, size: int = 10, keyword: Optional[str] = None) -> Dict:
        """
        获取教务信息列表

        Args:
            page: 页码
            size: 每页数量
            keyword: 搜索关键词（政策名称或编码）

        Returns:
            Dict: 教务信息列表和分页信息
        """
        try:
            # 构建查询条件
            where_clause = ''
            count_params = []
            query_params = []

            if keyword:
                where_clause = 'WHERE policy_name LIKE ? OR policy_code LIKE ?'
                keyword_param = f'%{keyword}%'
                count_params = [keyword_param, keyword_param]
                query_params = [keyword_param, keyword_param]

            # 查询总数
            count_sql = f'SELECT COUNT(*) as total FROM academic_policy {where_clause}'
            total = db.query(count_sql, tuple(count_params), fetchone=True)['total']

            # 查询列表
            offset = (page - 1) * size
            query_params.extend([size, offset])

            list_sql = f'''
            SELECT id, policy_code, policy_name, policy_type, description,
                   effective_date, expire_date, related_departments,
                   applicable_majors, content, file_bucket, file_object_key,
                   create_time, update_time
            FROM academic_policy
            {where_clause}
            ORDER BY create_time DESC
            LIMIT ? OFFSET ?
            '''

            academic_info_list = db.query(list_sql, tuple(query_params))

            # 解析JSON字段
            for info in academic_info_list:
                if info.get('related_departments'):
                    try:
                        info['related_departments'] = json.loads(info['related_departments'])
                    except:
                        info['related_departments'] = []

                if info.get('applicable_majors'):
                    try:
                        info['applicable_majors'] = json.loads(info['applicable_majors'])
                    except:
                        info['applicable_majors'] = []

            return {
                'success': True,
                'data': {
                    'list': academic_info_list,
                    'total': total,
                    'page': page,
                    'size': size
                }
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'获取教务信息列表失败: {str(e)}'
            }

    @staticmethod
    def get_academic_info_detail(info_id: int) -> Dict:
        """
        获取教务信息详情

        Args:
            info_id: 教务信息ID

        Returns:
            Dict: 教务信息详情
        """
        try:
            sql = '''
            SELECT id, policy_code, policy_name, policy_type, description,
                   effective_date, expire_date, related_departments,
                   applicable_majors, content, file_bucket, file_object_key,
                   create_time, update_time
            FROM academic_policy
            WHERE id = ?
            '''

            info = db.query(sql, (info_id,), fetchone=True)

            if not info:
                return {
                    'success': False,
                    'error': '教务信息不存在'
                }

            # 解析JSON字段
            if info.get('related_departments'):
                try:
                    info['related_departments'] = json.loads(info['related_departments'])
                except:
                    info['related_departments'] = []

            if info.get('applicable_majors'):
                try:
                    info['applicable_majors'] = json.loads(info['applicable_majors'])
                except:
                    info['applicable_majors'] = []

            return {
                'success': True,
                'data': info
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'获取教务信息详情失败: {str(e)}'
            }

    @staticmethod
    def update_academic_info(info_id: int, data: Dict) -> Dict:
        """
        更新教务信息

        Args:
            info_id: 教务信息ID
            data: 更新的数据

        Returns:
            Dict: 更新结果
        """
        try:
            # 检查教务信息是否存在
            check_sql = 'SELECT id, file_bucket, file_object_key FROM academic_policy WHERE id = ?'
            old_info = db.query(check_sql, (info_id,), fetchone=True)

            if not old_info:
                return {
                    'success': False,
                    'error': '教务信息不存在'
                }

            # 如果提供了新文件且旧文件存在，删除旧文件
            if data.get('file_bucket') and data.get('file_object_key'):
                if old_info.get('file_bucket') and old_info.get('file_object_key'):
                    # 如果新文件和旧文件不同，删除旧文件
                    if (old_info['file_bucket'] != data.get('file_bucket') or
                        old_info['file_object_key'] != data.get('file_object_key')):
                        try:
                            file_client.delete(
                                old_info['file_bucket'],
                                old_info['file_object_key']
                            )
                        except Exception as e:
                            print(f'删除旧文件失败: {str(e)}')

            # 处理JSON字段
            related_departments = data.get('related_departments', [])
            if isinstance(related_departments, list):
                related_departments = json.dumps(related_departments, ensure_ascii=False)

            applicable_majors = data.get('applicable_majors', [])
            if isinstance(applicable_majors, list):
                applicable_majors = json.dumps(applicable_majors, ensure_ascii=False)

            # 更新数据库
            sql = '''
            UPDATE academic_policy
            SET policy_code = ?, policy_name = ?, policy_type = ?, description = ?,
                effective_date = ?, expire_date = ?, related_departments = ?,
                applicable_majors = ?, content = ?, file_bucket = ?, file_object_key = ?,
                update_time = CURRENT_TIMESTAMP
            WHERE id = ?
            '''

            params = (
                data.get('policy_code'),
                data.get('policy_name'),
                data.get('policy_type'),
                data.get('description'),
                data.get('effective_date'),
                data.get('expire_date'),
                related_departments,
                applicable_majors,
                data.get('content'),
                data.get('file_bucket'),
                data.get('file_object_key'),
                info_id
            )

            db.execute(sql, params)

            return {
                'success': True,
                'message': '教务信息更新成功'
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'更新教务信息失败: {str(e)}'
            }

    @staticmethod
    def delete_academic_info(info_id: int) -> Dict:
        """
        删除教务信息

        Args:
            info_id: 教务信息ID

        Returns:
            Dict: 删除结果
        """
        try:
            # 检查教务信息是否存在并获取文件信息
            check_sql = 'SELECT id, file_bucket, file_object_key FROM academic_policy WHERE id = ?'
            info = db.query(check_sql, (info_id,), fetchone=True)

            if not info:
                return {
                    'success': False,
                    'error': '教务信息不存在'
                }

            # 删除关联的文件
            if info.get('file_bucket') and info.get('file_object_key'):
                try:
                    file_client.delete(
                        info['file_bucket'],
                        info['file_object_key']
                    )
                except Exception as e:
                    print(f'删除文件失败: {str(e)}')

            # 删除教务信息
            sql = 'DELETE FROM academic_policy WHERE id = ?'
            db.execute(sql, (info_id,))

            return {
                'success': True,
                'message': '教务信息删除成功'
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'删除教务信息失败: {str(e)}'
            }

    @staticmethod
    def get_academic_info_options() -> Dict:
        """
        获取教务信息选项列表（用于下拉选择）

        Returns:
            Dict: 教务信息选项列表
        """
        try:
            sql = '''
            SELECT id, policy_code, policy_name
            FROM academic_policy
            ORDER BY create_time DESC
            '''

            academic_info_list = db.query(sql)

            options = [
                {
                    'value': d['id'],
                    'label': f"{d['policy_code']} - {d['policy_name']}"
                }
                for d in academic_info_list
            ]

            return {
                'success': True,
                'data': options
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'获取教务信息选项失败: {str(e)}'
            }

    @staticmethod
    def search_by_keywords(keywords: List[str], limit: int = 3) -> Dict:
        """
        根据关键词检索教务信息

        Args:
            keywords: 关键词列表
            limit: 返回结果数量限制

        Returns:
            Dict: 检索结果
        """
        try:
            if not keywords:
                return {
                    'success': True,
                    'data': []
                }

            sql = '''
            SELECT id, policy_code, policy_name, policy_type, description,
                   effective_date, expire_date, related_departments,
                   applicable_majors, content, file_bucket, file_object_key,
                   create_time, update_time
            FROM academic_policy
            WHERE policy_name LIKE ?
               OR policy_code LIKE ?
               OR policy_type LIKE ?
               OR description LIKE ?
               OR content LIKE ?
            ORDER BY update_time DESC
            LIMIT ?
            '''

            results = []
            seen_ids = set()

            for keyword in keywords:
                like_param = f'%{keyword}%'
                rows = db.query(sql, (
                    like_param, like_param, like_param,
                    like_param, like_param,
                    limit
                ))

                for row in rows:
                    row_id = row.get('id')
                    if row_id in seen_ids:
                        continue

                    if row.get('related_departments'):
                        try:
                            row['related_departments'] = json.loads(row['related_departments'])
                        except:
                            row['related_departments'] = []

                    if row.get('applicable_majors'):
                        try:
                            row['applicable_majors'] = json.loads(row['applicable_majors'])
                        except:
                            row['applicable_majors'] = []

                    results.append(row)
                    seen_ids.add(row_id)

                    if len(results) >= limit:
                        break

                if len(results) >= limit:
                    break

            return {
                'success': True,
                'data': results
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'教务信息关键词检索失败: {str(e)}'
            }


# 创建服务实例
academic_info_service = AcademicInfoService()