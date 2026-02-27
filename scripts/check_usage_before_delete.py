# -*- coding: utf-8 -*-
"""
检查需要删除的字典项是否被使用
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
print("Check Usage Before Deletion")
print("=" * 120)

# 需要检查的项目
items_to_check = [
    {
        'type': 'method',
        'code': 'QC_CIRCLE',
        'label': '品管圈',
        'field': 'method_code'
    },
    {
        'type': 'quality_topic',
        'code': 'antibiotic_pathogen_test',
        'label': '提高住院患者抗菌药物治疗前病原学送检率',
        'field': 'quality_topic_code'
    }
]

total_usage = 0

for item in items_to_check:
    print(f"\n{'=' * 120}")
    print(f"[{item['type']}] {item['label']}")
    print(f"  Code: {item['code']}")
    print("-" * 120)
    
    # 检查使用次数
    cursor.execute(f"""
        SELECT COUNT(*) as count
        FROM activity_infos
        WHERE {item['field']} = %s
    """, (item['code'],))
    
    usage = cursor.fetchone()['count']
    total_usage += usage
    
    if usage > 0:
        print(f"\n  [WARNING] This item is being used by {usage} records!")
        
        # 显示使用此code的记录
        cursor.execute(f"""
            SELECT r.id, r.project_name, r.status, r.applicant_id
            FROM registrations r
            JOIN activity_infos a ON r.id = a.registration_id
            WHERE a.{item['field']} = %s
            LIMIT 10
        """, (item['code'],))
        
        records = cursor.fetchall()
        
        print(f"\n  Sample records using this code (showing up to 10):")
        for rec in records:
            print(f"    - Registration ID={rec['id']}, Project={rec['project_name']}, Status={rec['status']}")
        
        if usage > 10:
            print(f"    ... and {usage - 10} more records")
        
        print(f"\n  [ACTION REQUIRED] Need to migrate {usage} records before deletion")
    else:
        print(f"\n  [OK] This item is NOT being used, safe to delete")

cursor.close()
conn.close()

print(f"\n{'=' * 120}")
print("[SUMMARY]")
print("=" * 120)

if total_usage > 0:
    print(f"\n[WARNING] Total {total_usage} records are using items to be deleted")
    print(f"  Action required: Migrate these records before deletion")
else:
    print(f"\n[OK] No records are using items to be deleted")
    print(f"  Safe to proceed with deletion")

print(f"\n{'=' * 120}")
