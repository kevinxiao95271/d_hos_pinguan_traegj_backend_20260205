#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""完整测试评分流程"""

import requests
import json

BASE_URL = "http://localhost:6031"

print("=" * 80)
print("完整测试评分流程")
print("=" * 80)

# 1. 管理员登录
print("\n1. 管理员登录...")
admin_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
    "phone": "13800000041",
    "name": "CommitteeAdmin A",
    "role": "COMMITTEE_ADMIN"
}, timeout=5)

admin_token = admin_resp.json()['data']['token']
admin_headers = {"Authorization": f"Bearer {admin_token}"}
print("✓ 管理员登录成功")

# 2. 查询有任务的评审专家
print("\n2. 查询评审任务...")
tasks_resp = requests.get(
    f"{BASE_URL}/api/admin/reviews/tasks",
    params={"competitionId": 21, "stage": "BOOK"},
    headers=admin_headers,
    timeout=5
)

tasks = tasks_resp.json()['data']
print(f"✓ 找到 {len(tasks)} 个书审任务")

if not tasks:
    print("没有任务可测试")
    exit(0)

# 找一个待评分或已评分的任务
task = tasks[0]
reviewer_id = task['reviewerId']
reviewer_name = task['reviewerName']
reviewer_phone = None

print(f"\n选择任务:")
print(f"  任务ID: {task['id']}")
print(f"  项目: {task['projectName']}")
print(f"  评委: {reviewer_name} (ID:{reviewer_id})")

# 3. 查询评审专家详情获取phone
print("\n3. 查询评审专家列表找phone...")
reviewers_resp = requests.get(
    f"{BASE_URL}/api/admin/reviews/reviewers",
    headers=admin_headers,
    timeout=5
)

reviewers = reviewers_resp.json()['data']
for r in reviewers:
    if r['id'] == reviewer_id:
        reviewer_phone = r['phone']
        reviewer_title = r.get('title')
        reviewer_inst_id = r.get('institutionId')
        reviewer_bg = r.get('expertBackground')
        break

if not reviewer_phone:
    print(f"✗ 找不到评审专家phone")
    exit(1)

print(f"✓ 找到评审专家: {reviewer_name} ({reviewer_phone})")

# 4. 评审专家登录
print("\n4. 评审专家登录...")
reviewer_login = {
    "phone": reviewer_phone,
    "name": reviewer_name,
    "role": "REVIEWER"
}
if reviewer_title:
    reviewer_login['title'] = reviewer_title
if reviewer_inst_id:
    reviewer_login['institutionId'] = reviewer_inst_id
if reviewer_bg:
    reviewer_login['expertBackground'] = reviewer_bg

reviewer_resp = requests.post(
    f"{BASE_URL}/api/auth/login",
    json=reviewer_login,
    timeout=5
)

if reviewer_resp.status_code != 200:
    print(f"✗ 登录失败: {reviewer_resp.text}")
    exit(1)

reviewer_data = reviewer_resp.json()
if not reviewer_data.get('success'):
    print(f"✗ 登录失败: {reviewer_data.get('message')}")
    exit(1)

reviewer_token = reviewer_data['data']['token']
reviewer_headers = {"Authorization": f"Bearer {reviewer_token}"}
print(f"✓ 评审专家登录成功")

# 5. 提交评分
print("\n5. 提交评分...")
score_data = {
    "reviewTaskId": task['id'],
    "plan": 18.0,
    "problem": 17.5,
    "action": 18.5,
    "success": 13.0,
    "review": 9.0,
    "operation": 8.5,
    "presentation": 4.5,
    "highlight": "项目设计科学合理，实施路径清晰，效果显著",
    "weakness": "数据分析的深度和广度可以进一步加强，持续改进机制需要完善"
}

print(f"评分数据: {json.dumps(score_data, ensure_ascii=False, indent=2)}")

score_resp = requests.post(
    f"{BASE_URL}/api/reviews/scores",
    json=score_data,
    headers=reviewer_headers,
    timeout=5
)

print(f"\n状态码: {score_resp.status_code}")

if score_resp.status_code == 200:
    score_result = score_resp.json()
    print(f"响应: {json.dumps(score_result, ensure_ascii=False, indent=2)}")
    
    if score_result.get('success'):
        print(f"\n" + "=" * 80)
        print(f"✓✓✓ 评分提交成功! ✓✓✓")
        print(f"=" * 80)
        score_info = score_result['data']
        print(f"评分ID: {score_info.get('id')}")
        print(f"总分: {score_info.get('total')}")
        print(f"提交时间: {score_info.get('submittedAt')}")
    else:
        print(f"\n✗ 评分失败: {score_result.get('message')}")
else:
    print(f"响应: {score_resp.text}")
    print(f"\n✗ HTTP错误")

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)
