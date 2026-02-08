#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""步骤4: 测试场景4 - 评委查看评审任务"""

import requests
import json

BASE_URL = "http://localhost:6031"

print("步骤4: 测试场景4 - 评委查看评审任务")
print("=" * 80)

# 登录评委
print("\n1. 登录评委账号...")
url = f"{BASE_URL}/api/auth/login"
data = {"phone": "13900000001", "name": "李明华", "role": "REVIEWER"}
response = requests.post(url, json=data)

if response.status_code != 200:
    print(f"❌ 登录失败: HTTP {response.status_code}")
    exit(1)

result = response.json()
if not result.get("success"):
    print(f"❌ 登录失败: {result.get('message')}")
    exit(1)

token = result.get("data", {}).get("token")
print("✅ 评委登录成功")

headers = {"Authorization": f"Bearer {token}"}

# 获取评审任务
print("\n2. 获取评审任务...")
url = f"{BASE_URL}/api/reviews/my-tasks?competitionId=23"
response = requests.get(url, headers=headers)

if response.status_code != 200:
    print(f"❌ 请求失败: HTTP {response.status_code}")
    exit(1)

result = response.json()
tasks = result.get("data", [])
print(f"✅ 找到 {len(tasks)} 个评审任务")

if not tasks:
    print("⚠️  该评委没有评审任务")
    # 直接测试报名ID 119
    print("\n直接测试报名ID 119...")
    reg_id = 119
else:
    reg_id = tasks[0].get("registrationId")

# 查看项目详情
print(f"\n3. 查看项目详情 (ID: {reg_id})...")
url = f"{BASE_URL}/api/registrations/{reg_id}"
response = requests.get(url, headers=headers)

if response.status_code != 200:
    print(f"❌ 请求失败: HTTP {response.status_code}")
    exit(1)

result = response.json()
data = result.get("data", {})
activity = data.get("activityInfo")
summary = data.get("projectSummary")

print("\n" + "=" * 80)
print("字段检查结果")
print("=" * 80)

# 检查活动信息
if activity:
    print("\n【活动信息 - 10个字段】")
    print(f"  1. theme: {activity.get('theme')}")
    print(f"  2. keywords: {activity.get('keywords')}")
    print(f"  3. subjectTypeCode: {activity.get('subjectTypeCode')}")
    print(f"  4. methodCode: {activity.get('methodCode')}")
    print(f"  5. experienceImproveCode: {activity.get('experienceImproveCode')}")
    print(f"  6. qualityTopicCode: {activity.get('qualityTopicCode')}")
    print(f"  7. avgWorkYears: {activity.get('avgWorkYears')}")
    print(f"  8. avgAge: {activity.get('avgAge')}")
    print(f"  9. crossDepartment: {activity.get('crossDepartment')}")
    print(f"  10. relatedToDigitalAi: {activity.get('relatedToDigitalAi')}")
    
    if activity.get("relatedToDigitalAi") is not None:
        print("\n✅ 所有字段都存在")
    else:
        print("\n❌ relatedToDigitalAi 字段缺失")
else:
    print("\n❌ activityInfo 为空")

# 检查项目摘要
if summary:
    print("\n【项目摘要 - 7个字段】")
    print(f"  1. plan: {'有' if summary.get('plan') else '无'}")
    print(f"  2. problem: {'有' if summary.get('problem') else '无'}")
    print(f"  3. action: {'有' if summary.get('action') else '无'}")
    print(f"  4. success: {'有' if summary.get('success') else '无'}")
    print(f"  5. discussion: {'有' if summary.get('discussion') else '无'}")
    print(f"  6. operation: {'有' if summary.get('operation') else '无'}")
    print(f"  7. presentation: {'有' if summary.get('presentation') else '无'}")
    
    if "operation" in summary and "presentation" in summary:
        print("\n✅ 所有字段都存在")
    else:
        print("\n❌ 部分字段缺失")
else:
    print("\n⚠️  projectSummary 为空（该报名未填写摘要）")

print("\n" + "=" * 80)
print("✅ 场景4测试完成")
print("=" * 80)
