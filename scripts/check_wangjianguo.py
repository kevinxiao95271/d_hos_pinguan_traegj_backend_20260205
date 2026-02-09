#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查王建国的账号信息"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pymysql
from db_config import DB_CONFIG

# 数据库连接
conn = pymysql.connect(**DB_CONFIG)

cursor = conn.cursor(pymysql.cursors.DictCursor)

print("="*80)
print("检查王建国的账号信息")
print("="*80)

# 查询所有名为"王建国"的账号
cursor.execute("""
    SELECT id, phone, name, role, title, institution_id, 
           expert_background, reviewer_group_code, interview_group_code
    FROM user_accounts
    WHERE name = '王建国'
    ORDER BY id
""")

accounts = cursor.fetchall()

print(f"\n找到 {len(accounts)} 个名为'王建国'的账号:\n")

for acc in accounts:
    print(f"账号ID: {acc['id']}")
    print(f"  手机号: {acc['phone']}")
    print(f"  姓名: {acc['name']}")
    print(f"  角色: {acc['role']}")
    print(f"  职称: {acc['title']}")
    print(f"  专家背景: {acc['expert_background']}")
    print(f"  书审分组: {acc['reviewer_group_code']}")
    print(f"  面试分组: {acc['interview_group_code']}")
    print()

# 检查手机号13800000002的所有账号
print("="*80)
print("检查手机号 13800000002 的所有账号")
print("="*80)

cursor.execute("""
    SELECT id, phone, name, role, title
    FROM user_accounts
    WHERE phone = '13800000002'
    ORDER BY id
""")

phone_accounts = cursor.fetchall()

print(f"\n找到 {len(phone_accounts)} 个使用手机号 13800000002 的账号:\n")

for acc in phone_accounts:
    print(f"ID={acc['id']}: {acc['name']} - 角色={acc['role']} - 职称={acc['title']}")

# 检查是否有REVIEWER角色但不在用户提供的书审专家列表中的评委
print("\n" + "="*80)
print("所有REVIEWER角色的用户")
print("="*80)

cursor.execute("""
    SELECT u.id, u.phone, u.name, u.title, u.role,
           u.expert_background, u.reviewer_group_code,
           i.name as institution_name,
           (SELECT COUNT(*) FROM review_tasks rt WHERE rt.reviewer_id = u.id) as task_count
    FROM user_accounts u
    LEFT JOIN institutions i ON u.institution_id = i.id
    WHERE u.role = 'REVIEWER'
    ORDER BY u.name
""")

reviewers = cursor.fetchall()

print(f"\n找到 {len(reviewers)} 个REVIEWER角色的用户:\n")

# 用户提供的书审专家名单
book_reviewers = [
    '李明华', '张秀英', '陈卫东', '刘芳', '赵志强', '孙丽娟',
    '周建平', '吴晓明', '郑海波', '马丽华', '黄文龙', '徐静',
    '林建新', '钱志远', '何晓东', '陈明', '刘建平'
]

print("在书审专家列表中的评委:")
for r in reviewers:
    if r['name'] in book_reviewers:
        print(f"  ✅ {r['name']} ({r['phone']}) - {r['title']} - 任务数:{r['task_count']}")

print("\n不在书审专家列表中的评委:")
for r in reviewers:
    if r['name'] not in book_reviewers:
        print(f"  ⚠️  {r['name']} ({r['phone']}) - {r['role']} - 任务数:{r['task_count']}")

cursor.close()
conn.close()
