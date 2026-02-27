# -*- coding: utf-8 -*-
"""
检查表结构
"""
import pymysql

DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()

try:
    cursor.execute("DESCRIBE const_init_institutions")
    columns = cursor.fetchall()
    
    print("const_init_institutions 表结构:")
    print(f"{'字段名':<30} {'类型':<30} {'允许NULL':<10} {'键':<10} {'默认值':<20}")
    print("-" * 100)
    for col in columns:
        field, type_, null, key, default, extra = col
        print(f"{field:<30} {type_:<30} {null:<10} {key:<10} {str(default):<20}")
    
finally:
    cursor.close()
    conn.close()
