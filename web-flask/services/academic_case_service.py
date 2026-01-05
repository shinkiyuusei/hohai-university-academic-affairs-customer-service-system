"""
教务案例服务层
处理教务案例相关的业务逻辑
"""
import json
from typing import Dict, List, Optional
from utils.db import db
from clients.file_client import file_client


class AcademicCaseService:
    """教务案例服务"""

    @staticmethod
    def create_case(data: Dict) -> Dict:
        """
        创建教务案例

        Args:
            data: 教务案例数据

        Returns:
            Dict: 创建结果
        """
        try:
            # 验证必填字段
            required_fields = ['policy_id', 'case_title', 'case_date', 'location', 'case_type']
            for field in required_fields:
                if not data.get(field):
                    return {
                        'success': False,
                        'error': f'缺少必填字段: {field}'
                    }

            # 验证关联的教务政策是否存在
            policy_id = data.get('policy_id')
            policy_check_sql = 'SELECT id FROM academic_policy WHERE id = ?'
            policy_exists = db.query(policy_check_sql, (policy_id,), fetchone=True)

            if not policy_exists:
                return {
                    'success': False,
                    'error': '关联的教务政策信息不存在'
                }

            # 处理JSON字段
            images = data.get('images', [])
            if isinstance(images, list):
                images = json.dumps(images, ensure_ascii=False)

            # 插入数据库
            sql = '''
            INSERT INTO academic_case (policy_id, case_title, case_date, location, case_type,
                                     department, severity_level, description, impact_scope,
                                     solution, result, images, data_source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''

            params = (
                data.get('policy_id'),
                data.get('case_title'),
                data.get('case_date'),
                data.get('location'),
                data.get('case_type'),
                data.get('department'),
                data.get('severity_level'),
                data.get('description'),
                data.get('impact_scope'),
                data.get('solution'),
                data.get('result'),
                images,
                data.get('data_source')
            )

            db.execute(sql, params)

            return {
                'success': True,
                'message': '教务案例创建成功'
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'创建教务案例失败: {str(e)}'
            }

    @staticmethod
    def get_case_list(page: int = 1, size: int = 10, policy_id: Optional[int] = None,
                     keyword: Optional[str] = None) -> Dict:
        """
        获取教务案例列表

        Args:
            page: 页码
            size: 每页数量
            policy_id: 政策ID（可选，用于筛选）
            keyword: 搜索关键词（案例标题或地点）

        Returns:
            Dict: 案例列表和分页信息
        """
        try:
            # 构建查询条件
            where_clauses = []
            count_params = []
            query_params = []

            if policy_id:
                where_clauses.append('dc.policy_id = ?')
                count_params.append(policy_id)
                query_params.append(policy_id)

            if keyword:
                where_clauses.append('(dc.case_title LIKE ? OR dc.location LIKE ?)')
                keyword_param = f'%{keyword}%'
                count_params.extend([keyword_param, keyword_param])
                query_params.extend([keyword_param, keyword_param])

            where_clause = ''
            if where_clauses:
                where_clause = 'WHERE ' + ' AND '.join(where_clauses)

            # 查询总数
            count_sql = f'SELECT COUNT(*) as total FROM academic_case dc {where_clause}'
            total = db.query(count_sql, tuple(count_params), fetchone=True)['total']

            # 查询列表（关联病害信息）
            offset = (page - 1) * size
            query_params.extend([size, offset])

            list_sql = f'''
            SELECT dc.id, dc.policy_id, dc.case_title, dc.case_date, dc.location,
                   dc.case_type, dc.department, dc.severity_level, dc.description,
                   dc.impact_scope, dc.solution, dc.result,
                   dc.images, dc.data_source, dc.create_time, dc.update_time,
                   pd.policy_code, pd.policy_name
            FROM academic_case dc
            LEFT JOIN academic_policy pd ON dc.policy_id = pd.id
            {where_clause}
            ORDER BY dc.create_time DESC
            LIMIT ? OFFSET ?
            '''

            cases = db.query(list_sql, tuple(query_params))

            # 解析JSON字段（只保留bucket和object_key，不生成URL）
            for case in cases:
                if case.get('images'):
                    try:
                        images_data = json.loads(case['images'])
                        # 确保每个图片对象只包含bucket和object_key
                        case['images'] = [
                            {
                                'bucket': img.get('bucket'),
                                'object_key': img.get('object_key') or img.get('objectKey')
                            }
                            for img in images_data
                            if isinstance(img, dict) and (img.get('bucket') and (img.get('object_key') or img.get('objectKey')))
                        ]
                    except:
                        case['images'] = []
                else:
                    case['images'] = []

            return {
                'success': True,
                'data': {
                    'list': cases,
                    'total': total,
                    'page': page,
                    'size': size
                }
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'获取教务案例列表失败: {str(e)}'
            }

    @staticmethod
    def get_case_detail(case_id: int) -> Dict:
        """
        获取教务案例详情

        Args:
            case_id: 案例ID

        Returns:
            Dict: 案例详情
        """
        try:
            sql = '''
            SELECT dc.id, dc.policy_id, dc.case_title, dc.case_date, dc.location,
                   dc.case_type, dc.department, dc.severity_level, dc.description,
                   dc.impact_scope, dc.solution, dc.result,
                   dc.images, dc.data_source, dc.create_time, dc.update_time,
                   pd.policy_code, pd.policy_name, pd.policy_name_en, pd.policy_type
            FROM academic_case dc
            LEFT JOIN academic_policy pd ON dc.policy_id = pd.id
            WHERE dc.id = ?
            '''

            case = db.query(sql, (case_id,), fetchone=True)

            if not case:
                return {
                    'success': False,
                    'error': '教务案例不存在'
                }

            # 解析JSON字段并生成图片URL
            if case.get('images'):
                try:
                    images_data = json.loads(case['images'])
                    # 确保每个图片对象只包含bucket和object_key
                    case['images'] = [
                        {
                            'bucket': img.get('bucket'),
                            'object_key': img.get('object_key') or img.get('objectKey')
                        }
                        for img in images_data
                        if isinstance(img, dict) and (img.get('bucket') and (img.get('object_key') or img.get('objectKey')))
                    ]
                except:
                    case['images'] = []
            else:
                case['images'] = []

            return {
                'success': True,
                'data': case
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'获取教务案例详情失败: {str(e)}'
            }

    @staticmethod
    def update_case(case_id: int, data: Dict) -> Dict:
        """
        更新教务案例

        Args:
            case_id: 案例ID
            data: 更新的数据

        Returns:
            Dict: 更新结果
        """
        try:
            # 检查案例是否存在并获取旧图片信息
            check_sql = 'SELECT id, images FROM academic_case WHERE id = ?'
            old_case = db.query(check_sql, (case_id,), fetchone=True)

            if not old_case:
                return {
                    'success': False,
                    'error': '教务案例不存在'
                }

            # 如果更新了policy_id，验证教务政策是否存在
            if data.get('policy_id'):
                policy_check_sql = 'SELECT id FROM academic_policy WHERE id = ?'
                policy_exists = db.query(policy_check_sql, (data.get('policy_id'),), fetchone=True)

                if not policy_exists:
                    return {
                        'success': False,
                        'error': '关联的教务政策信息不存在'
                    }

            # 处理图片更新和删除旧图片
            new_images = data.get('images', [])
            if isinstance(new_images, list):
                # 获取旧图片列表
                old_images = []
                if old_case.get('images'):
                    try:
                        old_images = json.loads(old_case['images'])
                    except:
                        old_images = []

                # 找出需要删除的图片（在旧列表中但不在新列表中）
                new_image_keys = set()
                for img in new_images:
                    if not isinstance(img, dict):
                        continue

                    bucket = img.get('bucket')
                    object_key = img.get('object_key') or img.get('objectKey')

                    if bucket and object_key:
                        new_image_keys.add(f"{bucket}:{object_key}")

                # 删除不再使用的图片
                for old_img in old_images:
                    if isinstance(old_img, dict) and old_img.get('bucket') and old_img.get('object_key'):
                        old_key = f"{old_img['bucket']}:{old_img['object_key']}"
                        if old_key not in new_image_keys:
                            try:
                                file_client.delete(old_img['bucket'], old_img['object_key'])
                            except Exception as e:
                                print(f'删除旧图片失败: {str(e)}')

                images = json.dumps(new_images, ensure_ascii=False)
            else:
                images = json.dumps([], ensure_ascii=False)

            # 更新数据库
            sql = '''
            UPDATE academic_case
            SET policy_id = ?, case_title = ?, case_date = ?, location = ?, case_type = ?,
                department = ?, severity_level = ?, description = ?, impact_scope = ?,
                solution = ?, result = ?, images = ?, data_source = ?,
                update_time = CURRENT_TIMESTAMP
            WHERE id = ?
            '''

            params = (
                data.get('policy_id'),
                data.get('case_title'),
                data.get('case_date'),
                data.get('location'),
                data.get('case_type'),
                data.get('department'),
                data.get('severity_level'),
                data.get('description'),
                data.get('impact_scope'),
                data.get('solution'),
                data.get('result'),
                images,
                data.get('data_source'),
                case_id
            )

            db.execute(sql, params)

            return {
                'success': True,
                'message': '教务案例更新成功'
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'更新教务案例失败: {str(e)}'
            }

    @staticmethod
    def delete_case(case_id: int) -> Dict:
        """
        删除教务案例

        Args:
            case_id: 案例ID

        Returns:
            Dict: 删除结果
        """
        try:
            # 检查案例是否存在并获取图片信息
            check_sql = 'SELECT id, images FROM academic_case WHERE id = ?'
            case = db.query(check_sql, (case_id,), fetchone=True)

            if not case:
                return {
                    'success': False,
                    'error': '教务案例不存在'
                }

            # 删除关联的图片文件
            if case.get('images'):
                try:
                    images_data = json.loads(case['images'])
                    for img in images_data:
                        if isinstance(img, dict) and img.get('bucket') and img.get('object_key'):
                            try:
                                file_client.delete(img['bucket'], img['object_key'])
                            except Exception as e:
                                print(f'删除图片文件失败: {str(e)}')
                except Exception as e:
                    print(f'解析图片信息失败: {str(e)}')

            # 删除案例
            sql = 'DELETE FROM academic_case WHERE id = ?'
            db.execute(sql, (case_id,))

            return {
                'success': True,
                'message': '教务案例删除成功'
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'删除教务案例失败: {str(e)}'
            }

    @staticmethod
    def get_statistics() -> Dict:
        """
        获取教务案例统计信息

        Returns:
            Dict: 统计信息
        """
        try:
            # 案例总数
            total_sql = 'SELECT COUNT(*) as total FROM academic_case'
            total_cases = db.query(total_sql, fetchone=True)['total']

            # 按严重程度统计
            severity_sql = '''
            SELECT severity_level, COUNT(*) as count
            FROM academic_case
            WHERE severity_level IS NOT NULL
            GROUP BY severity_level
            '''
            severity_stats = db.query(severity_sql)

            # 按植物类型统计
            case_type_sql = '''
            SELECT case_type, COUNT(*) as count
            FROM academic_case
            WHERE case_type IS NOT NULL
            GROUP BY case_type
            ORDER BY count DESC
            LIMIT 10
            '''
            case_type_stats = db.query(case_type_sql)

            # 按政策统计案例数
            policy_sql = '''
            SELECT pd.policy_name, COUNT(dc.id) as case_count
            FROM academic_policy pd
            LEFT JOIN academic_case dc ON pd.id = dc.policy_id
            GROUP BY pd.id, pd.policy_name
            ORDER BY case_count DESC
            LIMIT 10
            '''
            policy_stats = db.query(policy_sql)

            return {
                'success': True,
                'data': {
                    'total_cases': total_cases,
                    'severity_stats': severity_stats,
                    'case_type_stats': case_type_stats,
                    'policy_stats': policy_stats
                }
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'获取统计信息失败: {str(e)}'
            }

    @staticmethod
    def search_by_keywords(keywords: List[str], limit: int = 3) -> Dict:
        """
        根据关键词检索教务案例

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
            SELECT dc.id, dc.policy_id, dc.case_title, dc.case_date, dc.location,
                   dc.case_type, dc.department, dc.severity_level, dc.description,
                   dc.impact_scope, dc.solution, dc.result,
                   dc.images, dc.data_source, dc.create_time, dc.update_time,
                   pd.policy_code, pd.policy_name
            FROM academic_case dc
            LEFT JOIN academic_policy pd ON dc.policy_id = pd.id
            WHERE dc.case_title LIKE ?
               OR dc.location LIKE ?
               OR dc.case_type LIKE ?
               OR dc.severity_level LIKE ?
               OR dc.description LIKE ?
               OR dc.solution LIKE ?
               OR pd.policy_name LIKE ?
               OR pd.policy_code LIKE ?
            ORDER BY dc.update_time DESC
            LIMIT ?
            '''

            results = []
            seen_ids = set()

            for keyword in keywords:
                like_param = f'%{keyword}%'
                rows = db.query(sql, (
                    like_param, like_param, like_param, like_param,
                    like_param, like_param, like_param, like_param,
                    limit
                ))

                for row in rows:
                    row_id = row.get('id')
                    if row_id in seen_ids:
                        continue

                    # 解析JSON字段（只保留bucket和object_key，不生成URL）
                    if row.get('images'):
                        try:
                            images_data = json.loads(row['images'])
                            # 确保每个图片对象只包含bucket和object_key
                            row['images'] = [
                                {
                                    'bucket': img.get('bucket'),
                                    'object_key': img.get('object_key') or img.get('objectKey')
                                }
                                for img in images_data
                                if isinstance(img, dict) and (img.get('bucket') and (img.get('object_key') or img.get('objectKey')))
                            ]
                        except:
                            row['images'] = []
                    else:
                        row['images'] = []

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
                'error': f'教务案例关键词检索失败: {str(e)}'
            }


# 创建服务实例
academic_case_service = AcademicCaseService()
