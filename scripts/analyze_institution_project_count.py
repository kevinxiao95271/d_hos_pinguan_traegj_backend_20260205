#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析历史数据中机构的项目数量分布
"""

import sys
import io
import pymysql
from collections import defaultdict, Counter
from db_config import DB_CONFIG

# 设置输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def analyze_institution_project_distribution():
    """分析机构项目数量分布"""
    conn = pymysql.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # 获取所有年度
    cur.execute("""
        SELECT DISTINCT year 
        FROM pinguan_his_data 
        WHERE year IS NOT NULL 
        ORDER BY year DESC
    """)
    years = [row[0] for row in cur.fetchall()]
    
    print("=" * 80)
    print("机构项目数量分布分析")
    print("=" * 80)
    
    for year in years:
        print(f"\n{'='*80}")
        print(f"年度: {year}")
        print(f"{'='*80}")
        
        # 统计每个机构的项目数
        cur.execute("""
            SELECT 
                institution_name,
                COUNT(*) as project_count
            FROM pinguan_his_data 
            WHERE year = %s AND institution_name IS NOT NULL
            GROUP BY institution_name
            ORDER BY project_count DESC, institution_name
        """, (year,))
        
        institution_counts = cur.fetchall()
        
        if not institution_counts:
            print(f"  [WARN] 该年度无数据")
            continue
        
        # 统计数据
        total_institutions = len(institution_counts)
        total_projects = sum(count for _, count in institution_counts)
        
        # 按项目数分组统计
        count_distribution = Counter(count for _, count in institution_counts)
        
        print(f"\n[总体统计]")
        print(f"  总机构数: {total_institutions}")
        print(f"  总项目数: {total_projects}")
        print(f"  平均每机构: {total_projects / total_institutions:.2f} 个项目")
        
        # 项目数分布
        print(f"\n[项目数分布]")
        for project_count in sorted(count_distribution.keys()):
            inst_count = count_distribution[project_count]
            percentage = inst_count / total_institutions * 100
            total_proj = project_count * inst_count
            proj_percentage = total_proj / total_projects * 100
            print(f"  {project_count}个项目: {inst_count}个机构 ({percentage:.1f}%) - 共{total_proj}个项目 ({proj_percentage:.1f}%)")
        
        # 按范围统计
        print(f"\n[按范围统计]")
        ranges = [
            (1, 1, "1个项目"),
            (2, 2, "2个项目"),
            (3, 3, "3个项目"),
            (4, 5, "4-5个项目"),
            (6, 8, "6-8个项目"),
            (9, float('inf'), "9个以上项目")
        ]
        
        for min_count, max_count, label in ranges:
            inst_in_range = sum(1 for _, count in institution_counts if min_count <= count <= max_count)
            proj_in_range = sum(count for _, count in institution_counts if min_count <= count <= max_count)
            if inst_in_range > 0:
                inst_pct = inst_in_range / total_institutions * 100
                proj_pct = proj_in_range / total_projects * 100
                print(f"  {label}: {inst_in_range}个机构 ({inst_pct:.1f}%) - 共{proj_in_range}个项目 ({proj_pct:.1f}%)")
        
        # 显示项目数最多的前10个机构
        print(f"\n[TOP 10 机构 - 按项目数排序]")
        for i, (inst_name, count) in enumerate(institution_counts[:10], 1):
            print(f"  {i}. {inst_name}: {count}个项目")
        
        # 按竞赛组别分析
        print(f"\n[按竞赛组别分析]")
        for comp_group in ['基层组', '综合组', '进阶组']:
            cur.execute("""
                SELECT 
                    institution_name,
                    COUNT(*) as project_count
                FROM pinguan_his_data 
                WHERE year = %s 
                    AND competition_group = %s
                    AND institution_name IS NOT NULL
                GROUP BY institution_name
                ORDER BY project_count DESC
            """, (year, comp_group))
            
            group_data = cur.fetchall()
            if not group_data:
                continue
            
            group_total_inst = len(group_data)
            group_total_proj = sum(count for _, count in group_data)
            group_avg = group_total_proj / group_total_inst
            
            # 项目数分布
            group_distribution = Counter(count for _, count in group_data)
            
            print(f"\n  {comp_group}:")
            print(f"    机构数: {group_total_inst}, 项目数: {group_total_proj}, 平均: {group_avg:.2f}")
            print(f"    分布:")
            for project_count in sorted(group_distribution.keys()):
                inst_count = group_distribution[project_count]
                percentage = inst_count / group_total_inst * 100
                print(f"      {project_count}个项目: {inst_count}个机构 ({percentage:.1f}%)")
            
            # 显示该组别项目数最多的前3个机构
            if len(group_data) > 0:
                print(f"    TOP 3:")
                for i, (inst_name, count) in enumerate(group_data[:3], 1):
                    print(f"      {i}. {inst_name}: {count}个项目")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    try:
        analyze_institution_project_distribution()
    except Exception as e:
        print(f"[ERROR] 错误: {e}")
        import traceback
        traceback.print_exc()
