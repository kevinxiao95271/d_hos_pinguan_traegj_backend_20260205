#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试methodLabel和subjectTypeLabel修复效果"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import requests
import time

BASE_URL = "http://localhost:6031"

# 等待服务器启动
print("等待服务器启动...")
for i in range(30):
    try:
        response = requests.get(f"{BASE_URL}/api/competitions", timeout=2)
        if response.status_code in [200, 401]:
            print(f"✅ 服务器已启动 (尝试 {i+1}/30)\n")
            break
    except:
        pass
    time.sleep(3)
else:
    print("❌ 服务器启动超时")
    sys.exit(1)

# 登录
print("登录中...")
response = requests.post(f"{BASE_URL}/api/auth/login", 
    json={
        "phone": "13900000000",
        "name": "Admin",
        "role": "OPS",
        "institutionId": 1
    })

if response.status_code != 200:
    print(f"❌ 登录失败: {response.status_code}")
    sys.exit(1)

token = response.json()['data']['token']
print("✅ 登录成功\n")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 测试filter API
print("=" * 100)
print("测试 GET /api/admin/registrations/filter")
print("=" * 100)
print()

response = requests.get(
    f"{BASE_URL}/api/admin/registrations/filter",
    params={
        "competitionId": 21,
        "institutionId": 17,  # 舟山医院
        "page": 1,
        "size": 10
    },
    headers=headers
)

if response.status_code != 200:
    print(f"❌ 请求失败: {response.status_code}")
    print(response.text)
    sys.exit(1)

data = response.json()['data']
projects = data['content']

print(f"查询到舟山医院的 {len(projects)} 个项目（第1页）\n")

has_label_count = 0
no_label_count = 0

for idx, project in enumerate(projects, 1):
    reg_id = project.get('registrationId')
    project_name = project.get('projectName', '')
    method_code = project.get('methodCode', '')
    method_label = project.get('methodLabel', '')
    subject_code = project.get('subjectTypeCode', '')
    subject_label = project.get('subjectTypeLabel', '')
    
    has_method_label = method_label and method_label.strip() != ''
    has_subject_label = subject_label and subject_label.strip() != ''
    
    if has_method_label and has_subject_label:
        has_label_count += 1
        status = "✅"
    else:
        no_label_count += 1
        status = "❌"
    
    print(f"{status} 项目 {reg_id}: {project_name[:45]}...")
    print(f"   品管工具: [{method_code}] → {method_label or '(空)'}")
    print(f"   主题类型: [{subject_code}] → {subject_label or '(空)'}")
    print()

print("=" * 100)
print(f"📊 测试结果：")
print(f"   有label的项目: {has_label_count}/{len(projects)}")
print(f"   无label的项目: {no_label_count}/{len(projects)}")

if no_label_count == 0:
    print(f"\n🎉 修复成功！所有项目都正确显示了品管工具和主题类型的label！")
else:
    print(f"\n⚠️  还有 {no_label_count} 个项目的label为空")
print("=" * 100)
