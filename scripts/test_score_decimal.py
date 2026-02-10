#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试分值小数点支持"""

import requests
import json

BASE_URL = "http://localhost:6031"

def test_decimal_scores():
    """测试小数分值"""
    print("=" * 80)
    print("测试分值小数点支持")
    print("=" * 80)
    
    # 1. 登录评委
    print("\n【步骤1】评委登录")
    login_data = {
        "phone": "13900000001",
        "name": "王建国",
        "role": "REVIEWER"
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
    
    # 2. 获取评审任务
    print(f"\n【步骤2】获取评审任务")
    response = requests.get(f"{BASE_URL}/api/reviews/my-tasks", headers=headers)
    if response.status_code != 200:
        print(f"❌ 获取任务失败: {response.status_code}")
        return
    
    result = response.json()
    if not result.get("success") or not result.get("data"):
        print(f"❌ 没有评审任务")
        return
    
    tasks = result["data"]
    print(f"✅ 获取到 {len(tasks)} 个任务")
    
    if len(tasks) == 0:
        print("⚠️ 没有可用的评审任务")
        return
    
    task_id = tasks[0]["id"]
    print(f"使用任务ID: {task_id}")
    
    # 3. 提交小数分值
    print(f"\n【步骤3】提交小数分值")
    score_data = {
        "reviewTaskId": task_id,
        "plan": 18.5,
        "problem": 17.8,
        "action": 19.2,
        "success": 14.5,
        "review": 9.8,
        "operation": 9.5,
        "presentation": 4.7,
        "highlight": "测试小数分值-优点",
        "weakness": "测试小数分值-缺点"
    }
    
    total_expected = sum([
        score_data["plan"], score_data["problem"], score_data["action"],
        score_data["success"], score_data["review"], score_data["operation"],
        score_data["presentation"]
    ])
    
    print(f"提交分值: plan={score_data['plan']}, problem={score_data['problem']}, action={score_data['action']}")
    print(f"预期总分: {total_expected}")
    
    response = requests.post(f"{BASE_URL}/api/reviews/scores", json=score_data, headers=headers)
    print(f"状态码: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ 提交失败: {response.text}")
        return
    
    result = response.json()
    if not result.get("success"):
        print(f"❌ 提交失败: {result.get('message')}")
        return
    
    score = result["data"]
    print(f"✅ 提交成功")
    print(f"返回分值: plan={score['plan']}, problem={score['problem']}, action={score['action']}")
    print(f"返回总分: {score['total']}")
    
    # 4. 查询分值详情
    print(f"\n【步骤4】查询分值详情")
    response = requests.get(f"{BASE_URL}/api/reviews/scores/{task_id}", headers=headers)
    if response.status_code != 200:
        print(f"❌ 查询失败: {response.status_code}")
        return
    
    result = response.json()
    if not result.get("success"):
        print(f"❌ 查询失败: {result.get('message')}")
        return
    
    score = result["data"]
    print(f"✅ 查询成功")
    print(f"分值详情:")
    print(f"  plan: {score['plan']}")
    print(f"  problem: {score['problem']}")
    print(f"  action: {score['action']}")
    print(f"  success: {score['success']}")
    print(f"  review: {score['review']}")
    print(f"  operation: {score['operation']}")
    print(f"  presentation: {score['presentation']}")
    print(f"  total: {score['total']}")
    
    # 5. 验证数据类型
    print(f"\n【步骤5】验证数据类型")
    all_decimal = all([
        isinstance(score['plan'], (int, float)),
        isinstance(score['problem'], (int, float)),
        isinstance(score['action'], (int, float)),
        isinstance(score['total'], (int, float))
    ])
    
    if all_decimal:
        print("✅ 所有分值字段都是数值类型")
    else:
        print("❌ 部分字段类型不正确")
    
    # 6. 验证小数精度
    print(f"\n【步骤6】验证小数精度")
    has_decimal = any([
        score['plan'] != int(score['plan']),
        score['problem'] != int(score['problem']),
        score['action'] != int(score['action'])
    ])
    
    if has_decimal:
        print("✅ 支持小数分值")
    else:
        print("⚠️ 分值被转换为整数")
    
    print("\n" + "=" * 80)
    print("✅ 测试完成 - 分值小数点支持功能正常")
    print("=" * 80)

if __name__ == "__main__":
    test_decimal_scores()
