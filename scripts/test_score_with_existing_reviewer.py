#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用现有评审专家测试评分"""

import requests
import json

BASE_URL = "http://localhost:6031"

# 1. 管理员登录
print("1. 管理员登录...")
admin_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
    "phone": "13800000041",
    "name": "CommitteeAdmin A",
    "role": "COMMITTEE_ADMIN"
}, timeout=5)

if admin_resp.status_code != 200 or not admin_resp.json().get('success'):
    print("管理员登录失败")
    exit(1)

admin_token = admin_resp.json()['data']['token']
print("✓ 管理员登录成功")

# 2. 查询评审专家列表
print("\n2. 查询评审专家列表...")
headers = {"Authorization": f"Bearer {admin_token}"}
reviewers_resp = requests.get(f"{BASE_URL}/api/admin/reviews/reviewers", headers=headers, timeout=5)

if reviewers_resp.status_code == 200:
    reviewers_data = reviewers_resp.json()
    if reviewers_data.get('success'):
        reviewers = reviewers_data.get('data', [])
        print(f"✓ 找到 {len(reviewers)} 个评审专家")
        
        if reviewers:
            # 显示前5个
            print("\n前5个评审专家:")
            for i, r in enumerate(reviewers[:5], 1):
                print(f"  {i}. ID:{r.get('id')} {r.get('name')} ({r.get('phone')})")
                print(f"     机构:{r.get('institutionName')} 背景:{r.get('expertBackground')}")
            
            # 选择第一个评审专家
            reviewer = reviewers[0]
            print(f"\n选择评审专家: {reviewer.get('name')} ({reviewer.get('phone')})")
            
            # 3. 用该评审专家登录
            print("\n3. 评审专家登录...")
            reviewer_login = {
                "phone": reviewer.get('phone'),
                "name": reviewer.get('name'),
                "role": "REVIEWER"
            }
            
            # 添加可选字段
            if reviewer.get('title'):
                reviewer_login['title'] = reviewer.get('title')
            if reviewer.get('institutionId'):
                reviewer_login['institutionId'] = reviewer.get('institutionId')
            if reviewer.get('expertBackground'):
                reviewer_login['expertBackground'] = reviewer.get('expertBackground')
            
            print(f"登录数据: {json.dumps(reviewer_login, ensure_ascii=False)}")
            
            reviewer_resp = requests.post(
                f"{BASE_URL}/api/auth/login",
                json=reviewer_login,
                timeout=5
            )
            
            print(f"状态码: {reviewer_resp.status_code}")
            
            if reviewer_resp.status_code == 200:
                reviewer_data = reviewer_resp.json()
                if reviewer_data.get('success'):
                    reviewer_token = reviewer_data['data']['token']
                    print(f"✓ 评审专家登录成功")
                    
                    # 4. 查询该评审专家的任务
                    print("\n4. 查询评审任务...")
                    reviewer_headers = {"Authorization": f"Bearer {reviewer_token}"}
                    tasks_resp = requests.get(
                        f"{BASE_URL}/api/reviews/my-tasks",
                        headers=reviewer_headers,
                        timeout=5
                    )
                    
                    if tasks_resp.status_code == 200:
                        tasks_data = tasks_resp.json()
                        if tasks_data.get('success'):
                            tasks = tasks_data.get('data', [])
                            print(f"✓ 找到 {len(tasks)} 个任务")
                            
                            if tasks:
                                task = tasks[0]
                                print(f"\n选择任务: ID={task['id']} {task.get('projectName')}")
                                
                                # 5. 提交评分
                                print("\n5. 提交评分...")
                                score_data = {
                                    "reviewTaskId": task['id'],
                                    "plan": 15.0,
                                    "problem": 15.0,
                                    "action": 15.0,
                                    "success": 10.0,
                                    "review": 8.0,
                                    "operation": 8.0,
                                    "presentation": 4.0,
                                    "highlight": "项目设计合理，实施效果明显",
                                    "weakness": "数据分析深度可以加强"
                                }
                                
                                score_resp = requests.post(
                                    f"{BASE_URL}/api/reviews/scores",
                                    json=score_data,
                                    headers=reviewer_headers,
                                    timeout=5
                                )
                                
                                print(f"状态码: {score_resp.status_code}")
                                print(f"响应: {score_resp.text}")
                                
                                if score_resp.status_code == 200:
                                    score_result = score_resp.json()
                                    if score_result.get('success'):
                                        print(f"\n✓✓✓ 评分提交成功! ✓✓✓")
                                        score_info = score_result['data']
                                        print(f"评分ID: {score_info.get('id')}")
                                        print(f"总分: {score_info.get('total')}")
                                    else:
                                        print(f"\n✗ 评分失败: {score_result.get('message')}")
                                else:
                                    print(f"\n✗ HTTP错误")
                            else:
                                print("该评审专家没有任务")
                        else:
                            print(f"✗ 查询任务失败: {tasks_data.get('message')}")
                    else:
                        print(f"✗ 查询任务HTTP错误: {tasks_resp.status_code}")
                else:
                    print(f"✗ 评审专家登录失败: {reviewer_data.get('message')}")
                    print(f"响应: {reviewer_resp.text}")
            else:
                print(f"✗ 评审专家登录HTTP错误")
                print(f"响应: {reviewer_resp.text}")
        else:
            print("没有评审专家")
    else:
        print(f"✗ 查询失败: {reviewers_data.get('message')}")
else:
    print(f"✗ HTTP错误: {reviewers_resp.status_code}")
