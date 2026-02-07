#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试三个阶段的入围管理API"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests

BASE = "http://localhost:6031"

print("="*80)
print("测试三个阶段的入围管理API")
print("="*80)

try:
    # 登录
    print("\n[步骤1] 登录组委会账号")
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
    
    # 测试三个阶段
    stages = ['BOOK', 'INTERVIEW', 'FINAL']
    stage_names = {'BOOK': '书审', 'INTERVIEW': '面谈', 'FINAL': '决赛'}
    stage_emojis = {'BOOK': '📘', 'INTERVIEW': '🎤', 'FINAL': '🏆'}
    
    all_stage_stats = {}
    
    for stage in stages:
        print(f"\n\n{'='*80}")
        print(f"{stage_emojis[stage]} 测试阶段: {stage_names[stage]} ({stage})")
        print('='*80)
        
        # 测试1: 获取排名
        print(f"\n1. 获取{stage_names[stage]}阶段排名")
        print("-" * 80)
        
        resp = requests.get(f"{BASE}/api/admin/reviews/rankings", params={
            "competitionId": 21,
            "stage": stage
        }, headers=headers, timeout=10)
        
        print(f"状态码: {resp.status_code}")
        
        if resp.status_code == 200:
            rankings = resp.json()['data']
            print(f"✅ {stage_names[stage]}阶段排名获取成功")
            print(f"   项目数: {len(rankings)}")
            
            if len(rankings) > 0:
                scores = [item['avgTotal'] for item in rankings]
                avg_score = sum(scores) / len(scores)
                max_score = max(scores)
                min_score = min(scores)
                
                print(f"   平均分: {avg_score:.1f}")
                print(f"   最高分: {max_score:.1f}")
                print(f"   最低分: {min_score:.1f}")
                
                # 保存统计信息
                all_stage_stats[stage] = {
                    'count': len(rankings),
                    'avg': avg_score,
                    'max': max_score,
                    'min': min_score
                }
                
                # 显示前3名
                print(f"\n   前3名:")
                for i, item in enumerate(rankings[:3], 1):
                    print(f"   {i}. {item['projectName']} - {item['avgTotal']:.1f}分")
                    print(f"      机构: {item['institutionName']}")
                
                # 测试2: 获取入围名单
                print(f"\n2. 获取{stage_names[stage]}阶段入围名单（前5名，80分以上）")
                print("-" * 80)
                
                shortlist_resp = requests.get(f"{BASE}/api/admin/reviews/shortlist", params={
                    "competitionId": 21,
                    "stage": stage,
                    "limit": 5,
                    "minAvgTotal": 80.0
                }, headers=headers, timeout=10)
                
                if shortlist_resp.status_code == 200:
                    shortlist = shortlist_resp.json()['data']
                    print(f"✅ 入围名单获取成功")
                    print(f"   入围数量: {len(shortlist)} 个项目")
                    
                    if len(shortlist) > 0:
                        print(f"   入围名单:")
                        for item in shortlist:
                            print(f"   - {item['rank']}. {item['projectName']} ({item['avgTotal']:.1f}分)")
                else:
                    print(f"❌ 入围名单获取失败")
                
                # 测试3: 查看项目详细评分
                first_id = rankings[0]['registrationId']
                print(f"\n3. 查看项目详细评分（ID: {first_id}）")
                print("-" * 80)
                
                detail_resp = requests.get(
                    f"{BASE}/api/registrations/{first_id}/review-details", 
                    headers=headers, 
                    timeout=10
                )
                
                if detail_resp.status_code == 200:
                    details = detail_resp.json()['data']
                    print(f"✅ 详细评分获取成功")
                    
                    # 查找当前阶段的评分
                    stage_detail = next((d for d in details if d['stage'] == stage), None)
                    if stage_detail:
                        print(f"\n   {stage_names[stage]}阶段详细评分:")
                        print(f"   - 计划: {stage_detail.get('avgPlan', 0):.1f}")
                        print(f"   - 问题: {stage_detail.get('avgProblem', 0):.1f}")
                        print(f"   - 行动: {stage_detail.get('avgAction', 0):.1f}")
                        print(f"   - 成效: {stage_detail.get('avgSuccess', 0):.1f}")
                        print(f"   - 回顾: {stage_detail.get('avgReview', 0):.1f}")
                        print(f"   - 运作: {stage_detail.get('avgOperation', 0):.1f}")
                        print(f"   - 展示: {stage_detail.get('avgPresentation', 0):.1f}")
                        print(f"   - 总分: {stage_detail.get('avgTotal', 0):.1f}")
                    else:
                        print(f"   ⚠️  该项目在{stage_names[stage]}阶段还没有评分")
                else:
                    print(f"❌ 详细评分获取失败")
                
            else:
                print(f"   ⚠️  {stage_names[stage]}阶段还没有评分数据")
                all_stage_stats[stage] = {
                    'count': 0,
                    'avg': 0,
                    'max': 0,
                    'min': 0
                }
        else:
            print(f"❌ {stage_names[stage]}阶段排名获取失败")
            all_stage_stats[stage] = {
                'count': 0,
                'avg': 0,
                'max': 0,
                'min': 0
            }
    
    # 汇总统计
    print("\n\n" + "="*80)
    print("各阶段统计汇总")
    print("="*80)
    
    for stage in stages:
        stats = all_stage_stats.get(stage, {})
        print(f"\n{stage_emojis[stage]} {stage_names[stage]}阶段:")
        print(f"   项目数: {stats.get('count', 0)}")
        if stats.get('count', 0) > 0:
            print(f"   平均分: {stats.get('avg', 0):.1f}")
            print(f"   最高分: {stats.get('max', 0):.1f}")
            print(f"   最低分: {stats.get('min', 0):.1f}")
        else:
            print(f"   状态: 暂无评分数据")

except requests.exceptions.ConnectionError:
    print("\n❌ 连接失败，服务器未启动")
    print("请启动服务器：mvn spring-boot:run")
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("测试完成")
print("="*80)

print("""
总结：

✅ 三个阶段的入围管理API已测试

阶段说明：
  📘 书审（BOOK）: 查看书审得分，筛选入围面谈
  🎤 面谈（INTERVIEW）: 查看面谈得分，筛选入围决赛
  🏆 决赛（FINAL）: 查看决赛得分，确定最终名次

API列表：
  1. GET /api/admin/reviews/rankings
     - 参数：competitionId, stage (BOOK/INTERVIEW/FINAL), groupType
  
  2. GET /api/admin/reviews/shortlist
     - 参数：competitionId, stage, limit, minAvgTotal, groupType
  
  3. GET /api/registrations/{id}/review-details
     - 返回所有阶段的详细评分

前端开发要点：
  1. 实现阶段切换（书审/面谈/决赛）
  2. 切换阶段时重新加载对应阶段的排名
  3. 查看详情时展示所有阶段的评分历史
  4. 导出名单时包含阶段信息

完整前端开发指引：
  docs/入围管理页面前端开发指引-完整版.md
""")
