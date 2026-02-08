#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查管理员账号"""

import pymysql

DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

def check_account():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 查找手机号为 13800000041 的账号
        cursor.execute("SELECT * FROM user_accounts WHERE phone = '13800000041'")
        account = cursor.fetchone()
        
        if account:
            cursor.execute("SHOW COLUMNS FROM user_accounts")
            columns = [col[0] for col in cursor.fetchall()]
            
            print("找到账号:")
            for i, col in enumerate(columns):
                print(f"  {col}: {account[i]}")
        else:
            print("未找到手机号为 13800000041 的账号")
            print("\n查找所有 COMMITTEE_ADMIN 和 OPS 角色的账号:")
            cursor.execute("SELECT id, phone, name, role FROM user_accounts WHERE role IN ('COMMITTEE_ADMIN', 'OPS')")
            accounts = cursor.fetchall()
            
            if accounts:
                for acc in accounts:
                    print(f"  ID: {acc[0]}, 手机: {acc[1]}, 姓名: {acc[2]}, 角色: {acc[3]}")
            else:
                print("  没有找到 COMMITTEE_ADMIN 或 OPS 角色的账号")
                
                print("\n所有账号:")
                cursor.execute("SELECT id, phone, name, role FROM user_accounts LIMIT 20")
                all_accounts = cursor.fetchall()
                for acc in all_accounts:
                    print(f"  ID: {acc[0]}, 手机: {acc[1]}, 姓名: {acc[2]}, 角色: {acc[3]}")
                    
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    check_account()
