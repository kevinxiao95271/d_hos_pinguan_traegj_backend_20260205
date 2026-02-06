#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""创建评审任务测试数据"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import json

BASE = "http://localhost:6031"

print("="*80)
print("创建评审任务测试数据")
print("="*80)

# 步骤1: 检查现有报名
print("\n[1] 检查现有报名")
try:
    # 先用组委会账号登录
    committee_login = requests.post(f"{BASE}/api/auth/login", json={
        "phone": "13800000009",
        "name": "组委会",
        "role": "COMMITTEE"
    })
    
    if committee_login.status_code != 200:
        print("组委会账号不存在，尝试OPS账号")
        committee_login = requests.post(f"{BASE}/api/auth/login", json={
            "phone": "13800000001",
            "name": "系统管理员",
            "role": "OPS"
        })
    
    committee_token = committee_login.json()['data']['token']
    committee_headers = {
        "Authorization": f"Bearer {committee_token}",
        "Content-Type": "application/json"
    }
    
    # 获取赛事列表
    competitions_resp = requests.get(f"{BASE}/api/competitions", headers=committee_headers)
    if competitions_resp.status_code == 200:
        competitions = competitions_resp.json()['data']
        if competitions:
            competition_id = competitions[0]['id']
            print(f"使用赛事: {competitions[0]['name']} (ID={competition_id})")
        else:
            print("没有赛事，无法创建任务")
            exit(1)
    
    # 获取已提交的报名列表
    registrations_resp = requests.get(f"{BASE}/api/registrations?competitionId={competition_id}", 
                                     headers=committee_headers)
    
    if registrations_resp.status_code == 200:
        registrations = [r for r in registrations_resp.json()['data'] 
                        if r.get('status') == 'SUBMITTED']
        print(f"找到 {len(registrations)} 个已提交的报名")
    else:
        registrations = []
        print("没有找到已提交的报名")
    
except Exception as e:
    print(f"检查失败: {e}")
    registrations = []

# 步骤2: 如果没有报名，创建一些测试报名
if len(registrations) < 3:
    print(f"\n[2] 创建测试报名（当前只有{len(registrations)}个）")
    
    # 参赛者登录
    contestant_login = requests.post(f"{BASE}/api/auth/login", json={
        "phone": "13900000001",
        "name": "测试参赛者1",
        "role": "CONTESTANT"
    })
    
    contestant_token = contestant_login.json()['data']['token']
    contestant_headers = {
        "Authorization": f"Bearer {contestant_token}",
        "Content-Type": "application/json"
    }
    
    # 创建3个报名
    for i in range(3):
        print(f"\n创建报名 {i+1}/3")
        
        # 创建报名
        reg_resp = requests.post(f"{BASE}/api/registrations", headers=contestant_headers, json={
            "competitionId": competition_id,
            "institutionId": (i % 5) + 1,  # 轮换机构
            "projectName": f"测试项目{i+1} - 优化医疗服务流程",
            "groupType": "BASIC" if i < 2 else "ADVANCED"
        })
        
        if reg_resp.status_code != 200:
            print(f"创建报名失败: {reg_resp.status_code}")
            continue
        
        reg_id = reg_resp.json()['data']['id']
        print(f"报名ID: {reg_id}")
        
        # 提交成员
        requests.put(f"{BASE}/api/registrations/{reg_id}/members", 
                    headers=contestant_headers, json={
            "members": [
                {
                    "name": f"成员{i+1}-1",
                    "title": "主管护师",
                    "role": "PARTICIPANT",
                    "department": "内科"
                },
                {
                    "name": f"成员{i+1}-2",
                    "title": "副主任医师",
                    "role": "MENTOR"
                }
            ]
        })
        
        # 提交活动说明
        requests.put(f"{BASE}/api/registrations/{reg_id}/activity", 
                    headers=contestant_headers, json={
            "theme": f"测试主题{i+1}",
            "keywords": "测试,优化,改进",
            "subjectTypeCode": "subject_type_1",
            "methodCode": "PDCA",
            "experienceImproveCode": "experience_1",
            "qualityTopicCode": "quality_topic_1",
            "avgWorkYears": 5 + i,
            "avgAge": 30 + i,
            "crossDepartment": False
        })
        
        # 提交总结
        requests.put(f"{BASE}/api/registrations/{reg_id}/summary", 
                    headers=contestant_headers, json={
            "theme": f"测试主题{i+1}",
            "plan": f"测试计划{i+1}",
            "problem": f"测试问题{i+1}",
            "action": f"测试措施{i+1}",
            "result": f"测试成效{i+1}",
            "conclusion": f"测试结论{i+1}"
        })
        
        # 提交报名
        submit_resp = requests.post(f"{BASE}/api/registrations/{reg_id}/submit", 
                                   headers=contestant_headers)
        
        if submit_resp.status_code == 200:
            print(f"报名 {reg_id} 已提交")
            registrations.append({"id": reg_id})
        else:
            print(f"提交失败: {submit_resp.status_code}")

