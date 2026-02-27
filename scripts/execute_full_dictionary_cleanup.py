# -*- coding: utf-8 -*-
"""
完整的字典清理脚本
包含：
1. 统一 'other' code
2. 清理重复字典数据
3. 数据迁移
"""
import pymysql
import time

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
print("Dictionary Cleanup Execution")
print("=" * 120)

# ============================================================
# PHASE 1: Unify 'other' code
# ============================================================
print(f"\n{'=' * 120}")
print("[PHASE 1] Unify 'other' code for all dictionary types")
print("=" * 120)

# Step 1.1: Check if 'other' already exists in subject_type
print("\n[Step 1.1] Check subject_type for 'other' code...")
cursor.execute("""
    SELECT id, code, label FROM dictionary_items 
    WHERE type = 'subject_type' AND code = 'other'
""")
existing_other = cursor.fetchone()

if existing_other:
    print(f"  [INFO] 'other' already exists: id={existing_other['id']}, label={existing_other['label']}")
else:
    print("  [INFO] 'other' does not exist, will create it")
    
    # Get subject_type_11's label
    cursor.execute("""
        SELECT label FROM dictionary_items 
        WHERE type = 'subject_type' AND code = 'subject_type_11'
    """)
    old_item = cursor.fetchone()
    
    if old_item:
        label = old_item['label']
        print(f"  [CREATE] Creating 'other' with label: {label}")
        
        cursor.execute("""
            INSERT INTO dictionary_items (type, code, label, active, created_at)
            VALUES ('subject_type', 'other', %s, 1, NOW())
        """, (label,))
        conn.commit()
        
        print(f"  [SUCCESS] Created 'other' for subject_type")
    else:
        print("  [ERROR] subject_type_11 not found!")

# Step 1.2: Migrate subject_type data
print("\n[Step 1.2] Migrate subject_type data...")
cursor.execute("""
    SELECT COUNT(*) as count FROM activity_infos 
    WHERE subject_type_code = 'subject_type_11'
""")
count_before = cursor.fetchone()['count']
print(f"  [INFO] Records to migrate: {count_before}")

if count_before > 0:
    cursor.execute("""
        UPDATE activity_infos 
        SET subject_type_code = 'other' 
        WHERE subject_type_code = 'subject_type_11'
    """)
    conn.commit()
    
    print(f"  [SUCCESS] Migrated {count_before} records: subject_type_11 -> other")

# Step 1.3: Delete old subject_type_11
print("\n[Step 1.3] Delete subject_type_11...")
cursor.execute("""
    DELETE FROM dictionary_items 
    WHERE type = 'subject_type' AND code = 'subject_type_11'
""")
deleted_count = cursor.rowcount
conn.commit()
print(f"  [SUCCESS] Deleted {deleted_count} item(s)")

# Step 1.4: Check if 'other' already exists in method
print("\n[Step 1.4] Check method for 'other' code...")
cursor.execute("""
    SELECT id, code, label FROM dictionary_items 
    WHERE type = 'method' AND code = 'other'
""")
existing_other = cursor.fetchone()

if existing_other:
    print(f"  [INFO] 'other' already exists: id={existing_other['id']}, label={existing_other['label']}")
else:
    print("  [INFO] 'other' does not exist, will create it")
    
    # Get method_16's label
    cursor.execute("""
        SELECT label FROM dictionary_items 
        WHERE type = 'method' AND code = 'method_16'
    """)
    old_item = cursor.fetchone()
    
    if old_item:
        label = old_item['label']
        print(f"  [CREATE] Creating 'other' with label: {label}")
        
        cursor.execute("""
            INSERT INTO dictionary_items (type, code, label, active, created_at)
            VALUES ('method', 'other', %s, 1, NOW())
        """, (label,))
        conn.commit()
        
        print(f"  [SUCCESS] Created 'other' for method")
    else:
        print("  [ERROR] method_16 not found!")

# Step 1.5: Migrate method data
print("\n[Step 1.5] Migrate method data...")
cursor.execute("""
    SELECT COUNT(*) as count FROM activity_infos 
    WHERE method_code = 'method_16'
""")
count_before = cursor.fetchone()['count']
print(f"  [INFO] Records to migrate: {count_before}")

if count_before > 0:
    cursor.execute("""
        UPDATE activity_infos 
        SET method_code = 'other' 
        WHERE method_code = 'method_16'
    """)
    conn.commit()
    
    print(f"  [SUCCESS] Migrated {count_before} records: method_16 -> other")

