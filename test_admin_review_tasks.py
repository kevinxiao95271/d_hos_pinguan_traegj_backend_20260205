#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试管理端已分配任务接口"""

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

def test_admin_review_tasks():
    """测试管理端已分配任务接口"""
    token = login()
    if not token:
        print("❌ 登录失败")
        return
    
    print("✅ 登录成功\n")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 测试书审阶段
    print("=" * 100)
    print("测试书审阶段已分配任务")
    print("=" * 100)
    
    url = f"{BASE_URL}/api/admin/reviews/tasks?competitionId=21&stage=BOOK"
    print(f"\n请求URL: {url}\n")
    
    response = requests.get(url, headers=headers)
    
    print(f"响应状态码: {response.status_code}\n")
    
    if response.status_code == 200:
        result = response.json()
        
        if result.get("success"):
            data = result.get("data", [])
            
            print(f"✅ 请求成功！")
            print(f"已分配任务数量: {len(data)}\n")
            
            if len(data) > 0:
                print("=" * 100)
                print("前5条任务详情")
                print("=" * 100)
                
                for i, task in enumerate(data[:5], 1):
                    print(f"\n任务 {i}:")
                    print(f"  任务ID: {task.get('id')}")
                    print(f"  阶段: {task.get('stage')}")
                    print(f"  状态: {task.get('status')}")
                    print(f"  创建时间: {task.get('createdAt')}")
                    print(f"\n  报名信息:")
                    print(f"    报名ID: {task.get('registrationId')}")
                    print(f"    项目名称: {task.get('projectName')}")
                    print(f"    医疗机构: {task.get('institutionName')}")
                    print(f"    组别: {task.get('groupType')}")
                    print(f"    分组: {task.get('groupCode')}")
                    print(f"\n  评委信息:")
                    print(f"    评委ID: {task.get('reviewerId')}")
                    print(f"    评委姓名: {task.get('reviewerName')}")
                    print(f"    职称: {task.get('reviewerTitle')}")
                    print(f"    评委机构: {task.get('reviewerInstitutionName')}")
                    print(f"    书审分组: {task.get('reviewerGroupCode')}")
                    print(f"    面谈分组: {task.get('interviewGroupCode')}")
                    print(f"    专家背景: {task.get('expertBackground')}")
                
                # 检查字段完整性
                print("\n" + "=" * 100)
                print("字段完整性检查")
                print("=" * 100)
                
                empty_fields = {
                    'projectName': 0,
                    'institutionName': 0,
                    'groupType': 0,
                    'groupCode': 0,
                    'reviewerName': 0,
                    'reviewerTitle': 0,
                    'reviewerInstitutionName': 0
                }
                
                for task in data:
                    for field in empty_fields.keys():
                        if not task.get(field):
                            empty_fields[field] += 1
                
                print(f"\n总任务数: {len(data)}")
                print(f"\n字段缺失统计:")
                for field, count in empty_fields.items():
                    status = "✅" if count == 0 else "⚠️"
                    print(f"  {status} {field}: {count} 条记录缺失 ({count/len(data)*100:.1f}%)")
                
                # 显示完整的JSON（第一条）
                print("\n" + "=" * 100)
                print("第一条任务的完整JSON")
                print("=" * 100)
                print(json.dumps(data[0], ensure_ascii=False, indent=2))
                
            else:
                print("⚠️  没有已分配的任务")
        else:
            print(f"❌ API返回失败: {result.get('message')}")
    else:
        print(f"❌ 请求失败: HTTP {response.status_code}")
        print(f"响应内容: {response.text}")
    
    # 测试面谈阶段
    print("\n\n" + "=" * 100)
    print("测试面谈阶段已分配任务")
    print("=" * 100)
    
    url = f"{BASE_URL}/api/admin/reviews/tasks?competitionId=21&stage=INTERVIEW"
    print(f"\n请求URL: {url}\n")
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        
        if result.get("success"):
            data = result.get("data", [])
            print(f"✅ 请求成功！")
            print(f"已分配任务数量: {len(data)}")
            
            if len(data) > 0:
                print(f"\n前3条任务:")
                for i, task in enumerate(data[:3], 1):
                    print(f"\n  {i}. {task.get('projectName')} - {task.get('institutionName')}")
                    print(f"     评委: {task.get('reviewerName')} ({task.get('reviewerTitle')}) - {task.get('reviewerInstitutionName')}")
                    print(f"     状态: {task.get('status')}")
        else:
            print(f"❌ API返回失败: {result.get('message')}")
    
    # 测试筛选功能
    print("\n\n" + "=" * 100)
    print("测试状态筛选功能")
    print("=" * 100)
    
    # 测试待评审状态
    url = f"{BASE_URL}/api/admin/reviews/tasks?competitionId=21&stage=BOOK&status=PENDING"
    print(f"\n请求URL: {url}")
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            data = result.get("data", [])
            print(f"✅ 待评审任务数量: {len(data)}")
    
    # 测试已评分状态
    url = f"{BASE_URL}/api/admin/reviews/tasks?competitionId=21&stage=BOOK&status=SCORED"
    print(f"\n请求URL: {url}")
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            data = result.get("data", [])
            print(f"✅ 已评分任务数量: {len(data)}")

if __name__ == "__main__":
    test_admin_review_tasks()
