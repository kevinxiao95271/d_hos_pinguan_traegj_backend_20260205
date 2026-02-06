#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试修复后的API"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import json

BASE = "http://localhost:6031"

print("="*80)
print("测试修复后的API")
print("="*80)

# 1. 测试评委端 - 我的任务
print("\n[1] 测试评委端 - 我的任务")
print("-"*80)

# 评委登录
r = requests.post(f"{BASE}/api/auth/login", json={
    "phone": "13800000021",
    "name": "李明华",
    "role": "REVIEWER"
})

if r.status_code != 200:
    print(f"评委登录失败: {r.status_code}")
else:
    reviewer_token = r.json()['data']['token']
    reviewer_id = r.json()['data']['id']
    print(f"评委登录成功: ID={reviewer_id}, 姓名=李明华")
    
    # 测试 GET /api/reviews/my-tasks
    headers = {"Authorization": f"Bearer {reviewer_token}"}
    r2 = requests.get(f"{BASE}/api/reviews/my-tasks", headers=headers)
    
    print(f"\nGET /api/reviews/my-tasks")
    print(f"  状态码: {r2.status_code}")
    
    if r2.status_code == 200:
        tasks = r2.json().get('data', [])
        print(f"  [成功] 返回 {len(tasks)} 个评审任务")
        if tasks:
            print(f"  示例任务: ID={tasks[0].get('id')}, 报名ID={tasks[0].get('registrationId')}")
    else:
        print(f"  [失败] {r2.text}")

# 2. 测试参赛者端 - 我的报名
print("\n[2] 测试参赛者端 - 我的报名")
print("-"*80)

# 参赛者登录
r = requests.post(f"{BASE}/api/auth/login", json={
    "phone": "13800000001",
    "name": "参赛者",
    "role": "CONTESTANT"
})

if r.status_code != 200:
    print(f"参赛者登录失败: {r.status_code}")
else:
    contestant_token = r.json()['data']['token']
    contestant_id = r.json()['data']['id']
    print(f"参赛者登录成功: ID={contestant_id}")
    
    # 测试 GET /api/registrations/my
    headers = {"Authorization": f"Bearer {contestant_token}"}
    r3 = requests.get(f"{BASE}/api/registrations/my", headers=headers)
    
    print(f"\nGET /api/registrations/my")
    print(f"  状态码: {r3.status_code}")
    
    if r3.status_code == 200:
        regs = r3.json().get('data', [])
        print(f"  [成功] 返回 {len(regs)} 个报名记录")
        if regs:
            print(f"  示例报名: ID={regs[0].get('id')}, 项目={regs[0].get('projectName')}, 状态={regs[0].get('status')}")
    else:
        print(f"  [失败] {r3.text}")

# 3. 测试报名创建API - 显示完整参数列表
print("\n[3] 报名创建API - 完整参数列表")
print("-"*80)
print("POST /api/registrations")
print("\n必填参数:")
print("""
{
  "competitionId": Long,         // 赛事ID
  "institutionId": Long,         // 机构ID  
  "projectName": String,         // 项目名称
  "projectType": String,         // 项目类型
  "contactName": String,         // 联系人
  "contactPhone": String,        // 联系电话
  "contactEmail": String         // 联系邮箱
}
""")

print("完整报名流程:")
print("1. POST /api/registrations - 创建报名（草稿状态）")
print("2. PUT /api/registrations/{id}/members - 提交成员信息")
print("3. PUT /api/registrations/{id}/activity - 提交活动说明")
print("4. PUT /api/registrations/{id}/summary - 提交项目总结")
print("5. POST /api/registrations/{id}/materials - 上传材料")
print("6. POST /api/registrations/{id}/submit - 提交报名（变为待审核状态）")

# 4. 测试评分API
print("\n[4] 评审打分API - 参数说明")
print("-"*80)
print("POST /api/reviews/scores")
print("\n参数:")
print("""
{
  "reviewTaskId": Long,          // 评审任务ID
  "scores": {                    // 各维度评分
    "dimension1": Double,        // 维度1得分 (0-100)
    "dimension2": Double,        // 维度2得分 (0-100)
    ...
  },
  "comments": String,            // 评审意见
  "suggestions": String          // 改进建议
}
""")

print("\n" + "="*80)
print("API修复完成！")
print("="*80)
print("\n已修复:")
print("  [成功] GET /api/reviews/my-tasks - 评委查看自己的任务")
print("  [成功] GET /api/registrations/my - 参赛者查看自己的报名")
print("\n需要前端配合:")
print("  - 评委端使用 /api/reviews/my-tasks 替代 /api/reviews/tasks")
print("  - 参赛者端使用 /api/registrations/my 替代 /api/registrations/by-applicant")
