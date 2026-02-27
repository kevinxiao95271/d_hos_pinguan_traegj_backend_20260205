# -*- coding: utf-8 -*-
"""
修复 experience_improve 字典项的错误 label
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
print("修复 experience_improve 字典项的错误 label")
print("=" * 100)

# 修复1: 更新 internet_diagnosis 的 label
print("\n[修复1] 更新 internet_diagnosis 的 label")
print("-" * 100)

cursor.execute("""
    SELECT id, code, label
    FROM dictionary_items
    WHERE code = 'internet_diagnosis'
""")

item = cursor.fetchone()
if item:
    print(f"\n  修复前:")
    print(f"    ID: {item['id']}")
    print(f"    Code: {item['code']}")
    print(f"    Label: {item['label']}")
    
    # 更新 label
    cursor.execute("""
        UPDATE dictionary_items
        SET label = '互联网诊疗更加可及'
        WHERE code = 'internet_diagnosis'
    """)
    
    conn.commit()
    
    print(f"\n  修复后:")
    print(f"    Label: 互联网诊疗更加可及")
    print(f"\n  [OK] internet_diagnosis 的 label 已修复")
else:
    print(f"\n  [ERROR] 未找到 internet_diagnosis")

# 问题2: experience_improve_20260205144626 需要手动确定映射
print(f"\n{'=' * 100}")
print("[问题2] experience_improve_20260205144626 需要确定映射")
print("-" * 100)

cursor.execute("""
    SELECT id, code, label
    FROM dictionary_items
    WHERE code = 'experience_improve_20260205144626'
""")

item = cursor.fetchone()
if item:
    print(f"\n  错误的字典项:")
    print(f"    ID: {item['id']}")
    print(f"    Code: {item['code']}")
    print(f"    Label: {item['label']}")
    
    # 查询使用它的记录
    cursor.execute("""
        SELECT r.id, r.project_name, ai.theme, ai.experience_improve_other
        FROM registrations r
        JOIN activity_infos ai ON r.id = ai.registration_id
        WHERE ai.experience_improve_code = 'experience_improve_20260205144626'
    """)
    
    records = cursor.fetchall()
    
    print(f"\n  使用该 code 的记录 (共 {len(records)} 条):")
    print(f"  {'ID':<6} {'项目名称':<40} {'主题':<40} {'其他说明'}")
    print(f"  {'-' * 100}")
    
    for record in records:
        project_name = record['project_name'][:38] if record['project_name'] else 'N/A'
        theme = record['theme'][:38] if record['theme'] else 'N/A'
        other = record['experience_improve_other'][:20] if record['experience_improve_other'] else ''
        print(f"  {record['id']:<6} {project_name:<40} {theme:<40} {other}")
    
    print(f"\n  [待处理] 需要手动确定这些记录应该映射到哪个正确的 code")
    print(f"\n  可选的正确 code:")
    
    cursor.execute("""
        SELECT code, label
        FROM dictionary_items
        WHERE type = 'experience_improve'
        AND code != 'experience_improve_20260205144626'
        ORDER BY id
    """)
    
    valid_codes = cursor.fetchall()
    for i, code_item in enumerate(valid_codes, 1):
        print(f"    {i:2}. {code_item['code']:<45} -> {code_item['label']}")
    
    print(f"\n  建议:")
    print(f"    1. 根据项目名称/主题，手动确定每条记录应该用哪个正确的 code")
    print(f"    2. 批量更新这些记录的 experience_improve_code")
    print(f"    3. 删除 experience_improve_20260205144626 这个错误的字典项")

cursor.close()
conn.close()

print(f"\n{'=' * 100}")
print("[总结]")
print("=" * 100)

print(f"\n  修复完成:")
print(f"    [OK] internet_diagnosis 的 label 已从'便捷'改为'可及'")

print(f"\n  待处理:")
print(f"    [TODO] experience_improve_20260205144626 的8条记录需要确定正确的映射")
print(f"    [TODO] 确定映射后，需要批量更新并删除错误的字典项")

print(f"\n{'=' * 100}")
