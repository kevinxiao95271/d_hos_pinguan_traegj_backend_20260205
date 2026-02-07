#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""清理脏数据赛事"""

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
print("清理脏数据赛事")
print("="*80)

# 1. 首先查看所有赛事及其报名数
print("\n[1] 当前所有赛事及报名数统计")
print("-" * 80)

cursor.execute("""
    SELECT 
        c.id,
        c.name,
        c.stage,
        c.register_start,
        c.register_end,
        COUNT(r.id) as registration_count
    FROM competitions c
    LEFT JOIN registrations r ON c.id = r.competition_id
    GROUP BY c.id, c.name, c.stage, c.register_start, c.register_end
    ORDER BY c.id
""")

competitions = cursor.fetchall()

print(f"\n找到 {len(competitions)} 个赛事:\n")

competitions_to_keep = []
competitions_to_delete = []

for comp in competitions:
    status = ""
    should_delete = False
    
    # 判断是否为脏数据
    if comp['registration_count'] == 0 and comp['register_start'] is None:
        status = "❌ 脏数据（无报名且缺失时间）"
        should_delete = True
        competitions_to_delete.append(comp['id'])
    elif comp['registration_count'] > 0:
        status = f"✅ 保留（有 {comp['registration_count']} 个报名）"
        competitions_to_keep.append(comp['id'])
    elif comp['register_start'] is not None:
        status = f"✅ 保留（有完整时间配置）"
        competitions_to_keep.append(comp['id'])
    else:
        status = "⚠️  待确认"
    
    print(f"ID {comp['id']}: {comp['name']}")
    print(f"  阶段: {comp['stage']}")
    print(f"  报名时间: {comp['register_start']} ~ {comp['register_end']}")
    print(f"  报名数: {comp['registration_count']}")
    print(f"  状态: {status}")
    print()

# 2. 显示清理计划
print("\n" + "="*80)
print("清理计划")
print("="*80)

print(f"\n保留的赛事 ({len(competitions_to_keep)} 个):")
for comp_id in competitions_to_keep:
    comp = next(c for c in competitions if c['id'] == comp_id)
    print(f"  - ID {comp_id}: {comp['name']} (报名数: {comp['registration_count']})")

print(f"\n待删除的赛事 ({len(competitions_to_delete)} 个):")
for comp_id in competitions_to_delete:
    comp = next(c for c in competitions if c['id'] == comp_id)
    print(f"  - ID {comp_id}: {comp['name']} (脏数据)")

# 3. 执行删除
if competitions_to_delete:
    print("\n" + "="*80)
    print("执行删除")
    print("="*80)
    
    for comp_id in competitions_to_delete:
        print(f"\n删除赛事 ID {comp_id}...")
        
        # 检查是否真的没有报名数据
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM registrations
            WHERE competition_id = %s
        """, (comp_id,))
        
        count = cursor.fetchone()['count']
        
        if count > 0:
            print(f"  ⚠️  跳过：发现 {count} 个报名数据，不能删除")
            continue
        
        # 删除赛事
        cursor.execute("""
            DELETE FROM competitions
            WHERE id = %s
        """, (comp_id,))
        
        print(f"  ✅ 已删除")
    
    conn.commit()
    print(f"\n✅ 已删除 {len(competitions_to_delete)} 个脏数据赛事")
else:
    print("\n✅ 没有需要删除的脏数据赛事")

# 4. 验证删除结果
print("\n" + "="*80)
print("删除后的赛事列表")
print("="*80)

cursor.execute("""
    SELECT 
        c.id,
        c.name,
        c.stage,
        c.register_start,
        c.register_end,
        COUNT(r.id) as registration_count
    FROM competitions c
    LEFT JOIN registrations r ON c.id = r.competition_id
    GROUP BY c.id, c.name, c.stage, c.register_start, c.register_end
    ORDER BY c.id
""")

remaining_competitions = cursor.fetchall()

print(f"\n剩余 {len(remaining_competitions)} 个赛事:\n")

for comp in remaining_competitions:
    print(f"ID {comp['id']}: {comp['name']}")
    print(f"  阶段: {comp['stage']}")
    print(f"  报名数: {comp['registration_count']}")
    print(f"  报名时间: {comp['register_start']} ~ {comp['register_end']}")
    print()

cursor.close()
conn.close()

print("="*80)
print("清理完成")
print("="*80)
print("\n说明：")
print("- 已删除的赛事不会再出现在赛事列表API中")
print("- GET /api/competitions 将只返回剩余的有效赛事")
