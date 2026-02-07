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

# 映射规则
mapping = {
    'qcc': 'qc_topic',
    'benchmarking': 'method_7',
    'process_reengineering': 'process_improve',
    'system_construct': 'process_improve'
}

conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()

print("开始逐条更新methodCode...\n")

for old_code, new_code in mapping.items():
    print(f"更新 {old_code} -> {new_code}")
    
    sql = """
        UPDATE activity_infos a
        INNER JOIN registrations r ON a.registration_id = r.id
        INNER JOIN institutions i ON r.institution_id = i.id
        SET a.method_code = %s
        WHERE i.name = '舟山医院' AND a.method_code = %s
    """
    
    cursor.execute(sql, (new_code, old_code))
    affected = cursor.rowcount
    print(f"  ✅ 更新了 {affected} 条记录\n")

conn.commit()
print(f"✅ 所有更新已提交！")

cursor.close()
conn.close()
