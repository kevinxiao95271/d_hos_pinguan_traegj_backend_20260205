# -*- coding: utf-8 -*-
"""
添加缺失的"未分级"选项
"""
import requests

BASE_URL = "http://localhost:6031/api"

print("=" * 100)
print("添加缺失的医院等级选项")
print("=" * 100)

# 登录
print("\n登录组委会账号...")
login_response = requests.post(
    f"{BASE_URL}/auth/login-with-password",
    json={
        "phone": "13800000127",
        "password": "committee2026"
    },
    timeout=30
)

if login_response.status_code != 200 or not login_response.json().get('success'):
    print("登录失败！")
    exit(1)

token = login_response.json()['data']['token']
print("登录成功！")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 添加"未分级"（从机构表复制的值）
print("\n添加 '未分级' 选项...")

response = requests.post(
    f"{BASE_URL}/dictionaries",
    headers=headers,
    json={
        "type": "institution_level",
        "code": "未分级",  # 从机构表实际使用的值
        "label": "未分级",
        "status": "ACTIVE"
    },
    timeout=30
)

if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        print("  [OK] 添加成功")
    else:
        print(f"  [FAIL] {data.get('message')}")
else:
    print(f"  [FAIL] HTTP {response.status_code}")
    print(f"  Response: {response.text}")

# 验证
print("\n验证结果...")
response = requests.get(
    f"{BASE_URL}/dictionaries/institution_level",
    timeout=30
)

if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        items = data.get('data', [])
        print(f"\n现在有 {len(items)} 个医院等级选项")
        
        # 检查是否包含所有实际使用的等级
        codes = [item['code'] for item in items]
        actual_levels = ['二级', '三级', '三甲', '未分级']
        
        print("\n实际使用的等级检查:")
        for level in actual_levels:
            if level in codes:
                print(f"  [OK] {level}")
            else:
                print(f"  [X] {level} - 缺失")

print("\n" + "=" * 100)
