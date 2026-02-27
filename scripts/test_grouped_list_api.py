# -*- coding: utf-8 -*-
"""
测试分组列表API，验证submittedAt字段是否返回
"""
import requests
import json

BASE_URL = "http://localhost:6031/api"

print("=" * 100)
print("测试分组列表API - 验证submittedAt字段")
print("=" * 100)

# 1. 登录获取token
print("\n[步骤1] 登录组委会管理员账号...")

login_response = requests.post(
    f"{BASE_URL}/auth/login-with-password",
    json={
        "phone": "13800000127",
        "password": "committee2026"
    },
    timeout=30
)

if login_response.status_code != 200:
    print(f"[ERROR] 登录失败: {login_response.status_code}")
    print(login_response.text)
    exit(1)

login_data = login_response.json()
if not login_data.get('success'):
    print(f"[ERROR] 登录失败: {login_data.get('message')}")
    exit(1)

token = login_data['data']['token']
print(f"[OK] 登录成功: {login_data['data']['name']}")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 2. 测试书审分组列表
print("\n[步骤2] 测试书审分组列表...")
print(f"API: GET {BASE_URL}/admin/registrations/book-review-groups?competitionId=1")

book_response = requests.get(
    f"{BASE_URL}/admin/registrations/book-review-groups",
    params={"competitionId": 1},
    headers=headers,
    timeout=30
)

print(f"状态码: {book_response.status_code}")

if book_response.status_code != 200:
    print(f"[ERROR] 请求失败:")
    print(book_response.text)
else:
    book_data = book_response.json()
    
    if book_data.get('success') and 'data' in book_data:
        groups = book_data['data']
        print(f"[OK] 返回 {len(groups)} 个分组")
        
        # 检查第一个分组的第一条记录
        if groups and len(groups) > 0 and groups[0]['items']:
            first_item = groups[0]['items'][0]
            print(f"\n[验证] 第一条记录字段检查:")
            print(f"  groupCode: {first_item.get('groupCode', 'N/A')}")
            print(f"  registrationId: {first_item.get('registrationId', 'N/A')}")
            print(f"  projectName: {first_item.get('projectName', 'N/A')}")
            print(f"  institutionName: {first_item.get('institutionName', 'N/A')}")
            print(f"  institutionLevel: {first_item.get('institutionLevel', 'N/A')}")
            print(f"  submittedAt: {first_item.get('submittedAt', 'N/A')}")
            
            if 'submittedAt' in first_item:
                print(f"\n[OK] submittedAt字段存在！")
            else:
                print(f"\n[ERROR] submittedAt字段缺失！")
            
            # 显示完整数据结构（仅第一条）
            print(f"\n[完整数据] 第一条记录:")
            print(json.dumps(first_item, ensure_ascii=False, indent=2))
        else:
            print(f"[WARN] 没有分组数据")
    else:
        print(f"[ERROR] API返回失败: {book_data.get('message')}")

# 3. 测试面谈分组列表
print("\n" + "=" * 100)
print("[步骤3] 测试面谈分组列表...")
print(f"API: GET {BASE_URL}/admin/registrations/interview-groups?competitionId=1")

interview_response = requests.get(
    f"{BASE_URL}/admin/registrations/interview-groups",
    params={"competitionId": 1},
    headers=headers,
    timeout=30
)

print(f"状态码: {interview_response.status_code}")

if interview_response.status_code != 200:
    print(f"[ERROR] 请求失败:")
    print(interview_response.text)
else:
    interview_data = interview_response.json()
    
    if interview_data.get('success') and 'data' in interview_data:
        groups = interview_data['data']
        print(f"[OK] 返回 {len(groups)} 个分组")
        
        # 检查第一个分组的第一条记录
        if groups and len(groups) > 0 and groups[0]['items']:
            first_item = groups[0]['items'][0]
            print(f"\n[验证] 第一条记录字段检查:")
            print(f"  groupCode: {first_item.get('groupCode', 'N/A')}")
            print(f"  registrationId: {first_item.get('registrationId', 'N/A')}")
            print(f"  projectName: {first_item.get('projectName', 'N/A')}")
            print(f"  institutionName: {first_item.get('institutionName', 'N/A')}")
            print(f"  institutionLevel: {first_item.get('institutionLevel', 'N/A')}")
            print(f"  submittedAt: {first_item.get('submittedAt', 'N/A')}")
            
            if 'submittedAt' in first_item:
                print(f"\n[OK] submittedAt字段存在！")
            else:
                print(f"\n[ERROR] submittedAt字段缺失！")
            
            # 统计有submittedAt的记录数
            items_with_submitted = sum(1 for item in groups[0]['items'] if item.get('submittedAt'))
            total_items = len(groups[0]['items'])
            print(f"\n[统计] 第一个分组中:")
            print(f"  总记录数: {total_items}")
            print(f"  有submittedAt的: {items_with_submitted}")
            print(f"  覆盖率: {items_with_submitted/total_items*100:.1f}%")
        else:
            print(f"[WARN] 没有分组数据")
    else:
        print(f"[ERROR] API返回失败: {interview_data.get('message')}")

print("\n" + "=" * 100)
print("测试完成")
print("=" * 100)
