#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试评分提交接口 - 正确版本"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import json

BASE = "http://localhost:6031"

print("="*80)
print("测试评分提交接口")
print("="*80)

# 1. 登录
print("\n[1] 登录李明华")
login_resp = requests.post(f"{BASE}/api/auth/login", json={
    "phone": "13800000021",
    "name": "李明华",
    "role": "REVIEWER"
})

if login_resp.status_code != 200:
    print(f"❌ 登录失败: {login_resp.status_code}")
    exit(1)

token = login_resp.json()['data']['token']
reviewer_id = login_resp.json()['data']['id']
print(f"✅ 登录成功 (评委ID={reviewer_id})")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 2. 获取任务
print("\n[2] 获取任务列表")
tasks_resp = requests.get(f"{BASE}/api/reviews/my-tasks", headers=headers)

if tasks_resp.status_code != 200:
    print(f"❌ 获取任务失败: {tasks_resp.status_code}")
    exit(1)

tasks = tasks_resp.json()['data']

if not tasks:
    print("❌ 没有可用任务")
    exit(1)

task = tasks[0]
task_id = task['id']
registration_id = task['registrationId']
project_name = task['projectName']

print(f"✅ 找到任务")
print(f"   任务ID (reviewTaskId): {task_id}")
print(f"   项目ID (registrationId): {registration_id}")
print(f"   项目名称: {project_name}")

# 3. 提交评分 - 正确的格式
print("\n[3] 提交评分")

score_data = {
    "reviewTaskId": task_id,  # ⭐ 使用任务ID，不是项目ID
    "plan": 18,
    "problem": 17,
    "action": 19,
    "success": 18,
    "review": 16,
    "operation": 0,
    "presentation": 0,
    "highlight": "项目主题明确，改进措施得当，成效显著。实施过程规范，数据收集完整，对比分析清晰。团队协作良好。",
    "weakness": "建议进一步量化成本效益分析。可以增加更多的跨部门协作案例。持续改进机制可以更完善。"
}

print("\n提交的数据:")
print(json.dumps(score_data, indent=2, ensure_ascii=False))

score_resp = requests.post(
    f"{BASE}/api/reviews/scores",
    headers=headers,
    json=score_data
)

print(f"\n状态码: {score_resp.status_code}")

if score_resp.status_code == 200:
    result = score_resp.json()['data']
    print("\n✅ 评分提交成功！")
    print(f"   评分ID: {result['id']}")
    print(f"   任务ID: {result.get('reviewTaskId')}")
    print(f"   总分: {result['total']}")
    print(f"   计划: {result['plan']}")
    print(f"   问题: {result['problem']}")
    print(f"   措施: {result['action']}")
    print(f"   成效: {result['success']}")
    print(f"   回顾: {result['review']}")
    print(f"   提交时间: {result.get('submittedAt')}")
    
    # 4. 验证：再次获取任务状态
    print("\n[4] 验证任务状态")
    tasks_resp2 = requests.get(f"{BASE}/api/reviews/my-tasks", headers=headers)
    if tasks_resp2.status_code == 200:
        tasks2 = tasks_resp2.json()['data']
        task2 = next((t for t in tasks2 if t['id'] == task_id), None)
        if task2:
            print(f"✅ 任务状态已更新: {task2['status']}")
        else:
            print("⚠️  任务列表中找不到该任务（可能已完成）")
    
else:
    print("\n❌ 提交失败")
    try:
        error_data = score_resp.json()
        print(f"   错误信息: {error_data.get('message', '未知错误')}")
        print(f"   完整响应: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
    except:
        print(f"   响应内容: {score_resp.text}")

print("\n" + "="*80)
print("测试完成")
print("="*80)
