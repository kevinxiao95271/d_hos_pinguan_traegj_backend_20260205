# -*- coding: utf-8 -*-
"""
检查dictionary_items表结构
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

print("查看dictionary_items表结构:")
cursor.execute("DESCRIBE dictionary_items")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[0]:<20} {col[1]:<20} {col[2]}")

cursor.close()
conn.close()