# 步骤3: 获取评委列表
print("\n[3] 获取评委列表")
reviewers_resp = requests.get(f"{BASE}/api/admin/reviewers", headers=committee_headers)

if reviewers_resp.status_code == 200:
    reviewers = reviewers_resp.json()['data']
    print(f"找到 {len(reviewers)} 个评委")
    
    if len(reviewers) < 3:
        print("评委数量不足，需要至少3个评委")
        exit(1)
else:
    print(f"获取评委失败: {reviewers_resp.status_code}")
    exit(1)

# 步骤4: 分配评审任务
print("\n[4] 分配评审任务")

# 为每个报名分配2-3个评委
task_count = 0
assigned_reviewers = {}

for i, reg in enumerate(registrations[:5]):  # 最多处理5个报名
    reg_id = reg['id']
    print(f"\n报名 {reg_id}:")
    
    # 为每个报名分配2个评委
    for j in range(min(2, len(reviewers))):
        reviewer = reviewers[j]
        reviewer_id = reviewer['id']
        reviewer_name = reviewer['name']
        
        # 分配任务
        task_resp = requests.post(f"{BASE}/api/reviews/tasks", 
                                 headers=committee_headers, json={
            "registrationId": reg_id,
            "reviewerId": reviewer_id,
            "stage": "BOOK"  # 正确的枚举值是BOOK，不是BOOK_REVIEW
        })
        
        if task_resp.status_code == 200:
            task = task_resp.json()['data']
            task_id = task['id']
            print(f"  - 分配给 {reviewer_name} (评委ID={reviewer_id}, 任务ID={task_id})")
            task_count += 1
            
            # 记录分配的评委
            if reviewer_id not in assigned_reviewers:
                assigned_reviewers[reviewer_id] = {
                    'name': reviewer_name,
                    'phone': reviewer.get('phone', '未知'),
                    'tasks': []
                }
            assigned_reviewers[reviewer_id]['tasks'].append(task_id)
        else:
            print(f"  - 分配失败: {task_resp.status_code} - {task_resp.text}")

print("\n" + "="*80)
print(f"评审任务创建完成！共创建 {task_count} 个任务")
print("="*80)

if assigned_reviewers:
    print("\n【有任务的评委账号】\n")
    for reviewer_id, info in assigned_reviewers.items():
        print(f"评委: {info['name']}")
        print(f"  手机号: {info['phone']}")
        print(f"  评委ID: {reviewer_id}")
        print(f"  任务数: {len(info['tasks'])} 个")
        print(f"  任务ID: {', '.join(map(str, info['tasks']))}")
        print()
    
    print("="*80)
    print("\n【测试步骤】")
    first_reviewer = list(assigned_reviewers.values())[0]
    print(f"\n1. 使用以下账号登录:")
    print(f"   手机号: {first_reviewer['phone']}")
    print(f"   姓名: {first_reviewer['name']}")
    print(f"   角色: REVIEWER")
    print(f"\n2. 调用 GET /api/reviews/my-tasks 查看任务")
    print(f"\n3. 应该能看到 {len(first_reviewer['tasks'])} 个待评审任务")
else:
    print("\n没有成功分配任务，请检查日志")
