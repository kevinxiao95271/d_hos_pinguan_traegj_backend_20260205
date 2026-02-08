#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""步骤3: 测试场景2和3 - 组委会管理员查看项目"""

import requests
import json

BASE_URL = "http://localhost:6031"

print("步骤3: 测试组委会管理员查看项目")
print("=" * 80)

# 登录
print("\n1. 登录组委会管理员...")
url = f"{BASE_URL}/api/auth/login"
data = {"phone": "13800000041", "name": "CommitteeAdmin A", "role": "COMMITTEE_ADMIN"}
response = requests.post(url, json=data)

token = response.json().get("data", {}).get("token")
print("✅ 登录成功")

headers = {"Authorization": f"Bearer {token}"}

# 场景2: 书审分组项目列表
print("\n" + "=" * 80)
print("场景2: 书审分组项目列表")
print("=" * 80)

url = f"{BASE_URL}/api/admin/registrations/grouped?competitionId=23"
response = requests.get(url, headers=headers)

if response.status_code == 200:
    result = response.json()
    groups = result.get("data", [])
    print(f"\n找到 {len(groups)} 个分组")
    
    if groups and groups[0].get("items"):
        reg_id = groups[0]["items"][0]["id"]
        print(f"测试第一个项目 ID: {reg_id}")
        
        # 获取详情
        detail_url = f"{BASE_URL}/api/registrations/{reg_id}"
        detail_response = requests.get(detail_url, headers=headers)
        
        if detail_response.status_code == 200:
            data = detail_response.json().get("data", {})
            activity = data.get("activityInfo")
            
            if activity and activity.get("relatedToDigitalAi") is not None:
                print("✅ 场景2: 字段完整")
            else:
                print("❌ 场景2: 字段缺失")
        else:
            print(f"❌ 获取详情失败: {detail_response.status_code}")
    else:
        print("⚠️  没有分组数据")
else:
    print(f"❌ 获取分组失败: {response.status_code}")

# 场景3: 筛选项目列表
print("\n" + "=" * 80)
print("场景3: 筛选项目列表")
print("=" * 80)

url = f"{BASE_URL}/api/admin/registrations/filter?competitionId=23"
response = requests.get(url, headers=headers)

if response.status_code == 200:
    result = response.json()
    registrations = result.get("data", [])
    print(f"\n找到 {len(registrations)} 个项目")
    
    if registrations:
        reg_id = registrations[0]["id"]
        print(f"测试第一个项目 ID: {reg_id}")
        
        # 获取详情
        detail_url = f"{BASE_URL}/api/registrations/{reg_id}"
        detail_response = requests.get(detail_url, headers=headers)
        
        if detail_response.status_code == 200:
            data = detail_response.json().get("data", {})
            activity = data.get("activityInfo")
            summary = data.get("projectSummary")
            
            print("\n【字段检查】")
            if activity:
                has_ai = activity.get("relatedToDigitalAi") is not None
                print(f"  relatedToDigitalAi: {'✅ 存在' if has_ai else '❌ 缺失'}")
            
            if summary:
                has_operation = "operation" in summary
                has_presentation = "presentation" in summary
                print(f"  operation: {'✅ 存在' if has_operation else '❌ 缺失'}")
                print(f"  presentation: {'✅ 存在' if has_presentation else '❌ 缺失'}")
            else:
                print("  ⚠️  projectSummary 为空")
            
            if activity and activity.get("relatedToDigitalAi") is not None:
                print("\n✅ 场景3: 字段完整")
            else:
                print("\n❌ 场景3: 字段缺失")
        else:
            print(f"❌ 获取详情失败: {detail_response.status_code}")
    else:
        print("⚠️  没有项目数据")
else:
    print(f"❌ 获取项目失败: {response.status_code}")

print("\n" + "=" * 80)
print("✅ 组委会管理员场景测试完成")
print("=" * 80)
