#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
执行SQL修正舟山医院的methodCode
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import pymysql

DB_CONFIG = {
    'host': '1.94.176.95',
    'user': 'wjx',
    'password': 'kevinxiao',
    'database': 'pinguan_db',
    'charset': 'utf8mb4',
    'port': 3306
}

def execute_fix():
    """执行修正SQL"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        print("=" * 100)
        print("开始修正舟山医院的methodCode")
        print("=" * 100)
        
        # 先查询当前状态
        print("\n修正前的数据：")
        cursor.execute("""
            SELECT 
                r.id as registration_id,
                r.project_name,
                a.method_code
            FROM registrations r
            LEFT JOIN activity_infos a ON a.registration_id = r.id
            WHERE r.institution_id = (SELECT id FROM institutions WHERE name = '舟山医院')
            ORDER BY r.id
        """)
        
        before_data = cursor.fetchall()
        for row in before_data:
            print(f"  ID={row['registration_id']}: {row['project_name'][:40]} | methodCode={row['method_code']}")
        
        # 执行修正
        print("\n" + "=" * 100)
        print("执行修正...")
        print("=" * 100)
        
        mappings = [
            ('qcc', 'qc_topic', '品管圈-课题达成'),
            ('benchmarking', 'method_7', '标杆学习'),
            ('process_reengineering', 'process_improve', '流程改造'),
            ('system_construct', 'process_improve', '流程改造'),
        ]
        
        for old_code, new_code, label in mappings:
            sql = """
                UPDATE activity_infos 
                SET method_code = %s
                WHERE method_code = %s
                  AND registration_id IN (
                    SELECT id FROM registrations 
                    WHERE institution_id = (SELECT id FROM institutions WHERE name = '舟山医院')
                  )
            """
            cursor.execute(sql, (new_code, old_code))
            affected = cursor.rowcount
            if affected > 0:
                print(f"✅ {old_code} -> {new_code} ({label}): 修改了 {affected} 条记录")
            else:
                print(f"⚪ {old_code} -> {new_code} ({label}): 没有需要修改的记录")
        
        # 提交事务
        conn.commit()
        print("\n✅ 事务已提交")
        
        # 查询修正后的状态
        print("\n" + "=" * 100)
        print("修正后的数据：")
        print("=" * 100)
        
        cursor.execute("""
            SELECT 
                r.id as registration_id,
                r.project_name,
                a.method_code
            FROM registrations r
            LEFT JOIN activity_infos a ON a.registration_id = r.id
            WHERE r.institution_id = (SELECT id FROM institutions WHERE name = '舟山医院')
            ORDER BY r.id
        """)
        
        after_data = cursor.fetchall()
        for row in after_data:
            print(f"  ID={row['registration_id']}: {row['project_name'][:40]} | methodCode={row['method_code']}")
        
        print("\n" + "=" * 100)
        print("修正完成！")
        print("=" * 100)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        conn.rollback()
        print("事务已回滚")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    execute_fix()
