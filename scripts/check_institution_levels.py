# -*- coding: utf-8 -*-
"""
查看 institution 表中的 level 字段值
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
print("查看 institution 表中的 level 字段值")
print("=" * 100)

cursor.execute("""
    SELECT level, COUNT(*) as count
    FROM const_init_institutions
    GROUP BY level
    ORDER BY count DESC
""")

levels = cursor.fetchall()

print(f"\n  level 字段的所有值:")
print(f"  {'Level':<30} {'Count'}")
print(f"  {'-' * 50}")

for level_item in levels:
    level = level_item['level'] if level_item['level'] else 'NULL'
    count = level_item['count']
    print(f"  {level:<30} {count}")

# 找一个有数据的level，随机选一个机构
print(f"\n{'=' * 100}")
print("[随机选择一个有效的机构]")
print("=" * 100)

cursor.execute("""
    SELECT id, name, level
    FROM const_init_institutions
    WHERE level IS NOT NULL AND level != ''
    ORDER BY RAND()
    LIMIT 5
""")

institutions = cursor.fetchall()

print(f"\n  随机选择的机构:")
for i, inst in enumerate(institutions, 1):
    print(f"    {i}. id={inst['id']}, level={inst['level']}, name={inst['name'][:40]}")

cursor.close()
conn.close()

print(f"\n{'=' * 100}")
