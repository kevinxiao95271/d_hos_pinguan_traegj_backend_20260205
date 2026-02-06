#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""显示更新后的评委列表"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests

BASE = "http://localhost:6031"

# 登录
r = requests.post(f"{BASE}/api/auth/login", json={
    "phone":"13800000009","name":"C","role":"COMMITTEE"
})
token = r.json()['data']['token']
headers = {"Authorization": f"Bearer {token}"}

# 获取评委列表
response = requests.get(f"{BASE}/api/admin/reviewers", headers=headers)
reviewers = response.json()['data']

print("="*100)
print("评委列表（更新后）")
print("="*100)
print(f"{'ID':<5} {'姓名':<10} {'职称':<18} {'机构':<30} {'专家背景':<10} {'分组':<8}")
print("-"*100)

for r in reviewers:
    bg_map = {'MEDICAL': '医疗', 'NURSING': '护理', 'MANAGEMENT': '管理'}
    bg = bg_map.get(r.get('expertBackground'), '未设置')
    inst = r.get('institutionName') or 'N/A'
    if inst and inst != 'N/A' and len(inst) > 25:
        inst = inst[:25] + '...'
    group = r.get('reviewerGroupCode') or '未分组'
    
    print(f"{r['id']:<5} {r['name']:<10} {r['title']:<18} {inst:<30} {bg:<10} {group:<8}")

print("\n专家背景统计:")
bg_count = {}
for r in reviewers:
    bg = r.get('expertBackground') or '未设置'
    bg_map = {'MEDICAL': '医疗', 'NURSING': '护理', 'MANAGEMENT': '管理', '未设置': '未设置'}
    bg_name = bg_map.get(bg, bg)
    bg_count[bg_name] = bg_count.get(bg_name, 0) + 1

for bg, cnt in sorted(bg_count.items()):
    print(f"  {bg}: {cnt}人")

print("\n" + "="*100)
