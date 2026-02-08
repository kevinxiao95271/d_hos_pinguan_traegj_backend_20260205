#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查 experience_improve 的数据"""

import pymysql

DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

def check_experience_improve():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        print("=" * 80)
        print("检查 experience_improve 字典数据")
        print("=" * 80)
        
        # 查询所有 experience_improve 类型的记录
        cursor.execute("""
            SELECT code, label, active
            FROM dictionary_items
            WHERE type = 'experience_improve'
            ORDER BY id
        """)
        
        results = cursor.fetchall()
        
        print(f"\n共 {len(results)} 条记录:\n")
        
        for i, (code, label, active) in enumerate(results, 1):
            status = "✅" if active else "❌"
            if label and '?' in label:
                print(f"{i:2d}. {status} {code:30s} → ❌ {label} (有问号)")
            elif not label:
                print(f"{i:2d}. {status} {code:30s} → ❌ (Label为空)")
            else:
                print(f"{i:2d}. {status} {code:30s} → {label}")
        
        # 检查是否有使用这些code的记录
        print("\n" + "=" * 80)
        print("检查使用情况")
        print("=" * 80)
        
        cursor.execute("""
            SELECT experience_improve_code, COUNT(*) as count
            FROM activity_infos
            WHERE experience_improve_code IS NOT NULL
            GROUP BY experience_improve_code
            ORDER BY count DESC
        """)
        
        usage = cursor.fetchall()
        
        if usage:
            print(f"\n共 {len(usage)} 个不同的code被使用:\n")
            for code, count in usage:
                # 查询label
                cursor.execute("""
                    SELECT label FROM dictionary_items
                    WHERE type = 'experience_improve' AND code = %s
                """, (code,))
                label_result = cursor.fetchone()
                label = label_result[0] if label_result else '❌ 字典中不存在'
                print(f"  {code:30s}: {count:3d} 条 → {label}")
        else:
            print("\n没有记录使用 experience_improve_code")
        
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    check_experience_improve()
