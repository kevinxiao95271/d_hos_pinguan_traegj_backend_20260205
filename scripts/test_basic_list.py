#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试基本的列表接口"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests

BASE = "http://localhost:6031"

print("="*80)
print("测试基本列表接口")
print("="*80)

try:
    # 登录
    print("\n[1] 登录...")
    login_resp = requests.post(f"{BASE}/api/auth/login", json={
        "phone": "13800000003",
        "name": "组委会管理员",
        "role": "COMMITTEE"
    }, timeout=10)
    
    if login_resp.status_code != 200:
        print(f"❌ 登录失败: {login_resp.status_code}")
        print(f"响应: {login_resp.text}")
        exit(1)
    
    token = login_resp.json()['data']['token']
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ 登录成功")
    
    # 测试1: 基本列表接口
    print("\n\n[2] 测试基本列表接口: GET /api/registrations?competitionId=21")
    print("-" * 80)
    
    resp1 = requests.get(
        f"{BASE}/api/registrations",
        params={"competitionId": 21},
        headers=headers,
        timeout=10
    )
    
    print(f"状态码: {resp1.status_code}")
    
    if resp1.status_code == 200:
        data = resp1.json()['data']
        print(f"✅ 成功，返回 {len(data)} 个报名")
    else:
        print(f"❌ 失败")
        print(f"响应头: {resp1.headers}")
        print(f"响应体:\n{resp1.text[:1000]}")
    
    # 测试2: 筛选接口（不传任何筛选参数）
    print("\n\n[3] 测试筛选接口（不传筛选参数）: GET /api/admin/registrations/filter?competitionId=21")
    print("-" * 80)
    
    resp2 = requests.get(
        f"{BASE}/api/admin/registrations/filter",
        params={"competitionId": 21},
        headers=headers,
        timeout=10
    )
    
    print(f"状态码: {resp2.status_code}")
    
    if resp2.status_code == 200:
        data = resp2.json()['data']
        print(f"✅ 成功，返回 {len(data)} 个报名")
    else:
        print(f"❌ 失败")
        print(f"响应头: {resp2.headers}")
        print(f"响应体:\n{resp2.text[:1000]}")
    
    # 测试3: 赛事列表
    print("\n\n[4] 测试赛事列表: GET /api/competitions")
    print("-" * 80)
    
    resp3 = requests.get(
        f"{BASE}/api/competitions",
        headers=headers,
        timeout=10
    )
    
    print(f"状态码: {resp3.status_code}")
    
    if resp3.status_code == 200:
        data = resp3.json()['data']
        print(f"✅ 成功，返回 {len(data)} 个赛事")
    else:
        print(f"❌ 失败")
        print(f"响应头: {resp3.headers}")
        print(f"响应体:\n{resp3.text[:1000]}")

except requests.exceptions.ConnectionError:
    print("\n❌ 连接失败，服务器未启动")
    print("请启动服务器：mvn spring-boot:run")
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("测试完成")
print("="*80)
