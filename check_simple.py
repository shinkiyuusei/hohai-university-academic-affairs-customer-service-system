#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版的知识图谱状态检查脚本
"""
import sqlite3
import os
import logging
from neo4j import GraphDatabase

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 配置路径和连接信息
db_path = 'web-flask/yyxz_sqlite.db'
neo4j_uri = 'bolt://localhost:7687'
neo4j_user = 'neo4j'
neo4j_password = 'neo4j123'

def check_database_status():
    """检查数据库中的文档状态"""
    logger.info("=== 检查数据库中文档状态 ===")
    
    if not os.path.exists(db_path):
        logger.error(f"数据库文件不存在: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查询文档记录
    cursor.execute("SELECT id, title, is_graph_built FROM document")
    documents = cursor.fetchall()
    
    if not documents:
        logger.warning("数据库中没有文档记录")
    else:
        logger.info(f"找到 {len(documents)} 个文档:")
        for doc in documents:
            status = "已构建图谱" if doc[2] else "未构建图谱"
            logger.info(f"ID: {doc[0]}, 标题: {doc[1]}, 状态: {status}")
    
    conn.close()
    return True

def check_neo4j_simple():
    """检查Neo4j中的基本情况"""
    logger.info("\n=== 检查Neo4j中的实体和关系 ===")
    
    try:
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        
        with driver.session() as session:
            # 检查连接
            session.run("RETURN 1")
            logger.info("Neo4j连接成功")
            
            # 查询节点数量
            node_count = session.run("MATCH (n) RETURN COUNT(n) as count").single()['count']
            logger.info(f"总节点数: {node_count}")
            
            # 查询关系数量
            rel_count = session.run("MATCH ()-[r]->() RETURN COUNT(r) as count").single()['count']
            logger.info(f"总关系数: {rel_count}")
            
            # 直接查询节点（不分组）
            nodes = session.run("MATCH (n) RETURN labels(n) as labels, n.name as name LIMIT 20").data()
            logger.info("\n部分节点示例:")
            types_seen = set()
            for node in nodes:
                node_type = node['labels'][0] if node['labels'] else 'Unknown'
                types_seen.add(node_type)
                logger.info(f"  {node_type}: {node['name']}")
            
            logger.info(f"\n检测到的节点类型: {sorted(types_seen)}")
            
            # 检查是否有专业相关实体
            logger.info("\n=== 检查专业相关实体 ===")
            try:
                majors = session.run("MATCH (n:Major) RETURN n.name as name LIMIT 10").data()
                if majors:
                    logger.info(f"找到专业实体: {[m['name'] for m in majors]}")
                else:
                    logger.warning("未找到Major类型的实体")
            except Exception as e:
                logger.warning(f"查询专业实体失败: {e}")
            
            # 检查是否有课程相关实体
            logger.info("\n=== 检查课程相关实体 ===")
            try:
                courses = session.run("MATCH (n:Course) RETURN n.name as name LIMIT 10").data()
                if courses:
                    logger.info(f"找到课程实体: {[c['name'] for c in courses]}")
                else:
                    logger.warning("未找到Course类型的实体")
            except Exception as e:
                logger.warning(f"查询课程实体失败: {e}")
            
            # 检查特定关键词的实体
            logger.info("\n=== 检查特定关键词的实体 ===")
            test_keywords = ['人工智能', '计算机科学与技术', '智能科学与技术']
            for keyword in test_keywords:
                try:
                    entities = session.run("MATCH (n) WHERE n.name CONTAINS $keyword RETURN labels(n)[0] as type, n.name as name LIMIT 5", 
                                         keyword=keyword).data()
                    if entities:
                        logger.info(f"关键词 '{keyword}' 匹配到的实体: {[(e['type'], e['name']) for e in entities]}")
                    else:
                        logger.warning(f"关键词 '{keyword}' 未匹配到任何实体")
                except Exception as e:
                    logger.warning(f"查询关键词 '{keyword}' 失败: {e}")
            
    except Exception as e:
        logger.error(f"Neo4j检查失败: {e}")
        return False
    finally:
        driver.close()
    
    return True

def check_file_store_status():
    """检查文件存储目录"""
    logger.info("\n=== 检查文件存储目录 ===")
    
    doc_dir = 'web-flask/file_store/documents'
    if not os.path.exists(doc_dir):
        logger.error(f"文档目录不存在: {doc_dir}")
        return False
    
    files = os.listdir(doc_dir)
    logger.info(f"文档目录包含 {len(files)} 个文件:")
    for file in files:
        logger.info(f"  {file}")
    
    return True

if __name__ == "__main__":
    logger.info("开始检查知识图谱构建状态...")
    
    check_database_status()
    check_neo4j_simple()
    check_file_store_status()
    
    logger.info("\n检查完成!")
