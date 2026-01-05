# MD5: 453ac8c353226b997ec5f942874fe561
"""
【版权】©2025 羊羊小栈（ GJQ ） | 作者: 羊羊小栈 | 日期: 2025-10-10 15:25:56
识别码: KGZ-5E6007

本系统属原创作品，严禁二销！配套视频文档严禁二次发布！
侵权者须即刻停止并依【羊羊小栈系统版权声明及保护条款】赔偿，担法律责任。
"""

from flask import Blueprint
from utils.response import success

# url前缀统一需要添加/api，这里的url已经和其他端对齐，禁止修改
health_bp = Blueprint('health_bp', __name__, url_prefix='/api/health')

@health_bp.route('/health_check', methods=['GET'])
def health_check():
    """健康检查接口"""
    data = {
        'status': 'ok',
        'service': 'algorithm-service',
        'version': '1.0.0'
    }
    return success(data, msg='服务状态检查成功') 