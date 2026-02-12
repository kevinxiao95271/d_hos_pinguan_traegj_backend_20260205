#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试Swagger登录"""

import requests
import json

BASE_URL = "http://localhost:6031"

print("=" * 60)
print("测试登录接口")
print("=" * 60)

# 测试管理员登录
print("\n1. 测试管理员登录")
print("-" * 60)
response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "phone": "13800000041",
    "name": "CommitteeAdmin A",
    "role": "COMMITTEE_ADMIN"
})

print(f"状态码: {response.status_code}")
print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

if response.status_code == 200 and response.json().get('success'):
    token = response.json()['data']['token']
    print(f"\n✓ 登录成功")
    print(f"Token (前50字符): {token[:50]}...")
    
    # 测试使用token调用接口
    print("\n2. 测试使用Token调用接口")
    print("-" * 60)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    test_response = requests.get(
        f"{BASE_URL}/api/admin/reviews/tasks",
        params={"competitionId": 21, "stage": "BOOK"},
        headers=headers
    )
    
    print(f"状态码: {test_response.status_code}")
    if test_response.status_code == 200:
        data = test_response.json()
        if data.get('success'):
            tasks = data.get('data', [])
            print(f"✓ 接口调用成功，返回 {len(tasks)} 条任务")
        else:
            print(f"✗ 接口返回失败: {data.get('message')}")
    else:
        print(f"✗ 接口调用失败: {test_response.text}")
else:
    print(f"✗ 登录失败")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
