#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""调试label到code的转换"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pymysql

conn = pymysql.connect(
    host='gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    port=63606,
    user='root',
    password='Yiguo9527_',
    database='d_hos_pinguan_traegj_20260205',
    charset='utf8mb4'
)

cursor = conn.cursor(pymysql.cursors.DictCursor)

print("="*80)
print("调试label到code的转换")
print("="*80)

# 查询所有method字典项
print("\n[1] 查询所有method字典项")
print("-" * 80)

cursor.execute("""
    SELECT code, label, active
    FROM dictionary_items
    WHERE type = 'method'
    ORDER BY code
""")

items = cursor.fetchall()

print(f"\n找到 {len(items)} 个method字典项:\n")

target_label = "品管圈-课题达成"

for item in items:
    status = "✅" if item['active'] else "❌"
    match = "👈 匹配!" if item['label'] == target_label else ""
    print(f"{status} code={item['code']:20s} label={item['label']:30s} {match}")
    
    # 检查是否有隐藏字符
    if item['label'] == target_label or target_label in item['label'] or item['label'] in target_label:
        label_bytes = item['label'].encode('utf-8')
        target_bytes = target_label.encode('utf-8')
        print(f"     label字节: {label_bytes}")
        print(f"     target字节: {target_bytes}")
        print(f"     相等: {item['label'] == target_label}")

# 查找特定label
print(f"\n\n[2] 查找label='{target_label}'的记录")
print("-" * 80)

cursor.execute("""
    SELECT code, label
    FROM dictionary_items
    WHERE type = 'method' AND label = %s AND active = true
""", (target_label,))

result = cursor.fetchone()

if result:
    print(f"\n✅ 找到匹配:")
    print(f"  code: {result['code']}")
    print(f"  label: {result['label']}")
else:
    print(f"\n❌ 未找到匹配")
    
    # 尝试模糊匹配
    cursor.execute("""
        SELECT code, label
        FROM dictionary_items
        WHERE type = 'method' AND label LIKE %s AND active = true
    """, (f"%{target_label}%",))
    
    fuzzy_results = cursor.fetchall()
    
    if fuzzy_results:
        print(f"\n模糊匹配结果:")
        for r in fuzzy_results:
            print(f"  code: {r['code']}, label: {r['label']}")

cursor.close()
conn.close()

print("\n" + "="*80)
print("调试完成")
print("="*80)
