#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查报名记录的 competition_id 是否正确保存"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pymysql
import requests

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
print("检查报名记录的 competition_id")
print("="*80)

# 1. 检查数据库中的报名记录
print("\n[1] 数据库中的报名记录（前10条）")
print("-" * 80)

cursor.execute("""
    SELECT 
        r.id,
        r.project_name,
        r.competition_id,
        r.status,
        c.name as competition_name,
        u.name as applicant_name,
        u.phone
    FROM registrations r
    LEFT JOIN competitions c ON r.competition_id = c.id
    LEFT JOIN user_accounts u ON r.applicant_id = u.id
    ORDER BY r.id DESC
    LIMIT 10
""")

registrations = cursor.fetchall()

print(f"\n找到 {len(registrations)} 条记录:\n")

has_null_competition = False

for reg in registrations:
    status = "✅" if reg['competition_id'] is not None else "❌"
    print(f"{status} 报名ID {reg['id']}: {reg['project_name']}")
    print(f"   申请人: {reg['applicant_name']} ({reg['phone']})")
    print(f"   竞赛ID: {reg['competition_id']}")
    print(f"   竞赛名称: {reg['competition_name'] or 'NULL'}")
    print(f"   状态: {reg['status']}")
    print()
    
    if reg['competition_id'] is None:
        has_null_competition = True

# 2. 统计空值情况
print("\n[2] competition_id 空值统计")
print("-" * 80)

cursor.execute("""
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN competition_id IS NULL THEN 1 ELSE 0 END) as null_count,
        SUM(CASE WHEN competition_id IS NOT NULL THEN 1 ELSE 0 END) as not_null_count
    FROM registrations
""")

stats = cursor.fetchone()

print(f"\n总报名数: {stats['total']}")
print(f"  有竞赛ID: {stats['not_null_count']} ({stats['not_null_count']*100//stats['total']}%)")
print(f"  无竞赛ID: {stats['null_count']} ({stats['null_count']*100//stats['total'] if stats['total'] > 0 else 0}%)")

if stats['null_count'] > 0:
    print(f"\n❌ 发现 {stats['null_count']} 条报名记录的 competition_id 为空！")
else:
    print(f"\n✅ 所有报名记录都有 competition_id")

# 3. 测试API返回
print("\n\n[3] 测试API返回（参赛者11）")
print("-" * 80)

try:
    # 登录
    BASE = "http://localhost:6031"
    login_resp = requests.post(f"{BASE}/api/auth/login", json={
        "phone": "13966000011",
        "name": "参赛者11",
        "role": "CONTESTANT"
    }, timeout=10)
    
    if login_resp.status_code == 200:
        token = login_resp.json()['data']['token']
        headers = {"Authorization": f"Bearer {token}"}
        
        # 获取我的报名
        reg_resp = requests.get(f"{BASE}/api/registrations/my", headers=headers, timeout=10)
        
        if reg_resp.status_code == 200:
            my_registrations = reg_resp.json()['data']
            
            print(f"\n✅ API请求成功，返回 {len(my_registrations)} 个报名\n")
            
            for reg in my_registrations:
                comp_id = reg.get('competitionId')
                status = "✅" if comp_id is not None else "❌"
                
                print(f"{status} 报名ID {reg['id']}: {reg['projectName']}")
                print(f"   竞赛ID: {comp_id}")
                print(f"   状态: {reg['status']}")
                print()
                
                if comp_id is None:
                    print(f"   ⚠️  问题：API返回的 competitionId 为空！")
                    print(f"   这会导致前端无法判断已报名哪个赛事")
                    print()
        else:
            print(f"❌ API请求失败: {reg_resp.status_code}")
    else:
        print(f"❌ 登录失败: {login_resp.status_code}")
        
except Exception as e:
    print(f"⚠️  服务器未启动或连接失败: {e}")

cursor.close()
conn.close()

print("\n" + "="*80)
print("诊断完成")
print("="*80)

if has_null_competition:
    print("\n问题确认：")
    print("❌ 数据库中存在 competition_id 为空的报名记录")
    print("❌ 这会导致前端无法判断用户已报名哪些赛事")
    print("❌ 所有赛事都会显示'立即报名'按钮")
    print("\n解决方案：")
    print("1. 修复后端创建报名时的逻辑，确保保存 competition_id")
    print("2. 修复 Registration 实体的序列化，返回 competitionId")
    print("3. 更新现有数据，补充缺失的 competition_id")
else:
    print("\n✅ 数据库数据正常")
