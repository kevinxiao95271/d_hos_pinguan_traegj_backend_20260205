#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试项目负责人职称统计功能
验证 /api/admin/stats API 返回的 leaderTitleCounts 字段
"""

import requests
import json
from db_config import DB_CONFIG

BASE_URL = "http://localhost:6031"

def login_admin():
    """管理员登录"""
    url = f"{BASE_URL}/api/auth/login"
    data = {
        "phone": "13800000041",
        "name": "CommitteeAdmin A",
        "role": "COMMITTEE_ADMIN"
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            return result.get('data', {}).get('token')
    print(f"登录失败: {response.status_code}")
    print(response.text)
    return None

def get_stats(token, competition_id=None):
    """获取统计数据"""
    if competition_id:
        url = f"{BASE_URL}/api/admin/stats/summary?competitionId={competition_id}"
    else:
        url = f"{BASE_URL}/api/admin/stats/summary"
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            return result.get('data')
    print(f"获取统计失败: {response.status_code}")
    print(response.text)
    return None

def main():
    print("=" * 60)
    print("测试项目负责人职称统计功能")
    print("=" * 60)
    
    # 1. 登录
    print("\n1. 管理员登录...")
    token = login_admin()
    if not token:
        print("❌ 登录失败")
        return
    print("✓ 登录成功")
    
    # 2. 获取统计数据
    print("\n2. 获取统计数据...")
    stats = get_stats(token)
    if not stats:
        print("❌ 获取统计失败")
        return
    
    print(f"✓ 获取成功")
    print(f"\n赛事: {stats.get('competitionName')}")
    print(f"报名数: {stats.get('registrationCount')}")
    
    # 3. 验证 leaderTitleCounts 字段
    print("\n3. 验证 leaderTitleCounts 字段...")
    leader_title_counts = stats.get('leaderTitleCounts')
    
    if leader_title_counts is None:
        print("❌ leaderTitleCounts 字段不存在")
        return
    
    if not isinstance(leader_title_counts, dict):
        print(f"❌ leaderTitleCounts 类型错误: {type(leader_title_counts)}")
        return
    
    print("✓ leaderTitleCounts 字段存在且类型正确")
    
    # 4. 显示职称分布
    print("\n4. 项目负责人职称分布:")
    print("-" * 60)
    
    if not leader_title_counts:
        print("  (无数据)")
    else:
        total = sum(leader_title_counts.values())
        sorted_titles = sorted(leader_title_counts.items(), key=lambda x: x[1], reverse=True)
        
        for title, count in sorted_titles:
            percentage = (count / total * 100) if total > 0 else 0
            print(f"  {title:20s}: {count:3d} ({percentage:5.1f}%)")
        
        print("-" * 60)
        print(f"  {'总计':20s}: {total:3d}")
    
    # 5. 显示完整响应（用于前端参考）
    print("\n5. 完整API响应示例:")
    print("-" * 60)
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    
    print("\n" + "=" * 60)
    print("✓ 测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
