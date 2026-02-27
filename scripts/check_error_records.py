# -*- coding: utf-8 -*-
"""
检查返回500错误的记录数据
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
print("检查返回500错误的记录")
print("=" * 100)

error_ids = [34, 49, 55, 56, 64, 116, 122, 125]

for reg_id in error_ids:
    print(f"\n{'-' * 100}")
    print(f"[记录 {reg_id}]")
    print(f"{'-' * 100}")
    
    # 检查 registrations 表
    cursor.execute("""
        SELECT id, project_name, competition_id, institution_id, applicant_id
        FROM registrations
        WHERE id = %s
    """, (reg_id,))
    
    reg = cursor.fetchone()
    
    if not reg:
        print(f"  [ERROR] registrations 表中未找到该记录")
        continue
    
    print(f"  registrations:")
    print(f"    id: {reg['id']}")
    print(f"    project_name: {reg['project_name']}")
    print(f"    competition_id: {reg['competition_id']}")
    print(f"    institution_id: {reg['institution_id']}")
    print(f"    applicant_id: {reg['applicant_id']}")
    
    # 检查 activity_infos 表
    cursor.execute("""
        SELECT id, experience_improve_code, subject_type_code, method_code, quality_topic_code
        FROM activity_infos
        WHERE registration_id = %s
    """, (reg_id,))
    
    activity = cursor.fetchone()
    
    if not activity:
        print(f"  [WARNING] activity_infos 表中未找到该记录")
    else:
        print(f"  activity_infos:")
        print(f"    experience_improve_code: {activity['experience_improve_code']}")
        print(f"    subject_type_code: {activity['subject_type_code']}")
        print(f"    method_code: {activity['method_code']}")
        print(f"    quality_topic_code: {activity['quality_topic_code']}")
        
        # 检查所有 code 是否在字典表中存在
        codes_to_check = [
            ('experience_improve', activity['experience_improve_code']),
            ('subject_type', activity['subject_type_code']),
            ('method', activity['method_code']),
            ('quality_topic', activity['quality_topic_code'])
        ]
        
        print(f"  字典项检查:")
        
        for dict_type, code in codes_to_check:
            if code:
                cursor.execute("""
                    SELECT label FROM dictionary_items
                    WHERE code = %s
                """, (code,))
                
                dict_item = cursor.fetchone()
                
                if dict_item:
                    print(f"    {dict_type:<25} {code:<35} -> OK (label: {dict_item['label'][:30]})")
                else:
                    print(f"    {dict_type:<25} {code:<35} -> ERROR (字典表中不存在)")

cursor.close()
conn.close()

print(f"\n{'=' * 100}")
