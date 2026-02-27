# -*- coding: utf-8 -*-
"""
初始化医院等级字典数据
"""
import requests

BASE_URL = "http://localhost:6031/api"

print("=" * 100)
print("初始化医院等级字典数据")
print("=" * 100)

# 1. 登录管理员账号
print("\n[步骤1] 登录管理员账号...")

login_response = requests.post(
    f"{BASE_URL}/auth/login-with-password",
    json={
        "phone": "13800000001",
        "password": "admin123"
    },
    timeout=30
)

if login_response.status_code != 200 or not login_response.json().get('success'):
    print("登录失败，尝试组委会账号...")
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

# 2. 定义医院等级字典数据（根据实际使用情况）
print("\n[步骤2] 准备医院等级字典数据...")

# 基于机构表实际使用的等级值
institution_levels = [
    {"code": "三甲", "label": "三级甲等", "sort": 1},
    {"code": "三乙", "label": "三级乙等", "sort": 2},
    {"code": "三丙", "label": "三级丙等", "sort": 3},
    {"code": "三级", "label": "三级", "sort": 4},
    {"code": "二甲", "label": "二级甲等", "sort": 5},
    {"code": "二乙", "label": "二级乙等", "sort": 6},
    {"code": "二级", "label": "二级", "sort": 7},
    {"code": "一甲", "label": "一级甲等", "sort": 8},
    {"code": "一乙", "label": "一级乙等", "sort": 9},
    {"code": "一级", "label": "一级", "sort": 10},
    {"code": "未分级", "label": "未分级", "sort": 99},
]

print(f"准备添加 {len(institution_levels)} 个医院等级选项")

# 3. 添加字典数据
print("\n[步骤3] 添加字典数据...")
print("-" * 100)

success_count = 0
error_count = 0

for level in institution_levels:
    try:
        response = requests.post(
            f"{BASE_URL}/dictionaries",
            headers=headers,
            json={
                "type": "institution_level",
                "code": level["code"],
                "label": level["label"],
                "status": "ACTIVE"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"  [OK] {level['code']:<10} -> {level['label']}")
                success_count += 1
            else:
                print(f"  [FAIL] {level['code']:<10} - {data.get('message')}")
                error_count += 1
        else:
            print(f"  [FAIL] {level['code']:<10} - HTTP {response.status_code}")
            error_count += 1
            
    except Exception as e:
        print(f"  [ERROR] {level['code']:<10} - {e}")
        error_count += 1

# 4. 验证结果
print(f"\n[步骤4] 验证结果...")
print("-" * 100)

response = requests.get(
    f"{BASE_URL}/dictionaries/institution_level",
    timeout=30
)

if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        items = data.get('data', [])
        print(f"\n字典表中现有 {len(items)} 个医院等级选项:")
        for item in items:
            print(f"  code: {item['code']:<10} label: {item['label']:<15} status: {item['status']}")

print("\n" + "=" * 100)
print(f"总结: 成功 {success_count} 个, 失败 {error_count} 个")
print("=" * 100)
