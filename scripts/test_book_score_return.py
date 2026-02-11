#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试书审得分驳回功能"""

import requests
import json

BASE_URL = "http://localhost:6031"

def test_return_score():
    """测试驳回评分功能"""
    print("=" * 80)
    print("测试书审得分驳回功能")
    print("=" * 80)
    
    # 1. 登录
    print("\n【步骤1】登录组委会管理员")
    login_data = {
        "phone": "13800000041",
        "name": "CommitteeAdmin A",
        "role": "COMMITTEE_ADMIN"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ 登录失败: {response.status_code}")
        return
    
    result = response.json()
    if not result.get("success"):
        print(f"❌ 登录失败: {result.get('message')}")
        return
    
    token = result["data"]["token"]
    print("✅ 登录成功")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. 获取书审得分列表
    print(f"\n【步骤2】获取书审得分列表")
    
    response = requests.get(
        f"{BASE_URL}/api/admin/reviews/book-scores?competitionId=21",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ 获取列表失败: {response.status_code}")
        return
    
    result = response.json()
    if not result.get("success"):
        print(f"❌ 获取列表失败: {result.get('message')}")
        return
    
    data = result["data"]
    print(f"✅ 获取成功，共 {len(data)} 条记录")
    
    if not data:
        print("  (无数据可测试)")
        return
    
    # 3. 选择第一条记录进行驳回测试
    test_item = data[0]
    task_id = test_item['taskId']
    project_name = test_item['projectName']
    reviewer_name = test_item['reviewerName']
    total_score = test_item['total']
    
    print(f"\n【步骤3】准备驳回评分")
    print(f"  任务ID: {task_id}")
    print(f"  项目: {project_name}")
    print(f"  评委: {reviewer_name}")
    print(f"  总分: {total_score}")
    
    # 4. 执行驳回操作
    print(f"\n【步骤4】执行驳回操作")
    
    return_data = {
        "reviewTaskId": task_id
    }
    
    response = requests.post(
        f"{BASE_URL}/api/admin/reviews/scores/return",
        headers=headers,
        json=return_data
    )
    
    if response.status_code != 200:
        print(f"❌ 驳回失败: {response.status_code}")
        print(response.text)
        return
    
    result = response.json()
    if not result.get("success"):
        print(f"❌ 驳回失败: {result.get('message')}")
        return
    
    print("✅ 驳回成功")
    print(f"  返回数据: {json.dumps(result['data'], indent=2, ensure_ascii=False)}")
    
    # 5. 验证驳回后的状态
    print(f"\n【步骤5】验证驳回后的状态")
    
    response = requests.get(
        f"{BASE_URL}/api/admin/reviews/book-scores?competitionId=21",
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            new_data = result["data"]
            print(f"✅ 当前列表记录数: {len(new_data)} (原 {len(data)})")
            
            # 检查被驳回的记录是否还在列表中
            found = any(item['taskId'] == task_id for item in new_data)
            if found:
                print(f"⚠️  被驳回的任务 {task_id} 仍在列表中（状态可能已变更）")
            else:
                print(f"✅ 被驳回的任务 {task_id} 已从列表中移除")
    
    # 6. 查询所有任务（包括RETURNED状态）
    print(f"\n【步骤6】查询所有任务状态")
    
    response = requests.get(
        f"{BASE_URL}/api/admin/reviews/tasks?competitionId=21&stage=BOOK",
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            all_tasks = result["data"]
            returned_task = next((t for t in all_tasks if t['id'] == task_id), None)
            if returned_task:
                print(f"✅ 找到被驳回的任务")
                print(f"  任务ID: {returned_task['id']}")
                print(f"  状态: {returned_task['status']}")
                print(f"  项目: {returned_task['projectName']}")
            else:
                print(f"⚠️  未找到任务 {task_id}")
    
    print("\n" + "=" * 80)
    print("✅ 测试完成")
    print("=" * 80)
    print("\n说明:")
    print("  - 驳回后，任务状态变为 RETURNED")
    print("  - 评分记录被删除")
    print("  - 书审得分列表中不再显示该记录（因为只显示SCORED状态）")
    print("  - 评委可以重新评分")

if __name__ == '__main__':
    test_return_score()
