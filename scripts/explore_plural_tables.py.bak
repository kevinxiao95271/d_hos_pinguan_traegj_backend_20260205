#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
探索复数形式的表
"""

import mysql.connector
from datetime import datetime

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
    print("数据库探索报告 (复数表)")
    print("=" * 80)
    
    # 1. 机构数据
    print("\n机构数据 (institutions)")
    cursor.execute("SELECT COUNT(*) as count FROM institutions")
    count = cursor.fetchone()['count']
    print(f"总数: {count}")
    
    if count > 0:
        cursor.execute("SELECT id, name, code, uscc FROM institutions ORDER BY id LIMIT 5")
        for row in cursor.fetchall():
            print(f"  ID={row['id']:3d} | {row['name']:40s} | code={row.get('code', 'N/A')}")
    
    # 2. 赛事数据
    print("\n赛事数据 (competitions)")
    cursor.execute("SELECT COUNT(*) as count FROM competitions")
    count = cursor.fetchone()['count']
    print(f"总数: {count}")
    
    if count > 0:
        cursor.execute("SELECT id, name, stage FROM competitions ORDER BY id")
        for row in cursor.fetchall():
            print(f"  ID={row['id']:3d} | {row['name']:50s} | stage={row.get('stage', 'N/A')}")
    
    # 3. 用户数据
    print("\n用户数据 (user_accounts)")
    cursor.execute("SELECT COUNT(*) as count FROM user_accounts")
    count = cursor.fetchone()['count']
    print(f"总数: {count}")
    
    if count > 0:
        cursor.execute("SELECT role, COUNT(*) as count FROM user_accounts GROUP BY role")
        print("\n按角色统计:")
        for row in cursor.fetchall():
            print(f"  {row['role']:15s}: {row['count']:3d} 人")
        
        cursor.execute("SELECT id, phone, name, role, institution_id FROM user_accounts ORDER BY id LIMIT 10")
        print("\n前10个用户:")
        for row in cursor.fetchall():
            print(f"  ID={row['id']:3d} | {row['role']:12s} | {row['name']:20s} | phone={row['phone']}")
    
    # 4. 报名数据
    print("\n报名数据 (registrations)")
    cursor.execute("SELECT COUNT(*) as count FROM registrations")
    count = cursor.fetchone()['count']
    print(f"总数: {count}")
    
    if count > 0:
        cursor.execute("SELECT status, COUNT(*) as count FROM registrations GROUP BY status")
        print("\n按状态统计:")
        for row in cursor.fetchall():
            print(f"  {row['status']:15s}: {row['count']:3d} 个")
        
        cursor.execute("SELECT group_type, group_code, COUNT(*) as count FROM registrations WHERE group_type IS NOT NULL GROUP BY group_type, group_code ORDER BY group_type, group_code")
        print("\n按组别统计:")
        for row in cursor.fetchall():
            print(f"  {row['group_type']:15s} - {row.get('group_code', 'N/A'):5s}: {row['count']:3d} 个")
        
        cursor.execute("""
            SELECT r.id, r.project_name, r.group_type, r.group_code, r.status, r.competition_id
            FROM registrations r
            ORDER BY r.id
            LIMIT 10
        """)
        print("\n前10个报名:")
        for row in cursor.fetchall():
            print(f"  ID={row['id']:3d} | 赛事={row['competition_id']:3d} | {row['project_name']:35s} | {row.get('group_type', 'N/A'):12s}-{row.get('group_code', 'N/A'):5s} | {row['status']}")
    
    # 5. 评审任务
    print("\n评审任务数据 (review_tasks)")
    cursor.execute("SELECT COUNT(*) as count FROM review_tasks")
    count = cursor.fetchone()['count']
    print(f"总数: {count}")
    
    if count > 0:
        cursor.execute("SELECT stage, status, COUNT(*) as count FROM review_tasks GROUP BY stage, status ORDER BY stage, status")
        print("\n按阶段和状态统计:")
        for row in cursor.fetchall():
            print(f"  {row['stage']:15s} | {row.get('status', 'N/A'):15s}: {row['count']:3d} 个")
    
    # 6. 评分数据
    print("\n评分数据 (review_scores)")
    cursor.execute("SELECT COUNT(*) as count FROM review_scores")
    count = cursor.fetchone()['count']
    print(f"总数: {count}")
    
    # 7. 字典数据
    print("\n字典数据 (dictionary_items)")
    cursor.execute("SELECT COUNT(*) as count FROM dictionary_items")
    count = cursor.fetchone()['count']
    print(f"总数: {count}")
    
    if count > 0:
        cursor.execute("SELECT type, COUNT(*) as count FROM dictionary_items WHERE active = TRUE GROUP BY type ORDER BY type")
        print("\n按类型统计:")
        for row in cursor.fetchall():
            print(f"  {row['type']:30s}: {row['count']:3d} 项")
    
    # 8. 活动信息
    print("\n活动信息 (activity_infos)")
    cursor.execute("SELECT COUNT(*) as count FROM activity_infos")
    count = cursor.fetchone()['count']
    print(f"总数: {count}")
    
    print("\n" + "=" * 80)
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n错误: {e}")
    import traceback
    traceback.print_exc()
