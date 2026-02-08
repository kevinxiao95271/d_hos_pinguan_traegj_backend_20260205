#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests

# 登录
login_data = {
    "phone": "13800000041",
    "name": "CommitteeAdmin A",
    "role": "COMMITTEE_ADMIN"
}
response = requests.post("http://localhost:6031/api/auth/login", json=login_data)
token = response.json()['data']['token']

headers = {"Authorization": f"Bearer {token}"}

print("=== 测试修改后的组别筛选 ===\n")

test_groups = [
    ("综合组", 1249),
    ("基层组", 417),
    ("进阶组", 152)
]

for group_name, expected_count in test_groups:
    response = requests.get(
        f"http://localhost:6031/api/historical-data?competitionGroup={group_name}&page=0&size=3",
        headers=headers
    )
    result = response.json()
    
    if result['success']:
        data = result['data']
        actual_count = data['totalElements']
        status = "✅" if actual_count == expected_count else "❌"
        
        print(f"{status} {group_name}")
        print(f"   期望: {expected_count} 条")
        print(f"   实际: {actual_count} 条")
        
        if data['content']:
            print(f"   前3条的组别:")
            for item in data['content']:
                print(f"     - {item['competitionGroup']}")
        print()

print("=== 组合查询测试 ===\n")

# 2024年 + 综合组
response = requests.get(
    "http://localhost:6031/api/historical-data?year=2024&competitionGroup=综合组&page=0&size=3",
    headers=headers
)
result = response.json()
if result['success']:
    data = result['data']
    print(f"✓ 2024年 + 综合组: {data['totalElements']} 条")
    for item in data['content']:
        print(f"  - {item['year']} | {item['competitionGroup']} | {item['projectName'][:30]}...")

print()

# 2024年 + 基层组
response = requests.get(
    "http://localhost:6031/api/historical-data?year=2024&competitionGroup=基层组&page=0&size=3",
    headers=headers
)
result = response.json()
if result['success']:
    data = result['data']
    print(f"✓ 2024年 + 基层组: {data['totalElements']} 条")
    for item in data['content']:
        print(f"  - {item['year']} | {item['competitionGroup']} | {item['projectName'][:30]}...")
