#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证组别统计逻辑 - 直接查询数据库模拟API计算
"""

import sys
import io
import pymysql
from collections import defaultdict
from db_config import DB_CONFIG

# 设置输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def verify_group_stats():
    """验证组别统计逻辑"""
    conn = pymysql.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    print("=" * 80)
    print("验证组别统计逻辑 - 模拟API计算")
    print("=" * 80)
    
    # 获取最新赛事
    cur.execute("""
        SELECT id, name 
        FROM competitions 
        ORDER BY id DESC 
        LIMIT 1
    """)
    competition = cur.fetchone()
    
    if not competition:
        print("没有找到赛事数据")
        return
    
    competition_id, competition_name = competition
    print(f"\n赛事: {competition_name} (ID: {competition_id})")
    
    # 获取所有报名数据
    cur.execute("""
        SELECT 
            r.id,
            r.group_type,
            r.institution_id
        FROM registrations r
        WHERE r.competition_id = %s
    """, (competition_id,))
    
    registrations = cur.fetchall()
    
    if not registrations:
        print("该赛事没有报名数据")
        return
    
    # 统计总数
    total_projects = len(registrations)
    unique_institutions = set()
    
    # 按组别分组
    group_stats = {
        'BASIC': {'institutions': set(), 'projects': []},
        'COMPREHENSIVE': {'institutions': set(), 'projects': []},
        'ADVANCED': {'institutions': set(), 'projects': []}
    }
    
    for reg_id, group_type, inst_id in registrations:
        if inst_id:
            unique_institutions.add(inst_id)
        
        if group_type in group_stats:
            group_stats[group_type]['projects'].append(reg_id)
            if inst_id:
                group_stats[group_type]['institutions'].add(inst_id)
    
    total_institutions = len(unique_institutions)
    
    print(f"\n[总体统计]")
    print(f"  总项目数: {total_projects}")
    print(f"  总机构数: {total_institutions}")
    
    print(f"\n[组别统计] (模拟API返回)")
    print(f"{'组别':<15} {'机构数':<10} {'项目数':<10} {'项目占比':<12} {'平均项目/机构':<15}")
    print("-" * 70)
    
    group_names = {
        'BASIC': '基层组',
        'COMPREHENSIVE': '综合组',
        'ADVANCED': '进阶组'
    }
    
    result_list = []
    
    for group_type in ['BASIC', 'COMPREHENSIVE', 'ADVANCED']:
        stats = group_stats[group_type]
        inst_count = len(stats['institutions'])
        proj_count = len(stats['projects'])
        percentage = (proj_count * 100.0 / total_projects) if total_projects > 0 else 0.0
        avg_proj = (proj_count * 1.0 / inst_count) if inst_count > 0 else 0.0
        
        # 保留小数位
        percentage = round(percentage * 10.0) / 10.0  # 1位小数
        avg_proj = round(avg_proj * 100.0) / 100.0    # 2位小数
        
        group_name = group_names[group_type]
        
        print(f"{group_name:<15} {inst_count:<10} {proj_count:<10} {percentage:<11.1f}% {avg_proj:<15.2f}")
        
        result_list.append({
            'groupType': group_type,
            'groupTypeName': group_name,
            'institutionCount': inst_count,
            'projectCount': proj_count,
            'projectPercentage': percentage,
            'avgProjectsPerInstitution': avg_proj
        })
    
    # 输出JSON格式
    print(f"\n[JSON格式输出]")
    import json
    print(json.dumps({
        'competitionId': competition_id,
        'competitionName': competition_name,
        'registrationCount': total_projects,
        'institutionCount': total_institutions,
        'groupTypeStats': result_list
    }, indent=2, ensure_ascii=False))
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    try:
        verify_group_stats()
    except Exception as e:
        print(f"[ERROR] 错误: {e}")
        import traceback
        traceback.print_exc()
