#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""直接测试查询API"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import json

BASE = "http://localhost:6031"

# 登录
phone = "13800000002"
name = "王建国"

print("="*80)
print(f"测试评委API - {name} ({phone})")
print("="*80)

login_resp = requests.post(f"{BASE}/api/auth/login", json={
    "phone": phone,
    "name": name,
    "role": "REVIEWER"
})

if login_resp.status_code != 200:
    print(f"登录失败: {login_resp.status_code}")
    exit(1)

login_data = login_resp.json()['data']
reviewer_id = login_data['id']
token = login_data['token']

print(f"\n✅ 登录成功 (ID={reviewer_id})\n")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 测试1: 直接用reviewerId参数查询
print("[测试1] GET /api/reviews/tasks?reviewerId=3")
resp1 = requests.get(f"{BASE}/api/reviews/tasks?reviewerId=3", headers=headers)
print(f"状态码: {resp1.status_code}")
if resp1.status_code == 200:
    data = resp1.json()['data']
    print(f"任务数: {len(data)}")
    if data:
        print("前3个任务:")
        for task in data[:3]:
            print(f"  - 任务{task['id']}: stage={task['stage']}, status={task['status']}")
else:
    print(f"错误: {resp1.text}")

# 测试2: 用my-tasks接口
print(f"\n[测试2] GET /api/reviews/my-tasks")
resp2 = requests.get(f"{BASE}/api/reviews/my-tasks", headers=headers)
print(f"状态码: {resp2.status_code}")
if resp2.status_code == 200:
    data = resp2.json()['data']
    print(f"任务数: {len(data)}")
    if data:
        print("前3个任务:")
        for task in data[:3]:
            print(f"  - 任务{task['id']}: {task.get('projectName')} ({task['status']})")
else:
    print(f"错误: {resp2.text}")

# 测试3: 验证token中的userId
print(f"\n[测试3] 验证token payload")
import base64
try:
    # JWT的第二部分是payload
    payload_encoded = token.split('.')[1]
    # 添加padding
    padding = 4 - len(payload_encoded) % 4
    if padding:
        payload_encoded += '=' * padding
    payload_json = base64.b64decode(payload_encoded)
    payload = json.loads(payload_json)
    print(f"Token中的sub(userId): {payload.get('sub')}")
    print(f"Token中的role: {payload.get('role')}")
    print(f"登录返回的ID: {reviewer_id}")
    if str(payload.get('sub')) == str(reviewer_id):
        print("✅ Token中的userId与登录ID一致")
    else:
        print("❌ Token中的userId与登录ID不一致！")
except Exception as e:
    print(f"解析token失败: {e}")
