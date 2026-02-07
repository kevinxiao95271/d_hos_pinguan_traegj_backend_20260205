#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查脏数据赛事的关联数据"""

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
print("检查脏数据赛事的关联数据")
print("="*80)

# 要清理的脏数据赛事ID
dirty_competition_ids = [25, 26, 27]

print(f"\n待清理的赛事ID: {dirty_competition_ids}\n")

# 检查每个赛事的详细信息
for comp_id in dirty_competition_ids:
    print(f"{'='*80}")
    print(f"赛事ID {comp_id}")
    print(f"{'='*80}")
    
    # 1. 查询赛事基本信息
    cursor.execute("""
        SELECT id, name, stage, register_start, register_end
        FROM competitions
        WHERE id = %s
    """, (comp_id,))
    
    competition = cursor.fetchone()
    
    if not competition:
        print(f"⚠️  赛事ID {comp_id} 不存在")
        print()
        continue
    
    print(f"\n赛事信息:")
    print(f"  名称: {competition['name']}")
    print(f"  阶段: {competition['stage']}")
    print(f"  报名开始: {competition['register_start']}")
    print(f"  报名结束: {competition['register_end']}")
    
    # 2. 检查是否有报名数据
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM registrations
        WHERE competition_id = %s
    """, (comp_id,))
    
    reg_count = cursor.fetchone()['count']
    
    print(f"\n关联数据:")
    print(f"  报名数: {reg_count}")
    
    if reg_count > 0:
        print(f"  ⚠️  有报名数据，需要先清理")
        
        # 查看具体的报名
        cursor.execute("""
            SELECT r.id, r.project_name, r.status, u.name as applicant_name
            FROM registrations r
            LEFT JOIN user_accounts u ON r.applicant_id = u.id
            WHERE r.competition_id = %s
            LIMIT 10
        """, (comp_id,))
        
        registrations = cursor.fetchall()
        
        if registrations:
            print(f"\n  报名列表（最多显示10条）:")
            for reg in registrations:
                print(f"    - 报名ID {reg['id']}: {reg['project_name']} - {reg['status']} - {reg['applicant_name']}")
    else:
        print(f"  ✅ 无关联数据，可以直接删除")
    
    print()

# 统计总结
print(f"{'='*80}")
print("清理建议")
print(f"{'='*80}\n")

has_relations = False

for comp_id in dirty_competition_ids:
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM registrations
        WHERE competition_id = %s
    """, (comp_id,))
    
    count = cursor.fetchone()['count']
    
    if count > 0:
        has_relations = True
        print(f"赛事ID {comp_id}: ⚠️  有 {count} 个报名，需要先清理")
    else:
        print(f"赛事ID {comp_id}: ✅ 无关联数据，可以直接删除")

print()

if has_relations:
    print("建议步骤:")
    print("1. 先清理关联的报名数据")
    print("2. 再删除赛事")
else:
    print("✅ 所有脏数据赛事都无关联数据，可以直接删除")

cursor.close()
conn.close()

print("\n" + "="*80)
print("检查完成")
print("="*80)
