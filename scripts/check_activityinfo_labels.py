# -*- coding: utf-8 -*-
"""
检查ActivityInfo表和字典表的数据情况
"""
import pymysql

db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

print("=" * 100)
print("检查 ActivityInfo 和字典表数据")
print("=" * 100)

conn = pymysql.connect(**db_config)
cursor = conn.cursor()

# 1. 检查 activity_infos 表的数据
print("\n[步骤1] 检查 activity_infos 表")

cursor.execute("""
    SELECT COUNT(*) FROM activity_infos
""")
total_count = cursor.fetchone()[0]
print(f"\n总记录数: {total_count}")

# 检查各字段的填充情况
cursor.execute("""
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN subject_type_code IS NOT NULL AND subject_type_code != '' THEN 1 ELSE 0 END) as has_subject_type,
        SUM(CASE WHEN method_code IS NOT NULL AND method_code != '' THEN 1 ELSE 0 END) as has_method,
        SUM(CASE WHEN experience_improve_code IS NOT NULL AND experience_improve_code != '' THEN 1 ELSE 0 END) as has_experience,
        SUM(CASE WHEN quality_topic_code IS NOT NULL AND quality_topic_code != '' THEN 1 ELSE 0 END) as has_quality
    FROM activity_infos
""")

row = cursor.fetchone()
print(f"\n字段填充情况:")
print(f"  subject_type_code 有值: {row[1]}/{row[0]} ({row[1]/row[0]*100:.1f}%)")
print(f"  method_code 有值: {row[2]}/{row[0]} ({row[2]/row[0]*100:.1f}%)")
print(f"  experience_improve_code 有值: {row[3]}/{row[0]} ({row[3]/row[0]*100:.1f}%)")
print(f"  quality_topic_code 有值: {row[4]}/{row[0]} ({row[4]/row[0]*100:.1f}%)")

# 查看几条样例数据
print(f"\n[样例数据] 前5条记录:")
cursor.execute("""
    SELECT 
        id,
        registration_id,
        subject_type_code,
        method_code,
        experience_improve_code,
        quality_topic_code
    FROM activity_infos
    LIMIT 5
""")

for row in cursor.fetchall():
    print(f"\n  ID: {row[0]}, Registration ID: {row[1]}")
    print(f"    subject_type_code: {row[2]}")
    print(f"    method_code: {row[3]}")
    print(f"    experience_improve_code: {row[4]}")
    print(f"    quality_topic_code: {row[5]}")

# 2. 检查字典表
print("\n" + "=" * 100)
print("[步骤2] 检查 dictionary_items 表")

# 按类型统计
cursor.execute("""
    SELECT 
        type,
        COUNT(*) as count,
        SUM(CASE WHEN active = 1 THEN 1 ELSE 0 END) as active_count
    FROM dictionary_items
    GROUP BY type
    ORDER BY type
""")

print(f"\n字典类型统计:")
dict_types = {}
for row in cursor.fetchall():
    dict_types[row[0]] = (row[1], row[2])
    print(f"  {row[0]}: 总数={row[1]}, 启用={row[2]}")

# 3. 检查 subject_type 字典
print("\n" + "=" * 100)
print("[步骤3] 检查 subject_type 字典详情")

cursor.execute("""
    SELECT code, label, active
    FROM dictionary_items
    WHERE type = 'subject_type'
    ORDER BY code
""")

print(f"\n主题类型字典:")
subject_type_dict = {}
for row in cursor.fetchall():
    subject_type_dict[row[0]] = row[1]
    status = "启用" if row[2] else "禁用"
    print(f"  {row[0]}: {row[1]} ({status})")

# 4. 检查 method 字典
print("\n[步骤4] 检查 method 字典详情 (前10条)")

cursor.execute("""
    SELECT code, label, active
    FROM dictionary_items
    WHERE type = 'method'
    ORDER BY code
    LIMIT 10
""")

print(f"\n品管工具字典 (前10条):")
method_dict = {}
for row in cursor.fetchall():
    method_dict[row[0]] = row[1]
    status = "启用" if row[2] else "禁用"
    print(f"  {row[0]}: {row[1]} ({status})")

# 5. 验证数据匹配情况
print("\n" + "=" * 100)
print("[步骤5] 验证 activity_infos 中的 code 是否在字典表中")

cursor.execute("""
    SELECT DISTINCT subject_type_code
    FROM activity_infos
    WHERE subject_type_code IS NOT NULL AND subject_type_code != ''
    ORDER BY subject_type_code
""")

print(f"\nactivity_infos 中使用的 subject_type_code:")
missing_codes = []
for row in cursor.fetchall():
    code = row[0]
    if code in subject_type_dict:
        print(f"  {code}: {subject_type_dict[code]} (OK)")
    else:
        print(f"  {code}: [NOT FOUND] (字典中不存在)")
        missing_codes.append(code)

if missing_codes:
    print(f"\n[WARNING] 有 {len(missing_codes)} 个code在字典中不存在！")
else:
    print(f"\n[OK] 所有code都在字典中存在")

# 6. 检查特定的 subject_type_4
print("\n" + "=" * 100)
print("[步骤6] 检查 subject_type_4 的情况")

cursor.execute("""
    SELECT code, label, active
    FROM dictionary_items
    WHERE code = 'subject_type_4'
""")

row = cursor.fetchone()
if row:
    print(f"\n字典中的 subject_type_4:")
    print(f"  code: {row[0]}")
    print(f"  label: {row[1]}")
    print(f"  active: {row[2]}")
else:
    print(f"\n[ERROR] 字典中没有 subject_type_4！")

# 检查有多少activity_infos使用了subject_type_4
cursor.execute("""
    SELECT COUNT(*) 
    FROM activity_infos
    WHERE subject_type_code = 'subject_type_4'
""")
count = cursor.fetchone()[0]
print(f"\n使用 subject_type_4 的记录数: {count}")

# 7. 总结
print("\n" + "=" * 100)
print("[总结]")
print("=" * 100)

print(f"\n数据源头检查结果:")
print(f"  1. activity_infos 表有 {total_count} 条记录")
print(f"  2. subject_type_code 字段有 {row[1]} 条有值")
print(f"  3. dictionary_items 中有 {dict_types.get('subject_type', (0,0))[1]} 条启用的主题类型")
print(f"  4. subject_type_4 {'存在' if row else '不存在'} 于字典表")

if missing_codes:
    print(f"\n[问题] 有 {len(missing_codes)} 个code在字典中找不到对应的label")

cursor.close()
conn.close()

print("\n" + "=" * 100)
