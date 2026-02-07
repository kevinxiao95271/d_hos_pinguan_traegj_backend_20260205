#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""清理测试报名数据"""

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
print("清理测试报名数据 (Contestant A)")
print("="*80)

# 要删除的报名ID
test_registration_ids = [140, 141, 142, 143]

print(f"\n待删除的报名ID: {test_registration_ids}\n")

# 1. 查看详细信息
print("[1] 待删除的报名详情")
print("-" * 80)

cursor.execute("""
    SELECT 
        r.id,
        r.project_name,
        r.status,
        u.name as applicant_name,
        u.phone
    FROM registrations r
    LEFT JOIN user_accounts u ON r.applicant_id = u.id
    WHERE r.id IN (%s, %s, %s, %s)
    ORDER BY r.id
""" % tuple(test_registration_ids))

registrations = cursor.fetchall()

for reg in registrations:
    print(f"ID {reg['id']}: {reg['project_name']}")
    print(f"  申请人: {reg['applicant_name']} ({reg['phone']})")
    print(f"  状态: {reg['status']}")
    print()

# 2. 删除关联数据
print("\n[2] 删除关联数据")
print("-" * 80)

for reg_id in test_registration_ids:
    print(f"\n处理报名 ID {reg_id}...")
    
    # 删除评审任务关联的评分
    cursor.execute("""
        DELETE rs FROM review_scores rs
        INNER JOIN review_tasks rt ON rs.review_task_id = rt.id
        WHERE rt.registration_id = %s
    """, (reg_id,))
    score_count = cursor.rowcount
    if score_count > 0:
        print(f"  删除评分: {score_count} 条")
    
    # 删除评审任务
    cursor.execute("""
        DELETE FROM review_tasks WHERE registration_id = %s
    """, (reg_id,))
    task_count = cursor.rowcount
    if task_count > 0:
        print(f"  删除评审任务: {task_count} 条")
    
    # 删除成员
    cursor.execute("""
        DELETE FROM registration_members WHERE registration_id = %s
    """, (reg_id,))
    member_count = cursor.rowcount
    if member_count > 0:
        print(f"  删除成员: {member_count} 条")
    
    # 删除活动信息
    cursor.execute("""
        DELETE FROM activity_infos WHERE registration_id = %s
    """, (reg_id,))
    activity_count = cursor.rowcount
    if activity_count > 0:
        print(f"  删除活动信息: {activity_count} 条")
    
    # 删除项目摘要
    cursor.execute("""
        DELETE FROM project_summaries WHERE registration_id = %s
    """, (reg_id,))
    summary_count = cursor.rowcount
    if summary_count > 0:
        print(f"  删除项目摘要: {summary_count} 条")
    
    # 删除材料
    cursor.execute("""
        DELETE FROM material_files WHERE registration_id = %s
    """, (reg_id,))
    material_count = cursor.rowcount
    if material_count > 0:
        print(f"  删除材料: {material_count} 条")
    
    # 删除报名
    cursor.execute("""
        DELETE FROM registrations WHERE id = %s
    """, (reg_id,))
    print(f"  ✅ 删除报名")

conn.commit()

print(f"\n✅ 已删除 {len(test_registration_ids)} 个测试报名")

# 3. 验证删除结果
print("\n\n[3] 验证删除结果")
print("-" * 80)

cursor.execute("""
    SELECT COUNT(*) as count
    FROM registrations
    WHERE id IN (%s, %s, %s, %s)
""" % tuple(test_registration_ids))

remaining = cursor.fetchone()['count']

if remaining == 0:
    print(f"\n✅ 确认已删除，数据库中不再存在这些报名")
else:
    print(f"\n⚠️  还有 {remaining} 个报名未删除")

# 4. 显示剩余的报名
print("\n\n[4] 剩余的报名列表")
print("-" * 80)

cursor.execute("""
    SELECT 
        r.id,
        r.project_name,
        r.status,
        u.name as applicant_name,
        c.name as competition_name
    FROM registrations r
    LEFT JOIN user_accounts u ON r.applicant_id = u.id
    LEFT JOIN competitions c ON r.competition_id = c.id
    ORDER BY r.id DESC
    LIMIT 10
""")

remaining_registrations = cursor.fetchall()

print(f"\n最新的10个报名:\n")

for reg in remaining_registrations:
    print(f"ID {reg['id']}: {reg['project_name']}")
    print(f"  申请人: {reg['applicant_name']}")
    print(f"  赛事: {reg['competition_name']}")
    print(f"  状态: {reg['status']}")
    print()

cursor.close()
conn.close()

print("="*80)
print("清理完成")
print("="*80)
print("\n说明：")
print("- 已删除 Contestant A 的4个测试报名")
print("- 组委会查看项目列表时不会再看到这些测试数据")
print("- 保留了其他参赛者的真实报名数据")
