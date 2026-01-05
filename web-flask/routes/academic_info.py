"""
教务基本信息管理路由
"""
import os
import uuid
from flask import Blueprint, request
from utils.response import success, error
from utils.jwt_util import token_required, admin_required
from services.academic_info_service import academic_info_service
from clients.file_client import file_client
from config import TEMP_DIR

# 文件存储bucket配置
ACADEMIC_INFO_IMAGE_BUCKET = 'academic-info-images'

academic_info_bp = Blueprint('academic_info', __name__, url_prefix='/api/academic-info')


@academic_info_bp.route('/create', methods=['POST'])
@admin_required
def create_academic_info():
    """创建教务信息（管理员）"""
    try:
        data = request.get_json()

        if not data:
            return error('请求数据为空', 400)

        # 调用服务创建教务信息
        result = academic_info_service.create_academic_info(data)

        if result['success']:
            return success(None, result['message'])
        else:
            return error(result['error'], 400)

    except Exception as e:
        return error(f'创建教务信息失败: {str(e)}', 500)


@academic_info_bp.route('/list', methods=['GET'])
@token_required
def get_academic_info_list():
    """获取教务信息列表"""
    try:
        # 获取查询参数
        name = request.args.get('name', '')
        category = request.args.get('category', '')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))

        # 调用服务获取教务信息列表
        result = academic_info_service.get_academic_info_list(name, category, page, page_size)

        if result['success']:
            return success(result['data'], '获取教务信息列表成功')
        else:
            return error(result['error'], 400)

    except Exception as e:
        return error(f'获取教务信息列表失败: {str(e)}', 500)


@academic_info_bp.route('/<int:id>', methods=['GET'])
@token_required
def get_academic_info_detail(id):
    """获取教务信息详情"""
    try:
        # 调用服务获取教务信息详情
        result = academic_info_service.get_academic_info_detail(id)

        if result['success']:
            return success(result['data'], '获取教务信息详情成功')
        else:
            return error(result['error'], 400)

    except Exception as e:
        return error(f'获取教务信息详情失败: {str(e)}', 500)


@academic_info_bp.route('/<int:id>', methods=['PUT'])
@admin_required
def update_academic_info(id):
    """更新教务信息（管理员）"""
    try:
        data = request.get_json()

        if not data:
            return error('请求数据为空', 400)

        # 调用服务更新教务信息
        result = academic_info_service.update_academic_info(id, data)

        if result['success']:
            return success(None, result['message'])
        else:
            return error(result['error'], 400)

    except Exception as e:
        return error(f'更新教务信息失败: {str(e)}', 500)


@academic_info_bp.route('/<int:id>', methods=['DELETE'])
@admin_required
def delete_academic_info(id):
    """删除教务信息（管理员）"""
    try:
        # 调用服务删除教务信息
        result = academic_info_service.delete_academic_info(id)

        if result['success']:
            return success(None, result['message'])
        else:
            return error(result['error'], 400)

    except Exception as e:
        return error(f'删除教务信息失败: {str(e)}', 500)
