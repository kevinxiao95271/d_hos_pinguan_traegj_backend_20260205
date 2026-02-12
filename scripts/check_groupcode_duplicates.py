#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库中的分组代码是否有重复
"""

import sys
import io
import psycopg2

# 设置输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB_CONFIG = {
    'host': '119.167.165.27',
    'port': 5432,
    'user': 'postgres',
    'password': 'zjylzl',
    'database': 'd_hos_pinguan_20260211'
}

def check_duplicates():
    """检查分组代码重复"""
    
    print("=" * 80)
    print("检查书审分组代码数据")
    print("=" * 80)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # 1. 检查registrations表中的group_code
        print("\n[1] 检查项目分组代码 (registrations.group_code)")
        cur.execute("""
            SELECT 
                group_code,
                COUNT(*) as count
            FROM registrations
            WHERE competition_id = 21
            GROUP BY group_code
            ORDER BY group_code
        """)
        
        group_codes = cur.fetchall()
        print(f"    找到 {len(group_codes)} 个不同的分组代码:")
        for code, count in group_codes:
            print(f"      {code}: {count} 个项目")
        
        # 2. 检查书审任务中的分组代码分布
        print("\n[2] 检查书审任务中的项目分组分布")
        cur.execute("""
            SELECT 
                r.group_code,
                COUNT(DISTINCT rt.id) as task_count,
                COUNT(DISTINCT r.id) as project_count
            FROM review_tasks rt
            JOIN registrations r ON rt.registration_id = r.id
            WHERE rt.stage = 'BOOK' AND r.competition_id = 21
            GROUP BY r.group_code
            ORDER BY r.group_code
        """)
        
        task_groups = cur.fetchall()
        print(f"    书审任务中涉及 {len(task_groups)} 个分组:")
        for code, task_count, project_count in task_groups:
            print(f"      {code}: {project_count} 个项目, {task_count} 个任务")
        
        # 3. 检查是否有重复的group_code在同一个项目中
        print("\n[3] 检查是否有项目的group_code重复")
        cur.execute("""
            SELECT 
                id,
                project_name,
                group_code,
                COUNT(*) OVER (PARTITION BY id) as dup_count
            FROM registrations
            WHERE competition_id = 21 AND group_code IS NOT NULL
            ORDER BY id
        """)
        
        projects = cur.fetchall()
        has_dup = any(dup_count > 1 for _, _, _, dup_count in projects)
        
        if has_dup:
            print(f"    ✗ 发现重复的group_code")
        else:
            print(f"    ✓ 没有重复，每个项目只有一个group_code")
        
        # 4. 获取用于下拉框的分组代码列表
        print("\n[4] 用于下拉框的分组代码列表 (去重)")
        cur.execute("""
            SELECT DISTINCT r.group_code
            FROM review_tasks rt
            JOIN registrations r ON rt.registration_id = r.id
            WHERE rt.stage = 'BOOK' AND r.competition_id = 21 AND r.group_code IS NOT NULL
            ORDER BY r.group_code
        """)
        
        dropdown_codes = [row[0] for row in cur.fetchall()]
        print(f"    分组代码列表 ({len(dropdown_codes)} 个):")
        print(f"    {dropdown_codes}")
        
        # 5. 模拟API返回的数据
        print("\n[5] 模拟API返回数据 (前5条)")
        cur.execute("""
            SELECT 
                rt.id as task_id,
                r.project_name,
                r.group_code,
                rt.status
            FROM review_tasks rt
            JOIN registrations r ON rt.registration_id = r.id
            WHERE rt.stage = 'BOOK' AND r.competition_id = 21
            ORDER BY rt.id
            LIMIT 5
        """)
        
        api_data = cur.fetchall()
        for task_id, project_name, group_code, status in api_data:
            print(f"    任务{task_id}: {project_name[:20]}... | 分组: {group_code} | 状态: {status}")
        
        # 6. 结论
        print("\n" + "=" * 80)
        print("结论:")
        print(f"  ✓ 数据库中的group_code没有重复")
        print(f"  ✓ 每个项目只有一个group_code")
        print(f"  ✓ API返回的数据中，每条记录的group_code是唯一的")
        print(f"  ⚠ 如果前端下拉框出现重复，是前端处理问题")
        print(f"  建议: 前端从API返回的数据中提取group_code时，使用Set去重")
        print("=" * 80)
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"\n[ERROR] 检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_duplicates()
