# -*- coding: utf-8 -*-
"""
检查 quality_topic 的所有正确选项
"""
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

print("=" * 100)
print("查看所有 quality_topic 的字典项")
print("=" * 100)

cursor.execute("""
    SELECT id, code, label
    FROM dictionary_items
    WHERE type = 'quality_topic'
    ORDER BY id
""")

items = cursor.fetchall()

print(f"\n  quality_topic 类型的字典项 (共 {len(items)} 个):")
print(f"  {'ID':<6} {'Code':<50} {'Label'}")
print(f"  {'-' * 100}")

other_code = None

for item in items:
    print(f"  {item['id']:<6} {item['code']:<50} {item['label']}")
    
    # 查找"其他"选项的 code
    if '其他' in item['label'] or 'other' in item['code'].lower():
        other_code = item['code']
        print(f"         ^^^^^ 这是'其他'选项")

print(f"\n{'=' * 100}")
print("[查找使用错误 code 的记录]")
print("=" * 100)

cursor.execute("""
    SELECT r.id, r.project_name
    FROM registrations r
    JOIN activity_infos ai ON r.id = ai.registration_id
    WHERE ai.quality_topic_code = 'quality_topic_20260205144626'
""")

records = cursor.fetchall()

print(f"\n  使用 quality_topic_20260205144626 的记录 (共 {len(records)} 条):")
for i, record in enumerate(records, 1):
    print(f"    {i}. registration_id={record['id']}, project={record['project_name'][:50]}")

cursor.close()
conn.close()

print(f"\n{'=' * 100}")
print("[修复建议]")
print("=" * 100)

if other_code:
    print(f"\n  找到'其他'选项的 code: {other_code}")
    print(f"\n  修复方案:")
    print(f"    1. 将这 {len(records)} 条记录的 quality_topic_code 改为 '{other_code}'")
    print(f"    2. 删除错误的字典项 quality_topic_20260205144626")
else:
    print(f"\n  [WARNING] 未找到 quality_topic 的'其他'选项")
    print(f"  需要先确定应该映射到哪个选项")

print(f"\n{'=' * 100}")
