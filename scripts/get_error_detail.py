#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""获取API详细错误信息"""

import requests
import json

BASE_URL = "http://localhost:6031"

# 登录
response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "phone": "13800000041",
    "name": "CommitteeAdmin A",
    "role": "COMMITTEE_ADMIN"
})

token = response.json()['data']['token']

# 调用API并获取详细错误
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json, text/plain, */*"
}

response = requests.get(
    f"{BASE_URL}/api/admin/reviews/tasks",
    params={"competitionId": 21, "stage": "BOOK"},
    headers=headers
)

print(f"状态码: {response.status_code}")
print(f"\n响应头:")
for key, value in response.headers.items():
    print(f"  {key}: {value}")

print(f"\n响应体:")
print(response.text)

# 尝试获取HTML错误页面中的详细信息
if 'text/html' in response.headers.get('Content-Type', ''):
    print("\n检测到HTML响应，可能包含详细错误信息")
    # 查找错误信息
    import re
    error_match = re.search(r'<h1>(.*?)</h1>', response.text)
    if error_match:
        print(f"错误标题: {error_match.group(1)}")
    
    message_match = re.search(r'<div[^>]*>message</div>.*?<div[^>]*>(.*?)</div>', response.text, re.DOTALL)
    if message_match:
        print(f"错误消息: {message_match.group(1)}")
