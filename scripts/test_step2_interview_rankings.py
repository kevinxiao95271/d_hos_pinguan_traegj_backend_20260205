#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""步骤2: 测试面谈排名API"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import json

BASE = "http://localhost:6031"

print("="*80)
print("步骤2: 测试面谈排名API")
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
    
    # 2. 获取面谈排名
    print("\n[2] 获取面谈排名")
    print("-" * 80)
    
    interview_resp = requests.get(f"{BASE}/api/admin/reviews/rankings", params={
        "competitionId": 21,
        "stage": "INTERVIEW"
    }, headers=headers, timeout=10)
    
    print(f"API路径: GET /api/admin/reviews/rankings")
    print(f"参数:")
    print(f"  - competitionId: 21")
    print(f"  - stage: INTERVIEW")
    print(f"状态码: {interview_resp.status_code}")
    
    if interview_resp.status_code == 200:
        interview_data = interview_resp.json()['data']
        print(f"✅ 获取成功")
        print(f"\n返回数据统计:")
        print(f"  - 面谈项目数: {len(interview_data)}")
        
        if len(interview_data) > 0:
            print(f"\n前5名面谈排名:")
            print(f"  {'排名':<6} {'项目名称':<35} {'机构':<30} {'组别':<10} {'得分':<8}")
            print(f"  {'-'*95}")
            
            for item in interview_data[:5]:
                project_name = item['projectName'][:30] if len(item['projectName']) > 30 else item['projectName']
                institution = item['institutionName'][:25] if len(item['institutionName']) > 25 else item['institutionName']
                group_map = {'BASIC': '基层组', 'ADVANCED': '进阶组', 'COMPREHENSIVE': '综合组'}
                group = group_map.get(item['groupType'], item['groupType'])
                
                print(f"  {item['rank']:<6} {project_name:<35} {institution:<30} {group:<10} {item['avgTotal']:<8.1f}")
            
            print(f"\n面谈得分统计:")
            scores = [item['avgTotal'] for item in interview_data]
            print(f"  - 平均分: {sum(scores) / len(scores):.2f}")
            print(f"  - 最高分: {max(scores):.2f}")
            print(f"  - 最低分: {min(scores):.2f}")
            
            print(f"\n返回数据结构示例（第1条）:")
            print(json.dumps(interview_data[0], ensure_ascii=False, indent=2))
            
            # 保存数据供下一步使用
            with open('scripts/test_data_interview.json', 'w', encoding='utf-8') as f:
                json.dump(interview_data, f, ensure_ascii=False, indent=2)
            print(f"\n✅ 数据已保存到: scripts/test_data_interview.json")
            
        else:
            print(f"\n⚠️  暂无面谈评分数据")
            print(f"   这是正常的，如果还没有项目完成面谈评审")
            
            # 保存空数据
            with open('scripts/test_data_interview.json', 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
            
    else:
        print(f"❌ 获取失败")
        print(f"   {interview_resp.text}")
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
print("✅ 步骤2测试完成")
print("="*80)
