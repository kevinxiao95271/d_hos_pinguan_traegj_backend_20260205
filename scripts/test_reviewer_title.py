#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
评委职称字段测试
验证所有相关API是否返回reviewerTitle字段
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import requests
import json
import time

BASE_URL = "http://localhost:6031"

def wait_for_server():
    """等待服务器启动"""
    print("等待服务器启动...")
    for i in range(15):
        try:
            response = requests.get(f"{BASE_URL}/api/competitions", timeout=3)
            if response.status_code in [200, 401]:
                print(f"✓ 服务器已启动 (尝试 {i+1}/15)\n")
                return True
        except:
            pass
        time.sleep(4)
    print("✗ 服务器启动超时\n")
    return False

def login():
    """登录获取token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "phone": "13800138001",
        "name": "Li Minghua",
        "title": "Professor",
        "role": "REVIEWER",
        "institutionId": 2
    })
    if response.status_code == 200:
        return response.json()["data"]["token"]
    raise Exception(f"登录失败: {response.status_code}")

def print_section(title):
    """打印分隔符"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def test_review_tasks_stage(token):
    """测试1：评审任务列表 - 按阶段查询"""
    print_section("测试1：GET /api/reviews/tasks/stage")
    
    response = requests.get(
        f"{BASE_URL}/api/reviews/tasks/stage",
        params={"competitionId": 21, "stage": "BOOK"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        print(f"✓ 请求成功，返回 {len(data)} 条数据\n")
        
        if len(data) > 0:
            task = data[0]
            print("首条数据字段:")
            print(f"  - id: {task.get('id')}")
            print(f"  - projectName: {task.get('projectName')}")
            print(f"  - reviewerId: {task.get('reviewerId')}")
            print(f"  - reviewerName: {task.get('reviewerName')}")
            print(f"  - reviewerTitle: {task.get('reviewerTitle')} {'✓' if task.get('reviewerTitle') else '✗ 缺失'}")
            print(f"  - reviewerInstitutionName: {task.get('reviewerInstitutionName')}")
            
            if task.get('reviewerTitle'):
                print(f"\n✓ 验证通过：reviewerTitle 字段存在")
                return True
            else:
                print(f"\n✗ 验证失败：reviewerTitle 字段缺失")
                return False
        else:
            print("⚠️  无数据，无法验证")
            return False
    else:
        print(f"✗ 请求失败：{response.status_code}")
        return False

def test_review_tasks_paginated(token):
    """测试2：评审任务列表 - 分页查询"""
    print_section("测试2：GET /api/reviews/tasks/stage（分页）")
    
    response = requests.get(
        f"{BASE_URL}/api/reviews/tasks/stage",
        params={"competitionId": 21, "stage": "BOOK", "page": 1, "size": 2},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        content = data.get('content', [])
        print(f"✓ 请求成功，返回 {len(content)} 条数据\n")
        
        if len(content) > 0:
            task = content[0]
            print("首条数据字段:")
            print(f"  - reviewerName: {task.get('reviewerName')}")
            print(f"  - reviewerTitle: {task.get('reviewerTitle')} {'✓' if task.get('reviewerTitle') else '✗ 缺失'}")
            
            if task.get('reviewerTitle'):
                print(f"\n✓ 验证通过：分页查询也返回reviewerTitle")
                return True
            else:
                print(f"\n✗ 验证失败：分页查询缺少reviewerTitle")
                return False
        else:
            print("⚠️  无数据，无法验证")
            return False
    else:
        print(f"✗ 请求失败：{response.status_code}")
        return False

def test_registration_score_detail(token):
    """测试3：项目评分详情（包含评委职称）"""
    print_section("测试3：GET /api/registrations/{id}/score-detail")
    
    # 先获取一个已评分的项目ID
    response = requests.get(
        f"{BASE_URL}/api/reviews/tasks/stage",
        params={"competitionId": 21, "stage": "BOOK"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code != 200 or not response.json()["data"]:
        print("⚠️  无法获取测试数据")
        return False
    
    registration_id = response.json()["data"][0].get("registrationId")
    
    # 获取评分详情
    response = requests.get(
        f"{BASE_URL}/api/registrations/{registration_id}/score-detail",
        params={"stage": "BOOK"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        reviewers = data.get("reviewerScores", [])
        print(f"✓ 请求成功，返回 {len(reviewers)} 个评委评分\n")
        
        if len(reviewers) > 0:
            reviewer = reviewers[0]
            print("首个评委信息:")
            print(f"  - reviewerId: {reviewer.get('reviewerId')}")
            print(f"  - reviewerName: {reviewer.get('reviewerName')}")
            print(f"  - reviewerTitle: {reviewer.get('reviewerTitle')} {'✓' if reviewer.get('reviewerTitle') else '✗ 缺失'}")
            print(f"  - reviewerInstitutionName: {reviewer.get('reviewerInstitutionName')}")
            
            if reviewer.get('reviewerTitle'):
                print(f"\n✓ 验证通过：评分详情包含reviewerTitle")
                return True
            else:
                print(f"\n✗ 验证失败：评分详情缺少reviewerTitle")
                return False
        else:
            print("⚠️  该项目暂无评分")
            return False
    else:
        print(f"✗ 请求失败：{response.status_code}")
        return False

def test_feedback_by_stage(token):
    """测试4：评审反馈列表（已废弃但仍需支持）"""
    print_section("测试4：GET /api/reviews/feedback/stage")
    
    response = requests.get(
        f"{BASE_URL}/api/reviews/feedback/stage",
        params={"competitionId": 21, "stage": "BOOK"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        print(f"✓ 请求成功，返回 {len(data)} 条数据\n")
        
        if len(data) > 0:
            feedback = data[0]
            print("首条数据字段:")
            print(f"  - reviewerName: {feedback.get('reviewerName')}")
            print(f"  - reviewerTitle: {feedback.get('reviewerTitle')} {'✓' if feedback.get('reviewerTitle') else '✗ 缺失'}")
            
            if feedback.get('reviewerTitle'):
                print(f"\n✓ 验证通过：反馈列表包含reviewerTitle")
                return True
            else:
                print(f"\n✗ 验证失败：反馈列表缺少reviewerTitle")
                return False
        else:
            print("⚠️  无已评分数据")
            return False
    else:
        print(f"✗ 请求失败：{response.status_code}")
        return False

def test_all_stages(token):
    """测试5：所有评审阶段"""
    print_section("测试5：所有评审阶段（BOOK/INTERVIEW/FINAL）")
    
    stages = ["BOOK", "INTERVIEW", "FINAL"]
    results = {}
    
    for stage in stages:
        response = requests.get(
            f"{BASE_URL}/api/reviews/tasks/stage",
            params={"competitionId": 21, "stage": stage},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            data = response.json()["data"]
            if len(data) > 0:
                has_title = bool(data[0].get('reviewerTitle'))
                results[stage] = has_title
                status = "✓" if has_title else "✗"
                print(f"  {status} {stage:12} - {len(data):2} 条数据, reviewerTitle: {data[0].get('reviewerTitle', '无')}")
            else:
                results[stage] = None
                print(f"  - {stage:12} - 无数据")
        else:
            results[stage] = False
            print(f"  ✗ {stage:12} - 请求失败")
    
    all_passed = all(v is True or v is None for v in results.values())
    if all_passed:
        print(f"\n✓ 验证通过：所有阶段都正确返回reviewerTitle")
        return True
    else:
        print(f"\n✗ 验证失败：部分阶段缺少reviewerTitle")
        return False

def main():
    print_section("评委职称字段完整测试")
    
    if not wait_for_server():
        print("服务器未启动，测试终止")
        return
    
    try:
        token = login()
        print("✓ 登录成功\n")
        
        results = []
        results.append(("评审任务列表", test_review_tasks_stage(token)))
        results.append(("分页查询", test_review_tasks_paginated(token)))
        results.append(("评分详情", test_registration_score_detail(token)))
        results.append(("评审反馈", test_feedback_by_stage(token)))
        results.append(("所有阶段", test_all_stages(token)))
        
        print_section("测试结果汇总")
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for name, result in results:
            status = "✓ 通过" if result else "✗ 失败"
            print(f"  {status}  {name}")
        
        print(f"\n总计: {passed}/{total} 通过")
        
        if passed == total:
            print("\n🎉 所有测试通过！reviewerTitle字段已正确返回。")
        else:
            print(f"\n⚠️  有 {total - passed} 个测试失败，请检查。")
        
    except Exception as e:
        print(f"\n✗ 测试失败：{str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
