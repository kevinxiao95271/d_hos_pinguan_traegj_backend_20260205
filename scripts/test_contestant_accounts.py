#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试参赛者账号登录和报名查看"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import json

BASE = "http://localhost:6031"

# 测试账号列表
test_accounts = [
    {"phone": "13966000011", "name": "参赛者11", "registration_id": 116, "project": "门诊预约体验提升-11", "institution": "嘉兴市第一医院"},
    {"phone": "13966000012", "name": "参赛者12", "registration_id": 117, "project": "病案质量提升-12", "institution": "嘉兴市第二医院"},
    {"phone": "13966000013", "name": "参赛者13", "registration_id": 118, "project": "病区巡查标准化-13", "institution": "湖州市中心医院"},
    {"phone": "13966000014", "name": "参赛者14", "registration_id": 119, "project": "康复流程改进-14", "institution": "绍兴市人民医院"},
    {"phone": "13966000015", "name": "参赛者15", "registration_id": 120, "project": "信息系统提效-15", "institution": "金华市中心医院"},
]

print("="*80)
print("测试参赛者账号")
print("="*80)

successful_accounts = []
failed_accounts = []

for account in test_accounts:
    print(f"\n{'='*80}")
    print(f"测试账号: {account['name']} ({account['phone']})")
    print(f"预期项目: {account['project']}")
    print(f"预期机构: {account['institution']}")
    print("-" * 80)
    
    # 1. 登录
    print("\n[1] 登录...")
    try:
        login_resp = requests.post(f"{BASE}/api/auth/login", json={
            "phone": account['phone'],
            "name": account['name'],
            "role": "CONTESTANT"
        }, timeout=10)
        
        if login_resp.status_code != 200:
            print(f"   ❌ 登录失败: {login_resp.status_code}")
            failed_accounts.append(account)
            continue
        
        login_data = login_resp.json()['data']
        token = login_data['token']
        user_id = login_data['id']
        
        print(f"   ✅ 登录成功")
        print(f"      用户ID: {user_id}")
        print(f"      姓名: {login_data['name']}")
        print(f"      机构: {login_data.get('institutionName', '未设置')}")
        
    except Exception as e:
        print(f"   ❌ 登录异常: {e}")
        failed_accounts.append(account)
        continue
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. 获取我的报名列表
    print("\n[2] 获取报名列表...")
    try:
        reg_resp = requests.get(f"{BASE}/api/registrations/my", headers=headers, timeout=10)
        
        if reg_resp.status_code != 200:
            print(f"   ❌ 获取报名失败: {reg_resp.status_code}")
            print(f"      响应: {reg_resp.text[:200]}")
            failed_accounts.append(account)
            continue
        
        registrations = reg_resp.json()['data']
        print(f"   ✅ 获取成功，共 {len(registrations)} 个报名")
        
        # 查找对应的报名
        target_reg = next((r for r in registrations if r['id'] == account['registration_id']), None)
        
        if target_reg:
            print(f"\n   找到报名ID {account['registration_id']}:")
            print(f"      项目名称: {target_reg.get('projectName', 'N/A')}")
            print(f"      状态: {target_reg.get('status', 'N/A')}")
            print(f"      组别: {target_reg.get('groupType', 'N/A')}")
        else:
            print(f"   ⚠️  未找到预期的报名ID {account['registration_id']}")
        
    except Exception as e:
        print(f"   ❌ 获取报名异常: {e}")
        failed_accounts.append(account)
        continue
    
    # 3. 获取报名详情
    print("\n[3] 获取报名详情...")
    try:
        detail_resp = requests.get(
            f"{BASE}/api/registrations/{account['registration_id']}", 
            headers=headers, 
            timeout=10
        )
        
        if detail_resp.status_code != 200:
            print(f"   ❌ 获取详情失败: {detail_resp.status_code}")
            failed_accounts.append(account)
            continue
        
        detail_data = detail_resp.json()['data']
        registration = detail_data.get('registration', {})
        members = detail_data.get('members', [])
        
        print(f"   ✅ 详情获取成功")
        print(f"      项目名称: {registration.get('projectName', 'N/A')}")
        print(f"      状态: {registration.get('status', 'N/A')}")
        print(f"      成员数: {len(members)}")
        
        if members:
            print(f"      成员列表:")
            for m in members[:3]:  # 只显示前3个
                print(f"        - {m.get('name', 'N/A')} ({m.get('role', 'N/A')}) - {m.get('title', 'N/A')}")
        
        # 标记为成功
        successful_accounts.append({
            **account,
            'user_id': user_id,
            'status': registration.get('status'),
            'members_count': len(members)
        })
        
    except Exception as e:
        print(f"   ❌ 获取详情异常: {e}")
        failed_accounts.append(account)
        continue

# 输出测试总结
print("\n" + "="*80)
print("测试总结")
print("="*80)

print(f"\n✅ 成功: {len(successful_accounts)} 个账号")
for acc in successful_accounts:
    print(f"   - {acc['name']} ({acc['phone']}) - 报名ID {acc['registration_id']} - {acc['project']}")

if failed_accounts:
    print(f"\n❌ 失败: {len(failed_accounts)} 个账号")
    for acc in failed_accounts:
        print(f"   - {acc['name']} ({acc['phone']})")

# 生成测试账号文档
print("\n" + "="*80)
print("可用测试账号")
print("="*80)

if successful_accounts:
    print("\n以下账号可以直接使用:\n")
    for acc in successful_accounts:
        print(f"账号: {acc['name']}")
        print(f"  手机号: {acc['phone']}")
        print(f"  角色: CONTESTANT")
        print(f"  报名ID: {acc['registration_id']}")
        print(f"  项目: {acc['project']}")
        print(f"  机构: {acc['institution']}")
        print(f"  状态: {acc['status']}")
        print()
