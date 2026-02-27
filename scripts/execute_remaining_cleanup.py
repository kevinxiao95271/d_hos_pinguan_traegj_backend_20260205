# -*- coding: utf-8 -*-
"""
执行剩余的字典清理
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
print("Execute Remaining Cleanup")
print("=" * 120)

# Step 1: Migrate remaining data
print(f"\n[Step 1] Migrate remaining duplicate data...")

migrations = [
    ('method_code', 'six_sigma', 'method_11', 2),
    ('method_code', 'fmea', 'method_6', 1),
    ('method_code', 'method_12', 'ebm', 2),
    ('experience_improve_code', 'comfortable_environment', 'environment', 10),
    ('quality_topic_code', 'stemi_reperfusion', 'stemi', 3),
]

total_migrated = 0

for field_name, old_code, new_code, expected_count in migrations:
    # Check current count
    cursor.execute(f"""
        SELECT COUNT(*) as count FROM activity_infos 
        WHERE {field_name} = %s
    """, (old_code,))
    
    actual_count = cursor.fetchone()['count']
    
    if actual_count > 0:
        cursor.execute(f"""
            UPDATE activity_infos 
            SET {field_name} = %s 
            WHERE {field_name} = %s
        """, (new_code, old_code))
        
        conn.commit()
        total_migrated += actual_count
        
        print(f"  [{field_name}] {old_code} -> {new_code}: {actual_count} records (expected {expected_count})")
    else:
        print(f"  [{field_name}] {old_code} -> {new_code}: already migrated or no records")

print(f"\n  [SUCCESS] Migrated {total_migrated} records total")

# Step 2: Delete remaining duplicates
print(f"\n[Step 2] Delete remaining duplicate items...")

delete_ids = [9, 5, 4, 7, 3, 10, 6, 1, 2, 19, 82, 80, 13, 75, 15, 23, 108, 105, 110, 116]

cursor.execute(f"""
    DELETE FROM dictionary_items 
    WHERE id IN ({','.join(['%s'] * len(delete_ids))})
""", delete_ids)

deleted_count = cursor.rowcount
conn.commit()

print(f"  [SUCCESS] Deleted {deleted_count} items (expected 20)")

cursor.close()
conn.close()

print(f"\n{'=' * 120}")
print("[REMAINING CLEANUP COMPLETE]")
print("=" * 120)

print(f"\nSummary:")
print(f"  Migrated: {total_migrated} records")
print(f"  Deleted: {deleted_count} dictionary items")

print(f"\n{'=' * 120}")
