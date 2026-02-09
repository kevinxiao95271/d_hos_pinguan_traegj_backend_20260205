#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
探索数据库中的现有数据
"""

import mysql.connector
import json
from datetime import datetime

# 数据库连接配置
db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

def format_datetime(dt):
    if dt:
        return dt.strftime('%Y-%m-%d %H:%M:%S') if isinstance(dt, datetime) else str(dt)
    return None

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    print("=" * 80)
    print("数据库探索报告")
    print("=" * 80)
    
    # 1. 查看所有表
    cursor.execute("SHOW TABLES")
    tables = [row[list(row.keys())[0]] for row in cursor.fetchall()]
    print(f"\n数据库中的表 ({len(tables)} 个):")
    for table in tables:
        print(f"  - {table}")
    
    # 2. 机构数据
    print("\n" + "=" * 80)
    print("机构数据 (Institution)")
    print("=" * 80)
    cursor.execute("SELECT COUNT(*) as count FROM institution")
    inst_count = cursor.fetchone()['count']
    print(f"总数: {inst_count}")
    
    if inst_count > 0:
        cursor.execute("SELECT id, name, code, uscc, region FROM institution ORDER BY id LIMIT 10")
        institutions = cursor.fetchall()
        print("\n前10个机构:")
        for inst in institutions:
            print(f"  ID={inst['id']:3d} | {inst['name']:30s} | 代码={inst.get('code', 'N/A'):15s} | USCC={inst.get('uscc', 'N/A'):20s} | 地区={inst.get('region', 'N/A')}")
    
    # 3. 赛事数据
    print("\n" + "=" * 80)
    print("赛事数据 (Competition)")
    print("=" * 80)
    cursor.execute("SELECT COUNT(*) as count FROM competition")
    comp_count = cursor.fetchone()['count']
    print(f"总数: {comp_count}")
    
    if comp_count > 0:
        cursor.execute("SELECT id, name, stage, description, created_at FROM competition ORDER BY id")
        competitions = cursor.fetchall()
        print("\n所有赛事:")
        for comp in competitions:
            print(f"  ID={comp['id']:3d} | {comp['name']:40s} | 阶段={comp.get('stage', 'N/A'):15s} | 创建时间={format_datetime(comp.get('created_at'))}")
            if comp.get('description'):
                print(f"       描述: {comp['description']}")
    
    # 4. 用户数据
    print("\n" + "=" * 80)
    print("用户数据 (User Account)")
    print("=" * 80)
    cursor.execute("SELECT COUNT(*) as count FROM user_account")
    user_count = cursor.fetchone()['count']
    print(f"总数: {user_count}")
    
    cursor.execute("SELECT role, COUNT(*) as count FROM user_account GROUP BY role")
    role_stats = cursor.fetchall()
    print("\n按角色统计:")
    for stat in role_stats:
        print(f"  {stat['role']:15s}: {stat['count']:3d} 人")
    
    # 查看各角色示例
    cursor.execute("""
        SELECT id, phone, name, title, role, institution_id, 
               reviewer_group_code, interview_group_code, expert_background
        FROM user_account 
        ORDER BY role, id 
        LIMIT 15
    """)
    users = cursor.fetchall()
    print("\n前15个用户示例:")
    for user in users:
        inst_info = f"机构ID={user.get('institution_id')}" if user.get('institution_id') else "无机构"
        reviewer_info = f"评审组={user.get('reviewer_group_code', 'N/A')}" if user.get('reviewer_group_code') else ""
        print(f"  ID={user['id']:3d} | {user['role']:12s} | {user['name']:15s} | {user['phone']:15s} | {inst_info:15s} | {reviewer_info}")
    
    # 5. 报名数据
    print("\n" + "=" * 80)
    print("报名数据 (Registration)")
    print("=" * 80)
    cursor.execute("SELECT COUNT(*) as count FROM registration")
    reg_count = cursor.fetchone()['count']
    print(f"总数: {reg_count}")
    
    if reg_count > 0:
        cursor.execute("""
            SELECT status, COUNT(*) as count 
            FROM registration 
            GROUP BY status
        """)
        status_stats = cursor.fetchall()
        print("\n按状态统计:")
        for stat in status_stats:
            print(f"  {stat['status']:15s}: {stat['count']:3d} 个")
        
        cursor.execute("""
            SELECT group_type, COUNT(*) as count 
            FROM registration 
            WHERE group_type IS NOT NULL
            GROUP BY group_type
        """)
        group_stats = cursor.fetchall()
        print("\n按组别统计:")
        for stat in group_stats:
            print(f"  {stat['group_type']:15s}: {stat['count']:3d} 个")
        
        cursor.execute("""
            SELECT r.id, r.project_name, r.group_type, r.group_code, r.status,
                   i.name as institution_name, u.name as applicant_name
            FROM registration r
            LEFT JOIN institution i ON r.institution_id = i.id
            LEFT JOIN user_account u ON r.applicant_id = u.id
            ORDER BY r.id
            LIMIT 10
        """)
        registrations = cursor.fetchall()
        print("\n前10个报名项目:")
        for reg in registrations:
            print(f"  ID={reg['id']:3d} | {reg['project_name']:30s} | {reg.get('group_type', 'N/A'):12s}-{reg.get('group_code', 'N/A'):5s} | {reg['status']:10s} | {reg.get('institution_name', 'N/A'):20s}")
    
    # 6. 评审任务数据
    print("\n" + "=" * 80)
    print("评审任务数据 (Review Task)")
    print("=" * 80)
    cursor.execute("SELECT COUNT(*) as count FROM review_task")
    task_count = cursor.fetchone()['count']
    print(f"总数: {task_count}")
    
    if task_count > 0:
        cursor.execute("""
            SELECT stage, status, COUNT(*) as count 
            FROM review_task 
            GROUP BY stage, status
            ORDER BY stage, status
        """)
        task_stats = cursor.fetchall()
        print("\n按阶段和状态统计:")
        for stat in task_stats:
            print(f"  {stat['stage']:15s} | {stat.get('status', 'N/A'):15s}: {stat['count']:3d} 个")
        
        cursor.execute("""
            SELECT rt.id, rt.stage, rt.status, 
                   r.project_name, u.name as reviewer_name
            FROM review_task rt
            LEFT JOIN registration r ON rt.registration_id = r.id
            LEFT JOIN user_account u ON rt.reviewer_id = u.id
            ORDER BY rt.id
            LIMIT 10
        """)
        tasks = cursor.fetchall()
        print("\n前10个评审任务:")
        for task in tasks:
            print(f"  任务ID={task['id']:3d} | {task['stage']:12s} | {task.get('status', 'N/A'):12s} | 项目={task.get('project_name', 'N/A'):25s} | 评审={task.get('reviewer_name', 'N/A')}")
    
    # 7. 评分数据
    print("\n" + "=" * 80)
    print("评分数据 (Review Score)")
    print("=" * 80)
    cursor.execute("SELECT COUNT(*) as count FROM review_score")
    score_count = cursor.fetchone()['count']
    print(f"总数: {score_count}")
    
    if score_count > 0:
        cursor.execute("""
            SELECT rs.id, rs.total, rs.highlight, rt.stage,
                   r.project_name
            FROM review_score rs
            LEFT JOIN review_task rt ON rs.review_task_id = rt.id
            LEFT JOIN registration r ON rt.registration_id = r.id
            ORDER BY rs.id
            LIMIT 10
        """)
        scores = cursor.fetchall()
        print("\n前10个评分:")
        for score in scores:
            highlight = score.get('highlight', '')[:30] if score.get('highlight') else 'N/A'
            print(f"  评分ID={score['id']:3d} | {score.get('stage', 'N/A'):12s} | 总分={score.get('total', 0):3d} | 项目={score.get('project_name', 'N/A'):25s} | 亮点={highlight}")
    
    # 8. 字典数据
    print("\n" + "=" * 80)
    print("字典数据 (Dictionary Item)")
    print("=" * 80)
    cursor.execute("SELECT COUNT(*) as count FROM dictionary_item")
    dict_count = cursor.fetchone()['count']
    print(f"总数: {dict_count}")
    
    if dict_count > 0:
        cursor.execute("""
            SELECT type, COUNT(*) as count 
            FROM dictionary_item 
            WHERE active = TRUE
            GROUP BY type
            ORDER BY type
        """)
        dict_stats = cursor.fetchall()
        print("\n按类型统计(仅活跃):")
        for stat in dict_stats:
            print(f"  {stat['type']:30s}: {stat['count']:3d} 项")
    
    # 9. 活动信息
    print("\n" + "=" * 80)
    print("活动信息 (Activity Info)")
    print("=" * 80)
    cursor.execute("SELECT COUNT(*) as count FROM activity_info")
    activity_count = cursor.fetchone()['count']
    print(f"总数: {activity_count}")
    
    if activity_count > 0:
        cursor.execute("""
            SELECT method_code, COUNT(*) as count 
            FROM activity_info 
            WHERE method_code IS NOT NULL
            GROUP BY method_code
            ORDER BY count DESC
        """)
        method_stats = cursor.fetchall()
        print("\n按品管工具统计:")
        for stat in method_stats[:10]:
            print(f"  {stat['method_code']:30s}: {stat['count']:3d} 个项目")
    
    print("\n" + "=" * 80)
    print("探索完成")
    print("=" * 80)
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n数据库连接或查询失败: {e}")
    import traceback
    traceback.print_exc()
