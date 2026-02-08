#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试品管工具分布统计"""

import requests
import json

BASE_URL = "http://localhost:6031"

def test_api():
    """测试API返回"""
    print("=" * 80)
    print("测试品管工具分布统计")
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
    
    # 2. 调用统计API（使用最新赛事）
    print(f"\n【步骤2】调用统计API（最新赛事）")
    
    response = requests.get(
        f"{BASE_URL}/api/admin/stats/summary",
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
    
    # 4. 显示地区分布
    region_counts = data.get("regionCounts", {})
    print(f"\n地区分布 (共 {len(region_counts)} 个地区):")
    for region, count in sorted(region_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {region:20s}: {count:3d}")
    
    # 5. 显示主题类型分布
    subject_type_counts = data.get("subjectTypeCounts", {})
    print(f"\n主题类型分布 (共 {len(subject_type_counts)} 种):")
    for subject, count in sorted(subject_type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {subject:30s}: {count:3d}")
    
    # 6. 显示品管工具分布 ⭐ 重点
    method_counts = data.get("methodCounts", {})
    print(f"\n⭐ 品管工具分布 (共 {len(method_counts)} 种):")
    if method_counts:
        total = sum(method_counts.values())
        for method, count in sorted(method_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total * 100) if total > 0 else 0
            print(f"  {method:30s}: {count:3d} ({percentage:5.1f}%)")
        print(f"  {'总计':30s}: {total:3d}")
    else:
        print("  ❌ 没有返回 methodCounts 字段！")
    
    # 7. 验证字段存在
    print("\n" + "=" * 80)
    print("字段验证")
    print("=" * 80)
    
    required_fields = [
        "competitionId",
        "competitionName", 
        "registrationCount",
        "regionCounts",
        "subjectTypeCounts",
        "methodCounts"  # ⭐ 新增字段
    ]
    
    all_ok = True
    for field in required_fields:
        if field in data:
            print(f"✅ {field:30s}: 存在")
        else:
            print(f"❌ {field:30s}: 缺失")
            all_ok = False
    
    print("\n" + "=" * 80)
    if all_ok and method_counts:
        print("✅ 测试通过！品管工具分布字段已正确返回")
    else:
        print("❌ 测试失败！品管工具分布字段缺失或为空")
    print("=" * 80)
    
    # 8. 显示完整响应（可选）
    print("\n【完整API响应】")
    print(json.dumps(data, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    test_api()
