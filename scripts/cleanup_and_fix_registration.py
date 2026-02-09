#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""清理垃圾报名数据并修改赛事时间"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pymysql
from db_config import DB_CONFIG
from datetime import datetime, timedelta

# 数据库连接
conn = pymysql.connect(**DB_CONFIG)

cursor = conn.cursor(pymysql.cursors.DictCursor)

print("="*80)
print("清理垃圾数据并修复赛事时间")
print("="*80)

# 1. 检查 Contestant A (13800000011) 的报名
print("\n[1] 检查 Contestant A 的报名...")
print("-" * 80)

cursor.execute("""
    SELECT u.id, u.phone, u.name
    FROM user_accounts u
    WHERE u.phone = '13800000011'
""")

contestant_a = cursor.fetchone()

if contestant_a:
    print(f"找到用户: {contestant_a['name']} (ID={contestant_a['id']})")
    
    cursor.execute("""
        SELECT 
            r.id,
            r.project_name,
            r.competition_id,
            r.status,
            c.name as competition_name,
            c.id as comp_id_check
        FROM registrations r
        LEFT JOIN competitions c ON r.competition_id = c.id
        WHERE r.applicant_id = %s
        ORDER BY r.id
    """, (contestant_a['id'],))
    
    registrations = cursor.fetchall()
    
    print(f"\n找到 {len(registrations)} 个报名:\n")
    
    invalid_registrations = []
    valid_registrations = []
    
    for reg in registrations:
        if reg['comp_id_check'] is None:
            print(f"❌ 报名ID {reg['id']}: {reg['project_name']} - 赛事ID {reg['competition_id']} 不存在")
            invalid_registrations.append(reg['id'])
        else:
            print(f"✅ 报名ID {reg['id']}: {reg['project_name']} - {reg['competition_name']} (状态: {reg['status']})")
            valid_registrations.append(reg['id'])
    
    # 删除无效的报名
    if invalid_registrations:
        print(f"\n准备删除 {len(invalid_registrations)} 个无效报名...")
        
        for reg_id in invalid_registrations:
            # 先删除关联的成员
            cursor.execute("DELETE FROM registration_members WHERE registration_id = %s", (reg_id,))
            print(f"  删除报名 {reg_id} 的成员数据")
            
            # 删除活动信息
            cursor.execute("DELETE FROM registration_activities WHERE registration_id = %s", (reg_id,))
            print(f"  删除报名 {reg_id} 的活动信息")
            
            # 删除报名
            cursor.execute("DELETE FROM registrations WHERE id = %s", (reg_id,))
            print(f"  删除报名 {reg_id}")
        
        conn.commit()
        print(f"\n✅ 已删除 {len(invalid_registrations)} 个无效报名")
    
    if valid_registrations:
        print(f"\n保留 {len(valid_registrations)} 个有效报名")
else:
    print("未找到 Contestant A 账号")

# 2. 检查所有无效的报名（赛事不存在）
print("\n\n[2] 检查所有无效报名（赛事不存在）...")
print("-" * 80)

cursor.execute("""
    SELECT 
        r.id,
        r.project_name,
        r.competition_id,
        r.applicant_id,
        u.name as applicant_name
    FROM registrations r
    LEFT JOIN competitions c ON r.competition_id = c.id
    LEFT JOIN user_accounts u ON r.applicant_id = u.id
    WHERE c.id IS NULL
    ORDER BY r.id
""")

all_invalid = cursor.fetchall()

if all_invalid:
    print(f"\n找到 {len(all_invalid)} 个无效报名:\n")
    
    for reg in all_invalid:
        print(f"报名ID {reg['id']}: {reg['project_name']} - 申请人: {reg['applicant_name']} - 赛事ID {reg['competition_id']} 不存在")
    
    print(f"\n删除这些无效报名...")
    
    for reg in all_invalid:
        reg_id = reg['id']
        cursor.execute("DELETE FROM registration_members WHERE registration_id = %s", (reg_id,))
        cursor.execute("DELETE FROM registration_activities WHERE registration_id = %s", (reg_id,))
        cursor.execute("DELETE FROM registrations WHERE id = %s", (reg_id,))
    
    conn.commit()
    print(f"✅ 已删除 {len(all_invalid)} 个无效报名")
else:
    print("\n✅ 没有找到无效报名")

# 3. 更新赛事21的报名时间
print("\n\n[3] 更新赛事21的报名时间...")
print("-" * 80)

cursor.execute("SELECT id, name, stage, register_start, register_end FROM competitions WHERE id = 21")
comp21 = cursor.fetchone()

if comp21:
    print(f"\n当前赛事21信息:")
    print(f"  名称: {comp21['name']}")
    print(f"  阶段: {comp21['stage']}")
    print(f"  报名开始: {comp21['register_start']}")
    print(f"  报名结束: {comp21['register_end']}")
    
    # 设置新的报名时间：当前时间 - 5天 到 当前时间 + 20天
    now = datetime.now()
    new_start = now - timedelta(days=5)
    new_end = now + timedelta(days=20)
    
    cursor.execute("""
        UPDATE competitions
        SET register_start = %s,
            register_end = %s,
            stage = 'REGISTER'
        WHERE id = 21
    """, (new_start, new_end))
    
    conn.commit()
    
    print(f"\n✅ 已更新赛事21的报名时间:")
    print(f"  报名开始: {new_start.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  报名结束: {new_end.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  阶段: REGISTER")
else:
    print("\n未找到赛事ID 21")

# 4. 检查所有赛事的报名时间
print("\n\n[4] 所有赛事的报名时间状态...")
print("-" * 80)

cursor.execute("""
    SELECT id, name, stage, register_start, register_end,
           book_review_start, book_review_end
    FROM competitions
    ORDER BY id
""")

competitions = cursor.fetchall()
now = datetime.now()

print(f"\n当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}\n")

for comp in competitions:
    print(f"赛事ID {comp['id']}: {comp['name']}")
    print(f"  阶段: {comp['stage']}")
    
    if comp['register_start'] and comp['register_end']:
        is_open = comp['register_start'] <= now <= comp['register_end']
        status = "✅ 可报名" if is_open else "❌ 已关闭"
        print(f"  报名时间: {comp['register_start']} ~ {comp['register_end']} {status}")
    else:
        print(f"  报名时间: 未设置")
    
    if comp['book_review_start'] and comp['book_review_end']:
        print(f"  书审时间: {comp['book_review_start']} ~ {comp['book_review_end']}")
    print()

cursor.close()
conn.close()

print("="*80)
print("清理完成")
print("="*80)
