#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check for duplicate material file records
Each registration_id + type should have only one file
"""

import pymysql

# Database configuration
DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

def get_db_connection():
    """Get database connection"""
    return pymysql.connect(**DB_CONFIG)

def analyze_duplicates():
    """Analyze duplicate records"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    print("=" * 80)
    print("Analyzing duplicate material file records...")
    print("=" * 80)
    print()
    
    # Query duplicate groups
    query = """
    SELECT 
        registration_id,
        type,
        COUNT(*) as file_count,
        MIN(uploaded_at) as earliest_upload,
        MAX(uploaded_at) as latest_upload
    FROM material_files
    GROUP BY registration_id, type
    HAVING COUNT(*) > 1
    ORDER BY file_count DESC, registration_id, type
    """
    
    cursor.execute(query)
    duplicates = cursor.fetchall()
    
    if not duplicates:
        print("[OK] No duplicate records found! Database is clean.")
        print()
        cursor.close()
        conn.close()
        return []
    
    print(f"[WARNING] Found {len(duplicates)} groups of duplicate records:")
    print()
    
    total_files_to_delete = 0
    
    for dup in duplicates:
        print(f"Registration ID: {dup['registration_id']}, Type: {dup['type']}")
        print(f"  File count: {dup['file_count']}")
        print(f"  Earliest upload: {dup['earliest_upload']}")
        print(f"  Latest upload: {dup['latest_upload']}")
        total_files_to_delete += (dup['file_count'] - 1)
        print()
    
    print(f"Total files to delete: {total_files_to_delete}")
    print()
    
    # Get detailed info
    detail_query = """
    SELECT 
        mf1.id,
        mf1.registration_id,
        mf1.type,
        mf1.file_name,
        mf1.file_url,
        mf1.uploaded_at,
        CASE 
            WHEN mf1.id = (
                SELECT id FROM material_files mf2 
                WHERE mf2.registration_id = mf1.registration_id 
                AND mf2.type = mf1.type 
                ORDER BY uploaded_at DESC, id DESC 
                LIMIT 1
            ) THEN 'KEEP(latest)'
            ELSE 'DELETE(old)'
        END AS action
    FROM material_files mf1
    WHERE EXISTS (
        SELECT 1 
        FROM material_files mf2 
        WHERE mf2.registration_id = mf1.registration_id 
        AND mf2.type = mf1.type 
        AND mf2.id != mf1.id
    )
    ORDER BY mf1.registration_id, mf1.type, mf1.uploaded_at DESC
    """
    
    cursor.execute(detail_query)
    details = cursor.fetchall()
    
    print("=" * 80)
    print("Detailed records:")
    print("=" * 80)
    print()
    
    for record in details:
        print(f"ID: {record['id']} | Registration: {record['registration_id']} | Type: {record['type']}")
        print(f"  File: {record['file_name']}")
        print(f"  Uploaded: {record['uploaded_at']}")
        print(f"  Action: {record['action']}")
        print()
    
    cursor.close()
    conn.close()
    
    return duplicates

def main():
    """Main function"""
    print()
    print("=" * 80)
    print("Material File Duplicate Check Tool")
    print("=" * 80)
    print()
    
    duplicates = analyze_duplicates()
    
    if not duplicates:
        print("[INFO] Database is clean. No cleanup needed.")
    else:
        print("[INFO] Found duplicate records.")
        print("[INFO] To clean up, please:")
        print("  1. Review the details above")
        print("  2. Run the cleanup script if needed")
    
    print()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
