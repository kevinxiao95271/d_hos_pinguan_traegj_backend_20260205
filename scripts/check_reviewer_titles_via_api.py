#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通过API检查评委职称数据"""

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

def check_reviewers():
    """检查评委信息"""
    token = login()
    if not token:
        print("❌ 登录失败")
        return
    
    print("✅ 登录成功\n")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 获取评委列表
    print("=" * 100)
    print("获取评委列表")
    print("=" * 100)
    
    url = f"{BASE_URL}/api/admin/reviews/reviewers"
    print(f"\n请求URL: {url}\n")
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        
        if result.get("success"):
            reviewers = result.get("data", [])
            
            print(f"✅ 请求成功！")
            print(f"评委总数: {len(reviewers)}\n")
            
            # 统计职称分布
            title_counts = {}
            for reviewer in reviewers:
                title = reviewer.get('title') or '空值'
                title_counts[title] = title_counts.get(title, 0) + 1
            
            print("=" * 100)
            print("职称分布统计")
            print("=" * 100)
            
            print(f"\n{'职称':<30} {'数量':<10} {'占比':<10}")
            print("-" * 60)
            
            for title, count in sorted(title_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / len(reviewers) * 100) if len(reviewers) > 0 else 0
                print(f"{title:<30} {count:<10} {percentage:>6.2f}%")
            
            print("-" * 60)
            print(f"{'总计':<30} {len(reviewers):<10} 100.00%")
            
            # 显示前10个评委的详细信息
            print("\n" + "=" * 100)
            print("前10个评委详细信息")
            print("=" * 100)
            
            print(f"\n{'ID':<5} {'姓名':<15} {'职称':<30} {'机构':<40}")
            print("-" * 100)
            
            for reviewer in reviewers[:10]:
                print(f"{reviewer.get('id', ''):<5} {reviewer.get('name', ''):<15} "
                      f"{reviewer.get('title', '(空)'):<30} "
                      f"{reviewer.get('institutionName', '(空)'):<40}")
            
            if len(reviewers) > 10:
                print(f"\n... 还有 {len(reviewers) - 10} 个评委")
            
            # 检查是否所有评委都是 "Test Title"
            test_title_count = sum(1 for r in reviewers if r.get('title') == 'Test Title')
            
            print("\n" + "=" * 100)
            print("问题分析")
            print("=" * 100)
            
            if test_title_count == len(reviewers):
                print(f"\n⚠️  所有 {len(reviewers)} 个评委的职称都是 'Test Title'")
                print("这是测试数据，需要更新为真实的职称信息。")
            elif test_title_count > 0:
                print(f"\n⚠️  有 {test_title_count} 个评委的职称是 'Test Title' "
                      f"({test_title_count/len(reviewers)*100:.1f}%)")
                print("部分评委使用了测试数据。")
            else:
                print(f"\n✅ 没有评委使用 'Test Title'")
            
            # 检查空值
            null_title_count = sum(1 for r in reviewers if not r.get('title'))
            if null_title_count > 0:
                print(f"\n⚠️  有 {null_title_count} 个评委的职称为空 "
                      f"({null_title_count/len(reviewers)*100:.1f}%)")
            
        else:
            print(f"❌ API返回失败: {result.get('message')}")
    else:
        print(f"❌ 请求失败: HTTP {response.status_code}")
    
    # 获取已分配任务
    print("\n\n" + "=" * 100)
    print("获取已分配任务中的评委职称")
    print("=" * 100)
    
    url = f"{BASE_URL}/api/admin/reviews/tasks?competitionId=21&stage=BOOK"
    print(f"\n请求URL: {url}\n")
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        
        if result.get("success"):
            tasks = result.get("data", [])
            
            print(f"✅ 请求成功！")
            print(f"书审任务数: {len(tasks)}\n")
            
            # 统计已分配任务中的评委职称
            reviewer_titles = {}
            for task in tasks:
                reviewer_id = task.get('reviewerId')
                reviewer_name = task.get('reviewerName')
                reviewer_title = task.get('reviewerTitle') or '空值'
                
                key = f"{reviewer_id}_{reviewer_name}"
                if key not in reviewer_titles:
                    reviewer_titles[key] = {
                        'id': reviewer_id,
                        'name': reviewer_name,
                        'title': reviewer_title,
                        'task_count': 0
                    }
                reviewer_titles[key]['task_count'] += 1
            
            print("=" * 100)
            print("已分配任务的评委职称统计")
            print("=" * 100)
            
            print(f"\n{'评委ID':<10} {'姓名':<15} {'职称':<30} {'任务数':<10}")
            print("-" * 80)
            
            for reviewer in sorted(reviewer_titles.values(), 
                                  key=lambda x: x['task_count'], reverse=True):
                print(f"{reviewer['id']:<10} {reviewer['name']:<15} "
                      f"{reviewer['title']:<30} {reviewer['task_count']:<10}")
            
            # 统计职称分布
            title_dist = {}
            for reviewer in reviewer_titles.values():
                title = reviewer['title']
                title_dist[title] = title_dist.get(title, 0) + 1
            
            print("\n" + "=" * 100)
            print("已分配任务评委职称分布")
            print("=" * 100)
            
            print(f"\n{'职称':<30} {'评委数':<10}")
            print("-" * 50)
            
            for title, count in sorted(title_dist.items(), key=lambda x: x[1], reverse=True):
                print(f"{title:<30} {count:<10}")
            
            # 检查是否都是 Test Title
            test_title_reviewers = sum(1 for r in reviewer_titles.values() 
                                      if r['title'] == 'Test Title')
            
            print("\n" + "=" * 100)
            print("已分配任务评委职称分析")
            print("=" * 100)
            
            if test_title_reviewers == len(reviewer_titles):
                print(f"\n⚠️  所有 {len(reviewer_titles)} 个已分配任务的评委职称都是 'Test Title'")
                print("这是测试数据，需要更新为真实的职称信息。")
            elif test_title_reviewers > 0:
                print(f"\n⚠️  有 {test_title_reviewers} 个已分配任务的评委职称是 'Test Title' "
                      f"({test_title_reviewers/len(reviewer_titles)*100:.1f}%)")
    
    # 建议的职称列表
    print("\n\n" + "=" * 100)
    print("建议的职称列表")
    print("=" * 100)
    
    suggested_titles = [
        "主任医师",
        "副主任医师",
        "主治医师",
        "主任护师",
        "副主任护师",
        "主管护师",
        "教授",
        "副教授",
        "讲师",
        "研究员",
        "副研究员",
        "助理研究员"
    ]
    
    print("\n医疗系统常用职称:")
    for i, title in enumerate(suggested_titles, 1):
        print(f"  {i}. {title}")
    
    print("\n" + "=" * 100)
    print("修复建议")
    print("=" * 100)
    
    print("""
1. 如果这是测试环境，可以保持 'Test Title'

2. 如果这是生产环境，需要更新为真实职称：
   
   方法1: 通过数据库直接更新
   UPDATE user_accounts 
   SET title = '主任医师' 
   WHERE id = 6;
   
   方法2: 准备CSV文件批量更新
   格式: id,title
   6,主任医师
   17,副主任医师
   ...
   
   方法3: 如果有评委信息导入功能，重新导入正确的数据

3. 建议在评委管理界面添加职称编辑功能，方便管理员维护
""")

if __name__ == "__main__":
    check_reviewers()
