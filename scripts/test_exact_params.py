#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""精确测试参数和响应"""
import requests
import json

# 登录
print("=== 1. 登录 ===\n")
login_url = "http://localhost:6031/api/auth/login"
login_data = {
    "phone": "13800000041",
    "name": "CommitteeAdmin A",
    "role": "COMMITTEE_ADMIN"
}
print(f"请求URL: {login_url}")
print(f"请求Body: {json.dumps(login_data, ensure_ascii=False)}\n")

response = requests.post(login_url, json=login_data)
result = response.json()
token = result['data']['token']
print(f"✓ 登录成功，Token: {token[:50]}...\n")

headers = {"Authorization": f"Bearer {token}"}

# 测试1: 查询综合组
print("=== 2. 测试查询综合组 ===\n")
url1 = "http://localhost:6031/api/historical-data?competitionGroup=综合组&page=0&size=5"
print(f"请求URL: {url1}")
print(f"请求Headers: Authorization: Bearer {token[:30]}...")
print()

response1 = requests.get(url1, headers=headers)
result1 = response1.json()

print(f"响应状态码: {response1.status_code}")
print(f"响应Body (部分):")
print(f"  success: {result1['success']}")
print(f"  data.totalElements: {result1['data']['totalElements']}")
print(f"  data.totalPages: {result1['data']['totalPages']}")
print(f"  data.numberOfElements: {result1['data']['numberOfElements']}")
print(f"  data.content 长度: {len(result1['data']['content'])}")
print()
print("前5条数据的组别:")
for i, item in enumerate(result1['data']['content'], 1):
    print(f"  {i}. {item['competitionGroup']}")
print()

# 测试2: 查询基层组
print("=== 3. 测试查询基层组 ===\n")
url2 = "http://localhost:6031/api/historical-data?competitionGroup=基层组&page=0&size=5"
print(f"请求URL: {url2}")
print()

response2 = requests.get(url2, headers=headers)
result2 = response2.json()

print(f"响应状态码: {response2.status_code}")
print(f"  data.totalElements: {result2['data']['totalElements']}")
print(f"  data.content 长度: {len(result2['data']['content'])}")
print()
print("前5条数据的组别:")
for i, item in enumerate(result2['data']['content'], 1):
    print(f"  {i}. {item['competitionGroup']}")
print()

# 测试3: 查询进阶组
print("=== 4. 测试查询进阶组 ===\n")
url3 = "http://localhost:6031/api/historical-data?competitionGroup=进阶组&page=0&size=5"
print(f"请求URL: {url3}")
print()

response3 = requests.get(url3, headers=headers)
result3 = response3.json()

print(f"响应状态码: {response3.status_code}")
print(f"  data.totalElements: {result3['data']['totalElements']}")
print(f"  data.content 长度: {len(result3['data']['content'])}")
print()
print("前5条数据的组别:")
for i, item in enumerate(result3['data']['content'], 1):
    print(f"  {i}. {item['competitionGroup']}")
print()

# 测试4: 不带组别参数
print("=== 5. 测试不带组别参数（全部数据）===\n")
url4 = "http://localhost:6031/api/historical-data?page=0&size=5"
print(f"请求URL: {url4}")
print()

response4 = requests.get(url4, headers=headers)
result4 = response4.json()

print(f"响应状态码: {response4.status_code}")
print(f"  data.totalElements: {result4['data']['totalElements']}")
print(f"  data.content 长度: {len(result4['data']['content'])}")
print()
print("前5条数据的组别:")
for i, item in enumerate(result4['data']['content'], 1):
    print(f"  {i}. {item['competitionGroup']}")
print()

# 汇总
print("=== 6. 测试结果汇总 ===\n")
print(f"综合组: {result1['data']['totalElements']} 条")
print(f"基层组: {result2['data']['totalElements']} 条")
print(f"进阶组: {result3['data']['totalElements']} 条")
print(f"全部: {result4['data']['totalElements']} 条")
print()
print(f"总和: {result1['data']['totalElements'] + result2['data']['totalElements'] + result3['data']['totalElements']}")
