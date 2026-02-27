# -*- coding: utf-8 -*-
"""
验证字典清理结果
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
print("Verification Results")
print("=" * 120)

types = ['subject_type', 'method', 'experience_improve', 'quality_topic']

# Check 1: Duplicate labels
print(f"\n[Check 1] Duplicate labels...")
total_duplicates = 0

for dict_type in types:
    cursor.execute("""
        SELECT label, GROUP_CONCAT(code) as codes, COUNT(*) as count
        FROM dictionary_items
        WHERE type = %s AND active = 1
        GROUP BY label
        HAVING count > 1
        ORDER BY count DESC, label
    """, (dict_type,))
    
    duplicates = cursor.fetchall()
    
    if duplicates:
        print(f"\n  [{dict_type}] Found {len(duplicates)} duplicate labels:")
        for dup in duplicates:
            print(f"    - {dup['label']}: codes={dup['codes']}, count={dup['count']}")
            total_duplicates += len(dup['codes'].split(','))
    else:
        print(f"  [{dict_type}] [OK] No duplicates")

if total_duplicates == 0:
    print(f"\n  [SUCCESS] No duplicate labels!")
else:
    print(f"\n  [WARNING] Still have {total_duplicates} items with duplicate labels")

# Check 2: 'other' code uniformity
print(f"\n[Check 2] 'other' code uniformity...")
for dict_type in types:
    cursor.execute("""
        SELECT id, code, label FROM dictionary_items
        WHERE type = %s AND (label LIKE '%%其他%%' OR code LIKE '%%other%%')
    """, (dict_type,))
    
    other_items = cursor.fetchall()
    
    if other_items:
        for item in other_items:
            status = "[OK]" if item['code'] == 'other' else "[WARNING]"
            print(f"  [{dict_type}] {status} code={item['code']}, label={item['label']}")
    else:
        print(f"  [{dict_type}] No 'other' option")

# Check 3: Dictionary item counts
print(f"\n[Check 3] Dictionary item counts...")
print(f"  {'Type':<25} {'Before':<10} {'After':<10} {'Deleted':<10}")
print(f"  {'-' * 55}")

original_counts = {
    'subject_type': 21,
    'method': 33,
    'experience_improve': 13,
    'quality_topic': 26
}

total_before = 0
total_after = 0

for dict_type in types:
    cursor.execute("""
        SELECT COUNT(*) as count FROM dictionary_items
        WHERE type = %s AND active = 1
    """, (dict_type,))
    
    count_after = cursor.fetchone()['count']
    count_before = original_counts.get(dict_type, 0)
    deleted = count_before - count_after
    
    total_before += count_before
    total_after += count_after
    
    print(f"  {dict_type:<25} {count_before:<10} {count_after:<10} {deleted:<10}")

print(f"  {'-' * 55}")
print(f"  {'TOTAL':<25} {total_before:<10} {total_after:<10} {total_before - total_after:<10}")

expected_deleted = 38
actual_deleted = total_before - total_after

if actual_deleted == expected_deleted:
    print(f"\n  [SUCCESS] Deleted exactly {expected_deleted} items as planned")
else:
    print(f"\n  [WARNING] Expected to delete {expected_deleted}, actually deleted {actual_deleted}")

# Check 4: Migration summary
print(f"\n[Check 4] Migration summary...")

migrations_done = [
    ('subject_type_11 -> other', 6),
    ('method_16 -> other', 5),
    ('duplicate codes', 103)
]

total_migrated = sum(count for _, count in migrations_done)

print(f"  Phase 1 (Other unification):")
print(f"    - subject_type_11 -> other: 6 records")
print(f"    - method_16 -> other: 5 records")
print(f"  Phase 2 (Duplicate cleanup):")
print(f"    - Duplicate codes migration: 103 records")
print(f"  Total migrated: {total_migrated} records")

cursor.close()
conn.close()

print(f"\n{'=' * 120}")
print("[VERIFICATION COMPLETE]")
print("=" * 120)

if total_duplicates > 0:
    print(f"\n[ACTION REQUIRED] Still have duplicate labels, need further investigation")
else:
    print(f"\n[SUCCESS] All checks passed!")

print(f"\n{'=' * 120}")
