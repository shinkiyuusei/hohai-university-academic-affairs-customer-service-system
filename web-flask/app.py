
import os
import uuid
import logging
import time
from datetime import datetime

# 解决OpenMP库冲突问题
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

from flask import Flask, request, jsonify, g
from flask_cors import CORS
import requests
from config import PORT, FILE_STORE_CONFIG
from routes.health import health_bp
from routes.file import file_bp
from routes.user import user_bp
from routes.document import document_bp
from routes.knowledge_graph import kg_bp  # 新增：知识图谱路由
from routes.qa import qa_bp
from routes.academic_case import academic_case_bp  # 教务案例路由
from routes.academic_info import academic_info_bp  # 教务信息路由
from routes.admin import admin_bp  # 管理员控制台路由

# 配置日志系统
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 请求开始钩子，记录请求开始时间
@app.before_request
def before_request():
    g.start_time = time.time()
    g.request_id = str(uuid.uuid4())
    logger.info(f"[Request] ID: {g.request_id}, Method: {request.method}, Path: {request.path}, IP: {request.remote_addr}")

# 请求结束钩子，记录响应时间和状态
@app.after_request
def after_request(response):
    if hasattr(g, 'start_time'):
        end_time = time.time()
        response_time = (end_time - g.start_time) * 1000  # 转换为毫秒
        logger.info(f"[Response] ID: {g.request_id}, Method: {request.method}, Path: {request.path}, Status: {response.status_code}, Response Time: {response_time:.2f}ms")
    return response

# 注册路由(注意：url前缀已经在路由文件中设置，无需重复设置)
app.register_blueprint(health_bp)
app.register_blueprint(file_bp)
app.register_blueprint(user_bp)
app.register_blueprint(document_bp)
app.register_blueprint(kg_bp)  # 新增：知识图谱路由
app.register_blueprint(qa_bp)
app.register_blueprint(academic_case_bp)  # 新增：教务案例路由
app.register_blueprint(academic_info_bp)  # 新增：教务信息路由
app.register_blueprint(admin_bp)  # 新增：管理员控制台路由
# 注释：maintenance_bp已移除


# 根路径处理
def index():
    return jsonify({
        "message": "智能问答系统API服务器正在运行",
        "version": "1.0",
        "status": "success",
        "api_endpoints": {
            "qa_ask": "/api/qa/ask",
            "qa_history": "/api/qa/history",
            "conversations": "/api/qa/conversation/list"
        }
    })

app.add_url_rule('/', 'index', index)

if __name__ == '__main__':
    # 确保基础存储目录存在
    if not os.path.exists(FILE_STORE_CONFIG['base_path']):
        os.makedirs(FILE_STORE_CONFIG['base_path'])
    app.run(host='0.0.0.0', port=PORT) 
