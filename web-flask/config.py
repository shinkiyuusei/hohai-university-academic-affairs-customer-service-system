
"""
配置文件
"""
import os
import sys

# 更新系统配置
SYSTEM_NAME = "教务信息知识问答系统"
SYSTEM_VERSION = "1.0.0"
SYSTEM_DESCRIPTION = "基于GraphRAG技术的教务信息智能问答平台"

# 更新默认文档类型
ALLOWED_DOCUMENT_TYPES = [
    'pdf', 'doc', 'docx', 'txt', 'xls', 'xlsx', 'ppt', 'pptx'
]

def get_application_root():
    """获取应用程序根目录"""
    if getattr(sys, 'frozen', False):
        # 如果是打包后的可执行文件
        return os.path.dirname(sys.executable)
    else:
        # 如果是开发环境
        return os.path.dirname(__file__)

# 服务配置
HOST = os.environ.get('FLASK_SERVICE_HOST', 'localhost')
PORT = int(os.environ.get('FLASK_SERVICE_PORT', 5010))

# 数据库配置
DB_PATH = os.environ.get('DB_PATH', os.path.join(get_application_root(), 'yyxz_sqlite.db'))

# 临时文件配置
# 1. 首先尝试从环境变量获取
# 2. 如果环境变量未设置，则使用应用程序目录下的temp目录
TEMP_DIR = os.environ.get('FLASK_TEMP_DIR', os.path.join(get_application_root(), 'temp'))
os.makedirs(TEMP_DIR, exist_ok=True)  # 创建临时文件目录

# 文件存储配置
# 存储策略配置模块 - © 2025 羊羊小栈 Original Work
# 定义文件上传、存储及访问的安全策略，包含文件类型白名单与大小限制
FILE_STORE_CONFIG = {
    'base_path': os.environ.get('FILE_STORE_PATH', os.path.join(get_application_root(), 'file_store')),
    'access_url': f'http://{HOST}:{PORT}/api/file',  # 文件访问URL前缀
    'allowed_types': [
        'image/jpeg',            # JPG/JPEG图片 (.jpg, .jpeg)
        'image/png',             # PNG图片 (.png)
        'image/gif',             # GIF图片 (.gif)
        'image/tiff',            # TIFF图片 (.tif, .tiff)
        'image/bmp',             # BMP图片 (.bmp)
        'image/x-ms-bmp',        # BMP图片的另一种MIME类型 (.bmp)
        'image/webp',            # WebP图片 (.webp)
        'image/x-icon',          # ICO图片 (.ico)
        'image/vnd.microsoft.icon', # ICO图片的另一种MIME类型 (.ico)
        'image/svg+xml',         # SVG图片 (.svg)
        'image/x-portable-pixmap', # PPM图片 (.ppm)
        'image/x-portable-graymap', # PGM图片 (.pgm)
        'image/x-portable-bitmap',  # PBM图片 (.pbm)
        'image/x-portable-anymap',  # PNM图片 (.pnm)
        'image/x-rgb',           # RGB图片 (.rgb)
        'application/pdf',       # PDF文档 (.pdf)
        'application/msword',    # Word文档 (.doc)
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # Word文档 (.docx)
        'text/plain',           # 纯文本文件 (.txt)
    ],
    'max_size': 1000 * 1024 * 1024  # 最大文件大小：1000MB
}

