#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
评审任务API简单测试 - 输出详细错误信息
"""

import requests
import json

BASE_URL = "http://localhost:6031"

# 登录
login_url = f"{BASE_URL}/api/auth/login"
login_data = {
    "phone": "13800000041",
    "name": "CommitteeAdmin A",
    "role": "COMMITTEE_ADMIN"
}

print("=" * 60)
print("登录...")
print("=" * 60)
response = requests.post(login_url, json=login_data)
print(f"状态码: {response.status_code}")
print(f"响应: {response.text}\n")

if response.status_code != 200:
    print("登录失败")
    exit(1)

result = response.json()
if not result.get('success'):
    print("登录失败")
    exit(1)

token = result.get('data', {}).get('token')
print(f"Token: {token[:50]}...\n")

# 测试查询任务
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

print("=" * 60)
print("测试1: 查询书审任务（带stage参数）")
print("=" * 60)
url = f"{BASE_URL}/api/admin/reviews/tasks"
params = {
    "competitionId": 21,
    "stage": "BOOK"
}
print(f"URL: {url}")
print(f"参数: {json.dumps(params, ensure_ascii=False, indent=2)}")

response = requests.get(url, params=params, headers=headers)
print(f"状态码: {response.status_code}")
print(f"响应头: {dict(response.headers)}")
print(f"响应体: {response.text}\n")

print("=" * 60)
print("测试2: 查询所有任务（不带stage参数）")
print("=" * 60)
params2 = {
    "competitionId": 21
}
print(f"URL: {url}")
print(f"参数: {json.dumps(params2, ensure_ascii=False, indent=2)}")

response2 = requests.get(url, params=params2, headers=headers)
print(f"状态码: {response2.status_code}")
print(f"响应头: {dict(response2.headers)}")
print(f"响应体: {response2.text}\n")
