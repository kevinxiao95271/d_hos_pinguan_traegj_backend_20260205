#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查是否有报名记录使用了乱码的quality_topic code"""

import pymysql
from db_config import DB_CONFIG

# DB_CONFIG imported from db_config.py

def check_bad_usage():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        print("=" * 80)
        print("检查是否有报名记录使用了乱码的quality_topic code")
        print("=" * 80)
        
        bad_codes = [
            'quality_topic_1', 'quality_topic_2', 'quality_topic_3',
            'quality_topic_4', 'quality_topic_5', 'quality_topic_6',
            'quality_topic_7', 'quality_topic_8', 'quality_topic_9',
            'quality_topic_10', 'quality_topic_11'
        ]
        
        print(f"\n检查的code: {', '.join(bad_codes)}")
        print("")
        
        # 检查 activity_infos 表
        placeholders = ','.join(['%s'] * len(bad_codes))
        sql = f"""
        SELECT quality_topic_code, COUNT(*) as count
        FROM activity_infos
        WHERE quality_topic_code IN ({placeholders})
        GROUP BY quality_topic_code
        """
        
        cursor.execute(sql, bad_codes)
        results = cursor.fetchall()
        
        if results:
            print("❌ 发现使用了乱码code的记录:")
            print("")
            total = 0
            for code, count in results:
                print(f"  {code}: {count} 条记录")
                total += count
            
            print(f"\n  总计: {total} 条记录需要更新")
            print("")
            
            # 显示详细信息
            print("详细记录:")
            print("")
            for code, _ in results:
                sql = """
                SELECT ai.id, r.id as registration_id, r.project_name
                FROM activity_infos ai
                JOIN registrations r ON ai.registration_id = r.id
                WHERE ai.quality_topic_code = %s
                LIMIT 5
                """
                cursor.execute(sql, (code,))
                records = cursor.fetchall()
                
                print(f"  {code}:")
                for record in records:
                    print(f"    - ActivityInfo ID: {record[0]}, Registration ID: {record[1]}, Project: {record[2]}")
                print("")
            
            print("=" * 80)
            print("⚠️  需要手动更新这些记录的quality_topic_code为正确的值")
            print("=" * 80)
            
        else:
            print("✅ 没有记录使用乱码code")
            print("")
            print("=" * 80)
            print("✅ 数据库状态正常，无需额外操作")
            print("=" * 80)
        
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    check_bad_usage()
