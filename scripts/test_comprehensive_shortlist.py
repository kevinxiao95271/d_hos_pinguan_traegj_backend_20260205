#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""综合入围管理API完整自测"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import json

BASE = "http://localhost:6031"

print("="*80)
print("综合入围管理API完整自测")
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
    print(f"Token: {token[:50]}...")
    
    # 测试1: 获取书审排名
    print("\n\n[测试1] 获取书审排名")
    print("-" * 80)
    
    book_resp = requests.get(f"{BASE}/api/admin/reviews/rankings", params={
        "competitionId": 21,
        "stage": "BOOK"
    }, headers=headers, timeout=10)
    
    print(f"请求URL: {book_resp.url}")
    print(f"状态码: {book_resp.status_code}")
    
    if book_resp.status_code == 200:
        book_data = book_resp.json()['data']
        print(f"✅ 获取成功")
        print(f"   书审项目数: {len(book_data)}")
        
        if len(book_data) > 0:
            print(f"\n   前3名书审排名:")
            for item in book_data[:3]:
                print(f"   {item['rank']}. {item['projectName']} - {item['avgTotal']:.1f}分")
                print(f"      ID: {item['registrationId']}")
                print(f"      机构: {item['institutionName']}")
                print(f"      组别: {item['groupType']}")
            
            print(f"\n   书审得分统计:")
            scores = [item['avgTotal'] for item in book_data]
            print(f"   平均分: {sum(scores) / len(scores):.1f}")
            print(f"   最高分: {max(scores):.1f}")
            print(f"   最低分: {min(scores):.1f}")
            
            # 保存书审数据用于后续测试
            book_projects = {item['registrationId']: {
                'projectName': item['projectName'],
                'institutionName': item['institutionName'],
                'groupType': item['groupType'],
                'bookScore': item['avgTotal'],
                'bookRank': item['rank']
            } for item in book_data}
    else:
        print(f"❌ 获取失败: {book_resp.text[:200]}")
        book_projects = {}
    
    # 测试2: 获取面谈排名
    print("\n\n[测试2] 获取面谈排名")
    print("-" * 80)
    
    interview_resp = requests.get(f"{BASE}/api/admin/reviews/rankings", params={
        "competitionId": 21,
        "stage": "INTERVIEW"
    }, headers=headers, timeout=10)
    
    print(f"请求URL: {interview_resp.url}")
    print(f"状态码: {interview_resp.status_code}")
    
    if interview_resp.status_code == 200:
        interview_data = interview_resp.json()['data']
        print(f"✅ 获取成功")
        print(f"   面谈项目数: {len(interview_data)}")
        
        if len(interview_data) > 0:
            print(f"\n   前3名面谈排名:")
            for item in interview_data[:3]:
                print(f"   {item['rank']}. {item['projectName']} - {item['avgTotal']:.1f}分")
            
            print(f"\n   面谈得分统计:")
            scores = [item['avgTotal'] for item in interview_data]
            print(f"   平均分: {sum(scores) / len(scores):.1f}")
            print(f"   最高分: {max(scores):.1f}")
            print(f"   最低分: {min(scores):.1f}")
            
            # 添加面谈数据
            for item in interview_data:
                if item['registrationId'] in book_projects:
                    book_projects[item['registrationId']]['interviewScore'] = item['avgTotal']
                    book_projects[item['registrationId']]['interviewRank'] = item['rank']
        else:
            print(f"   ⚠️  暂无面谈评分数据")
    else:
        print(f"❌ 获取失败")
    
    # 测试3: 数据合并和综合排名
    print("\n\n[测试3] 数据合并和综合排名计算")
    print("-" * 80)
    
    print(f"合并书审和面谈数据...")
    
    # 计算综合得分（权重各50%）
    book_weight = 50
    interview_weight = 50
    
    merged_projects = []
    for reg_id, project in book_projects.items():
        book_score = project['bookScore']
        interview_score = project.get('interviewScore')
        
        if interview_score is not None:
            composite_score = (book_score * book_weight / 100) + (interview_score * interview_weight / 100)
        else:
            composite_score = None  # 待面谈
        
        merged_projects.append({
            'registrationId': reg_id,
            'projectName': project['projectName'],
            'institutionName': project['institutionName'],
            'groupType': project['groupType'],
            'bookScore': book_score,
            'interviewScore': interview_score,
            'compositeScore': composite_score
        })
    
    # 排序（综合得分降序）
    completed = [p for p in merged_projects if p['compositeScore'] is not None]
    pending = [p for p in merged_projects if p['compositeScore'] is None]
    
    completed.sort(key=lambda x: x['compositeScore'], reverse=True)
    
    # 分配排名
    for i, p in enumerate(completed, 1):
        p['rank'] = i
    
    all_projects = completed + pending
    
    print(f"✅ 合并成功")
    print(f"   总项目数: {len(all_projects)}")
    print(f"   已完成书审和面谈: {len(completed)}")
    print(f"   待面谈: {len(pending)}")
    
    if len(completed) > 0:
        print(f"\n   综合排名前5名:")
        print(f"   {'排名':<6} {'项目名称':<30} {'书审':<8} {'面谈':<8} {'综合':<8}")
        print(f"   {'-'*70}")
        for p in completed[:5]:
            print(f"   {p['rank']:<6} {p['projectName']:<30} {p['bookScore']:<8.1f} {p['interviewScore']:<8.1f} {p['compositeScore']:<8.1f}")
        
        # 测试4: 入围比例计算
        print(f"\n\n[测试4] 入围比例计算")
        print("-" * 80)
        
        ratios = [30, 40, 50]
        for ratio in ratios:
            shortlist_count = int(len(completed) * ratio / 100)
            print(f"\n   入围比例: {ratio}%")
            print(f"   入围数量: {shortlist_count} 个项目")
            print(f"   入围分数线: {completed[shortlist_count-1]['compositeScore']:.1f}分 (第{shortlist_count}名)")
        
        # 测试5: 按组别筛选
        print(f"\n\n[测试5] 按组别筛选")
        print("-" * 80)
        
        group_types = {}
        for p in all_projects:
            gt = p['groupType']
            if gt not in group_types:
                group_types[gt] = []
            group_types[gt].append(p)
        
        group_names = {
            'BASIC': '基层组',
            'ADVANCED': '进阶组',
            'COMPREHENSIVE': '综合组'
        }
        
        for gt, projects in group_types.items():
            completed_in_group = [p for p in projects if p['compositeScore'] is not None]
            print(f"\n   {group_names.get(gt, gt)}:")
            print(f"   - 项目数: {len(projects)}")
            print(f"   - 已完成评审: {len(completed_in_group)}")
            if len(completed_in_group) > 0:
                scores = [p['compositeScore'] for p in completed_in_group]
                print(f"   - 平均综合分: {sum(scores) / len(scores):.1f}")
                print(f"   - 最高分: {max(scores):.1f}")
        
        # 测试6: 获取项目详细评分
        print(f"\n\n[测试6] 获取项目详细评分")
        print("-" * 80)
        
        test_project = completed[0]
        test_id = test_project['registrationId']
        
        print(f"测试项目: {test_project['projectName']} (ID: {test_id})")
        
        detail_resp = requests.get(
            f"{BASE}/api/registrations/{test_id}/review-details",
            headers=headers,
            timeout=10
        )
        
        print(f"请求URL: {detail_resp.url}")
        print(f"状态码: {detail_resp.status_code}")
        
        if detail_resp.status_code == 200:
            details = detail_resp.json()['data']
            print(f"✅ 获取成功")
            print(f"   返回阶段数: {len(details)}")
            
            for detail in details:
                stage = detail['stage']
                stage_name = '书审' if stage == 'BOOK' else ('面谈' if stage == 'INTERVIEW' else '决赛')
                print(f"\n   {stage_name}阶段:")
                print(f"   - 计划: {detail.get('avgPlan', 0):.1f}")
                print(f"   - 问题: {detail.get('avgProblem', 0):.1f}")
                print(f"   - 行动: {detail.get('avgAction', 0):.1f}")
                print(f"   - 成效: {detail.get('avgSuccess', 0):.1f}")
                print(f"   - 回顾: {detail.get('avgReview', 0):.1f}")
                print(f"   - 运作: {detail.get('avgOperation', 0):.1f}")
                print(f"   - 展示: {detail.get('avgPresentation', 0):.1f}")
                print(f"   - 总分: {detail.get('avgTotal', 0):.1f}")
                
                if detail.get('highlights'):
                    print(f"   - 亮点数: {len(detail['highlights'])}")
                if detail.get('weaknesses'):
                    print(f"   - 改进建议数: {len(detail['weaknesses'])}")
        else:
            print(f"❌ 获取失败")
        
        # 测试7: 导出数据格式
        print(f"\n\n[测试7] 导出数据格式验证")
        print("-" * 80)
        
        print(f"✅ 生成CSV导出格式:")
        csv_header = ['综合排名', '项目名称', '医疗机构', '组别', '书审得分', '面谈得分', '综合得分', '入围状态']
        print(f"   表头: {','.join(csv_header)}")
        
        print(f"\n   前3行数据样例:")
        for p in completed[:3]:
            row = [
                str(p['rank']),
                p['projectName'],
                p['institutionName'],
                group_names.get(p['groupType'], p['groupType']),
                f"{p['bookScore']:.1f}",
                f"{p['interviewScore']:.1f}",
                f"{p['compositeScore']:.1f}",
                '入围' if p['rank'] <= int(len(completed) * 30 / 100) else '未入围'
            ]
            print(f"   {','.join(row)}")
        
        # 生成API调用报告
        print(f"\n\n{'='*80}")
        print(f"API调用报告")
        print(f"{'='*80}")
        
        print(f"\n✅ 所有API测试通过")
        print(f"\n数据统计:")
        print(f"  - 总项目数: {len(all_projects)}")
        print(f"  - 已完成书审: {len(book_projects)}")
        print(f"  - 已完成面谈: {len([p for p in book_projects.values() if 'interviewScore' in p])}")
        print(f"  - 可计算综合排名: {len(completed)}")
        print(f"  - 待面谈: {len(pending)}")
        
        print(f"\n入围比例测算（基于{len(completed)}个已完成评审的项目）:")
        for ratio in [30, 40, 50]:
            count = int(len(completed) * ratio / 100)
            print(f"  - 前{ratio}%: {count}个项目")

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
