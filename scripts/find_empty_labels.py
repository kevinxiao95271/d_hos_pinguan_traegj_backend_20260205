#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""找出methodLabel为空的记录"""
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

print("=" * 100)
print("methodLabel为空的记录")
print("=" * 100)

empty_count = 0
for item in items:
    method_label = item.get('methodLabel', '')
    if not method_label or not method_label.strip():
        empty_count += 1
        reg_id = item.get('registrationId') or item.get('id')
        project_name = item.get('projectName', 'N/A')
        method_code = item.get('methodCode', '')
        institution = item.get('institutionName', 'N/A')
        
        print(f"\n[{empty_count}] ID={reg_id}: {project_name}")
        print(f"    机构: {institution}")
        print(f"    methodCode='{method_code}' -> methodLabel='{method_label}' (空)")

print(f"\n总共 {empty_count} 条记录的methodLabel为空")
print("=" * 100)

# 看看这些methodCode在数据库的字典表中是否存在
print("\n检查这些methodCode...")
unique_codes = set()
for item in items:
    method_label = item.get('methodLabel', '')
    if not method_label or not method_label.strip():
        method_code = item.get('methodCode', '')
        if method_code:
            unique_codes.add(method_code)

if unique_codes:
    print(f"\n这些记录的methodCode有: {sorted(unique_codes)}")
    print("\n这说明：这些记录有methodCode，但找不到对应的label")
else:
    print("\n这些记录的methodCode都是空的，所以methodLabel也是空的")
