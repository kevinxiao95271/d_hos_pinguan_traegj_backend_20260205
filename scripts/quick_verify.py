#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""快速验证核心API"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests, json

BASE = "http://localhost:6031"

# 登录
r = requests.post(f"{BASE}/api/auth/login", json={"phone":"13800000009","name":"C","title":"C","role":"COMMITTEE"})
token = r.json()['data']['token']
h = {"Authorization": f"Bearer {token}"}

print("="*60)
print("核心API验证")
print("="*60)

# 验证
print(f"\n1. 机构: {len(requests.get(f'{BASE}/api/institutions', headers=h).json()['data'])} 个")
print(f"2. 赛事: {len(requests.get(f'{BASE}/api/competitions', headers=h).json()['data'])} 个")
print(f"3. 评委: {len(requests.get(f'{BASE}/api/admin/reviewers', headers=h).json()['data'])} 个")

# 示例数据
inst = requests.get(f'{BASE}/api/institutions', headers=h).json()['data'][0]
comp = requests.get(f'{BASE}/api/competitions', headers=h).json()['data'][0]
revs = requests.get(f'{BASE}/api/admin/reviewers', headers=h).json()['data'][:2]

print("\n" + "="*60)
print("示例数据已导出")
print("="*60)

with open('API示例数据.json', 'w', encoding='utf-8') as f:
    json.dump({
        "login": r.json(),
        "institution_example": inst,
        "competition_example": comp,
        "reviewer_examples": revs,
        "token_format": "Bearer " + token[:30] + "..."
    }, f, ensure_ascii=False, indent=2)

print("\n文件: API示例数据.json")
print("文件: API开发指引文档.md")
print("文件: 评委数据报告.md")
