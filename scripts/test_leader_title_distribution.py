#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试项目负责人职称分布统计功能
"""
import requests
import json

BASE_URL = "http://localhost:6031"

def test_stats_api():
    """测试报名统计API - 验证leaderTitleCounts字段"""
    print("=" * 60)
    print("测试报名统计API - 项目负责人职称分布")
    print("=" * 60)
    
    # 使用组委会管理员账号登录
    login_data = {
        "phone": "13800000041",
        "name": "CommitteeAdmin A",
        "role": "COMMITTEE_ADMIN"
    }
    
    print("\n1. 组委会管理员登录...")
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print(f"状态码: {response.status_code}")
    
    if response.status_code != 200:
        print(f"登录失败: {response.text}")
        return
    
    result = response.json()
    if not result.get("success"):
        print(f"登录失败: {result.get('message')}")
        return
    
    token = result["data"]["token"]
    print(f"登录成功，获取token")
    
    # 调用统计API - 使用赛事21（有更多数据）
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n2. 调用报名统计API（赛事21）...")
    response = requests.get(f"{BASE_URL}/api/admin/stats/summary?competitionId=21", headers=headers)
    print(f"状态码: {response.status_code}")
    
    if response.status_code != 200:
        print(f"请求失败: {response.text}")
        return
    
    result = response.json()
    if not result.get("success"):
        print(f"请求失败: {result.get('message')}")
        return
    
    data = result["data"]
    
    print("\n3. 验证返回数据...")
    print(f"赛事ID: {data.get('competitionId')}")
    print(f"赛事名称: {data.get('competitionName')}")
    print(f"报名总数: {data.get('registrationCount')}")
    
    # 验证leaderTitleCounts字段
    leader_title_counts = data.get('leaderTitleCounts')
    if leader_title_counts is None:
        print("\n❌ 错误: leaderTitleCounts字段不存在")
        return
    
    print(f"\n✅ leaderTitleCounts字段存在")
    print(f"职称分布统计:")
    
    # 按数量排序显示
    sorted_titles = sorted(leader_title_counts.items(), key=lambda x: x[1], reverse=True)
    total = sum(leader_title_counts.values())
    
    for title, count in sorted_titles:
        percentage = (count / total * 100) if total > 0 else 0
        print(f"  {title}: {count} ({percentage:.1f}%)")
    
    print(f"\n总计: {total}")
    
    # 验证其他统计字段
    print("\n4. 其他统计字段:")
    print(f"  地区分布: {len(data.get('regionCounts', {}))} 个地区")
    print(f"  学科类型分布: {len(data.get('subjectTypeCounts', {}))} 个类型")
    print(f"  品管工具分布: {len(data.get('methodCounts', {}))} 个工具")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成 - 项目负责人职称分布统计功能正常")
    print("=" * 60)

if __name__ == "__main__":
    test_stats_api()
