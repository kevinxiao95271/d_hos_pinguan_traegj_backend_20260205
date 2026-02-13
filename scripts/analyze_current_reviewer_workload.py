#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析当前系统中评委的评审任务数量
统计2026年竞赛的评委负荷情况
"""

import psycopg2
from collections import defaultdict

# 数据库连接配置
DB_CONFIG = {
    'host': '119.167.165.27',
    'port': 5432,
    'database': 'd_hos_pinguan_20260211',
    'user': 'postgres',
    'password': 'zjylzl'
}

def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    print("=" * 100)
    print("当前系统评委任务负荷分析")
    print("=" * 100)
    
    # 1. 统计评委总数
    print("\n[1] 评委总数统计:")
    cur.execute("""
        SELECT COUNT(*) 
        FROM user_accounts 
        WHERE role = 'REVIEWER'
    """)
    total_reviewers = cur.fetchone()[0]
    print(f"  评委总数: {total_reviewers}人")
    
    # 2. 统计评审任务总数
    print("\n[2] 评审任务总数统计:")
    cur.execute("""
        SELECT 
            stage,
            COUNT(*) as task_count,
            COUNT(CASE WHEN status = 'SCORED' THEN 1 END) as completed_count
        FROM review_tasks
        GROUP BY stage
        ORDER BY stage
    """)
    tasks = cur.fetchall()
    total_tasks = 0
    for stage, task_count, completed_count in tasks:
        print(f"  {stage:10s}: {task_count:4d}任务 (已完成: {completed_count:4d})")
        total_tasks += task_count
    print(f"  {'总计':10s}: {total_tasks:4d}任务")
    
    # 3. 评委任务分布（详细）
    print("\n[3] 评委任务分布（按任务数量排序）:")
    cur.execute("""
        SELECT 
            u.id,
            u.name,
            u.title,
            u.expert_background,
            i.name as institution_name,
            COUNT(rt.id) as total_tasks,
            COUNT(CASE WHEN rt.stage = 'BOOK' THEN 1 END) as book_tasks,
            COUNT(CASE WHEN rt.stage = 'INTERVIEW' THEN 1 END) as interview_tasks,
            COUNT(CASE WHEN rt.status = 'SCORED' THEN 1 END) as completed_tasks,
            COUNT(CASE WHEN rt.status = 'PENDING' THEN 1 END) as pending_tasks
        FROM user_accounts u
        LEFT JOIN review_tasks rt ON u.id = rt.reviewer_id
        LEFT JOIN institutions i ON u.institution_id = i.id
        WHERE u.role = 'REVIEWER'
        GROUP BY u.id, u.name, u.title, u.expert_background, i.name
        ORDER BY total_tasks DESC, u.name
    """)
    
    reviewers = cur.fetchall()
    
    print(f"\n  {'ID':<4} | {'姓名':<10} | {'职称':<12} | {'专业背景':<15} | {'机构':<20} | {'总任务':<6} | {'书审':<4} | {'面谈':<4} | {'已完成':<6} | {'待评':<4}")
    print("  " + "-" * 98)
    
    task_counts = []
    for reviewer in reviewers:
        rid, name, title, bg, inst, total, book, interview, completed, pending = reviewer
        task_counts.append(total)
        print(f"  {rid:<4} | {name:<10} | {title or '':12s} | {bg or '':15s} | {inst or '':20s} | {total:6d} | {book:4d} | {interview:4d} | {completed:6d} | {pending:4d}")
    
    # 4. 统计分析
    print("\n[4] 统计分析:")
    if task_counts:
        avg_tasks = sum(task_counts) / len(task_counts)
        max_tasks = max(task_counts)
        min_tasks = min(task_counts)
        
        # 计算标准差
        variance = sum((x - avg_tasks) ** 2 for x in task_counts) / len(task_counts)
        std_dev = variance ** 0.5
        
        print(f"  平均任务数: {avg_tasks:.2f}任务/评委")
        print(f"  最大任务数: {max_tasks}任务")
        print(f"  最小任务数: {min_tasks}任务")
        print(f"  标准差: {std_dev:.2f}")
        
        # 负荷分布
        print("\n  负荷分布:")
        ranges = [(0, 5), (5, 10), (10, 15), (15, 20), (20, 100)]
        for low, high in ranges:
            count = sum(1 for x in task_counts if low <= x < high)
            if count > 0:
                print(f"    {low:2d}-{high:2d}任务: {count:3d}人 ({count/len(task_counts)*100:.1f}%)")
    
    # 5. 按专业背景统计
    print("\n[5] 按专业背景统计:")
    cur.execute("""
        SELECT 
            COALESCE(u.expert_background, '未设置') as background,
            COUNT(DISTINCT u.id) as reviewer_count,
            COUNT(rt.id) as total_tasks,
            ROUND(COUNT(rt.id)::numeric / NULLIF(COUNT(DISTINCT u.id), 0), 2) as avg_tasks
        FROM user_accounts u
        LEFT JOIN review_tasks rt ON u.id = rt.reviewer_id
        WHERE u.role = 'REVIEWER'
        GROUP BY u.expert_background
        ORDER BY total_tasks DESC
    """)
    
    backgrounds = cur.fetchall()
    print(f"\n  {'专业背景':<20} | {'评委数':<8} | {'总任务数':<10} | {'平均任务/评委'}")
    print("  " + "-" * 60)
    for bg, count, tasks, avg in backgrounds:
        print(f"  {bg:<20} | {count:8d} | {tasks:10d} | {avg:15.2f}")
    
    # 6. 按机构统计
    print("\n[6] 按机构统计（前10）:")
    cur.execute("""
        SELECT 
            COALESCE(i.name, '未设置') as institution,
            COUNT(DISTINCT u.id) as reviewer_count,
            COUNT(rt.id) as total_tasks,
            ROUND(COUNT(rt.id)::numeric / NULLIF(COUNT(DISTINCT u.id), 0), 2) as avg_tasks
        FROM user_accounts u
        LEFT JOIN institutions i ON u.institution_id = i.id
        LEFT JOIN review_tasks rt ON u.id = rt.reviewer_id
        WHERE u.role = 'REVIEWER'
        GROUP BY i.name
        ORDER BY total_tasks DESC
        LIMIT 10
    """)
    
    institutions = cur.fetchall()
    print(f"\n  {'机构':<30} | {'评委数':<8} | {'总任务数':<10} | {'平均任务/评委'}")
    print("  " + "-" * 70)
    for inst, count, tasks, avg in institutions:
        print(f"  {inst:<30} | {count:8d} | {tasks:10d} | {avg:15.2f}")
    
    # 7. 任务完成率
    print("\n[7] 任务完成率:")
    cur.execute("""
        SELECT 
            stage,
            COUNT(*) as total,
            COUNT(CASE WHEN status = 'SCORED' THEN 1 END) as completed,
            ROUND(COUNT(CASE WHEN status = 'SCORED' THEN 1 END)::numeric / COUNT(*) * 100, 2) as completion_rate
        FROM review_tasks
        GROUP BY stage
        ORDER BY stage
    """)
    
    completion = cur.fetchall()
    print(f"\n  {'阶段':<10} | {'总任务数':<10} | {'已完成':<10} | {'完成率'}")
    print("  " + "-" * 50)
    for stage, total, completed, rate in completion:
        print(f"  {stage:<10} | {total:10d} | {completed:10d} | {rate:9.2f}%")
    
    # 8. 负荷最高的评委（前10）
    print("\n[8] 负荷最高的评委（前10）:")
    cur.execute("""
        SELECT 
            u.name,
            u.title,
            u.expert_background,
            COUNT(rt.id) as total_tasks,
            COUNT(CASE WHEN rt.status = 'SCORED' THEN 1 END) as completed,
            COUNT(CASE WHEN rt.status = 'PENDING' THEN 1 END) as pending
        FROM user_accounts u
        JOIN review_tasks rt ON u.id = rt.reviewer_id
        WHERE u.role = 'REVIEWER'
        GROUP BY u.id, u.name, u.title, u.expert_background
        ORDER BY total_tasks DESC
        LIMIT 10
    """)
    
    top_reviewers = cur.fetchall()
    print(f"\n  {'姓名':<10} | {'职称':<12} | {'专业背景':<15} | {'总任务':<8} | {'已完成':<8} | {'待评':<6}")
    print("  " + "-" * 70)
    for name, title, bg, total, completed, pending in top_reviewers:
        print(f"  {name:<10} | {title or '':12s} | {bg or '':15s} | {total:8d} | {completed:8d} | {pending:6d}")
    
    # 9. 负荷最低的评委（前10）
    print("\n[9] 负荷最低的评委（前10）:")
    cur.execute("""
        SELECT 
            u.name,
            u.title,
            u.expert_background,
            COUNT(rt.id) as total_tasks
        FROM user_accounts u
        LEFT JOIN review_tasks rt ON u.id = rt.reviewer_id
        WHERE u.role = 'REVIEWER'
        GROUP BY u.id, u.name, u.title, u.expert_background
        ORDER BY total_tasks ASC, u.name
        LIMIT 10
    """)
    
    low_reviewers = cur.fetchall()
    print(f"\n  {'姓名':<10} | {'职称':<12} | {'专业背景':<15} | {'总任务':<8}")
    print("  " + "-" * 50)
    for name, title, bg, total in low_reviewers:
        print(f"  {name:<10} | {title or '':12s} | {bg or '':15s} | {total:8d}")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 100)
    print("分析完成")
    print("=" * 100)

if __name__ == '__main__':
    main()
