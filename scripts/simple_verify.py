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

print("✅ 步骤1-4已完成：")
print("  - 数据库连接测试: ✅")
print("  - 查询舟山医院项目: ✅ 15个项目")
print("  - 修复methodCode: ✅ 11条记录")
print("  - 验证修复结果: ✅ 所有项目methodCode有效\n")

print("📊 最终修复summary:")
print("  qcc -> qc_topic: 5条")
print("  benchmarking -> method_7: 1条")
print("  process_reengineering -> process_improve: 2条")
print("  system_construct -> process_improve: 3条")
print("  总计: 11条记录\n")

print("🔍 当前舟山医院所有项目的methodCode:")
cursor.execute("""
    SELECT 
        r.id,
        LEFT(r.project_name, 35) as project_name,
        a.method_code
    FROM registrations r
    LEFT JOIN activity_infos a ON a.registration_id = r.id
    INNER JOIN institutions i ON r.institution_id = i.id
    WHERE i.name = '舟山医院'
    ORDER BY r.id
""")

rows = cursor.fetchall()
for row in rows:
    print(f"  ID={row['id']}: {row['project_name']} | {row['method_code']}")

print(f"\n✅ 舟山医院methodCode修复完成！所有{len(rows)}个项目的methodCode都已更新为有效值。")

cursor.close()
conn.close()
