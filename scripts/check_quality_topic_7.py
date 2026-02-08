#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查 quality_topic_7 的Label值"""

import pymysql

DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

def check_quality_topic_7():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        print("=" * 80)
        print("检查 quality_topic_7 的Label值")
        print("=" * 80)
        
        # 查询 quality_topic_7
        sql = """
        SELECT id, type, code, label, active
        FROM dictionary_items
        WHERE type = 'quality_topic' AND code = 'quality_topic_7'
        """
        
        cursor.execute(sql)
        result = cursor.fetchone()
        
        if result:
            print("\n找到记录:")
            print(f"  ID: {result[0]}")
            print(f"  Type: {result[1]}")
            print(f"  Code: {result[2]}")
            print(f"  Label: {result[3]}")
            print(f"  Active: {result[4]}")
            
            # 检查Label是否是乱码
            label = result[3]
            if label and all(ord(c) > 127 for c in label if c != ' '):
                print(f"\n❌ Label显示为乱码: {label}")
                print("   这可能是编码问题")
            elif label and '?' in label:
                print(f"\n❌ Label包含问号: {label}")
                print("   这说明数据插入时编码有问题")
            else:
                print(f"\n✅ Label正常: {label}")
        else:
            print("\n❌ 未找到 quality_topic_7 记录")
        
        # 查询所有 quality_topic 类型的记录
        print("\n" + "=" * 80)
        print("所有 quality_topic 类型的记录")
        print("=" * 80)
        
        sql = """
        SELECT code, label, active
        FROM dictionary_items
        WHERE type = 'quality_topic'
        ORDER BY id
        """
        
        cursor.execute(sql)
        results = cursor.fetchall()
        
        print(f"\n共 {len(results)} 条记录:\n")
        
        for i, row in enumerate(results, 1):
            code, label, active = row
            status = "✅" if active else "❌"
            
            # 检查Label是否有问题
            if label and '?' in label:
                print(f"{i:2d}. {status} {code:30s} → ❌ {label} (有问号)")
            elif not label:
                print(f"{i:2d}. {status} {code:30s} → ❌ (Label为空)")
            else:
                print(f"{i:2d}. {status} {code:30s} → {label}")
        
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    check_quality_topic_7()
