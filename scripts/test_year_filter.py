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
print("Token获取成功\n")

# 2. 测试按年份查询
headers = {"Authorization": f"Bearer {token}"}

print("=== 测试年份筛选 ===\n")

# 查询2024年数据
print("1. 查询2024年数据...")
response = requests.get(
    "http://localhost:6031/api/historical-data?year=2024&page=0&size=5",
    headers=headers
)
result = response.json()
if result['success']:
    data = result['data']
    print(f"   找到 {data['totalElements']} 条记录")
    for item in data['content'][:3]:
        print(f"   - {item['year']}: {item['projectName']}")

print()

# 查询2025年数据
print("2. 查询2025年数据...")
response = requests.get(
    "http://localhost:6031/api/historical-data?year=2025&page=0&size=5",
    headers=headers
)
result = response.json()
if result['success']:
    data = result['data']
    print(f"   找到 {data['totalElements']} 条记录")
    for item in data['content'][:3]:
        print(f"   - {item['year']}: {item['projectName']}")

print()

# 组合查询：2024年 + 杭州 + 综合组
print("3. 组合查询（2024年 + 杭州 + 综合组）...")
response = requests.get(
    "http://localhost:6031/api/historical-data?year=2024&region=杭州&competitionGroup=综合组&page=0&size=5",
    headers=headers
)
result = response.json()
if result['success']:
    data = result['data']
    print(f"   找到 {data['totalElements']} 条记录")
    for item in data['content'][:3]:
        print(f"   - {item['year']} | {item['institutionName']} | {item['projectName']}")

print("\n=== 测试完成 ===")
