#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证API返回的地区分布中是否有"其他"分类"""

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

def check_api_response(token):
    """检查API返回的地区分布"""
    url = f"{BASE_URL}/api/admin/stats/summary"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"competitionId": 21}
    
    print("=" * 80)
    print("验证API返回的地区分布")
    print("=" * 80)
    print(f"\n请求: GET {url}?competitionId=21\n")
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            data = result.get("data", {})
            
            print(f"赛事ID: {data.get('competitionId')}")
            print(f"赛事名称: {data.get('competitionName')}")
            print(f"报名总数: {data.get('registrationCount')}")
            
            print(f"\n📊 地区分布（API返回）:")
            print("-" * 80)
            
            region_counts = data.get('regionCounts', {})
            
            # 检查是否有"其他"、"未知"等分类
            has_other = False
            other_keys = ['其他', '未知', 'other', 'unknown', '【空值】', '']
            
            total = sum(region_counts.values())
            
            print(f"{'地区':<15} {'报名数':<10} {'占比':<10}")
            print("-" * 80)
            
            for region, count in sorted(region_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total * 100) if total > 0 else 0
                
                # 检查是否是"其他"类分类
                if region in other_keys:
                    has_other = True
                    print(f"{region:<15} {count:<10} {percentage:>5.2f}%  ⚠️  异常分类")
                else:
                    print(f"{region:<15} {count:<10} {percentage:>5.2f}%")
            
            print("-" * 80)
            print(f"{'总计':<15} {total:<10} 100.00%")
            
            print(f"\n完整的regionCounts对象:")
            print(json.dumps(region_counts, ensure_ascii=False, indent=2))
            
            # 验证结果
            print("\n" + "=" * 80)
            print("验证结果")
            print("=" * 80)
            
            if has_other:
                print("❌ 发现异常分类（其他/未知）")
                print("   请检查后端逻辑")
            else:
                print("✅ 所有地区都是浙江省11个地级市")
                print("✅ 没有'其他'或'未知'分类")
            
            # 检查是否所有地区都是标准地区
            standard_regions = {'杭州', '宁波', '温州', '绍兴', '嘉兴', '湖州', '金华', '衢州', '舟山', '台州', '丽水'}
            non_standard = set(region_counts.keys()) - standard_regions
            
            if non_standard:
                print(f"\n⚠️  发现非标准地区名称: {non_standard}")
            else:
                print("\n✅ 所有地区名称都是标准的浙江省地级市")
            
            return region_counts
        else:
            print(f"❌ API返回失败: {result.get('message')}")
    else:
        print(f"❌ 请求失败: {response.status_code}")
    
    return None

def main():
    print("=" * 80)
    print("验证统计API中是否有'其他'分类")
    print("=" * 80)
    
    token = login()
    if not token:
        print("❌ 登录失败")
        return
    
    print("✅ 登录成功\n")
    
    region_counts = check_api_response(token)
    
    if region_counts:
        print("\n" + "=" * 80)
        print("结论")
        print("=" * 80)
        
        if '其他' in region_counts or '未知' in region_counts:
            print("❌ API返回的数据中包含'其他'或'未知'分类")
            print("   这是后端的问题，需要修复")
        else:
            print("✅ API返回的数据正确，没有'其他'或'未知'分类")
            print("   如果前端看到'其他'，可能是前端的分类逻辑问题")
            print("\n建议前端检查:")
            print("  1. 是否有自定义的地区分类逻辑")
            print("  2. 是否缓存了旧数据")
            print("  3. 是否查询的是正确的赛事ID")

if __name__ == "__main__":
    main()
