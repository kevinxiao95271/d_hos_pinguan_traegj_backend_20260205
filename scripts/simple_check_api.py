#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""简单测试：全量查询API返回的数据"""
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
    print(f"登录失败: {login_response.status_code}")
    sys.exit(1)

token = login_response.json()['data']['token']
print("登录成功\n")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 全量查询 - 只传competitionId=21，不传其他filter
print("=" * 100)
print("全量查询 competitionId=21，不带任何filter")
print("=" * 100)

response = requests.get(
    f"{BASE_URL}/api/admin/registrations/filter",
    params={"competitionId": 21},
    headers=headers
)

print(f"响应状态码: {response.status_code}")

if response.status_code != 200:
    print(f"查询失败: {response.text}")
    sys.exit(1)

result = response.json()
data = result.get('data', [])

# 处理分页数据
if isinstance(data, dict) and 'content' in data:
    items = data['content']
    print(f"\n分页数据: 总记录数={data.get('totalCount', 'N/A')}, 当前页记录数={len(items)}")
else:
    items = data
    print(f"\n非分页数据: 记录数={len(items)}")

# 统计
total = len(items)
has_method_label_count = 0
has_subject_label_count = 0
empty_both_count = 0
has_both_count = 0

print(f"\n总共 {total} 条记录\n")

# 详细分析前20条
print("=" * 100)
print("详细数据（前20条）")
print("=" * 100)

for i, item in enumerate(items[:20], 1):
    reg_id = item.get('registrationId') or item.get('id')
    project_name = item.get('projectName', 'N/A')[:40]
    institution = item.get('institutionName', 'N/A')
    method_code = item.get('methodCode', '')
    method_label = item.get('methodLabel', '')
    subject_code = item.get('subjectTypeCode', '')
    subject_label = item.get('subjectTypeLabel', '')
    
    # 统计
    if method_label and method_label.strip():
        has_method_label_count += 1
    if subject_label and subject_label.strip():
        has_subject_label_count += 1
    if (not method_label or not method_label.strip()) and (not subject_label or not subject_label.strip()):
        empty_both_count += 1
    if (method_label and method_label.strip()) and (subject_label and subject_label.strip()):
        has_both_count += 1
    
    print(f"\n[{i}] ID={reg_id}: {project_name}")
    print(f"    机构: {institution}")
    print(f"    methodCode='{method_code}' -> methodLabel='{method_label}'")
    print(f"    subjectCode='{subject_code}' -> subjectLabel='{subject_label}'")

# 全部统计（包括所有记录，不只是前20条）
for item in items[20:]:
    method_label = item.get('methodLabel', '')
    subject_label = item.get('subjectTypeLabel', '')
    
    if method_label and method_label.strip():
        has_method_label_count += 1
    if subject_label and subject_label.strip():
        has_subject_label_count += 1
    if (not method_label or not method_label.strip()) and (not subject_label or not subject_label.strip()):
        empty_both_count += 1
    if (method_label and method_label.strip()) and (subject_label and subject_label.strip()):
        has_both_count += 1

print("\n" + "=" * 100)
print("统计汇总（全部记录）")
print("=" * 100)
print(f"总记录数: {total}")
print(f"有 methodLabel 的记录: {has_method_label_count} ({has_method_label_count*100//total if total > 0 else 0}%)")
print(f"有 subjectTypeLabel 的记录: {has_subject_label_count} ({has_subject_label_count*100//total if total > 0 else 0}%)")
print(f"两个label都有的记录: {has_both_count} ({has_both_count*100//total if total > 0 else 0}%)")
print(f"两个label都为空的记录: {empty_both_count} ({empty_both_count*100//total if total > 0 else 0}%)")
print("=" * 100)
