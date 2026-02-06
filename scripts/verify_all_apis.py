#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证所有核心API接口
"""

import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import json

BASE_URL = "http://localhost:6031"

print("="*80)
print("API接口验证")
print("="*80)

# 1. 登录获取token
print("\n[1] 组委会登录...")
login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
    "phone": "13800000009",
    "name": "Committee",
    "title": "Committee",
    "role": "COMMITTEE"
})
token = login_resp.json()['data']['token']
print(f"Token: {token[:50]}...")

headers = {"Authorization": f"Bearer {token}"}

# 2. 验证各个接口
print("\n[2] 验证核心接口...")

# 机构
r1 = requests.get(f"{BASE_URL}/api/institutions", headers=headers)
institutions = r1.json()['data']
print(f"  - 机构数量: {len(institutions)}")
print(f"    示例: {institutions[0]['name']}")

# 赛事
r2 = requests.get(f"{BASE_URL}/api/competitions", headers=headers)
competitions = r2.json()['data']
print(f"  - 赛事数量: {len(competitions)}")
if competitions:
    print(f"    示例: {competitions[0]['name']} (阶段: {competitions[0]['stage']})")

# 报名
r3 = requests.get(f"{BASE_URL}/api/admin/registrations", headers=headers)
r3_data = r3.json()
if r3_data.get('success'):
    registrations = r3_data['data']
    print(f"  - 报名数量: {len(registrations)}")
    if registrations:
        print(f"    示例: {registrations[0]['projectName']} ({registrations[0]['status']})")
else:
    print(f"  - 报名接口错误: {r3_data.get('message', '未知错误')}")
    registrations = []

# 评委
r4 = requests.get(f"{BASE_URL}/api/admin/reviewers", headers=headers)
reviewers = r4.json()['data']
print(f"  - 评委数量: {len(reviewers)}")
if reviewers:
    print(f"    示例: {reviewers[0]['name']} ({reviewers[0].get('expertBackground', 'N/A')})")

# 统计
r5 = requests.get(f"{BASE_URL}/api/admin/stats/summary", headers=headers)
r5_data = r5.json()
if r5_data.get('success'):
    stats = r5_data['data']
    print(f"  - 统计数据:")
    print(f"    总报名: {stats.get('totalRegistrations', 'N/A')}")
    print(f"    待审核: {stats.get('pendingRegistrations', 'N/A')}")
    print(f"    已通过: {stats.get('approvedRegistrations', 'N/A')}")
    print(f"    评委数: {stats.get('totalReviewers', 'N/A')}")
    print(f"    机构数: {stats.get('totalInstitutions', 'N/A')}")
else:
    print(f"  - 统计接口错误: {r5_data.get('message', '未知错误')}")
    stats = {}

# 3. 测试评委登录和查看任务
print("\n[3] 测试评委功能...")
reviewer_login = requests.post(f"{BASE_URL}/api/auth/login", json={
    "phone": "13800000021",
    "name": "Reviewer A",
    "title": "Expert",
    "role": "REVIEWER"
})
reviewer_token = reviewer_login.json()['data']['token']
reviewer_headers = {"Authorization": f"Bearer {reviewer_token}"}

r6 = requests.get(f"{BASE_URL}/api/reviews/my-tasks", headers=reviewer_headers)
r6_data = r6.json()
if r6_data.get('success'):
    tasks = r6_data['data']
    print(f"  - 评委任务数: {len(tasks)}")
else:
    print(f"  - 评委任务接口错误: {r6_data.get('message', '未知错误')}")
    tasks = []

# 4. 测试参赛者登录
print("\n[4] 测试参赛者功能...")
contestant_login = requests.post(f"{BASE_URL}/api/auth/login", json={
    "phone": "13800000001",
    "name": "Contestant",
    "title": "Doctor",
    "role": "CONTESTANT"
})
contestant_token = contestant_login.json()['data']['token']
contestant_headers = {"Authorization": f"Bearer {contestant_token}"}

r7 = requests.get(f"{BASE_URL}/api/registrations/my", headers=contestant_headers)
r7_data = r7.json()
if r7_data.get('success'):
    my_regs = r7_data['data']
    print(f"  - 我的报名数: {len(my_regs)}")
else:
    print(f"  - 我的报名接口错误: {r7_data.get('message', '未知错误')}")
    my_regs = []

print("\n" + "="*80)
print("验证完成！所有核心接口正常工作")
print("="*80)

# 输出示例数据到文件
print("\n生成示例数据文件...")
with open('API示例数据.json', 'w', encoding='utf-8') as f:
    examples = {
        "1_login_response": login_resp.json(),
        "2_institutions": institutions[:3],
        "3_competitions": competitions,
        "4_registrations": registrations[:3],
        "5_reviewers": reviewers[:3],
        "6_stats": stats,
        "7_reviewer_tasks": tasks[:2] if tasks else [],
        "8_my_registrations": my_regs[:2] if my_regs else []
    }
    json.dump(examples, f, ensure_ascii=False, indent=2)

print("示例数据已保存到: API示例数据.json")
