#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""直接测试项目详情API并展示完整数据"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import json

BASE = "http://localhost:6031"

print("="*80)
print("测试项目详情API - 项目ID: 106")
print("="*80)

try:
    # 登录
    print("\n[1] 登录")
    login_resp = requests.post(f"{BASE}/api/auth/login", json={
        "phone": "13800000003",
        "name": "组委会管理员",
        "role": "COMMITTEE"
    }, timeout=10)
    
    token = login_resp.json()['data']['token']
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ 登录成功")
    
    # 测试review-details API
    print("\n[2] 调用 GET /api/registrations/106/review-details")
    print("-" * 80)
    
    resp = requests.get(
        f"{BASE}/api/registrations/106/review-details",
        headers=headers,
        timeout=10
    )
    
    print(f"状态码: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"\n完整返回JSON:")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        
        print(f"\n\n{'='*80}")
        print("数据解析 - 书审阶段")
        print("="*80)
        
        review_data = data['data']
        book_stage = None
        
        for stage in review_data:
            if stage['stage'] == 'BOOK':
                book_stage = stage
                break
        
        if book_stage:
            print(f"\n分项得分:")
            print(f"  计划（Plan）: {book_stage.get('avgPlan')}")
            print(f"  问题（Problem）: {book_stage.get('avgProblem')}")
            print(f"  行动（Action）: {book_stage.get('avgAction')}")
            print(f"  成效（Success）: {book_stage.get('avgSuccess')}")
            print(f"  回顾（Review）: {book_stage.get('avgReview')}")
            print(f"  运作（Operation）: {book_stage.get('avgOperation')}")
            print(f"  展示（Presentation）: {book_stage.get('avgPresentation')}")
            print(f"  总分（Total）: {book_stage.get('avgTotal')}")
            
            print(f"\n评委意见:")
            print(f"  亮点数量: {len(book_stage.get('highlights', []))}")
            if book_stage.get('highlights'):
                for i, h in enumerate(book_stage['highlights'], 1):
                    print(f"  {i}. {h}")
            
            print(f"\n  改进建议数量: {len(book_stage.get('weaknesses', []))}")
            if book_stage.get('weaknesses'):
                for i, w in enumerate(book_stage['weaknesses'], 1):
                    print(f"  {i}. {w}")
            
            print(f"\n任务分配:")
            print(f"  分配任务数: {book_stage.get('taskCount')}")
            print(f"  已完成评审: {book_stage.get('scoredCount')}")
        else:
            print("❌ 未找到书审阶段数据")
    else:
        print(f"❌ 请求失败: {resp.text}")

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
