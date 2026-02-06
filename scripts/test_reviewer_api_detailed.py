#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""详细测试评委API"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import json

BASE = "http://localhost:6031"

print("="*80)
print("详细测试评委API")
print("="*80)

# 测试王建国账号
phone = "13800000002"
name = "王建国"

print(f"\n[1] 登录: {name} ({phone})")
login_resp = requests.post(f"{BASE}/api/auth/login", json={
    "phone": phone,
    "name": name,
    "role": "REVIEWER"
})

if login_resp.status_code != 200:
    print(f"登录失败: {login_resp.status_code}")
    print(login_resp.text)
    exit(1)

login_data = login_resp.json()['data']
reviewer_id = login_data['id']
token = login_data['token']

print(f"✅ 登录成功")
print(f"  评委ID: {reviewer_id}")
print(f"  Token: {token[:50]}...")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 测试获取任务列表
print(f"\n[2] 获取任务列表")
tasks_resp = requests.get(f"{BASE}/api/reviews/my-tasks", headers=headers)

print(f"状态码: {tasks_resp.status_code}")
print(f"响应:")
print(json.dumps(tasks_resp.json(), indent=2, ensure_ascii=False))

if tasks_resp.status_code == 200:
    tasks = tasks_resp.json()['data']
    print(f"\n任务数量: {len(tasks)}")
    
    if tasks:
        print("\n任务详情:")
        for task in tasks:
            print(f"  - 任务{task['id']}: {task.get('projectName', 'N/A')} ({task['status']})")
    else:
        print("\n⚠️  返回空数组，但数据库中应该有5个任务")
        print("   这可能是查询逻辑的问题")

# 测试其他评委
print("\n" + "="*80)
print("测试其他评委")
print("="*80)

for phone, name in [("13800000021", "李明华"), ("13800002004", "孙丽娟")]:
    print(f"\n{name} ({phone}):")
    
    login_resp = requests.post(f"{BASE}/api/auth/login", json={
        "phone": phone,
        "name": name,
        "role": "REVIEWER"
    })
    
    if login_resp.status_code != 200:
        print(f"  ❌ 登录失败")
        continue
    
    token = login_resp.json()['data']['token']
    tasks_resp = requests.get(f"{BASE}/api/reviews/my-tasks", 
                             headers={"Authorization": f"Bearer {token}"})
    
    if tasks_resp.status_code == 200:
        tasks = tasks_resp.json()['data']
        print(f"  任务数: {len(tasks)} 个")
    else:
        print(f"  ❌ 获取任务失败: {tasks_resp.status_code}")
