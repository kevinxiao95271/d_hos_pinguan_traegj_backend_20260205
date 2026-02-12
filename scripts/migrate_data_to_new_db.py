#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从旧库zjylzl的*_discard表迁移数据到新库d_hos_pinguan_20260211
"""

import sys
import io
import psycopg2
from psycopg2.extras import execute_batch

# 设置输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# PostgreSQL配置
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

# 需要迁移的表（按依赖顺序）
TABLES_TO_MIGRATE = [
    'dictionary_items',
    'system_settings',
    'competitions',
    'institutions',
    'user_accounts',
    'activity_templates',
    'competition_templates',
    'activity_infos',
    'registrations',
    'registration_members',
    'project_summaries',
    'material_files',
    'review_tasks',
    'review_scores',
    'institution_update_requests',
    'pinguan_his_data'
]

def migrate_table_data(table_name, old_cur, new_conn):
    """迁移单个表的数据"""
    
    # 获取新库表的列名
    new_cur = new_conn.cursor()
    new_cur.execute(f"""
        SELECT column_name 
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = '{table_name}'
        ORDER BY ordinal_position
    """)
    new_columns = [row[0] for row in new_cur.fetchall()]
    
    if not new_columns:
        new_cur.close()
        print(f"  ✗ {table_name}: 新库中不存在此表")
        return 0
    
    # 从旧库读取数据（只读取新库中存在的列）
    columns_str = ', '.join(new_columns)
    old_cur.execute(f"SELECT {columns_str} FROM zjylzl.{table_name}_discard")
    rows = old_cur.fetchall()
    
    if not rows:
        new_cur.close()
        print(f"  ⚠ {table_name}: 没有数据需要迁移")
        return 0
    
    # 构建INSERT语句
    placeholders = ', '.join(['%s'] * len(new_columns))
    insert_sql = f"INSERT INTO public.{table_name} ({columns_str}) VALUES ({placeholders})"
    
    # 批量插入到新库
    try:
        execute_batch(new_cur, insert_sql, rows, page_size=100)
        new_conn.commit()
        print(f"  ✓ {table_name}: 迁移了 {len(rows)} 行数据 ({len(new_columns)} 列)")
        return len(rows)
    except Exception as e:
        new_conn.rollback()
        print(f"  ✗ {table_name}: 迁移失败 - {e}")
        return 0
    finally:
        new_cur.close()

def migrate_all_data():
    """迁移所有数据"""
    
    print("=" * 80)
    print("数据迁移: zjylzl.*_discard → d_hos_pinguan_20260211")
    print("=" * 80)
    
    try:
        # 连接到旧库
        print("\n[1] 连接到旧库 zjylzl...")
        old_conn = psycopg2.connect(**OLD_DB_CONFIG)
        old_cur = old_conn.cursor()
        print("  ✓ 连接成功")
        
        # 连接到新库
        print("\n[2] 连接到新库 d_hos_pinguan_20260211...")
        new_conn = psycopg2.connect(**NEW_DB_CONFIG)
        print("  ✓ 连接成功")
        
        # 迁移每个表
        print("\n[3] 开始迁移数据...")
        total_rows = 0
        
        for table_name in TABLES_TO_MIGRATE:
            rows_migrated = migrate_table_data(table_name, old_cur, new_conn)
            total_rows += rows_migrated
        
        # 验证迁移结果
        print("\n[4] 验证迁移结果...")
        new_cur = new_conn.cursor()
        
        for table_name in TABLES_TO_MIGRATE:
            new_cur.execute(f"SELECT COUNT(*) FROM public.{table_name}")
            new_count = new_cur.fetchone()[0]
            
            old_cur.execute(f"SELECT COUNT(*) FROM zjylzl.{table_name}_discard")
            old_count = old_cur.fetchone()[0]
            
            if new_count == old_count:
                status = "✓"
            else:
                status = "✗"
            
            print(f"  {status} {table_name}: 新库 {new_count} 行 / 旧库 {old_count} 行")
        
        new_cur.close()
        
        print("\n" + "=" * 80)
        print(f"迁移完成! 总共迁移了 {total_rows} 行数据")
        print("=" * 80)
        
        old_cur.close()
        old_conn.close()
        new_conn.close()
        
    except Exception as e:
        print(f"\n[ERROR] 迁移失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrate_all_data()
