#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""步骤1: 检查数据库字段是否已添加"""

import requests

BASE_URL = "http://localhost:6031"

def login():
    """登录"""
    url = f"{BASE_URL}/api/auth/login"
    data = {
        "phone": "13800000041",
        "name": "CommitteeAdmin A",
        "role": "COMMITTEE_ADMIN"
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            return result.get("data", {}).get("token")
    return None

def check_fields():
    """检查字段"""
    token = login()
    if not token:
        print("❌ 登录失败")
        return False
    
    print("✅ 登录成功\n")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 获取报名详情
    url = f"{BASE_URL}/api/registrations/119"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ 请求失败: HTTP {response.status_code}")
        return False
    
    result = response.json()
    if not result.get("success"):
        print(f"❌ API返回失败: {result.get('message')}")
        return False
    
    data = result.get("data", {})
    activity = data.get("activityInfo")
    summary = data.get("projectSummary")
    
    print("=" * 80)
    print("字段检查结果")
    print("=" * 80)
    
    # 检查 activityInfo
    if activity:
        print("\n【活动信息】")
        print(f"  ✅ theme: {activity.get('theme')}")
        print(f"  ✅ keywords: {activity.get('keywords')}")
        print(f"  ✅ avgWorkYears: {activity.get('avgWorkYears')}")
        print(f"  ✅ avgAge: {activity.get('avgAge')}")
        print(f"  ✅ crossDepartment: {activity.get('crossDepartment')}")
        
        # 重点检查新字段
        related_to_ai = activity.get('relatedToDigitalAi')
        if related_to_ai is None:
            print(f"  ❌ relatedToDigitalAi: None (字段未添加或应用未重启)")
            return False
        else:
            print(f"  ✅ relatedToDigitalAi: {related_to_ai}")
    else:
        print("\n❌ activityInfo 为空")
        return False
    
    # 检查 projectSummary
    if summary:
        print("\n【项目摘要】")
        print(f"  ✅ theme: {'有' if summary.get('theme') else '无'}")
        print(f"  ✅ plan: {'有' if summary.get('plan') else '无'}")
        print(f"  ✅ problem: {'有' if summary.get('problem') else '无'}")
        print(f"  ✅ action: {'有' if summary.get('action') else '无'}")
        print(f"  ✅ success: {'有' if summary.get('success') else '无'}")
        print(f"  ✅ discussion: {'有' if summary.get('discussion') else '无'}")
        
        # 重点检查新字段
        operation = summary.get('operation')
        presentation = summary.get('presentation')
        
        if 'operation' not in summary:
            print(f"  ❌ operation: 字段不存在（应用未重启）")
            return False
        else:
            print(f"  ✅ operation: {'有' if operation else '无（可以为空）'}")
        
        if 'presentation' not in summary:
            print(f"  ❌ presentation: 字段不存在（应用未重启）")
            return False
        else:
            print(f"  ✅ presentation: {'有' if presentation else '无（可以为空）'}")
    else:
        print("\n⚠️  projectSummary 为空（这个报名还没填写摘要，正常）")
    
    print("\n" + "=" * 80)
    print("✅ 所有字段检查通过！")
    print("=" * 80)
    return True

if __name__ == "__main__":
    success = check_fields()
    if not success:
        print("\n⚠️  需要执行以下操作：")
        print("1. 执行 add_digital_ai_field.sql")
        print("2. 重新编译应用: mvn clean package")
        print("3. 重启应用")
        print("4. 再次运行本脚本")
