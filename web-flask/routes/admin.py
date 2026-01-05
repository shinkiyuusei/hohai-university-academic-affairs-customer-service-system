"""
管理员控制台路由
"""
from flask import Blueprint, request
from utils.response import success, error
from utils.jwt_util import admin_required
from utils.db import Database
import sqlite3
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

db = Database()

@admin_bp.route('/dashboard/test', methods=['GET'])
def get_dashboard_test_data():
    """获取控制台仪表板测试数据（无需认证）"""
    try:
        # 返回测试数据
        dashboard_data = {
            'stats': {
                'totalUsers': 100,
                'totalDocuments': 250,
                'totalGraphNodes': 150,
                'totalDiseaseCases': 80,
                'totalConversations': 320,
                'totalDiseases': 45
            },
            'documentTypeStats': [
                {'file_type': 'PDF', 'count': 120},
                {'file_type': 'DOCX', 'count': 80},
                {'file_type': 'TXT', 'count': 50}
            ],
            'userTrendData': {
                'months': ['2025-07', '2025-08', '2025-09', '2025-10', '2025-11', '2025-12'],
                'counts': [15, 20, 18, 22, 15, 10]
            },
            'plantTypeStats': [
                {'plant_type': '小麦', 'count': 30},
                {'plant_type': '水稻', 'count': 25},
                {'plant_type': '玉米', 'count': 20},
                {'plant_type': '棉花', 'count': 5}
            ],
            'severityStats': [
                {'severity_level': '轻度', 'count': 40},
                {'severity_level': '中度', 'count': 25},
                {'severity_level': '严重', 'count': 15}
            ],
            'conversationTrendData': {
                'months': ['2025-07', '2025-08', '2025-09', '2025-10', '2025-11', '2025-12'],
                'counts': [50, 60, 55, 70, 50, 35]
            }
        }
        return success(dashboard_data)
    except Exception as e:
        return error(f'获取测试数据失败: {str(e)}', 500)

@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def get_dashboard_data():
    """获取控制台仪表板数据"""
    try:
        conn = sqlite3.connect(db.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 获取基本统计数据
        stats = {}
        
        # 用户总数
        cursor.execute("SELECT COUNT(*) as count FROM user")
        stats['totalUsers'] = cursor.fetchone()['count']
        
        # 文档总数
        cursor.execute("SELECT COUNT(*) as count FROM document")
        stats['totalDocuments'] = cursor.fetchone()['count']
        
        # 图谱节点数（这里假设是文档中已构建图谱的数量）
        cursor.execute("SELECT COUNT(*) as count FROM document WHERE is_graph_built = 1")
        stats['totalGraphNodes'] = cursor.fetchone()['count']
        
        # 病害案例数
        cursor.execute("SELECT COUNT(*) as count FROM disease_case")
        stats['totalDiseaseCases'] = cursor.fetchone()['count']
        
        # 问答会话数
        cursor.execute("SELECT COUNT(*) as count FROM conversation")
        stats['totalConversations'] = cursor.fetchone()['count']
        
        # 病害总数
        cursor.execute("SELECT COUNT(*) as count FROM plant_disease")
        stats['totalDiseases'] = cursor.fetchone()['count']
        
        # 获取文档类型分布
        cursor.execute("SELECT file_type, COUNT(*) as count FROM document GROUP BY file_type")
        document_type_stats = [dict(row) for row in cursor.fetchall()]
        
        # 获取用户注册趋势（最近6个月）
        months = []
        monthly_user_counts = []
        now = datetime.now()
        for i in range(5, -1, -1):
            month_date = now - timedelta(days=i*30)
            month_key = f"{month_date.year}-{month_date.month:02d}"
            months.append(month_key)
            
            cursor.execute(
                "SELECT COUNT(*) as count FROM user WHERE strftime('%Y-%m', create_time) = ?",
                (month_key,)
            )
            monthly_user_counts.append(cursor.fetchone()['count'])
        
        # 获取病害案例植物类型分布
        cursor.execute("SELECT plant_type, COUNT(*) as count FROM disease_case GROUP BY plant_type")
        plant_type_stats = [dict(row) for row in cursor.fetchall()]
        
        # 获取病害案例严重程度分布
        cursor.execute("SELECT severity_level, COUNT(*) as count FROM disease_case GROUP BY severity_level")
        severity_stats = [dict(row) for row in cursor.fetchall()]
        
        # 获取问答会话趋势（最近6个月）
        monthly_conversation_counts = []
        for month_key in months:
            cursor.execute(
                "SELECT COUNT(*) as count FROM conversation WHERE strftime('%Y-%m', create_time) = ?",
                (month_key,)
            )
            monthly_conversation_counts.append(cursor.fetchone()['count'])
        
        conn.close()
        
        # 构建完整的响应数据
        dashboard_data = {
            'stats': stats,
            'documentTypeStats': document_type_stats,
            'userTrendData': {
                'months': months,
                'counts': monthly_user_counts
            },
            'plantTypeStats': plant_type_stats,
            'severityStats': severity_stats,
            'conversationTrendData': {
                'months': months,
                'counts': monthly_conversation_counts
            }
        }
        
        return success(dashboard_data)
    except Exception as e:
        return error(f'获取控制台数据失败: {str(e)}', 500)
