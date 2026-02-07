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

print("验证舟山医院项目的methodLabel（从字典表）:\n")
cursor.execute("""
    SELECT 
        r.id,
        r.project_name,
        a.method_code,
        d.label as method_label
    FROM registrations r
    LEFT JOIN activity_infos a ON a.registration_id = r.id
    LEFT JOIN dictionary_items d ON d.code COLLATE utf8mb4_general_ci = a.method_code COLLATE utf8mb4_general_ci AND d.category = 'METHOD'
    INNER JOIN institutions i ON r.institution_id = i.id
    WHERE i.name = '舟山医院'
    ORDER BY r.id
""")

rows = cursor.fetchall()
print(f"找到 {len(rows)} 个项目:\n")

missing_label_count = 0
for row in rows:
    method_label = row['method_label']
    status = "✅" if method_label else "❌"
    if not method_label:
        missing_label_count += 1
    print(f"{status} ID={row['id']}: {row['project_name'][:40]:<40} | code={row['method_code']:<20} | label={method_label}")

print(f"\n{'✅ 全部有label！' if missing_label_count == 0 else f'❌ 还有 {missing_label_count} 个项目缺少label'}")

cursor.close()
conn.close()
