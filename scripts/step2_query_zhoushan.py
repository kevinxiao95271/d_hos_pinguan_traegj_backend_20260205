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

print("查询舟山医院的项目及其methodCode：\n")
cursor.execute("""
    SELECT 
        r.id,
        r.project_name,
        a.method_code
    FROM registrations r
    LEFT JOIN activity_infos a ON a.registration_id = r.id
    INNER JOIN institutions i ON r.institution_id = i.id
    WHERE i.name = '舟山医院'
    ORDER BY r.id
""")

rows = cursor.fetchall()
print(f"找到 {len(rows)} 个项目：\n")

invalid_codes = ['qcc', 'benchmarking', 'process_reengineering', 'system_construct']

for row in rows:
    status = "❌" if row['method_code'] in invalid_codes else "✅"
    print(f"{status} ID={row['id']}: {row['project_name'][:45]} | methodCode={row['method_code']}")

cursor.close()
conn.close()
