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
response = requests.post("http://localhost:6031/api/auth/login", json=login_data)
token = response.json()['data']['token']
print(f"Token获取成功\n")

# 2. 查询历史数据
print("查询历史数据...")
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://localhost:6031/api/historical-data?page=0&size=10", headers=headers)

print(f"状态码: {response.status_code}")
print(f"\n完整响应:")
result = response.json()
print(json.dumps(result, indent=2, ensure_ascii=False))

if result.get('success'):
    data = result['data']
    print(f"\n数据分析:")
    print(f"  totalElements: {data.get('totalElements')}")
    print(f"  totalPages: {data.get('totalPages')}")
    print(f"  number (当前页): {data.get('number')}")
    print(f"  size (每页大小): {data.get('size')}")
    print(f"  numberOfElements (当前页实际数量): {data.get('numberOfElements')}")
    print(f"  content 长度: {len(data.get('content', []))}")
    print(f"  empty: {data.get('empty')}")
    
    if data.get('content'):
        print(f"\n第一条数据:")
        print(json.dumps(data['content'][0], indent=2, ensure_ascii=False))
