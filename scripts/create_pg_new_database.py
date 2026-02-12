#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
在PostgreSQL中创建新数据库 d_hos_pinguan_20260211
并从旧库zjylzl迁移数据,旧库表改名为_discard
"""

import sys
import io
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# 设置输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# PostgreSQL配置
PG_CONFIG = {
    'host': '119.167.165.27',
    'port': 5432,
    'user': 'postgres',
    'password': 'zjylzl',
    'database': 'postgres'  # 先连接到默认数据库
}

OLD_DATABASE = 'zjylzl'
NEW_DATABASE = 'd_hos_pinguan_20260211'

def create_pg_database():
    """创建PostgreSQL新数据库并迁移数据"""
    
    print("=" * 80)
    print("PostgreSQL数据库迁移")
    print("=" * 80)
    
    # 1. 连接到postgres数据库创建新库
    print(f"\n[步骤1] 创建新数据库: {NEW_DATABASE}")
    conn = psycopg2.connect(**PG_CONFIG)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    try:
        # 检查数据库是否存在
        cur.execute(f"""
            SELECT 1 FROM pg_database WHERE datname = '{NEW_DATABASE}'
        """)
        if cur.fetchone():
            print(f"  ⚠ 数据库 {NEW_DATABASE} 已存在")
        else:
            cur.execute(f"""
                CREATE DATABASE {NEW_DATABASE} 
                WITH ENCODING 'UTF8' 
                LC_COLLATE = 'en_US.UTF-8' 
                LC_CTYPE = 'en_US.UTF-8' 
                TEMPLATE template0
            """)
            print(f"  ✓ 数据库 {NEW_DATABASE} 创建成功 (UTF8编码)")
    except Exception as e:
        print(f"  ✗ 创建数据库失败: {e}")
        return
    
    cur.close()
    conn.close()
    
    # 2. 连接到旧库,获取所有表
    print(f"\n[步骤2] 连接到旧库 {OLD_DATABASE}")
    old_conn = psycopg2.connect(
        host=PG_CONFIG['host'],
        port=PG_CONFIG['port'],
        user=PG_CONFIG['user'],
        password=PG_CONFIG['password'],
        database=OLD_DATABASE
    )
    old_cur = old_conn.cursor()
    
    # 获取zjylzl schema中的所有表
    old_cur.execute("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'zjylzl'
        ORDER BY tablename
    """)
    old_tables = [row[0] for row in old_cur.fetchall()]
    print(f"  找到 {len(old_tables)} 个表")
    
    # 3. 连接到新库
    print(f"\n[步骤3] 连接到新库 {NEW_DATABASE}")
    new_conn = psycopg2.connect(
        host=PG_CONFIG['host'],
        port=PG_CONFIG['port'],
        user=PG_CONFIG['user'],
        password=PG_CONFIG['password'],
        database=NEW_DATABASE
    )
    new_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    new_cur = new_conn.cursor()
    
    # 创建public schema(如果不存在)
    new_cur.execute("CREATE SCHEMA IF NOT EXISTS public")
    
    # 4. 复制表结构和数据
    print(f"\n[步骤4] 使用pg_dump复制表")
    
    import subprocess
    import os
    
    # 只复制项目需要的表
    project_tables = [
        'competitions',
        'institutions',
        'user_accounts',
        'registrations',
        'registration_members',
        'activity_infos',
        'project_summaries',
        'material_files',
        'review_tasks',
        'review_scores',
        'dictionary_items',
        'system_settings',
        'institution_update_requests',
        'activity_templates',
        'competition_templates',
        'pinguan_his_data'
    ]
    
    for table in project_tables:
        if table in old_tables:
            try:
                # 使用pg_dump导出表结构和数据
                dump_cmd = [
                    'pg_dump',
                    '-h', PG_CONFIG['host'],
                    '-p', str(PG_CONFIG['port']),
                    '-U', PG_CONFIG['user'],
                    '-d', OLD_DATABASE,
                    '-n', 'zjylzl',
                    '-t', f'zjylzl.{table}',
                    '--no-owner',
                    '--no-acl'
                ]
                
                # 设置密码环境变量
                env = os.environ.copy()
                env['PGPASSWORD'] = PG_CONFIG['password']
                
                # 导出SQL
                result = subprocess.run(dump_cmd, capture_output=True, text=True, env=env)
                
                if result.returncode == 0:
                    sql = result.stdout
                    # 替换schema名称
                    sql = sql.replace('zjylzl.', 'public.')
                    sql = sql.replace('SET search_path = zjylzl', 'SET search_path = public')
                    
                    # 在新库执行
                    new_cur.execute(sql)
                    
                    # 统计行数
                    new_cur.execute(f"SELECT COUNT(*) FROM public.{table}")
                    count = new_cur.fetchone()[0]
                    print(f"  ✓ {table}: 复制了 {count} 行数据")
                else:
                    print(f"  ✗ {table}: pg_dump失败 - {result.stderr}")
                
            except Exception as e:
                print(f"  ✗ {table}: 失败 - {e}")
        else:
            print(f"  ⚠ {table}: 在旧库中不存在")
    
    # 5. 重命名旧库中的表
    print(f"\n[步骤5] 重命名旧库中的表为 _discard")
    
    for table in project_tables:
        if table in old_tables:
            try:
                new_name = f"{table}_discard"
                old_cur.execute(f"ALTER TABLE zjylzl.{table} RENAME TO {new_name}")
                old_conn.commit()
                print(f"  ✓ {table} → {new_name}")
            except Exception as e:
                print(f"  ✗ {table}: 重命名失败 - {e}")
                old_conn.rollback()
    
    # 6. 验证新库
    print(f"\n[步骤6] 验证新数据库")
    new_cur.execute("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public'
        ORDER BY tablename
    """)
    new_tables = [row[0] for row in new_cur.fetchall()]
    
    print(f"  新库中有 {len(new_tables)} 个表:")
    for table in new_tables:
        new_cur.execute(f"SELECT COUNT(*) FROM public.{table}")
        count = new_cur.fetchone()[0]
        print(f"    - {table}: {count} 行")
    
    print(f"\n[完成] PostgreSQL数据库迁移完成!")
    print(f"  新数据库: {NEW_DATABASE}")
    print(f"  旧数据库: {OLD_DATABASE} (zjylzl schema中的表已重命名为 *_discard)")
    
    old_cur.close()
    old_conn.close()
    new_cur.close()
    new_conn.close()

if __name__ == "__main__":
    try:
        create_pg_database()
    except Exception as e:
        print(f"[ERROR] 错误: {e}")
        import traceback
        traceback.print_exc()
