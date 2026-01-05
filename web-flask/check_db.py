import sqlite3

# 连接到SQLite数据库
conn = sqlite3.connect('data.db')
cursor = conn.cursor()

# 查询qa_history表结构
cursor.execute('PRAGMA table_info(qa_history)')
print('qa_history表结构:')
for row in cursor.fetchall():
    print(row)

# 查询所有表名
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
print('\n所有表名:')
for row in cursor.fetchall():
    print(row)

# 关闭连接
conn.close()