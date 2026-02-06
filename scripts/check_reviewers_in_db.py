#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""直接查询数据库中的评委数据"""

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
print("数据库中的评委账号")
print("="*80)

# 查询所有评委
cursor.execute("""
    SELECT u.id, u.phone, u.name, u.role, u.title, 
           i.name as institution_name,
           (SELECT COUNT(*) FROM review_tasks rt WHERE rt.reviewer_id = u.id) as task_count
    FROM user_accounts u
    LEFT JOIN institutions i ON u.institution_id = i.id
    WHERE u.role = 'REVIEWER'
    ORDER BY u.id
""")

reviewers = cursor.fetchall()

print(f"\n找到 {len(reviewers)} 个评委账号:\n")

reviewers_with_tasks = []
reviewers_without_tasks = []

for r in reviewers:
    task_count = r['task_count']
    if task_count > 0:
        reviewers_with_tasks.append(r)
    else:
        reviewers_without_tasks.append(r)

# 显示有任务的评委
if reviewers_with_tasks:
    print("=" * 80)
    print(f"有任务的评委 ({len(reviewers_with_tasks)} 个):")
    print("=" * 80)
    for r in reviewers_with_tasks:
        print(f"\nID: {r['id']}")
        print(f"  手机号: {r['phone']}")
        print(f"  姓名: {r['name']}")
        print(f"  职称: {r['title'] or '未设置'}")
        print(f"  机构: {r['institution_name'] or '未设置'}")
        print(f"  任务数: {r['task_count']} 个")

# 显示前5个无任务的评委
if reviewers_without_tasks:
    print("\n" + "=" * 80)
    print(f"无任务的评委 (前5个):")
    print("=" * 80)
    for r in reviewers_without_tasks[:5]:
        print(f"\nID: {r['id']}")
        print(f"  手机号: {r['phone']}")
        print(f"  姓名: {r['name']}")
        print(f"  职称: {r['title'] or '未设置'}")

# 查询评审任务详情
if reviewers_with_tasks:
    print("\n" + "=" * 80)
    print("评审任务详情:")
    print("=" * 80)
    
    for r in reviewers_with_tasks[:2]:  # 只显示前2个评委的任务
        reviewer_id = r['id']
        cursor.execute("""
            SELECT rt.id, rt.status, rt.stage,
                   reg.id as reg_id, reg.project_name, reg.status as reg_status,
                   i.name as institution_name
            FROM review_tasks rt
            LEFT JOIN registrations reg ON rt.registration_id = reg.id
            LEFT JOIN institutions i ON reg.institution_id = i.id
            WHERE rt.reviewer_id = %s
            ORDER BY rt.id
        """, (reviewer_id,))
        
        tasks = cursor.fetchall()
        
        print(f"\n{r['name']} (ID={reviewer_id}, {r['phone']})的任务:")
        for t in tasks:
            print(f"  任务{t['id']}: 报名{t['reg_id']} - {t['project_name']} - {t['status']}")

print("\n" + "="*80)
print("推荐测试账号:")
print("="*80)

if reviewers_with_tasks:
    print("\n✅ 有任务的评委（可直接测试打分）:\n")
    for r in reviewers_with_tasks[:3]:
        print(f"手机号: {r['phone']}")
        print(f"姓名: {r['name']}")
        print(f"角色: REVIEWER")
        print(f"任务数: {r['task_count']} 个")
        print()
else:
    print("\n⚠️  没有评委有任务，请先分配任务")

cursor.close()
conn.close()
