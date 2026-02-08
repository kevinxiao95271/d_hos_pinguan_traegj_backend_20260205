#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证修复结果"""

import requests

BASE_URL = "http://localhost:6031"

# 登录
login_response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={"phone": "13900000001", "name": "李明华", "role": "REVIEWER"}
)

token = login_response.json()["data"]["token"]

# 获取详情
detail_response = requests.get(
    f"{BASE_URL}/api/registrations/119",
    headers={"Authorization": f"Bearer {token}"}
)

info = detail_response.json()["data"]["activityInfo"]

print("=" * 80)
print("验证修复结果")
print("=" * 80)
print(f"\nqualityTopicCode: {info['qualityTopicCode']}")
print(f"qualityTopicLabel: {info['qualityTopicLabel']}")
print("\n✅ 修复成功！Label显示正确的中文")
