#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import sys
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:6031"

print("步骤1: 登录...")
login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
    "phone": "13800000002",
    "password": "123456"
})
if login_resp.status_code != 200:
    print(f"❌ 登录失败: {login_resp.status_code}")
    sys.exit(1)

token = login_resp.json()['data']['token']
headers = {"Authorization": f"Bearer {token}"}
print(f"✅ 登录成功!\n")

print("步骤2: 查询舟山医院的项目列表...")
filter_resp = requests.get(
    f"{BASE_URL}/api/admin/registrations/filter",
    params={"institutionName": "舟山医院"},
    headers=headers
)

if filter_resp.status_code != 200:
    print(f"❌ API调用失败: {filter_resp.status_code}")
    sys.exit(1)

data = filter_resp.json()['data']
projects = data if isinstance(data, list) else data.get('content', [])

print(f"找到 {len(projects)} 个项目:\n")

missing_label_count = 0
for p in projects:
    method_label = p.get('methodLabel')
    status = "✅" if method_label else "❌"
    if not method_label:
        missing_label_count += 1
    print(f"{status} ID={p.get('registrationId')}: {p.get('projectName')[:45]} | methodLabel={method_label}")

print(f"\n{'✅ 全部显示正常！' if missing_label_count == 0 else f'❌ 还有 {missing_label_count} 个项目的methodLabel为空'}")
