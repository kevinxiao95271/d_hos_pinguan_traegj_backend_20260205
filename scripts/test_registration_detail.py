#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试报名详情接口"""

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

def test_registration_detail():
    """测试报名详情接口"""
    token = login()
    if not token:
        print("❌ 登录失败")
        return
    
    print("✅ 登录成功\n")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 测试报名ID 119（从用户提供的数据中获取）
    registration_id = 119
    
    print("=" * 100)
    print(f"测试报名详情接口 - 报名ID: {registration_id}")
    print("=" * 100)
    
    url = f"{BASE_URL}/api/registrations/{registration_id}"
    print(f"\n请求URL: {url}\n")
    
    response = requests.get(url, headers=headers)
    
    print(f"响应状态码: {response.status_code}\n")
    
    if response.status_code == 200:
        result = response.json()
        
        if result.get("success"):
            data = result.get("data", {})
            
            print(f"✅ 请求成功！\n")
            
            # 检查各个部分
            print("=" * 100)
            print("返回数据结构")
            print("=" * 100)
            
            print(f"\n1. registration (报名基本信息): {'✅ 有' if data.get('registration') else '❌ 无'}")
            print(f"2. institution (机构信息): {'✅ 有' if data.get('institution') else '❌ 无'}")
            print(f"3. members (成员列表): {'✅ 有' if data.get('members') else '❌ 无'}")
            print(f"4. activityInfo (活动说明): {'✅ 有' if data.get('activityInfo') else '❌ 无'}")
            print(f"5. projectSummary (项目摘要): {'✅ 有' if data.get('projectSummary') else '❌ 无'}")
            print(f"6. materials (材料列表): {'✅ 有' if data.get('materials') else '❌ 无'}")
            
            # 检查 projectSummary 的字段
            if data.get('projectSummary'):
                print("\n" + "=" * 100)
                print("projectSummary (项目摘要) 字段")
                print("=" * 100)
                
                summary = data['projectSummary']
                print(f"\n  - theme (主题): {'✅ 有' if summary.get('theme') else '❌ 无'}")
                print(f"  - plan (计划): {'✅ 有' if summary.get('plan') else '❌ 无'}")
                print(f"  - problem (问题): {'✅ 有' if summary.get('problem') else '❌ 无'}")
                print(f"  - action (行动): {'✅ 有' if summary.get('action') else '❌ 无'}")
                print(f"  - success (成效): {'✅ 有' if summary.get('success') else '❌ 无'}")
                print(f"  - discussion (回顾/讨论): {'✅ 有' if summary.get('discussion') else '❌ 无'}")
                
                # 检查是否有"运作"和"展示"字段
                print(f"  - operation (运作): {'✅ 有' if summary.get('operation') else '❌ 无'}")
                print(f"  - presentation (展示): {'✅ 有' if summary.get('presentation') else '❌ 无'}")
                
                # 显示实际内容（前100个字符）
                print("\n" + "=" * 100)
                print("projectSummary 内容预览")
                print("=" * 100)
                
                for field in ['theme', 'plan', 'problem', 'action', 'success', 'discussion', 'operation', 'presentation']:
                    value = summary.get(field, '')
                    if value:
                        preview = value[:100] + '...' if len(value) > 100 else value
                        print(f"\n  {field}: {preview}")
                    else:
                        print(f"\n  {field}: (空)")
            else:
                print("\n⚠️  projectSummary 为空，参赛者可能还没有填写摘要")
            
            # 显示完整的JSON
            print("\n" + "=" * 100)
            print("完整的返回数据（JSON格式）")
            print("=" * 100)
            print(json.dumps(data, ensure_ascii=False, indent=2))
            
        else:
            print(f"❌ API返回失败: {result.get('message')}")
    else:
        print(f"❌ 请求失败: HTTP {response.status_code}")
        print(f"响应内容: {response.text}")

if __name__ == "__main__":
    test_registration_detail()
