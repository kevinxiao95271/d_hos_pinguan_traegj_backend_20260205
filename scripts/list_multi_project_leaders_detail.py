#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
列出所有提交多个项目的负责人详细信息
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

def list_multi_project_leaders():
    """列出所有提交多个项目的负责人"""
    
    print("=" * 100)
    print("提交多个项目的负责人详细名单")
    print("=" * 100)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # 查询所有历史数据
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
              AND competition_group IS NOT NULL
            ORDER BY year, project_leader_name, institution_name
        """)
        
        all_data = cur.fetchall()
        
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
            multi_project_leaders = {k: v for k, v in leaders.items() if len(v) > 1}
            
            print(f"\n提交多个项目的负责人数: {len(multi_project_leaders)}")
            
            # 按大类分组
            single_group_leaders = []
            cross_group_leaders = []
            
            for leader_key, projects in sorted(multi_project_leaders.items()):
                leader_name = leader_key.split('_')[0]
                leader_phone = projects[0]['phone']
                
                comp_groups = [p['competition_group'] for p in projects]
                unique_groups = set(comp_groups)
                
                leader_info = {
                    'name': leader_name,
                    'phone': leader_phone,
                    'institution': projects[0]['institution'],
                    'project_count': len(projects),
                    'groups': list(unique_groups),
                    'projects': projects
                }
                
                if len(unique_groups) == 1:
                    single_group_leaders.append(leader_info)
                else:
                    cross_group_leaders.append(leader_info)
            
            # 输出同一大类的负责人
            print(f"\n{'─'*100}")
            print(f"【同一大类】共 {len(single_group_leaders)} 人")
            print(f"{'─'*100}")
            
            # 按大类分组输出
            basic_leaders = [l for l in single_group_leaders if '基层' in l['groups'][0]]
            comprehensive_leaders = [l for l in single_group_leaders if '综合' in l['groups'][0]]
            advanced_leaders = [l for l in single_group_leaders if '进阶' in l['groups'][0]]
            
            if basic_leaders:
                print(f"\n仅基层组 ({len(basic_leaders)}人):")
                for i, leader in enumerate(basic_leaders, 1):
                    print(f"\n  {i}. {leader['name']} (手机: {leader['phone']})")
                    print(f"     机构: {leader['institution']}")
                    print(f"     项目数: {leader['project_count']}")
                    for j, proj in enumerate(leader['projects'], 1):
                        print(f"     项目{j}: {proj['project_name'][:50]}...")
                        print(f"            [{proj['competition_group']}] {proj['group_name']}")
            
            if comprehensive_leaders:
                print(f"\n仅综合组 ({len(comprehensive_leaders)}人):")
                for i, leader in enumerate(comprehensive_leaders, 1):
                    print(f"\n  {i}. {leader['name']} (手机: {leader['phone']})")
                    print(f"     机构: {leader['institution']}")
                    print(f"     项目数: {leader['project_count']}")
                    for j, proj in enumerate(leader['projects'], 1):
                        print(f"     项目{j}: {proj['project_name'][:50]}...")
                        print(f"            [{proj['competition_group']}] {proj['group_name']}")
            
            if advanced_leaders:
                print(f"\n仅进阶组 ({len(advanced_leaders)}人):")
                for i, leader in enumerate(advanced_leaders, 1):
                    print(f"\n  {i}. {leader['name']} (手机: {leader['phone']})")
                    print(f"     机构: {leader['institution']}")
                    print(f"     项目数: {leader['project_count']}")
                    for j, proj in enumerate(leader['projects'], 1):
                        print(f"     项目{j}: {proj['project_name'][:50]}...")
                        print(f"            [{proj['competition_group']}] {proj['group_name']}")
            
            # 输出跨大类的负责人
            print(f"\n{'─'*100}")
            print(f"【跨大类】共 {len(cross_group_leaders)} 人")
            print(f"{'─'*100}")
            
            for i, leader in enumerate(cross_group_leaders, 1):
                groups_str = ' + '.join(leader['groups'])
                print(f"\n  {i}. {leader['name']} (手机: {leader['phone']})")
                print(f"     机构: {leader['institution']}")
                print(f"     项目数: {leader['project_count']}")
                print(f"     跨大类: {groups_str}")
                for j, proj in enumerate(leader['projects'], 1):
                    print(f"     项目{j}: {proj['project_name'][:50]}...")
                    print(f"            [{proj['competition_group']}] {proj['group_name']}")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 100)
        
    except Exception as e:
        print(f"\n[ERROR] 查询失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    list_multi_project_leaders()
