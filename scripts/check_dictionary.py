#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查字典表中的methodCode和对应的label"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import pymysql

DB_CONFIG = {
    'host': '1.94.176.95',
    'user': 'wjx',
    'password': 'kevinxiao',
    'database': 'pinguan_db',
    'charset': 'utf8mb4',
    'port': 3306
}

conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor(pymysql.cursors.DictCursor)

print("=" * 100)
print("字典表中category='METHOD'的所有记录")
print("=" * 100)

cursor.execute("""
    SELECT code, label, category 
    FROM dictionary_items 
    WHERE category = 'METHOD'
    ORDER BY code
""")

methods = cursor.fetchall()
print(f"\n总共 {len(methods)} 条METHOD记录：\n")

method_codes = []
for m in methods:
    print(f"  {m['code']} -> {m['label']}")
    method_codes.append(m['code'])

print("\n" + "=" * 100)
print("舟山医院使用的methodCode对比")
print("=" * 100)

zhoushan_codes = ['system_construct', 'qcc', 'process_reengineering', 'benchmarking']

print("\n舟山医院使用的code:")
for code in zhoushan_codes:
    exists = "✅ 存在" if code in method_codes else "❌ 不存在"
    print(f"  {code} - {exists}")

cursor.close()
conn.close()
