#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查项目负责人的职称分布"""

import pymysql
from db_config import DB_CONFIG

def check_titles():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 查询项目负责人的职称分布
        cursor.execute("""
            SELECT title, COUNT(*) as count
            FROM registration_members
            WHERE role = 'PARTICIPANT'
            GROUP BY title
            ORDER BY count DESC
        """)
        
        print("项目负责人职称分布:")
        print("=" * 50)
        total = 0
        for title, count in cursor.fetchall():
            print(f"{title}: {count}")
            total += count
        print("=" * 50)
        print(f"总计: {total}")
        
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    check_titles()
