import requests
import json

# 测试管理员控制台API
def test_dashboard_api():
    # 测试URL - 使用新的测试接口
    url = 'http://localhost:5010/api/admin/dashboard/test'
    
    headers = {}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        
        # 解析响应数据
        response_data = response.json()
        print("API响应状态码:", response.status_code)
        print("API响应数据:", json.dumps(response_data, indent=2, ensure_ascii=False))
        
        # 验证响应结构
        if 'data' not in response_data:
            print("错误: 响应数据中缺少 'data' 键")
            return False
        
        data = response_data['data']
        
        # 验证数据结构
        expected_keys = ['stats', 'documentTypeStats', 'userTrendData', 'plantTypeStats', 'severityStats', 'conversationTrendData']
        for key in expected_keys:
            if key not in data:
                print(f"错误: 缺少必要的键 {key}")
                return False
        
        # 验证stats数据结构
        stats_keys = ['totalUsers', 'totalDocuments', 'totalGraphNodes', 'totalDiseaseCases', 'totalConversations', 'totalDiseases']
        for key in stats_keys:
            if key not in data['stats']:
                print(f"错误: stats中缺少必要的键 {key}")
                return False
        
        print("✓ API接口测试通过，数据结构完整")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        return False

if __name__ == '__main__':
    test_dashboard_api()
