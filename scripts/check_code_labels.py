# -*- coding: utf-8 -*-
"""
查询指定code的中文标签
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

print("=" * 120)
print("Query Code Labels")
print("=" * 120)

codes_to_check = ['antibiotic_pathogen_test', 'QC_CIRCLE']

for code in codes_to_check:
    print(f"\n{'=' * 120}")
    print(f"Code: {code}")
    print("-" * 120)
    
    cursor.execute("""
        SELECT id, type, code, label, active, created_at
        FROM dictionary_items
        WHERE code = %s
    """, (code,))
    
    result = cursor.fetchone()
    
    if result:
        print(f"\n  ID: {result['id']}")
        print(f"  Type: {result['type']}")
        print(f"  Code: {result['code']}")
        print(f"  Label (中文): {result['label']}")
        print(f"  Active: {result['active']}")
        print(f"  Created At: {result['created_at']}")
        
        # 查询使用次数
        field_map = {
            'subject_type': 'subject_type_code',
            'method': 'method_code',
            'experience_improve': 'experience_improve_code',
            'quality_topic': 'quality_topic_code'
        }
        
        field_name = field_map.get(result['type'])
        if field_name:
            cursor.execute(f"""
                SELECT COUNT(*) as count
                FROM activity_infos
                WHERE {field_name} = %s
            """, (code,))
            
            usage = cursor.fetchone()['count']
            print(f"  Usage Count: {usage} records")
    else:
        print(f"\n  [NOT FOUND] Code '{code}' does not exist in dictionary_items table")

cursor.close()
conn.close()

print(f"\n{'=' * 120}")
