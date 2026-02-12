#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析历史数据表的分组特征
检查:
1. 每个机构的项目散落在几个分组内
2. 每个分组的项目数量分布是否均衡
"""

import sys
import io
import pymysql
from collections import defaultdict
from db_config import DB_CONFIG

# 设置输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def analyze_grouping_by_year():
    """按年度分析分组特征"""
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
    print("历史数据分组特征分析")
    print("=" * 80)
    
    for year in years:
        print(f"\n{'='*80}")
        print(f"年度: {year}")
        print(f"{'='*80}")
        
        # 获取该年度的所有数据 - 使用 group_name (A1/B1/C1等)
        cur.execute("""
            SELECT 
                institution_name,
                group_name,
                project_name,
                competition_group
            FROM pinguan_his_data 
            WHERE year = %s AND group_name IS NOT NULL AND group_name != ''
            ORDER BY institution_name, group_name
        """, (year,))
        
        rows = cur.fetchall()
        
        if not rows:
            print(f"  [WARN] 该年度无分组数据")
            continue
        
        # 统计数据
        institution_groups = defaultdict(set)  # 机构 -> 分组集合 (A1/B1/C1等)
        institution_projects = defaultdict(list)  # 机构 -> 项目列表
        group_counts = defaultdict(int)  # 分组 -> 项目数
        competition_group_stats = defaultdict(lambda: defaultdict(set))  # 基层/综合/进阶 -> 机构 -> 分组集合
        
        for inst_name, group_name, proj_name, competition_group in rows:
            institution_groups[inst_name].add(group_name)
            institution_projects[inst_name].append((group_name, proj_name))
            group_counts[group_name] += 1
            if competition_group:
                competition_group_stats[competition_group][inst_name].add(group_name)
        
        # 分析1: 机构分组分布
        print(f"\n[统计] 机构分组分布统计:")
        print(f"  总机构数: {len(institution_groups)}")
        print(f"  总项目数: {len(rows)}")
        print(f"  总分组数: {len(group_counts)}")
        
        # 统计机构散落在几个分组
        group_spread = defaultdict(int)
        for inst, groups in institution_groups.items():
            group_spread[len(groups)] += 1
        
        print(f"\n  机构分组散落情况:")
        for num_groups in sorted(group_spread.keys()):
            count = group_spread[num_groups]
            percentage = count / len(institution_groups) * 100
            print(f"    散落在 {num_groups} 个分组: {count} 个机构 ({percentage:.1f}%)")
        
        # 分析2: 每个分组的项目数量
        print(f"\n[统计] 分组项目数量分布:")
        group_sizes = list(group_counts.values())
        avg_size = sum(group_sizes) / len(group_sizes)
        min_size = min(group_sizes)
        max_size = max(group_sizes)
        
        print(f"  平均每组项目数: {avg_size:.1f}")
        print(f"  最小组项目数: {min_size}")
        print(f"  最大组项目数: {max_size}")
        print(f"  标准差: {calculate_std(group_sizes):.2f}")
        
        # 显示项目数分布
        size_distribution = defaultdict(int)
        for size in group_sizes:
            size_range = (size // 5) * 5  # 按5分组
            size_distribution[size_range] += 1
        
        print(f"\n  项目数分布:")
        for size_range in sorted(size_distribution.keys()):
            count = size_distribution[size_range]
            print(f"    {size_range}-{size_range+4}个项目: {count} 个分组")
        
        # 分析3: 按竞赛组别统计 (基层/综合/进阶)
        if competition_group_stats:
            print(f"\n[统计] 按竞赛组别分析 (基层/综合/进阶):")
            for comp_group in sorted(competition_group_stats.keys()):
                type_data = competition_group_stats[comp_group]
                print(f"\n  {comp_group}:")
                print(f"    机构数: {len(type_data)}")
                
                # 统计该竞赛组别下的分组数量
                all_groups_in_type = set()
                for inst, groups in type_data.items():
                    all_groups_in_type.update(groups)
                print(f"    分组数: {len(all_groups_in_type)} ({', '.join(sorted(all_groups_in_type))})")
                
                type_spread = defaultdict(int)
                for inst, groups in type_data.items():
                    type_spread[len(groups)] += 1
                
                for num_groups in sorted(type_spread.keys()):
                    count = type_spread[num_groups]
                    percentage = count / len(type_data) * 100
                    print(f"      散落在 {num_groups} 个分组: {count} 个机构 ({percentage:.1f}%)")
        
        # 分析4: 典型案例展示
        print(f"\n[案例] 典型案例展示 (散落在2-3个分组的机构):")
        examples_shown = 0
        for inst, groups in sorted(institution_groups.items(), key=lambda x: len(x[1]), reverse=True):
            if 2 <= len(groups) <= 3 and examples_shown < 5:
                projects = institution_projects[inst]
                print(f"\n  机构: {inst}")
                print(f"  分组: {', '.join(sorted(groups))}")
                print(f"  项目数: {len(projects)}")
                
                # 显示每个分组的项目数
                group_proj_count = defaultdict(int)
                for group_name, _ in projects:
                    group_proj_count[group_name] += 1
                
                for group_name in sorted(groups):
                    print(f"    {group_name}: {group_proj_count[group_name]} 个项目")
                
                examples_shown += 1
        
        # 分析5: 异常情况
        print(f"\n[检查] 异常情况检查:")
        
        # 散落在4个以上分组的机构
        over_spread = [(inst, groups) for inst, groups in institution_groups.items() if len(groups) > 3]
        if over_spread:
            print(f"  散落在4个以上分组的机构: {len(over_spread)} 个")
            for inst, groups in over_spread[:3]:
                print(f"    {inst}: {len(groups)} 个分组 ({', '.join(sorted(groups))})")
        else:
            print(f"  [OK] 无机构散落在4个以上分组")
        
        # 项目数过少或过多的分组
        small_groups = [g for g, c in group_counts.items() if c < 3]
        large_groups = [g for g, c in group_counts.items() if c > 15]
        
        if small_groups:
            print(f"  项目数<3的分组: {len(small_groups)} 个")
        if large_groups:
            print(f"  项目数>15的分组: {len(large_groups)} 个")
    
    cur.close()
    conn.close()

def calculate_std(values):
    """计算标准差"""
    if not values:
        return 0
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return variance ** 0.5

if __name__ == "__main__":
    try:
        analyze_grouping_by_year()
    except Exception as e:
        print(f"[ERROR] 错误: {e}")
        import traceback
        traceback.print_exc()
