#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看dictionary_items表结构
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

def check_structure():
    """查看表结构"""
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # 查看表结构
        cur.execute("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = 'dictionary_items'
            ORDER BY ordinal_position
        """)
        
        columns = cur.fetchall()
        print("dictionary_items表结构:")
        for col_name, data_type, max_len in columns:
            print(f"  {col_name}: {data_type}" + (f"({max_len})" if max_len else ""))
        
        # 查询所有method数据
        cur.execute("""
            SELECT *
            FROM dictionary_items
            WHERE type = 'method'
            ORDER BY id
        """)
        
        methods = cur.fetchall()
        print(f"\n找到 {len(methods)} 条method记录")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_structure()
