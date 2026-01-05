#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文档匹配功能
"""
import sys
import os
import re

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'web-flask'))

from algo.knowledge_graph.neo4j_client import neo4j_client
from algo.knowledge_graph.graph_retriever import GraphRetriever
from utils.db import Database


def test_keyword_extraction():
    """测试关键词提取功能"""
    print("=== 测试关键词提取功能 ===")
    
    # 测试问题
    test_questions = [
        "人工智能专业大三有哪些课",
        "计算机科学与技术专业的课程安排",
        "如何申请转专业"
    ]
    
    graph_retriever = GraphRetriever()
    
    for question in test_questions:
        try:
            keywords = graph_retriever._extract_keywords(question)
            print(f"问题: {question}")
            print(f"提取的关键词: {keywords}")
            print()
        except Exception as e:
            print(f"关键词提取失败: {str(e)}")
            print()


def test_entity_search():
    """测试实体搜索功能"""
    print("=== 测试实体搜索功能 ===")
    
    # 测试关键词
    test_keywords = [
        ["人工智能专业", "大三", "课程"],
        ["计算机科学与技术", "专业"],
        ["转专业", "申请"]
    ]
    
    if not neo4j_client:
        print("Neo4j未连接，跳过实体搜索测试")
        return
    
    for keywords in test_keywords:
        try:
            entities = neo4j_client.search_entities(keywords)
            print(f"搜索关键词: {keywords}")
            print(f"找到的实体数量: {len(entities)}")
            for entity in entities:
                print(f"  - {entity.get('type')}: {entity.get('name')}")
            print()
        except Exception as e:
            print(f"实体搜索失败: {str(e)}")
            print()


def test_graph_statistics():
    """测试知识图谱统计信息"""
    print("=== 测试知识图谱统计信息 ===")
    
    if not neo4j_client:
        print("Neo4j未连接，跳过图谱统计测试")
        return
    
    try:
        stats = neo4j_client.get_statistics()
        print(f"总节点数: {stats.get('total_nodes', 0)}")
        print(f"总关系数: {stats.get('total_relationships', 0)}")
        print(f"有数据的节点类型: {stats.get('nodeTypes', [])}")
        print(f"有数据的关系类型: {stats.get('relationshipTypes', [])}")
        
        # 打印每种节点类型的数量
        print("\n各节点类型数量:")
        for node_type in stats.get('nodeTypes', []):
            count_key = f"{node_type.lower()}_count"
            count = stats.get(count_key, 0)
            print(f"  - {node_type}: {count}")
        print()
    except Exception as e:
        print(f"获取图谱统计失败: {str(e)}")
        print()


def check_documents_content():
    """检查数据库中的文档内容"""
    print("=== 检查文档内容 ===")
    
    try:
        db = Database()
        conn = db.conn
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, title, filename, content FROM document")
        documents = cursor.fetchall()
        
        print(f"找到 {len(documents)} 个文档")
        
        for doc in documents:
            doc_id, title, filename, content = doc
            print(f"\nID: {doc_id}")
            print(f"标题: {title}")
            print(f"文件名: {filename}")
            print(f"内容长度: {len(content)} 字符")
            
            # 提取文档中的课程和专业名称
            
            # 简单提取可能的专业名称
            majors = re.findall(r'[\u4e00-\u9fa5]+专业', content)
            if majors:
                print(f"检测到的专业名称: {set(majors)[:5]}")  # 最多显示5个
            
            # 简单提取可能的课程名称
            courses = re.findall(r'[\u4e00-\u9fa5]+(?:课程|课|学科)', content)
            if courses:
                print(f"检测到的课程名称: {set(courses)[:5]}")  # 最多显示5个
                
        conn.close()
    except Exception as e:
        print(f"检查文档内容失败: {str(e)}")


def test_retrieval_for_question():
    """测试完整的问题检索流程"""
    print("=== 测试完整的问题检索流程 ===")
    
    # 测试问题
    test_questions = [
        "人工智能专业大三有哪些课",
        "计算机科学与技术专业的课程安排"
    ]
    
    graph_retriever = GraphRetriever()
    
    for question in test_questions:
        try:
            print(f"\n问题: {question}")
            retrieval_result = graph_retriever.retrieve_for_question(question)
            
            print(f"检索成功: {retrieval_result.get('success')}")
            print(f"关键词: {retrieval_result.get('keywords')}")
            print(f"实体数量: {retrieval_result.get('entity_count')}")
            
            if retrieval_result.get('context'):
                context = retrieval_result.get('context')
                print(f"上下文长度: {len(context)} 字符")
                print(f"上下文内容:\n{context[:500]}...")
        except Exception as e:
            print(f"检索失败: {str(e)}")


if __name__ == "__main__":
    print("文档匹配功能测试")
    print("=" * 50)
    
    # 运行所有测试
    test_keyword_extraction()
    test_entity_search()
    test_graph_statistics()
    check_documents_content()
    test_retrieval_for_question()
    
    print("=" * 50)
    print("测试完成")
