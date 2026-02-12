#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试自动分组算法
验证分组结果是否符合预期
"""

import sys
import io
import pymysql
from collections import defaultdict
from db_config import DB_CONFIG

# 设置输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_auto_grouping():
    """测试自动分组算法"""
    conn = pymysql.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    print("=" * 80)
    print("自动分组算法测试")
    print("=" * 80)
    
    # 获取最新的竞赛ID
    cur.execute("""
        SELECT id, name 
        FROM competitions 
        ORDER BY id DESC 
        LIMIT 1
    """)
    competition = cur.fetchone()
    
    if not competition:
        print("[ERROR] 没有找到竞赛数据")
        return
    
    competition_id, competition_name = competition
    print(f"\n[竞赛] {competition_name} (ID: {competition_id})")
    
    # 统计各组别的报名数据
    cur.execute("""
        SELECT 
            group_type,
            COUNT(*) as project_count,
            COUNT(DISTINCT institution_id) as institution_count
        FROM registrations
        WHERE competition_id = %s
        GROUP BY group_type
        ORDER BY group_type
    """, (competition_id,))
    
    print("\n[统计] 按组别统计:")
    print(f"{'组别':<15} {'项目数':<10} {'机构数':<10}")
    print("-" * 40)
    
    group_stats = {}
    for row in cur.fetchall():
        group_type, project_count, institution_count = row
        group_stats[group_type] = {
            'project_count': project_count,
            'institution_count': institution_count
        }
        print(f"{group_type:<15} {project_count:<10} {institution_count:<10}")
    
    # 分析每个组别的机构项目分布
    for group_type in group_stats.keys():
        print(f"\n{'='*80}")
        print(f"[分析] {group_type} 详细分析")
        print(f"{'='*80}")
        
        # 获取该组别的所有报名
        cur.execute("""
            SELECT 
                r.id,
                r.project_name,
                r.group_code,
                i.id as institution_id,
                i.name as institution_name
            FROM registrations r
            JOIN institutions i ON r.institution_id = i.id
            WHERE r.competition_id = %s AND r.group_type = %s
            ORDER BY i.name, r.id
        """, (competition_id, group_type))
        
        registrations = cur.fetchall()
        
        # 统计机构项目分布
        institution_projects = defaultdict(list)
        institution_groups = defaultdict(set)
        group_counts = defaultdict(int)
        
        for reg_id, proj_name, group_code, inst_id, inst_name in registrations:
            institution_projects[inst_name].append({
                'id': reg_id,
                'name': proj_name,
                'group_code': group_code
            })
            if group_code:
                institution_groups[inst_name].add(group_code)
                group_counts[group_code] += 1
        
        # 统计机构散落情况
        print(f"\n[机构散落] 机构项目散落在多少个分组:")
        spread_stats = defaultdict(int)
        for inst_name, groups in institution_groups.items():
            spread_stats[len(groups)] += 1
        
        for num_groups in sorted(spread_stats.keys()):
            count = spread_stats[num_groups]
            percentage = count / len(institution_groups) * 100 if institution_groups else 0
            print(f"  散落在{num_groups}个分组: {count}个机构 ({percentage:.1f}%)")
        
        # 显示散落在3个以上分组的机构（异常情况）
        over_spread = [(inst, groups) for inst, groups in institution_groups.items() if len(groups) > 3]
        if over_spread:
            print(f"\n  [WARNING] 散落在4个以上分组的机构: {len(over_spread)}个")
            for inst, groups in over_spread[:5]:
                print(f"    {inst}: {len(groups)}个分组 ({', '.join(sorted(groups))})")
        else:
            print(f"\n  [OK] 没有机构散落在4个以上分组")
        
        # 统计分组大小分布
        if group_counts:
            print(f"\n[分组大小] 各分组项目数量:")
            group_sizes = list(group_counts.values())
            avg_size = sum(group_sizes) / len(group_sizes)
            min_size = min(group_sizes)
            max_size = max(group_sizes)
            std_dev = calculate_std(group_sizes)
            
            print(f"  总分组数: {len(group_counts)}")
            print(f"  平均每组: {avg_size:.1f}个项目")
            print(f"  最小组: {min_size}个项目")
            print(f"  最大组: {max_size}个项目")
            print(f"  标准差: {std_dev:.2f}")
            
            if std_dev > 2.5:
                print(f"  [WARNING] 标准差超过2.5，分组不够均衡")
            else:
                print(f"  [OK] 标准差在2.5以内，分组均衡")
            
            # 显示每个分组的详细信息
            print(f"\n  各分组详情:")
            for group_code in sorted(group_counts.keys()):
                count = group_counts[group_code]
                print(f"    {group_code}: {count}个项目")
        else:
            print(f"\n  [INFO] 该组别尚未分组")
        
        # 显示典型案例
        print(f"\n[案例] 典型机构案例 (项目数>=4):")
        examples_shown = 0
        for inst_name in sorted(institution_projects.keys(), key=lambda x: len(institution_projects[x]), reverse=True):
            projects = institution_projects[inst_name]
            if len(projects) >= 4 and examples_shown < 5:
                groups = institution_groups.get(inst_name, set())
                print(f"\n  机构: {inst_name}")
                print(f"  项目数: {len(projects)}")
                print(f"  散落分组: {len(groups)}个 ({', '.join(sorted(groups)) if groups else '未分组'})")
                
                # 统计每个分组的项目数
                if groups:
                    group_proj_count = defaultdict(int)
                    for proj in projects:
                        if proj['group_code']:
                            group_proj_count[proj['group_code']] += 1
                    
                    for group_code in sorted(groups):
                        print(f"    {group_code}: {group_proj_count[group_code]}个项目")
                
                examples_shown += 1
    
    # 总体评估
    print(f"\n{'='*80}")
    print("[总体评估]")
    print(f"{'='*80}")
    
    # 检查是否所有项目都已分组
    cur.execute("""
        SELECT COUNT(*) 
        FROM registrations 
        WHERE competition_id = %s AND (group_code IS NULL OR group_code = '')
    """, (competition_id,))
    ungrouped_count = cur.fetchone()[0]
    
    if ungrouped_count > 0:
        print(f"[WARNING] 还有{ungrouped_count}个项目未分组")
    else:
        print(f"[OK] 所有项目都已分组")
    
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
        test_auto_grouping()
    except Exception as e:
        print(f"[ERROR] 错误: {e}")
        import traceback
        traceback.print_exc()
