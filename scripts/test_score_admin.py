#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用管理员账号测试评分接口"""

import requests
import json

BASE_URL = "http://localhost:6031"

# 1. 用管理员登录（之前测试成功的）
print("1. 管理员登录...")
login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
    "phone": "13800000041",
    "name": "CommitteeAdmin A",
    "role": "COMMITTEE_ADMIN"
}, timeout=5)

print(f"状态码: {login_resp.status_code}")

if login_resp.status_code != 200:
    print(f"登录失败: {login_resp.text}")
    exit(1)

login_data = login_resp.json()
if not login_data.get('success'):
    print(f"登录失败: {login_data}")
    exit(1)

token = login_data['data']['token']
print(f"✓ 登录成功")

# 2. 提交评分（用管理员token测试接口是否正常）
print("\n2. 测试评分接口...")
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

score_data = {
    "reviewTaskId": 115,
    "plan": 10.0,
    "problem": 10.0,
    "action": 10.0,
    "success": 10.0,
    "review": 10.0,
    "operation": 10.0,
    "presentation": 10.0,
    "highlight": "测试亮点",
    "weakness": "测试不足"
}

print(f"请求: POST /api/reviews/scores")
print(f"数据: {json.dumps(score_data, ensure_ascii=False)}")

score_resp = requests.post(
    f"{BASE_URL}/api/reviews/scores",
    json=score_data,
    headers=headers,
    timeout=5
)

print(f"\n状态码: {score_resp.status_code}")
print(f"响应: {score_resp.text}")

if score_resp.status_code == 200:
    result = score_resp.json()
    if result.get('success'):
        print(f"\n✓ 评分接口正常工作!")
    else:
        print(f"\n✗ 业务失败: {result.get('message')}")
else:
    print(f"\n✗ HTTP错误")
