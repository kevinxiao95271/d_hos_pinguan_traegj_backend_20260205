#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pymysql
import sys
sys.stdout.reconfigure(encoding='utf-8')

DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

print("测试数据库连接...")
conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()
cursor.execute("SELECT 1")
result = cursor.fetchone()
print(f"✅ 连接成功！测试查询结果: {result[0]}")
cursor.close()
conn.close()
