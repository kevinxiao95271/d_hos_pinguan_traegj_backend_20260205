#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复评委角色问题"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pymysql
from db_config import DB_CONFIG

# 数据库连接
conn = pymysql.connect(**DB_CONFIG)

cursor = conn.cursor(pymysql.cursors.DictCursor)

print("="*80)
print("修复评委角色问题")
print("="*80)

# 1. 检查王建国的评审任务
print("\n[1] 检查王建国(ID=3)的评审任务")
cursor.execute("""
    SELECT id, registration_id, stage, status
    FROM review_tasks
    WHERE reviewer_id = 3
""")

tasks = cursor.fetchall()
print(f"   找到 {len(tasks)} 个任务:")
for task in tasks:
    print(f"   - 任务{task['id']}: 报名{task['registration_id']}, {task['stage']}, {task['status']}")

# 2. 删除王建国的所有评审任务（因为他不是评委）
print("\n[2] 删除王建国的评审任务（他的角色是CONTESTANT，不应该有评审任务）")
cursor.execute("DELETE FROM review_tasks WHERE reviewer_id = 3")
deleted_count = cursor.rowcount
print(f"   ✅ 已删除 {deleted_count} 个任务")

# 3. 检查是否有其他CONTESTANT角色但有评审任务的账号
print("\n[3] 检查其他错误的评审任务分配")
cursor.execute("""
    SELECT DISTINCT u.id, u.name, u.phone, u.role, COUNT(rt.id) as task_count
    FROM user_accounts u
    INNER JOIN review_tasks rt ON u.id = rt.reviewer_id
    WHERE u.role != 'REVIEWER'
    GROUP BY u.id, u.name, u.phone, u.role
""")

wrong_assignments = cursor.fetchall()
if wrong_assignments:
    print(f"   ⚠️  发现 {len(wrong_assignments)} 个非评委角色但有评审任务的账号:")
    for acc in wrong_assignments:
        print(f"   - {acc['name']} ({acc['phone']}) - 角色:{acc['role']} - 任务数:{acc['task_count']}")
        # 删除这些错误的任务
        cursor.execute("DELETE FROM review_tasks WHERE reviewer_id = %s", (acc['id'],))
        print(f"     已删除该用户的所有评审任务")
else:
    print("   ✅ 没有发现其他错误的评审任务分配")

conn.commit()

# 4. 验证修复结果
print("\n[4] 验证修复结果")

# 检查当前有任务的评委
cursor.execute("""
    SELECT u.id, u.name, u.phone, u.role, COUNT(rt.id) as task_count
    FROM user_accounts u
    INNER JOIN review_tasks rt ON u.id = rt.reviewer_id
    WHERE u.role = 'REVIEWER'
    GROUP BY u.id, u.name, u.phone, u.role
    ORDER BY task_count DESC
""")

reviewers_with_tasks = cursor.fetchall()

print(f"\n   当前有任务的评委 ({len(reviewers_with_tasks)} 个):")
for r in reviewers_with_tasks:
    print(f"   - {r['name']} ({r['phone']}) - {r['task_count']} 个任务")

print("\n" + "="*80)
print("修复完成")
print("="*80)
print("\n✅ 已删除所有非评委角色的评审任务")
print("✅ 现在只有REVIEWER角色的用户才有评审任务")

cursor.close()
conn.close()
