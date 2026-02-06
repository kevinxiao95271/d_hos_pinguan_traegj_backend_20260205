#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""探索参赛者数据结构"""

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
print("探索参赛者和报名数据")
print("="*80)

# 查询用户提到的这几个报名
registration_ids = [116, 117, 118, 119, 120]

print("\n[1] 查询指定的报名信息")
print("-" * 80)

cursor.execute("""
    SELECT 
        r.id,
        r.project_name,
        r.applicant_id,
        r.status,
        r.created_at,
        r.submitted_at,
        i.name as institution_name,
        u.id as user_id,
        u.phone as user_phone,
        u.name as user_name,
        u.role as user_role
    FROM registrations r
    LEFT JOIN institutions i ON r.institution_id = i.id
    LEFT JOIN user_accounts u ON r.applicant_id = u.id
    WHERE r.id IN (%s, %s, %s, %s, %s)
    ORDER BY r.id
""" % tuple(registration_ids))

registrations = cursor.fetchall()

print(f"\n找到 {len(registrations)} 个报名:\n")

for reg in registrations:
    print(f"报名ID: {reg['id']}")
    print(f"  项目名称: {reg['project_name']}")
    print(f"  机构: {reg['institution_name']}")
    print(f"  申请人ID (applicant_id): {reg['applicant_id']}")
    print(f"  状态: {reg['status']}")
    print(f"  创建时间: {reg['created_at']}")
    print(f"  用户账号信息:")
    if reg['user_id']:
        print(f"    - 用户ID: {reg['user_id']}")
        print(f"    - 手机号: {reg['user_phone']}")
        print(f"    - 姓名: {reg['user_name']}")
        print(f"    - 角色: {reg['user_role']}")
    else:
        print(f"    ⚠️  申请人ID {reg['applicant_id']} 在 user_accounts 表中不存在！")
    print()

# 检查所有 CONTESTANT 角色的用户
print("\n[2] 所有 CONTESTANT 角色的用户")
print("-" * 80)

cursor.execute("""
    SELECT 
        u.id,
        u.phone,
        u.name,
        u.role,
        u.institution_id,
        i.name as institution_name,
        COUNT(r.id) as registration_count
    FROM user_accounts u
    LEFT JOIN institutions i ON u.institution_id = i.id
    LEFT JOIN registrations r ON u.id = r.applicant_id
    WHERE u.role = 'CONTESTANT'
    GROUP BY u.id, u.phone, u.name, u.role, u.institution_id, i.name
    ORDER BY u.id
""")

contestants = cursor.fetchall()

print(f"\n找到 {len(contestants)} 个参赛者账号:\n")

for c in contestants:
    print(f"ID={c['id']}: {c['name']} ({c['phone']})")
    print(f"  机构: {c['institution_name'] or '未设置'}")
    print(f"  报名数: {c['registration_count']}")
    print()

# 检查报名的成员信息（可能包含"参赛者11"等名字）
print("\n[3] 报名成员信息（可能包含'参赛者11'等）")
print("-" * 80)

cursor.execute("""
    SELECT 
        rm.id,
        rm.registration_id,
        rm.role as member_role,
        rm.name as member_name,
        rm.title,
        r.project_name,
        r.applicant_id
    FROM registration_members rm
    INNER JOIN registrations r ON rm.registration_id = r.id
    WHERE rm.registration_id IN (%s, %s, %s, %s, %s)
    ORDER BY rm.registration_id, rm.role
""" % tuple(registration_ids))

members = cursor.fetchall()

print(f"\n找到 {len(members)} 个成员记录:\n")

for m in members:
    print(f"报名ID {m['registration_id']} - {m['project_name']}")
    print(f"  成员: {m['member_name']} ({m['member_role']}) - {m['title']}")
    print(f"  申请人ID: {m['applicant_id']}")
    print()

# 查找名字中包含"参赛者"的用户
print("\n[4] 名字包含'参赛者'的用户账号")
print("-" * 80)

cursor.execute("""
    SELECT id, phone, name, role, institution_id
    FROM user_accounts
    WHERE name LIKE '%参赛者%'
    ORDER BY id
""")

participants = cursor.fetchall()

if participants:
    print(f"\n找到 {len(participants)} 个账号:\n")
    for p in participants:
        print(f"ID={p['id']}: {p['name']} ({p['phone']}) - {p['role']}")
else:
    print("\n没有找到名字包含'参赛者'的账号")

# 检查赛事时间
print("\n[5] 赛事信息（检查报名时间）")
print("-" * 80)

cursor.execute("""
    SELECT id, name, stage, register_start, register_end,
           book_review_start, book_review_end
    FROM competitions
    ORDER BY id DESC
    LIMIT 3
""")

competitions = cursor.fetchall()

print(f"\n最近 {len(competitions)} 个赛事:\n")

for comp in competitions:
    print(f"赛事ID {comp['id']}: {comp['name']}")
    print(f"  阶段: {comp['stage']}")
    print(f"  报名时间: {comp['register_start']} ~ {comp['register_end']}")
    print(f"  书审时间: {comp['book_review_start']} ~ {comp['book_review_end']}")
    print()

cursor.close()
conn.close()

print("="*80)
print("探索完成")
print("="*80)
print("\n建议：")
print("1. 如果 applicant_id 对应的用户不存在，需要创建这些用户账号")
print("2. 确保这些用户的角色是 CONTESTANT")
print("3. 用户的姓名应该与报名成员中的名字一致")
print("4. 调整赛事的报名时间，确保包含当前时间")
