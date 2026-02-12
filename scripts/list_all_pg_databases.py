#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
列出PostgreSQL服务器上的所有数据库
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
    'database': 'postgres'  # 连接到默认数据库
}

def list_all_databases():
    """列出所有数据库"""
    
    print("=" * 80)
    print("PostgreSQL服务器数据库列表")
    print(f"服务器: {PG_CONFIG['host']}:{PG_CONFIG['port']}")
    print("=" * 80)
    
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        
        # 查询所有数据库
        cur.execute("""
            SELECT 
                datname as database_name,
                pg_encoding_to_char(encoding) as encoding,
                datcollate as collate,
                pg_size_pretty(pg_database_size(datname)) as size
            FROM pg_database
            WHERE datistemplate = false
            ORDER BY datname
        """)
        
        databases = cur.fetchall()
        
        print(f"\n找到 {len(databases)} 个数据库:\n")
        print(f"{'数据库名':<40} {'编码':<10} {'大小':<15}")
        print("-" * 80)
        
        for db_name, encoding, collate, size in databases:
            print(f"{db_name:<40} {encoding:<10} {size:<15}")
        
        print("\n" + "=" * 80)
        
        # 特别检查我们的目标数据库
        print("\n检查目标数据库:")
        target_dbs = ['zjylzl', 'd_hos_pinguan_20260211']
        
        for target in target_dbs:
            cur.execute("""
                SELECT 
                    datname,
                    pg_encoding_to_char(encoding) as encoding,
                    pg_size_pretty(pg_database_size(datname)) as size
                FROM pg_database
                WHERE datname = %s
            """, (target,))
            
            result = cur.fetchone()
            if result:
                db_name, encoding, size = result
                print(f"  ✓ {db_name}: 存在 (编码: {encoding}, 大小: {size})")
                
                # 如果是zjylzl，检查schema
                if db_name == 'zjylzl':
                    conn2 = psycopg2.connect(
                        host=PG_CONFIG['host'],
                        port=PG_CONFIG['port'],
                        user=PG_CONFIG['user'],
                        password=PG_CONFIG['password'],
                        database='zjylzl'
                    )
                    cur2 = conn2.cursor()
                    cur2.execute("""
                        SELECT schema_name 
                        FROM information_schema.schemata 
                        WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
                        ORDER BY schema_name
                    """)
                    schemas = [row[0] for row in cur2.fetchall()]
                    print(f"    Schema: {', '.join(schemas)}")
                    cur2.close()
                    conn2.close()
                    
            else:
                print(f"  ✗ {target}: 不存在")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"\n[ERROR] 查询失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    list_all_databases()
