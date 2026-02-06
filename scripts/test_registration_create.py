#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试报名创建API"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import json

BASE = "http://localhost:6031"

print("="*80)
print("测试报名创建API")
print("="*80)

# 1. 参赛者登录
print("\n[1] 参赛者登录")
r = requests.post(f"{BASE}/api/auth/login", json={
    "phone": "13900000001",
    "name": "测试参赛者",
    "role": "CONTESTANT"
})

if r.status_code != 200:
    print(f"登录失败: {r.status_code}")
    exit(1)

token = r.json()['data']['token']
user_id = r.json()['data']['id']
print(f"登录成功: ID={user_id}")

headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# 2. 获取赛事列表
print("\n[2] 获取赛事列表")
r2 = requests.get(f"{BASE}/api/competitions", headers=headers)
competitions = r2.json()['data']
print(f"赛事数量: {len(competitions)}")
if competitions:
    comp = competitions[0]
    print(f"使用赛事: ID={comp['id']}, 名称={comp['name']}")
    competition_id = comp['id']
else:
    print("没有赛事，无法测试")
    exit(1)

# 3. 获取机构列表
print("\n[3] 获取机构列表")
r3 = requests.get(f"{BASE}/api/institutions", headers=headers)
institutions = r3.json()['data']
print(f"机构数量: {len(institutions)}")
if institutions:
    inst = institutions[0]
    print(f"使用机构: ID={inst['id']}, 名称={inst['name']}")
    institution_id = inst['id']
else:
    print("没有机构，无法测试")
    exit(1)

# 4. 创建报名（最少参数）
print("\n[4] 创建报名")
print("请求参数:")
create_data = {
    "competitionId": competition_id,
    "institutionId": institution_id,
    "projectName": "测试项目-自动创建",
    "groupType": "BASIC"
}
print(json.dumps(create_data, indent=2, ensure_ascii=False))

r4 = requests.post(f"{BASE}/api/registrations", headers=headers, json=create_data)

print(f"\n状态码: {r4.status_code}")
if r4.status_code == 200:
    result = r4.json()
    if result.get('success'):
        reg = result['data']
        print(f"[成功] 创建报名成功")
        print(f"  报名ID: {reg['id']}")
        print(f"  项目名称: {reg.get('projectName')}")
        print(f"  状态: {reg.get('status')}")
        print(f"  创建时间: {reg.get('createdAt')}")
        
        registration_id = reg['id']
        
        # 5. 查看我的报名列表
        print("\n[5] 查看我的报名列表")
        r5 = requests.get(f"{BASE}/api/registrations/my", headers=headers)
        my_regs = r5.json()['data']
        print(f"我的报名数量: {len(my_regs)}")
        if my_regs:
            print(f"最新报名: {my_regs[0].get('projectName')}")
    else:
        print(f"[失败] {result.get('message')}")
else:
    print(f"[失败] {r4.text}")

print("\n" + "="*80)
print("测试完成")
print("="*80)
