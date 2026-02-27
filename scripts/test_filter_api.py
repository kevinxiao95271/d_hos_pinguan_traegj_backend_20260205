# -*- coding: utf-8 -*-
"""
测试 GET /api/admin/registrations/filter API
验证methodLabel和subjectTypeLabel是否返回中文label而不是code
"""
import requests
import json

BASE_URL = "http://localhost:6031/api"

print("=" * 100)
print("测试报名筛选API（验证label返回）")
print("=" * 100)

# 1. 登录获取token（使用组委会账号）
print("\n[步骤1] 登录组委会账号...")

login_response = requests.post(
    f"{BASE_URL}/auth/login-with-password",
    json={
        "phone": "13800000127",
        "password": "committee2026"
    },
    timeout=30
)

if login_response.status_code != 200:
    print(f"登录失败: {login_response.status_code}")
    print(login_response.text)
    exit(1)

login_data = login_response.json()

if login_data.get('success') != True:
    print(f"登录失败: {login_data.get('message')}")
    exit(1)

token = login_data['data']['token']
print(f"登录成功！")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 2. 调用筛选接口
print("\n[步骤2] 调用报名筛选接口...")
print(f"API: GET {BASE_URL}/admin/registrations/filter?competitionId=1")

filter_response = requests.get(
    f"{BASE_URL}/admin/registrations/filter",
    headers=headers,
    params={"competitionId": 1},
    timeout=30
)

print(f"状态码: {filter_response.status_code}")

if filter_response.status_code != 200:
    print(f"请求失败:")
    print(filter_response.text)
    exit(1)

filter_data = filter_response.json()

# 3. 解析并验证数据
print("\n" + "=" * 100)
print("数据验证")
print("=" * 100)

if filter_data.get('success') == True and 'data' in filter_data:
    items = filter_data['data']
elif isinstance(filter_data, list):
    items = filter_data
else:
    print("无法解析响应数据")
    exit(1)

print(f"\n总记录数: {len(items)}")

if len(items) == 0:
    print("没有返回数据")
    exit(0)

# 4. 检查前10条记录的label
print(f"\n前10条记录验证:")
print(f"{'序号':<4} {'项目名称':<40} {'品管工具(methodLabel)':<30} {'主题类型(subjectTypeLabel)':<30} {'状态'}")
print("-" * 140)

code_count = 0
label_count = 0

for i, item in enumerate(items[:10], 1):
    project_name = item.get('projectName', 'N/A')[:38]
    method_label = item.get('methodLabel', 'N/A')
    subject_label = item.get('subjectTypeLabel', 'N/A')
    
    # 检查是否是code格式（包含下划线或纯数字）
    is_method_code = method_label and ('_' in method_label or method_label.replace('method', '').isdigit())
    is_subject_code = subject_label and ('_' in subject_label or subject_label.replace('subject', '').isdigit())
    
    if is_method_code or is_subject_code:
        status = "[错误-仍是code]"
        code_count += 1
    else:
        status = "[正确-已转为label]"
        label_count += 1
    
    print(f"{i:<4} {project_name:<40} {method_label:<30} {subject_label:<30} {status}")

# 5. 统计结果
print("\n" + "=" * 100)
print("验证结果统计")
print("=" * 100)

print(f"\n检查的记录数: {min(10, len(items))}")
print(f"  正确（返回label）: {label_count} 条")
print(f"  错误（仍是code）: {code_count} 条")

if code_count == 0:
    print(f"\n[成功] 所有品管工具和主题类型都已正确返回中文label！")
else:
    print(f"\n[失败] 还有 {code_count} 条记录返回的是code而不是label")

# 6. 显示完整的第一条记录
if len(items) > 0:
    print(f"\n完整的第一条记录（JSON格式）:")
    print(json.dumps(items[0], ensure_ascii=False, indent=2))

print("\n" + "=" * 100)
print("测试完成！")
print("=" * 100)
