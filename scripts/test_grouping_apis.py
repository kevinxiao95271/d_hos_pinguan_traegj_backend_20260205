# -*- coding: utf-8 -*-
"""
对比书审筛选和面谈分组API的返回字段
"""
import requests
import json

BASE_URL = "http://localhost:6031/api"

print("=" * 100)
print("对比API返回字段")
print("=" * 100)

# 1. 登录获取token（使用组委会账号）
print("\n[步骤1] 登录组委会账号...")

login_response = requests.post(
    f"{BASE_URL}/auth/login-with-password",
    json={
        "phone": "13800000127",
        "password": "committee2026"
    },
    timeout=30
)

if login_response.status_code != 200 or not login_response.json().get('success'):
    print(f"登录失败")
    exit(1)

token = login_response.json()['data']['token']
print(f"登录成功！")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 2. 测试书审筛选API（/filter）
print("\n" + "=" * 100)
print("[API 1] GET /api/admin/registrations/filter (书审筛选)")
print("=" * 100)

filter_response = requests.get(
    f"{BASE_URL}/admin/registrations/filter",
    headers=headers,
    params={"competitionId": 1},
    timeout=30
)

if filter_response.status_code == 200:
    filter_data = filter_response.json()
    
    if filter_data.get('success') and len(filter_data.get('data', [])) > 0:
        first_item = filter_data['data'][0]
        
        print(f"\n数据结构:")
        print(f"  总记录数: {len(filter_data['data'])}")
        print(f"\n第一条记录的字段:")
        for key in sorted(first_item.keys()):
            value = first_item[key]
            if isinstance(value, str) and len(value) > 40:
                value = value[:40] + "..."
            print(f"    {key:<25} = {value}")
        
        # 重点检查id字段
        print(f"\n[关键字段检查]")
        print(f"  registrationId: {first_item.get('registrationId', '[缺失]')}")
        print(f"  id: {first_item.get('id', '[缺失]')}")
        
        if 'registrationId' in first_item:
            print(f"  [OK] 有registrationId字段")
        else:
            print(f"  [FAIL] 缺少registrationId字段！")
else:
    print(f"请求失败: {filter_response.status_code}")

# 3. 测试面谈分组API（/interview-groups）
print("\n" + "=" * 100)
print("[API 2] GET /api/admin/registrations/interview-groups (面谈分组)")
print("=" * 100)

interview_response = requests.get(
    f"{BASE_URL}/admin/registrations/interview-groups",
    headers=headers,
    params={"competitionId": 1},
    timeout=30
)

if interview_response.status_code == 200:
    interview_data = interview_response.json()
    
    if interview_data.get('success') and len(interview_data.get('data', [])) > 0:
        first_group = interview_data['data'][0]
        
        print(f"\n数据结构:")
        print(f"  总分组数: {len(interview_data['data'])}")
        print(f"  第一个分组: {first_group.get('groupCode')}")
        
        if 'items' in first_group and len(first_group['items']) > 0:
            first_item = first_group['items'][0]
            
            print(f"\n第一个分组的第一条记录字段:")
            for key in sorted(first_item.keys()):
                value = first_item[key]
                if isinstance(value, str) and len(value) > 40:
                    value = value[:40] + "..."
                print(f"    {key:<25} = {value}")
            
            # 重点检查id字段
            print(f"\n[关键字段检查]")
            print(f"  registrationId: {first_item.get('registrationId', '[缺失]')}")
            print(f"  id: {first_item.get('id', '[缺失]')}")
            
            if 'registrationId' in first_item:
                print(f"  [OK] 有registrationId字段")
            else:
                print(f"  [FAIL] 缺少registrationId字段！")
        else:
            print(f"  [WARN] 分组中没有items数据")
    else:
        print(f"  [WARN] 没有返回分组数据")
else:
    print(f"请求失败: {interview_response.status_code}")

# 4. 对比总结
print("\n" + "=" * 100)
print("字段对比总结")
print("=" * 100)

print(f"\n[对比] registrationId字段:")
print(f"  /filter API: {'有' if filter_response.status_code == 200 else '未知'}")
print(f"  /interview-groups API: {'有' if interview_response.status_code == 200 else '未知'}")

print("\n" + "=" * 100)
