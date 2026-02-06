#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试评审专家API
"""

import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests

BASE_URL = "http://localhost:6031"

print("="*80)
print("调试评审专家API")
print("="*80)

# 1. 登录
print("\n[步骤1] 登录获取token")
login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
    "phone": "13800000009",
    "name": "Committee",
    "title": "组委会",
    "role": "COMMITTEE"
}, timeout=10)

print(f"登录状态码: {login_resp.status_code}")
login_data = login_resp.json()
print(f"登录结果: {login_data.get('success')}")

if not login_data.get("success"):
    print("登录失败，无法继续")
    exit(1)

token = login_data["data"]["token"]
print(f"Token (前50字符): {token[:50]}...")

# 2. 测试评审专家API
print("\n[步骤2] 调用评审专家API")
print(f"URL: {BASE_URL}/api/admin/reviewers")
print(f"Header: Authorization: Bearer {token[:30]}...")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

resp = requests.get(f"{BASE_URL}/api/admin/reviewers", headers=headers, timeout=10)

print(f"\n响应状态码: {resp.status_code}")
print(f"响应头: {dict(resp.headers)}")
print(f"响应体: {resp.text[:500]}")

if resp.status_code == 200:
    data = resp.json()
    if data.get("success"):
        reviewers = data.get("data", [])
        print(f"\n[成功] 返回 {len(reviewers)} 个评审专家")
        if reviewers:
            print(f"第一个评审专家: {reviewers[0]}")
    else:
        print(f"\n[失败] {data.get('message')}")
elif resp.status_code == 401:
    print("\n[401] 未授权 - JWT验证失败或token无效")
elif resp.status_code == 403:
    print("\n[403] 禁止访问 - 权限不足")
else:
    print(f"\n[错误] HTTP {resp.status_code}")

print("\n" + "="*80)
