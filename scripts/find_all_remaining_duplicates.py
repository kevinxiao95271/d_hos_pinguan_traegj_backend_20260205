# -*- coding: utf-8 -*-
"""
找出所有剩余的重复 label
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
print("Find All Remaining Duplicate Labels")
print("=" * 120)

types = ['subject_type', 'method', 'experience_improve', 'quality_topic']

field_map = {
    'subject_type': 'subject_type_code',
    'method': 'method_code',
    'experience_improve': 'experience_improve_code',
    'quality_topic': 'quality_topic_code'
}

all_migrations = []
all_deletes = []

for dict_type in types:
    print(f"\n{'=' * 120}")
    print(f"[{dict_type}]")
    print("-" * 120)
    
    # Find duplicate labels
    cursor.execute("""
        SELECT label, GROUP_CONCAT(id ORDER BY id) as ids, 
               GROUP_CONCAT(code ORDER BY id) as codes,
               COUNT(*) as count
        FROM dictionary_items
        WHERE type = %s AND active = 1
        GROUP BY label
        HAVING count > 1
        ORDER BY label
    """, (dict_type,))
    
    duplicates = cursor.fetchall()
    
    if not duplicates:
        print(f"\n  No duplicates found [OK]")
        continue
    
    print(f"\nFound {len(duplicates)} duplicate labels:\n")
    
    for dup in duplicates:
        label = dup['label']
        ids = dup['ids'].split(',')
        codes = dup['codes'].split(',')
        
        print(f"  Label: {label}")
        print(f"  Codes: {', '.join(codes)}")
        
        # Get usage count for each code
        usage_counts = []
        for code in codes:
            cursor.execute(f"""
                SELECT COUNT(*) as count
                FROM activity_infos
                WHERE {field_map[dict_type]} = %s
            """, (code,))
            
            count = cursor.fetchone()['count']
            usage_counts.append(count)
        
        # Determine which code to keep
        max_usage = max(usage_counts)
        keep_index = usage_counts.index(max_usage)
        
        # If multiple codes have same max usage, prefer semantic ones
        if usage_counts.count(max_usage) > 1:
            # Prefer codes without underscores followed by numbers (e.g., prefer 'patient_care' over 'subject_type_1')
            semantic_codes = [i for i, code in enumerate(codes) if not code.split('_')[-1].isdigit()]
            if semantic_codes and keep_index not in semantic_codes:
                keep_index = semantic_codes[0]
        
        keep_code = codes[keep_index]
        keep_id = ids[keep_index]
        
        print(f"  Usage counts: {', '.join([f'{codes[i]}={usage_counts[i]}' for i in range(len(codes))])}")
        print(f"  Decision: Keep '{keep_code}' (id={keep_id}, usage={usage_counts[keep_index]})")
        
        # Generate migrations for others
        for i in range(len(codes)):
            if i != keep_index:
                delete_code = codes[i]
                delete_id = ids[i]
                delete_usage = usage_counts[i]
                
                if delete_usage > 0:
                    print(f"  Action: Migrate {delete_usage} records from '{delete_code}' to '{keep_code}'")
                    all_migrations.append((field_map[dict_type], delete_code, keep_code, delete_usage))
                else:
                    print(f"  Action: Delete '{delete_code}' (id={delete_id}, no usage)")
                
                all_deletes.append((dict_type, delete_id, delete_code))
        
        print()

cursor.close()
conn.close()

# Generate SQL
print(f"\n{'=' * 120}")
print("[SQL SCRIPT - Phase 2 Continued]")
print("=" * 120)

print(f"\n-- Step 1: Migrate remaining duplicate data ({len(all_migrations)} migrations)")
print(f"-- Total records to migrate: {sum(m[3] for m in all_migrations)}")
print()

for field_name, old_code, new_code, count in all_migrations:
    print(f"UPDATE activity_infos SET {field_name} = '{new_code}' WHERE {field_name} = '{old_code}';")
    print(f"-- Migrated {count} records: {old_code} -> {new_code}")
    print()

print(f"\n-- Step 2: Delete remaining duplicate items ({len(all_deletes)} items)")
print()

delete_ids = [d[1] for d in all_deletes]
print(f"DELETE FROM dictionary_items WHERE id IN ({','.join(delete_ids)});")
print(f"-- Deleted {len(delete_ids)} duplicate dictionary items")

print(f"\n{'=' * 120}")
print("[SUMMARY]")
print("=" * 120)

print(f"\nRemaining cleanup:")
print(f"  Migrations needed: {len(all_migrations)}")
print(f"  Records to migrate: {sum(m[3] for m in all_migrations)}")
print(f"  Items to delete: {len(all_deletes)}")

print(f"\n{'=' * 120}")
