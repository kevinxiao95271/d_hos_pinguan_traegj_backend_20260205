#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试项目摘要7个字段是否返回"""

import requests
import json

BASE_URL = "http://localhost:6031"

def test_project_summary_fields():
    print("=" * 80)
    print("测试项目摘要字段")
    print("=" * 80)
    
    # 测试项目ID（刚填充的数据）
    test_id = 119
    
    # 场景1: 参赛者 - 我的报名
    print("\n【场景1】参赛者 - 我的报名")
    print("-" * 80)
    
    login_data = {
        "phone": "13800000001",
        "name": "张三",
        "role": "CONTESTANT"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ 登录失败")
        return
    
    token = response.json()["data"]["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/api/registrations/{test_id}", headers=headers)
    if response.status_code != 200:
        print(f"❌ 获取详情失败: {response.status_code}")
        return
    
    data = response.json()["data"]
    check_fields(data, "参赛者")
    
    # 场景2: 组委会管理员 - 书审分组
    print("\n【场景2】组委会管理员 - 书审分组")
    print("-" * 80)
    
    login_data = {
        "phone": "13800000041",
        "name": "CommitteeAdmin A",
        "role": "COMMITTEE_ADMIN"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    token = response.json()["data"]["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/api/registrations/{test_id}", headers=headers)
    if response.status_code != 200:
        print(f"❌ 获取详情失败: {response.status_code}")
        return
    
    data = response.json()["data"]
    check_fields(data, "组委会管理员")
    
    # 场景3: 评委 - 评审任务
    print("\n【场景3】评委 - 评审任务")
    print("-" * 80)
    
    login_data = {
        "phone": "13800000021",
        "name": "李明华",
        "role": "REVIEWER"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    token = response.json()["data"]["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/api/registrations/{test_id}", headers=headers)
    if response.status_code != 200:
        print(f"❌ 获取详情失败: {response.status_code}")
        return
    
    data = response.json()["data"]
    check_fields(data, "评委")

def check_fields(data, role_name):
    """检查项目摘要字段"""
    project_summary = data.get("projectSummary")
    
    if not project_summary:
        print(f"❌ {role_name}: projectSummary 字段不存在")
        return
    
    print(f"✅ {role_name}: projectSummary 字段存在")
    
    # 检查7个字段
    fields = [
        ("plan", "计划"),
        ("problem", "问题结构与对策措施探讨"),
        ("action", "对策行动过程"),
        ("success", "成果表现"),
        ("discussion", "讨论总结"),
        ("operation", "运作"),
        ("presentation", "展示")
    ]
    
    all_ok = True
    for field_name, field_label in fields:
        value = project_summary.get(field_name)
        if value is not None:
            # 截取前30个字符显示
            display_value = value[:30] + "..." if len(value) > 30 else value
            print(f"  ✅ {field_label:20s}: {display_value}")
        else:
            print(f"  ❌ {field_label:20s}: 字段缺失")
            all_ok = False
    
    if all_ok:
        print(f"  ✅ 所有7个字段都正确返回")
    else:
        print(f"  ❌ 部分字段缺失")
    
    # 显示完整的projectSummary
    print(f"\n  完整projectSummary:")
    print(json.dumps(project_summary, indent=4, ensure_ascii=False))

if __name__ == '__main__':
    test_project_summary_fields()
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)
