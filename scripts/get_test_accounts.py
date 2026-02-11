#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""获取最新的测试账号"""

import psycopg2

PG_CONFIG = {
    'host': '119.167.165.27',
    'port': 5432,
    'database': 'zjylzl',
    'user': 'postgres',
    'password': 'zjylzl',
    'options': '-c search_path=zjylzl'
}

def get_test_accounts():
    """获取测试账号"""
    conn = psycopg2.connect(**PG_CONFIG)
    cursor = conn.cursor()
    
    try:
        print("=" * 80)
        print("最新测试账号清单")
        print("=" * 80)
        
        # 1. 参赛者账号（5个）
        print("\n【参赛者账号】(5个)")
        cursor.execute("""
            SELECT id, phone, name, institution_id
            FROM zjylzl.user_accounts
            WHERE role = 'CONTESTANT'
            ORDER BY id
            LIMIT 5
        """)
        
        contestants = cursor.fetchall()
        print(f"{'ID':<5} {'手机号':<15} {'姓名':<20} {'机构ID':<10}")
        print("-" * 60)
        for row in contestants:
            print(f"{row[0]:<5} {row[1]:<15} {row[2]:<20} {row[3] or 'N/A':<10}")
        
        # 2. 评委账号（3个）
        print("\n【评委账号】(3个)")
        cursor.execute("""
            SELECT id, phone, name, title
            FROM zjylzl.user_accounts
            WHERE role = 'REVIEWER'
            ORDER BY id
            LIMIT 3
        """)
        
        reviewers = cursor.fetchall()
        print(f"{'ID':<5} {'手机号':<15} {'姓名':<20} {'职称':<15}")
        print("-" * 60)
        for row in reviewers:
            print(f"{row[0]:<5} {row[1]:<15} {row[2]:<20} {row[3] or 'N/A':<15}")
        
        # 3. 组委会管理员（2个）
        print("\n【组委会管理员】(2个)")
        cursor.execute("""
            SELECT id, phone, name
            FROM zjylzl.user_accounts
            WHERE role = 'COMMITTEE_ADMIN'
            ORDER BY id
            LIMIT 2
        """)
        
        admins = cursor.fetchall()
        print(f"{'ID':<5} {'手机号':<15} {'姓名':<20}")
        print("-" * 45)
        for row in admins:
            print(f"{row[0]:<5} {row[1]:<15} {row[2]:<20}")
        
        # 4. 系统维护员（2个）
        print("\n【系统维护员】(2个)")
        cursor.execute("""
            SELECT id, phone, name
            FROM zjylzl.user_accounts
            WHERE role = 'SYSTEM_ADMIN'
            ORDER BY id
            LIMIT 2
        """)
        
        sys_admins = cursor.fetchall()
        print(f"{'ID':<5} {'手机号':<15} {'姓名':<20}")
        print("-" * 45)
        for row in sys_admins:
            print(f"{row[0]:<5} {row[1]:<15} {row[2]:<20}")
        
        print("\n" + "=" * 80)
        
        return {
            'contestants': contestants,
            'reviewers': reviewers,
            'admins': admins,
            'sys_admins': sys_admins
        }
        
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    get_test_accounts()
