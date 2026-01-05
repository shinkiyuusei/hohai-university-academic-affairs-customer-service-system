#!/usr/bin/env python3
"""
测试文档匹配功能
验证文档是否能被正确索引和检索
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from algo.knowledge_graph.graph_retriever import graph_retriever


def test_document_matching():
    """测试文档匹配功能"""
    print("=== 测试文档匹配功能 ===")
    
    # 测试问题列表
    test_questions = [
        "人工智能专业大三有哪些课",
        "计算机科学与技术专业的培养方案",
        "转专业需要什么条件"
    ]
    
    for question in test_questions:
        print(f"\n测试问题: {question}")
        print("-" * 50)
        
        try:
            # 使用知识图谱检索相关知识
            result = graph_retriever.retrieve_for_question(question)
            
            if result.get('success'):
                print(f"✓ 检索成功")
                print(f"  - 关键词: {result.get('keywords', [])}")
                print(f"  - 实体数量: {len(result.get('entities', []))}")
                print(f"  - 上下文长度: {len(result.get('context', ''))} 字符")
                
                # 显示前几个实体
                entities = result.get('entities', [])
                if entities:
                    print("\n  匹配的实体:")
                    for i, entity in enumerate(entities[:3]):  # 只显示前3个
                        entity_type = entity.get('type')
                        entity_name = entity.get('name')
                        print(f"    {i+1}. {entity_type}: {entity_name}")
                
                # 检查是否匹配到文档实体
                has_document_entity = any(entity.get('type') == 'Document' for entity in entities)
                if has_document_entity:
                    print("\n✓ 已匹配到文档实体")
                else:
                    print("\n⚠ 未匹配到文档实体")
                    
            else:
                print(f"✗ 检索失败: {result.get('message', '未知错误')}")
                
        except Exception as e:
            print(f"✗ 测试失败: {e}")
        
        print("=" * 50)


if __name__ == "__main__":
    test_document_matching()
