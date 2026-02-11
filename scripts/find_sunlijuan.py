#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查找孙丽娟账号"""

import psycopg2

PG_CONFIG = {
    'host': '119.167.165.27',
    'port': 5432,
    'database': 'zjylzl',
    'user': 'postgres',
    'password': 'zjylzl',
    'options': '-c search_path=zjylzl'
}

def find_account():
    conn = psycopg2.connect(**PG_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 查找孙丽娟
        cursor.execute("""
            SELECT id, phone, name, role, title
            FROM zjylzl.user_accounts
            WHERE name LIKE '%孙丽娟%' OR name LIKE '%Sun%'
        """)
        
        rows = cursor.fetchall()
        
        if rows:
            print("找到孙丽娟账号:")
            print(f"{'ID':<5} {'手机号':<15} {'姓名':<20} {'角色':<15} {'职称':<15}")
            print("-" * 75)
            for row in rows:
                print(f"{row[0]:<5} {row[1]:<15} {row[2]:<20} {row[3]:<15} {row[4] or 'N/A':<15}")
        else:
            print("未找到孙丽娟账号，查询所有评委账号:")
            cursor.execute("""
                SELECT id, phone, name, role, title
                FROM zjylzl.user_accounts
                WHERE role = 'REVIEWER'
                ORDER BY id
            """)
            
            rows = cursor.fetchall()
            print(f"\n共 {len(rows)} 个评委账号:")
            print(f"{'ID':<5} {'手机号':<15} {'姓名':<20} {'角色':<15} {'职称':<15}")
            print("-" * 75)
            for row in rows:
                print(f"{row[0]:<5} {row[1]:<15} {row[2]:<20} {row[3]:<15} {row[4] or 'N/A':<15}")
        
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    find_account()
