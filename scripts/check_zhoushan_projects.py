#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查舟山医院的项目提交情况
"""

import sys
import io
import psycopg2
from collections import defaultdict

# 设置输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB_CONFIG = {
    'host': '119.167.165.27',
    'port': 5432,
    'user': 'postgres',
    'password': 'zjylzl',
    'database': 'd_hos_pinguan_20260211'
}

def check_zhoushan():
    """检查舟山医院情况"""
    
    print("=" * 100)
    print("舟山医院项目提交情况分析")
    print("=" * 100)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # 查询舟山相关的所有项目
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
            WHERE institution_name LIKE '%舟山%'
            ORDER BY year, project_leader_name, institution_name
        """)
        
        all_data = cur.fetchall()
        
        print(f"\n舟山相关医院总项目数: {len(all_data)}")
        
        # 统计各医院
        institutions = defaultdict(int)
        for row in all_data:
            institutions[row[1]] += 1
        
        print(f"\n舟山相关医院列表:")
        for inst, count in sorted(institutions.items(), key=lambda x: -x[1]):
            print(f"  {inst}: {count} 个项目")
        
        # 按年度和负责人分组
        year_leader_projects = defaultdict(lambda: defaultdict(list))
        
        for year, inst_name, leader_name, leader_phone, proj_name, comp_group, group_name in all_data:
            leader_key = f"{leader_name}_{leader_phone if leader_phone else 'unknown'}"
            
            year_leader_projects[year][leader_key].append({
                'institution': inst_name,
                'project_name': proj_name,
                'competition_group': comp_group,
                'group_name': group_name,
                'phone': leader_phone
            })
        
        # 按年度输出
        for year in sorted(year_leader_projects.keys()):
            print(f"\n{'='*100}")
            print(f"年度: {year}")
            print(f"{'='*100}")
            
            leaders = year_leader_projects[year]
            
            print(f"\n总负责人数: {len(leaders)}")
            
            # 找出提交多个项目的负责人
            multi_project_leaders = {k: v for k, v in leaders.items() if len(v) > 1}
            
            if multi_project_leaders:
                print(f"提交多个项目的负责人数: {len(multi_project_leaders)}")
                
                for leader_key, projects in sorted(multi_project_leaders.items(), key=lambda x: -len(x[1])):
                    leader_name = leader_key.split('_')[0]
                    leader_phone = projects[0]['phone']
                    
                    print(f"\n  {leader_name} (手机: {leader_phone})")
                    print(f"  机构: {projects[0]['institution']}")
                    print(f"  项目数: {len(projects)}")
                    
                    comp_groups = [p['competition_group'] for p in projects]
                    unique_groups = set(comp_groups)
                    if len(unique_groups) > 1:
                        print(f"  跨大类: {' + '.join(unique_groups)}")
                    else:
                        print(f"  大类: {list(unique_groups)[0]}")
                    
                    for i, proj in enumerate(projects, 1):
                        print(f"    项目{i}: {proj['project_name'][:60]}...")
                        print(f"           [{proj['competition_group']}] {proj['group_name']}")
            else:
                print(f"没有负责人提交多个项目")
            
            # 列出所有项目
            print(f"\n{'─'*100}")
            print(f"所有项目列表:")
            print(f"{'─'*100}")
            
            all_projects = []
            for leader_key, projects in leaders.items():
                leader_name = leader_key.split('_')[0]
                for proj in projects:
                    all_projects.append({
                        'leader': leader_name,
                        'phone': proj['phone'],
                        'institution': proj['institution'],
                        'project': proj['project_name'],
                        'group': proj['competition_group'],
                        'subgroup': proj['group_name']
                    })
            
            for i, proj in enumerate(sorted(all_projects, key=lambda x: (x['institution'], x['leader'])), 1):
                print(f"\n  {i}. {proj['leader']} (手机: {proj['phone']})")
                print(f"     {proj['institution']}")
                print(f"     {proj['project'][:70]}...")
                print(f"     [{proj['group']}] {proj['subgroup']}")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 100)
        
    except Exception as e:
        print(f"\n[ERROR] 查询失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_zhoushan()
