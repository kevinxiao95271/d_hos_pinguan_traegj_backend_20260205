# -*- coding: utf-8 -*-
"""
测试登录时是否返回默认赛事ID
"""
import requests
import json

BASE_URL = "http://localhost:6031/api"

print("=" * 100)
print("测试登录接口 - 验证默认赛事功能")
print("=" * 100)

# 1. 先获取最新赛事（验证API）
print("\n[1] 获取最新赛事")
response = requests.get(f"{BASE_URL}/competitions/latest", timeout=10)
print(f"状态码: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        latest = data['data']
        print(f"[OK] Latest competition: ID={latest['id']}, Name={latest['name']}")
        expected_comp_id = latest['id']
        expected_comp_name = latest['name']
    else:
        print(f"[FAIL] API returned failure: {data.get('message')}")
        expected_comp_id = None
        expected_comp_name = None
else:
    print(f"[FAIL] Request failed: {response.status_code}")
    expected_comp_id = None
    expected_comp_name = None

# 2. 测试组委会账号登录
print("\n[2] 测试组委会账号登录（13800000127 / committee2026）")
response = requests.post(
    f"{BASE_URL}/auth/login-with-password",
    json={
        "phone": "13800000127",
        "password": "committee2026"
    },
    timeout=10
)

print(f"状态码: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        user_info = data['data']
        print(f"\n[OK] Login successful!")
        print(f"  User ID: {user_info['id']}")
        print(f"  Phone: {user_info['phone']}")
        print(f"  Name: {user_info['name']}")
        print(f"  Role: {user_info['role']}")
        print(f"  Current Competition ID: {user_info.get('currentCompetitionId', 'NOT SET')}")
        print(f"  Current Competition Name: {user_info.get('currentCompetitionName', 'NOT SET')}")
        
        # 验证是否正确返回了最新赛事
        if user_info.get('currentCompetitionId') == expected_comp_id:
            print(f"\n[SUCCESS] Default competition is correctly set!")
            print(f"  Expected: ID={expected_comp_id}, Name={expected_comp_name}")
            print(f"  Actual: ID={user_info.get('currentCompetitionId')}, Name={user_info.get('currentCompetitionName')}")
        elif user_info.get('currentCompetitionId') is None:
            print(f"\n[WARNING] currentCompetitionId is NULL (no competitions in database?)")
        else:
            print(f"\n[MISMATCH] Competition ID does not match!")
            print(f"  Expected: {expected_comp_id}")
            print(f"  Actual: {user_info.get('currentCompetitionId')}")
    else:
        print(f"[FAIL] Login failed: {data.get('message')}")
else:
    print(f"[FAIL] Request failed: {response.status_code}")
    print(response.text)

# 3. 测试其他角色的登录（参赛者）
print("\n[3] 测试参赛者账号登录（验证所有角色都能获取默认赛事）")
response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "phone": "13800000001",
        "name": "测试参赛者",
        "role": "CONTESTANT"
    },
    timeout=10
)

if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        user_info = data['data']
        print(f"[OK] Contestant login successful")
        print(f"  Current Competition ID: {user_info.get('currentCompetitionId', 'NOT SET')}")
        print(f"  Current Competition Name: {user_info.get('currentCompetitionName', 'NOT SET')}")
    else:
        print(f"[FAIL] {data.get('message')}")
else:
    print(f"[FAIL] Request failed: {response.status_code}")

print("\n" + "=" * 100)
print("测试完成！")
print("=" * 100)
print("\n前端使用指引:")
print("1. 登录后从响应中获取 currentCompetitionId 和 currentCompetitionName")
print("2. 将这两个字段保存到前端状态管理（如 localStorage 或 Vuex）")
print("3. 前端无需再弹出'赛事不存在'提示，直接使用 currentCompetitionId")
print("4. 如果用户需要切换赛事，可以通过赛事选择器修改")
