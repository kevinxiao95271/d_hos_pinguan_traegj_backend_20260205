#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查评委职称数据"""

import pymysql
import json

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'Mysql@2024',
    'database': 'pinguan_db',
    'charset': 'utf8mb4'
}

def check_reviewer_titles():
    """检查评委职称"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        print("=" * 100)
        print("检查评委职称数据")
        print("=" * 100)
        
        # 查询所有评委
        sql = """
        SELECT 
            id,
            name,
            phone,
            title,
            role,
            institution_id
        FROM user_accounts
        WHERE role = 'REVIEWER'
        ORDER BY id
        """
        
        cursor.execute(sql)
        reviewers = cursor.fetchall()
        
        print(f"\n总评委数: {len(reviewers)}\n")
        
        # 统计职称分布
        title_counts = {}
        for reviewer in reviewers:
            title = reviewer['title'] or '空值'
            title_counts[title] = title_counts.get(title, 0) + 1
        
        print("职称分布统计:")
        print(f"{'职称':<30} {'数量':<10} {'占比':<10}")
        print("-" * 60)
        
        for title, count in sorted(title_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(reviewers) * 100) if len(reviewers) > 0 else 0
            print(f"{title:<30} {count:<10} {percentage:>6.2f}%")
        
        print("-" * 60)
        print(f"{'总计':<30} {len(reviewers):<10} 100.00%")
        
        # 显示所有评委的详细信息
        print("\n" + "=" * 100)
        print("所有评委详细信息")
        print("=" * 100)
        
        print(f"\n{'ID':<5} {'姓名':<15} {'手机号':<15} {'职称':<30} {'机构ID':<10}")
        print("-" * 100)
        
        for reviewer in reviewers:
            print(f"{reviewer['id']:<5} {reviewer['name']:<15} {reviewer['phone']:<15} "
                  f"{reviewer['title'] or '(空)':<30} {reviewer['institution_id'] or '(空)':<10}")
        
        # 检查是否所有评委都是 "Test Title"
        test_title_count = sum(1 for r in reviewers if r['title'] == 'Test Title')
        
        print("\n" + "=" * 100)
        print("问题分析")
        print("=" * 100)
        
        if test_title_count == len(reviewers):
            print(f"\n⚠️  所有 {len(reviewers)} 个评委的职称都是 'Test Title'")
            print("这是测试数据，需要更新为真实的职称信息。")
        elif test_title_count > 0:
            print(f"\n⚠️  有 {test_title_count} 个评委的职称是 'Test Title' ({test_title_count/len(reviewers)*100:.1f}%)")
            print("部分评委使用了测试数据。")
        else:
            print(f"\n✅ 没有评委使用 'Test Title'")
        
        # 检查空值
        null_title_count = sum(1 for r in reviewers if not r['title'])
        if null_title_count > 0:
            print(f"\n⚠️  有 {null_title_count} 个评委的职称为空 ({null_title_count/len(reviewers)*100:.1f}%)")
        
        # 查询已分配任务中的评委
        print("\n" + "=" * 100)
        print("已分配任务中的评委职称")
        print("=" * 100)
        
        sql = """
        SELECT DISTINCT
            u.id,
            u.name,
            u.title,
            COUNT(rt.id) as task_count
        FROM review_tasks rt
        JOIN user_accounts u ON rt.reviewer_id = u.id
        WHERE rt.registration_id IN (
            SELECT id FROM registrations WHERE competition_id = 21
        )
        GROUP BY u.id, u.name, u.title
        ORDER BY task_count DESC
        """
        
        cursor.execute(sql)
        assigned_reviewers = cursor.fetchall()
        
        print(f"\n已分配任务的评委数: {len(assigned_reviewers)}\n")
        
        print(f"{'评委ID':<10} {'姓名':<15} {'职称':<30} {'任务数':<10}")
        print("-" * 80)
        
        for reviewer in assigned_reviewers:
            print(f"{reviewer['id']:<10} {reviewer['name']:<15} "
                  f"{reviewer['title'] or '(空)':<30} {reviewer['task_count']:<10}")
        
        # 检查已分配任务的评委职称
        assigned_test_title = sum(1 for r in assigned_reviewers if r['title'] == 'Test Title')
        
        print("\n" + "=" * 100)
        print("已分配任务评委职称分析")
        print("=" * 100)
        
        if assigned_test_title == len(assigned_reviewers):
            print(f"\n⚠️  所有 {len(assigned_reviewers)} 个已分配任务的评委职称都是 'Test Title'")
            print("这是测试数据，需要更新为真实的职称信息。")
        elif assigned_test_title > 0:
            print(f"\n⚠️  有 {assigned_test_title} 个已分配任务的评委职称是 'Test Title' "
                  f"({assigned_test_title/len(assigned_reviewers)*100:.1f}%)")
        
        # 建议的职称列表
        print("\n" + "=" * 100)
        print("建议的职称列表")
        print("=" * 100)
        
        suggested_titles = [
            "主任医师",
            "副主任医师",
            "主治医师",
            "主任护师",
            "副主任护师",
            "主管护师",
            "教授",
            "副教授",
            "讲师",
            "研究员",
            "副研究员",
            "助理研究员"
        ]
        
        print("\n医疗系统常用职称:")
        for i, title in enumerate(suggested_titles, 1):
            print(f"  {i}. {title}")
        
        print("\n" + "=" * 100)
        print("修复建议")
        print("=" * 100)
        
        print("""
1. 如果这是测试环境，可以保持 'Test Title'
2. 如果这是生产环境，需要更新为真实职称：
   
   方法1: 手动更新（适合少量数据）
   UPDATE user_accounts 
   SET title = '主任医师' 
   WHERE id = 6;
   
   方法2: 批量更新（适合大量数据）
   - 准备一个CSV文件，包含 id 和 title
   - 使用脚本批量更新
   
   方法3: 从其他表导入
   - 如果有其他表包含职称信息，可以关联更新
""")
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    check_reviewer_titles()
