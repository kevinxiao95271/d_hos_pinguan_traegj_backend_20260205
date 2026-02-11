#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试项目负责人职称统计功能 - 使用赛事21"""

import requests
import json

BASE_URL = "http://localhost:6031"

def test_api():
    """测试API返回"""
    print("=" * 80)
    print("测试项目负责人职称统计功能")
    print("=" * 80)
    
    # 1. 登录
    print("\n【步骤1】登录组委会管理员")
    login_data = {
        "phone": "13800000041",
        "name": "CommitteeAdmin A",
        "role": "COMMITTEE_ADMIN"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ 登录失败: {response.status_code}")
        return
    
    result = response.json()
    if not result.get("success"):
        print(f"❌ 登录失败: {result.get('message')}")
        return
    
    token = result["data"]["token"]
    print("✅ 登录成功")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. 调用统计API（使用赛事21，有完整数据）
    print(f"\n【步骤2】调用统计API（赛事21）")
    
    response = requests.get(
        f"{BASE_URL}/api/admin/stats/summary?competitionId=21",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ API调用失败: {response.status_code}")
        print(response.text)
        return
    
    result = response.json()
    if not result.get("success"):
        print(f"❌ API调用失败: {result.get('message')}")
        return
    
    print("✅ API调用成功")
    
    data = result["data"]
    
    # 3. 显示统计数据
    print("\n" + "=" * 80)
    print("统计数据")
    print("=" * 80)
    
    print(f"\n基本信息:")
    print(f"  赛事ID: {data.get('competitionId')}")
    print(f"  赛事名称: {data.get('competitionName')}")
    print(f"  报名总数: {data.get('registrationCount')}")
    print(f"  品管工具种类数: {data.get('toolTypeCount')}")
    print(f"  评委数: {data.get('reviewerCount')}")
    
    # 4. 显示项目负责人职称分布 ⭐ 重点
    leader_title_counts = data.get("leaderTitleCounts", {})
    print(f"\n⭐ 项目负责人职称分布 (共 {len(leader_title_counts)} 种):")
    if leader_title_counts:
        total = sum(leader_title_counts.values())
        for title, count in sorted(leader_title_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total * 100) if total > 0 else 0
            print(f"  {title:30s}: {count:3d} ({percentage:5.1f}%)")
        print(f"  {'总计':30s}: {total:3d}")
    else:
        print("  (无数据)")
    
    # 5. 显示品管工具分布（对比）
    method_counts = data.get("methodCounts", {})
    print(f"\n品管工具分布 (共 {len(method_counts)} 种):")
    if method_counts:
        total = sum(method_counts.values())
        for method, count in sorted(method_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            percentage = (count / total * 100) if total > 0 else 0
            print(f"  {method:30s}: {count:3d} ({percentage:5.1f}%)")
    
    # 6. 验证字段存在
    print("\n" + "=" * 80)
    print("字段验证")
    print("=" * 80)
    
    required_fields = [
        "competitionId",
        "competitionName", 
        "registrationCount",
        "regionCounts",
        "subjectTypeCounts",
        "methodCounts",
        "leaderTitleCounts"  # ⭐ 新增字段
    ]
    
    all_ok = True
    for field in required_fields:
        if field in data:
            print(f"✅ {field:30s}: 存在")
        else:
            print(f"❌ {field:30s}: 缺失")
            all_ok = False
    
    print("\n" + "=" * 80)
    if all_ok and leader_title_counts:
        print("✅ 测试通过！项目负责人职称统计字段已正确返回")
    elif all_ok:
        print("⚠️  字段存在但无数据（可能该赛事没有成员数据）")
    else:
        print("❌ 测试失败！项目负责人职称统计字段缺失")
    print("=" * 80)
    
    # 7. 显示完整响应（可选）
    print("\n【完整API响应】")
    print(json.dumps(data, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    test_api()
