#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
比较旧库和新库的表结构差异
"""

import sys
import io
import psycopg2

# 设置输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

OLD_DB_CONFIG = {
    'host': '119.167.165.27',
    'port': 5432,
    'user': 'postgres',
    'password': 'zjylzl',
    'database': 'zjylzl'
}

NEW_DB_CONFIG = {
    'host': '119.167.165.27',
    'port': 5432,
    'user': 'postgres',
    'password': 'zjylzl',
    'database': 'd_hos_pinguan_20260211'
}

def get_table_columns(conn, schema, table_name):
    """获取表的列信息"""
    cur = conn.cursor()
    cur.execute("""
        SELECT column_name, data_type, character_maximum_length
        FROM information_schema.columns
        WHERE table_schema = %s AND table_name = %s
        ORDER BY ordinal_position
    """, (schema, table_name))
    columns = cur.fetchall()
    cur.close()
    return columns

def compare_structures():
    """比较表结构"""
    
    print("=" * 80)
    print("表结构对比: 旧库 vs 新库")
    print("=" * 80)
    
    old_conn = psycopg2.connect(**OLD_DB_CONFIG)
    new_conn = psycopg2.connect(**NEW_DB_CONFIG)
    
    # 重点检查失败的表
    problem_tables = ['competitions', 'institutions']
    
    for table_name in problem_tables:
        print(f"\n{'='*80}")
        print(f"表: {table_name}")
        print(f"{'='*80}")
        
        old_table = f"{table_name}_discard"
        old_cols = get_table_columns(old_conn, 'zjylzl', old_table)
        new_cols = get_table_columns(new_conn, 'public', table_name)
        
        old_col_names = {col[0] for col in old_cols}
        new_col_names = {col[0] for col in new_cols}
        
        # 旧库有但新库没有的列
        missing_in_new = old_col_names - new_col_names
        if missing_in_new:
            print(f"\n旧库有但新库缺少的列:")
            for col_name in sorted(missing_in_new):
                col_info = [c for c in old_cols if c[0] == col_name][0]
                print(f"  - {col_info[0]}: {col_info[1]}")
        
        # 新库有但旧库没有的列
        extra_in_new = new_col_names - old_col_names
        if extra_in_new:
            print(f"\n新库有但旧库没有的列:")
            for col_name in sorted(extra_in_new):
                col_info = [c for c in new_cols if c[0] == col_name][0]
                print(f"  - {col_info[0]}: {col_info[1]}")
        
        # 共同的列
        common_cols = old_col_names & new_col_names
        print(f"\n共同的列 ({len(common_cols)} 个):")
        for col_name in sorted(common_cols):
            print(f"  - {col_name}")
    
    old_conn.close()
    new_conn.close()
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    compare_structures()
