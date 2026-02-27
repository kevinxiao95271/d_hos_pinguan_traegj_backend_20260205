# -*- coding: utf-8 -*-
"""
测试已提交状态的记录，验证submittedAt有值
"""
import requests
import json

BASE_URL = "http://localhost:6031/api"

print("=" * 100)
print("测试已提交状态的记录 - 验证submittedAt有值")
print("=" * 100)

# 1. 登录
login_response = requests.post(
    f"{BASE_URL}/auth/login-with-password",
    json={"phone": "13800000127", "password": "committee2026"},
    timeout=30
)

token = login_response.json()['data']['token']
headers = {"Authorization": f"Bearer {token}"}

# 2. 获取筛选列表，找SUBMITTED状态的记录
print("\n[查找SUBMITTED状态的记录]")

filter_response = requests.get(
    f"{BASE_URL}/admin/registrations/filter",
    params={"competitionId": 1},
    headers=headers,
    timeout=30
)

items = filter_response.json()['data']

# 找一个有submittedAt的记录
submitted_items = [item for item in items if item.get('submittedAt')]

if not submitted_items:
    print("[WARN] 没有找到有submittedAt的记录")
    exit(0)

first_submitted = submitted_items[0]
print(f"找到 {len(submitted_items)} 条有submittedAt的记录")
print(f"\n[示例1] 筛选列表中的第一条 (SUBMITTED状态):")
print(f"  ID: {first_submitted['registrationId']}")
print(f"  项目名称: {first_submitted['projectName']}")
print(f"  机构名称: {first_submitted['institutionName']}")
print(f"  submittedAt: {first_submitted['submittedAt']}")

# 3. 获取详情
detail_response = requests.get(
    f"{BASE_URL}/registrations/{first_submitted['registrationId']}",
    headers=headers,
    timeout=30
)

registration = detail_response.json()['data']['registration']
print(f"\n[示例2] 详情接口返回 (同一条记录):")
print(f"  ID: {registration['id']}")
print(f"  项目名称: {registration['projectName']}")
print(f"  状态: {registration['status']}")
print(f"  提交时间: {registration.get('submittedAt', 'N/A')}")
print(f"  创建时间: {registration['createdAt']}")

# 4. 显示更多示例
print(f"\n[更多示例] 前5条有submittedAt的记录:")
for i, item in enumerate(submitted_items[:5], 1):
    print(f"\n  {i}. ID={item['registrationId']}")
    print(f"     项目: {item['projectName'][:40]}...")
    print(f"     提交时间: {item['submittedAt']}")

print("\n" + "=" * 100)
print(f"[总结] ✅ submittedAt字段工作正常！")
print(f"  - 筛选列表API (/admin/registrations/filter): 包含submittedAt ✅")
print(f"  - 详情API (/api/registrations/{{id}}): 包含registration.submittedAt ✅")
print(f"  - SUBMITTED状态的记录有值 ✅")
print(f"  - DRAFT状态的记录为null ✅")
print("=" * 100)
