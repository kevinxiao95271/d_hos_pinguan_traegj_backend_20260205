#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clean up duplicate material file records
Keep only the latest file per registration_id + type
"""

import pymysql
from minio import Minio

# Database configuration
DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

# MinIO configuration
MINIO_CONFIG = {
    'endpoint': '119.167.165.27:58010',
    'access_key': 'minioadmin',
    'secret_key': 'Ygcx2025',
    'bucket': 'registration-files',
    'secure': False
}

def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

def get_minio_client():
    return Minio(
        MINIO_CONFIG['endpoint'],
        access_key=MINIO_CONFIG['access_key'],
        secret_key=MINIO_CONFIG['secret_key'],
        secure=MINIO_CONFIG['secure']
    )

def get_files_to_delete():
    """Get files that need to be deleted (keep only latest)"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    query = """
    SELECT 
        mf1.id,
        mf1.registration_id,
        mf1.type,
        mf1.file_name,
        mf1.file_url,
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
    ORDER BY mf1.registration_id, mf1.type, mf1.uploaded_at DESC
    """
    
    cursor.execute(query)
    files = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return files

def cleanup():
    """Execute cleanup"""
    files_to_delete = get_files_to_delete()
    
    if not files_to_delete:
        print("[OK] No duplicate files to clean up")
        return
    
    print(f"Found {len(files_to_delete)} old files to delete:")
    print()
    
    for file in files_to_delete:
        print(f"ID: {file['id']} | Registration: {file['registration_id']} | Type: {file['type']}")
        print(f"  File: {file['file_name']}")
        print(f"  Uploaded: {file['uploaded_at']}")
        print()
    
    print("=" * 80)
    confirm = input("Proceed with deletion? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Operation cancelled")
        return
    
    # Initialize MinIO client
    minio_client = None
    delete_minio = input("Delete MinIO files as well? (yes/no): ").strip().lower()
    if delete_minio == 'yes':
        try:
            minio_client = get_minio_client()
            print("[OK] MinIO client connected")
        except Exception as e:
            print(f"[WARNING] MinIO connection failed: {e}")
            print("Will only delete database records")
            minio_client = None
    
    # Execute deletion
    conn = get_db_connection()
    cursor = conn.cursor()
    
    deleted_db = 0
    deleted_minio = 0
    
    print()
    print("Starting cleanup...")
    print()
    
    for file in files_to_delete:
        try:
            # Delete MinIO file
            if minio_client and file['file_url']:
                try:
                    minio_client.remove_object(MINIO_CONFIG['bucket'], file['file_url'])
                    deleted_minio += 1
                    print(f"[OK] Deleted MinIO: {file['file_url']}")
                except Exception as e:
                    print(f"[FAIL] MinIO delete failed {file['file_url']}: {e}")
            
            # Delete database record
            cursor.execute("DELETE FROM material_files WHERE id = %s", (file['id'],))
            deleted_db += 1
            print(f"[OK] Deleted DB record: ID={file['id']}")
            
        except Exception as e:
            print(f"[FAIL] Delete failed ID={file['id']}: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print()
    print("=" * 80)
    print("Cleanup completed!")
    print(f"DB records deleted: {deleted_db}")
    if minio_client:
        print(f"MinIO files deleted: {deleted_minio}")
    print()

def main():
    print()
    print("=" * 80)
    print("Material File Cleanup Tool")
    print("=" * 80)
    print()
    
    cleanup()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Operation interrupted")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
