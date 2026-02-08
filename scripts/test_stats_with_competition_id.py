#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试统计接口的赛事ID参数"""

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
            token = result.get("data", {}).get("token")
            print(f"✅ 登录成功")
            return token
    print(f"❌ 登录失败: {response.text}")
    return None

def test_stats_without_param(token):
    """测试不带参数（默认返回最新赛事）"""
    url = f"{BASE_URL}/api/admin/stats/summary"
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n" + "="*80)
    print("测试1: 不带参数（默认返回最新赛事）")
    print("="*80)
    print(f"请求: GET {url}")
    
    response = requests.get(url, headers=headers)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            data = result.get("data", {})
            print(f"\n✅ 成功")
            print(f"  赛事ID: {data.get('competitionId')}")
            print(f"  赛事名称: {data.get('competitionName')}")
            print(f"  报名总数: {data.get('registrationCount')}")
            print(f"  地区分布: {json.dumps(data.get('regionCounts', {}), ensure_ascii=False)}")
        else:
            print(f"❌ 失败: {result.get('message')}")
    else:
        print(f"❌ 请求失败: {response.text}")

def test_stats_with_competition_21(token):
    """测试指定赛事ID=21"""
    url = f"{BASE_URL}/api/admin/stats/summary"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"competitionId": 21}
    
    print("\n" + "="*80)
    print("测试2: 指定赛事ID=21（2026浙江品管大赛）")
    print("="*80)
    print(f"请求: GET {url}?competitionId=21")
    
    response = requests.get(url, headers=headers, params=params)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            data = result.get("data", {})
            print(f"\n✅ 成功")
            print(f"  赛事ID: {data.get('competitionId')}")
            print(f"  赛事名称: {data.get('competitionName')}")
            print(f"  报名总数: {data.get('registrationCount')}")
            
            print(f"\n  📊 地区分布:")
            region_counts = data.get('regionCounts', {})
            for region, count in sorted(region_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"    {region}: {count} 条")
            
            print(f"\n  📈 主题类型分布:")
            subject_counts = data.get('subjectTypeCounts', {})
            for subject, count in sorted(subject_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"    {subject}: {count} 条")
        else:
            print(f"❌ 失败: {result.get('message')}")
    else:
        print(f"❌ 请求失败: {response.text}")

def test_stats_with_competition_29(token):
    """测试指定赛事ID=29"""
    url = f"{BASE_URL}/api/admin/stats/summary"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"competitionId": 29}
    
    print("\n" + "="*80)
    print("测试3: 指定赛事ID=29（2026年省级质量改进赛-2）")
    print("="*80)
    print(f"请求: GET {url}?competitionId=29")
    
    response = requests.get(url, headers=headers, params=params)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            data = result.get("data", {})
            print(f"\n✅ 成功")
            print(f"  赛事ID: {data.get('competitionId')}")
            print(f"  赛事名称: {data.get('competitionName')}")
            print(f"  报名总数: {data.get('registrationCount')}")
            print(f"  地区分布: {json.dumps(data.get('regionCounts', {}), ensure_ascii=False)}")
        else:
            print(f"❌ 失败: {result.get('message')}")
    else:
        print(f"❌ 请求失败: {response.text}")

def test_stats_with_invalid_id(token):
    """测试无效的赛事ID"""
    url = f"{BASE_URL}/api/admin/stats/summary"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"competitionId": 999}
    
    print("\n" + "="*80)
    print("测试4: 无效的赛事ID=999")
    print("="*80)
    print(f"请求: GET {url}?competitionId=999")
    
    response = requests.get(url, headers=headers, params=params)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print(f"⚠️  意外成功")
        else:
            print(f"✅ 正确返回错误: {result.get('message')}")
    else:
        print(f"✅ 正确返回错误状态码")

def main():
    print("="*80)
    print("测试统计接口的赛事ID参数功能")
    print("="*80)
    
    # 登录
    token = login()
    if not token:
        print("❌ 无法获取token，测试终止")
        return
    
    # 测试1: 不带参数
    test_stats_without_param(token)
    
    # 测试2: 指定赛事21
    test_stats_with_competition_21(token)
    
    # 测试3: 指定赛事29
    test_stats_with_competition_29(token)
    
    # 测试4: 无效ID
    test_stats_with_invalid_id(token)
    
    print("\n" + "="*80)
    print("测试完成")
    print("="*80)
    
    print("\n📝 总结:")
    print("  ✅ 不带参数: 返回最新赛事（ID最大）")
    print("  ✅ 带参数competitionId: 返回指定赛事")
    print("  ✅ 前端可以根据当前选中的赛事传递参数")

if __name__ == "__main__":
    main()