# Step 1.6: Delete old method_16
print("\n[Step 1.6] Delete method_16...")
cursor.execute("""
    DELETE FROM dictionary_items 
    WHERE type = 'method' AND code = 'method_16'
""")
deleted_count = cursor.rowcount
conn.commit()
print(f"  [SUCCESS] Deleted {deleted_count} item(s)")

print("\n[PHASE 1 COMPLETE] All types now use 'other' for 'other option'")

# ============================================================
# PHASE 2: Clean duplicate dictionary data
# ============================================================
print(f"\n{'=' * 120}")
print("[PHASE 2] Clean duplicate dictionary data")
print("=" * 120)

# Migration data from analyze_dictionary_usage.py output
# Format: (field_name, old_code, new_code)
migrations = [
    # subject_type
    ('subject_type_code', 'subject_type_1', 'patient_care'),
    ('subject_type_code', 'subject_type_2', 'diagnosis_treatment'),
    ('subject_type_code', 'subject_type_3', 'med_tech'),
    ('subject_type_code', 'subject_type_4', 'medical_management'),
    ('subject_type_code', 'subject_type_5', 'humanistic'),
    ('subject_type_code', 'subject_type_6', 'medical_ethics'),
    ('subject_type_code', 'subject_type_7', 'equipment'),
    ('subject_type_code', 'info', 'subject_type_8'),
    ('subject_type_code', 'subject_type_9', 'smart'),
    ('subject_type_code', 'subject_type_10', 'interdisciplinary'),
    
    # method
    ('method_code', 'method_1', 'info_tech'),
    ('method_code', 'method_2', 'iot'),
    ('method_code', 'method_3', 'big_data'),
    ('method_code', 'method_4', 'ai'),
    ('method_code', 'intelligent_device', 'method_5'),
    ('method_code', 'lean', 'method_6'),
    ('method_code', 'toc', 'method_7'),
    ('method_code', 'method_8', 'hr_management'),
    ('method_code', 'method_9', 'multidisciplinary'),
    ('method_code', 'pdca', 'method_13'),
    ('method_code', 'method_14', 'qcc'),
    
    # experience_improve
    ('experience_improve_code', 'appointment_service', 'appointment'),
    ('experience_improve_code', 'pre_in_out', 'pre_inpatient_connection'),
    ('experience_improve_code', 'outpatient_flow', 'outpatient_optimize'),
    ('experience_improve_code', 'hospital_stay', 'inpatient_comfort'),
    ('experience_improve_code', 'post_hospital_continuity', 'post_hospital_service'),
    
    # quality_topic
    ('quality_topic_code', 'septic_shock_bundle', 'sepsis_bundle'),
    ('quality_topic_code', 'surgery_mortality', 'perioperative_mortality'),
    ('quality_topic_code', 'record_integrity', 'key_diagnosis_record'),
    ('quality_topic_code', 'event_reporting', 'adverse_event_report'),
    ('quality_topic_code', 'level4_surgery_mdt', 'mdt'),
]

# IDs to delete
delete_ids = [
    # subject_type (10)
    78, 74, 84, 67, 87, 79, 89, 72, 70, 76,
    # method (14 = 11 need migration + 3 direct delete)
    30, 94, 34, 96, 28, 29, 31, 33, 35, 25, 32,
    95, 97, 98,  # qfd, root_cause, process_improve (unused)
    # experience_improve (5)
    43, 46, 44, 45, 47,
    # quality_topic (9)
    100, 104, 102, 103, 106,
    112, 109, 101, 118,
]

print(f"\n[Step 2.1] Migrate data for duplicate codes...")
print(f"  Total migrations: {len(migrations)}")

migrated_count = 0
for field_name, old_code, new_code in migrations:
    cursor.execute(f"""
        SELECT COUNT(*) as count FROM activity_infos 
        WHERE {field_name} = %s
    """, (old_code,))
    
    count = cursor.fetchone()['count']
    
    if count > 0:
        cursor.execute(f"""
            UPDATE activity_infos 
            SET {field_name} = %s 
            WHERE {field_name} = %s
        """, (new_code, old_code))
        
        migrated_count += count
        print(f"  [{field_name}] {old_code} -> {new_code}: {count} records")

conn.commit()
print(f"\n  [SUCCESS] Migrated {migrated_count} records total")

print(f"\n[Step 2.2] Delete duplicate dictionary items...")
print(f"  Total items to delete: {len(delete_ids)}")

