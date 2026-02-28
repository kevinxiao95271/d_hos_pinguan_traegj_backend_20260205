#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
执行系统模版表建表 SQL
"""

import pymysql
from pathlib import Path

# 数据库配置
DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

def main():
    print("=" * 60)
    print("执行系统模版表建表 SQL")
    print("=" * 60)
    
    # 读取 SQL 文件
    sql_file = Path(__file__).parent / 'create_system_template_table.sql'
    if not sql_file.exists():
        print(f"错误: SQL 文件不存在 {sql_file}")
        return
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # 连接数据库
    print("\n连接数据库...")
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 检查表是否已存在
        cursor.execute("SHOW TABLES LIKE 'system_template_files'")
        if cursor.fetchone():
            print("\n警告: 表 system_template_files 已存在")
            response = input("是否删除并重建? (yes/no): ")
            if response.lower() == 'yes':
                print("删除旧表...")
                cursor.execute("DROP TABLE system_template_files")
                conn.commit()
            else:
                print("跳过建表")
                return
        
        # 执行建表 SQL
        print("\n执行建表 SQL...")
        
        # 移除注释行，只保留 CREATE TABLE 语句
        sql_lines = [line for line in sql_content.split('\n') 
                     if line.strip() and not line.strip().startswith('--')]
        clean_sql = '\n'.join(sql_lines)
        
        cursor.execute(clean_sql)
        conn.commit()
        print("建表成功！")
        
        # 验证表结构
        print("\n验证表结构...")
        cursor.execute("DESC system_template_files")
        columns = cursor.fetchall()
        
        print(f"\n表 system_template_files 字段列表（共 {len(columns)} 个）:")
        for col in columns:
            print(f"  {col[0]:<20} {col[1]:<20} {col[2]:<10} {col[3]:<10}")
        
    except Exception as e:
        conn.rollback()
        print(f"\n错误: {e}")
    finally:
        cursor.close()
        conn.close()
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)

if __name__ == '__main__':
    main()
