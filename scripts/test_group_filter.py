#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json

# 登录
login_data = {
    "phone": "13800000041",
    "name": "CommitteeAdmin A",
    "role": "COMMITTEE_ADMIN"
}
response = requests.post("http://localhost:6031/api/auth/login", json=login_data)
token = response.json()['data']['token']

headers = {"Authorization": f"Bearer {token}"}

print("=== 测试组别筛选 ===\n")

# 1. 测试综合组
print("1. 查询'综合组'...")
response = requests.get(
    "http://localhost:6031/api/historical-data?competitionGroup=综合组&page=0&size=5",
    headers=headers
)
result = response.json()
if result['success']:
    data = result['data']
    print(f"   总记录数: {data['totalElements']}")
    print(f"   前3条数据的组别:")
    for item in data['content'][:3]:
        print(f"     - {item['competitionGroup']}")
else:
    print(f"   错误: {result.get('message')}")

print()

# 2. 测试基层组（完整名称）
print("2. 查询'基层组(基层组积分方式同综合组)'...")
response = requests.get(
    "http://localhost:6031/api/historical-data?competitionGroup=基层组(基层组积分方式同综合组)&page=0&size=5",
    headers=headers
)
result = response.json()
if result['success']:
    data = result['data']
    print(f"   总记录数: {data['totalElements']}")
    print(f"   前3条数据的组别:")
    for item in data['content'][:3]:
        print(f"     - {item['competitionGroup']}")
else:
    print(f"   错误: {result.get('message')}")

print()

# 3. 测试进阶组
print("3. 查询'进阶组'...")
response = requests.get(
    "http://localhost:6031/api/historical-data?competitionGroup=进阶组&page=0&size=5",
    headers=headers
)
result = response.json()
if result['success']:
    data = result['data']
    print(f"   总记录数: {data['totalElements']}")
    print(f"   前3条数据的组别:")
    for item in data['content'][:3]:
        print(f"     - {item['competitionGroup']}")
else:
    print(f"   错误: {result.get('message')}")

print()

# 4. 测试不带筛选
print("4. 查询全部（不带组别筛选）...")
response = requests.get(
    "http://localhost:6031/api/historical-data?page=0&size=5",
    headers=headers
)
result = response.json()
if result['success']:
    data = result['data']
    print(f"   总记录数: {data['totalElements']}")
    print(f"   前5条数据的组别:")
    for item in data['content']:
        print(f"     - {item['competitionGroup']}")
else:
    print(f"   错误: {result.get('message')}")
