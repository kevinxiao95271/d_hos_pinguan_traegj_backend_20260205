#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析舟山医院的报名分布情况
按年度统计项目数、组别分布、负责人分布等
"""

import sys
import io
import pymysql
from collections import defaultdict
from db_config import DB_CONFIG

# 设置输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def analyze_zhoushan_distribution():
    """分析舟山医院的报名分布"""
    conn = pymysql.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    print("=" * 80)
    print("舟山医院报名分布分析")
    print("=" * 80)
    
    # 获取所有年度
    cur.execute("""
        SELECT DISTINCT year 
        FROM pinguan_his_data
        WHERE year IS NOT NULL
        ORDER BY year DESC
    """)
    years = [row[0] for row in cur.fetchall()]
    
    for year in years:
        print(f"\n{'='*80}")
        print(f"年度: {year}")
        print(f"{'='*80}")
        
        # 获取舟山相关医院的所有项目
        cur.execute("""
            SELECT 
                institution_name,
                project_name,
                project_leader_name,
                competition_group,
                group_name
            FROM pinguan_his_data
            WHERE year = %s 
                AND institution_name LIKE '%%舟山%%'
            ORDER BY institution_name, project_leader_name
        """, (year,))
        
        rows = cur.fetchall()
        
        if not rows:
            print(f"  [INFO] 该年度无舟山医院数据")
            continue
        
        print(f"\n[总体统计]")
        print(f"  总项目数: {len(rows)}")
        
        # 按医院统计
        by_institution = defaultdict(list)
        for inst_name, proj_name, leader_name, comp_group, group_name in rows:
            by_institution[inst_name].append({
                'project': proj_name,
                'leader': leader_name,
                'comp_group': comp_group,
                'group_name': group_name
            })
        
        print(f"  医院数: {len(by_institution)}")
        
        # 显示各医院统计
        print(f"\n[按医院统计]")
        for inst_name in sorted(by_institution.keys()):
            projects = by_institution[inst_name]
            print(f"\n  {inst_name}: {len(projects)}个项目")
            
            # 统计组别分布
            comp_group_stats = defaultdict(int)
            for proj in projects:
                if proj['comp_group']:
                    comp_group_stats[proj['comp_group']] += 1
            
            if comp_group_stats:
                print(f"    组别分布:")
                for comp_group in sorted(comp_group_stats.keys()):
                    count = comp_group_stats[comp_group]
                    percentage = count / len(projects) * 100
                    print(f"      {comp_group}: {count}个项目 ({percentage:.1f}%)")
            
            # 统计负责人
            leaders = defaultdict(list)
            for proj in projects:
                leaders[proj['leader']].append(proj['project'])
            
            print(f"    负责人数: {len(leaders)}")
            
            # 显示提交多个项目的负责人
            multi_project_leaders = {name: projs for name, projs in leaders.items() if len(projs) > 1}
            if multi_project_leaders:
                print(f"    提交多个项目的负责人: {len(multi_project_leaders)}人")
                for leader_name in sorted(multi_project_leaders.keys()):
                    projs = multi_project_leaders[leader_name]
                    print(f"      {leader_name}: {len(projs)}个项目")
                    for proj_name in projs:
                        print(f"        - {proj_name}")
            else:
                print(f"    [OK] 没有负责人提交多个项目")
            
            # 统计细分组分布
            group_name_stats = defaultdict(int)
            for proj in projects:
                if proj['group_name']:
                    group_name_stats[proj['group_name']] += 1
            
            if group_name_stats:
                print(f"    细分组分布: {len(group_name_stats)}个分组")
                for group_name in sorted(group_name_stats.keys()):
                    count = group_name_stats[group_name]
                    print(f"      {group_name}: {count}个项目")
        
        # 按组别统计
        print(f"\n[按组别统计]")
        by_comp_group = defaultdict(lambda: defaultdict(list))
        for inst_name, proj_name, leader_name, comp_group, group_name in rows:
            if comp_group:
                by_comp_group[comp_group][inst_name].append({
                    'project': proj_name,
                    'leader': leader_name,
                    'group_name': group_name
                })
        
        for comp_group in sorted(by_comp_group.keys()):
            institutions = by_comp_group[comp_group]
            total_projects = sum(len(projs) for projs in institutions.values())
            print(f"\n  {comp_group}: {total_projects}个项目, {len(institutions)}家医院")
            
            for inst_name in sorted(institutions.keys()):
                projects = institutions[inst_name]
                print(f"    {inst_name}: {len(projects)}个项目")
        
        # 按负责人统计
        print(f"\n[按负责人统计]")
        by_leader = defaultdict(lambda: defaultdict(list))
        for inst_name, proj_name, leader_name, comp_group, group_name in rows:
            by_leader[leader_name][inst_name].append({
                'project': proj_name,
                'comp_group': comp_group,
                'group_name': group_name
            })
        
        # 只显示提交多个项目的负责人
        multi_project_leaders = {name: data for name, data in by_leader.items() if sum(len(projs) for projs in data.values()) > 1}
        
        if multi_project_leaders:
            print(f"  提交多个项目的负责人: {len(multi_project_leaders)}人")
            for leader_name in sorted(multi_project_leaders.keys()):
                institutions = multi_project_leaders[leader_name]
                total_projects = sum(len(projs) for projs in institutions.values())
                print(f"\n    {leader_name}: {total_projects}个项目")
                
                for inst_name in sorted(institutions.keys()):
                    projects = institutions[inst_name]
                    print(f"      {inst_name}:")
                    
                    for proj in projects:
                        comp_group = proj['comp_group'] or '未分类'
                        group_name = proj['group_name'] or '未分组'
                        print(f"        - {proj['project']} [{comp_group}/{group_name}]")
        else:
            print(f"  [OK] 没有负责人提交多个项目")
        
        # 细分组散落分析
        print(f"\n[细分组散落分析]")
        institution_groups = defaultdict(set)
        for inst_name, proj_name, leader_name, comp_group, group_name in rows:
            if group_name:
                institution_groups[inst_name].add(group_name)
        
        if institution_groups:
            spread_stats = defaultdict(int)
            for inst_name, groups in institution_groups.items():
                spread_stats[len(groups)] += 1
            
            print(f"  医院项目散落在多少个细分组:")
            for num_groups in sorted(spread_stats.keys()):
                count = spread_stats[num_groups]
                percentage = count / len(institution_groups) * 100
                print(f"    散落在{num_groups}个分组: {count}家医院 ({percentage:.1f}%)")
            
            # 显示散落在3个以上分组的医院
            over_spread = [(inst, groups) for inst, groups in institution_groups.items() if len(groups) > 3]
            if over_spread:
                print(f"\n  [WARNING] 散落在4个以上分组的医院:")
                for inst, groups in over_spread:
                    print(f"    {inst}: {len(groups)}个分组 ({', '.join(sorted(groups))})")
            else:
                print(f"\n  [OK] 没有医院散落在4个以上分组")
    
    # 跨年度对比
    if len(years) > 1:
        print(f"\n{'='*80}")
        print(f"跨年度对比")
        print(f"{'='*80}")
        
        print(f"\n{'年度':<10} {'总项目数':<10} {'医院数':<10} {'负责人数':<10} {'多项目负责人':<15}")
        print("-" * 60)
        
        for year in sorted(years):
            cur.execute("""
                SELECT 
                    COUNT(*) as project_count,
                    COUNT(DISTINCT institution_name) as institution_count,
                    COUNT(DISTINCT project_leader_name) as leader_count
                FROM pinguan_his_data
                WHERE year = %s AND institution_name LIKE '%%舟山%%'
            """, (year,))
            
            project_count, institution_count, leader_count = cur.fetchone()
            
            # 统计多项目负责人
            cur.execute("""
                SELECT project_leader_name, COUNT(*) as cnt
                FROM pinguan_his_data
                WHERE year = %s AND institution_name LIKE '%%舟山%%'
                GROUP BY project_leader_name
                HAVING COUNT(*) > 1
            """, (year,))
            
            multi_project_leaders = cur.fetchall()
            multi_count = len(multi_project_leaders)
            
            print(f"{year:<10} {project_count:<10} {institution_count:<10} {leader_count:<10} {multi_count:<15}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    try:
        analyze_zhoushan_distribution()
    except Exception as e:
        print(f"[ERROR] 错误: {e}")
        import traceback
        traceback.print_exc()
