#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细分析舟山医院的分组情况
显示每个项目的大类和细分组
"""

import sys
import io
import pymysql
from collections import defaultdict
from db_config import DB_CONFIG

# 设置输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def analyze_zhoushan_detail():
    """详细分析舟山医院的分组"""
    conn = pymysql.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    print("=" * 100)
    print("舟山医院分组详细分析")
    print("=" * 100)
    
    # 获取所有年度
    cur.execute("""
        SELECT DISTINCT year 
        FROM pinguan_his_data
        WHERE year IS NOT NULL
        ORDER BY year DESC
    """)
    years = [row[0] for row in cur.fetchall()]
    
    for year in years:
        print(f"\n{'='*100}")
        print(f"年度: {year}")
        print(f"{'='*100}")
        
        # 获取舟山医院的所有项目
        cur.execute("""
            SELECT 
                institution_name,
                project_name,
                project_leader_name,
                competition_group,
                group_name
            FROM pinguan_his_data
            WHERE year = %s 
                AND institution_name = '舟山医院'
            ORDER BY competition_group, group_name
        """, (year,))
        
        rows = cur.fetchall()
        
        if not rows:
            print(f"  [INFO] 该年度无舟山医院数据")
            continue
        
        print(f"\n舟山医院: {len(rows)}个项目\n")
        
        # 按大类分组
        by_comp_group = defaultdict(list)
        all_groups = set()
        
        for inst_name, proj_name, leader_name, comp_group, group_name in rows:
            by_comp_group[comp_group].append({
                'project': proj_name,
                'leader': leader_name,
                'group_name': group_name
            })
            if group_name:
                all_groups.add(group_name)
        
        print(f"总共散落在 {len(all_groups)} 个细分组: {', '.join(sorted(all_groups))}\n")
        
        # 显示每个大类的详细信息
        for comp_group in sorted(by_comp_group.keys()):
            projects = by_comp_group[comp_group]
            print(f"\n【{comp_group}】 - {len(projects)}个项目")
            print("-" * 100)
            
            # 统计该大类下的细分组
            groups_in_type = set()
            for proj in projects:
                if proj['group_name']:
                    groups_in_type.add(proj['group_name'])
            
            print(f"细分组: {', '.join(sorted(groups_in_type))}\n")
            
            # 按细分组显示项目
            by_group = defaultdict(list)
            for proj in projects:
                group_name = proj['group_name'] or '未分组'
                by_group[group_name].append(proj)
            
            for group_name in sorted(by_group.keys()):
                projs = by_group[group_name]
                print(f"  {group_name}:")
                for proj in projs:
                    print(f"    - {proj['project']}")
                    print(f"      负责人: {proj['leader']}")
                print()
        
        # 分析跨大类情况
        print(f"\n【分组分析】")
        print("-" * 100)
        
        # 统计每个大类的细分组数量
        comp_group_stats = {}
        for comp_group, projects in by_comp_group.items():
            groups = set()
            for proj in projects:
                if proj['group_name']:
                    groups.add(proj['group_name'])
            comp_group_stats[comp_group] = groups
        
        print(f"\n各大类的细分组分布:")
        for comp_group in sorted(comp_group_stats.keys()):
            groups = comp_group_stats[comp_group]
            print(f"  {comp_group}: {len(groups)}个细分组 ({', '.join(sorted(groups))})")
        
        # 判断是否跨大类
        if len(by_comp_group) > 1:
            print(f"\n⚠️ 跨大类报名: 项目分布在 {len(by_comp_group)} 个大类")
            print(f"   大类: {', '.join(sorted(by_comp_group.keys()))}")
        else:
            print(f"\n✅ 未跨大类: 所有项目都在 {list(by_comp_group.keys())[0]}")
        
        # 分析细分组前缀
        print(f"\n细分组前缀分析:")
        prefix_stats = defaultdict(int)
        for group_name in all_groups:
            if group_name:
                prefix = group_name[0]  # A/B/C
                prefix_stats[prefix] += 1
        
        for prefix in sorted(prefix_stats.keys()):
            count = prefix_stats[prefix]
            prefix_name = {'A': '进阶组', 'B': '综合组', 'C': '基层组'}.get(prefix, '未知')
            print(f"  {prefix}组({prefix_name}): {count}个细分组")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    try:
        analyze_zhoushan_detail()
    except Exception as e:
        print(f"[ERROR] 错误: {e}")
        import traceback
        traceback.print_exc()
