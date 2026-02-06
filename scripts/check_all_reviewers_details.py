#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查所有评委的详细信息"""

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
print("数据库中的所有评委详细信息")
print("="*80)

# 查询所有评委及其任务
cursor.execute("""
    SELECT 
        u.id, 
        u.phone, 
        u.name, 
        u.title,
        u.role,
        u.expert_background,
        u.reviewer_group_code,
        u.interview_group_code,
        i.id as institution_id,
        i.name as institution_name,
        (SELECT COUNT(*) FROM review_tasks rt WHERE rt.reviewer_id = u.id) as task_count
    FROM user_accounts u
    LEFT JOIN institutions i ON u.institution_id = i.id
    WHERE u.role = 'REVIEWER'
    ORDER BY u.id
""")

reviewers = cursor.fetchall()

print(f"\n找到 {len(reviewers)} 个评委:\n")

for idx, r in enumerate(reviewers, 1):
    print(f"评委 {idx}: {r['name']} (ID={r['id']})")
    print(f"  手机号: {r['phone']}")
    print(f"  职称: {r['title'] or '未设置'}")
    print(f"  专家背景: {r['expert_background'] or '未设置'}")
    print(f"  机构ID: {r['institution_id'] or '未设置'}")
    print(f"  机构名称: {r['institution_name'] or '未设置'}")
    print(f"  书审分组: {r['reviewer_group_code'] or '未设置'}")
    print(f"  面试分组: {r['interview_group_code'] or '未设置'}")
    print(f"  任务数: {r['task_count']}")
    print()

# 检查是否有"Reviewer A/B/C"这样的名字
print("="*80)
print("检查英文名称的评委")
print("="*80)

cursor.execute("""
    SELECT id, phone, name, title
    FROM user_accounts
    WHERE role = 'REVIEWER' AND name LIKE 'Reviewer%'
    ORDER BY name
""")

english_names = cursor.fetchall()

if english_names:
    print(f"\n发现 {len(english_names)} 个使用英文名称的评委:\n")
    for r in english_names:
        print(f"  ID={r['id']}: {r['name']} - {r['phone']} - {r['title']}")
    print("\n⚠️  建议更新这些评委的姓名和职称为中文")
else:
    print("\n✅ 所有评委都使用中文姓名")

cursor.close()
conn.close()
