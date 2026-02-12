#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查新数据库 d_hos_pinguan_20260211 的当前状态
"""

import sys
import io
import psycopg2

# 设置输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# PostgreSQL配置
PG_CONFIG = {
    'host': '119.167.165.27',
    'port': 5432,
    'user': 'postgres',
    'password': 'zjylzl',
    'database': 'd_hos_pinguan_20260211'
}

def check_database_status():
    """检查新数据库状态"""
    
    print("=" * 80)
    print("检查新数据库状态: d_hos_pinguan_20260211")
    print("=" * 80)
    
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        
        # 1. 检查数据库编码
        print("\n[1] 数据库编码:")
        cur.execute("SELECT pg_encoding_to_char(encoding) FROM pg_database WHERE datname = 'd_hos_pinguan_20260211'")
        encoding = cur.fetchone()[0]
        print(f"  编码: {encoding}")
        
        # 2. 检查所有schema
        print("\n[2] Schema列表:")
        cur.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            ORDER BY schema_name
        """)
        schemas = [row[0] for row in cur.fetchall()]
        for schema in schemas:
            print(f"  - {schema}")
        
        # 3. 检查public schema中的表
        print("\n[3] public schema中的表:")
        cur.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename
        """)
        tables = cur.fetchall()
        
        if tables:
            print(f"  找到 {len(tables)} 个表:")
            for (table,) in tables:
                cur.execute(f"SELECT COUNT(*) FROM public.{table}")
                count = cur.fetchone()[0]
                print(f"    - {table}: {count} 行")
        else:
            print("  ⚠ 没有找到任何表 (新库是空的)")
        
        # 4. 检查旧库zjylzl中的_discard表
        print("\n[4] 检查旧库zjylzl中的_discard表:")
        old_conn = psycopg2.connect(
            host='119.167.165.27',
            port=5432,
            user='postgres',
            password='zjylzl',
            database='zjylzl'
        )
        old_cur = old_conn.cursor()
        
        old_cur.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'zjylzl' AND tablename LIKE '%_discard'
            ORDER BY tablename
        """)
        discard_tables = old_cur.fetchall()
        
        if discard_tables:
            print(f"  找到 {len(discard_tables)} 个_discard表:")
            for (table,) in discard_tables:
                old_cur.execute(f"SELECT COUNT(*) FROM zjylzl.{table}")
                count = old_cur.fetchone()[0]
                print(f"    - {table}: {count} 行")
        else:
            print("  ⚠ 没有找到_discard表")
        
        old_cur.close()
        old_conn.close()
        
        print("\n" + "=" * 80)
        print("检查完成")
        print("=" * 80)
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"\n[ERROR] 检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database_status()
