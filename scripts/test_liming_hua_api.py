#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试李明华的评审任务API"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import json

BASE = "http://localhost:6031"

print("="*80)
print("测试李明华的评审任务API")
print("="*80)

# 登录
print("\n[1] 登录李明华")
login_resp = requests.post(f"{BASE}/api/auth/login", json={
    "phone": "13800000021",
    "name": "李明华",
    "role": "REVIEWER"
})

if login_resp.status_code != 200:
    print(f"❌ 登录失败: {login_resp.status_code}")
    print(login_resp.text)
    exit(1)

login_data = login_resp.json()['data']
token = login_data['token']
reviewer_id = login_data['id']

print(f"✅ 登录成功")
print(f"   评委ID: {reviewer_id}")
print(f"   姓名: {login_data['name']}")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 获取任务列表
print("\n[2] 获取任务列表 - GET /api/reviews/my-tasks")
tasks_resp = requests.get(f"{BASE}/api/reviews/my-tasks", headers=headers)

print(f"   状态码: {tasks_resp.status_code}")

if tasks_resp.status_code != 200:
    print(f"   ❌ 获取任务失败")
    print(f"   响应: {tasks_resp.text}")
    exit(1)

tasks_data = tasks_resp.json()['data']
print(f"   ✅ 成功获取 {len(tasks_data)} 个任务\n")

# 显示每个任务的详细信息
print("="*80)
print("任务列表详情")
print("="*80)

for idx, task in enumerate(tasks_data, 1):
    print(f"\n任务 {idx}:")
    print(f"  任务ID (id): {task.get('id')}")
    print(f"  报名ID (registrationId): {task.get('registrationId')}")
    print(f"  项目名称 (projectName): {task.get('projectName')}")
    print(f"  机构名称 (institutionName): {task.get('institutionName')}")
    print(f"  阶段 (stage): {task.get('stage')}")
    print(f"  状态 (status): {task.get('status')}")
    print(f"  创建时间 (createdAt): {task.get('createdAt')}")
    
    # 检查缺失字段
    missing_fields = []
    if not task.get('registrationId'):
        missing_fields.append('registrationId')
    if not task.get('projectName'):
        missing_fields.append('projectName')
    if not task.get('institutionName'):
        missing_fields.append('institutionName')
    
    if missing_fields:
        print(f"  ⚠️  缺失字段: {', '.join(missing_fields)}")

# 测试单个任务的详情API
if tasks_data:
    first_task = tasks_data[0]
    task_id = first_task['id']
    registration_id = first_task.get('registrationId')
    
    print("\n" + "="*80)
    print(f"测试任务详情API - 任务ID={task_id}")
    print("="*80)
    
    if registration_id:
        # 测试获取报名详情
        print(f"\n[3] 获取报名详情 - GET /api/registrations/{registration_id}")
        reg_resp = requests.get(f"{BASE}/api/registrations/{registration_id}", headers=headers)
        print(f"   状态码: {reg_resp.status_code}")
        
        if reg_resp.status_code == 200:
            reg_data = reg_resp.json()['data']
            print(f"   ✅ 成功获取报名详情")
            print(f"   项目名称: {reg_data.get('projectName')}")
            print(f"   机构ID: {reg_data.get('institutionId')}")
            print(f"   状态: {reg_data.get('status')}")
            
            # 显示完整的JSON结构（方便前端参考）
            print("\n   完整数据结构:")
            print(json.dumps(reg_data, indent=2, ensure_ascii=False)[:500] + "...")
        else:
            print(f"   ❌ 获取失败: {reg_resp.text}")
    else:
        print(f"\n⚠️  任务数据中缺少 registrationId，无法获取报名详情")

# 给出前端指引
print("\n" + "="*80)
print("前端开发指引")
print("="*80)

print("""
【问题分析】
前端提示"缺少项目id，无法加载详情"，说明前端需要 registrationId。

【API调用流程】

1. 获取任务列表
   GET /api/reviews/my-tasks
   
   返回数据应包含:
   {
     "id": 115,                    // 任务ID
     "registrationId": 106,         // ⭐ 报名ID（项目ID）
     "projectName": "xxx",          // 项目名称
     "institutionName": "xxx",      // 机构名称
     "stage": "BOOK",
     "status": "PENDING",
     "createdAt": "2026-02-06T..."
   }

2. 点击任务，跳转到评审页面
   URL: /reviewer/review/{taskId}?registrationId={registrationId}
   
   或者前端从任务数据中提取 registrationId

3. 在评审页面加载项目详情
   GET /api/registrations/{registrationId}
   
   返回完整的报名信息，包括:
   - projectName: 项目名称
   - institution: 机构信息
   - members: 成员列表
   - activityInfo: 活动说明
   - summary: 项目总结
   - materials: 材料文件

4. 提交评分
   POST /api/reviews/scores
   {
     "reviewTaskId": 115,
     "plan": 18,
     "problem": 17,
     "action": 19,
     "success": 18,
     "review": 16,
     "operation": 0,
     "presentation": 0,
     "highlight": "...",
     "weakness": "..."
   }

【前端路由配置】
/reviewer/review/:taskId
  - 从路由参数获取 taskId
  - 从任务列表数据中获取对应任务的 registrationId
  - 或者在URL中传递: /reviewer/review/:taskId?registrationId=xxx

【数据流向】
任务列表 -> 点击任务 -> 传递 registrationId -> 加载报名详情 -> 显示评分表单
""")

print("\n" + "="*80)
print("建议前端修改")
print("="*80)

print("""
1. 任务列表组件 (TaskList.vue)
   - 确保显示 task.projectName 和 task.institutionName
   - 点击任务时，传递 task.registrationId

2. 评审详情组件 (ReviewDetail.vue)
   - 从路由或父组件获取 registrationId
   - 调用 GET /api/registrations/{registrationId} 加载详情
   - 显示项目信息、成员、活动说明等

3. 评分表单组件 (ScoreForm.vue)
   - 表单提交时使用 taskId (不是registrationId)
   - POST /api/reviews/scores
""")
