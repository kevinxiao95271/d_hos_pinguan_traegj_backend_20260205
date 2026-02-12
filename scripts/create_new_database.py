#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建新数据库 d_hos_pinguan_20260211
并从旧库迁移数据
"""

import sys
import io
import pymysql
from db_config import DB_CONFIG

# 设置输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def create_new_database():
    """创建新数据库并迁移数据"""
    
    # 连接到MySQL服务器(不指定数据库)
    conn_config = DB_CONFIG.copy()
    old_database = conn_config.pop('database')
    
    conn = pymysql.connect(**conn_config)
    cur = conn.cursor()
    
    print("=" * 80)
    print("创建新数据库并迁移数据")
    print("=" * 80)
    
    new_database = 'd_hos_pinguan_20260211'
    
    # 1. 创建新数据库
    print(f"\n[步骤1] 创建新数据库: {new_database}")
    try:
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {new_database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"  ✓ 数据库 {new_database} 创建成功")
    except Exception as e:
        print(f"  ✗ 创建数据库失败: {e}")
        return
    
    # 2. 获取旧库中的所有表
    print(f"\n[步骤2] 检查旧库 {old_database} 中的表")
    cur.execute(f"USE {old_database}")
    cur.execute("SHOW TABLES")
    old_tables = [row[0] for row in cur.fetchall()]
    
    print(f"  找到 {len(old_tables)} 个表")
    
    # 需要迁移的表(项目使用的表)
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
    
    # 3. 复制表结构和数据到新库
    print(f"\n[步骤3] 复制表到新数据库")
    for table in project_tables:
        if table in old_tables:
            try:
                # 获取建表语句
                cur.execute(f"SHOW CREATE TABLE {old_database}.{table}")
                create_stmt = cur.fetchone()[1]
                
                # 在新库中创建表
                cur.execute(f"USE {new_database}")
                cur.execute(create_stmt)
                
                # 复制数据
                cur.execute(f"""
                    INSERT INTO {new_database}.{table}
                    SELECT * FROM {old_database}.{table}
                """)
                
                row_count = cur.rowcount
                print(f"  ✓ {table}: 复制了 {row_count} 行数据")
                
            except Exception as e:
                print(f"  ✗ {table}: 复制失败 - {e}")
        else:
            print(f"  ⚠ {table}: 在旧库中不存在,跳过")
    
    conn.commit()
    
    # 4. 重命名旧库中的表为 _discard
    print(f"\n[步骤4] 重命名旧库中的表为 _discard")
    cur.execute(f"USE {old_database}")
    
    for table in project_tables:
        if table in old_tables:
            try:
                new_name = f"{table}_discard"
                cur.execute(f"RENAME TABLE {table} TO {new_name}")
                print(f"  ✓ {table} → {new_name}")
            except Exception as e:
                print(f"  ✗ {table}: 重命名失败 - {e}")
    
    conn.commit()
    
    # 5. 验证新库
    print(f"\n[步骤5] 验证新数据库")
    cur.execute(f"USE {new_database}")
    cur.execute("SHOW TABLES")
    new_tables = [row[0] for row in cur.fetchall()]
    
    print(f"  新库中有 {len(new_tables)} 个表:")
    for table in sorted(new_tables):
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        print(f"    - {table}: {count} 行")
    
    print(f"\n[完成] 数据库迁移完成!")
    print(f"  新数据库: {new_database}")
    print(f"  旧数据库: {old_database} (表已重命名为 *_discard)")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    try:
        create_new_database()
    except Exception as e:
        print(f"[ERROR] 错误: {e}")
        import traceback
        traceback.print_exc()
