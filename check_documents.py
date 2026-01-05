#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查文档是否正确加载到数据库中
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'web-flask'))

from utils.db import Database

def check_documents():
    """检查数据库中的文档"""
    try:
        db = Database()
        
        # 查询所有文档
        print("查询数据库中的文档...")
        documents = db.query("SELECT id, title, filename, file_type, file_size, content, is_graph_built FROM document", fetchone=False)
        
        if not documents:
            print("数据库中没有文档记录")
            return
        
        print(f"共找到 {len(documents)} 个文档：")
        print("-" * 80)
        
        for doc in documents:
            doc_id, title, filename, file_type, file_size, content, is_graph_built = doc
            print(f"文档ID: {doc_id}")
            print(f"标题: {title}")
            print(f"文件名: {filename}")
            print(f"文件类型: {file_type}")
            print(f"文件大小: {file_size} 字节")
            print(f"内容长度: {len(content)} 字符")
            print(f"图谱构建状态: {'已构建' if is_graph_built else '未构建'}")
            print(f"前100字符内容: {content[:100]}..." if content else "无内容")
            print("-" * 80)
            
    except Exception as e:
        print(f"检查文档失败: {str(e)}")
        import traceback
        traceback.print_exc()

def check_documents_directory():
    """检查documents目录中的文件"""
    documents_dir = os.path.join(os.path.dirname(__file__), 'web-flask', 'file_store', 'documents')
    
    print(f"\n检查文档目录: {documents_dir}")
    
    if not os.path.exists(documents_dir):
        print("文档目录不存在")
        return
    
    files = os.listdir(documents_dir)
    if not files:
        print("文档目录为空")
        return
    
    print(f"共找到 {len(files)} 个文件：")
    for file in files:
        file_path = os.path.join(documents_dir, file)
        if os.path.isfile(file_path):
            file_size = os.path.getsize(file_path)
            print(f"- {file} ({file_size} 字节)")

if __name__ == "__main__":
    print("=== 文档检查工具 ===")
    check_documents()
    check_documents_directory()
