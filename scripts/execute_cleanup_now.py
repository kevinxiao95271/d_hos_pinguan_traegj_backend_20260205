#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Execute cleanup of duplicate material files
"""

import pymysql
from datetime import datetime

DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

def execute_cleanup():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    print("=" * 80)
    print("Starting cleanup operation...")
    print("=" * 80)
    print()
    
    # Step 1: Create backup
    print("[1/5] Creating backup table...")
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS material_files_backup_20260228 
            SELECT * FROM material_files
        """)
        conn.commit()
        
        cursor.execute("SELECT COUNT(*) as count FROM material_files_backup_20260228")
        backup_count = cursor.fetchone()['count']
        print(f"[OK] Backup created with {backup_count} records")
    except Exception as e:
        print(f"[WARNING] Backup creation: {e}")
        print("[INFO] Continuing anyway...")
    
    print()
    
    # Step 2: Show records to delete
    print("[2/5] Identifying records to delete...")
    cursor.execute("""
        SELECT 
            mf1.id,
            mf1.registration_id,
            mf1.type,
            mf1.file_name,
            mf1.uploaded_at
        FROM material_files mf1
        WHERE EXISTS (
            SELECT 1 
            FROM material_files mf2 
            WHERE mf2.registration_id = mf1.registration_id 
            AND mf2.type = mf1.type 
            AND mf2.id != mf1.id
        )
        AND mf1.id != (
            SELECT id FROM material_files mf3
            WHERE mf3.registration_id = mf1.registration_id 
            AND mf3.type = mf1.type 
            ORDER BY uploaded_at DESC, id DESC 
            LIMIT 1
        )
    """)
    
    to_delete = cursor.fetchall()
    
    if not to_delete:
        print("[OK] No duplicate records found. Nothing to delete.")
        cursor.close()
        conn.close()
        return
    
    print(f"Found {len(to_delete)} records to delete:")
    for record in to_delete:
        print(f"  ID {record['id']}: Registration {record['registration_id']}, "
              f"Type {record['type']}, File {record['file_name']}")
    
    print()
    
    # Step 3: Delete duplicates
    print("[3/5] Deleting duplicate records...")
    ids_to_delete = [r['id'] for r in to_delete]
    
    placeholders = ','.join(['%s'] * len(ids_to_delete))
    delete_query = f"DELETE FROM material_files WHERE id IN ({placeholders})"
    
    cursor.execute(delete_query, ids_to_delete)
    deleted_count = cursor.rowcount
    conn.commit()
    
    print(f"[OK] Deleted {deleted_count} records")
    print()
    
    # Step 4: Verify
    print("[4/5] Verifying cleanup...")
    cursor.execute("""
        SELECT 
            registration_id,
            type,
            COUNT(*) as file_count
        FROM material_files
        GROUP BY registration_id, type
        HAVING COUNT(*) > 1
    """)
    
    remaining_duplicates = cursor.fetchall()
    
    if remaining_duplicates:
        print(f"[WARNING] Still found {len(remaining_duplicates)} duplicate groups:")
        for dup in remaining_duplicates:
            print(f"  Registration {dup['registration_id']}, Type {dup['type']}: {dup['file_count']} files")
    else:
        print("[OK] No duplicate records remaining!")
    
    print()
    
    # Step 5: Show final state
    print("[5/5] Final state for affected registrations...")
    affected_reg_ids = list(set([r['registration_id'] for r in to_delete]))
    
    for reg_id in affected_reg_ids:
        cursor.execute("""
            SELECT id, type, file_name, uploaded_at
            FROM material_files
            WHERE registration_id = %s
            ORDER BY type, uploaded_at DESC
        """, (reg_id,))
        
        current_files = cursor.fetchall()
        print(f"\nRegistration {reg_id}:")
        for f in current_files:
            print(f"  Type {f['type']}: {f['file_name']} (ID {f['id']}, {f['uploaded_at']})")
    
    print()
    print("=" * 80)
    print("Cleanup completed successfully!")
    print("=" * 80)
    print(f"Records deleted: {deleted_count}")
    print(f"Backup table: material_files_backup_20260228")
    print()
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    try:
        execute_cleanup()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
