# -*- coding: utf-8 -*-
"""
直接测试活动说明保存API（不登录，查看400错误详情）
"""
import requests
import json

BASE_URL = "http://localhost:6031/api"

print("=" * 100)
print("测试活动说明保存API - 直接测试（无认证）")
print("=" * 100)

# 直接使用已知的报名ID
registration_id = 7

# 测试不同的活动说明数据
test_cases = [
    {
        "name": "完整数据 - 所有必填字段",
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
        "name": "空主题（预期400）",
        "data": {
            "theme": "",
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
        "name": "缺少methodCode（预期400）",
        "data": {
            "theme": "测试主题",
            "keywords": "测试关键词",
            "subjectTypeCode": "case_quality",
            # 缺少 methodCode
            "experienceImproveCode": "appointment",
            "qualityTopicCode": "adverse_event_report",
            "avgWorkYears": 5,
            "avgAge": 30,
            "crossDepartment": False,
            "relatedToDigitalAi": False
        }
    },
    {
        "name": "缺少avgAge（预期400）",
        "data": {
            "theme": "测试主题",
            "keywords": "测试关键词",
            "subjectTypeCode": "case_quality",
            "methodCode": "pdca",
            "experienceImproveCode": "appointment",
            "qualityTopicCode": "adverse_event_report",
            "avgWorkYears": 5,
            # 缺少 avgAge
            "crossDepartment": False,
            "relatedToDigitalAi": False
        }
    },
    {
        "name": "null值测试",
        "data": {
            "theme": "测试主题",
            "keywords": "测试关键词",
            "subjectTypeCode": "case_quality",
            "methodCode": "pdca",
            "experienceImproveCode": "appointment",
            "qualityTopicCode": "adverse_event_report",
            "avgWorkYears": None,  # null
            "avgAge": 30,
            "crossDepartment": False,
            "relatedToDigitalAi": False
        }
    }
]

for i, test_case in enumerate(test_cases):
    print(f"\n[测试 {i+1}] {test_case['name']}")
    print("-" * 100)
    print(f"请求数据: {json.dumps(test_case['data'], ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.put(
            f"{BASE_URL}/registrations/{registration_id}/activity",
            json=test_case['data'],
            timeout=10
        )
        
        print(f"\n状态码: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        
        if response.status_code == 200:
            print("✓ 保存成功！")
            try:
                result = response.json()
                print(f"返回数据: {json.dumps(result, ensure_ascii=False, indent=2)[:300]}...")
            except:
                print(f"返回内容: {response.text[:300]}...")
        elif response.status_code == 400:
            print("✗ 400 Bad Request - 验证失败")
            print(f"\n完整响应:")
            print(response.text)
            
            # 尝试解析JSON错误
            try:
                error_json = response.json()
                print(f"\n错误详情（JSON格式化）:")
                print(json.dumps(error_json, ensure_ascii=False, indent=2))
            except:
                pass
        elif response.status_code == 401:
            print("✗ 401 Unauthorized - 需要认证")
            print(f"这是预期的，因为我们没有提供token")
            break  # 如果需要认证，后面的测试也会失败，直接退出
        else:
            print(f"✗ 其他错误")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"✗ 请求异常: {str(e)}")

print("\n" + "=" * 100)
print("测试完成")
print("=" * 100)
print("\n💡 分析说明:")
print("1. 如果返回401，说明API需要认证")
print("2. 如果返回400，查看错误详情中的validation错误")
print("3. 注意检查哪些字段导致了验证失败")
