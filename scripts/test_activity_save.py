# -*- coding: utf-8 -*-
"""
测试活动说明保存API，重现400错误
"""
import requests
import json

BASE_URL = "http://localhost:6031/api"

print("=" * 100)
print("测试活动说明保存API")
print("=" * 100)

# 1. 登录获取token
print("\n[步骤1] 登录...")
login_response = requests.post(
    f"{BASE_URL}/auth/login-with-password",
    json={
        "phone": "13600001234",
        "password": "test001234"
    }
)

if login_response.status_code != 200:
    print(f"登录失败: {login_response.status_code}")
    print(login_response.text)
    exit(1)

login_data = login_response.json()
print(f"登录响应: {json.dumps(login_data, ensure_ascii=False, indent=2)}")

# 尝试不同的token路径
if 'token' in login_data:
    token = login_data['token']
elif 'data' in login_data and isinstance(login_data['data'], dict) and 'token' in login_data['data']:
    token = login_data['data']['token']
elif 'data' in login_data and isinstance(login_data['data'], str):
    token = login_data['data']
else:
    print(f"无法从响应中提取token")
    exit(1)

print(f"登录成功，token: {token[:20]}...")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 2. 获取用户的报名记录
print("\n[步骤2] 获取报名列表...")
registrations_response = requests.get(
    f"{BASE_URL}/registrations",
    headers=headers
)

if registrations_response.status_code != 200:
    print(f"获取报名列表失败: {registrations_response.status_code}")
    print(registrations_response.text)
    exit(1)

reg_data = registrations_response.json()
print(f"报名列表响应: {json.dumps(reg_data, ensure_ascii=False, indent=2)[:500]}...")

# 处理可能的API响应包装
if isinstance(reg_data, dict) and 'data' in reg_data:
    registrations = reg_data['data']
elif isinstance(reg_data, list):
    registrations = reg_data
else:
    registrations = []

if not registrations:
    print("没有报名记录")
    exit(1)

registration_id = registrations[0]['id']
print(f"找到报名记录 ID: {registration_id}")

# 3. 测试不同的活动说明数据
test_cases = [
    {
        "name": "完整数据",
        "data": {
            "theme": "如何缩短肾病患者脚趾感染的康复周期",
            "keywords": "肾内科,脚趾感染",
            "subjectTypeCode": "case_quality",
            "subjectTypeOther": "",
            "methodCode": "pdca",
            "methodOther": "",
            "experienceImproveCode": "appointment",
            "experienceImproveOther": "",
            "qualityTopicCode": "adverse_event_report",
            "qualityTopicOther": "",
            "avgWorkYears": 5,
            "avgAge": 30,
            "crossDepartment": False,
            "relatedToDigitalAi": False
        }
    },
    {
        "name": "缺少主题",
        "data": {
            "theme": "",  # 空字符串
            "keywords": "测试关键词",
            "subjectTypeCode": "case_quality",
            "methodCode": "pdca",
            "experienceImproveCode": "appointment",
            "qualityTopicCode": "adverse_event_report",
            "avgWorkYears": 5,
            "avgAge": 30,
            "crossDepartment": False,
            "relatedToDigitalAi": False
        }
    },
    {
        "name": "缺少必填字段",
        "data": {
            "theme": "测试主题",
            "keywords": "测试关键词"
            # 缺少其他必填字段
        }
    },
    {
        "name": "无效的code值",
        "data": {
            "theme": "测试主题",
            "keywords": "测试关键词",
            "subjectTypeCode": "invalid_code",  # 不存在的code
            "methodCode": "invalid_method",
            "experienceImproveCode": "invalid_exp",
            "qualityTopicCode": "invalid_topic",
            "avgWorkYears": 5,
            "avgAge": 30,
            "crossDepartment": False,
            "relatedToDigitalAi": False
        }
    }
]

for i, test_case in enumerate(test_cases):
    print(f"\n[测试 {i+1}] {test_case['name']}")
    print("-" * 100)
    
    response = requests.put(
        f"{BASE_URL}/registrations/{registration_id}/activity",
        headers=headers,
        json=test_case['data']
    )
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        print("保存成功！")
        result = response.json()
        if isinstance(result, dict) and 'data' in result:
            print(f"返回数据: {json.dumps(result['data'], ensure_ascii=False, indent=2)}")
        else:
            print(f"返回数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
    else:
        print(f"保存失败！")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容: {response.text}")
        
        # 尝试解析JSON错误
        try:
            error_json = response.json()
            print(f"\n错误详情（JSON）:")
            print(json.dumps(error_json, ensure_ascii=False, indent=2))
        except:
            pass

print("\n" + "=" * 100)
print("测试完成")
print("=" * 100)
