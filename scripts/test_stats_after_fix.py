#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试修正后的统计接口"""

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

def test_stats_api(token):
    """测试统计接口"""
    url = f"{BASE_URL}/api/admin/stats/summary"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    print("\n" + "="*80)
    print("测试统计汇总接口（修正后）")
    print("="*80)
    
    response = requests.get(url, headers=headers)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            data = result.get("data", {})
            print(f"\n✅ 接口调用成功\n")
            
            print(f"赛事ID: {data.get('competitionId')}")
            print(f"赛事名称: {data.get('competitionName')}")
            print(f"报名总数: {data.get('registrationCount')}")
            
            print(f"\n📊 地区分布（修正后）:")
            print("-" * 40)
            region_counts = data.get('regionCounts', {})
            if region_counts:
                # 按报名数排序
                sorted_regions = sorted(region_counts.items(), key=lambda x: x[1], reverse=True)
                total = sum(region_counts.values())
                
                for region, count in sorted_regions:
                    percentage = (count / total * 100) if total > 0 else 0
                    print(f"  {region:<10} {count:>3} 条  ({percentage:>5.1f}%)")
                
                print("-" * 40)
                print(f"  {'总计':<10} {total:>3} 条  (100.0%)")
                
                # 检查是否有"未知"或"其他"
                if "未知" in region_counts:
                    print(f"\n⚠️  发现 {region_counts['未知']} 条地区为'未知'的报名")
                else:
                    print(f"\n✅ 没有地区为'未知'的报名")
                
                # 验证杭州数量
                hangzhou_count = region_counts.get('杭州', 0)
                if hangzhou_count >= 15:
                    print(f"✅ 杭州报名数正常: {hangzhou_count} 条（包含省级医院）")
                else:
                    print(f"⚠️  杭州报名数偏低: {hangzhou_count} 条")
                
            else:
                print("  无数据")
            
            print(f"\n📈 主题类型分布:")
            print("-" * 40)
            subject_type_counts = data.get('subjectTypeCounts', {})
            if subject_type_counts:
                sorted_subjects = sorted(subject_type_counts.items(), key=lambda x: x[1], reverse=True)
                for subject_type, count in sorted_subjects:
                    print(f"  {subject_type:<15} {count:>3} 条")
            else:
                print("  无数据")
            
            # 完整JSON输出
            print(f"\n📄 完整返回数据:")
            print(json.dumps(data, ensure_ascii=False, indent=2))
            
        else:
            print(f"❌ API返回失败: {result.get('message')}")
    else:
        print(f"❌ 请求失败: {response.text}")

def main():
    print("="*80)
    print("测试修正后的统计接口")
    print("="*80)
    
    # 登录
    token = login()
    if not token:
        print("❌ 无法获取token，测试终止")
        return
    
    # 测试统计接口
    test_stats_api(token)
    
    print("\n" + "="*80)
    print("测试完成")
    print("="*80)

if __name__ == "__main__":
    main()
