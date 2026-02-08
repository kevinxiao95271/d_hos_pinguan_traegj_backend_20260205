#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试书审分组筛选接口是否返回机构等级字段
"""
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

def test_filter_api(token):
    """测试筛选接口"""
    url = f"{BASE_URL}/api/admin/registrations/filter"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # 测试1: 获取所有数据（不带筛选条件）
    print("\n" + "="*60)
    print("测试1: 获取所有数据")
    print("="*60)
    params = {
        "competitionId": 21
    }
    response = requests.get(url, headers=headers, params=params)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            data = result.get("data", [])
            print(f"✅ 返回数据条数: {len(data)}")
            
            if len(data) > 0:
                # 检查第一条数据
                first_item = data[0]
                print(f"\n第一条数据示例:")
                print(json.dumps(first_item, ensure_ascii=False, indent=2))
                
                # 检查是否包含 institutionLevel 字段
                if "institutionLevel" in first_item:
                    print(f"\n✅ 包含 institutionLevel 字段")
                    print(f"   机构名称: {first_item.get('institutionName')}")
                    print(f"   机构等级: {first_item.get('institutionLevel')}")
                else:
                    print(f"\n❌ 缺少 institutionLevel 字段")
                
                # 统计有多少条数据有机构等级
                with_level = sum(1 for item in data if item.get("institutionLevel"))
                print(f"\n统计: {with_level}/{len(data)} 条数据有机构等级")
            else:
                print("⚠️  返回数据为空")
        else:
            print(f"❌ API返回失败: {result.get('message')}")
    else:
        print(f"❌ 请求失败: {response.text}")
    
    # 测试2: 按组别筛选
    print("\n" + "="*60)
    print("测试2: 按组别筛选（综合组）")
    print("="*60)
    params = {
        "competitionId": 21,
        "groupType": "COMPREHENSIVE"
    }
    response = requests.get(url, headers=headers, params=params)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            data = result.get("data", [])
            print(f"✅ 返回数据条数: {len(data)}")
            
            if len(data) > 0:
                first_item = data[0]
                if "institutionLevel" in first_item:
                    print(f"✅ 包含 institutionLevel 字段")
                    print(f"   机构名称: {first_item.get('institutionName')}")
                    print(f"   机构等级: {first_item.get('institutionLevel')}")
                else:
                    print(f"❌ 缺少 institutionLevel 字段")
        else:
            print(f"❌ API返回失败: {result.get('message')}")
    else:
        print(f"❌ 请求失败: {response.text}")

def main():
    print("="*60)
    print("测试书审分组筛选接口 - 机构等级字段")
    print("="*60)
    
    # 登录
    token = login()
    if not token:
        print("❌ 无法获取token，测试终止")
        return
    
    # 测试筛选接口
    test_filter_api(token)
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)

if __name__ == "__main__":
    main()
