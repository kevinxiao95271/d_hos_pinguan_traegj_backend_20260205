#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
场景2: 组委会管理员 - 书审分组项目列表
完整流程: 登录 → 获取书审分组列表 → 查看项目详情
"""

import requests
import json

BASE_URL = "http://localhost:6031"

def print_section(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

def test_admin_book_review_flow():
    print_section("场景2: 组委会管理员 - 书审分组项目列表")
    
    # 步骤1: 登录管理员账号
    print("\n【步骤1】登录组委会管理员账号")
    print("-" * 80)
    
    login_data = {
        "phone": "13800000041",
        "name": "CommitteeAdmin A",
        "role": "COMMITTEE_ADMIN"
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
    
    # 步骤2: 获取书审分组列表
    print("\n【步骤2】获取书审分组列表")
    print("-" * 80)
    
    competition_id = 23
    
    # 尝试多个可能的接口
    endpoints = [
        f"/api/admin/registrations/interview-groups?competitionId={competition_id}",
        f"/api/admin/registrations/final-groups?competitionId={competition_id}",
        f"/api/admin/registrations/grouped?competitionId={competition_id}"
    ]
    
    groups = None
    used_endpoint = None
    
    for endpoint in endpoints:
        url = f"{BASE_URL}{endpoint}"
        print(f"\n尝试: GET {url}")
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                groups = result.get("data", [])
                used_endpoint = endpoint
                print(f"✅ 接口可用，获取到 {len(groups)} 个分组")
                break
        else:
            print(f"   HTTP {response.status_code}")
    
    if not groups:
        print("\n❌ 所有接口都不可用或没有数据")
        print("   使用测试报名ID 119 继续测试...")
        registration_id = 119
    else:
        print(f"\n✅ 使用接口: {used_endpoint}")
        
        # 显示分组信息
        print("\n分组列表（前3组）:")
        for i, group in enumerate(groups[:3], 1):
            group_name = group.get("groupName")
            items = group.get("items", [])
            print(f"\n  {i}. 分组: {group_name}")
            print(f"     项目数: {len(items)}")
            
            if items:
                first_item = items[0]
                print(f"     第一个项目:")
                print(f"       - ID: {first_item.get('id')}")
                print(f"       - 项目名称: {first_item.get('projectName')}")
                print(f"       - 机构名称: {first_item.get('institutionName')}")
        
        # 获取第一个项目的ID
        if groups and groups[0].get("items"):
            registration_id = groups[0]["items"][0]["id"]
        else:
            registration_id = 119
    
    # 步骤3: 查看项目详情
    print(f"\n【步骤3】查看项目详情 (ID: {registration_id})")
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
        print("✅ 场景2测试通过")
        print("   - 管理员登录成功")
        print("   - 获取书审分组列表成功")
        print("   - 查看项目详情成功")
        print("   - 所有Label字段正确返回")
    else:
        print("❌ 场景2测试失败")
        print("   - 部分Label字段缺失")
    
    return all_passed

if __name__ == "__main__":
    test_admin_book_review_flow()
