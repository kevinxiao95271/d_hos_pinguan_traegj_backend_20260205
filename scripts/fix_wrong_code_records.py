# -*- coding: utf-8 -*-
"""
修复使用错误 code 的记录
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
print("修复使用 experience_improve_20260205144626 的记录")
print("=" * 100)

# 1. 查看受影响的记录
print("\n[步骤1] 查看受影响的记录")
print("-" * 100)

cursor.execute("""
    SELECT r.id, r.project_name, ai.experience_improve_code
    FROM registrations r
    JOIN activity_infos ai ON r.id = ai.registration_id
    WHERE ai.experience_improve_code = 'experience_improve_20260205144626'
""")

records = cursor.fetchall()

print(f"\n  找到 {len(records)} 条使用错误 code 的记录:")
for i, record in enumerate(records, 1):
    print(f"    {i}. registration_id={record['id']}, project={record['project_name'][:50]}")

# 2. 更新这些记录为 'other'
print(f"\n{'=' * 100}")
print("[步骤2] 更新这些记录的 experience_improve_code 为 'other'")
print("-" * 100)

cursor.execute("""
    UPDATE activity_infos
    SET experience_improve_code = 'other'
    WHERE experience_improve_code = 'experience_improve_20260205144626'
""")

affected_rows = cursor.rowcount
conn.commit()

print(f"\n  [OK] 已更新 {affected_rows} 条记录")

# 3. 删除错误的字典项
print(f"\n{'=' * 100}")
print("[步骤3] 删除错误的字典项")
print("-" * 100)

# 先确认没有记录在使用这个 code 了
cursor.execute("""
    SELECT COUNT(*) as count
    FROM activity_infos
    WHERE experience_improve_code = 'experience_improve_20260205144626'
""")

usage_count = cursor.fetchone()['count']

if usage_count == 0:
    print(f"\n  确认: 没有记录在使用 'experience_improve_20260205144626'")
    
    cursor.execute("""
        DELETE FROM dictionary_items
        WHERE code = 'experience_improve_20260205144626'
    """)
    
    conn.commit()
    
    print(f"\n  [OK] 已删除错误的字典项")
else:
    print(f"\n  [WARNING] 还有 {usage_count} 条记录在使用这个 code，未删除字典项")

# 4. 验证修复结果
print(f"\n{'=' * 100}")
print("[步骤4] 验证修复结果")
print("-" * 100)

# 检查这些记录现在的 code
cursor.execute("""
    SELECT r.id, ai.experience_improve_code
    FROM registrations r
    JOIN activity_infos ai ON r.id = ai.registration_id
    WHERE r.id IN (34, 49, 55, 56, 64, 116, 122, 125)
""")

updated_records = cursor.fetchall()

print(f"\n  修复后的记录:")
all_ok = True
for record in updated_records:
    code = record['experience_improve_code']
    status = "OK" if code == 'other' else "ERROR"
    if code != 'other':
        all_ok = False
    print(f"    registration_id={record['id']}, code={code}, status=[{status}]")

# 检查字典项是否已删除
cursor.execute("""
    SELECT COUNT(*) as count
    FROM dictionary_items
    WHERE code = 'experience_improve_20260205144626'
""")

dict_count = cursor.fetchone()['count']

if dict_count == 0:
    print(f"\n  [OK] 错误的字典项已删除")
else:
    print(f"\n  [WARNING] 错误的字典项仍然存在")

cursor.close()
conn.close()

print(f"\n{'=' * 100}")
print("[总结]")
print("=" * 100)

if all_ok and dict_count == 0:
    print(f"\n  [OK] 所有修复完成!")
    print(f"    - 已将8条记录的 experience_improve_code 改为 'other'")
    print(f"    - 已删除错误的字典项 experience_improve_20260205144626")
else:
    print(f"\n  [ERROR] 修复过程中出现问题，请检查")

print(f"\n{'=' * 100}")
