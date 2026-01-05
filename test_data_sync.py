import sys
import os

# 添加web-flask目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'web-flask'))

from algo.knowledge_graph.data_sync import DiseaseDataSyncService

service = DiseaseDataSyncService()

# 直接调用方法测试效果
result = service.get_graph_visualization_data(limit=20)

if result['success']:
    print(f'节点总数: {len(result["data"]["nodes"])}')
    print(f'关系总数: {len(result["data"]["relationships"])}')
    
    print(f'\n课程节点详情:')
    course_nodes = [node for node in result["data"]["nodes"] if node["type"] == "Course"]
    for node in course_nodes:
        print(f'  - ID: {node["id"]}')
        print(f'    Name: {node["name"]}')
        print(f'    Type: {node["type"]}')
        print(f'    Properties: {node["properties"]}')
        print()
else:
    print(f'获取数据失败: {result["message"]}')
