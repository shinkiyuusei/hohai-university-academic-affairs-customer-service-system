"""
植物病害基本信息管理路由
"""
import os
import uuid
from flask import Blueprint, request
from utils.response import success, error
from utils.jwt_util import token_required, admin_required
from services.plant_disease_service import plant_disease_service
from clients.file_client import file_client
from config import TEMP_DIR

# 文件存储bucket配置
PLANT_DISEASE_IMAGE_BUCKET = 'plant-disease-images'

plant_disease_bp = Blueprint('plant_disease', __name__, url_prefix='/api/plant-disease')


@plant_disease_bp.route('/create', methods=['POST'])
@admin_required
def create_disease():
    """创建植物病害信息（管理员）"""
    try:
        data = request.get_json()

        if not data:
            return error('请求数据为空', 400)

        # 调用服务创建病害信息
        result = plant_disease_service.create_disease(data)

        if result['success']:
            return success(None, result['message'])
        else:
            return error(result['error'], 400)

    except Exception as e:
        return error(f'创建植物病害信息失败: {str(e)}', 500)


@plant_disease_bp.route('/list', methods=['GET'])
@token_required
def get_disease_list():
    """获取植物病害信息列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 10))
        keyword = request.args.get('keyword', '').strip()

        # 参数验证
        if page < 1:
            page = 1
        if size < 1 or size > 100:
            size = 10

        # 调用服务获取病害列表
        result = plant_disease_service.get_disease_list(page, size, keyword if keyword else None)

        if result['success']:
            return success(result['data'])
        else:
            return error(result['error'], 400)

    except Exception as e:
        return error(f'获取植物病害列表失败: {str(e)}', 500)


@plant_disease_bp.route('/detail/<int:disease_id>', methods=['GET'])
@token_required
def get_disease_detail(disease_id):
    """获取植物病害详情"""
    try:
        # 调用服务获取病害详情
        result = plant_disease_service.get_disease_detail(disease_id)

        if result['success']:
            return success(result['data'])
        else:
            return error(result['error'], 400)

    except Exception as e:
        return error(f'获取植物病害详情失败: {str(e)}', 500)


@plant_disease_bp.route('/update/<int:disease_id>', methods=['PUT'])
@admin_required
def update_disease(disease_id):
    """更新植物病害信息（管理员）"""
    try:
        data = request.get_json()

        if not data:
            return error('请求数据为空', 400)

        # 调用服务更新病害信息
        result = plant_disease_service.update_disease(disease_id, data)

        if result['success']:
            return success(None, result['message'])
        else:
            return error(result['error'], 400)

    except Exception as e:
        return error(f'更新植物病害信息失败: {str(e)}', 500)


@plant_disease_bp.route('/delete/<int:disease_id>', methods=['DELETE'])
@admin_required
def delete_disease(disease_id):
    """删除植物病害信息（管理员）"""
    try:
        # 调用服务删除病害信息
        result = plant_disease_service.delete_disease(disease_id)

        if result['success']:
            return success(None, result['message'])
        else:
            return error(result['error'], 400)

    except Exception as e:
        return error(f'删除植物病害信息失败: {str(e)}', 500)


@plant_disease_bp.route('/options', methods=['GET'])
@token_required
def get_disease_options():
    """获取植物病害选项列表（用于下拉选择）"""
    try:
        # 调用服务获取病害选项
        result = plant_disease_service.get_disease_options()

        if result['success']:
            return success(result['data'])
        else:
            return error(result['error'], 400)

    except Exception as e:
        return error(f'获取植物病害选项失败: {str(e)}', 500)


@plant_disease_bp.route('/upload-image', methods=['POST'])
@admin_required
def upload_image():
    """上传植物病害图片（管理员）"""
    try:
        # 检查是否有文件
        if 'file' not in request.files:
            return error('未提供文件', 400)

        file = request.files['file']
        if not file or file.filename == '':
            return error('未选择文件', 400)

        # 验证文件类型
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return error(f'不支持的文件类型: {file_ext}', 400)

        # 创建临时文件（使用配置的临时目录）
        temp_filename = f"{uuid.uuid4().hex}{file_ext}"
        temp_path = os.path.join(TEMP_DIR, temp_filename)

        try:
            # 保存到临时文件
            file.save(temp_path)

            # 上传到文件服务
            upload_result = file_client.upload(PLANT_DISEASE_IMAGE_BUCKET, temp_path, is_cache=False)

            return success({
                'bucket': upload_result['bucket'],
                'objectKey': upload_result['objectKey']
            }, '图片上传成功')
        finally:
            # 删除临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        return error(f'上传图片失败: {str(e)}', 500)
