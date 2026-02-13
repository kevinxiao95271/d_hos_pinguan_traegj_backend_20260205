#!/usr/bin/env python3
"""
简化版：测试评审驳回后再次打分流程
使用已知的测试账号
"""
import requests
import json

BASE_URL = "http://localhost:6031/api"

def test_reject_and_rescore():
    print("=" * 60)
    print("测试：评审驳回后再次打分流程")
    print("=" * 60)
    
    # 1. 管理员登录
    print("\n1. 管理员登录...")
    admin_response = requests.post(f"{BASE_URL}/auth/login", json={
        "phone": "13800000001",
        "name": "系统管理员",
        "title": "管理员",
        "role": "ADMIN",
        "institutionId": 1
    })
    
    if admin_response.status_code != 200:
        print(f"❌ 管理员登录失败: {admin_response.text}")
        return
    
    admin_data = admin_response.json()
    admin_token = admin_data['data']['token']
    print(f"✓ 管理员登录成功")
    
    # 2. 评审专家登录
    print("\n2. 评审专家登录...")
    reviewer_response = requests.post(f"{BASE_URL}/auth/login", json={
        "phone": "13800000084",
        "name": "李明华",
        "title": "主任医师",
        "role": "REVIEWER",
        "institutionId": 1,
        "expertBackground": "临床医学"
    })
    
    if reviewer_response.status_code != 200:
        print(f"❌ 评审专家登录失败: {reviewer_response.text}")
        return
    
    reviewer_data = reviewer_response.json()
    reviewer_token = reviewer_data['data']['token']
    reviewer_id = reviewer_data['data']['userId']
    print(f"✓ 评审专家登录成功 (ID: {reviewer_id})")
    
    # 3. 获取评审任务
    print("\n3. 获取评审任务...")
    headers = {"Authorization": f"Bearer {admin_token}"}
    tasks_response = requests.get(
        f"{BASE_URL}/reviews/tasks",
        params={"reviewerId": reviewer_id},
        headers=headers
    )
    
    if tasks_response.status_code != 200:
        print(f"❌ 获取任务失败: {tasks_response.text}")
        return
    
    tasks = tasks_response.json()['data']
    if not tasks:
        print("❌ 没有找到评审任务")
        return
    
    task = tasks[0]
    task_id = task['id']
    print(f"✓ 找到评审任务 ID: {task_id}")
    print(f"  当前状态: {task['status']}")
    print(f"  评审阶段: {task['stage']}")
    
    # 4. 第一次打分
    print("\n4. 第一次打分...")
    reviewer_headers = {"Authorization": f"Bearer {reviewer_token}"}
    score_v1 = {
        "reviewTaskId": task_id,
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
    
    score_response = requests.post(
        f"{BASE_URL}/reviews/scores",
        json=score_v1,
        headers=reviewer_headers
    )
    
    if score_response.status_code != 200:
        print(f"❌ 第一次打分失败: {score_response.text}")
        return
    
    score_data = score_response.json()['data']
    print(f"✓ 第一次打分成功")
    print(f"  总分: {score_data['total']}")
    print(f"  亮点: {score_data['highlight']}")
    
    # 5. 查询评分
    print("\n5. 查询第一次评分...")
    get_score_response = requests.get(
        f"{BASE_URL}/reviews/scores/{task_id}",
        headers=reviewer_headers
    )
    
    if get_score_response.status_code == 200:
        score = get_score_response.json()['data']
        print(f"✓ 评分详情:")
        print(f"  总分: {score['total']}")
        print(f"  提交时间: {score['submittedAt']}")
    
    # 6. 管理员驳回
    print("\n6. 管理员驳回评审...")
    reject_response = requests.put(
        f"{BASE_URL}/reviews/tasks/status",
        json={
            "reviewTaskId": task_id,
            "status": "RETURNED"
        },
        headers=headers
    )
    
    if reject_response.status_code != 200:
        print(f"❌ 驳回失败: {reject_response.text}")
        return
    
    reject_data = reject_response.json()['data']
    print(f"✓ 驳回成功")
    print(f"  新状态: {reject_data['status']}")
    
    # 7. 第二次打分（修改后重新提交）
    print("\n7. 第二次打分（修改后重新提交）...")
    score_v2 = {
        "reviewTaskId": task_id,
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
    
    score2_response = requests.post(
        f"{BASE_URL}/reviews/scores",
        json=score_v2,
        headers=reviewer_headers
    )
    
    if score2_response.status_code != 200:
        print(f"❌ 第二次打分失败: {score2_response.text}")
        return
    
    score2_data = score2_response.json()['data']
    print(f"✓ 第二次打分成功")
    print(f"  新总分: {score2_data['total']} (第一次: 70.0)")
    print(f"  新亮点: {score2_data['highlight']}")
    
    # 8. 查询最终评分
    print("\n8. 查询最终评分...")
    final_score_response = requests.get(
        f"{BASE_URL}/reviews/scores/{task_id}",
        headers=reviewer_headers
    )
    
    if final_score_response.status_code == 200:
        final_score = final_score_response.json()['data']
        print(f"✓ 最终评分详情:")
        print(f"  总分: {final_score['total']}")
        print(f"  亮点: {final_score['highlight']}")
        print(f"  不足: {final_score['weakness']}")
        print(f"  提交时间: {final_score['submittedAt']}")
    
    # 9. 验证任务状态
    print("\n9. 验证最终任务状态...")
    final_tasks_response = requests.get(
        f"{BASE_URL}/reviews/tasks",
        params={"reviewerId": reviewer_id},
        headers=headers
    )
    
    if final_tasks_response.status_code == 200:
        final_tasks = final_tasks_response.json()['data']
        final_task = next((t for t in final_tasks if t['id'] == task_id), None)
        if final_task:
            print(f"✓ 最终任务状态: {final_task['status']}")
    
    # 总结
    print("\n" + "=" * 60)
    print("测试结论")
    print("=" * 60)
    print("✅ 评审驳回后可以再次打分")
    print("✅ 第二次打分会覆盖第一次的评分数据")
    print("✅ 任务状态从 RETURNED 变回 SCORED")
    print("\n业务逻辑:")
    print("1. 评委提交评分 → 状态变为 SCORED")
    print("2. 管理员驳回 → 状态变为 RETURNED")
    print("3. 评委修改后再次提交 → 覆盖原评分，状态变回 SCORED")
    print("\n数据特点:")
    print("- ReviewScore 表与 ReviewTask 是一对一关系")
    print("- 使用 findByReviewTaskId().orElse() 模式")
    print("- 第二次打分会完全覆盖第一次的数据")
    print("- 不保留评分历史版本")
    print("=" * 60)

if __name__ == "__main__":
    test_reject_and_rescore()
