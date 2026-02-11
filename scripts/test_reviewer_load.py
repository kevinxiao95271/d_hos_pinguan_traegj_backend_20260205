#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试评委负荷字段"""

import requests
import json

BASE_URL = "http://localhost:6031"

def test_reviewer_load():
    """测试评委负荷"""
    print("=" * 80)
    print("测试评委负荷字段")
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
    
    # 2. 调用评委列表API
    print(f"\n【步骤2】调用评委列表API")
    
    response = requests.get(
        f"{BASE_URL}/api/admin/reviewers?competitionId=21",
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
    
    # 3. 显示评委列表
    print("\n" + "=" * 80)
    print("评委列表")
    print("=" * 80)
    
    print(f"\n总评委数: {len(data)}")
    
    if not data:
        print("  (无数据)")
        return
    
    # 4. 检查currentLoad字段
    print(f"\n【步骤3】检查currentLoad字段")
    
    has_load_field = 'currentLoad' in data[0] if data else False
    
    if has_load_field:
        print("✅ currentLoad 字段存在")
    else:
        print("❌ currentLoad 字段不存在")
        print(f"   实际字段: {list(data[0].keys()) if data else '无数据'}")
        return
    
    # 5. 显示前10个评委的负荷
    print(f"\n前10个评委的负荷:")
    print("-" * 80)
    
    for i, reviewer in enumerate(data[:10], 1):
        load = reviewer.get('currentLoad', 'N/A')
        print(f"{i:2d}. {reviewer.get('name'):15s} | "
              f"机构: {reviewer.get('institutionName', '未知'):30s} | "
              f"负荷: {load:3}")
    
    # 6. 统计负荷分布
    print("\n" + "=" * 80)
    print("负荷统计")
    print("=" * 80)
    
    loads = [r.get('currentLoad', 0) for r in data]
    
    if loads:
        print(f"\n总负荷: {sum(loads)}")
        print(f"平均负荷: {sum(loads) / len(loads):.1f}")
        print(f"最大负荷: {max(loads)}")
        print(f"最小负荷: {min(loads)}")
        
        # 按负荷分组
        load_distribution = {}
        for load in loads:
            load_distribution[load] = load_distribution.get(load, 0) + 1
        
        print(f"\n负荷分布:")
        for load in sorted(load_distribution.keys()):
            count = load_distribution[load]
            print(f"  负荷 {load:2d}: {count:2d} 人")
    
    # 7. 显示负荷最高的评委
    print("\n" + "=" * 80)
    print("负荷最高的评委 (Top 5)")
    print("=" * 80)
    
    sorted_reviewers = sorted(data, key=lambda x: x.get('currentLoad', 0), reverse=True)
    
    for i, reviewer in enumerate(sorted_reviewers[:5], 1):
        print(f"\n{i}. {reviewer.get('name')}")
        print(f"   机构: {reviewer.get('institutionName', '未知')}")
        print(f"   职称: {reviewer.get('title', '未知')}")
        print(f"   负荷: {reviewer.get('currentLoad', 0)} 个任务")
    
    # 8. 显示完整响应示例
    print("\n" + "=" * 80)
    print("完整API响应示例（第1个评委）")
    print("=" * 80)
    if data:
        print(json.dumps(data[0], indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 80)
    print("✅ 测试完成")
    print("=" * 80)

if __name__ == '__main__':
    test_reviewer_load()
