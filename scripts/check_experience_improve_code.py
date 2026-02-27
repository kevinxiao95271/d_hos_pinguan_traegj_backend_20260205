# -*- coding: utf-8 -*-
"""
检查 experience_improve 这个 code 在字典表中的情况
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
print("检查 experience_improve code 在字典表中的情况")
print("=" * 100)

# 1. 查询字典表中是否有这个 code
print("\n[步骤1] 查询字典表中的 experience_improve")
cursor.execute("""
    SELECT code, label, type
    FROM dictionary_items
    WHERE code = 'experience_improve'
""")

result = cursor.fetchone()

if result:
    print(f"\n  [找到] experience_improve 在字典表中:")
    print(f"    code: {result['code']}")
    print(f"    label: {result['label']}")
    print(f"    type: {result['type']}")
else:
    print(f"\n  [未找到] experience_improve 不在字典表中！")

# 2. 查询所有 experience_improve 相关的 code
print(f"\n{'=' * 100}")
print("[步骤2] 查询所有 experience_improve 相关的 code")
print(f"{'=' * 100}")

cursor.execute("""
    SELECT code, label, type
    FROM dictionary_items
    WHERE code LIKE 'experience_improve%'
    ORDER BY code
""")

results = cursor.fetchall()

if results:
    print(f"\n  找到 {len(results)} 条相关记录:")
    for row in results:
        print(f"    - {row['code']:<40} -> {row['label']}")
else:
    print(f"\n  未找到任何 experience_improve 相关的 code")

# 3. 查询 activity_infos 表中是否有使用 experience_improve 这个 code
print(f"\n{'=' * 100}")
print("[步骤3] 查询哪些记录使用了 experience_improve code")
print(f"{'=' * 100}")

cursor.execute("""
    SELECT ai.id, ai.registration_id, ai.experience_improve_code, r.project_name
    FROM activity_infos ai
    JOIN registrations r ON ai.registration_id = r.id
    WHERE ai.experience_improve_code = 'experience_improve'
    LIMIT 10
""")

results = cursor.fetchall()

if results:
    print(f"\n  找到 {len(results)} 条记录使用了 'experience_improve' code:")
    for row in results:
        print(f"    - registration_id: {row['registration_id']}, project: {row['project_name']}")
else:
    print(f"\n  没有记录使用 'experience_improve' code")

# 4. 统计所有 experience_improve_code 的使用情况
print(f"\n{'=' * 100}")
print("[步骤4] 统计所有 experience_improve_code 的使用情况")
print(f"{'=' * 100}")

cursor.execute("""
    SELECT experience_improve_code, COUNT(*) as count
    FROM activity_infos
    WHERE experience_improve_code IS NOT NULL AND experience_improve_code != ''
    GROUP BY experience_improve_code
    ORDER BY count DESC
""")

results = cursor.fetchall()

print(f"\n  experience_improve_code 使用统计:")
print(f"  {'Code':<40} {'使用次数':<10} {'有Label':<10} {'Label值'}")
print(f"  {'-' * 120}")

for row in results:
    code = row['experience_improve_code']
    count = row['count']
    
    # 查询字典中是否有这个 code
    cursor.execute("""
        SELECT label FROM dictionary_items WHERE code = %s
    """, (code,))
    
    label_result = cursor.fetchone()
    has_label = "YES" if label_result else "NO"
    label_value = label_result['label'] if label_result else "N/A"
    
    print(f"  {code:<40} {count:<10} {has_label:<10} {label_value}")

cursor.close()
conn.close()

print(f"\n{'=' * 100}")
print("[总结]")
print(f"{'=' * 100}")

print(f"\n问题分析:")
print(f"  如果有记录使用了 'experience_improve' 这个 code，")
print(f"  但字典表中没有对应的 label，")
print(f"  那么 getLabel() 方法会返回 null 或 code 本身。")

print(f"\n{'=' * 100}")
