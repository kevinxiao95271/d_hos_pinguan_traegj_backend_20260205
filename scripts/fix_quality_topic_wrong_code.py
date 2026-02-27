# -*- coding: utf-8 -*-
"""
修复 quality_topic_20260205144626 错误code的记录
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
print("修复 quality_topic_20260205144626 错误code的记录")
print("=" * 100)

# 1. 更新记录
print("\n[步骤1] 更新使用错误 code 的记录")
print("-" * 100)

cursor.execute("""
    UPDATE activity_infos
    SET quality_topic_code = 'other'
    WHERE quality_topic_code = 'quality_topic_20260205144626'
""")

affected_rows = cursor.rowcount
conn.commit()

print(f"\n  [OK] 已更新 {affected_rows} 条记录")

# 2. 验证
print(f"\n{'=' * 100}")
print("[步骤2] 验证是否还有记录使用错误的 code")
print("-" * 100)

cursor.execute("""
    SELECT COUNT(*) as count
    FROM activity_infos
    WHERE quality_topic_code = 'quality_topic_20260205144626'
""")

usage_count = cursor.fetchone()['count']

if usage_count == 0:
    print(f"\n  [OK] 没有记录在使用 quality_topic_20260205144626")
else:
    print(f"\n  [WARNING] 还有 {usage_count} 条记录在使用这个 code")

# 3. 删除错误的字典项
if usage_count == 0:
    print(f"\n{'=' * 100}")
    print("[步骤3] 删除错误的字典项")
    print("-" * 100)
    
    cursor.execute("""
        DELETE FROM dictionary_items
        WHERE code = 'quality_topic_20260205144626'
    """)
    
    conn.commit()
    
    print(f"\n  [OK] 已删除错误的字典项")

# 4. 验证修复结果
print(f"\n{'=' * 100}")
print("[步骤4] 验证修复后的记录")
print("-" * 100)

test_ids = [11, 35, 59, 82, 86, 109, 111, 116]

cursor.execute(f"""
    SELECT r.id, ai.quality_topic_code
    FROM registrations r
    JOIN activity_infos ai ON r.id = ai.registration_id
    WHERE r.id IN ({','.join(map(str, test_ids))})
""")

updated_records = cursor.fetchall()

print(f"\n  修复后的记录:")
all_ok = True
for record in updated_records:
    code = record['quality_topic_code']
    status = "OK" if code == 'other' else "ERROR"
    if code != 'other':
        all_ok = False
    print(f"    registration_id={record['id']}, quality_topic_code={code}, status=[{status}]")

cursor.close()
conn.close()

print(f"\n{'=' * 100}")
print("[总结]")
print("=" * 100)

if all_ok and usage_count == 0:
    print(f"\n  [OK] quality_topic_20260205144626 修复完成!")
    print(f"    - 已将8条记录的 quality_topic_code 改为 'other'")
    print(f"    - 已删除错误的字典项")
else:
    print(f"\n  [ERROR] 修复过程中出现问题")

print(f"\n{'=' * 100}")
