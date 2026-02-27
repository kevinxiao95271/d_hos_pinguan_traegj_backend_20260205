# -*- coding: utf-8 -*-
"""
执行字典同步 - 与标准列表对齐
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
print("Execute Dictionary Synchronization")
print("=" * 120)

# ============================================================
# STEP 1: Data Migration (12 records)
# ============================================================
print(f"\n{'=' * 120}")
print("[STEP 1] Data Migration")
print("=" * 120)

# Migration 1: QC_CIRCLE -> qc_topic
print(f"\n[Migration 1] QC_CIRCLE -> qc_topic")
cursor.execute("""
    SELECT COUNT(*) as count FROM activity_infos 
    WHERE method_code = 'QC_CIRCLE'
""")
count1 = cursor.fetchone()['count']
print(f"  Records to migrate: {count1}")

if count1 > 0:
    cursor.execute("""
        UPDATE activity_infos 
        SET method_code = 'qc_topic' 
        WHERE method_code = 'QC_CIRCLE'
    """)
    conn.commit()
    print(f"  [SUCCESS] Migrated {count1} records: QC_CIRCLE -> qc_topic")

# Migration 2: antibiotic_pathogen_test -> other
print(f"\n[Migration 2] antibiotic_pathogen_test -> other")
cursor.execute("""
    SELECT COUNT(*) as count FROM activity_infos 
    WHERE quality_topic_code = 'antibiotic_pathogen_test'
""")
count2 = cursor.fetchone()['count']
print(f"  Records to migrate: {count2}")

if count2 > 0:
    cursor.execute("""
        UPDATE activity_infos 
        SET quality_topic_code = 'other' 
        WHERE quality_topic_code = 'antibiotic_pathogen_test'
    """)
    conn.commit()
    print(f"  [SUCCESS] Migrated {count2} records: antibiotic_pathogen_test -> other")

total_migrated = count1 + count2
print(f"\n[STEP 1 COMPLETE] Total migrated: {total_migrated} records")

# ============================================================
# STEP 2: Delete Extra Items (2 items)
# ============================================================
print(f"\n{'=' * 120}")
print("[STEP 2] Delete Extra Items")
print("=" * 120)

# Delete 1: QC_CIRCLE
print(f"\n[Delete 1] QC_CIRCLE (id=56)")
cursor.execute("""
    DELETE FROM dictionary_items 
    WHERE id = 56 AND code = 'QC_CIRCLE'
""")
deleted1 = cursor.rowcount
conn.commit()
print(f"  [SUCCESS] Deleted {deleted1} item(s)")

# Delete 2: antibiotic_pathogen_test
print(f"\n[Delete 2] antibiotic_pathogen_test (id=113)")
cursor.execute("""
    DELETE FROM dictionary_items 
    WHERE id = 113 AND code = 'antibiotic_pathogen_test'
""")
deleted2 = cursor.rowcount
conn.commit()
print(f"  [SUCCESS] Deleted {deleted2} item(s)")

total_deleted = deleted1 + deleted2
print(f"\n[STEP 2 COMPLETE] Total deleted: {total_deleted} items")

# ============================================================
# STEP 3: Add Missing Items (5 items)
# ============================================================
print(f"\n{'=' * 120}")
print("[STEP 3] Add Missing Items")
print("=" * 120)

# Add 1: method - FOCUS-PDCA
print(f"\n[Add 1] method: FOCUS-PDCA")
cursor.execute("""
    INSERT INTO dictionary_items (type, code, label, active, created_at)
    VALUES ('method', 'focus_pdca', 'FOCUS-PDCA', 1, NOW())
""")
conn.commit()
print(f"  [SUCCESS] Added: FOCUS-PDCA (code=focus_pdca)")

# Add 2: experience_improve - 患者住院体验更加舒适
print(f"\n[Add 2] experience_improve: 患者住院体验更加舒适")
cursor.execute("""
    INSERT INTO dictionary_items (type, code, label, active, created_at)
    VALUES ('experience_improve', 'inpatient_comfort', '患者住院体验更加舒适', 1, NOW())
""")
conn.commit()
print(f"  [SUCCESS] Added: 患者住院体验更加舒适 (code=inpatient_comfort)")

# Add 3: quality_topic - 提高肿瘤治疗前临床 TNM 分期评估率
print(f"\n[Add 3] quality_topic: 提高肿瘤治疗前临床 TNM 分期评估率")
cursor.execute("""
    INSERT INTO dictionary_items (type, code, label, active, created_at)
    VALUES ('quality_topic', 'tumor_tnm_staging', '提高肿瘤治疗前临床 TNM 分期评估率', 1, NOW())
""")
conn.commit()
print(f"  [SUCCESS] Added: 提高肿瘤治疗前临床 TNM 分期评估率 (code=tumor_tnm_staging)")

# Add 4: quality_topic - 提高住院患者静脉输液规范使用率
print(f"\n[Add 4] quality_topic: 提高住院患者静脉输液规范使用率")
cursor.execute("""
    INSERT INTO dictionary_items (type, code, label, active, created_at)
    VALUES ('quality_topic', 'iv_infusion_standard', '提高住院患者静脉输液规范使用率', 1, NOW())
""")
conn.commit()
print(f"  [SUCCESS] Added: 提高住院患者静脉输液规范使用率 (code=iv_infusion_standard)")

# Add 5: quality_topic - 提高医疗机构检查检验结果互认率
print(f"\n[Add 5] quality_topic: 提高医疗机构检查检验结果互认率")
cursor.execute("""
    INSERT INTO dictionary_items (type, code, label, active, created_at)
    VALUES ('quality_topic', 'test_result_mutual_recognition', '提高医疗机构检查检验结果互认率', 1, NOW())
""")
conn.commit()
print(f"  [SUCCESS] Added: 提高医疗机构检查检验结果互认率 (code=test_result_mutual_recognition)")

print(f"\n[STEP 3 COMPLETE] Total added: 5 items")

# ============================================================
# STEP 4: Verification
# ============================================================
print(f"\n{'=' * 120}")
print("[STEP 4] Verification")
print("=" * 120)

types = ['subject_type', 'method', 'experience_improve', 'quality_topic']
expected_counts = {
    'subject_type': 11,
    'method': 17,
    'experience_improve': 8,
    'quality_topic': 14
}

all_match = True

for dict_type in types:
    cursor.execute("""
        SELECT COUNT(*) as count FROM dictionary_items
        WHERE type = %s AND active = 1
    """, (dict_type,))
    
    actual_count = cursor.fetchone()['count']
    expected_count = expected_counts[dict_type]
    
    if actual_count == expected_count:
        print(f"  [{dict_type}] Count: {actual_count}/{expected_count} [OK]")
    else:
        print(f"  [{dict_type}] Count: {actual_count}/{expected_count} [MISMATCH]")
        all_match = False

cursor.close()
conn.close()

print(f"\n{'=' * 120}")
print("[EXECUTION COMPLETE]")
print("=" * 120)

print(f"\nSummary:")
print(f"  Step 1: Migrated {total_migrated} records")
print(f"  Step 2: Deleted {total_deleted} items")
print(f"  Step 3: Added 5 items")
print(f"  Step 4: Verification {'PASSED' if all_match else 'FAILED'}")

print(f"\nNext steps:")
print(f"  1. Run comparison script to verify all labels match")
print(f"  2. Test dictionary APIs")
print(f"  3. Verify 'other' option is still at the end")

print(f"\n{'=' * 120}")
