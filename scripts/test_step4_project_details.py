#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""步骤4: 测试获取项目详细评分"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import json
import os

BASE = "http://localhost:6031"

print("="*80)
print("步骤4: 测试获取项目详细评分API")
print("="*80)

try:
    # 1. 登录
    print("\n[1] 登录组委会账号")
    print("-" * 80)
    
    login_resp = requests.post(f"{BASE}/api/auth/login", json={
        "phone": "13800000003",
        "name": "组委会管理员",
        "role": "COMMITTEE"
    }, timeout=10)
    
    if login_resp.status_code != 200:
        print(f"❌ 登录失败: {login_resp.status_code}")
        exit(1)
    
    token = login_resp.json()['data']['token']
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ 登录成功")
    
    # 2. 加载合并后的数据，选择一个项目测试
    print("\n[2] 选择测试项目")
    print("-" * 80)
    
    if not os.path.exists('scripts/test_data_merged.json'):
        print("❌ 找不到合并数据文件")
        print("   请先运行: python scripts/test_step3_merge_and_rank.py")
        exit(1)
    
    with open('scripts/test_data_merged.json', 'r', encoding='utf-8') as f:
        merged_data = json.load(f)
    
    # 选择第一个项目（优先已完成评审的，如果没有则选待面谈的）
    test_project = None
    for project in merged_data:
        if project['status'] == 'completed':
            test_project = project
            break
    
    if not test_project and len(merged_data) > 0:
        # 没有已完成评审的，选择第一个待面谈的
        test_project = merged_data[0]
        print("⚠️  没有已完成书审和面谈的项目，选择待面谈的项目测试")
    
    if not test_project:
        print("❌ 没有找到任何项目")
        exit(1)
    
    test_id = test_project['registrationId']
    print(f"✅ 选择测试项目:")
    print(f"  - ID: {test_id}")
    print(f"  - 项目名称: {test_project['projectName']}")
    print(f"  - 书审得分: {test_project['bookScore']:.2f}")
    if test_project.get('interviewScore'):
        print(f"  - 面谈得分: {test_project['interviewScore']:.2f}")
        print(f"  - 综合得分: {test_project['compositeScore']:.2f}")
    else:
        print(f"  - 面谈得分: 待评审")
        print(f"  - 综合得分: 待计算")
    
    # 3. 获取项目详细评分
    print(f"\n[3] 获取项目详细评分")
    print("-" * 80)
    
    detail_resp = requests.get(
        f"{BASE}/api/registrations/{test_id}/review-details",
        headers=headers,
        timeout=10
    )
    
    print(f"API路径: GET /api/registrations/{test_id}/review-details")
    print(f"状态码: {detail_resp.status_code}")
    
    if detail_resp.status_code == 200:
        details = detail_resp.json()['data']
        print(f"✅ 获取成功")
        print(f"\n返回阶段数: {len(details)}")
        
        stage_names = {
            'BOOK': '书审',
            'INTERVIEW': '面谈',
            'FINAL': '决赛'
        }
        
        for detail in details:
            stage = detail['stage']
            stage_name = stage_names.get(stage, stage)
            
            print(f"\n{stage_name}阶段详细评分:")
            print(f"  - 计划（Plan）: {detail.get('avgPlan') or 0:.2f}")
            print(f"  - 问题（Problem）: {detail.get('avgProblem') or 0:.2f}")
            print(f"  - 行动（Action）: {detail.get('avgAction') or 0:.2f}")
            print(f"  - 成效（Success）: {detail.get('avgSuccess') or 0:.2f}")
            print(f"  - 回顾（Review）: {detail.get('avgReview') or 0:.2f}")
            print(f"  - 运作（Operation）: {detail.get('avgOperation') or 0:.2f}")
            print(f"  - 展示（Presentation）: {detail.get('avgPresentation') or 0:.2f}")
            print(f"  - 总分（Total）: {detail.get('avgTotal') or 0:.2f}")
            
            if detail.get('highlights'):
                print(f"  - 亮点数: {len(detail['highlights'])}")
                if len(detail['highlights']) > 0:
                    print(f"    例: {detail['highlights'][0][:50]}...")
            
            if detail.get('weaknesses'):
                print(f"  - 改进建议数: {len(detail['weaknesses'])}")
                if len(detail['weaknesses']) > 0:
                    print(f"    例: {detail['weaknesses'][0][:50]}...")
        
        print(f"\n返回数据结构示例（第1个阶段）:")
        print(json.dumps(details[0], ensure_ascii=False, indent=2))
        
    else:
        print(f"❌ 获取失败")
        print(f"   {detail_resp.text}")
        exit(1)

except requests.exceptions.ConnectionError:
    print("\n❌ 连接失败，服务器未启动")
    exit(1)
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "="*80)
print("✅ 步骤4测试完成")
print("="*80)
