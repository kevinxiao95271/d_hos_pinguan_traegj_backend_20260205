#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""步骤1: 简单检查字段"""

import requests
import json

BASE_URL = "http://localhost:6031"

print("步骤1: 检查数据库字段")
print("=" * 60)

# 登录
print("\n1. 登录...")
url = f"{BASE_URL}/api/auth/login"
data = {"phone": "13800000041", "name": "CommitteeAdmin A", "role": "COMMITTEE_ADMIN"}
response = requests.post(url, json=data)

if response.status_code != 200:
    print(f"❌ 登录失败: HTTP {response.status_code}")
    exit(1)

result = response.json()
if not result.get("success"):
    print(f"❌ 登录失败: {result.get('message')}")
    exit(1)

token = result.get("data", {}).get("token")
print("✅ 登录成功")

# 获取报名详情
print("\n2. 获取报名详情...")
headers = {"Authorization": f"Bearer {token}"}
url = f"{BASE_URL}/api/registrations/119"
response = requests.get(url, headers=headers)

if response.status_code != 200:
    print(f"❌ 请求失败: HTTP {response.status_code}")
    exit(1)

result = response.json()
data = result.get("data", {})
activity = data.get("activityInfo")

# 检查字段
print("\n3. 检查字段...")
print("-" * 60)

if not activity:
    print("❌ activityInfo 为空")
    exit(1)

print(f"crossDepartment: {activity.get('crossDepartment')}")
print(f"relatedToDigitalAi: {activity.get('relatedToDigitalAi')}")

if activity.get('relatedToDigitalAi') is None:
    print("\n❌ relatedToDigitalAi 字段为 None")
    print("\n需要执行:")
    print("1. add_digital_ai_field.sql")
    print("2. 重启应用")
else:
    print("\n✅ relatedToDigitalAi 字段存在")

print("\n完整的 activityInfo:")
print(json.dumps(activity, ensure_ascii=False, indent=2))
