#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查评委账号登录情况"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests

BASE = "http://localhost:6031"

print("="*80)
print("检查评委账号登录情况")
print("="*80)

# 测试账号列表
test_accounts = [
    ("13800000002", "王建国"),
    ("13800000021", "李明华"),
    ("13800000022", "张秀英"),
    ("13800002001", "陈卫东"),
    ("13800002002", "刘芳"),
]

print("\n逐个测试登录:\n")

valid_accounts = []
failed_accounts = []

for phone, name in test_accounts:
    print(f"测试账号: {phone} - {name}")
    
    # 尝试登录
    resp = requests.post(f"{BASE}/api/auth/login", json={
        "phone": phone,
        "name": name,
        "role": "REVIEWER"
    })
    
    if resp.status_code == 200:
        data = resp.json()['data']
        user_id = data['id']
        token = data['token']
        print(f"  ✅ 登录成功 - 用户ID: {user_id}")
        valid_accounts.append((phone, name, user_id))
        
        # 检查是否有任务
        headers = {"Authorization": f"Bearer {token}"}
        tasks_resp = requests.get(f"{BASE}/api/reviews/my-tasks", headers=headers)
        
        if tasks_resp.status_code == 200:
            tasks = tasks_resp.json()['data']
            print(f"  📋 任务数: {len(tasks)}")
        else:
            print(f"  ⚠️  无法获取任务: {tasks_resp.status_code}")
    else:
        print(f"  ❌ 登录失败: {resp.status_code}")
        if resp.status_code == 500:
            print(f"     可能原因: 该手机号不存在于数据库中")
        failed_accounts.append((phone, name))
    
    print()

print("="*80)
print("检查结果")
print("="*80)

if valid_accounts:
    print(f"\n✅ 可用账号 ({len(valid_accounts)}个):\n")
    for phone, name, user_id in valid_accounts:
        print(f"  手机号: {phone}")
        print(f"  姓名: {name}")
        print(f"  用户ID: {user_id}")
        print()

if failed_accounts:
    print(f"\n❌ 失败账号 ({len(failed_accounts)}个):\n")
    for phone, name in failed_accounts:
        print(f"  {phone} - {name}")
    print()
    print("这些账号需要先在数据库中创建")

print("="*80)
