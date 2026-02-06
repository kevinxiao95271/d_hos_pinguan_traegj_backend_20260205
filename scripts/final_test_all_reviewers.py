#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""最终测试所有评委账号"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import json

BASE = "http://localhost:6031"

test_reviewers = [
    ("13800000002", "王建国"),
    ("13800000021", "李明华"),
    ("13800002004", "孙丽娟"),
    ("13800000022", "张秀英"),
    ("13800002001", "陈卫东"),
]

print("="*80)
print("最终测试评委账号")
print("="*80)

working_with_tasks = []
working_no_tasks = []
failed = []

for phone, name in test_reviewers:
    print(f"\n测试: {name} ({phone})")
    
    # 登录
    login_resp = requests.post(f"{BASE}/api/auth/login", json={
        "phone": phone,
        "name": name,
        "role": "REVIEWER"
    })
    
    if login_resp.status_code != 200:
        print(f"  ❌ 登录失败")
        failed.append((phone, name))
        continue
    
    token = login_resp.json()['data']['token']
    
    # 获取任务
    tasks_resp = requests.get(f"{BASE}/api/reviews/my-tasks",
                             headers={"Authorization": f"Bearer {token}"})
    
    if tasks_resp.status_code != 200:
        print(f"  ❌ 获取任务失败")
        failed.append((phone, name))
        continue
    
    tasks = tasks_resp.json()['data']
    print(f"  ✅ 登录成功，任务数: {len(tasks)}")
    
    if tasks:
        working_with_tasks.append((phone, name, len(tasks)))
        # 显示前2个任务
        for task in tasks[:2]:
            print(f"     - 任务{task['id']}: {task.get('projectName', 'N/A')} ({task['status']})")
    else:
        working_no_tasks.append((phone, name))

print("\n" + "="*80)
print("测试结果汇总")
print("="*80)

if working_with_tasks:
    print(f"\n✅ 有任务的评委 ({len(working_with_tasks)} 个):")
    for phone, name, count in working_with_tasks:
        print(f"   {phone} - {name} ({count}个任务)")

if working_no_tasks:
    print(f"\n⚠️  无任务的评委 ({len(working_no_tasks)} 个):")
    for phone, name in working_no_tasks:
        print(f"   {phone} - {name}")

if failed:
    print(f"\n❌ 失败的账号 ({len(failed)} 个):")
    for phone, name in failed:
        print(f"   {phone} - {name}")

print("\n" + "="*80)
print("推荐测试账号:")
print("="*80)

if working_with_tasks:
    print("\n可直接用于测试书审打分功能:\n")
    for phone, name, count in working_with_tasks[:3]:
        print(f"手机号: {phone}")
        print(f"姓名: {name}")
        print(f"角色: REVIEWER")
        print(f"任务数: {count} 个")
        print()
