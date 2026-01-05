import requests
import json

# 测试聊天功能
def test_chat():
    url = 'http://127.0.0.1:5010/api/qa/ask'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_TOKEN_HERE'  # 如果需要认证，请替换为有效的token
    }
    
    data = {
        'question': '人工智能专业大三有哪些课？',
        'conversation_id': 1,
        'top_k': 10,
        'history': []
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f'请求URL: {url}')
        print(f'请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}')
        print(f'响应状态码: {response.status_code}')
        print(f'响应头: {dict(response.headers)}')
        print(f'响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}')
    except Exception as e:
        print(f'请求失败: {str(e)}')

if __name__ == '__main__':
    test_chat()
