#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""步骤3: 数据合并和综合排名计算"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import json
import os

print("="*80)
print("步骤3: 数据合并和综合排名计算")
print("="*80)

try:
    # 1. 加载书审数据
    print("\n[1] 加载书审数据")
    print("-" * 80)
    
    if not os.path.exists('scripts/test_data_book.json'):
        print("❌ 找不到书审数据文件")
        print("   请先运行: python scripts/test_step1_book_rankings.py")
        exit(1)
    
    with open('scripts/test_data_book.json', 'r', encoding='utf-8') as f:
        book_data = json.load(f)
    
    print(f"✅ 书审数据加载成功: {len(book_data)} 个项目")
    
    # 2. 加载面谈数据
    print("\n[2] 加载面谈数据")
    print("-" * 80)
    
    if not os.path.exists('scripts/test_data_interview.json'):
        print("❌ 找不到面谈数据文件")
        print("   请先运行: python scripts/test_step2_interview_rankings.py")
        exit(1)
    
    with open('scripts/test_data_interview.json', 'r', encoding='utf-8') as f:
        interview_data = json.load(f)
    
    print(f"✅ 面谈数据加载成功: {len(interview_data)} 个项目")
    
    # 3. 合并数据
    print("\n[3] 合并数据")
    print("-" * 80)
    
    # 创建字典方便查找
    book_dict = {item['registrationId']: item for item in book_data}
    interview_dict = {item['registrationId']: item for item in interview_data}
    
    # 合并
    merged_projects = []
    for reg_id, book_item in book_dict.items():
        interview_item = interview_dict.get(reg_id)
        
        merged = {
            'registrationId': reg_id,
            'projectName': book_item['projectName'],
            'institutionName': book_item['institutionName'],
            'groupType': book_item['groupType'],
            'bookScore': book_item['avgTotal'],
            'bookRank': book_item['rank'],
            'interviewScore': interview_item['avgTotal'] if interview_item else None,
            'interviewRank': interview_item['rank'] if interview_item else None
        }
        
        merged_projects.append(merged)
    
    print(f"✅ 合并完成: {len(merged_projects)} 个项目")
    
    # 4. 计算综合得分
    print("\n[4] 计算综合得分（权重：书审50% + 面谈50%）")
    print("-" * 80)
    
    book_weight = 50
    interview_weight = 50
    
    completed = []
    pending = []
    
    for project in merged_projects:
        if project['interviewScore'] is not None:
            # 已完成书审和面谈，计算综合得分
            composite_score = (
                project['bookScore'] * book_weight / 100 +
                project['interviewScore'] * interview_weight / 100
            )
            project['compositeScore'] = composite_score
            project['status'] = 'completed'
            completed.append(project)
        else:
            # 待面谈
            project['compositeScore'] = None
            project['status'] = 'pending_interview'
            pending.append(project)
    
    # 5. 综合排名
    print("\n[5] 综合排名")
    print("-" * 80)
    
    completed.sort(key=lambda x: x['compositeScore'], reverse=True)
    
    for i, project in enumerate(completed, 1):
        project['compositeRank'] = i
    
    print(f"✅ 排名完成")
    print(f"  - 已完成评审（可排名）: {len(completed)}")
    print(f"  - 待面谈（无法排名）: {len(pending)}")
    
    # 6. 显示综合排名
    if len(completed) > 0:
        print(f"\n综合排名前10名:")
        print(f"  {'排名':<6} {'项目名称':<30} {'书审':<8} {'面谈':<8} {'综合':<8}")
        print(f"  {'-'*70}")
        
        for project in completed[:10]:
            project_name = project['projectName'][:28] if len(project['projectName']) > 28 else project['projectName']
            print(f"  {project['compositeRank']:<6} {project_name:<30} {project['bookScore']:<8.2f} {project['interviewScore']:<8.2f} {project['compositeScore']:<8.2f}")
        
        # 7. 入围比例计算
        print(f"\n[6] 入围比例计算（基于{len(completed)}个已完成评审的项目）")
        print("-" * 80)
        
        ratios = [30, 40, 50]
        for ratio in ratios:
            shortlist_count = int(len(completed) * ratio / 100)
            if shortlist_count > 0 and shortlist_count <= len(completed):
                threshold_score = completed[shortlist_count - 1]['compositeScore']
                print(f"\n  入围比例: {ratio}%")
                print(f"  - 入围数量: {shortlist_count} 个项目")
                print(f"  - 分数线: {threshold_score:.2f}分（第{shortlist_count}名的得分）")
                print(f"  - 入围项目:")
                for project in completed[:min(3, shortlist_count)]:
                    print(f"    · {project['projectName'][:40]} - {project['compositeScore']:.2f}分")
                if shortlist_count > 3:
                    print(f"    ... 还有 {shortlist_count - 3} 个项目")
        
        # 8. 按组别统计
        print(f"\n[7] 按组别统计")
        print("-" * 80)
        
        group_names = {
            'BASIC': '基层组',
            'ADVANCED': '进阶组',
            'COMPREHENSIVE': '综合组'
        }
        
        groups = {}
        for project in completed:
            gt = project['groupType']
            if gt not in groups:
                groups[gt] = []
            groups[gt].append(project)
        
        for gt, projects in groups.items():
            print(f"\n  {group_names.get(gt, gt)}:")
            print(f"  - 项目数: {len(projects)}")
            scores = [p['compositeScore'] for p in projects]
            print(f"  - 平均综合分: {sum(scores) / len(scores):.2f}")
            print(f"  - 最高分: {max(scores):.2f}")
            print(f"  - 最低分: {min(scores):.2f}")
        
        # 保存合并后的数据
        all_projects = completed + pending
        with open('scripts/test_data_merged.json', 'w', encoding='utf-8') as f:
            json.dump(all_projects, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 合并数据已保存到: scripts/test_data_merged.json")
        
    else:
        print(f"\n⚠️  没有已完成书审和面谈的项目，无法计算综合排名")
        # 仍然保存待面谈的项目
        all_projects = completed + pending
        with open('scripts/test_data_merged.json', 'w', encoding='utf-8') as f:
            json.dump(all_projects, f, ensure_ascii=False, indent=2)
        print(f"✅ 待面谈项目已保存到: scripts/test_data_merged.json")

except FileNotFoundError as e:
    print(f"\n❌ 文件不存在: {e}")
    print("   请先运行步骤1和步骤2")
    exit(1)
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "="*80)
print("✅ 步骤3测试完成")
print("="*80)
