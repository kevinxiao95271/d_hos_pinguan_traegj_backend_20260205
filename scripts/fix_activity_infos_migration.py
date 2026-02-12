#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复activity_infos表的迁移问题
"""

import sys
import io
import psycopg2
from psycopg2.extras import execute_batch

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

def fix_activity_infos():
    """修复activity_infos迁移"""
    
    print("=" * 80)
    print("修复activity_infos表迁移")
    print("=" * 80)
    
    old_conn = psycopg2.connect(**OLD_DB_CONFIG)
    old_cur = old_conn.cursor()
    
    new_conn = psycopg2.connect(**NEW_DB_CONFIG)
    new_cur = new_conn.cursor()
    
    # 1. 检查activity_infos中的registration_id是否都存在于registrations表
    print("\n[1] 检查外键约束...")
    old_cur.execute("""
        SELECT DISTINCT ai.registration_id
        FROM zjylzl.activity_infos_discard ai
        LEFT JOIN zjylzl.registrations_discard r ON ai.registration_id = r.id
        WHERE r.id IS NULL
    """)
    missing_reg_ids = [row[0] for row in old_cur.fetchall()]
    
    if missing_reg_ids:
        print(f"  ⚠ 发现 {len(missing_reg_ids)} 个无效的registration_id: {missing_reg_ids}")
        print(f"  这些记录将被跳过")
    
    # 2. 获取新库表的列名
    new_cur.execute("""
        SELECT column_name 
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'activity_infos'
        ORDER BY ordinal_position
    """)
    new_columns = [row[0] for row in new_cur.fetchall()]
    print(f"\n[2] 新库activity_infos表有 {len(new_columns)} 列")
    
    # 3. 从旧库读取有效数据
    columns_str = ', '.join(new_columns)
    
    if missing_reg_ids:
        placeholders = ', '.join(['%s'] * len(missing_reg_ids))
        old_cur.execute(f"""
            SELECT {columns_str} 
            FROM zjylzl.activity_infos_discard
            WHERE registration_id NOT IN ({placeholders})
        """, missing_reg_ids)
    else:
        old_cur.execute(f"SELECT {columns_str} FROM zjylzl.activity_infos_discard")
    
    rows = old_cur.fetchall()
    
    if not rows:
        print(f"\n[3] 没有有效数据需要迁移")
        return
    
    print(f"\n[3] 准备迁移 {len(rows)} 行数据...")
    
    # 4. 插入到新库
    placeholders = ', '.join(['%s'] * len(new_columns))
    insert_sql = f"INSERT INTO public.activity_infos ({columns_str}) VALUES ({placeholders})"
    
    try:
        execute_batch(new_cur, insert_sql, rows, page_size=100)
        new_conn.commit()
        print(f"  ✓ 成功迁移 {len(rows)} 行数据")
    except Exception as e:
        new_conn.rollback()
        print(f"  ✗ 迁移失败: {e}")
    
    # 5. 验证
    new_cur.execute("SELECT COUNT(*) FROM public.activity_infos")
    new_count = new_cur.fetchone()[0]
    
    old_cur.execute("SELECT COUNT(*) FROM zjylzl.activity_infos_discard")
    old_count = old_cur.fetchone()[0]
    
    print(f"\n[4] 验证结果:")
    print(f"  新库: {new_count} 行")
    print(f"  旧库: {old_count} 行")
    print(f"  跳过: {old_count - new_count} 行 (外键约束)")
    
    old_cur.close()
    old_conn.close()
    new_cur.close()
    new_conn.close()
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    fix_activity_infos()
