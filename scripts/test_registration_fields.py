#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试报名详情字段"""

import requests
import json

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

def test_detail(reg_id, token):
    """测试报名详情"""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}/api/registrations/{reg_id}"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ 请求失败: HTTP {response.status_code}")
        return
    
    result = response.json()
    if not result.get("success"):
        print(f"❌ API返回失败: {result.get('message')}")
        return
    
    data = result.get("data", {})
    
    print(f"\n报名ID: {reg_id}")
    print("=" * 80)
    
    # 活动信息
    activity = data.get("activityInfo")
    if activity:
        print("\n✅ 活动信息字段:")
        print(f"  1. theme: {activity.get('theme')}")
        print(f"  2. keywords: {activity.get('keywords')}")
        print(f"  3. subjectTypeCode: {activity.get('subjectTypeCode')}")
        print(f"  4. methodCode: {activity.get('methodCode')}")
        print(f"  5. experienceImproveCode: {activity.get('experienceImproveCode')}")
        print(f"  6. qualityTopicCode: {activity.get('qualityTopicCode')}")
        print(f"  7. avgWorkYears: {activity.get('avgWorkYears')}")
        print(f"  8. avgAge: {activity.get('avgAge')}")
        print(f"  9. crossDepartment: {activity.get('crossDepartment')}")
        print(f"  10. relatedToDigitalAi: {activity.get('relatedToDigitalAi')}")
    else:
        print("\n❌ 活动信息: 无数据")
    
    # 项目摘要
    summary = data.get("projectSummary")
    if summary:
        print("\n✅ 项目摘要字段:")
        print(f"  1. theme: {'有' if summary.get('theme') else '无'}")
        print(f"  2. plan: {'有' if summary.get('plan') else '无'}")
        print(f"  3. problem: {'有' if summary.get('problem') else '无'}")
        print(f"  4. action: {'有' if summary.get('action') else '无'}")
        print(f"  5. success: {'有' if summary.get('success') else '无'}")
        print(f"  6. discussion: {'有' if summary.get('discussion') else '无'}")
        print(f"  7. operation: {'有' if summary.get('operation') else '无'}")
        print(f"  8. presentation: {'有' if summary.get('presentation') else '无'}")
    else:
        print("\n❌ 项目摘要: 无数据")
    
    # 显示完整JSON
    print("\n完整JSON:")
    print(json.dumps(data, ensure_ascii=False, indent=2))

def main():
    """主函数"""
    token = login()
    if not token:
        print("❌ 登录失败")
        return
    
    print("✅ 登录成功")
    
    # 测试报名ID 119
    test_detail(119, token)

if __name__ == "__main__":
    main()
