#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试书审得分列表API"""

import requests
import json

BASE_URL = "http://localhost:6031"

def test_book_scores():
    """测试书审得分列表"""
    print("=" * 80)
    print("测试书审得分列表API")
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
    
    # 2. 调用书审得分列表API（赛事21）
    print(f"\n【步骤2】调用书审得分列表API（赛事21）")
    
    response = requests.get(
        f"{BASE_URL}/api/admin/reviews/book-scores?competitionId=21",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ API调用失败: {response.status_code}")
        print(response.text)
        return
    
    result = response.json()
    if not result.get("success"):
        print(f"❌ API调用失败: {result.get('message')}")
        return
    
    print("✅ API调用成功")
    
    data = result["data"]
    
    # 3. 显示统计信息
    print("\n" + "=" * 80)
    print("书审得分列表")
    print("=" * 80)
    
    print(f"\n总记录数: {len(data)}")
    
    if not data:
        print("  (无数据)")
        return
    
    # 4. 显示前5条记录
    print(f"\n前5条记录:")
    print("-" * 80)
    
    for i, item in enumerate(data[:5], 1):
        print(f"\n{i}. 任务ID: {item.get('taskId')}")
        print(f"   项目名称: {item.get('projectName')}")
        print(f"   机构: {item.get('institutionName')} ({item.get('institutionLevel', '未知')})")
        print(f"   组别: {item.get('groupType')} - {item.get('groupCode')}")
        print(f"   评委: {item.get('reviewerName')} ({item.get('reviewerTitle')})")
        print(f"   评委机构: {item.get('reviewerInstitutionName')}")
        print(f"   得分: 计划{item.get('plan')} + 问题{item.get('problem')} + 行动{item.get('action')} + 成功{item.get('success')} + 评价{item.get('review')} = 总分{item.get('total')}")
        print(f"   提交时间: {item.get('submittedAt')}")
        print(f"   状态: {item.get('status')}")
    
    # 5. 统计分析
    print("\n" + "=" * 80)
    print("统计分析")
    print("=" * 80)
    
    total_scores = [item.get('total', 0) for item in data]
    if total_scores:
        print(f"\n总分统计:")
        print(f"  最高分: {max(total_scores):.1f}")
        print(f"  最低分: {min(total_scores):.1f}")
        print(f"  平均分: {sum(total_scores) / len(total_scores):.1f}")
    
    # 按评委统计
    reviewer_counts = {}
    for item in data:
        reviewer = item.get('reviewerName', '未知')
        reviewer_counts[reviewer] = reviewer_counts.get(reviewer, 0) + 1
    
    print(f"\n按评委统计:")
    for reviewer, count in sorted(reviewer_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {reviewer:20s}: {count:3d} 条")
    
    # 6. 测试筛选功能
    print("\n" + "=" * 80)
    print("测试筛选功能")
    print("=" * 80)
    
    # 按状态筛选
    print(f"\n【测试】按状态筛选 (status=SCORED)")
    response = requests.get(
        f"{BASE_URL}/api/admin/reviews/book-scores?competitionId=21&status=SCORED",
        headers=headers
    )
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print(f"✅ 筛选成功，返回 {len(result['data'])} 条记录")
        else:
            print(f"❌ 筛选失败: {result.get('message')}")
    else:
        print(f"❌ 请求失败: {response.status_code}")
    
    # 7. 显示完整响应示例
    print("\n" + "=" * 80)
    print("完整API响应示例（第1条）")
    print("=" * 80)
    if data:
        print(json.dumps(data[0], indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 80)
    print("✅ 测试完成")
    print("=" * 80)

if __name__ == '__main__':
    test_book_scores()
