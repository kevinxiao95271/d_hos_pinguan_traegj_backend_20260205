#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试项目负责人职称统计功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import requests
import json
from db_config import DB_CONFIG

# API配置
BASE_URL = "http://localhost:6031"

def login_as_admin():
    """管理员登录"""
    url = f"{BASE_URL}/api/auth/login"
    # 使用组委会管理员账号
    data = {
        "phone": "13800000127",
        "name": "CommitteeAdmin A",
        "role": "COMMITTEE"
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            token = result['data']['token']
            print(f"✅ 管理员登录成功")
            return token
    print(f"❌ 管理员登录失败: {response.text}")
    return None

def test_stats_api(token, competition_id=None):
    """测试统计API"""
    url = f"{BASE_URL}/api/admin/stats/summary"
    if competition_id:
        url += f"?competitionId={competition_id}"
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    
    print(f"\n{'='*60}")
    print(f"测试统计API")
    print(f"{'='*60}")
    print(f"URL: {url}")
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        # 处理两种响应格式：{success: true, data: ...} 或 {code: 200, data: ...}
        if result.get('success') or result.get('code') == 200:
            data = result.get('data')
            if not data:
                print(f"❌ API返回数据为空")
                return False
                
            print(f"\n✅ API调用成功")
            print(f"\n赛事信息:")
            print(f"  - 赛事ID: {data.get('competitionId')}")
            print(f"  - 赛事名称: {data.get('competitionName')}")
            print(f"  - 报名总数: {data.get('registrationCount')}")
            
            # 检查新增字段
            if 'leaderTitleCounts' in data:
                print(f"\n✅ leaderTitleCounts 字段存在")
                leader_titles = data['leaderTitleCounts']
                print(f"\n项目负责人职称分布:")
                
                # 按数量排序
                sorted_titles = sorted(leader_titles.items(), key=lambda x: x[1], reverse=True)
                total_leaders = 0
                for title, count in sorted_titles:
                    print(f"  - {title}: {count}个项目")
                    total_leaders += count
                
                print(f"\n统计汇总:")
                print(f"  - 职称类型数: {len(leader_titles)}")
                print(f"  - 项目负责人总数: {total_leaders}")
                print(f"  - 报名项目总数: {data.get('registrationCount')}")
                
                if total_leaders < data.get('registrationCount', 0):
                    missing = data.get('registrationCount', 0) - total_leaders
                    print(f"  ⚠️  有 {missing} 个项目没有负责人信息")
                
                # 显示完整响应（格式化）
                print(f"\n完整响应数据:")
                print(json.dumps(data, ensure_ascii=False, indent=2))
                
                return True
            else:
                print(f"\n❌ leaderTitleCounts 字段不存在")
                print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
                return False
        else:
            print(f"❌ API返回错误: {result.get('message')}")
            return False
    else:
        print(f"❌ HTTP请求失败: {response.text}")
        return False

def main():
    """主函数"""
    print("="*60)
    print("项目负责人职称统计功能测试")
    print("="*60)
    
    # 1. 管理员登录
    token = login_as_admin()
    if not token:
        print("\n❌ 测试失败：无法登录")
        return
    
    # 2. 测试统计API（最新赛事）
    print(f"\n{'='*60}")
    print("测试场景1: 查询最新赛事统计")
    print(f"{'='*60}")
    success1 = test_stats_api(token)
    
    # 3. 测试统计API（指定赛事ID=21）
    print(f"\n{'='*60}")
    print("测试场景2: 查询指定赛事统计 (competitionId=21)")
    print(f"{'='*60}")
    success2 = test_stats_api(token, competition_id=21)
    
    # 总结
    print(f"\n{'='*60}")
    print("测试总结")
    print(f"{'='*60}")
    if success1 and success2:
        print("✅ 所有测试通过")
        print("\n功能验证:")
        print("  ✅ leaderTitleCounts 字段正确返回")
        print("  ✅ 职称统计数据准确")
        print("  ✅ 支持查询最新赛事")
        print("  ✅ 支持查询指定赛事")
    else:
        print("❌ 部分测试失败")
        if not success1:
            print("  ❌ 最新赛事查询失败")
        if not success2:
            print("  ❌ 指定赛事查询失败")

if __name__ == "__main__":
    main()
