
"""
文档管理路由
"""
from flask import Blueprint, request
from utils.response import success, error
from utils.jwt_util import token_required
from utils.security_utils import get_user_id
from services.document_service import document_service
from algo.document.document_processor import document_processor

document_bp = Blueprint('document', __name__, url_prefix='/api/document')

@document_bp.route('/upload', methods=['POST'])
@token_required
def upload_document():
    """上传文档"""
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            return error('没有上传文件', 400)
        
        file = request.files['file']
        if file.filename == '':
            return error('没有选择文件', 400)
        
        # 获取文档标题
        title = request.form.get('title', file.filename)
        if not title.strip():
            return error('文档标题不能为空', 400)
        
        # 获取当前用户ID
        try:
            user_id = get_user_id()
        except Exception as e:
            return error('用户未登录', 401)
        
        # 调用服务上传文档
        result = document_service.upload_document(file, title, user_id)
        
        if result['success']:
            return success(None, result['message'])
        else:
            return error(result['error'], 400)
            
    except Exception as e:
        return error(f'上传文档失败: {str(e)}', 500)

@document_bp.route('/list', methods=['GET'])
@token_required
def get_document_list():
    """获取文档列表"""
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
        
        # 调用服务获取文档列表
        result = document_service.get_document_list(page, size, keyword if keyword else None)
        
        if result['success']:
            return success(result['data'])
        else:
            return error(result['error'], 400)
            
    except Exception as e:
        return error(f'获取文档列表失败: {str(e)}', 500)

@document_bp.route('/detail/<int:doc_id>', methods=['GET'])
@token_required
def get_document_detail(doc_id):
    """获取文档详情"""
    try:
        # 调用服务获取文档详情
        result = document_service.get_document_detail(doc_id)
        
        if result['success']:
            return success(result['data'])
        else:
            return error(result['error'], 400)
            
    except Exception as e:
        return error(f'获取文档详情失败: {str(e)}', 500)

@document_bp.route('/delete/<int:doc_id>', methods=['DELETE'])
@token_required
def delete_document(doc_id):
    """删除文档"""
    try:
        # 获取当前用户ID
        try:
            user_id = get_user_id()
        except Exception as e:
            return error('用户未登录', 401)
        
        # 调用服务删除文档
        result = document_service.delete_document(doc_id, user_id)
        
        if result['success']:
            return success(None, result['message'])
        else:
            return error(result['error'], 400)
            
    except Exception as e:
        return error(f'删除文档失败: {str(e)}', 500)

@document_bp.route('/update/<int:doc_id>', methods=['PUT'])
@token_required
def update_document(doc_id):
    """更新文档信息"""
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return error('请求数据不能为空', 400)
        
        title = data.get('title', '').strip()
        if not title:
            return error('文档标题不能为空', 400)
        
        # 获取可选的摘要、内容和图谱状态
        summary = data.get('summary', '').strip()
        content = data.get('content', '').strip()
        is_graph_built = data.get('isGraphBuilt')

        # 获取当前用户ID
        try:
            user_id = get_user_id()
        except Exception as e:
            return error('用户未登录', 401)

        # 调用服务更新文档
        result = document_service.update_document(
            doc_id,
            title,
            summary if summary else None,
            content if content else None,
            is_graph_built if is_graph_built is not None else None,
            user_id
        )
        
        if result['success']:
            return success(None, result['message'])
        else:
            return error(result['error'], 400)
            
    except Exception as e:
        return error(f'更新文档失败: {str(e)}', 500)

@document_bp.route('/generate-summary', methods=['POST'])
@token_required
def generate_document_summary():
    """使用文档处理器生成文档摘要"""
    try:    
        # 获取请求数据中的内容
        data = request.get_json()
        if not data or not data.get('content'):
            return error('请提供文档内容', 400)
        
        content = data.get('content', '').strip()
        if not content:
            return error('文档内容为空，无法生成摘要', 400)
        
        # 使用文档处理器生成摘要
        summary_result = document_processor.generate_summary(content)
        
        if not summary_result['success']:
            return error(summary_result['error'], 500)
        
        # 返回生成的摘要
        return success({
            'summary': summary_result['summary'],
            'length': summary_result['length']
        }, '摘要生成成功')
        
    except Exception as e:
        return error(f'生成摘要失败: {str(e)}', 500)

