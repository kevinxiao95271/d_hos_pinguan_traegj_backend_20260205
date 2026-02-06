#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查并修复评委账号"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import json

BASE = "http://localhost:6031"

print("="*80)
print("检查评委账号")
print("="*80)

# 测试的账号列表
test_accounts = [
    ("13800000002", "王建国"),
    ("13800000021", "李明华"),
    ("13800000022", "张秀英"),
    ("13800002001", "陈卫东"),
    ("13800002002", "刘芳"),
]

print("\n[测试评委账号登录]\n")

working_accounts = []
failed_accounts = []

for phone, name in test_accounts:
    print(f"测试: {phone} - {name}")
    
    # 尝试登录
    resp = requests.post(f"{BASE}/api/auth/login", json={
        "phone": phone,
        "name": name,
        "role": "REVIEWER"
    })
    
    if resp.status_code == 200:
        data = resp.json()['data']
        reviewer_id = data['id']
        print(f"  ✅ 登录成功 (ID={reviewer_id})")
        working_accounts.append((phone, name, reviewer_id))
    else:
        print(f"  ❌ 登录失败: {resp.status_code}")
        failed_accounts.append((phone, name))

print("\n" + "="*80)
print("检查结果")
print("="*80)

print(f"\n可用账号: {len(working_accounts)} 个")
for phone, name, reviewer_id in working_accounts:
    print(f"  {phone} - {name} (ID={reviewer_id})")

if failed_accounts:
    print(f"\n失败账号: {len(failed_accounts)} 个")
    for phone, name in failed_accounts:
        print(f"  {phone} - {name}")

# 如果有可用账号，获取他们的任务
if working_accounts:
    print("\n" + "="*80)
    print("检查评审任务")
    print("="*80)
    
    for phone, name, reviewer_id in working_accounts:
        # 登录
        login_resp = requests.post(f"{BASE}/api/auth/login", json={
            "phone": phone,
            "name": name,
            "role": "REVIEWER"
        })
        
        if login_resp.status_code != 200:
            continue
        
        token = login_resp.json()['data']['token']
        
        # 获取任务
        tasks_resp = requests.get(f"{BASE}/api/reviews/my-tasks", 
                                 headers={"Authorization": f"Bearer {token}"})
        
        if tasks_resp.status_code == 200:
            tasks = tasks_resp.json()['data']
            print(f"\n{name} ({phone}):")
            if tasks:
                print(f"  任务数: {len(tasks)} 个")
                for task in tasks[:3]:  # 只显示前3个
                    print(f"    - 任务{task['id']}: {task.get('projectName', '无名称')} ({task['status']})")
            else:
                print(f"  无任务")
        else:
            print(f"\n{name} ({phone}): 获取任务失败")

print("\n" + "="*80)
print("建议")
print("="*80)

if working_accounts:
    print("\n✅ 推荐使用以下账号测试:\n")
    for phone, name, reviewer_id in working_accounts[:3]:
        print(f"手机号: {phone}")
        print(f"姓名: {name}")
        print(f"角色: REVIEWER")
        print()
else:
    print("\n⚠️  没有可用的评委账号")
    print("请检查数据库中的user_accounts表")
