#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""调试review_tasks表"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pymysql

# 数据库连接
conn = pymysql.connect(
    host='gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    port=63606,
    user='root',
    password='Yiguo9527_',
    database='d_hos_pinguan_traegj_20260205',
    charset='utf8mb4'
)

cursor = conn.cursor(pymysql.cursors.DictCursor)

print("="*80)
print("review_tasks表结构")
print("="*80)

cursor.execute("DESCRIBE review_tasks")
columns = cursor.fetchall()

print("\n字段列表:")
for col in columns:
    print(f"  {col['Field']} - {col['Type']} - {col['Null']} - {col['Key']}")

print("\n" + "="*80)
print("review_tasks数据示例（王建国的任务）")
print("="*80)

# 查询王建国(ID=3)的任务
cursor.execute("""
    SELECT rt.id, rt.reviewer_id, rt.registration_id, rt.stage, rt.status,
           u.name as reviewer_name,
           reg.project_name
    FROM review_tasks rt
    LEFT JOIN user_accounts u ON rt.reviewer_id = u.id
    LEFT JOIN registrations reg ON rt.registration_id = reg.id
    WHERE rt.reviewer_id = 3
    ORDER BY rt.id
""")

tasks = cursor.fetchall()

print(f"\n找到 {len(tasks)} 个任务:")
for task in tasks:
    print(f"\n任务ID: {task['id']}")
    print(f"  reviewer_id: {task['reviewer_id']}")
    print(f"  registration_id: {task['registration_id']}")
    print(f"  stage: {task['stage']}")
    print(f"  status: {task['status']}")
    print(f"  评委: {task['reviewer_name']}")
    print(f"  项目: {task['project_name']}")

# 检查是否有NULL的reviewer_id
print("\n" + "="*80)
print("检查NULL的reviewer_id")
print("="*80)

cursor.execute("SELECT COUNT(*) as count FROM review_tasks WHERE reviewer_id IS NULL")
null_count = cursor.fetchone()['count']
print(f"reviewer_id为NULL的记录数: {null_count}")

cursor.close()
conn.close()
