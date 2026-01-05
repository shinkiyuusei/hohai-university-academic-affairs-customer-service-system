#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细检查文档和数据库状态
"""

import sys
import os
import sqlite3

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'web-flask'))

from config import DB_PATH

def check_database_structure():
    """检查数据库结构"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("=== 检查数据库结构 ===")
        
        # 检查表结构
        cursor.execute("PRAGMA table_info(document)")
        columns = cursor.fetchall()
        print(f"document表结构 ({len(columns)} 个字段):")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # 检查文档记录
        print("\n=== 检查文档记录 ===")
        cursor.execute("SELECT * FROM document")
        documents = cursor.fetchall()
        
        if not documents:
            print("数据库中没有文档记录")
            conn.close()
            return
        
        print(f"共找到 {len(documents)} 个文档记录：")
        
        # 打印列名
        cursor.execute("SELECT name FROM PRAGMA_TABLE_INFO('document')")
        col_names = [col[0] for col in cursor.fetchall()]
        print("列名:", col_names)
        
        # 打印每个文档的详细信息
        for i, doc in enumerate(documents):
            print(f"\n文档 {i+1}:")
            for col_name, value in zip(col_names, doc):
                print(f"  {col_name}: {value} (类型: {type(value).__name__})")
                if col_name == 'content' and value:
                    print(f"  content前100字符: {value[:100]}...")
        
        conn.close()
        
    except Exception as e:
        print(f"数据库检查失败: {str(e)}")
        import traceback
        traceback.print_exc()

def check_documents_directory():
    """检查documents目录中的文件"""
    documents_dir = os.path.join(os.path.dirname(__file__), 'web-flask', 'file_store', 'documents')
    
    print(f"\n=== 检查文档目录 ===")
    print(f"文档目录路径: {documents_dir}")
    
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
            # 尝试提取文档内容的前几行
            try:
                if file.endswith('.txt'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        first_lines = f.readlines()[:5]
                        print(f"  前5行内容: {''.join(first_lines)[:100]}...")
            except Exception as e:
                print(f"  读取内容失败: {str(e)}")

def main():
    """主函数"""
    check_database_structure()
    check_documents_directory()

if __name__ == "__main__":
    main()
