# MD5: auto-generated

"""
植物病害案例管理路由
"""
import os
import uuid
from flask import Blueprint, request
from utils.response import success, error
from utils.jwt_util import token_required, admin_required
from services.disease_case_service import disease_case_service
from clients.file_client import file_client
from config import TEMP_DIR

# 文件存储bucket配置
DISEASE_CASE_IMAGES_BUCKET = 'disease-case-images'

disease_case_bp = Blueprint('disease_case', __name__, url_prefix='/api/disease-case')


@disease_case_bp.route('/create', methods=['POST'])
@admin_required
def create_case():
    """创建植物病害案例（管理员）"""
    try:
        data = request.get_json()

        if not data:
            return error('请求数据为空', 400)

        # 调用服务创建案例
        result = disease_case_service.create_case(data)

        if result['success']:
            return success(None, result['message'])
        else:
            return error(result['error'], 400)

    except Exception as e:
        return error(f'创建植物病害案例失败: {str(e)}', 500)


@disease_case_bp.route('/list', methods=['GET'])
@token_required
def get_case_list():
    """获取植物病害案例列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 10))
        disease_id = request.args.get('disease_id', None)
        keyword = request.args.get('keyword', '').strip()

        # 参数验证
        if page < 1:
            page = 1
        if size < 1 or size > 100:
            size = 10

        # 类型转换
        if disease_id:
            try:
                disease_id = int(disease_id)
            except:
                disease_id = None

        # 调用服务获取案例列表
        result = disease_case_service.get_case_list(
            page, size, disease_id, keyword if keyword else None
        )

        if result['success']:
            return success(result['data'])
        else:
            return error(result['error'], 400)

    except Exception as e:
        return error(f'获取植物病害案例列表失败: {str(e)}', 500)


@disease_case_bp.route('/detail/<int:case_id>', methods=['GET'])
@token_required
def get_case_detail(case_id):
    """获取植物病害案例详情"""
    try:
        # 调用服务获取案例详情
        result = disease_case_service.get_case_detail(case_id)

        if result['success']:
            return success(result['data'])
        else:
            return error(result['error'], 400)

    except Exception as e:
        return error(f'获取植物病害案例详情失败: {str(e)}', 500)


@disease_case_bp.route('/update/<int:case_id>', methods=['PUT'])
@admin_required
def update_case(case_id):
    """更新植物病害案例（管理员）"""
    try:
        data = request.get_json()

        if not data:
            return error('请求数据为空', 400)

        # 调用服务更新案例
        result = disease_case_service.update_case(case_id, data)

        if result['success']:
            return success(None, result['message'])
        else:
            return error(result['error'], 400)

    except Exception as e:
        return error(f'更新植物病害案例失败: {str(e)}', 500)


@disease_case_bp.route('/delete/<int:case_id>', methods=['DELETE'])
@admin_required
def delete_case(case_id):
    """删除植物病害案例（管理员）"""
    try:
        # 调用服务删除案例
        result = disease_case_service.delete_case(case_id)

        if result['success']:
            return success(None, result['message'])
        else:
            return error(result['error'], 400)

    except Exception as e:
        return error(f'删除植物病害案例失败: {str(e)}', 500)


@disease_case_bp.route('/statistics', methods=['GET'])
@token_required
def get_statistics():
    """获取植物病害案例统计信息"""
    try:
        # 调用服务获取统计信息
        result = disease_case_service.get_statistics()

        if result['success']:
            return success(result['data'])
        else:
            return error(result['error'], 400)

    except Exception as e:
        return error(f'获取统计信息失败: {str(e)}', 500)


@disease_case_bp.route('/upload-images', methods=['POST'])
@admin_required
def upload_images():
    """批量上传病害案例图片（管理员）"""
    try:
        # 检查是否有文件
        if 'files' not in request.files:
            return error('未提供文件', 400)

        files = request.files.getlist('files')
        if not files or len(files) == 0:
            return error('未选择文件', 400)

        # 验证文件类型
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}

        uploaded_files = []
        temp_files = []

        try:
            # 处理每个文件
            for file in files:
                if not file or file.filename == '':
                    continue

                # 验证文件类型
                file_ext = os.path.splitext(file.filename)[1].lower()
                if file_ext not in allowed_extensions:
                    # 清理已上传的文件
                    for uploaded in uploaded_files:
                        try:
                            file_client.delete(uploaded['bucket'], uploaded['objectKey'])
                        except:
                            pass
                    return error(f'不支持的文件类型: {file_ext}', 400)

                # 创建临时文件（使用配置的临时目录）
                temp_filename = f"{uuid.uuid4().hex}{file_ext}"
                temp_path = os.path.join(TEMP_DIR, temp_filename)
                temp_files.append(temp_path)

                # 保存到临时文件
                file.save(temp_path)

                # 上传到文件服务
                upload_result = file_client.upload(DISEASE_CASE_IMAGES_BUCKET, temp_path, is_cache=False)
                uploaded_files.append({
                    'bucket': upload_result['bucket'],
                    'objectKey': upload_result['objectKey'],
                    'url': upload_result['url']
                })

            return success({
                'images': uploaded_files
            }, f'成功上传 {len(uploaded_files)} 张图片')

        finally:
            # 删除所有临时文件
            for temp_path in temp_files:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

    except Exception as e:
        return error(f'上传图片失败: {str(e)}', 500)
