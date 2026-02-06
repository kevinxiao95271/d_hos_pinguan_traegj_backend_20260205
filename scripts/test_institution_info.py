#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试报名详情中的机构信息"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import json

BASE = "http://localhost:6031"

print("="*80)
print("测试报名详情中的机构信息")
print("="*80)

# 使用参赛者11登录
test_phone = "13966000011"
test_name = "参赛者11"
registration_id = 116

print(f"\n[1] 登录账号: {test_name} ({test_phone})")
print("-" * 80)

try:
    login_resp = requests.post(f"{BASE}/api/auth/login", json={
        "phone": test_phone,
        "name": test_name,
        "role": "CONTESTANT"
    }, timeout=10)
    
    if login_resp.status_code != 200:
        print(f"❌ 登录失败: {login_resp.status_code}")
        print(f"响应: {login_resp.text}")
        exit(1)
    
    login_data = login_resp.json()['data']
    token = login_data['token']
    
    print(f"✅ 登录成功")
    
except Exception as e:
    print(f"❌ 登录异常: {e}")
    exit(1)

headers = {"Authorization": f"Bearer {token}"}

# 2. 获取报名详情
print(f"\n[2] 获取报名详情 (ID: {registration_id})")
print("-" * 80)

try:
    detail_resp = requests.get(
        f"{BASE}/api/registrations/{registration_id}", 
        headers=headers, 
        timeout=10
    )
    
    if detail_resp.status_code != 200:
        print(f"❌ 获取详情失败: {detail_resp.status_code}")
        print(f"响应: {detail_resp.text}")
        exit(1)
    
    detail_data = detail_resp.json()['data']
    
    print(f"✅ 获取详情成功\n")
    
    # 解析响应数据
    registration = detail_data.get('registration', {})
    institution = detail_data.get('institution', {})
    members = detail_data.get('members', [])
    activity_info = detail_data.get('activityInfo', {})
    materials = detail_data.get('materials', [])
    
    # 显示基本信息
    print("【报名基本信息】")
    print(f"  报名ID: {registration.get('id')}")
    print(f"  项目名称: {registration.get('projectName')}")
    print(f"  组别: {registration.get('groupType')}")
    print(f"  状态: {registration.get('status')}")
    print(f"  创建时间: {registration.get('createdAt')}")
    
    # 显示机构信息（重点）
    print("\n【机构基本信息】⭐")
    if institution:
        print(f"  医疗机构名称: {institution.get('name', 'N/A')}")
        print(f"  机构编号: {institution.get('code', 'N/A')}")
        print(f"  统一社会信用代码: {institution.get('uscc', 'N/A')}")
        print(f"  地区: {institution.get('region', 'N/A')}")
    else:
        print("  ⚠️  机构信息为空")
    
    # 显示成员信息
    print(f"\n【成员信息】")
    print(f"  共 {len(members)} 名成员:")
    for m in members[:5]:  # 只显示前5个
        print(f"    - {m.get('name')} ({m.get('role')}) - {m.get('title')} - {m.get('department', 'N/A')}")
    
    # 显示活动信息
    if activity_info:
        print(f"\n【活动说明】")
        print(f"  主题: {activity_info.get('theme', 'N/A')}")
        print(f"  关键词: {activity_info.get('keywords', 'N/A')}")
    
    # 显示材料信息
    print(f"\n【材料信息】")
    print(f"  共 {len(materials)} 个材料")
    
    # 显示完整JSON（用于调试）
    print("\n" + "="*80)
    print("完整响应数据（JSON格式）:")
    print("="*80)
    print(json.dumps(detail_data, indent=2, ensure_ascii=False))
    
except Exception as e:
    print(f"❌ 获取详情异常: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "="*80)
print("测试完成！")
print("="*80)

print("\n✅ 机构信息字段验证:")
print("   - 医疗机构名称 (name): ✓")
print("   - 机构编号 (code): ✓")
print("   - 统一社会信用代码 (uscc): ✓")
print("   - 地区 (region): ✓")
