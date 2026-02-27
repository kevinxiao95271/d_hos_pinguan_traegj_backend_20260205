# -*- coding: utf-8 -*-
"""
对比正常记录和错误记录的差异
"""
import pymysql
import json

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
print("对比正常记录和错误记录")
print("=" * 100)

ok_id = 1  # 正常的记录
error_id = 34  # 500错误的记录

for label, reg_id in [("正常记录", ok_id), ("错误记录", error_id)]:
    print(f"\n{'-' * 100}")
    print(f"[{label} - ID={reg_id}]")
    print(f"{'-' * 100}")
    
    # registrations 表
    cursor.execute("SELECT * FROM registrations WHERE id = %s", (reg_id,))
    reg = cursor.fetchone()
    
    print(f"\n  registrations:")
    for key in ['id', 'project_name', 'status', 'competition_id', 'institution_id', 'applicant_id', 'group_type', 'group_code']:
        print(f"    {key:<20}: {reg.get(key)}")
    
    # activity_infos 表
    cursor.execute("SELECT * FROM activity_infos WHERE registration_id = %s", (reg_id,))
    activity = cursor.fetchone()
    
    if activity:
        print(f"\n  activity_infos:")
        for key in ['experience_improve_code', 'subject_type_code', 'method_code', 'quality_topic_code']:
            code = activity.get(key)
            
            # 查询 label
            if code:
                cursor.execute("SELECT label FROM dictionary_items WHERE code = %s", (code,))
                dict_item = cursor.fetchone()
                label_value = dict_item['label'] if dict_item else '[NOT FOUND]'
            else:
                label_value = '[NULL]'
            
            print(f"    {key:<30}: {code:<40} -> {label_value}")
    
    # registration_members 表
    cursor.execute("SELECT COUNT(*) as count FROM registration_members WHERE registration_id = %s", (reg_id,))
    members_count = cursor.fetchone()['count']
    print(f"\n  registration_members: {members_count} 条")
    
    # project_summaries 表
    cursor.execute("SELECT COUNT(*) as count FROM project_summaries WHERE registration_id = %s", (reg_id,))
    summary_count = cursor.fetchone()['count']
    print(f"  project_summaries: {summary_count} 条")
    
    # material_files 表
    cursor.execute("SELECT COUNT(*) as count FROM material_files WHERE registration_id = %s", (reg_id,))
    materials_count = cursor.fetchone()['count']
    print(f"  material_files: {materials_count} 条")

cursor.close()
conn.close()

print(f"\n{'=' * 100}")
print("[分析]")
print("=" * 100)

print(f"\n  请对比两条记录的差异，特别注意:")
print(f"    1. experience_improve_code 等字段的 code 值")
print(f"    2. 是否有字段的 code 在字典表中不存在")
print(f"    3. 关联表记录数量的差异")

print(f"\n{'=' * 100}")
