#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
场景1: 参赛者 - 我的报名
完整流程: 登录 → 获取我的报名列表 → 查看报名详情
"""

import requests
import json

BASE_URL = "http://localhost:6031"

def print_section(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

def test_contestant_flow():
    print_section("场景1: 参赛者 - 我的报名")
    
    # 步骤1: 登录参赛者账号
    print("\n【步骤1】登录参赛者账号")
    print("-" * 80)
    
    login_data = {
        "phone": "13800000001",
        "name": "张三",
        "role": "CONTESTANT"
    }
    
    print(f"请求: POST {BASE_URL}/api/auth/login")
    print(f"参数: {json.dumps(login_data, ensure_ascii=False)}")
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"❌ 登录失败: HTTP {response.status_code}")
        print(response.text)
        return
    
    result = response.json()
    if not result.get("success"):
        print(f"❌ 登录失败: {result.get('message')}")
        return
    
    token = result["data"]["token"]
    print(f"✅ 登录成功")
    print(f"   Token: {token[:30]}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 步骤2: 获取我的报名列表
    print("\n【步骤2】获取我的报名列表")
    print("-" * 80)
    
    url = f"{BASE_URL}/api/registrations/my"
    print(f"请求: GET {url}")
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ 请求失败: HTTP {response.status_code}")
        print(response.text)
        return
    
    result = response.json()
    if not result.get("success"):
        print(f"❌ 请求失败: {result.get('message')}")
        return
    
    registrations = result.get("data", [])
    print(f"✅ 获取成功，共 {len(registrations)} 条报名")
    
    if not registrations:
        print("⚠️  该参赛者没有报名记录")
        print("\n使用测试报名ID 119 继续测试...")
        registration_id = 119
    else:
        # 显示前3条报名
        print("\n报名列表（前3条）:")
        for i, reg in enumerate(registrations[:3], 1):
            print(f"\n  {i}. 报名ID: {reg.get('id')}")
            print(f"     项目名称: {reg.get('projectName')}")
            print(f"     机构名称: {reg.get('institutionName')}")
            print(f"     状态: {reg.get('status')}")
        
        registration_id = registrations[0]["id"]
    
    # 步骤3: 查看报名详情
    print(f"\n【步骤3】查看报名详情 (ID: {registration_id})")
    print("-" * 80)
    
    url = f"{BASE_URL}/api/registrations/{registration_id}"
    print(f"请求: GET {url}")
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ 请求失败: HTTP {response.status_code}")
        print(response.text)
        return
    
    result = response.json()
    if not result.get("success"):
        print(f"❌ 请求失败: {result.get('message')}")
        return
    
    print("✅ 获取详情成功")
    
    data = result["data"]
    activity_info = data.get("activityInfo")
    
    # 验证活动信息字段
    print("\n【字段验证】活动信息")
    print("-" * 80)
    
    if not activity_info:
        print("❌ activityInfo 为空")
        return
    
    # 检查4个Label字段
    label_fields = [
        ("subjectTypeCode", "subjectTypeLabel", "主题类型"),
        ("methodCode", "methodLabel", "运用手法"),
        ("experienceImproveCode", "experienceImproveLabel", "改善就医环境"),
        ("qualityTopicCode", "qualityTopicLabel", "医疗质量相关主题")
    ]
    
    all_passed = True
    for code_field, label_field, field_name in label_fields:
        code = activity_info.get(code_field)
        label = activity_info.get(label_field)
        
        if code and label:
            print(f"✅ {field_name}: {label}")
        elif code and not label:
            print(f"❌ {field_name}: Code={code}, Label缺失")
            all_passed = False
        else:
            print(f"⚠️  {field_name}: 未填写")
    
    # 检查其他字段
    print("\n其他字段:")
    print(f"  活动主题: {activity_info.get('theme')}")
    print(f"  关键词: {activity_info.get('keywords')}")
    print(f"  平均工作年限: {activity_info.get('avgWorkYears')} 年")
    print(f"  平均年龄: {activity_info.get('avgAge')} 岁")
    print(f"  是否跨部门: {'是' if activity_info.get('crossDepartment') else '否'}")
    print(f"  是否与数字化/AI相关: {'是' if activity_info.get('relatedToDigitalAi') else '否'}")
    
    # 总结
    print_section("测试总结")
    
    if all_passed:
        print("✅ 场景1测试通过")
        print("   - 参赛者登录成功")
        print("   - 获取报名列表成功")
        print("   - 查看报名详情成功")
        print("   - 所有Label字段正确返回")
    else:
        print("❌ 场景1测试失败")
        print("   - 部分Label字段缺失")
    
    return all_passed

if __name__ == "__main__":
    test_contestant_flow()
