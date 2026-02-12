#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试组别统计API
"""

import requests
import json

BASE_URL = "http://localhost:8080"

def test_stats_api():
    """测试统计API"""
    print("=" * 80)
    print("测试组别统计API")
    print("=" * 80)
    
    # 获取统计数据
    url = f"{BASE_URL}/api/admin/stats/summary"
    
    print(f"\n请求: GET {url}")
    
    try:
        response = requests.get(url)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                result = data.get('data', {})
                
                print(f"\n[总体统计]")
                print(f"  赛事ID: {result.get('competitionId')}")
                print(f"  赛事名称: {result.get('competitionName')}")
                print(f"  总项目数: {result.get('registrationCount')}")
                print(f"  总机构数: {result.get('institutionCount')}")
                
                # 显示组别统计
                group_stats = result.get('groupTypeStats', [])
                if group_stats:
                    print(f"\n[组别统计]")
                    print(f"{'组别':<15} {'机构数':<10} {'项目数':<10} {'项目占比':<12} {'平均项目/机构':<15}")
                    print("-" * 70)
                    
                    for stat in group_stats:
                        group_name = stat.get('groupTypeName', '')
                        inst_count = stat.get('institutionCount', 0)
                        proj_count = stat.get('projectCount', 0)
                        percentage = stat.get('projectPercentage', 0.0)
                        avg_proj = stat.get('avgProjectsPerInstitution', 0.0)
                        
                        print(f"{group_name:<15} {inst_count:<10} {proj_count:<10} {percentage:<11.1f}% {avg_proj:<15.2f}")
                
                # 完整JSON输出
                print(f"\n[完整响应]")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(f"API返回失败: {data.get('message')}")
        else:
            print(f"请求失败: {response.text}")
    
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_stats_api()
