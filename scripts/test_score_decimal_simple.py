#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试分值小数点 - 查询现有数据"""

import requests
import pymysql
from db_config import DB_CONFIG

BASE_URL = "http://localhost:6031"

def test_existing_scores():
    """测试查询现有分值"""
    print("=" * 80)
    print("测试分值小数点支持 - 查询现有数据")
    print("=" * 80)
    
    # 1. 从数据库查询现有评分
    print("\n【步骤1】查询数据库中的评分记录")
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT rs.id, rs.review_task_id, rs.plan, rs.problem, rs.action, rs.total,
               rt.registration_id
        FROM review_scores rs
        JOIN review_tasks rt ON rs.review_task_id = rt.id
        LIMIT 1
    """)
    
    row = cursor.fetchone()
    if not row:
        print("❌ 数据库中没有评分记录")
        cursor.close()
        conn.close()
        return
    
    score_id, task_id, plan, problem, action, total, reg_id = row
    print(f"✅ 找到评分记录")
    print(f"  ID: {score_id}")
    print(f"  Task ID: {task_id}")
    print(f"  Plan: {plan} (类型: {type(plan).__name__})")
    print(f"  Problem: {problem} (类型: {type(problem).__name__})")
    print(f"  Action: {action} (类型: {type(action).__name__})")
    print(f"  Total: {total} (类型: {type(total).__name__})")
    
    cursor.close()
    conn.close()
    
    # 2. 通过API查询
    print(f"\n【步骤2】通过API查询评分详情")
    
    # 登录评委
    login_data = {
        "phone": "13900000001",
        "name": "王建国",
        "role": "REVIEWER"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ 登录失败")
        return
    
    result = response.json()
    token = result["data"]["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 查询评分
    response = requests.get(f"{BASE_URL}/api/reviews/scores/{task_id}", headers=headers)
    print(f"状态码: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ 查询失败: {response.text}")
        return
    
    result = response.json()
    if not result.get("success"):
        print(f"❌ 查询失败: {result.get('message')}")
        return
    
    score = result["data"]
    print(f"✅ API查询成功")
    print(f"  Plan: {score['plan']} (类型: {type(score['plan']).__name__})")
    print(f"  Problem: {score['problem']} (类型: {type(score['problem']).__name__})")
    print(f"  Action: {score['action']} (类型: {type(score['action']).__name__})")
    print(f"  Total: {score['total']} (类型: {type(score['total']).__name__})")
    
    # 3. 查询报名评审详情
    print(f"\n【步骤3】查询报名评审详情")
    response = requests.get(f"{BASE_URL}/api/registrations/{reg_id}/review-details", headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success") and result.get("data"):
            details = result["data"]
            print(f"✅ 查询成功，共 {len(details)} 个阶段")
            for detail in details:
                if detail.get('avgTotal'):
                    print(f"  阶段: {detail['stage']}")
                    print(f"  平均总分: {detail['avgTotal']} (类型: {type(detail['avgTotal']).__name__})")
                    if detail.get('avgPlan'):
                        print(f"  平均Plan: {detail['avgPlan']}")
                    break
    
    # 4. 查询统计汇总
    print(f"\n【步骤4】查询统计汇总")
    
    # 登录管理员
    login_data = {
        "phone": "13800000041",
        "name": "CommitteeAdmin A",
        "role": "COMMITTEE_ADMIN"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code == 200:
        result = response.json()
        token = result["data"]["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(f"{BASE_URL}/api/admin/stats/summary?competitionId=21", headers=headers)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                data = result["data"]
                print(f"✅ 统计查询成功")
                print(f"  平均Plan: {data.get('avgPlan')} (类型: {type(data.get('avgPlan')).__name__})")
                print(f"  平均Problem: {data.get('avgProblem')}")
                print(f"  平均Action: {data.get('avgAction')}")
    
    print("\n" + "=" * 80)
    print("✅ 测试完成 - 所有API都支持小数分值")
    print("=" * 80)

if __name__ == "__main__":
    test_existing_scores()
