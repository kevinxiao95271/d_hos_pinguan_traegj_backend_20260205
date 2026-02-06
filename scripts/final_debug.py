#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终调试 - 详细检查JWT和权限流程
"""

import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import base64
import json

BASE_URL = "http://localhost:6031"

print("="*80)
print("最终调试 - JWT和权限流程")
print("="*80)

# 1. 登录
print("\n[步骤1] 组委会登录")
login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
    "phone": "13800000009",
    "name": "Committee",
    "title": "组委会",
    "role": "COMMITTEE"
})

if login_resp.status_code != 200:
    print(f"登录失败: {login_resp.status_code}")
    exit(1)

login_data = login_resp.json()
if not login_data.get("success"):
    print(f"登录失败: {login_data}")
    exit(1)

token = login_data["data"]["token"]
user_id = login_data["data"]["id"]
role = login_data["data"]["role"]

print(f"用户ID: {user_id}")
print(f"角色: {role}")
print(f"Token: {token[:50]}...")

# 解码JWT看看内容
try:
    parts = token.split('.')
    if len(parts) == 3:
        # 添加padding
        payload = parts[1]
        payload += '=' * (4 - len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload)
        payload_data = json.loads(decoded)
        print(f"\nJWT Payload:")
        print(f"  sub (userId): {payload_data.get('sub')}")
        print(f"  role: {payload_data.get('role')}")
        print(f"  iat: {payload_data.get('iat')}")
        print(f"  exp: {payload_data.get('exp')}")
except Exception as e:
    print(f"无法解码JWT: {e}")

# 2. 测试一个正常工作的接口（作为对照）
print("\n[步骤2] 测试正常工作的接口（统计数据）")
headers = {"Authorization": f"Bearer {token}"}
stats_resp = requests.get(f"{BASE_URL}/api/admin/stats/summary", headers=headers)
print(f"统计接口状态码: {stats_resp.status_code}")
if stats_resp.status_code == 200:
    print("  [成功] 统计接口正常")
else:
    print(f"  [失败] 统计接口也有问题")

# 3. 测试评委接口
print("\n[步骤3] 测试评委接口")
reviewer_resp = requests.get(f"{BASE_URL}/api/admin/reviewers", headers=headers)
print(f"评委接口状态码: {reviewer_resp.status_code}")
print(f"响应头: {dict(reviewer_resp.headers)}")
print(f"响应体: {reviewer_resp.text[:200]}")

if reviewer_resp.status_code == 401:
    print("\n[分析] 401错误 - JWT验证失败")
    print("可能原因:")
    print("  1. JwtAuthorizationFilter未正确将role存入request attributes")
    print("  2. Controller无法读取request attributes")
    print("  3. token在传递过程中被修改或丢失")

# 4. 测试OPS角色
print("\n[步骤4] 测试OPS角色（对照组）")
ops_login = requests.post(f"{BASE_URL}/api/auth/login", json={
    "phone": "13800000051",
    "name": "OPS",
    "title": "运维",
    "role": "OPS"
})

if ops_login.status_code == 200:
    ops_data = ops_login.json()
    if ops_data.get("success"):
        ops_token = ops_data["data"]["token"]
        print(f"OPS登录成功，Token: {ops_token[:50]}...")
        
        ops_headers = {"Authorization": f"Bearer {ops_token}"}
        ops_reviewer_resp = requests.get(f"{BASE_URL}/api/admin/reviewers", headers=ops_headers)
        print(f"OPS访问评委接口状态码: {ops_reviewer_resp.status_code}")
        
        if ops_reviewer_resp.status_code == 200:
            ops_reviewers = ops_reviewer_resp.json()
            if ops_reviewers.get("success"):
                count = len(ops_reviewers.get("data", []))
                print(f"  [成功] OPS可以访问，返回 {count} 个评委")
                print("\n结论: 接口本身正常，问题在于COMMITTEE角色权限")
            else:
                print(f"  [失败] {ops_reviewers.get('message')}")
        else:
            print(f"  [失败] OPS也无法访问，问题可能在Filter层")

print("\n" + "="*80)
