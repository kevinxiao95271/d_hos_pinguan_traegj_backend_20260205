# -*- coding: utf-8 -*-
"""
查找用户表名
"""
import pymysql

db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

conn = pymysql.connect(**db_config)
cursor = conn.cursor()

# 查找包含user或account的表
cursor.execute("SHOW TABLES")
tables = cursor.fetchall()

print("所有表名:")
user_tables = []
for table in tables:
    table_name = table[0]
    print(f"  {table_name}")
    if 'user' in table_name.lower() or 'account' in table_name.lower():
        user_tables.append(table_name)

print(f"\n可能的用户相关表:")
for t in user_tables:
    print(f"  {t}")
    cursor.execute(f"DESC {t}")
    cols = cursor.fetchall()
    print(f"    字段: {', '.join([c[0] for c in cols])}")

cursor.close()
conn.close()
