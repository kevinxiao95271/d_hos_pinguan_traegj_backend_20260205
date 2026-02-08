#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""步骤2: 测试场景1 - 参赛者查看我的报名"""

import requests
import json

BASE_URL = "http://localhost:6031"

print("步骤2: 测试场景1 - 参赛者查看我的报名")
print("=" * 80)

# 登录参赛者账号
print("\n1. 登录参赛者账号...")
url = f"{BASE_URL}/api/auth/login"
data = {"phone": "13800000001", "name": "张三", "role": "CONTESTANT"}
response = requests.post(url, json=data)

if response.status_code != 200:
    print(f"❌ 登录失败: HTTP {response.status_code}")
    exit(1)

result = response.json()
if not result.get("success"):
    print(f"❌ 登录失败: {result.get('message')}")
    exit(1)

token = result.get("data", {}).get("token")
print("✅ 参赛者登录成功")

# 获取我的报名列表
print("\n2. 获取我的报名列表...")
headers = {"Authorization": f"Bearer {token}"}
url = f"{BASE_URL}/api/registrations/my"
response = requests.get(url, headers=headers)

if response.status_code != 200:
    print(f"❌ 请求失败: HTTP {response.status_code}")
    exit(1)

result = response.json()
registrations = result.get("data", [])
print(f"✅ 找到 {len(registrations)} 个报名")

if not registrations:
    print("⚠️  该参赛者没有报名数据")
    exit(0)

# 查看第一个报名的详情
reg_id = registrations[0].get("id")
print(f"\n3. 查看报名详情 (ID: {reg_id})...")
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
    fields = [
        ("theme", "活动主题"),
        ("keywords", "关键词"),
        ("subjectTypeCode", "主题类型"),
        ("methodCode", "运用手法"),
        ("experienceImproveCode", "改善就医环境"),
        ("qualityTopicCode", "医疗质量主题"),
        ("avgWorkYears", "平均工作年限"),
        ("avgAge", "平均年龄"),
        ("crossDepartment", "是否跨部门"),
        ("relatedToDigitalAi", "是否与数字化/AI相关")
    ]
    
    all_ok = True
    for field, label in fields:
        value = activity.get(field)
        if value is not None:
            print(f"  ✅ {label} ({field}): {value}")
        else:
            print(f"  ❌ {label} ({field}): None")
            all_ok = False
    
    if all_ok:
        print("\n✅ 所有活动信息字段都存在")
    else:
        print("\n❌ 部分字段缺失")
else:
    print("\n❌ activityInfo 为空")

# 检查项目摘要
if summary:
    print("\n【项目摘要 - 7个字段】")
    fields = [
        ("plan", "计划"),
        ("problem", "问题"),
        ("action", "行动"),
        ("success", "成效"),
        ("discussion", "讨论"),
        ("operation", "运作"),
        ("presentation", "展示")
    ]
    
    for field, label in fields:
        value = summary.get(field)
        if value:
            print(f"  ✅ {label} ({field}): 有内容")
        else:
            print(f"  ⚠️  {label} ({field}): 无内容（可能未填写）")
else:
    print("\n⚠️  projectSummary 为空（该报名未填写摘要）")

print("\n" + "=" * 80)
print("✅ 场景1测试完成")
print("=" * 80)
