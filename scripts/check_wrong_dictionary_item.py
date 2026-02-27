# -*- coding: utf-8 -*-
"""
检查错误的字典项 experience_improve_20260205144626
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
print("检查错误的字典项")
print("=" * 100)

# 1. 查看这个错误的字典项的完整信息
print("\n[步骤1] 错误字典项的完整信息")
cursor.execute("""
    SELECT * FROM dictionary_items
    WHERE code = 'experience_improve_20260205144626'
""")

result = cursor.fetchone()
if result:
    print(f"\n  错误的字典项:")
    for key, value in result.items():
        print(f"    {key}: {value}")

# 2. 查看所有正确的 experience_improve 相关的字典项
print(f"\n{'=' * 100}")
print("[步骤2] 所有正确的 experience_improve 相关字典项")
print(f"{'=' * 100}")

cursor.execute("""
    SELECT code, label, type
    FROM dictionary_items
    WHERE type = (SELECT type FROM dictionary_items WHERE code = 'experience_improve_20260205144626')
    AND code != 'experience_improve_20260205144626'
    ORDER BY code
""")

results = cursor.fetchall()

print(f"\n  同类型的其他字典项 (共 {len(results)} 条):")
for i, row in enumerate(results, 1):
    print(f"    {i:2}. {row['code']:<40} -> {row['label']}")

# 3. 查看哪些记录使用了这个错误的 code
print(f"\n{'=' * 100}")
print("[步骤3] 使用了错误code的记录")
print(f"{'=' * 100}")

cursor.execute("""
    SELECT r.id, r.project_name, ai.experience_improve_code
    FROM registrations r
    JOIN activity_infos ai ON r.id = ai.registration_id
    WHERE ai.experience_improve_code = 'experience_improve_20260205144626'
""")

results = cursor.fetchall()

print(f"\n  使用了错误code的记录 (共 {len(results)} 条):")
for i, row in enumerate(results, 1):
    print(f"    {i}. registration_id={row['id']}, project={row['project_name'][:30]}...")

# 4. 分析这个code的来源
print(f"\n{'=' * 100}")
print("[步骤4] 问题分析")
print(f"{'=' * 100}")

print(f"\n  问题:")
print(f"    1. 字典表中有一个错误的 code: experience_improve_20260205144626")
print(f"    2. 它的 label 是: 'experience_improve 20260205144626' (应该是中文)")
print(f"    3. 有 {len(results)} 条记录在使用这个错误的 code")

print(f"\n  可能的原因:")
print(f"    1. 数据导入时出错")
print(f"    2. 后缀 20260205144626 看起来像时间戳 (2026年2月5日 14:46:26)")
print(f"    3. 可能是导入脚本生成的临时/错误数据")

print(f"\n  修复建议:")
print(f"    方案1: 删除这个错误的字典项，但需要先更新使用它的记录")
print(f"    方案2: 修正这个字典项的 label 为正确的中文")
print(f"    方案3: 查找这个 code 应该对应的正确 code，批量更新记录")

cursor.close()
conn.close()

print(f"\n{'=' * 100}")
