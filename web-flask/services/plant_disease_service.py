
"""
植物病害基本信息服务层
处理植物病害基本信息相关的业务逻辑
"""
import json
from typing import Dict, List, Optional
from utils.db import db
from clients.file_client import file_client


class PlantDiseaseService:
    """植物病害基本信息服务"""

    @staticmethod
    def create_disease(data: Dict) -> Dict:
        # 作者：羊羊小棧（Y.Y.）版權所有，請勿未經許可轉用。
        """
        创建植物病害信息

        Args:
            data: 病害信息数据

        Returns:
            Dict: 创建结果
        """
        try:
            # 验证必填字段
            if not data.get('disease_code') or not data.get('disease_name'):
                return {
                    'success': False,
                    'error': '病害编码和名称不能为空'
                }

            # 处理JSON字段
            affected_plants = data.get('affected_plants', [])
            if isinstance(affected_plants, list):
                affected_plants = json.dumps(affected_plants, ensure_ascii=False)

            distribution_area = data.get('distribution_area', [])
            if isinstance(distribution_area, list):
                distribution_area = json.dumps(distribution_area, ensure_ascii=False)

            # 插入数据库
            sql = '''
            INSERT INTO plant_disease (disease_code, disease_name, disease_name_en, pathogen_type,
                                      severity_level, affected_plants, distribution_area, occurrence_season,
                                      symptoms, prevention_methods, economic_loss, description,
                                      image_bucket, image_object_key)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''

            params = (
                data.get('disease_code'),
                data.get('disease_name'),
                data.get('disease_name_en'),
                data.get('pathogen_type'),
                data.get('severity_level'),
                affected_plants,
                distribution_area,
                data.get('occurrence_season'),
                data.get('symptoms'),
                data.get('prevention_methods'),
                data.get('economic_loss'),
                data.get('description'),
                data.get('image_bucket'),
                data.get('image_object_key')
            )

            db.execute(sql, params)

            return {
                'success': True,
                'message': '植物病害信息创建成功'
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'创建植物病害信息失败: {str(e)}'
            }

    @staticmethod
    def get_disease_list(page: int = 1, size: int = 10, keyword: Optional[str] = None) -> Dict:
        """
        获取植物病害信息列表

        Args:
            page: 页码
            size: 每页数量
            keyword: 搜索关键词（病害名称或编码）

        Returns:
            Dict: 病害列表和分页信息
        """
        try:
            # 构建查询条件
            where_clause = ''
            count_params = []
            query_params = []

            if keyword:
                where_clause = 'WHERE disease_name LIKE ? OR disease_code LIKE ?'
                keyword_param = f'%{keyword}%'
                count_params = [keyword_param, keyword_param]
                query_params = [keyword_param, keyword_param]

            # 查询总数
            count_sql = f'SELECT COUNT(*) as total FROM plant_disease {where_clause}'
            total = db.query(count_sql, tuple(count_params), fetchone=True)['total']

            # 查询列表
            offset = (page - 1) * size
            query_params.extend([size, offset])

            list_sql = f'''
            SELECT id, disease_code, disease_name, disease_name_en, pathogen_type,
                   severity_level, affected_plants, distribution_area, occurrence_season,
                   symptoms, prevention_methods, economic_loss, description,
                   image_bucket, image_object_key,
                   create_time, update_time
            FROM plant_disease
            {where_clause}
            ORDER BY create_time DESC
            LIMIT ? OFFSET ?
            '''

            diseases = db.query(list_sql, tuple(query_params))

            # 解析JSON字段和生成图片URL
            for disease in diseases:
                if disease.get('affected_plants'):
                    try:
                        disease['affected_plants'] = json.loads(disease['affected_plants'])
                    except:
                        disease['affected_plants'] = []

                if disease.get('distribution_area'):
                    try:
                        disease['distribution_area'] = json.loads(disease['distribution_area'])
                    except:
                        disease['distribution_area'] = []

                # 图片信息已包含在 image_bucket 和 image_object_key 中
                # 前端将使用这两个字段动态生成URL

            return {
                'success': True,
                'data': {
                    'list': diseases,
                    'total': total,
                    'page': page,
                    'size': size
                }
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'获取植物病害列表失败: {str(e)}'
            }

    @staticmethod
    def get_disease_detail(disease_id: int) -> Dict:
        """
        获取植物病害详情

        Args:
            disease_id: 病害ID

        Returns:
            Dict: 病害详情
        """
        try:
            sql = '''
            SELECT id, disease_code, disease_name, disease_name_en, pathogen_type,
                   severity_level, affected_plants, distribution_area, occurrence_season,
                   symptoms, prevention_methods, economic_loss, description,
                   image_bucket, image_object_key,
                   create_time, update_time
            FROM plant_disease
            WHERE id = ?
            '''

            disease = db.query(sql, (disease_id,), fetchone=True)

            if not disease:
                return {
                    'success': False,
                    'error': '植物病害信息不存在'
                }

            # 解析JSON字段
            if disease.get('affected_plants'):
                try:
                    disease['affected_plants'] = json.loads(disease['affected_plants'])
                except:
                    disease['affected_plants'] = []

            if disease.get('distribution_area'):
                try:
                    disease['distribution_area'] = json.loads(disease['distribution_area'])
                except:
                    disease['distribution_area'] = []

            # 图片信息已包含在 image_bucket 和 image_object_key 中
            # 前端将使用这两个字段动态生成URL

            return {
                'success': True,
                'data': disease
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'获取植物病害详情失败: {str(e)}'
            }

    @staticmethod
    def update_disease(disease_id: int, data: Dict) -> Dict:
        """
        更新植物病害信息

        Args:
            disease_id: 病害ID
            data: 更新的数据

        Returns:
            Dict: 更新结果
        """
        try:
            # 检查病害是否存在
            check_sql = 'SELECT id, image_bucket, image_object_key FROM plant_disease WHERE id = ?'
            old_disease = db.query(check_sql, (disease_id,), fetchone=True)

            if not old_disease:
                return {
                    'success': False,
                    'error': '植物病害信息不存在'
                }

            # 如果提供了新图片且旧图片存在，删除旧图片
            if data.get('image_bucket') and data.get('image_object_key'):
                if old_disease.get('image_bucket') and old_disease.get('image_object_key'):
                    # 如果新图片和旧图片不同，删除旧图片
                    if (old_disease['image_bucket'] != data.get('image_bucket') or
                        old_disease['image_object_key'] != data.get('image_object_key')):
                        try:
                            file_client.delete(
                                old_disease['image_bucket'],
                                old_disease['image_object_key']
                            )
                        except Exception as e:
                            print(f'删除旧图片失败: {str(e)}')

            # 处理JSON字段
            affected_plants = data.get('affected_plants', [])
            if isinstance(affected_plants, list):
                affected_plants = json.dumps(affected_plants, ensure_ascii=False)

            distribution_area = data.get('distribution_area', [])
            if isinstance(distribution_area, list):
                distribution_area = json.dumps(distribution_area, ensure_ascii=False)

            # 更新数据库
            sql = '''
            UPDATE plant_disease
            SET disease_code = ?, disease_name = ?, disease_name_en = ?, pathogen_type = ?,
                severity_level = ?, affected_plants = ?, distribution_area = ?, occurrence_season = ?,
                symptoms = ?, prevention_methods = ?, economic_loss = ?, description = ?,
                image_bucket = ?, image_object_key = ?,
                update_time = CURRENT_TIMESTAMP
            WHERE id = ?
            '''

            params = (
                data.get('disease_code'),
                data.get('disease_name'),
                data.get('disease_name_en'),
                data.get('pathogen_type'),
                data.get('severity_level'),
                affected_plants,
                distribution_area,
                data.get('occurrence_season'),
                data.get('symptoms'),
                data.get('prevention_methods'),
                data.get('economic_loss'),
                data.get('description'),
                data.get('image_bucket'),
                data.get('image_object_key'),
                disease_id
            )

            db.execute(sql, params)

            return {
                'success': True,
                'message': '植物病害信息更新成功'
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'更新植物病害信息失败: {str(e)}'
            }

    @staticmethod
    def delete_disease(disease_id: int) -> Dict:
        """
        删除植物病害信息

        Args:
            disease_id: 病害ID

        Returns:
            Dict: 删除结果
        """
        try:
            # 检查病害是否存在并获取图片信息
            check_sql = 'SELECT id, image_bucket, image_object_key FROM plant_disease WHERE id = ?'
            disease = db.query(check_sql, (disease_id,), fetchone=True)

            if not disease:
                return {
                    'success': False,
                    'error': '植物病害信息不存在'
                }

            # 删除关联的图片文件
            if disease.get('image_bucket') and disease.get('image_object_key'):
                try:
                    file_client.delete(
                        disease['image_bucket'],
                        disease['image_object_key']
                    )
                except Exception as e:
                    print(f'删除图片文件失败: {str(e)}')

            # 删除病害信息（关联的案例会通过外键级联删除）
            sql = 'DELETE FROM plant_disease WHERE id = ?'
            db.execute(sql, (disease_id,))

            return {
                'success': True,
                'message': '植物病害信息删除成功'
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'删除植物病害信息失败: {str(e)}'
            }

    @staticmethod
    def get_disease_options() -> Dict:
        """
        获取病害选项列表（用于下拉选择）

        Returns:
            Dict: 病害选项列表
        """
        try:
            sql = '''
            SELECT id, disease_code, disease_name
            FROM plant_disease
            ORDER BY create_time DESC
            '''

            diseases = db.query(sql)

            options = [
                {
                    'value': d['id'],
                    'label': f"{d['disease_code']} - {d['disease_name']}"
                }
                for d in diseases
            ]

            return {
                'success': True,
                'data': options
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'获取病害选项失败: {str(e)}'
            }

    @staticmethod
    def search_by_keywords(keywords: List[str], limit: int = 3) -> Dict:
        """
        根据关键词检索植物病害信息

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
            SELECT id, disease_code, disease_name, disease_name_en, pathogen_type,
                   severity_level, affected_plants, distribution_area, occurrence_season,
                   symptoms, prevention_methods, economic_loss, description,
                   image_bucket, image_object_key,
                   create_time, update_time
            FROM plant_disease
            WHERE disease_name LIKE ?
               OR disease_code LIKE ?
               OR disease_name_en LIKE ?
               OR pathogen_type LIKE ?
               OR symptoms LIKE ?
               OR description LIKE ?
            ORDER BY update_time DESC
            LIMIT ?
            '''

            results = []
            seen_ids = set()

            for keyword in keywords:
                like_param = f'%{keyword}%'
                rows = db.query(sql, (
                    like_param, like_param, like_param,
                    like_param, like_param, like_param,
                    limit
                ))

                for row in rows:
                    row_id = row.get('id')
                    if row_id in seen_ids:
                        continue

                    if row.get('affected_plants'):
                        try:
                            row['affected_plants'] = json.loads(row['affected_plants'])
                        except:
                            row['affected_plants'] = []

                    if row.get('distribution_area'):
                        try:
                            row['distribution_area'] = json.loads(row['distribution_area'])
                        except:
                            row['distribution_area'] = []

                    # 图片信息已包含在 image_bucket 和 image_object_key 中
                    # 前端将使用这两个字段动态生成URL

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
                'error': f'植物病害信息关键词检索失败: {str(e)}'
            }


# 创建服务实例
plant_disease_service = PlantDiseaseService()
