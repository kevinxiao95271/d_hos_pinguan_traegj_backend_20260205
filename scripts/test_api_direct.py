# -*- coding: utf-8 -*-
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:6031"

# 登录
login_data = {
    "phone": "13800000001",
    "name": "参赛者A",
    "title": "主任护师",
    "role": "CONTESTANT",
    "institutionId": 2
}

login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
token = login_response.json()['data']['token']

headers = {"Authorization": f"Bearer {token}"}

# 测试新API
response = requests.get(f"{BASE_URL}/api/registrations/106/reviewer-scores", headers=headers)

print(f"Status Code: {response.status_code}")
print(f"\nResponse:")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
