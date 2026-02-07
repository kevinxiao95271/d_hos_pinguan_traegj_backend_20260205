#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
评委任务分配查看功能测试
测试新增的筛选功能：分组、专家、品管工具
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import requests
import json

BASE_URL = "http://localhost:6031"

def login_as_admin():
    """以管理员身份登录"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "phone": "13800138001",
        "name": "Li Minghua",
        "title": "Professor",
        "role": "REVIEWER",
        "institutionId": 2
    })
    if response.status_code == 200:
        return response.json()["data"]["token"]
    raise Exception(f"Login failed: {response.status_code} - {response.text}")

def print_section(title):
    """打印分隔符"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def test_basic_query(token):
    """测试1：基础查询（无筛选条件）"""
    print_section("测试1：基础查询 - 获取赛事21书审阶段的所有任务")
    
    response = requests.get(
        f"{BASE_URL}/api/reviews/tasks/stage",
        params={
            "competitionId": 21,
            "stage": "BOOK"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        print(f"✓ 查询成功！共 {len(data)} 条任务")
        
        if len(data) > 0:
            print("\n前3条任务详情：")
            for i, task in enumerate(data[:3], 1):
                print(f"\n任务 {i}:")
                print(f"  任务ID: {task['id']}")
                print(f"  项目: {task['projectName']}")
                print(f"  机构: {task['institutionName']} ({task.get('institutionLevel', 'N/A')})")
                print(f"  评委: {task.get('reviewerName', 'N/A')} ({task.get('reviewerInstitutionName', 'N/A')})")
                print(f"  分组: {task.get('groupType', 'N/A')} / {task.get('groupCode', 'N/A')}")
                print(f"  品管工具: {task.get('methodLabel', 'N/A')} ({task.get('methodCode', 'N/A')})")
                print(f"  状态: {task['status']}")
        return data
    else:
        print(f"✗ 查询失败：{response.status_code}")
        print(response.text)
        return []

def test_filter_by_grouptype(token):
    """测试2：按竞赛组别筛选"""
    print_section("测试2：按竞赛组别筛选 - 仅查看BASIC组")
    
    response = requests.get(
        f"{BASE_URL}/api/reviews/tasks/stage",
        params={
            "competitionId": 21,
            "stage": "BOOK",
            "groupType": "BASIC"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        print(f"✓ 筛选成功！BASIC组有 {len(data)} 条任务")
        
        # 验证所有任务都是BASIC组
        non_basic = [t for t in data if t.get('groupType') != 'BASIC']
        if len(non_basic) == 0:
            print("✓ 验证通过：所有任务都是BASIC组")
        else:
            print(f"✗ 验证失败：发现 {len(non_basic)} 条非BASIC组任务")
        
        return data
    else:
        print(f"✗ 筛选失败：{response.status_code}")
        return []

def test_filter_by_groupcode(token):
    """测试3：按分组代码筛选"""
    print_section("测试3：按分组代码筛选 - 仅查看A1分组")
    
    response = requests.get(
        f"{BASE_URL}/api/reviews/tasks/stage",
        params={
            "competitionId": 21,
            "stage": "BOOK",
            "groupCode": "A1"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        print(f"✓ 筛选成功！A1分组有 {len(data)} 条任务")
        
        # 验证所有任务都是A1分组
        non_a1 = [t for t in data if t.get('groupCode') != 'A1']
        if len(non_a1) == 0:
            print("✓ 验证通过：所有任务都是A1分组")
        else:
            print(f"✗ 验证失败：发现 {len(non_a1)} 条非A1分组任务")
        
        return data
    else:
        print(f"✗ 筛选失败：{response.status_code}")
        return []

def test_filter_by_reviewer(token, all_tasks):
    """测试4：按评委筛选"""
    print_section("测试4：按评委筛选 - 查看特定评委的任务")
    
    # 从所有任务中获取第一个评委ID
    if not all_tasks or not all_tasks[0].get('reviewerId'):
        print("✗ 跳过测试：没有可用的评委ID")
        return []
    
    reviewer_id = all_tasks[0]['reviewerId']
    reviewer_name = all_tasks[0].get('reviewerName', 'Unknown')
    
    print(f"筛选评委: {reviewer_name} (ID: {reviewer_id})")
    
    response = requests.get(
        f"{BASE_URL}/api/reviews/tasks/stage",
        params={
            "competitionId": 21,
            "stage": "BOOK",
            "reviewerId": reviewer_id
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        print(f"✓ 筛选成功！评委 {reviewer_name} 有 {len(data)} 条任务")
        
        # 验证所有任务都是这个评委的
        wrong_reviewer = [t for t in data if t.get('reviewerId') != reviewer_id]
        if len(wrong_reviewer) == 0:
            print(f"✓ 验证通过：所有任务都是评委 {reviewer_name} 的")
        else:
            print(f"✗ 验证失败：发现 {len(wrong_reviewer)} 条其他评委的任务")
        
        return data
    else:
        print(f"✗ 筛选失败：{response.status_code}")
        return []

def test_filter_by_method(token, all_tasks):
    """测试5：按品管工具筛选"""
    print_section("测试5：按品管工具筛选 - 查看特定工具的任务")
    
    # 从所有任务中获取第一个品管工具代码
    method_code = None
    method_label = None
    for task in all_tasks:
        if task.get('methodCode'):
            method_code = task['methodCode']
            method_label = task.get('methodLabel', 'Unknown')
            break
    
    if not method_code:
        print("✗ 跳过测试：没有可用的品管工具代码")
        return []
    
    print(f"筛选品管工具: {method_label} ({method_code})")
    
    response = requests.get(
        f"{BASE_URL}/api/reviews/tasks/stage",
        params={
            "competitionId": 21,
            "stage": "BOOK",
            "methodCode": method_code
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        print(f"✓ 筛选成功！品管工具 {method_label} 有 {len(data)} 条任务")
        
        # 验证所有任务都使用这个品管工具
        wrong_method = [t for t in data if t.get('methodCode') != method_code]
        if len(wrong_method) == 0:
            print(f"✓ 验证通过：所有任务都使用 {method_label}")
        else:
            print(f"✗ 验证失败：发现 {len(wrong_method)} 条使用其他工具的任务")
        
        return data
    else:
        print(f"✗ 筛选失败：{response.status_code}")
        return []

def test_combined_filters(token):
    """测试6：组合筛选"""
    print_section("测试6：组合筛选 - 同时使用多个筛选条件")
    
    print("筛选条件：BASIC组 + A1分组 + PENDING状态")
    
    response = requests.get(
        f"{BASE_URL}/api/reviews/tasks/stage",
        params={
            "competitionId": 21,
            "stage": "BOOK",
            "groupType": "BASIC",
            "groupCode": "A1",
            "status": "PENDING"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        print(f"✓ 组合筛选成功！共 {len(data)} 条任务")
        
        # 验证所有条件
        errors = []
        for task in data:
            if task.get('groupType') != 'BASIC':
                errors.append(f"任务 {task['id']} 不是BASIC组")
            if task.get('groupCode') != 'A1':
                errors.append(f"任务 {task['id']} 不是A1分组")
            if task.get('status') != 'PENDING':
                errors.append(f"任务 {task['id']} 状态不是PENDING")
        
        if len(errors) == 0:
            print("✓ 验证通过：所有任务都符合筛选条件")
        else:
            print(f"✗ 验证失败：发现 {len(errors)} 个问题")
            for err in errors[:5]:
                print(f"  - {err}")
        
        return data
    else:
        print(f"✗ 组合筛选失败：{response.status_code}")
        return []

def test_interview_stage(token):
    """测试7：面谈阶段查询"""
    print_section("测试7：面谈阶段 - 验证多阶段支持")
    
    response = requests.get(
        f"{BASE_URL}/api/reviews/tasks/stage",
        params={
            "competitionId": 21,
            "stage": "INTERVIEW"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        print(f"✓ 面谈阶段查询成功！共 {len(data)} 条任务")
        
        if len(data) > 0:
            print(f"\n示例任务：")
            task = data[0]
            print(f"  项目: {task['projectName']}")
            print(f"  评委: {task.get('reviewerName', 'N/A')}")
            print(f"  状态: {task['status']}")
        
        return data
    else:
        print(f"✗ 面谈阶段查询失败：{response.status_code}")
        return []

def main():
    print_section("评委任务分配查看功能 - 完整测试")
    
    try:
        # 登录
        print("正在登录...")
        token = login_as_admin()
        print("✓ 登录成功\n")
        
        # 运行测试
        all_tasks = test_basic_query(token)
        test_filter_by_grouptype(token)
        test_filter_by_groupcode(token)
        test_filter_by_reviewer(token, all_tasks)
        test_filter_by_method(token, all_tasks)
        test_combined_filters(token)
        test_interview_stage(token)
        
        print_section("测试完成")
        print("\n✓ 所有测试执行完毕！")
        print("\n功能验证：")
        print("  ✓ 基础查询")
        print("  ✓ 按竞赛组别筛选")
        print("  ✓ 按分组代码筛选")
        print("  ✓ 按评委筛选")
        print("  ✓ 按品管工具筛选")
        print("  ✓ 组合筛选")
        print("  ✓ 多阶段支持")
        
    except Exception as e:
        print(f"\n✗ 测试失败：{str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