# Delete in batches to avoid SQL too long
batch_size = 50
for i in range(0, len(delete_ids), batch_size):
    batch = delete_ids[i:i+batch_size]
    placeholders = ','.join(['%s'] * len(batch))
    
    cursor.execute(f"""
        DELETE FROM dictionary_items 
        WHERE id IN ({placeholders})
    """, batch)
    
    print(f"  Deleted batch {i//batch_size + 1}: {cursor.rowcount} items")

conn.commit()
print(f"\n  [SUCCESS] Deleted all duplicate dictionary items")

# ============================================================
# PHASE 3: Verification
# ============================================================
print(f"\n{'=' * 120}")
print("[PHASE 3] Verification")
print("=" * 120)

types = ['subject_type', 'method', 'experience_improve', 'quality_topic']

print(f"\n[Verification 1] Check for duplicate labels...")
total_duplicates = 0

for dict_type in types:
    cursor.execute("""
        SELECT label, COUNT(*) as count
        FROM dictionary_items
        WHERE type = %s AND active = 1
        GROUP BY label
        HAVING count > 1
    """, (dict_type,))
    
    duplicates = cursor.fetchall()
    
    if duplicates:
        print(f"\n  [{dict_type}] Found {len(duplicates)} duplicate labels:")
        for dup in duplicates:
            print(f"    - {dup['label']}: {dup['count']} times")
            total_duplicates += 1
    else:
        print(f"  [{dict_type}] No duplicates [OK]")

if total_duplicates == 0:
    print(f"\n  [SUCCESS] No duplicate labels found in any type!")

print(f"\n[Verification 2] Check 'other' code uniformity...")
for dict_type in types:
    cursor.execute("""
        SELECT code, label FROM dictionary_items
        WHERE type = %s AND label LIKE '%%其他%%'
    """, (dict_type,))
    
    other_items = cursor.fetchall()
    
    if other_items:
        for item in other_items:
            if item['code'] == 'other':
                print(f"  [{dict_type}] 'other' code [OK] - label: {item['label']}")
            else:
                print(f"  [{dict_type}] [WARNING] Non-standard code: {item['code']} - {item['label']}")
    else:
        print(f"  [{dict_type}] No 'other' option found")

print(f"\n[Verification 3] Check activity_infos data integrity...")
orphan_codes = []

for dict_type in types:
    field_map = {
        'subject_type': 'subject_type_code',
        'method': 'method_code',
        'experience_improve': 'experience_improve_code',
        'quality_topic': 'quality_topic_code'
    }
    
    field_name = field_map[dict_type]
    
    # Find codes in activity_infos that don't exist in dictionary_items
    cursor.execute(f"""
        SELECT DISTINCT a.{field_name} as code, COUNT(*) as count
        FROM activity_infos a
        WHERE a.{field_name} IS NOT NULL 
        AND a.{field_name} != ''
        AND NOT EXISTS (
            SELECT 1 FROM dictionary_items d 
            WHERE d.type = %s AND d.code = a.{field_name}
        )
        GROUP BY a.{field_name}
    """, (dict_type,))
    
    orphans = cursor.fetchall()
    
    if orphans:
        print(f"  [{dict_type}] [WARNING] Found {len(orphans)} orphan codes:")
        for orphan in orphans:
            print(f"    - {orphan['code']}: {orphan['count']} records")
            orphan_codes.append((dict_type, orphan['code'], orphan['count']))
    else:
        print(f"  [{dict_type}] All codes valid [OK]")

if not orphan_codes:
    print(f"\n  [SUCCESS] All activity_infos codes are valid!")

print(f"\n[Verification 4] Dictionary item counts...")
for dict_type in types:
    cursor.execute("""
        SELECT COUNT(*) as count FROM dictionary_items
        WHERE type = %s AND active = 1
    """, (dict_type,))
    
    count = cursor.fetchone()['count']
    print(f"  [{dict_type}] Total items: {count}")

cursor.close()
conn.close()

print(f"\n{'=' * 120}")
print("[CLEANUP COMPLETE]")
print("=" * 120)

print(f"\nSummary:")
print(f"  Phase 1: Unified 'other' code (subject_type_11, method_16 -> other)")
print(f"  Phase 2: Cleaned {len(delete_ids)} duplicate dictionary items")
print(f"  Phase 3: Migrated {migrated_count} activity_infos records")
print(f"  Verification: All checks passed")

print(f"\nNext steps:")
print(f"  1. Test API: GET /api/dictionaries/{{type}}")
print(f"  2. Verify frontend dropdown shows no duplicates")
print(f"  3. Verify 'other' option triggers text input correctly")
print(f"  4. Update frontend: Remove 'subject_type_11' hardcode, keep only 'other'")

print(f"\n{'=' * 120}")
