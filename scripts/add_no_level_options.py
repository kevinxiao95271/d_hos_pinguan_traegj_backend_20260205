# -*- coding: utf-8 -*-
"""
添加无等级相关的选项到字典表
按照Excel表中的原始命名：无定级、无级别、无等级
"""
import requests

BASE_URL = "http://localhost:6031/api"

print("=" * 100)
print("添加无等级相关选项")
print("=" * 100)

# 1. 登录
print("\n[步骤1] 登录管理员账号...")
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

# 2. 获取当前字典
print("\n[步骤2] 获取当前机构等级字典...")
response = requests.get(f"{BASE_URL}/dictionaries/institution_level", timeout=30)

if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        current_items = data.get('data', [])
        current_codes = [item['code'] for item in current_items]
        
        print(f"当前字典中有 {len(current_items)} 个等级:")
        for item in current_items:
            print(f"  - {item['code']}")

# 3. 定义要添加的选项（按Excel原样）
print("\n[步骤3] 定义要添加的选项...")
to_add = [
    {"code": "无定级", "label": "无定级"},
    {"code": "无级别", "label": "无级别"},
    {"code": "无等级", "label": "无等级"}  # 对应Excel中的空值
]

print("要添加的选项:")
for item in to_add:
    print(f"  - {item['code']}")

# 检查哪些需要添加
need_add = [item for item in to_add if item['code'] not in current_codes]

if not need_add:
    print("\n[OK] 所有选项都已存在，无需添加")
    exit(0)

print(f"\n实际需要添加 {len(need_add)} 个:")
for item in need_add:
    print(f"  - {item['code']}")

# 4. 添加选项
print("\n[步骤4] 添加选项到字典表...")
print("-" * 100)

added_count = 0
failed_count = 0

for item in need_add:
    try:
        response = requests.post(
            f"{BASE_URL}/dictionaries",
            headers=headers,
            json={
                "type": "institution_level",
                "code": item['code'],
                "label": item['label'],
                "status": "ACTIVE"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"  [OK] 已添加: {item['code']}")
                added_count += 1
            else:
                print(f"  [FAIL] 添加失败: {item['code']} - {data.get('message')}")
                failed_count += 1
        else:
            print(f"  [FAIL] 添加失败: {item['code']} - HTTP {response.status_code}")
            failed_count += 1
    except Exception as e:
        print(f"  [ERROR] 添加出错: {item['code']} - {e}")
        failed_count += 1

print(f"\n添加结果: 成功 {added_count} 个, 失败 {failed_count} 个")

# 5. 验证结果
print("\n[步骤5] 验证最终结果...")
print("=" * 100)

response = requests.get(f"{BASE_URL}/dictionaries/institution_level", timeout=30)

if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        final_items = data.get('data', [])
        
        print(f"\n最终字典表中的等级 ({len(final_items)} 个):")
        for item in final_items:
            print(f"  - {item['code']:<15} (label: {item['label']})")
        
        # 检查是否包含所有需要的等级
        expected = ['一级', '二级', '三级', '无定级', '无级别', '无等级']
        final_codes = [item['code'] for item in final_items]
        
        print(f"\n[检查] 所需等级是否齐全:")
        all_present = True
        for level in expected:
            if level in final_codes:
                print(f"  [OK] {level}")
            else:
                print(f"  [X] {level} - 缺失")
                all_present = False
        
        if all_present:
            print(f"\n[成功] 所有等级选项已齐全！")
            print(f"\n前端下拉框将显示 {len(final_items)} 个选项:")
            print(f"  - 一级 (223个机构)")
            print(f"  - 二级 (253个机构)")
            print(f"  - 三级 (164个机构)")
            print(f"  - 无定级 (根据Excel数据)")
            print(f"  - 无级别 (根据Excel数据)")
            print(f"  - 无等级 (对应Excel空值，约35433个机构)")

print("\n" + "=" * 100)
print("完成")
print("=" * 100)
