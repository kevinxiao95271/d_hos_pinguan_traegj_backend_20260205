#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试所有4个Label字段是否正确返回
"""

import requests
import json

BASE_URL = "http://localhost:6031"

def test_registration_detail():
    """测试报名详情接口 - 验证4个Label字段"""
    
    print("=" * 80)
    print("测试报名详情接口 - 验证4个Label字段")
    print("=" * 80)
    
    # 使用评委账号登录
    login_data = {
        "phone": "13900000001",
        "name": "李明华",
        "role": "REVIEWER"
    }
    
    print("\n1. 登录评委账号...")
    login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ 登录失败: {login_response.status_code}")
        print(login_response.text)
        return
    
    login_result = login_response.json()
    if not login_result.get("success"):
        print(f"❌ 登录失败: {login_result}")
        return
    
    token = login_result["data"]["token"]
    print(f"✅ 登录成功，Token: {token[:20]}...")
    
    # 获取报名详情
    registration_id = 119
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n2. 获取报名详情 (ID: {registration_id})...")
    detail_response = requests.get(
        f"{BASE_URL}/api/registrations/{registration_id}",
        headers=headers
    )
    
    if detail_response.status_code != 200:
        print(f"❌ 获取详情失败: {detail_response.status_code}")
        print(detail_response.text)
        return
    
    detail_result = detail_response.json()
    if not detail_result.get("success"):
        print(f"❌ 获取详情失败: {detail_result}")
        return
    
    print("✅ 获取详情成功")
    
    # 检查activityInfo
    activity_info = detail_result["data"].get("activityInfo")
    
    if not activity_info:
        print("\n❌ activityInfo 为空")
        return
    
    print("\n" + "=" * 80)
    print("活动信息字段验证")
    print("=" * 80)
    
    # 验证4个Code字段和对应的Label字段
    fields_to_check = [
        ("subjectTypeCode", "subjectTypeLabel", "主题类型"),
        ("methodCode", "methodLabel", "运用手法"),
        ("experienceImproveCode", "experienceImproveLabel", "改善就医环境"),
        ("qualityTopicCode", "qualityTopicLabel", "医疗质量相关主题")
    ]
    
    all_passed = True
    
    for code_field, label_field, field_name in fields_to_check:
        code_value = activity_info.get(code_field)
        label_value = activity_info.get(label_field)
        
        print(f"\n【{field_name}】")
        print(f"  {code_field}: {code_value}")
        print(f"  {label_field}: {label_value}")
        
        if code_value and label_value:
            print(f"  ✅ Code和Label都存在")
        elif code_value and not label_value:
            print(f"  ❌ Code存在但Label缺失")
            all_passed = False
        elif not code_value and not label_value:
            print(f"  ⚠️  Code和Label都为空（可能未填写）")
        else:
            print(f"  ⚠️  异常情况")
    
    # 显示其他字段
    print("\n" + "=" * 80)
    print("其他活动信息字段")
    print("=" * 80)
    
    other_fields = [
        ("theme", "活动主题"),
        ("keywords", "关键词"),
        ("avgWorkYears", "平均工作年限"),
        ("avgAge", "平均年龄"),
        ("crossDepartment", "是否跨部门"),
        ("relatedToDigitalAi", "是否与数字化/AI相关")
    ]
    
    for field, field_name in other_fields:
        value = activity_info.get(field)
        print(f"{field_name} ({field}): {value}")
    
    # 显示完整的activityInfo JSON
    print("\n" + "=" * 80)
    print("完整的 activityInfo JSON")
    print("=" * 80)
    print(json.dumps(activity_info, indent=2, ensure_ascii=False))
    
    # 总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    
    if all_passed:
        print("✅ 所有4个Label字段都正确返回")
    else:
        print("❌ 部分Label字段缺失")
    
    return all_passed

if __name__ == "__main__":
    test_registration_detail()
