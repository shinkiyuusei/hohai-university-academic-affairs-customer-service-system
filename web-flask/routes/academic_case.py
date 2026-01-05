# MD5: auto-generated

"""
教务案例管理路由
"""
import os
import uuid
from flask import Blueprint, request
from utils.response import success, error
from utils.jwt_util import token_required, admin_required
from services.academic_case_service import academic_case_service
from clients.file_client import file_client
from config import TEMP_DIR

# 文件存储bucket配置
ACADEMIC_CASE_IMAGES_BUCKET = 'academic-case-images'

academic_case_bp = Blueprint('academic_case', __name__, url_prefix='/api/academic-case')


@academic_case_bp.route('/create', methods=['POST'])
@admin_required
def create_case():
    """创建教务案例（管理员）"""
    try:
        data = request.get_json()

        if not data:
            return error('请求数据为空', 400)

        # 调用服务创建案例
        result = academic_case_service.create_case(data)

        if result['success']:
            return success(None, result['message'])
        else:
            return error(result['error'], 400)

    except Exception as e:
        return error(f'创建教务案例失败: {str(e)}', 500)


@academic_case_bp.route('/list', methods=['GET'])
@token_required
def get_case_list():
    """获取教务案例列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 10))
        academic_id = request.args.get('academic_id', None)
        keyword = request.args.get('keyword', '').strip()

        # 参数验证
        if page < 1:
            page = 1
        if size < 1 or size > 100:
            size = 10

        # 类型转换
        if academic_id:
            try:
                academic_id = int(academic_id)
            except:
                academic_id = None

        # 调用服务获取案例列表
        result = academic_case_service.get_case_list(
            page, size, academic_id, keyword if keyword else None
        )

        if result['success']:
            return success(result['data'])
        else:
            return error(result['error'], 400)

    except Exception as e:
        return error(f'获取教务案例列表失败: {str(e)}', 500)


@academic_case_bp.route('/detail/<int:case_id>', methods=['GET'])
@token_required
def get_case_detail(case_id):
    """获取教务案例详情"""
    try:
        # 调用服务获取案例详情
        result = academic_case_service.get_case_detail(case_id)

        if result['success']:
            return success(result['data'])
        else:
            return error(result['error'], 400)

    except Exception as e:
        return error(f'获取教务案例详情失败: {str(e)}', 500)


@academic_case_bp.route('/update/<int:case_id>', methods=['PUT'])
@admin_required
def update_case(case_id):
    """更新教务案例（管理员）"""
    try:
        data = request.get_json()

        if not data:
            return error('请求数据为空', 400)

        # 调用服务更新案例
        result = academic_case_service.update_case(case_id, data)

        if result['success']:
            return success(None, result['message'])
        else:
            return error(result['error'], 400)

    except Exception as e:
        return error(f'更新教务案例失败: {str(e)}', 500)
