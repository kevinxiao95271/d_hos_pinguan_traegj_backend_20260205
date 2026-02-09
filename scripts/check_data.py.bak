#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库中的现有数据
"""

import mysql.connector
import json

# 数据库连接配置
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
    
    # 检查机构数量
    cursor.execute("SELECT COUNT(*) as count FROM institution")
    inst_count = cursor.fetchone()
    print(f"机构总数: {inst_count['count']}")
    
    # 查看前10个机构
    cursor.execute("SELECT id, name, code, uscc FROM institution LIMIT 10")
    institutions = cursor.fetchall()
    print("\n前10个机构:")
    for inst in institutions:
        print(f"  ID={inst['id']}, 名称={inst['name']}, 代码={inst.get('code', 'N/A')}")
    
    # 检查字典数量
    cursor.execute("SELECT type, COUNT(*) as count FROM dictionary_item GROUP BY type")
    dict_counts = cursor.fetchall()
    print("\n字典配置:")
    for dc in dict_counts:
        print(f"  {dc['type']}: {dc['count']} 项")
    
    # 检查用户数量
    cursor.execute("SELECT COUNT(*) as count FROM user_account")
    user_count = cursor.fetchone()
    print(f"\n用户总数: {user_count['count']}")
    
    # 检查赛事数量
    cursor.execute("SELECT COUNT(*) as count FROM competition")
    comp_count = cursor.fetchone()
    print(f"赛事总数: {comp_count['count']}")
    
    # 检查报名数量
    cursor.execute("SELECT COUNT(*) as count FROM registration")
    reg_count = cursor.fetchone()
    print(f"报名总数: {reg_count['count']}")
    
    cursor.close()
    conn.close()
    
    print("\n数据库检查完成")
    
except Exception as e:
    print(f"数据库连接失败: {e}")
