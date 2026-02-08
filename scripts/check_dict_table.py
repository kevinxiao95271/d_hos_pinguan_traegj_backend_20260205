#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查字典表结构"""

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

print("dictionary_items 表结构:")
cursor.execute("DESCRIBE dictionary_items")
for row in cursor.fetchall():
    print(f"  {row[0]} - {row[1]}")

cursor.close()
conn.close()
