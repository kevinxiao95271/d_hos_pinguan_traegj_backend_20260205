#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接查询数据库检查数据情况
"""

import pymysql

# 数据库配置
DB_CONFIG = {
    'host': '1.94.176.95',
    'user': 'wjx',
    'password': 'kevinxiao',
    'database': 'pinguan_db',
    'charset': 'utf8mb4',
    'port': 3306
}

def check_competitions():
    """检查竞赛数据"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    print("=" * 80)
    print("检查竞赛数据")
    print("=" * 80)
    
    cursor.execute("SELECT id, name, year, status FROM competitions ORDER BY id")
    competitions = cursor.fetchall()
    
    for comp in competitions:
        print(f"ID: {comp['id']}, Name: {comp['name']}, Year: {comp['year']}, Status: {comp['status']}")
    
    cursor.close()
    conn.close()
    
    return competitions

def check_registrations(competition_id):
    """检查指定竞赛的报名数据"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    print(f"\n" + "=" * 80)
    print(f"检查竞赛ID={competition_id}的报名数据")
    print("=" * 80)
    
    sql = """
    SELECT r.id, r.project_name, i.name as institution_name, r.group_type, r.group_code,
           a.method_code, a.subject_type_code
    FROM registrations r
    LEFT JOIN institutions i ON r.institution_id = i.id
    LEFT JOIN activity_infos a ON a.registration_id = r.id
    WHERE r.competition_id = %s
    LIMIT 10
    """
    
    cursor.execute(sql, (competition_id,))
    registrations = cursor.fetchall()
    
    print(f"查询到 {len(registrations)} 条报名记录（最多显示10条）")
    
    for reg in registrations:
        print(f"\nID: {reg['id']}")
        print(f"  项目: {reg['project_name']}")
        print(f"  机构: {reg['institution_name']}")
        print(f"  组别: {reg['group_type']}")
        print(f"  分组: {reg['group_code']}")
        print(f"  methodCode: {reg['method_code']}")
        print(f"  subjectTypeCode: {reg['subject_type_code']}")
    
    cursor.close()
    conn.close()
    
    return len(registrations)

def check_dictionary_items():
    """检查字典项"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    print(f"\n" + "=" * 80)
    print("检查字典项")
    print("=" * 80)
    
    # 检查method相关的字典项
    cursor.execute("""
        SELECT code, label, category FROM dictionary_items 
        WHERE category = 'METHOD' OR category = 'SUBJECT_TYPE'
        ORDER BY category, code
    """)
    items = cursor.fetchall()
    
    print(f"\n找到 {len(items)} 个字典项")
    
    current_category = None
    for item in items:
        if item['category'] != current_category:
            current_category = item['category']
            print(f"\n{current_category}:")
        print(f"  {item['code']} -> {item['label']}")
    
    cursor.close()
    conn.close()

def main():
    # 检查竞赛
    competitions = check_competitions()
    
    if competitions:
        # 检查第一个竞赛的报名数据
        comp_id = competitions[0]['id']
        reg_count = check_registrations(comp_id)
        
        if reg_count > 0:
            # 检查字典项
            check_dictionary_items()

if __name__ == "__main__":
    main()
