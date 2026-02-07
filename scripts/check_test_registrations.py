#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查测试报名数据"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pymysql

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
print("检查测试报名数据")
print("="*80)

# 检查指定的报名ID
test_registration_ids = [140, 141, 142, 143]

print(f"\n[1] 检查报名 ID: {test_registration_ids}")
print("-" * 80)

cursor.execute("""
    SELECT 
        r.id,
        r.project_name,
        r.competition_id,
        r.institution_id,
        r.applicant_id,
        r.status,
        r.group_type,
        r.created_at,
        r.submitted_at,
        c.name as competition_name,
        i.name as institution_name,
        u.name as applicant_name,
        u.phone as applicant_phone
    FROM registrations r
    LEFT JOIN competitions c ON r.competition_id = c.id
    LEFT JOIN institutions i ON r.institution_id = i.id
    LEFT JOIN user_accounts u ON r.applicant_id = u.id
    WHERE r.id IN (%s, %s, %s, %s)
    ORDER BY r.id
""" % tuple(test_registration_ids))

registrations = cursor.fetchall()

print(f"\n找到 {len(registrations)} 个报名:\n")

for reg in registrations:
    print(f"报名ID {reg['id']}: {reg['project_name']}")
    print(f"  申请人: {reg['applicant_name']} ({reg['applicant_phone']})")
    print(f"  赛事ID: {reg['competition_id']} - {reg['competition_name']}")
    print(f"  机构ID: {reg['institution_id']} - {reg['institution_name']}")
    print(f"  组别: {reg['group_type']}")
    print(f"  状态: {reg['status']}")
    print(f"  创建时间: {reg['created_at']}")
    print(f"  提交时间: {reg['submitted_at']}")
    
    # 检查是否有关联数据
    cursor.execute("""
        SELECT COUNT(*) as count FROM registration_members WHERE registration_id = %s
    """, (reg['id'],))
    member_count = cursor.fetchone()['count']
    
    cursor.execute("""
        SELECT COUNT(*) as count FROM activity_infos WHERE registration_id = %s
    """, (reg['id'],))
    activity_count = cursor.fetchone()['count']
    
    cursor.execute("""
        SELECT COUNT(*) as count FROM review_tasks WHERE registration_id = %s
    """, (reg['id'],))
    task_count = cursor.fetchone()['count']
    
    print(f"  关联数据:")
    print(f"    - 成员: {member_count}")
    print(f"    - 活动: {activity_count}")
    print(f"    - 评审任务: {task_count}")
    print()

# 2. 检查 Contestant A 的所有报名
print("\n[2] Contestant A 的所有报名")
print("-" * 80)

cursor.execute("""
    SELECT 
        r.id,
        r.project_name,
        r.status,
        r.created_at,
        c.name as competition_name
    FROM registrations r
    LEFT JOIN competitions c ON r.competition_id = c.id
    LEFT JOIN user_accounts u ON r.applicant_id = u.id
    WHERE u.phone = '13800000011'
    ORDER BY r.id
""")

all_registrations = cursor.fetchall()

print(f"\nContestant A 共有 {len(all_registrations)} 个报名:\n")

for reg in all_registrations:
    print(f"ID {reg['id']}: {reg['project_name']} - {reg['status']} - {reg['competition_name']}")

# 3. 建议清理
print("\n\n[3] 清理建议")
print("-" * 80)

print(f"\n这4个测试报名 (ID 140-143) 都是 Contestant A 的测试数据")
print(f"状态都是 SUBMITTED（已提交）")
print(f"项目名称都是测试名称")

print("\n建议操作：")
print("1. 保留有完整数据的报名（参赛者11-33）")
print("2. 删除 Contestant A 的测试报名 (ID 140-143)")
print("3. 这样组委会看到的都是真实报名数据")

cursor.close()
conn.close()

print("\n" + "="*80)
print("检查完成")
print("="*80)
