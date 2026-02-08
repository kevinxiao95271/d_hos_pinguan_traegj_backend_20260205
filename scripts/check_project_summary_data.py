#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查项目摘要数据"""

import pymysql

DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

def check_data():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 检查项目119
        test_id = 119
        
        print("=" * 80)
        print(f"检查报名ID {test_id} 的项目摘要数据")
        print("=" * 80)
        
        cursor.execute("""
            SELECT id, registration_id, theme, 
                   LENGTH(plan) as plan_len,
                   LENGTH(problem) as problem_len,
                   LENGTH(action) as action_len,
                   LENGTH(success) as success_len,
                   LENGTH(discussion) as discussion_len,
                   LENGTH(operation) as operation_len,
                   LENGTH(presentation) as presentation_len
            FROM project_summaries
            WHERE registration_id = %s
        """, (test_id,))
        
        result = cursor.fetchone()
        
        if result:
            print(f"\n✅ 找到项目摘要数据:")
            print(f"  ID: {result[0]}")
            print(f"  Registration ID: {result[1]}")
            print(f"  Theme: {result[2]}")
            print(f"  Plan 长度: {result[3]}")
            print(f"  Problem 长度: {result[4]}")
            print(f"  Action 长度: {result[5]}")
            print(f"  Success 长度: {result[6]}")
            print(f"  Discussion 长度: {result[7]}")
            print(f"  Operation 长度: {result[8]}")
            print(f"  Presentation 长度: {result[9]}")
        else:
            print(f"\n❌ 报名ID {test_id} 没有项目摘要数据")
        
        # 统计所有项目摘要
        print("\n" + "=" * 80)
        print("统计所有项目摘要")
        print("=" * 80)
        
        cursor.execute("SELECT COUNT(*) FROM project_summaries")
        total = cursor.fetchone()[0]
        print(f"\n总共有 {total} 条项目摘要记录")
        
        # 查看前5条
        cursor.execute("""
            SELECT registration_id, theme
            FROM project_summaries
            ORDER BY id
            LIMIT 5
        """)
        
        print(f"\n前5条记录:")
        for reg_id, theme in cursor.fetchall():
            print(f"  报名ID {reg_id}: {theme}")
        
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    check_data()
