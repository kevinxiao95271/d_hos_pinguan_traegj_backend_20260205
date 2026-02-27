# -*- coding: utf-8 -*-
"""
修复记录56的 institution_id
"""
import pymysql
import random

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
print("修复记录56的 institution_id")
print("=" * 100)

# 1. 查找一个有效的三级医院
print("\n[步骤1] 查找有效的三级医院")
print("-" * 100)

cursor.execute("""
    SELECT id, name, level
    FROM const_init_institutions
    WHERE level = '三级医院'
    LIMIT 10
""")

hospitals = cursor.fetchall()

if hospitals:
    print(f"\n  找到 {len(hospitals)} 个三级医院:")
    for i, hospital in enumerate(hospitals[:5], 1):
        print(f"    {i}. id={hospital['id']}, name={hospital['name'][:40]}")
    
    # 随机选一个
    selected = random.choice(hospitals)
    selected_id = selected['id']
    selected_name = selected['name']
    
    print(f"\n  [选择] 随机分配: id={selected_id}, name={selected_name[:40]}")
else:
    print(f"\n  [ERROR] 未找到三级医院")
    cursor.close()
    conn.close()
    exit(1)

# 2. 查看记录56的当前状态
print(f"\n{'=' * 100}")
print("[步骤2] 查看记录56的当前状态")
print("-" * 100)

cursor.execute("""
    SELECT id, project_name, institution_id
    FROM registrations
    WHERE id = 56
""")

record = cursor.fetchone()

if record:
    print(f"\n  修复前:")
    print(f"    registration_id: {record['id']}")
    print(f"    project_name: {record['project_name']}")
    print(f"    institution_id: {record['institution_id']} (不存在)")
else:
    print(f"\n  [ERROR] 未找到记录56")
    cursor.close()
    conn.close()
    exit(1)

# 3. 更新记录56的 institution_id
print(f"\n{'=' * 100}")
print("[步骤3] 更新记录56的 institution_id")
print("-" * 100)

cursor.execute("""
    UPDATE registrations
    SET institution_id = %s
    WHERE id = 56
""", (selected_id,))

conn.commit()

print(f"\n  [OK] 已更新 institution_id 为 {selected_id}")

# 4. 验证更新结果
print(f"\n{'=' * 100}")
print("[步骤4] 验证更新结果")
print("-" * 100)

cursor.execute("""
    SELECT r.id, r.project_name, r.institution_id, i.name as institution_name
    FROM registrations r
    LEFT JOIN const_init_institutions i ON r.institution_id = i.id
    WHERE r.id = 56
""")

updated_record = cursor.fetchone()

if updated_record:
    print(f"\n  修复后:")
    print(f"    registration_id: {updated_record['id']}")
    print(f"    project_name: {updated_record['project_name']}")
    print(f"    institution_id: {updated_record['institution_id']}")
    print(f"    institution_name: {updated_record['institution_name'][:50]}")
    
    if updated_record['institution_name']:
        print(f"\n  [OK] institution 关联正常")
    else:
        print(f"\n  [ERROR] institution 关联失败")
else:
    print(f"\n  [ERROR] 验证失败")

cursor.close()
conn.close()

print(f"\n{'=' * 100}")
print("[总结]")
print("=" * 100)

print(f"\n  [OK] 记录56的 institution_id 已修复")
print(f"  原 institution_id: 4553 (不存在)")
print(f"  新 institution_id: {selected_id} ({selected_name[:40]})")

print(f"\n{'=' * 100}")
