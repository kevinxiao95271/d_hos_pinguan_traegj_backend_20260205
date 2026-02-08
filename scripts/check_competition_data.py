#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查赛事和报名数据"""

import pymysql

DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

def check_data():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 查看所有赛事
        print("=== 赛事列表 ===")
        cursor.execute("SELECT id, name, stage FROM competitions ORDER BY id")
        competitions = cursor.fetchall()
        
        if competitions:
            for comp in competitions:
                print(f"  ID: {comp[0]}, 名称: {comp[1]}, 阶段: {comp[2]}")
        else:
            print("  没有赛事数据")
        
        print()
        
        # 查看报名数据统计
        print("=== 报名数据统计 ===")
        cursor.execute("""
            SELECT 
                r.competition_id,
                c.name as competition_name,
                COUNT(*) as registration_count
            FROM registrations r
            LEFT JOIN competitions c ON r.competition_id = c.id
            GROUP BY r.competition_id, c.name
            ORDER BY r.competition_id
        """)
        stats = cursor.fetchall()
        
        if stats:
            for stat in stats:
                print(f"  赛事ID {stat[0]} ({stat[1]}): {stat[2]} 条报名")
        else:
            print("  没有报名数据")
        
        print()
        
        # 查看报名数据样例（如果有的话）
        print("=== 报名数据样例 ===")
        cursor.execute("""
            SELECT 
                r.id,
                r.project_name,
                i.name as institution_name,
                i.level as institution_level,
                r.group_type,
                r.group_code
            FROM registrations r
            LEFT JOIN institutions i ON r.institution_id = i.id
            LIMIT 5
        """)
        samples = cursor.fetchall()
        
        if samples:
            for sample in samples:
                print(f"  ID: {sample[0]}")
                print(f"    项目: {sample[1]}")
                print(f"    机构: {sample[2]}")
                print(f"    机构等级: {sample[3]}")
                print(f"    组别: {sample[4]}")
                print(f"    分组: {sample[5]}")
                print()
        else:
            print("  没有报名数据")
        
        # 检查机构表中是否有 level 字段
        print("=== 机构表结构 ===")
        cursor.execute("SHOW COLUMNS FROM institutions LIKE 'level'")
        level_column = cursor.fetchone()
        
        if level_column:
            print(f"  ✅ institutions 表有 level 字段")
            print(f"     字段类型: {level_column[1]}")
            
            # 统计有多少机构有等级数据
            cursor.execute("SELECT COUNT(*) FROM institutions WHERE level IS NOT NULL AND level != ''")
            count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM institutions")
            total = cursor.fetchone()[0]
            print(f"     {count}/{total} 个机构有等级数据")
        else:
            print(f"  ❌ institutions 表没有 level 字段")
                    
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    check_data()
