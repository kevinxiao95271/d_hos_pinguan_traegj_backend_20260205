#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查评审专家数据
"""

import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import mysql.connector

db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    print("评审专家列表:")
    print("="*80)
    
    cursor.execute("""
        SELECT id, phone, name, title, institution_id, 
               reviewer_group_code, interview_group_code, expert_background
        FROM user_accounts 
        WHERE role = 'REVIEWER'
        ORDER BY id
    """)
    
    reviewers = cursor.fetchall()
    
    if len(reviewers) == 0:
        print("没有找到评审专家")
    else:
        print(f"共找到 {len(reviewers)} 个评审专家:\n")
        for r in reviewers:
            reviewer_group = r.get('reviewer_group_code') or 'N/A'
            interview_group = r.get('interview_group_code') or 'N/A'
            background = r.get('expert_background') or 'N/A'
            print(f"ID={r['id']:3d} | 手机: {r['phone']:15s} | 姓名: {r['name']:20s} | "
                  f"评审组: {reviewer_group:5s} | 面谈组: {interview_group:5s} | 背景: {background}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
