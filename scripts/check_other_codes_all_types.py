# -*- coding: utf-8 -*-
"""
检查4个字典类型中所有"其他"相关的code
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
print("Check 'Other' related codes in all 4 dictionary types")
print("=" * 120)

types = ['subject_type', 'method', 'experience_improve', 'quality_topic']

for dict_type in types:
    print(f"\n{'=' * 120}")
    print(f"[{dict_type}]")
    print("-" * 120)
    
    # Find all items with label containing "其他" or code containing "other"
    cursor.execute("""
        SELECT id, code, label, active
        FROM dictionary_items
        WHERE type = %s
        AND (label LIKE '%%其他%%' OR code LIKE '%%other%%')
        ORDER BY id
    """, (dict_type,))
    
    other_items = cursor.fetchall()
    
    if other_items:
        print(f"\nFound {len(other_items)} 'other' related items:")
        
        field_map = {
            'subject_type': 'subject_type_code',
            'method': 'method_code',
            'experience_improve': 'experience_improve_code',
            'quality_topic': 'quality_topic_code'
        }
        
        for item in other_items:
            cursor.execute(f"""
                SELECT COUNT(*) as count
                FROM activity_infos
                WHERE {field_map[dict_type]} = %s
            """, (item['code'],))
            
            usage_count = cursor.fetchone()['count']
            
            print(f"  - id={item['id']:<4}, code={item['code']:<30}, label={item['label']:<40}, active={item['active']}, usage={usage_count}")
    else:
        print(f"\n[WARNING] No 'other' option found!")

cursor.close()
conn.close()

print(f"\n{'=' * 120}")
print("[Summary]")
print("=" * 120)

print(f"\nFrontend hardcoded values:")
print(f"  1. 'other' - Expected in all 4 types")
print(f"  2. 'subject_type_11' - Old 'other' code for subject_type")

print(f"\nRecommendations:")
print(f"  1. Standardize all types to use 'other' as the 'other option' code")
print(f"  2. Migrate data from old codes (subject_type_11, method_xx, etc.) to 'other'")
print(f"  3. Frontend only needs to check: if (code === 'other')")

print(f"\n{'=' * 120}")
