#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的数据库探索报告
"""

import mysql.connector
import json
from datetime import datetime

db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

def format_dt(dt):
    return dt.strftime('%Y-%m-%d %H:%M:%S') if isinstance(dt, datetime) else (str(dt) if dt else 'N/A')

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    report = {
        "database": db_config['database'],
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "summary": {},
        "competitions": [],
        "users_by_role": {},
        "registrations_by_status": {},
        "registrations_by_group": {},
        "review_tasks_by_stage": {},
        "dictionaries": {}
    }
    
    print("=" * 100)
    print(f"数据库探索报告: {db_config['database']}")
    print(f"生成时间: {report['timestamp']}")
    print("=" * 100)
    
    # 统计总数
    tables = ['institutions', 'competitions', 'user_accounts', 'registrations', 
              'review_tasks', 'review_scores', 'dictionary_items', 'activity_infos']
    
    print("\n【数据总览】")
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            count = cursor.fetchone()['count']
            report['summary'][table] = count
            print(f"  {table:20s}: {count:4d} 条")
        except:
            report['summary'][table] = 0
            print(f"  {table:20s}:    0 条 (表不存在或为空)")
    
    # 赛事详情
    print("\n" + "=" * 100)
    print("【赛事列表】")
    cursor.execute("SELECT * FROM competitions ORDER BY id")
    competitions = cursor.fetchall()
    for comp in competitions:
        report['competitions'].append({
            'id': comp['id'],
            'name': comp['name'],
            'stage': comp.get('stage'),
            'created_at': format_dt(comp.get('created_at'))
        })
        print(f"\n  赛事 ID={comp['id']}")
        print(f"  名称: {comp['name']}")
        print(f"  阶段: {comp.get('stage', 'N/A')}")
        print(f"  创建时间: {format_dt(comp.get('created_at'))}")
        if comp.get('description'):
            print(f"  描述: {comp['description']}")
        
        # 该赛事的报名统计
        cursor.execute(f"SELECT COUNT(*) as count FROM registrations WHERE competition_id = {comp['id']}")
        reg_count = cursor.fetchone()['count']
        print(f"  报名数: {reg_count}")
    
    # 用户按角色
    print("\n" + "=" * 100)
    print("【用户统计】")
    cursor.execute("SELECT role, COUNT(*) as count FROM user_accounts GROUP BY role ORDER BY role")
    for row in cursor.fetchall():
        report['users_by_role'][row['role']] = row['count']
        print(f"  {row['role']:20s}: {row['count']:3d} 人")
    
    # 显示部分用户示例
    print("\n  各角色用户示例:")
    for role in report['users_by_role'].keys():
        cursor.execute(f"SELECT id, name, phone, institution_id FROM user_accounts WHERE role = '{role}' LIMIT 3")
        users = cursor.fetchall()
        for u in users:
            inst_info = f"机构ID={u.get('institution_id')}" if u.get('institution_id') else "无机构"
            print(f"    {role:15s} | ID={u['id']:3d} | {u['name']:20s} | {u['phone']:15s} | {inst_info}")
    
    # 报名统计
    print("\n" + "=" * 100)
    print("【报名统计】")
    
    cursor.execute("SELECT status, COUNT(*) as count FROM registrations GROUP BY status")
    for row in cursor.fetchall():
        report['registrations_by_status'][row['status']] = row['count']
        print(f"  状态 {row['status']:15s}: {row['count']:3d} 个")
    
    cursor.execute("""
        SELECT group_type, group_code, COUNT(*) as count 
        FROM registrations 
        WHERE group_type IS NOT NULL 
        GROUP BY group_type, group_code 
        ORDER BY group_type, group_code
    """)
    print("\n  按组别分布:")
    for row in cursor.fetchall():
        gt = row['group_type'] if row['group_type'] else 'NULL'
        gc = row['group_code'] if row['group_code'] else 'NULL'
        key = f"{gt}-{gc}"
        report['registrations_by_group'][key] = row['count']
        print(f"    {gt:15s} - {gc:5s}: {row['count']:3d} 个")
    
    # 报名项目示例
    print("\n  报名项目示例 (前15个):")
    cursor.execute("""
        SELECT r.id, r.project_name, r.group_type, r.group_code, r.status,
               i.name as inst_name, u.name as applicant_name, r.competition_id
        FROM registrations r
        LEFT JOIN institutions i ON r.institution_id = i.id
        LEFT JOIN user_accounts u ON r.applicant_id = u.id
        ORDER BY r.id
        LIMIT 15
    """)
    for row in cursor.fetchall():
        gt = row.get('group_type', 'N/A')
        gc = row.get('group_code', 'N/A')
        print(f"    ID={row['id']:3d} | 赛事={row['competition_id']:2d} | {row['project_name']:35s} | {gt:12s}-{gc:5s} | {row['status']:10s} | {row.get('inst_name', 'N/A')[:20]}")
    
    # 评审任务统计
    print("\n" + "=" * 100)
    print("【评审任务统计】")
    cursor.execute("SELECT stage, status, COUNT(*) as count FROM review_tasks GROUP BY stage, status ORDER BY stage, status")
    tasks_stats = cursor.fetchall()
    if tasks_stats:
        for row in tasks_stats:
            stage = row['stage'] if row['stage'] else 'NULL'
            status = row.get('status', 'NULL') if row.get('status') else 'NULL'
            key = f"{stage}-{status}"
            report['review_tasks_by_stage'][key] = row['count']
            print(f"  {stage:15s} | {status:15s}: {row['count']:3d} 个")
    else:
        print("  暂无评审任务")
    
    # 评分统计
    print("\n" + "=" * 100)
    print("【评分统计】")
    cursor.execute("SELECT COUNT(*) as count FROM review_scores")
    score_count = cursor.fetchone()['count']
    print(f"  总评分数: {score_count}")
    
    if score_count > 0:
        cursor.execute("SELECT AVG(total) as avg_total, MIN(total) as min_total, MAX(total) as max_total FROM review_scores WHERE total IS NOT NULL")
        stats = cursor.fetchone()
        if stats['avg_total']:
            print(f"  平均分: {stats['avg_total']:.2f}")
            print(f"  最低分: {stats['min_total']}")
            print(f"  最高分: {stats['max_total']}")
    
    # 字典统计
    print("\n" + "=" * 100)
    print("【字典配置】")
    cursor.execute("SELECT type, COUNT(*) as count FROM dictionary_items WHERE active = TRUE GROUP BY type ORDER BY type")
    for row in cursor.fetchall():
        report['dictionaries'][row['type']] = row['count']
        print(f"  {row['type']:30s}: {row['count']:3d} 项")
    
    # 机构信息
    print("\n" + "=" * 100)
    print("【机构信息】(前20个)")
    cursor.execute("SELECT id, name, code, uscc FROM institutions ORDER BY id LIMIT 20")
    for row in cursor.fetchall():
        print(f"  ID={row['id']:3d} | {row['name']:40s} | code={row.get('code', 'N/A'):15s}")
    
    print("\n" + "=" * 100)
    print("报告生成完成")
    print("=" * 100)
    
    # 保存报告
    with open('data/exports/database_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("\n详细报告已保存到: data/exports/database_report.json")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n错误: {e}")
    import traceback
    traceback.print_exc()
