#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析历史数据中同一个项目负责人提交多个项目时的分组分布特征
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

def analyze_leader_projects():
    """分析项目负责人的多项目分组特征"""
    
    print("=" * 80)
    print("历史数据：项目负责人多项目分组分布分析")
    print("=" * 80)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # 1. 查询所有历史数据
        print("\n[1] 查询历史数据...")
        cur.execute("""
            SELECT 
                year,
                institution_name,
                project_leader_name,
                project_leader_phone,
                project_name,
                competition_group,
                group_name
            FROM pinguan_his_data
            WHERE project_leader_name IS NOT NULL
            ORDER BY year, institution_name, project_leader_name
        """)
        
        all_data = cur.fetchall()
        print(f"    总记录数: {len(all_data)}")
        
        # 2. 按年度和负责人分组
        print("\n[2] 按年度和负责人分组统计...")
        
        # 数据结构: {year: {leader_key: [projects]}}
        year_leader_projects = defaultdict(lambda: defaultdict(list))
        
        for year, inst_name, leader_name, leader_phone, proj_name, comp_group, group_name in all_data:
            # 使用姓名+手机号作为唯一标识（手机号可能为空）
            leader_key = f"{leader_name}_{leader_phone if leader_phone else 'unknown'}"
            
            year_leader_projects[year][leader_key].append({
                'institution': inst_name,
                'project_name': proj_name,
                'competition_group': comp_group,
                'group_name': group_name
            })
        
        # 3. 分析每个年度的情况
        for year in sorted(year_leader_projects.keys()):
            print(f"\n{'='*80}")
            print(f"年度: {year}")
            print(f"{'='*80}")
            
            leaders = year_leader_projects[year]
            
            # 统计提交多个项目的负责人
            multi_project_leaders = {k: v for k, v in leaders.items() if len(v) > 1}
            
            print(f"\n  总负责人数: {len(leaders)}")
            print(f"  提交多个项目的负责人数: {len(multi_project_leaders)}")
            print(f"  占比: {len(multi_project_leaders)/len(leaders)*100:.1f}%")
            
            if not multi_project_leaders:
                print(f"  该年度没有负责人提交多个项目")
                continue
            
            # 分析分组分布特征
            group_distribution = {
                '1个组': 0,  # 所有项目在同一个细分组
                '2个组': 0,
                '3个组': 0,
                '4个组及以上': 0
            }
            
            comp_group_distribution = {
                '1个大类': 0,  # 所有项目在同一个大类（基层/综合/进阶）
                '2个大类': 0,
                '3个大类': 0
            }
            
            # 详细案例
            examples = {
                '1个组': [],
                '2个组': [],
                '3个组': [],
                '4个组及以上': []
            }
            
            for leader_key, projects in multi_project_leaders.items():
                leader_name = leader_key.split('_')[0]
                
                # 统计细分组（group_name: A1, B2, C1等）
                group_names = [p['group_name'] for p in projects if p['group_name']]
                unique_groups = set(group_names)
                group_count = len(unique_groups)
                
                # 统计大类（competition_group: 基层组/综合组/进阶组）
                comp_groups = [p['competition_group'] for p in projects if p['competition_group']]
                unique_comp_groups = set(comp_groups)
                comp_group_count = len(unique_comp_groups)
                
                # 分类统计
                if group_count == 1:
                    group_distribution['1个组'] += 1
                    if len(examples['1个组']) < 3:
                        examples['1个组'].append({
                            'leader': leader_name,
                            'count': len(projects),
                            'groups': list(unique_groups),
                            'institution': projects[0]['institution']
                        })
                elif group_count == 2:
                    group_distribution['2个组'] += 1
                    if len(examples['2个组']) < 3:
                        examples['2个组'].append({
                            'leader': leader_name,
                            'count': len(projects),
                            'groups': list(unique_groups),
                            'institution': projects[0]['institution']
                        })
                elif group_count == 3:
                    group_distribution['3个组'] += 1
                    if len(examples['3个组']) < 3:
                        examples['3个组'].append({
                            'leader': leader_name,
                            'count': len(projects),
                            'groups': list(unique_groups),
                            'institution': projects[0]['institution']
                        })
                else:
                    group_distribution['4个组及以上'] += 1
                    if len(examples['4个组及以上']) < 3:
                        examples['4个组及以上'].append({
                            'leader': leader_name,
                            'count': len(projects),
                            'groups': list(unique_groups),
                            'institution': projects[0]['institution']
                        })
                
                # 大类统计
                if comp_group_count == 1:
                    comp_group_distribution['1个大类'] += 1
                elif comp_group_count == 2:
                    comp_group_distribution['2个大类'] += 1
                elif comp_group_count >= 3:
                    comp_group_distribution['3个大类'] += 1
            
            # 输出细分组分布
            print(f"\n  细分组分布（A1/B2/C1等）:")
            total = len(multi_project_leaders)
            for key in ['1个组', '2个组', '3个组', '4个组及以上']:
                count = group_distribution[key]
                pct = count / total * 100 if total > 0 else 0
                print(f"    {key}: {count} 人 ({pct:.1f}%)")
            
            # 输出大类分布
            print(f"\n  大类分布（基层组/综合组/进阶组）:")
            for key in ['1个大类', '2个大类', '3个大类']:
                count = comp_group_distribution[key]
                pct = count / total * 100 if total > 0 else 0
                print(f"    {key}: {count} 人 ({pct:.1f}%)")
            
            # 输出典型案例
            print(f"\n  典型案例:")
            for category, cases in examples.items():
                if cases:
                    print(f"\n    {category}:")
                    for case in cases:
                        print(f"      - {case['leader']} ({case['institution']})")
                        print(f"        提交 {case['count']} 个项目，分布在: {', '.join(case['groups'])}")
        
        # 4. 总体统计
        print(f"\n{'='*80}")
        print(f"总体统计")
        print(f"{'='*80}")
        
        all_multi_leaders = []
        for year, leaders in year_leader_projects.items():
            for leader_key, projects in leaders.items():
                if len(projects) > 1:
                    group_names = [p['group_name'] for p in projects if p['group_name']]
                    unique_groups = set(group_names)
                    all_multi_leaders.append(len(unique_groups))
        
        if all_multi_leaders:
            group_counter = Counter(all_multi_leaders)
            print(f"\n  提交多个项目的负责人总数: {len(all_multi_leaders)}")
            print(f"\n  分组数量分布:")
            for group_count in sorted(group_counter.keys()):
                count = group_counter[group_count]
                pct = count / len(all_multi_leaders) * 100
                print(f"    {group_count}个组: {count} 人 ({pct:.1f}%)")
            
            # 计算平均值
            avg_groups = sum(all_multi_leaders) / len(all_multi_leaders)
            print(f"\n  平均分组数: {avg_groups:.2f}")
        
        # 5. 结论
        print(f"\n{'='*80}")
        print(f"结论")
        print(f"{'='*80}")
        
        if all_multi_leaders:
            one_group_pct = group_counter.get(1, 0) / len(all_multi_leaders) * 100
            two_groups_pct = group_counter.get(2, 0) / len(all_multi_leaders) * 100
            three_groups_pct = group_counter.get(3, 0) / len(all_multi_leaders) * 100
            
            print(f"\n  1. 同一负责人提交多个项目时:")
            print(f"     - {one_group_pct:.1f}% 的情况下，所有项目在同一个细分组")
            print(f"     - {two_groups_pct:.1f}% 的情况下，项目分布在2个细分组")
            print(f"     - {three_groups_pct:.1f}% 的情况下，项目分布在3个细分组")
            
            if one_group_pct > 50:
                print(f"\n  2. 主要特征: 大多数负责人的多个项目集中在同一个组")
            elif two_groups_pct > 40:
                print(f"\n  2. 主要特征: 负责人的多个项目倾向于分布在2个组")
            else:
                print(f"\n  2. 主要特征: 负责人的多个项目分组较为分散")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n[ERROR] 分析失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_leader_projects()
