#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查现有的评委相关表结构和数据"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pymysql
from db_config import DB_CONFIG

# 数据库连接
conn = pymysql.connect(**DB_CONFIG)

cursor = conn.cursor(pymysql.cursors.DictCursor)

print("="*80)
print("检查数据库中所有表")
print("="*80)

cursor.execute("SHOW TABLES")
tables = cursor.fetchall()

print("\n所有表:")
for table in tables:
    table_name = list(table.values())[0]
    print(f"  - {table_name}")

# 查找与reviewer相关的表
print("\n" + "="*80)
print("与评委相关的表（包含'review'关键字）")
print("="*80)

reviewer_tables = [list(t.values())[0] for t in tables if 'review' in list(t.values())[0].lower()]

for table_name in reviewer_tables:
    print(f"\n表名: {table_name}")
    cursor.execute(f"DESCRIBE {table_name}")
    columns = cursor.fetchall()
    
    print("  字段:")
    for col in columns:
        print(f"    - {col['Field']}: {col['Type']} {col['Null']} {col['Key']}")
    
    # 查看数据量
    cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
    count = cursor.fetchone()['count']
    print(f"  数据量: {count} 条")
    
    # 如果是小表，显示前几条数据
    if count > 0 and count <= 100:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
        rows = cursor.fetchall()
        if rows:
            print(f"  示例数据（前5条）:")
            for row in rows:
                print(f"    {row}")

# 检查user_accounts表中与评委相关的字段
print("\n" + "="*80)
print("user_accounts表结构（评委相关字段）")
print("="*80)

cursor.execute("DESCRIBE user_accounts")
columns = cursor.fetchall()

print("\n所有字段:")
for col in columns:
    print(f"  - {col['Field']}: {col['Type']}")

# 检查是否有专门的评委池表
print("\n" + "="*80)
print("查找可能的评委池表")
print("="*80)

pool_keywords = ['pool', 'reviewer', 'expert', '专家', '池']
pool_tables = []

for table in tables:
    table_name = list(table.values())[0]
    for keyword in pool_keywords:
        if keyword in table_name.lower():
            pool_tables.append(table_name)
            break

if pool_tables:
    print(f"\n找到可能的评委池表: {pool_tables}")
    for table_name in pool_tables:
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        print(f"\n{table_name} 表结构:")
        for col in columns:
            print(f"  - {col['Field']}: {col['Type']}")
else:
    print("\n未找到专门的评委池表")
    print("评委信息可能存储在 user_accounts 表中")

# 检查user_accounts中REVIEWER角色的分布
print("\n" + "="*80)
print("user_accounts表中的REVIEWER数据分析")
print("="*80)

cursor.execute("""
    SELECT 
        reviewer_group_code,
        interview_group_code,
        expert_background,
        COUNT(*) as count
    FROM user_accounts
    WHERE role = 'REVIEWER'
    GROUP BY reviewer_group_code, interview_group_code, expert_background
    ORDER BY reviewer_group_code, expert_background
""")

groups = cursor.fetchall()

print("\n按分组和背景统计:")
for g in groups:
    print(f"  书审组:{g['reviewer_group_code'] or '未设置'}, "
          f"面试组:{g['interview_group_code'] or '未设置'}, "
          f"背景:{g['expert_background'] or '未设置'}, "
          f"人数:{g['count']}")

cursor.close()
conn.close()

print("\n" + "="*80)
print("分析完成")
print("="*80)
