#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析同一个项目负责人跨基层组/综合组/进阶组报名的情况
"""

import sys
import io
import psycopg2
from collections import defaultdict, Counter

# 设置输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB_CONFIG = {
    'host': '119.167.165.27',
    'port': 5432,
    'user': 'postgres',
    'password': 'zjylzl',
    'database': 'd_hos_pinguan_20260211'
}

def analyze_cross_group_type():
    """分析跨大类报名情况"""
    
    print("=" * 80)
    print("历史数据：项目负责人跨大类（基层/综合/进阶）报名分析")
    print("=" * 80)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # 查询所有历史数据
        print("\n[1] 查询历史数据...")
        cur.execute("""
            SELECT 
                year,
                institution_name,
                project_leader_name,
                project_leader_phone,
                project_name,
                competition_group
            FROM pinguan_his_data
            WHERE project_leader_name IS NOT NULL 
              AND competition_group IS NOT NULL
            ORDER BY year, project_leader_name
        """)
        
        all_data = cur.fetchall()
        print(f"    总记录数: {len(all_data)}")
        
        # 按年度和负责人分组
        year_leader_groups = defaultdict(lambda: defaultdict(list))
        
        for year, inst_name, leader_name, leader_phone, proj_name, comp_group in all_data:
            # 使用姓名+手机号作为唯一标识
            leader_key = f"{leader_name}_{leader_phone if leader_phone else 'unknown'}"
            
            year_leader_groups[year][leader_key].append({
                'institution': inst_name,
                'project_name': proj_name,
                'competition_group': comp_group
            })
        
        # 分析每个年度
        for year in sorted(year_leader_groups.keys()):
            print(f"\n{'='*80}")
            print(f"年度: {year}")
            print(f"{'='*80}")
            
            leaders = year_leader_groups[year]
            
            # 统计提交多个项目的负责人
            multi_project_leaders = {k: v for k, v in leaders.items() if len(v) > 1}
            
            print(f"\n  总负责人数: {len(leaders)}")
            print(f"  提交多个项目的负责人数: {len(multi_project_leaders)}")
            
            if not multi_project_leaders:
                print(f"  该年度没有负责人提交多个项目")
                continue
            
            # 分析大类分布
            cross_group_stats = {
                '仅基层组': 0,
                '仅综合组': 0,
                '仅进阶组': 0,
                '基层+综合': 0,
                '基层+进阶': 0,
                '综合+进阶': 0,
                '三类都有': 0
            }
            
            # 详细案例
            cross_examples = {
                '基层+综合': [],
                '基层+进阶': [],
                '综合+进阶': [],
                '三类都有': []
            }
            
            for leader_key, projects in multi_project_leaders.items():
                leader_name = leader_key.split('_')[0]
                
                # 统计大类
                comp_groups = [p['competition_group'] for p in projects]
                unique_groups = set(comp_groups)
                
                # 分类统计
                if len(unique_groups) == 1:
                    group = list(unique_groups)[0]
                    if '基层' in group:
                        cross_group_stats['仅基层组'] += 1
                    elif '综合' in group:
                        cross_group_stats['仅综合组'] += 1
                    elif '进阶' in group:
                        cross_group_stats['仅进阶组'] += 1
                elif len(unique_groups) == 2:
                    groups_list = sorted(list(unique_groups))
                    if '基层组' in groups_list and '综合组' in groups_list:
                        cross_group_stats['基层+综合'] += 1
                        if len(cross_examples['基层+综合']) < 5:
                            cross_examples['基层+综合'].append({
                                'leader': leader_name,
                                'institution': projects[0]['institution'],
                                'projects': [(p['project_name'][:30], p['competition_group']) for p in projects]
                            })
                    elif '基层组' in groups_list and '进阶组' in groups_list:
                        cross_group_stats['基层+进阶'] += 1
                        if len(cross_examples['基层+进阶']) < 5:
                            cross_examples['基层+进阶'].append({
                                'leader': leader_name,
                                'institution': projects[0]['institution'],
                                'projects': [(p['project_name'][:30], p['competition_group']) for p in projects]
                            })
                    elif '综合组' in groups_list and '进阶组' in groups_list:
                        cross_group_stats['综合+进阶'] += 1
                        if len(cross_examples['综合+进阶']) < 5:
                            cross_examples['综合+进阶'].append({
                                'leader': leader_name,
                                'institution': projects[0]['institution'],
                                'projects': [(p['project_name'][:30], p['competition_group']) for p in projects]
                            })
                elif len(unique_groups) >= 3:
                    cross_group_stats['三类都有'] += 1
                    if len(cross_examples['三类都有']) < 5:
                        cross_examples['三类都有'].append({
                            'leader': leader_name,
                            'institution': projects[0]['institution'],
                            'projects': [(p['project_name'][:30], p['competition_group']) for p in projects]
                        })
            
            # 输出统计结果
            print(f"\n  大类分布统计:")
            total = len(multi_project_leaders)
            
            print(f"\n    单一大类:")
            for key in ['仅基层组', '仅综合组', '仅进阶组']:
                count = cross_group_stats[key]
                pct = count / total * 100 if total > 0 else 0
                print(f"      {key}: {count} 人 ({pct:.1f}%)")
            
            single_total = sum([cross_group_stats[k] for k in ['仅基层组', '仅综合组', '仅进阶组']])
            single_pct = single_total / total * 100 if total > 0 else 0
            print(f"      小计: {single_total} 人 ({single_pct:.1f}%)")
            
            print(f"\n    跨大类:")
            for key in ['基层+综合', '基层+进阶', '综合+进阶', '三类都有']:
                count = cross_group_stats[key]
                pct = count / total * 100 if total > 0 else 0
                print(f"      {key}: {count} 人 ({pct:.1f}%)")
            
            cross_total = sum([cross_group_stats[k] for k in ['基层+综合', '基层+进阶', '综合+进阶', '三类都有']])
            cross_pct = cross_total / total * 100 if total > 0 else 0
            print(f"      小计: {cross_total} 人 ({cross_pct:.1f}%)")
            
            # 输出典型案例
            if cross_total > 0:
                print(f"\n  跨大类典型案例:")
                
                for category, cases in cross_examples.items():
                    if cases:
                        print(f"\n    【{category}】:")
                        for case in cases:
                            print(f"      - {case['leader']} ({case['institution']})")
                            for proj_name, comp_group in case['projects']:
                                print(f"        · {proj_name}... [{comp_group}]")
        
        # 总体统计
        print(f"\n{'='*80}")
        print(f"总体统计（2024-2025）")
        print(f"{'='*80}")
        
        all_multi_leaders = []
        all_cross_leaders = []
        
        for year, leaders in year_leader_groups.items():
            for leader_key, projects in leaders.items():
                if len(projects) > 1:
                    comp_groups = [p['competition_group'] for p in projects]
                    unique_groups = set(comp_groups)
                    all_multi_leaders.append(len(unique_groups))
                    
                    if len(unique_groups) > 1:
                        all_cross_leaders.append({
                            'year': year,
                            'leader': leader_key.split('_')[0],
                            'groups': list(unique_groups)
                        })
        
        if all_multi_leaders:
            total_multi = len(all_multi_leaders)
            total_cross = len(all_cross_leaders)
            
            print(f"\n  提交多个项目的负责人总数: {total_multi}")
            print(f"  跨大类报名的负责人数: {total_cross}")
            print(f"  跨大类占比: {total_cross/total_multi*100:.1f}%")
            
            # 统计跨大类的具体分布
            cross_counter = Counter()
            for leader in all_cross_leaders:
                groups_key = '+'.join(sorted(leader['groups']))
                cross_counter[groups_key] += 1
            
            print(f"\n  跨大类组合分布:")
            for groups_key, count in cross_counter.most_common():
                pct = count / total_cross * 100 if total_cross > 0 else 0
                print(f"    {groups_key}: {count} 人 ({pct:.1f}%)")
        
        # 结论
        print(f"\n{'='*80}")
        print(f"结论")
        print(f"{'='*80}")
        
        if all_multi_leaders:
            single_pct = (total_multi - total_cross) / total_multi * 100
            cross_pct = total_cross / total_multi * 100
            
            print(f"\n  1. 同一负责人提交多个项目时:")
            print(f"     - {single_pct:.1f}% 的情况下，所有项目在同一大类")
            print(f"     - {cross_pct:.1f}% 的情况下，项目跨越不同大类")
            
            if cross_pct < 30:
                print(f"\n  2. 主要特征: 绝大多数负责人的多个项目集中在同一大类")
                print(f"     建议: 自动分组时优先保持同一大类")
            else:
                print(f"\n  2. 主要特征: 有相当比例的负责人跨大类报名")
                print(f"     建议: 自动分组时需要考虑跨大类分配")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n[ERROR] 分析失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_cross_group_type()
