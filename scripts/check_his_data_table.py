#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查看历史数据表结构"""

import pymysql

# 数据库配置
DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

def check_table_structure():
    """查看表结构"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 查看表结构
        print("=== pinguan_his_data 表结构 ===\n")
        cursor.execute("DESCRIBE pinguan_his_data")
        columns = cursor.fetchall()
        
        for col in columns:
            print(f"字段: {col[0]:<30} 类型: {col[1]:<20} 可空: {col[2]:<5} 键: {col[3]:<5} 默认: {col[4]}")
        
        # 查看数据样例
        print("\n=== 数据样例 (前3条) ===\n")
        cursor.execute("SELECT * FROM pinguan_his_data LIMIT 3")
        rows = cursor.fetchall()
        
        # 获取列名
        cursor.execute("SHOW COLUMNS FROM pinguan_his_data")
        column_names = [col[0] for col in cursor.fetchall()]
        
        for row in rows:
            print("\n记录:")
            for i, col_name in enumerate(column_names):
                print(f"  {col_name}: {row[i]}")
        
        # 统计总数
        cursor.execute("SELECT COUNT(*) FROM pinguan_his_data")
        total = cursor.fetchone()[0]
        print(f"\n=== 总记录数: {total} ===")
        
        # 查看地区分布
        print("\n=== 地区分布 ===")
        cursor.execute("SELECT DISTINCT region FROM pinguan_his_data WHERE region IS NOT NULL ORDER BY region")
        regions = cursor.fetchall()
        for r in regions:
            cursor.execute("SELECT COUNT(*) FROM pinguan_his_data WHERE region = %s", (r[0],))
            count = cursor.fetchone()[0]
            print(f"  {r[0]}: {count} 条")
        
        # 查看组别分布
        print("\n=== 组别分布 ===")
        cursor.execute("SELECT DISTINCT group_type FROM pinguan_his_data WHERE group_type IS NOT NULL ORDER BY group_type")
        groups = cursor.fetchall()
        for g in groups:
            cursor.execute("SELECT COUNT(*) FROM pinguan_his_data WHERE group_type = %s", (g[0],))
            count = cursor.fetchone()[0]
            print(f"  {g[0]}: {count} 条")
        
        # 查看入围状态分布
        print("\n=== 入围状态分布 ===")
        cursor.execute("SELECT DISTINCT finalist_status FROM pinguan_his_data WHERE finalist_status IS NOT NULL ORDER BY finalist_status")
        statuses = cursor.fetchall()
        for s in statuses:
            cursor.execute("SELECT COUNT(*) FROM pinguan_his_data WHERE finalist_status = %s", (s[0],))
            count = cursor.fetchone()[0]
            print(f"  {s[0]}: {count} 条")
            
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    check_table_structure()
