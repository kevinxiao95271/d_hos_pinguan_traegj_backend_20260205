#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试历史数据API"""

import requests
import json

BASE_URL = "http://localhost:6031/api"

def login(phone, name, role):
    """登录获取token"""
    url = f"{BASE_URL}/auth/login"
    data = {
        "phone": phone,
        "name": name,
        "role": role
    }
    response = requests.post(url, json=data)
    result = response.json()
    
    if result.get('success'):
        print(f"✓ 登录成功: {result['data']['name']} ({result['data']['role']})")
        return result['data']['token']
    else:
        print(f"✗ 登录失败: {result.get('message')}")
        return None

def test_query_historical_data(token, **params):
    """测试查询历史数据"""
    url = f"{BASE_URL}/historical-data"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers, params=params)
    result = response.json()
    
    return result

def main():
    print("=== 历史数据API测试 ===\n")
    
    # 1. 使用组委会管理员账号登录
    print("1. 测试组委会管理员登录...")
    token = login("13800000041", "CommitteeAdmin A", "COMMITTEE_ADMIN")
    
    if not token:
        print("登录失败，无法继续测试")
        return
    
    print()
    
    # 2. 测试基本查询（不带筛选条件）
    print("2. 测试基本查询（第1页，每页10条）...")
    result = test_query_historical_data(token, page=0, size=10)
    
    if result.get('success'):
        data = result['data']
        print(f"✓ 查询成功")
        print(f"  总记录数: {data['totalElements']}")
        print(f"  总页数: {data['totalPages']}")
        print(f"  当前页: {data['number']}")
        print(f"  每页大小: {data['size']}")
        print(f"  当前页记录数: {len(data['content'])}")
        
        if data['content']:
            print(f"\n  第一条记录:")
            first = data['content'][0]
            print(f"    ID: {first['id']}")
            print(f"    项目名称: {first['projectName']}")
            print(f"    医院: {first['institutionName']}")
            print(f"    组别: {first['competitionGroup']}")
            print(f"    状态: {first['dataStatus']}")
    else:
        print(f"✗ 查询失败: {result.get('message')}")
    
    print()
    
    # 3. 测试按地区筛选
    print("3. 测试按地区筛选（杭州）...")
    result = test_query_historical_data(token, region="杭州", page=0, size=5)
    
    if result.get('success'):
        data = result['data']
        print(f"✓ 查询成功，找到 {data['totalElements']} 条记录")
        for item in data['content'][:3]:
            print(f"  - {item['institutionName']} ({item['institutionAddress']})")
    else:
        print(f"✗ 查询失败: {result.get('message')}")
    
    print()
    
    # 4. 测试按组别筛选
    print("4. 测试按组别筛选（综合组）...")
    result = test_query_historical_data(token, competitionGroup="综合组", page=0, size=5)
    
    if result.get('success'):
        data = result['data']
        print(f"✓ 查询成功，找到 {data['totalElements']} 条记录")
        for item in data['content'][:3]:
            print(f"  - {item['projectName']} ({item['competitionGroup']})")
    else:
        print(f"✗ 查询失败: {result.get('message')}")
    
    print()
    
    # 5. 测试按医院筛选
    print("5. 测试按医院筛选（人民医院）...")
    result = test_query_historical_data(token, institutionName="人民医院", page=0, size=5)
    
    if result.get('success'):
        data = result['data']
        print(f"✓ 查询成功，找到 {data['totalElements']} 条记录")
        for item in data['content'][:3]:
            print(f"  - {item['institutionName']}")
    else:
        print(f"✗ 查询失败: {result.get('message')}")
    
    print()
    
    # 6. 测试组合筛选
    print("6. 测试组合筛选（综合组 + 杭州）...")
    result = test_query_historical_data(
        token, 
        competitionGroup="综合组",
        region="杭州",
        page=0, 
        size=5
    )
    
    if result.get('success'):
        data = result['data']
        print(f"✓ 查询成功，找到 {data['totalElements']} 条记录")
        for item in data['content'][:3]:
            print(f"  - {item['institutionName']} - {item['projectName']}")
    else:
        print(f"✗ 查询失败: {result.get('message')}")
    
    print()
    
    # 7. 测试排序
    print("7. 测试排序（按项目编号升序）...")
    result = test_query_historical_data(
        token, 
        page=0, 
        size=5,
        sortBy="projectCode",
        sortDirection="ASC"
    )
    
    if result.get('success'):
        data = result['data']
        print(f"✓ 查询成功")
        for item in data['content']:
            print(f"  - {item['projectCode']}: {item['projectName']}")
    else:
        print(f"✗ 查询失败: {result.get('message')}")
    
    print()
    
    # 8. 测试权限（使用评委账号）
    print("8. 测试权限控制（使用评委账号）...")
    reviewer_token = login("13800000021", "李明华", "REVIEWER")
    
    if reviewer_token:
        result = test_query_historical_data(reviewer_token, page=0, size=5)
        
        if not result.get('success'):
            print(f"✓ 权限控制正常: {result.get('message')}")
        else:
            print(f"✗ 权限控制失败: 评委不应该能访问历史数据")
    
    print()
    print("=== 测试完成 ===")

if __name__ == '__main__':
    main()
