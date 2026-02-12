#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试提交评分接口"""

import requests
import json

BASE_URL = "http://localhost:6031"

print("=" * 80)
print("测试提交评分接口")
print("=" * 80)

# 1. 登录评审专家账号
print("\n1. 登录评审专家账号")
print("-" * 80)
login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "phone": "13800000006",
    "name": "李明华",
    "title": "主任医师",
    "role": "REVIEWER",
    "institutionId": 2,
    "expertBackground": "MEDICAL"
})

print(f"状态码: {login_response.status_code}")
if login_response.status_code == 200:
    data = login_response.json()
    if data.get('success'):
        token = data['data']['token']
        print(f"✓ 登录成功")
        print(f"Token: {token[:50]}...")
    else:
        print(f"✗ 登录失败: {data.get('message')}")
        exit(1)
else:
    print(f"✗ 请求失败")
    exit(1)

headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# 2. 查询我的评审任务
print("\n2. 查询我的评审任务")
print("-" * 80)
tasks_response = requests.get(f"{BASE_URL}/api/reviews/my-tasks", headers=headers)
print(f"状态码: {tasks_response.status_code}")

if tasks_response.status_code == 200:
    tasks_data = tasks_response.json()
    if tasks_data.get('success'):
        tasks = tasks_data.get('data', [])
        print(f"✓ 查询成功，共 {len(tasks)} 个任务")
        
        if tasks:
            # 找一个待评分的任务
            task_to_score = None
            for task in tasks:
                print(f"\n  任务ID: {task['id']}")
                print(f"  项目: {task.get('projectName')}")
                print(f"  状态: {task['status']}")
                print(f"  环节: {task['stage']}")
                
                if task['status'] in ['PENDING', 'CONFIRMED'] and not task_to_score:
                    task_to_score = task
            
            if task_to_score:
                print(f"\n选择任务 {task_to_score['id']} 进行评分测试")
                
                # 3. 提交评分
                print("\n3. 提交评分")
                print("-" * 80)
                
                score_data = {
                    "reviewTaskId": task_to_score['id'],
                    "plan": 10.0,
                    "problem": 10.0,
                    "action": 10.0,
                    "success": 10.0,
                    "review": 10.0,
                    "operation": 10.0,
                    "presentation": 10.0,
                    "highlight": "项目计划清晰，问题分析到位",
                    "weakness": "数据分析可以更深入"
                }
                
                print(f"请求数据: {json.dumps(score_data, ensure_ascii=False, indent=2)}")
                
                score_response = requests.post(
                    f"{BASE_URL}/api/reviews/scores",
                    json=score_data,
                    headers=headers
                )
                
                print(f"\n状态码: {score_response.status_code}")
                print(f"响应: {score_response.text}")
                
                if score_response.status_code == 200:
                    score_result = score_response.json()
                    if score_result.get('success'):
                        print(f"\n✓ 评分提交成功")
                        score_info = score_result.get('data', {})
                        print(f"评分ID: {score_info.get('id')}")
                        print(f"总分: {score_info.get('total')}")
                    else:
                        print(f"\n✗ 评分提交失败: {score_result.get('message')}")
                else:
                    print(f"\n✗ 请求失败")
                    # 尝试解析错误信息
                    try:
                        error_data = score_response.json()
                        print(f"错误信息: {json.dumps(error_data, ensure_ascii=False, indent=2)}")
                    except:
                        pass
            else:
                print(f"\n没有可评分的任务（所有任务都已评分）")
                print(f"尝试对已评分的任务重新评分...")
                
                # 使用第一个任务测试
                if tasks:
                    test_task = tasks[0]
                    print(f"\n使用任务 {test_task['id']} 测试")
                    
                    score_data = {
                        "reviewTaskId": test_task['id'],
                        "plan": 9.5,
                        "problem": 9.0,
                        "action": 9.5,
                        "success": 9.0,
                        "review": 9.5,
                        "operation": 9.0,
                        "presentation": 9.5,
                        "highlight": "测试评分-亮点",
                        "weakness": "测试评分-不足"
                    }
                    
                    print(f"\n3. 提交评分（重新评分）")
                    print("-" * 80)
                    print(f"请求数据: {json.dumps(score_data, ensure_ascii=False, indent=2)}")
                    
                    score_response = requests.post(
                        f"{BASE_URL}/api/reviews/scores",
                        json=score_data,
                        headers=headers
                    )
                    
                    print(f"\n状态码: {score_response.status_code}")
                    print(f"响应: {score_response.text}")
        else:
            print(f"该评审专家没有分配任务")
    else:
        print(f"✗ 查询失败: {tasks_data.get('message')}")
else:
    print(f"✗ 请求失败")

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)
