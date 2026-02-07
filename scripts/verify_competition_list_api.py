#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证赛事列表API"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import json

BASE = "http://localhost:6031"

print("="*80)
print("验证赛事列表API")
print("="*80)

# 登录获取token
print("\n[1] 登录...")
try:
    login_resp = requests.post(f"{BASE}/api/auth/login", json={
        "phone": "13800000003",
        "name": "组委会管理员",
        "role": "COMMITTEE"
    }, timeout=10)
    
    if login_resp.status_code != 200:
        print(f"❌ 登录失败: {login_resp.status_code}")
        exit(1)
    
    token = login_resp.json()['data']['token']
    print("✅ 登录成功")
    
except Exception as e:
    print(f"❌ 登录异常: {e}")
    exit(1)

headers = {"Authorization": f"Bearer {token}"}

# 获取赛事列表
print("\n[2] 获取赛事列表...")
print("-" * 80)

try:
    resp = requests.get(f"{BASE}/api/competitions", headers=headers, timeout=10)
    
    if resp.status_code != 200:
        print(f"❌ 请求失败: {resp.status_code}")
        print(f"响应: {resp.text}")
        exit(1)
    
    competitions = resp.json()['data']
    
    print(f"✅ 获取成功，共 {len(competitions)} 个赛事\n")
    
    # 显示每个赛事
    for comp in competitions:
        print(f"ID {comp['id']}: {comp['name']}")
        print(f"  阶段: {comp['stage']}")
        print(f"  报名时间: {comp.get('registerStart', 'N/A')} ~ {comp.get('registerEnd', 'N/A')}")
        print()
    
    # 验证
    print("="*80)
    print("验证结果")
    print("="*80)
    
    expected_ids = [21, 28, 29]
    actual_ids = [comp['id'] for comp in competitions]
    
    print(f"\n预期赛事ID: {expected_ids}")
    print(f"实际赛事ID: {actual_ids}")
    
    if set(actual_ids) == set(expected_ids):
        print("\n✅ 验证通过：赛事列表正确，已删除脏数据赛事")
    else:
        print("\n⚠️  验证失败：赛事列表不符合预期")
        
        missing = set(expected_ids) - set(actual_ids)
        extra = set(actual_ids) - set(expected_ids)
        
        if missing:
            print(f"缺失的赛事ID: {missing}")
        if extra:
            print(f"多余的赛事ID: {extra}")
    
    # 检查是否还有脏数据
    print("\n检查脏数据...")
    has_dirty = False
    for comp in competitions:
        if comp.get('registerStart') is None and comp.get('registerEnd') is None:
            print(f"⚠️  发现脏数据: ID {comp['id']} - {comp['name']}")
            has_dirty = True
    
    if not has_dirty:
        print("✅ 没有脏数据赛事")
    
except Exception as e:
    print(f"❌ 请求异常: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "="*80)
print("验证完成")
print("="*80)
