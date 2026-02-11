#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
评审任务数据库测试
直接查询数据库验证评审任务数据
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'pinguan_new',
    'user': 'postgres',
    'password': 'postgres'
}

def get_connection():
    """获取数据库连接"""
    return psycopg2.connect(**DB_CONFIG)

def test_review_tasks_data():
    """测试评审任务数据"""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print(f"\n{'='*80}")
        print(f"评审任务数据测试")
        print(f"{'='*80}")
        
        # 1. 统计各环节任务数量
        print(f"\n1. 各环节任务统计:")
        cursor.execute("""
            SELECT 
                stage,
                status,
                COUNT(*) as count
            FROM review_tasks
            GROUP BY stage, status
            ORDER BY stage, status
        """)
        
        stats = cursor.fetchall()
        if stats:
            print(f"\n{'环节':<15} {'状态':<15} {'数量':<10}")
            print(f"{'-'*40}")
            for row in stats:
                stage_name = {
                    'BOOK': '书审',
                    'INTERVIEW': '面谈',
                    'FINAL': '终审'
                }.get(row['stage'], row['stage'])
                
                status_name = {
                    'PENDING': '待确认',
                    'CONFIRMED': '已确认',
                    'SCORED': '已评分',
                    'RETURNED': '已退回'
                }.get(row['status'], row['status'])
                
                print(f"{stage_name:<15} {status_name:<15} {row['count']:<10}")
        else:
            print("  暂无任务数据")
        
        # 2. 书审环节任务详情（前5条）
        print(f"\n2. 书审环节任务详情（前5条）:")
        cursor.execute("""
            SELECT 
                rt.id,
                rt.stage,
                rt.status,
                rt.created_at,
                r.id as registration_id,
                r.project_name,
                i.name as institution_name,
                r.group_type,
                r.group_code,
                u.id as reviewer_id,
                u.real_name as reviewer_name,
                u.title as reviewer_title,
                u.institution_name as reviewer_institution_name,
                u.expert_background
            FROM review_tasks rt
            LEFT JOIN registrations r ON rt.registration_id = r.id
            LEFT JOIN institutions i ON r.institution_id = i.id
            LEFT JOIN user_accounts u ON rt.reviewer_id = u.id
            WHERE rt.stage = 'BOOK'
            ORDER BY rt.created_at DESC
            LIMIT 5
        """)
        
        book_tasks = cursor.fetchall()
        if book_tasks:
            for idx, task in enumerate(book_tasks, 1):
                print(f"\n  [{idx}] 任务ID: {task['id']}")
                print(f"      项目: {task['project_name']}")
                print(f"      机构: {task['institution_name']}")
                print(f"      组别: {task['group_type']} - {task['group_code']}")
                print(f"      评委: {task['reviewer_name']} ({task['reviewer_title']})")
                print(f"      评委机构: {task['reviewer_institution_name']}")
                print(f"      专业背景: {task['expert_background']}")
                print(f"      状态: {task['status']}")
                print(f"      创建时间: {task['created_at']}")
        else:
            print("  暂无书审任务")
        
        # 3. 面谈环节任务详情（前5条）
        print(f"\n3. 面谈环节任务详情（前5条）:")
        cursor.execute("""
            SELECT 
                rt.id,
                rt.stage,
                rt.status,
                rt.created_at,
                r.id as registration_id,
                r.project_name,
                i.name as institution_name,
                r.group_type,
                r.group_code,
                u.id as reviewer_id,
                u.real_name as reviewer_name,
                u.title as reviewer_title,
                u.institution_name as reviewer_institution_name,
                u.expert_background
            FROM review_tasks rt
            LEFT JOIN registrations r ON rt.registration_id = r.id
            LEFT JOIN institutions i ON r.institution_id = i.id
            LEFT JOIN user_accounts u ON rt.reviewer_id = u.id
            WHERE rt.stage = 'INTERVIEW'
            ORDER BY rt.created_at DESC
            LIMIT 5
        """)
        
        interview_tasks = cursor.fetchall()
        if interview_tasks:
            for idx, task in enumerate(interview_tasks, 1):
                print(f"\n  [{idx}] 任务ID: {task['id']}")
                print(f"      项目: {task['project_name']}")
                print(f"      机构: {task['institution_name']}")
                print(f"      组别: {task['group_type']} - {task['group_code']}")
                print(f"      评委: {task['reviewer_name']} ({task['reviewer_title']})")
                print(f"      评委机构: {task['reviewer_institution_name']}")
                print(f"      专业背景: {task['expert_background']}")
                print(f"      状态: {task['status']}")
                print(f"      创建时间: {task['created_at']}")
        else:
            print("  暂无面谈任务")
        
        # 4. 按评委统计任务分布
        print(f"\n4. 评委任务分布（前10名）:")
        cursor.execute("""
            SELECT 
                u.real_name as reviewer_name,
                u.title as reviewer_title,
                u.expert_background,
                COUNT(CASE WHEN rt.stage = 'BOOK' THEN 1 END) as book_count,
                COUNT(CASE WHEN rt.stage = 'INTERVIEW' THEN 1 END) as interview_count,
                COUNT(*) as total_count
            FROM review_tasks rt
            LEFT JOIN user_accounts u ON rt.reviewer_id = u.id
            GROUP BY u.id, u.real_name, u.title, u.expert_background
            ORDER BY total_count DESC
            LIMIT 10
        """)
        
        reviewer_stats = cursor.fetchall()
        if reviewer_stats:
            print(f"\n{'评委':<20} {'职称':<15} {'专业背景':<20} {'书审':<8} {'面谈':<8} {'总计':<8}")
            print(f"{'-'*90}")
            for row in reviewer_stats:
                print(f"{row['reviewer_name']:<20} {row['reviewer_title'] or '':<15} "
                      f"{row['expert_background'] or '':<20} {row['book_count']:<8} "
                      f"{row['interview_count']:<8} {row['total_count']:<8}")
        else:
            print("  暂无数据")
        
        # 5. 按组别统计任务分布
        print(f"\n5. 组别任务分布:")
        cursor.execute("""
            SELECT 
                r.group_type,
                r.group_code,
                COUNT(CASE WHEN rt.stage = 'BOOK' THEN 1 END) as book_count,
                COUNT(CASE WHEN rt.stage = 'INTERVIEW' THEN 1 END) as interview_count,
                COUNT(*) as total_count
            FROM review_tasks rt
            LEFT JOIN registrations r ON rt.registration_id = r.id
            GROUP BY r.group_type, r.group_code
            ORDER BY r.group_type, r.group_code
        """)
        
        group_stats = cursor.fetchall()
        if group_stats:
            print(f"\n{'组别类型':<15} {'组别代码':<10} {'书审':<8} {'面谈':<8} {'总计':<8}")
            print(f"{'-'*60}")
            for row in group_stats:
                group_type_name = {
                    'BASIC': '基层组',
                    'COMPREHENSIVE': '综合组',
                    'ADVANCED': '进阶组'
                }.get(row['group_type'], row['group_type'])
                
                print(f"{group_type_name:<15} {row['group_code'] or '':<10} "
                      f"{row['book_count']:<8} {row['interview_count']:<8} {row['total_count']:<8}")
        else:
            print("  暂无数据")
        
        # 6. 验证API返回字段的数据完整性
        print(f"\n6. 数据完整性检查:")
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(rt.registration_id) as has_registration,
                COUNT(r.project_name) as has_project_name,
                COUNT(i.name) as has_institution_name,
                COUNT(r.group_type) as has_group_type,
                COUNT(r.group_code) as has_group_code,
                COUNT(rt.reviewer_id) as has_reviewer,
                COUNT(u.real_name) as has_reviewer_name,
                COUNT(u.title) as has_reviewer_title,
                COUNT(u.institution_name) as has_reviewer_institution,
                COUNT(u.expert_background) as has_expert_background
            FROM review_tasks rt
            LEFT JOIN registrations r ON rt.registration_id = r.id
            LEFT JOIN institutions i ON r.institution_id = i.id
            LEFT JOIN user_accounts u ON rt.reviewer_id = u.id
        """)
        
        integrity = cursor.fetchone()
        if integrity:
            total = integrity['total']
            print(f"\n  总任务数: {total}")
            if total > 0:
                print(f"  关联报名: {integrity['has_registration']} ({integrity['has_registration']*100/total:.1f}%)")
                print(f"  项目名称: {integrity['has_project_name']} ({integrity['has_project_name']*100/total:.1f}%)")
                print(f"  机构名称: {integrity['has_institution_name']} ({integrity['has_institution_name']*100/total:.1f}%)")
                print(f"  组别类型: {integrity['has_group_type']} ({integrity['has_group_type']*100/total:.1f}%)")
                print(f"  组别代码: {integrity['has_group_code']} ({integrity['has_group_code']*100/total:.1f}%)")
                print(f"  关联评委: {integrity['has_reviewer']} ({integrity['has_reviewer']*100/total:.1f}%)")
                print(f"  评委姓名: {integrity['has_reviewer_name']} ({integrity['has_reviewer_name']*100/total:.1f}%)")
                print(f"  评委职称: {integrity['has_reviewer_title']} ({integrity['has_reviewer_title']*100/total:.1f}%)")
                print(f"  评委机构: {integrity['has_reviewer_institution']} ({integrity['has_reviewer_institution']*100/total:.1f}%)")
                print(f"  专业背景: {integrity['has_expert_background']} ({integrity['has_expert_background']*100/total:.1f}%)")
        
        print(f"\n{'='*80}")
        print(f"测试完成")
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"\n✗ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

def main():
    test_review_tasks_data()

if __name__ == "__main__":
    main()
