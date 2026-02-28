#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Execute script to add external institutions
"""

import pymysql

DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

def execute_add_external_institutions():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    print("=" * 80)
    print("Adding External Institutions Support")
    print("=" * 80)
    print()
    
    try:
        # Step 1: Add is_ext column
        print("[1/4] Adding is_ext column to institutions table...")
        try:
            cursor.execute("""
                ALTER TABLE institutions 
                ADD COLUMN is_ext TINYINT NOT NULL DEFAULT 0 
                COMMENT '是否外部机构: 0-医院, 1-外部机构'
            """)
            conn.commit()
            print("[OK] is_ext column added successfully")
        except pymysql.err.OperationalError as e:
            if "Duplicate column name" in str(e):
                print("[INFO] is_ext column already exists, skipping...")
            else:
                raise
        
        print()
        
        # Step 2: Check current status
        print("[2/4] Checking current institutions...")
        cursor.execute("""
            SELECT 
                COUNT(*) AS total,
                SUM(CASE WHEN is_ext = 0 THEN 1 ELSE 0 END) AS hospitals,
                SUM(CASE WHEN is_ext = 1 THEN 1 ELSE 0 END) AS external
            FROM institutions
        """)
        stats = cursor.fetchone()
        print(f"Total institutions: {stats['total']}")
        print(f"  - Hospitals (is_ext=0): {stats['hospitals']}")
        print(f"  - External (is_ext=1): {stats['external']}")
        print()
        
        # Step 3: Insert external institutions
        print("[3/4] Inserting external institutions...")
        
        external_institutions = [
            {
                'name': '卡内基',
                'code': 'EXT_CARNEGIE',
                'uscc': 'EXT000000001',
                'region': '外部',
                'level': '外部机构'
            },
            {
                'name': '浙江省护理质控中心',
                'code': 'EXT_NURSING_QC',
                'uscc': 'EXT000000002',
                'region': '浙江省',
                'level': '外部机构'
            },
            {
                'name': '浙江省质量协会',
                'code': 'EXT_QUALITY_ASSOC',
                'uscc': 'EXT000000003',
                'region': '浙江省',
                'level': '外部机构'
            },
            {
                'name': '浙江省医疗服务管理评价中心',
                'code': 'EXT_MEDICAL_EVAL',
                'uscc': 'EXT000000004',
                'region': '浙江省',
                'level': '外部机构'
            }
        ]
        
        inserted_count = 0
        skipped_count = 0
        
        for inst in external_institutions:
            try:
                # Check if already exists
                cursor.execute("""
                    SELECT id FROM institutions 
                    WHERE code = %s OR uscc = %s
                """, (inst['code'], inst['uscc']))
                
                existing = cursor.fetchone()
                
                if existing:
                    print(f"[SKIP] {inst['name']} already exists (ID: {existing['id']})")
                    skipped_count += 1
                else:
                    cursor.execute("""
                        INSERT INTO institutions 
                        (name, code, uscc, region, level, is_ext, created_at) 
                        VALUES (%s, %s, %s, %s, %s, 1, NOW())
                    """, (inst['name'], inst['code'], inst['uscc'], 
                          inst['region'], inst['level']))
                    conn.commit()
                    new_id = cursor.lastrowid
                    print(f"[OK] Inserted: {inst['name']} (ID: {new_id})")
                    inserted_count += 1
                    
            except Exception as e:
                print(f"[ERROR] Failed to insert {inst['name']}: {e}")
        
        print()
        print(f"Inserted: {inserted_count}, Skipped: {skipped_count}")
        print()
        
        # Step 4: Display results
        print("[4/4] External institutions in database:")
        cursor.execute("""
            SELECT id, name, code, region, level, created_at
            FROM institutions
            WHERE is_ext = 1
            ORDER BY id
        """)
        
        external_insts = cursor.fetchall()
        
        if external_insts:
            print()
            for inst in external_insts:
                print(f"ID: {inst['id']}")
                print(f"  Name: {inst['name']}")
                print(f"  Code: {inst['code']}")
                print(f"  Region: {inst['region']}")
                print(f"  Level: {inst['level']}")
                print(f"  Created: {inst['created_at']}")
                print()
        else:
            print("[WARNING] No external institutions found!")
        
        # Final statistics
        print("=" * 80)
        print("Summary:")
        print("=" * 80)
        cursor.execute("""
            SELECT 
                is_ext,
                CASE WHEN is_ext = 0 THEN 'Hospital' ELSE 'External' END AS type,
                COUNT(*) AS count
            FROM institutions
            GROUP BY is_ext
            ORDER BY is_ext
        """)
        
        summary = cursor.fetchall()
        for row in summary:
            print(f"{row['type']}: {row['count']} institutions")
        
        print()
        print("[OK] External institutions setup completed!")
        print()
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    try:
        execute_add_external_institutions()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
