#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试按品管工具筛选报名"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pymysql
import requests
import json

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
print("测试按品管工具筛选报名")
print("="*80)

# 1. 检查报名106的详细信息
print("\n[1] 检查报名106的数据")
print("-" * 80)

cursor.execute("""
    SELECT 
        r.id,
        r.project_name,
        r.group_code,
        a.method_code,
        a.method_other
    FROM registrations r
    LEFT JOIN activity_infos a ON r.id = a.registration_id
    WHERE r.id = 106
""")

reg = cursor.fetchone()

if reg:
    print(f"\n报名ID 106: {reg['project_name']}")
    print(f"  组代码: {reg['group_code']}")
    print(f"  品管工具代码: {reg['method_code']}")
    print(f"  品管工具其他: {reg['method_other']}")
else:
    print("\n未找到报名106")
    cursor.close()
    conn.close()
    exit(1)

# 2. 查询所有报名的品管工具
print("\n\n[2] 数据库中的品管工具分布")
print("-" * 80)

cursor.execute("""
    SELECT 
        a.method_code,
        COUNT(*) as count
    FROM registrations r
    INNER JOIN activity_infos a ON r.id = a.registration_id
    WHERE a.method_code IS NOT NULL
    GROUP BY a.method_code
    ORDER BY count DESC
""")

methods = cursor.fetchall()

print(f"\n找到 {len(methods)} 种品管工具:\n")

for m in methods:
    print(f"代码: {m['method_code']:30s} 数量: {m['count']}")

# 3. 查询字典表中的method配置
print("\n\n[3] 字典表中的method配置")
print("-" * 80)

cursor.execute("""
    SELECT code, label, active
    FROM dictionary_items
    WHERE type = 'method'
    ORDER BY code
""")

dict_methods = cursor.fetchall()

print(f"\n找到 {len(dict_methods)} 个method字典项:\n")

for d in dict_methods:
    status = "✅" if d['active'] else "❌"
    print(f"{status} 代码: {d['code']:20s} 标签: {d['label']}")

cursor.close()
conn.close()

# 4. 测试API筛选
print("\n\n[4] 测试API筛选")
print("-" * 80)

BASE = "http://localhost:6031"

try:
    # 登录
    print("\n登录...")
    login_resp = requests.post(f"{BASE}/api/auth/login", json={
        "phone": "13800000003",
        "name": "组委会管理员",
        "role": "COMMITTEE"
    }, timeout=10)
    
    if login_resp.status_code != 200:
        print(f"❌ 登录失败: {login_resp.status_code}")
        exit(1)
    
    token = login_resp.json()['data']['token']
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ 登录成功")
    
    # 测试1: 获取所有报名（不筛选）
    print("\n\n测试1: 获取所有报名（赛事21）")
    print("-" * 40)
    
    resp1 = requests.get(
        f"{BASE}/api/registrations",
        params={"competitionId": 21},
        headers=headers,
        timeout=10
    )
    
    if resp1.status_code == 200:
        all_regs = resp1.json()['data']
        print(f"✅ 成功，返回 {len(all_regs)} 个报名")
        
        # 检查报名106是否在列表中
        reg_106 = next((r for r in all_regs if r['id'] == 106), None)
        if reg_106:
            print(f"\n找到报名106:")
            print(f"  ID: {reg_106['id']}")
            print(f"  项目名称: {reg_106['projectName']}")
            print(f"  组代码: {reg_106.get('groupCode', 'N/A')}")
            # 注意：这里可能没有返回methodCode
        else:
            print("\n⚠️  未找到报名106")
    else:
        print(f"❌ 请求失败: {resp1.status_code}")
        print(f"响应: {resp1.text[:500]}")
    
    # 测试2: 按品管工具筛选（使用数据库中的实际值）
    if reg:
        method_code = reg['method_code']
        
        print(f"\n\n测试2: 按品管工具筛选 (methodCode={method_code})")
        print("-" * 40)
        
        # 检查后端是否有筛选接口
        print("\n尝试几种可能的API格式...")
        
        # 格式1: query参数
        print("\n格式1: GET /api/registrations?competitionId=21&methodCode=xxx")
        resp2 = requests.get(
            f"{BASE}/api/registrations",
            params={
                "competitionId": 21,
                "methodCode": method_code
            },
            headers=headers,
            timeout=10
        )
        
        if resp2.status_code == 200:
            filtered_regs = resp2.json()['data']
            print(f"  状态码: 200")
            print(f"  返回: {len(filtered_regs)} 个报名")
            
            if len(filtered_regs) > 0:
                print(f"  ✅ 筛选成功！")
                for r in filtered_regs[:3]:
                    print(f"    - ID {r['id']}: {r['projectName']}")
            else:
                print(f"  ⚠️  返回空列表（筛选可能无效）")
        else:
            print(f"  状态码: {resp2.status_code}")
        
        # 格式2: POST筛选
        print(f"\n格式2: POST /api/registrations/filter")
        try:
            resp3 = requests.post(
                f"{BASE}/api/registrations/filter",
                json={
                    "competitionId": 21,
                    "methodCode": method_code
                },
                headers=headers,
                timeout=10
            )
            
            if resp3.status_code == 200:
                filtered_regs = resp3.json()['data']
                print(f"  状态码: 200")
                print(f"  返回: {len(filtered_regs)} 个报名")
            else:
                print(f"  状态码: {resp3.status_code}")
        except Exception as e:
            print(f"  请求失败: {e}")
        
        # 格式3: 查看Swagger文档
        print(f"\n\n建议：")
        print(f"  1. 查看Swagger文档: http://localhost:6031/swagger")
        print(f"  2. 查找筛选报名的API接口")
        print(f"  3. 确认筛选参数名称（methodCode 还是 method_code）")

except Exception as e:
    print(f"❌ API测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("诊断完成")
print("="*80)

print("\n分析：")
print("1. 检查数据库中报名106的品管工具代码")
print("2. 检查后端是否支持按品管工具筛选")
print("3. 检查前端传递的筛选参数是否正确")
print("4. 检查后端筛选逻辑是否正确")
