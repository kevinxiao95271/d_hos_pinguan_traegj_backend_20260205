# -*- coding: utf-8 -*-
"""
删除8条有问题的测试记录及其关联数据
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
print("删除8条有问题的测试记录")
print("=" * 100)

error_ids = [34, 49, 55, 56, 64, 116, 122, 125]

# 1. 先查看这些记录的信息
print("\n[步骤1] 查看要删除的记录")
print("-" * 100)

cursor.execute(f"""
    SELECT id, project_name, status
    FROM registrations
    WHERE id IN ({','.join(map(str, error_ids))})
    ORDER BY id
""")

records = cursor.fetchall()

print(f"\n  要删除的记录 (共 {len(records)} 条):")
for record in records:
    print(f"    ID={record['id']:<4}, status={record['status']:<12}, project={record['project_name'][:50]}")

# 2. 统计关联数据
print(f"\n{'=' * 100}")
print("[步骤2] 统计关联数据")
print("-" * 100)

tables = [
    ('activity_infos', 'registration_id'),
    ('registration_members', 'registration_id'),
    ('project_summaries', 'registration_id'),
    ('material_files', 'registration_id'),
    ('review_tasks', 'registration_id')
]

total_related = 0

for table_name, fk_column in tables:
    cursor.execute(f"""
        SELECT COUNT(*) as count
        FROM {table_name}
        WHERE {fk_column} IN ({','.join(map(str, error_ids))})
    """)
    
    count = cursor.fetchone()['count']
    total_related += count
    print(f"  {table_name:<30}: {count} 条")

print(f"\n  关联数据总计: {total_related} 条")

# 3. 删除关联数据
print(f"\n{'=' * 100}")
print("[步骤3] 删除关联数据")
print("-" * 100)

for table_name, fk_column in tables:
    cursor.execute(f"""
        DELETE FROM {table_name}
        WHERE {fk_column} IN ({','.join(map(str, error_ids))})
    """)
    
    deleted = cursor.rowcount
    if deleted > 0:
        print(f"  {table_name:<30}: 已删除 {deleted} 条")

conn.commit()

# 4. 删除主记录
print(f"\n{'=' * 100}")
print("[步骤4] 删除主记录")
print("-" * 100)

cursor.execute(f"""
    DELETE FROM registrations
    WHERE id IN ({','.join(map(str, error_ids))})
""")

deleted_main = cursor.rowcount
print(f"\n  registrations: 已删除 {deleted_main} 条")

conn.commit()

# 5. 验证删除结果
print(f"\n{'=' * 100}")
print("[步骤5] 验证删除结果")
print("-" * 100)

cursor.execute(f"""
    SELECT COUNT(*) as count
    FROM registrations
    WHERE id IN ({','.join(map(str, error_ids))})
""")

remaining = cursor.fetchone()['count']

if remaining == 0:
    print(f"\n  [OK] 所有记录已成功删除")
else:
    print(f"\n  [WARNING] 还有 {remaining} 条记录未删除")

# 检查关联数据是否清理干净
print(f"\n  验证关联数据:")

for table_name, fk_column in tables:
    cursor.execute(f"""
        SELECT COUNT(*) as count
        FROM {table_name}
        WHERE {fk_column} IN ({','.join(map(str, error_ids))})
    """)
    
    count = cursor.fetchone()['count']
    if count > 0:
        print(f"    {table_name:<30}: 还有 {count} 条未删除")
    else:
        print(f"    {table_name:<30}: OK (已清空)")

cursor.close()
conn.close()

print(f"\n{'=' * 100}")
print("[总结]")
print("=" * 100)

print(f"\n  删除完成:")
print(f"    - 主记录: {deleted_main} 条")
print(f"    - 关联数据: {total_related} 条")
print(f"    - 总计: {deleted_main + total_related} 条")

print(f"\n  已删除的记录ID: {', '.join(map(str, error_ids))}")

print(f"\n{'=' * 100}")
