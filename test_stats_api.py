#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试统计接口"""

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
    print("测试统计汇总接口")
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
            print(f"报名总数: {data.get('totalRegistrations')}")
            print(f"品管工具数: {data.get('totalToolTypes')}")
            print(f"评委数: {data.get('totalReviewers')}")
            print(f"评委机构数: {data.get('totalReviewerInstitutions')}")
            print(f"书审任务数: {data.get('totalBookReviewTasks')}")
            print(f"未评分数: {data.get('unscoredBookReviewTasks')}")
            
            print(f"\n地区分布:")
            region_counts = data.get('regionCounts', {})
            if region_counts:
                for region, count in sorted(region_counts.items(), key=lambda x: x[1], reverse=True):
                    print(f"  {region}: {count} 条报名")
            else:
                print("  无数据")
            
            print(f"\n主题类型分布:")
            subject_type_counts = data.get('subjectTypeCounts', {})
            if subject_type_counts:
                for subject_type, count in sorted(subject_type_counts.items(), key=lambda x: x[1], reverse=True):
                    print(f"  {subject_type}: {count} 条报名")
            else:
                print("  无数据")
            
            print(f"\n平均分数:")
            print(f"  计划 (Plan): {data.get('avgPlan', 0):.2f}")
            print(f"  问题 (Problem): {data.get('avgProblem', 0):.2f}")
            print(f"  行动 (Action): {data.get('avgAction', 0):.2f}")
            print(f"  成功 (Success): {data.get('avgSuccess', 0):.2f}")
            print(f"  评审 (Review): {data.get('avgReview', 0):.2f}")
            print(f"  操作 (Operation): {data.get('avgOperation', 0):.2f}")
            print(f"  展示 (Presentation): {data.get('avgPresentation', 0):.2f}")
            
            # 完整JSON输出
            print(f"\n完整返回数据:")
            print(json.dumps(data, ensure_ascii=False, indent=2))
            
        else:
            print(f"❌ API返回失败: {result.get('message')}")
    else:
        print(f"❌ 请求失败: {response.text}")

def main():
    print("="*80)
    print("测试报名统计接口")
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
