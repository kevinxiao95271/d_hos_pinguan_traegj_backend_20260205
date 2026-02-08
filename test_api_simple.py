#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json

# 1. 登录
print("登录...")
login_data = {
    "phone": "13800000041",
    "name": "CommitteeAdmin A",
    "role": "COMMITTEE_ADMIN"
}
response = requests.post("http://localhost:6031/api/auth/login", json=login_data, timeout=10)
print(f"登录响应: {response.status_code}")
result = response.json()
print(json.dumps(result, indent=2, ensure_ascii=False))

if result.get('success'):
    token = result['data']['token']
    print(f"\nToken: {token[:50]}...")
    
    # 2. 查询历史数据
    print("\n查询历史数据...")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(
            "http://localhost:6031/api/historical-data?page=0&size=5",
            headers=headers,
            timeout=30
        )
        print(f"查询响应: {response.status_code}")
        print(f"响应内容: {response.text[:500]}")
    except Exception as e:
        print(f"查询出错: {e}")
