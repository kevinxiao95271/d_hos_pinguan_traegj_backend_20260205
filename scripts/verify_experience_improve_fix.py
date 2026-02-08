#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证 experience_improve 修复结果"""

import requests
import json

BASE_URL = "http://localhost:6031"

def test_experience_improve_label():
    print("=" * 80)
    print("验证 experienceImproveLabel 修复结果")
    print("=" * 80)
    
    # 登录获取token
    login_data = {
        "phone": "13800000001",
        "name": "张三",
        "role": "CONTESTANT"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data, timeout=10)
    except Exception as e:
        print(f"❌ 登录请求失败: {e}")
        return
    
    if response.status_code != 200:
        print(f"❌ 登录失败: {response.status_code}")
        print(response.text)
        return
    
    result = response.json()
    if not result.get("success"):
        print(f"❌ 登录失败: {result.get('message')}")
        return
    
    token = result['data']['token']
    headers = {"Authorization": f"Bearer {token}"}
    
    # 测试项目ID 119
    test_id = 119
    
    print(f"\n测试项目 ID: {test_id}")
    print("-" * 80)
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/registrations/{test_id}",
            headers=headers,
            timeout=10
        )
    except Exception as e:
        print(f"❌ 获取详情请求失败: {e}")
        return
    
    if response.status_code != 200:
        print(f"❌ 获取详情失败: {response.status_code}")
        print(response.text)
        return
    
    result = response.json()
    if not result.get("success"):
        print(f"❌ 获取详情失败: {result.get('message')}")
        return
    
    data = result['data']
    activity_info = data.get('activityInfo', {})
    
    # 检查4个Label字段
    print("\n4个Label字段:")
    print("-" * 80)
    
    fields = [
        ('subjectTypeCode', 'subjectTypeLabel', '主题类型'),
        ('methodCode', 'methodLabel', '品管工具'),
        ('experienceImproveCode', 'experienceImproveLabel', '改善就医环境'),
        ('qualityTopicCode', 'qualityTopicLabel', '医疗质量相关主题')
    ]
    
    all_ok = True
    for code_field, label_field, name in fields:
        code = activity_info.get(code_field)
        label = activity_info.get(label_field)
        
        if code and label:
            print(f"✅ {name:20s}: {code:30s} → {label}")
        elif code and not label:
            print(f"❌ {name:20s}: {code:30s} → (Label缺失)")
            all_ok = False
        else:
            print(f"⚠️  {name:20s}: 未填写")
    
    print("\n" + "=" * 80)
    if all_ok:
        print("✅ 所有Label字段都正确返回！")
    else:
        print("❌ 仍有Label字段缺失")
    print("=" * 80)

if __name__ == '__main__':
    test_experience_improve_label()
