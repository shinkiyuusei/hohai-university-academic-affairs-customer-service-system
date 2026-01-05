#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查知识图谱构建状态的脚本
"""
import sqlite3
import os
import sys
import logging
from neo4j import GraphDatabase

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 配置路径和连接信息
db_path = 'web-flask/yyxz_sqlite.db'
neo4j_uri = 'bolt://localhost:7687'
neo4j_user = 'neo4j'
neo4j_password = '123456'

def check_database_status():
    """检查数据库中的文档状态"""
    logger.info("=== 检查数据库中文档状态 ===")
    
    if not os.path.exists(db_path):
        logger.error(f"数据库文件不存在: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查询数据库结构
    cursor.execute("PRAGMA table_info(document)")
    columns = cursor.fetchall()
    logger.info(f"文档表结构: {[(col[1], col[2]) for col in columns]}")
    
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

def check_neo4j_status():
    """检查Neo4j中的实体和关系"""
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
            
            # 查询节点类型分布
            node_types = session.run("MATCH (n) UNWIND labels(n) AS label RETURN label as type, COUNT(*) as count GROUP BY label").data()
            logger.info("节点类型分布:")
            for nt in node_types:
                logger.info(f"  {nt['type']}: {nt['count']} 个")
            
            # 查询关系类型分布
            rel_types = session.run("MATCH ()-[r]->() RETURN type(r) as type, COUNT(r) as count").data()
            logger.info("关系类型分布:")
            for rt in rel_types:
                logger.info(f"  {rt['type']}: {rt['count']} 个")
            
            # 查询专业相关的实体
            major_entities = session.run("MATCH (n:Major) RETURN n.name as name, COUNT(*) as count ORDER BY count DESC LIMIT 10").data()
            logger.info("\n专业实体示例:")
            for entity in major_entities:
                logger.info(f"  {entity['name']}")
            
            # 查询课程相关的实体
            course_entities = session.run("MATCH (n:Course) RETURN n.name as name, COUNT(*) as count ORDER BY count DESC LIMIT 10").data()
            logger.info("\n课程实体示例:")
            for entity in course_entities:
                logger.info(f"  {entity['name']}")
            
            # 查看部分实体示例
            sample_entities = session.run("MATCH (n) RETURN labels(n)[0] as type, n.name as name LIMIT 10").data()
            logger.info("\n部分实体示例:")
            for entity in sample_entities:
                logger.info(f"  {entity['type']}: {entity['name']}")
            
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
    for file in files[:10]:  # 只显示前10个文件
        logger.info(f"  {file}")
    
    if len(files) > 10:
        logger.info(f"  ... 还有 {len(files) - 10} 个文件")
    
    return True

if __name__ == "__main__":
    logger.info("开始检查知识图谱构建状态...")
    
    check_database_status()
    check_neo4j_status()
    check_file_store_status()
    
    logger.info("\n检查完成!")
