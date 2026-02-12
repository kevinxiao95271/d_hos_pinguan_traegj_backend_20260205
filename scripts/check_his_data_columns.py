#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看pinguan_his_data表的字段结构
"""

import sys
import io
import psycopg2

# 设置输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB_CONFIG = {
    'host': '119.167.165.27',
    'port': 5432,
    'user': 'postgres',
    'password': 'zjylzl',
    'database': 'd_hos_pinguan_20260211'
}

def check_columns():
    """查看表结构"""
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # 查看表结构
        cur.execute("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = 'pinguan_his_data'
            ORDER BY ordinal_position
        """)
        
        columns = cur.fetchall()
        print("pinguan_his_data表结构:")
        for col_name, data_type, max_len in columns:
            len_str = f"({max_len})" if max_len else ""
            print(f"  {col_name:30s} {data_type}{len_str}")
        
        # 查看示例数据
        print("\n示例数据（前3条）:")
        cur.execute("SELECT * FROM pinguan_his_data LIMIT 3")
        rows = cur.fetchall()
        
        col_names = [desc[0] for desc in cur.description]
        
        for i, row in enumerate(rows, 1):
            print(f"\n记录 {i}:")
            for col_name, value in zip(col_names, row):
                print(f"  {col_name}: {value}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_columns()
