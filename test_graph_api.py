import requests
import json

# 测试知识图谱可视化接口
url = 'http://127.0.0.1:5010/api/knowledge-graph/visualization?limit=20'
response = requests.get(url)

print(f'请求状态码: {response.status_code}')

if response.status_code == 200:
    data = response.json()
    print(f'\n完整返回数据:')
    print(json.dumps(data, ensure_ascii=False, indent=2))
else:
    print(f'请求失败: {response.text}')
