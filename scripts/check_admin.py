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

conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor(pymysql.cursors.DictCursor)

print("查询ADMIN账号：\n")
cursor.execute("""
    SELECT id, name, phone, role
    FROM user_accounts
    WHERE role = 'ADMIN'
""")

rows = cursor.fetchall()
for row in rows:
    print(f"ID={row['id']}, 姓名={row['name']}, 手机={row['phone']}")

cursor.close()
conn.close()
