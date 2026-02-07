#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""通过API检查舟山医院项目数据"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import requests
import json

BASE_URL = "http://localhost:6031"

# 登录
print("登录中...")
login_response = requests.post(f"{BASE_URL}/api/auth/login", 
    json={
        "phone": "13900000000",
        "name": "Admin User",
        "title": "Manager",
        "role": "OPS",
        "institutionId": 1
    })

if login_response.status_code != 200:
    print(f"❌ 登录失败: {login_response.status_code}")
    sys.exit(1)

token = login_response.json()['data']['token']
print("✅ 登录成功\n")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 查询舟山医院的项目（institution_id=17）
print("=" * 100)
print("查询舟山医院的书审项目")
print("=" * 100)
print()

# 使用筛选API
response = requests.get(
    f"{BASE_URL}/api/admin/registrations/filter",
    params={
        "competitionId": 21,
        "institutionId": 17
    },
    headers=headers
)

if response.status_code != 200:
    print(f"❌ 查询失败: {response.status_code}")
    print(response.text)
    sys.exit(1)

data = response.json()['data']

if isinstance(data, dict) and 'content' in data:
    projects = data['content']
else:
    projects = data

print(f"找到 {len(projects)} 个舟山医院的项目\n")

missing_count = 0

for i, proj in enumerate(projects, 1):
    reg_id = proj.get('registrationId') or proj.get('id')
    project_name = proj.get('projectName', '')
    applicant = proj.get('applicantName', '')
    group_code = proj.get('groupCode', '')
    
    # 获取详细信息
    detail_response = requests.get(
        f"{BASE_URL}/api/registrations/{reg_id}",
        headers=headers
    )
    
    if detail_response.status_code == 200:
        detail = detail_response.json()['data']
        activity_info = detail.get('activityInfo', {})
        project_summary = detail.get('projectSummary', {})
        
        method_code = activity_info.get('methodCode')
        subject_type = activity_info.get('subjectTypeCode')
        theme = activity_info.get('theme')
        
        has_summary = project_summary.get('theme') is not None
        
        is_complete = method_code and subject_type and theme and has_summary
        
        status = "✅" if is_complete else "❌"
        if not is_complete:
            missing_count += 1
        
        print(f"{status} [{reg_id}] {applicant} - {project_name[:35]}... ({group_code})")
        
        if not method_code:
            print(f"      ❌ 品管工具 (methodCode): 空")
        else:
            print(f"      ✅ 品管工具: {method_code}")
            
        if not subject_type:
            print(f"      ❌ 主题类型 (subjectTypeCode): 空")
        else:
            print(f"      ✅ 主题类型: {subject_type}")
            
        if not theme:
            print(f"      ❌ 主题 (theme): 空")
        else:
            print(f"      ✅ 主题: {theme}")
            
        if not has_summary:
            print(f"      ❌ 项目总结: 空")
        else:
            print(f"      ✅ 项目总结: 有")
        
        print()
    else:
        print(f"❌ [{reg_id}] 获取详情失败: {detail_response.status_code}")
        print()

print("=" * 100)
print(f"统计: 共 {len(projects)} 个项目，缺失字段的有 {missing_count} 个")
print("=" * 100)
