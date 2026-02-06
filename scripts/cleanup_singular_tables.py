#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理单数形式的表（避免冲突）
"""

import mysql.connector

db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

# 要删除的单数表
singular_tables = [
    'institution',
    'user_account',
    'competition',
    'registration',
    'registration_member',
    'activity_info',
    'project_summary',
    'material_file',
    'review_task',
    'review_score',
    'dictionary_item',
    'system_setting',
    'competition_template',
    'activity_template',
    'institution_update_request'
]

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    print("开始清理单数表...")
    
    # 先禁用外键检查
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    
    for table in singular_tables:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS `{table}`")
            print(f"  删除表: {table}")
        except Exception as e:
            print(f"  删除表 {table} 失败: {e}")
    
    # 恢复外键检查
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    
    conn.commit()
    print("\n清理完成！")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"数据库操作失败: {e}")
