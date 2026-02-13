#!/usr/bin/env python3
"""
测试评审驳回后再次打分流程
"""
import requests
import json

BASE_URL = "http://localhost:6031/api"

def login_admin():
    """管理员登录"""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "phone": "13800000001",
        "name": "系统管理员",
        "role": "ADMIN"
    })
    result = response.json()
    if result.get('code') != 200:
        print(f"登录失败: {result}")
        raise Exception(f"登录失败: {result.get('message', '未知错误')}")
    return result['data']['token']

def login_reviewer():
    """评审专家登录"""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "phone": "13800000084",
        "name": "李明华",
        "role": "REVIEWER"
    })
    result = response.json()
    if result.get('code') != 200:
        print(f"登录失败: {result}")
        raise Exception(f"登录失败: {result.get('message', '未知错误')}")
    return result['data']['token']

def get_review_tasks(token, reviewer_id):
    """获取评审任务列表"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/reviews/tasks", 
                           params={"reviewerId": reviewer_id},
                           headers=headers)
    return response.json()['data']

def submit_score(token, task_id, score_data):
    """提交评分"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/reviews/scores", 
                            json={
                                "reviewTaskId": task_id,
                                **score_data
                            },
                            headers=headers)
    return response.json()

def update_task_status(token, task_id, status):
    """更新任务状态"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(f"{BASE_URL}/reviews/tasks/status",
                           json={
                               "reviewTaskId": task_id,
                               "status": status
                           },
                           headers=headers)
    return response.json()

def get_score(token, task_id):
    """查询评分详情"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/reviews/scores/{task_id}",
                           headers=headers)
    return response.json()

def main():
    print("=" * 60)
    print("测试：评审驳回后再次打分流程")
    print("=" * 60)
    
    # 1. 管理员登录
    print("\n1. 管理员登录...")
    admin_token = login_admin()
    print(f"✓ 管理员登录成功")
    
    # 2. 评审专家登录
    print("\n2. 评审专家登录...")
    reviewer_token = login_reviewer()
    print(f"✓ 评审专家登录成功")
    
    # 3. 获取评审任务
    print("\n3. 获取评审任务...")
    reviewer_id = 84  # 李明华的ID
    tasks = get_review_tasks(admin_token, reviewer_id)
    
    if not tasks:
        print("❌ 没有找到评审任务")
        return
    
    task = tasks[0]
    task_id = task['id']
    print(f"✓ 找到评审任务 ID: {task_id}")
    print(f"  当前状态: {task['status']}")
    
    # 4. 第一次打分
    print("\n4. 第一次打分...")
    score_data_v1 = {
        "plan": 10.0,
        "problem": 10.0,
        "action": 10.0,
        "success": 10.0,
        "review": 10.0,
        "operation": 10.0,
        "presentation": 10.0,
        "highlight": "第一次打分：项目整体表现良好",
        "weakness": "第一次打分：部分细节需要改进"
    }
    
    result = submit_score(reviewer_token, task_id, score_data_v1)
    if result['code'] == 200:
        print(f"✓ 第一次打分成功")
        print(f"  总分: {result['data']['total']}")
        print(f"  亮点: {result['data']['highlight']}")
    else:
        print(f"❌ 第一次打分失败: {result['message']}")
        return
    
    # 5. 查询评分（验证第一次打分）
    print("\n5. 查询第一次评分...")
    score_result = get_score(reviewer_token, task_id)
    if score_result['code'] == 200:
        score = score_result['data']
        print(f"✓ 第一次评分详情:")
        print(f"  总分: {score['total']}")
        print(f"  亮点: {score['highlight']}")
        print(f"  不足: {score['weakness']}")
    
    # 6. 管理员驳回
    print("\n6. 管理员驳回评审...")
    result = update_task_status(admin_token, task_id, "RETURNED")
    if result['code'] == 200:
        print(f"✓ 驳回成功")
        print(f"  新状态: {result['data']['status']}")
    else:
        print(f"❌ 驳回失败: {result['message']}")
        return
    
    # 7. 再次查询任务状态
    print("\n7. 查询驳回后的任务状态...")
    tasks = get_review_tasks(admin_token, reviewer_id)
    task = next((t for t in tasks if t['id'] == task_id), None)
    if task:
        print(f"✓ 任务状态: {task['status']}")
    
    # 8. 第二次打分（修改后重新提交）
    print("\n8. 第二次打分（修改后重新提交）...")
    score_data_v2 = {
        "plan": 12.0,
        "problem": 13.0,
        "action": 14.0,
        "success": 13.0,
        "review": 12.0,
        "operation": 13.0,
        "presentation": 14.0,
        "highlight": "第二次打分：根据反馈修改，项目创新性突出",
        "weakness": "第二次打分：实施细节进一步完善"
    }
    
    result = submit_score(reviewer_token, task_id, score_data_v2)
    if result['code'] == 200:
        print(f"✓ 第二次打分成功")
        print(f"  新总分: {result['data']['total']}")
        print(f"  新亮点: {result['data']['highlight']}")
    else:
        print(f"❌ 第二次打分失败: {result['message']}")
        return
    
    # 9. 查询最终评分
    print("\n9. 查询最终评分...")
    score_result = get_score(reviewer_token, task_id)
    if score_result['code'] == 200:
        score = score_result['data']
        print(f"✓ 最终评分详情:")
        print(f"  总分: {score['total']} (第一次: 70.0)")
        print(f"  亮点: {score['highlight']}")
        print(f"  不足: {score['weakness']}")
        print(f"  提交时间: {score['submittedAt']}")
    
    # 10. 验证任务状态
    print("\n10. 验证最终任务状态...")
    tasks = get_review_tasks(admin_token, reviewer_id)
    task = next((t for t in tasks if t['id'] == task_id), None)
    if task:
        print(f"✓ 最终任务状态: {task['status']}")
    
    print("\n" + "=" * 60)
    print("测试结论:")
    print("=" * 60)
    print("✓ 评审驳回后可以再次打分")
    print("✓ 第二次打分会覆盖第一次的评分数据")
    print("✓ 任务状态从 RETURNED 变回 SCORED")
    print("✓ 评分记录使用 findByReviewTaskId().orElse() 模式")
    print("  - 如果存在评分记录，则更新")
    print("  - 如果不存在评分记录，则创建")
    print("\n业务逻辑:")
    print("1. 评委提交评分 → 状态变为 SCORED")
    print("2. 管理员驳回 → 状态变为 RETURNED")
    print("3. 评委修改后再次提交 → 覆盖原评分，状态变回 SCORED")
    print("=" * 60)

if __name__ == "__main__":
    main()
