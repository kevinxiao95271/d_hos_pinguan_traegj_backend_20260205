#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试入围管理相关API"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import json

BASE = "http://localhost:6031"

print("="*80)
print("测试入围管理API")
print("="*80)

try:
    # 步骤1：登录
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
    
    # 步骤2：获取书审排名
    print("\n\n[步骤2] 获取书审排名（所有项目）")
    print("-" * 80)
    
    rankings_resp = requests.get(f"{BASE}/api/admin/reviews/rankings", params={
        "competitionId": 21,
        "stage": "BOOK"
    }, headers=headers, timeout=10)
    
    print(f"状态码: {rankings_resp.status_code}")
    
    if rankings_resp.status_code == 200:
        rankings = rankings_resp.json()['data']
        print(f"✅ 获取成功")
        print(f"   总项目数: {len(rankings)}")
        
        if len(rankings) > 0:
            print(f"\n   前5名:")
            for i, item in enumerate(rankings[:5], 1):
                print(f"   {i}. {item['projectName']}")
                print(f"      机构: {item['institutionName']}")
                print(f"      组别: {item['groupType']}")
                print(f"      平均分: {item['avgTotal']}")
                print()
        else:
            print("   ⚠️  暂无排名数据，可能还没有完成评分")
    else:
        print(f"❌ 获取失败: {rankings_resp.text[:200]}")
        exit(1)
    
    # 步骤3：按组别筛选
    print("\n\n[步骤3] 按组别筛选（基层组）")
    print("-" * 80)
    
    basic_resp = requests.get(f"{BASE}/api/admin/reviews/rankings", params={
        "competitionId": 21,
        "stage": "BOOK",
        "groupType": "BASIC"
    }, headers=headers, timeout=10)
    
    if basic_resp.status_code == 200:
        basic_rankings = basic_resp.json()['data']
        print(f"✅ 筛选成功")
        print(f"   基层组项目数: {len(basic_rankings)}")
        
        if len(basic_rankings) > 0:
            print(f"   平均分: {sum(item['avgTotal'] for item in basic_rankings) / len(basic_rankings):.1f}")
    else:
        print(f"❌ 筛选失败")
    
    # 步骤4：获取入围名单（前10名）
    print("\n\n[步骤4] 获取入围名单（前10名）")
    print("-" * 80)
    
    shortlist_resp = requests.get(f"{BASE}/api/admin/reviews/shortlist", params={
        "competitionId": 21,
        "stage": "BOOK",
        "limit": 10
    }, headers=headers, timeout=10)
    
    if shortlist_resp.status_code == 200:
        shortlist = shortlist_resp.json()['data']
        print(f"✅ 获取成功")
        print(f"   入围数量: {len(shortlist)}")
        
        if len(shortlist) > 0:
            print(f"\n   入围名单:")
            for item in shortlist:
                print(f"   {item['rank']}. {item['projectName']} - {item['avgTotal']:.1f}分")
    else:
        print(f"❌ 获取失败")
    
    # 步骤5：获取入围名单（分数线85分以上）
    print("\n\n[步骤5] 获取入围名单（85分以上，前15名）")
    print("-" * 80)
    
    shortlist_score_resp = requests.get(f"{BASE}/api/admin/reviews/shortlist", params={
        "competitionId": 21,
        "stage": "BOOK",
        "limit": 15,
        "minAvgTotal": 85.0
    }, headers=headers, timeout=10)
    
    if shortlist_score_resp.status_code == 200:
        shortlist_score = shortlist_score_resp.json()['data']
        print(f"✅ 获取成功")
        print(f"   入围数量: {len(shortlist_score)}")
        
        if len(shortlist_score) > 0:
            print(f"   最低分: {min(item['avgTotal'] for item in shortlist_score):.1f}")
            print(f"   最高分: {max(item['avgTotal'] for item in shortlist_score):.1f}")
    else:
        print(f"❌ 获取失败")
    
    # 步骤6：查看项目详细评分
    if len(rankings) > 0:
        first_id = rankings[0]['registrationId']
        print(f"\n\n[步骤6] 查看项目详细评分（ID: {first_id}）")
        print("-" * 80)
        
        detail_resp = requests.get(
            f"{BASE}/api/registrations/{first_id}/review-details", 
            headers=headers, 
            timeout=10
        )
        
        if detail_resp.status_code == 200:
            details = detail_resp.json()['data']
            print(f"✅ 获取成功")
            
            for d in details:
                if d['stage'] == 'BOOK':
                    print(f"\n   书审阶段详细评分:")
                    print(f"   - 计划: {d['avgPlan']:.1f}")
                    print(f"   - 问题: {d['avgProblem']:.1f}")
                    print(f"   - 行动: {d['avgAction']:.1f}")
                    print(f"   - 成效: {d['avgSuccess']:.1f}")
                    print(f"   - 回顾: {d['avgReview']:.1f}")
                    print(f"   - 运作: {d['avgOperation']:.1f}")
                    print(f"   - 展示: {d['avgPresentation']:.1f}")
                    print(f"   - 总分: {d['avgTotal']:.1f}")
                    
                    if d['highlights']:
                        print(f"\n   亮点:")
                        for h in d['highlights']:
                            print(f"   - {h}")
                    
                    if d['weaknesses']:
                        print(f"\n   不足:")
                        for w in d['weaknesses']:
                            print(f"   - {w}")
        else:
            print(f"❌ 获取失败")
    
    # 步骤7：统计分析
    print("\n\n[步骤7] 统计分析")
    print("-" * 80)
    
    if len(rankings) > 0:
        scores = [item['avgTotal'] for item in rankings]
        
        print(f"✅ 统计信息:")
        print(f"   总项目数: {len(rankings)}")
        print(f"   平均分: {sum(scores) / len(scores):.1f}")
        print(f"   最高分: {max(scores):.1f}")
        print(f"   最低分: {min(scores):.1f}")
        print(f"   90分以上: {len([s for s in scores if s >= 90])} 个")
        print(f"   80-90分: {len([s for s in scores if 80 <= s < 90])} 个")
        print(f"   70-80分: {len([s for s in scores if 70 <= s < 80])} 个")
        print(f"   70分以下: {len([s for s in scores if s < 70])} 个")
        
        # 组别统计
        group_stats = {}
        for item in rankings:
            gt = item['groupType']
            if gt not in group_stats:
                group_stats[gt] = []
            group_stats[gt].append(item['avgTotal'])
        
        print(f"\n   各组别统计:")
        group_names = {
            'BASIC': '基层组',
            'ADVANCED': '进阶组',
            'COMPREHENSIVE': '综合组'
        }
        
        for gt, scores_list in group_stats.items():
            print(f"   - {group_names.get(gt, gt)}:")
            print(f"     项目数: {len(scores_list)}")
            print(f"     平均分: {sum(scores_list) / len(scores_list):.1f}")
            print(f"     最高分: {max(scores_list):.1f}")

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

✅ 所有API已测试

API列表：
  1. GET /api/admin/reviews/rankings
     - 获取书审排名
     - 参数：competitionId, stage, groupType
  
  2. GET /api/admin/reviews/shortlist
     - 获取入围名单
     - 参数：competitionId, stage, limit, minAvgTotal
  
  3. GET /api/registrations/{id}/review-details
     - 获取项目详细评分
     - 包含分项得分和评委意见

前端开发建议：
  1. 使用排名API展示所有项目
  2. 使用入围API快速筛选入围项目
  3. 使用详情API展示项目详细评分
  4. 实现前端筛选（组别/分数线/数量）
  5. 实现手动标记入围功能
  6. 实现导出CSV功能

完整前端开发指引：
  docs/入围管理页面前端开发指引.md
""")
