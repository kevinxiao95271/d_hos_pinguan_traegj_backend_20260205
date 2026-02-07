#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""展示需要修正的code映射方案"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import requests

BASE_URL = "http://localhost:6031"

# 登录
login_response = requests.post(f"{BASE_URL}/api/auth/login", 
    json={
        "phone": "13900000000",
        "name": "Admin User",
        "title": "Manager",
        "role": "OPS",
        "institutionId": 1
    })

token = login_response.json()['data']['token']
headers = {"Authorization": f"Bearer {token}"}

# 全量查询
response = requests.get(
    f"{BASE_URL}/api/admin/registrations/filter",
    params={"competitionId": 21},
    headers=headers
)

data = response.json().get('data', [])
items = data['content'] if isinstance(data, dict) and 'content' in data else data

# 收集所有有效的methodCode -> label映射
valid_mapping = {}
for item in items:
    method_code = item.get('methodCode', '')
    method_label = item.get('methodLabel', '')
    if method_code and method_label and method_label != 'None':
        valid_mapping[method_code] = method_label

print("=" * 100)
print("当前系统中有效的methodCode（从API返回中提取）")
print("=" * 100)
for code, label in sorted(valid_mapping.items()):
    print(f"  {code:20s} -> {label}")

print("\n" + "=" * 100)
print("舟山医院使用的无效code及推荐映射")
print("=" * 100)

mapping_plan = {
    'qcc': 'qc_topic',  # 品管圈 -> 品管圈-课题达成
    'benchmarking': 'method_7',  # 标杆学习 -> 标杆学习
    'process_reengineering': 'process_improve',  # 流程再造 -> 流程改造
    'system_construct': 'process_improve',  # 体系构建 -> 流程改造
}

print("\n推荐映射方案：")
for old_code, new_code in mapping_plan.items():
    new_label = valid_mapping.get(new_code, '未知')
    print(f"  {old_code:25s} -> {new_code:20s} ({new_label})")

# 统计需要修改的记录
print("\n" + "=" * 100)
print("需要修改的记录详情")
print("=" * 100)

for old_code, new_code in mapping_plan.items():
    new_label = valid_mapping.get(new_code, '未知')
    affected = [item for item in items if item.get('methodCode') == old_code]
    
    if affected:
        print(f"\n{old_code} -> {new_code} ({new_label})")
        print(f"  影响 {len(affected)} 条记录：")
        for item in affected:
            reg_id = item.get('registrationId') or item.get('id')
            project_name = item.get('projectName', '')[:50]
            print(f"    ID={reg_id}: {project_name}")

print("\n" + "=" * 100)
print("总结")
print("=" * 100)
print(f"需要修改的记录总数：{len([item for item in items if item.get('methodCode') in mapping_plan])}")
print("=" * 100)
