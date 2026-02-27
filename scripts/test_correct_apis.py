# -*- coding: utf-8 -*-
"""
测试正确的API接口 - 验证submittedAt字段
"""
import requests
import json

BASE_URL = "http://localhost:6031/api"

print("=" * 100)
print("测试书审和面谈分组API - 验证submittedAt字段")
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

# 2. 测试 API 1: /admin/registrations/filter (书审和面谈列表都用这个)
print("\n" + "=" * 100)
print("[步骤2] 测试筛选接口 (书审和面谈分组列表)")
print("=" * 100)
print(f"API: GET {BASE_URL}/admin/registrations/filter?competitionId=1")

filter_response = requests.get(
    f"{BASE_URL}/admin/registrations/filter",
    params={"competitionId": 1},
    headers=headers,
    timeout=30
)

print(f"状态码: {filter_response.status_code}")

if filter_response.status_code != 200:
    print(f"[ERROR] 请求失败:")
    print(filter_response.text)
else:
    filter_data = filter_response.json()
    
    if filter_data.get('success') and 'data' in filter_data:
        items = filter_data['data']
        print(f"[OK] 返回 {len(items)} 条记录")
        
        if items:
            first_item = items[0]
            print(f"\n[验证] 第一条记录字段检查:")
            print(f"  id: {first_item.get('id', 'N/A')}")
            print(f"  registrationId: {first_item.get('registrationId', 'N/A')}")
            print(f"  projectName: {first_item.get('projectName', 'N/A')}")
            print(f"  institutionName: {first_item.get('institutionName', 'N/A')}")
            print(f"  institutionLevel: {first_item.get('institutionLevel', 'N/A')}")
            print(f"  groupType: {first_item.get('groupType', 'N/A')}")
            print(f"  groupCode: {first_item.get('groupCode', 'N/A')}")
            print(f"  submittedAt: {first_item.get('submittedAt', 'N/A')}")
            print(f"  methodLabel: {first_item.get('methodLabel', 'N/A')}")
            print(f"  subjectTypeLabel: {first_item.get('subjectTypeLabel', 'N/A')}")
            
            if 'submittedAt' in first_item:
                print(f"\n[OK] submittedAt字段存在！")
            else:
                print(f"\n[ERROR] submittedAt字段缺失！")
            
            # 统计有submittedAt的记录数
            items_with_submitted = sum(1 for item in items if item.get('submittedAt'))
            total_items = len(items)
            print(f"\n[统计]")
            print(f"  总记录数: {total_items}")
            print(f"  有submittedAt的: {items_with_submitted}")
            print(f"  覆盖率: {items_with_submitted/total_items*100:.1f}%")
            
            # 显示完整数据结构（仅第一条）
            print(f"\n[完整数据] 第一条记录:")
            print(json.dumps(first_item, ensure_ascii=False, indent=2))
        else:
            print(f"[WARN] 没有数据")
    else:
        print(f"[ERROR] API返回失败: {filter_data.get('message')}")

# 3. 测试 API 2: /api/registrations/{id} (报名详情)
print("\n" + "=" * 100)
print("[步骤3] 测试报名详情接口 (面谈详情对话框)")
print("=" * 100)

# 获取第一条报名的ID
if filter_response.status_code == 200 and filter_data.get('success'):
    items = filter_data['data']
    if items:
        first_reg_id = items[0]['registrationId']
        print(f"API: GET {BASE_URL}/registrations/{first_reg_id}")
        
        detail_response = requests.get(
            f"{BASE_URL}/registrations/{first_reg_id}",
            headers=headers,
            timeout=30
        )
        
        print(f"状态码: {detail_response.status_code}")
        
        if detail_response.status_code != 200:
            print(f"[ERROR] 请求失败:")
            print(detail_response.text)
        else:
            detail_data = detail_response.json()
            
            if detail_data.get('success') and 'data' in detail_data:
                data = detail_data['data']
                registration = data.get('registration', {})
                
                print(f"\n[验证] 报名详情字段检查:")
                print(f"  registration.id: {registration.get('id', 'N/A')}")
                print(f"  registration.projectName: {registration.get('projectName', 'N/A')}")
                print(f"  registration.status: {registration.get('status', 'N/A')}")
                print(f"  registration.submittedAt: {registration.get('submittedAt', 'N/A')}")
                print(f"  registration.createdAt: {registration.get('createdAt', 'N/A')}")
                
                if 'submittedAt' in registration:
                    print(f"\n[OK] registration.submittedAt字段存在！")
                else:
                    print(f"\n[ERROR] registration.submittedAt字段缺失！")
                
                # 显示registration对象的部分内容
                print(f"\n[registration对象]:")
                print(json.dumps({
                    'id': registration.get('id'),
                    'projectName': registration.get('projectName'),
                    'status': registration.get('status'),
                    'submittedAt': registration.get('submittedAt'),
                    'createdAt': registration.get('createdAt')
                }, ensure_ascii=False, indent=2))
            else:
                print(f"[ERROR] API返回失败: {detail_data.get('message')}")
    else:
        print("[WARN] 没有报名记录，跳过详情测试")
else:
    print("[WARN] 筛选接口失败，跳过详情测试")

print("\n" + "=" * 100)
print("测试完成")
print("=" * 100)
