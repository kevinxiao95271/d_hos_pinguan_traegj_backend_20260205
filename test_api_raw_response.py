#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试API原始响应"""

import requests
import json

BASE_URL = "http://localhost:6031"

def login():
    """登录获取token"""
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

def test_api():
    """测试API"""
    token = login()
    if not token:
        print("❌ 登录失败")
        return
    
    print("✅ 登录成功\n")
    
    # 测试赛事21
    url = f"{BASE_URL}/api/admin/stats/summary?competitionId=21"
    headers = {"Authorization": f"Bearer {token}"}
    
    print("=" * 100)
    print("测试赛事21的统计接口")
    print("=" * 100)
    print(f"\n请求URL: {url}")
    print(f"请求头: Authorization: Bearer {token[:20]}...\n")
    
    response = requests.get(url, headers=headers)
    
    print(f"响应状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}\n")
    
    print("=" * 100)
    print("完整的原始响应（JSON格式）")
    print("=" * 100)
    
    try:
        result = response.json()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        if result.get("success"):
            data = result.get("data", {})
            
            print("\n" + "=" * 100)
            print("地区分布详细分析")
            print("=" * 100)
            
            region_counts = data.get("regionCounts", {})
            
            print(f"\nregionCounts 对象类型: {type(region_counts)}")
            print(f"regionCounts 键数量: {len(region_counts)}")
            print(f"regionCounts 所有键: {list(region_counts.keys())}")
            
            print(f"\n逐个键值对:")
            total = 0
            for key, value in region_counts.items():
                print(f"  键: '{key}' (类型: {type(key).__name__}, 长度: {len(key)})")
                print(f"  值: {value} (类型: {type(value).__name__})")
                print(f"  键的字节表示: {key.encode('utf-8')}")
                total += value
                print()
            
            print(f"总计: {total} 条报名")
            
            # 检查是否有特殊字符或空格
            print("\n" + "=" * 100)
            print("检查特殊情况")
            print("=" * 100)
            
            for key in region_counts.keys():
                if key.strip() != key:
                    print(f"⚠️  键 '{key}' 包含前后空格")
                if '\n' in key or '\r' in key or '\t' in key:
                    print(f"⚠️  键 '{key}' 包含换行或制表符")
                if not key:
                    print(f"⚠️  发现空字符串键")
            
            # 统计百分比
            print("\n" + "=" * 100)
            print("地区分布统计（带百分比）")
            print("=" * 100)
            
            print(f"\n{'地区':<20} {'报名数':<10} {'占比':<10}")
            print("-" * 50)
            
            for region, count in sorted(region_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total * 100) if total > 0 else 0
                print(f"{region:<20} {count:<10} {percentage:>6.2f}%")
            
            print("-" * 50)
            print(f"{'总计':<20} {total:<10} 100.00%")
            
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败: {e}")
        print(f"原始响应文本:\n{response.text}")

if __name__ == "__main__":
    test_api()
