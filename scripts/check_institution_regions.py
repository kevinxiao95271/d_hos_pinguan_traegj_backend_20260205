#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查机构地区信息"""

import pymysql

DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

def check_regions():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 1. 统计机构地区情况
        print("=" * 80)
        print("机构地区信息统计")
        print("=" * 80)
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN region IS NULL OR region = '' THEN 1 ELSE 0 END) as empty_region,
                SUM(CASE WHEN region IS NOT NULL AND region != '' THEN 1 ELSE 0 END) as has_region
            FROM institutions
        """)
        stats = cursor.fetchone()
        print(f"总机构数: {stats[0]}")
        print(f"地区为空: {stats[1]}")
        print(f"有地区信息: {stats[2]}")
        print()
        
        # 2. 查看地区分布
        print("=" * 80)
        print("地区分布")
        print("=" * 80)
        cursor.execute("""
            SELECT 
                COALESCE(NULLIF(region, ''), '【空值】') as region_display,
                COUNT(*) as count
            FROM institutions
            GROUP BY region
            ORDER BY count DESC
        """)
        regions = cursor.fetchall()
        for region in regions:
            print(f"  {region[0]}: {region[1]} 个机构")
        print()
        
        # 3. 查看地区为空的机构详情
        print("=" * 80)
        print("地区为空的机构列表")
        print("=" * 80)
        cursor.execute("""
            SELECT id, name, code, region
            FROM institutions
            WHERE region IS NULL OR region = ''
            ORDER BY id
        """)
        empty_regions = cursor.fetchall()
        
        if empty_regions:
            print(f"共 {len(empty_regions)} 个机构地区为空：\n")
            for inst in empty_regions:
                print(f"  ID: {inst[0]}")
                print(f"  名称: {inst[1]}")
                print(f"  代码: {inst[2]}")
                print(f"  地区: {inst[3] if inst[3] else '【空】'}")
                print()
        else:
            print("所有机构都有地区信息")
        
        # 4. 检查报名统计中的地区分布
        print("=" * 80)
        print("报名数据中的地区分布（最新赛事）")
        print("=" * 80)
        
        # 获取最新赛事ID
        cursor.execute("SELECT MAX(id) FROM competitions")
        latest_competition_id = cursor.fetchone()[0]
        print(f"最新赛事ID: {latest_competition_id}\n")
        
        cursor.execute("""
            SELECT 
                COALESCE(NULLIF(i.region, ''), '【空值/其他】') as region_display,
                COUNT(*) as registration_count,
                GROUP_CONCAT(DISTINCT i.name SEPARATOR '; ') as institutions
            FROM registrations r
            LEFT JOIN institutions i ON r.institution_id = i.id
            WHERE r.competition_id = %s
            GROUP BY i.region
            ORDER BY registration_count DESC
        """, (latest_competition_id,))
        
        registration_regions = cursor.fetchall()
        for region in registration_regions:
            print(f"地区: {region[0]}")
            print(f"  报名数: {region[1]}")
            print(f"  机构: {region[2][:200]}{'...' if len(region[2]) > 200 else ''}")
            print()
        
        # 5. 列出地区为空的报名详情
        print("=" * 80)
        print("地区为空的报名详情")
        print("=" * 80)
        cursor.execute("""
            SELECT 
                r.id as registration_id,
                r.project_name,
                i.id as institution_id,
                i.name as institution_name,
                i.region
            FROM registrations r
            LEFT JOIN institutions i ON r.institution_id = i.id
            WHERE r.competition_id = %s
            AND (i.region IS NULL OR i.region = '')
            ORDER BY r.id
        """, (latest_competition_id,))
        
        empty_region_registrations = cursor.fetchall()
        if empty_region_registrations:
            print(f"共 {len(empty_region_registrations)} 条报名的机构地区为空：\n")
            for reg in empty_region_registrations:
                print(f"  报名ID: {reg[0]}")
                print(f"  项目名称: {reg[1]}")
                print(f"  机构ID: {reg[2]}")
                print(f"  机构名称: {reg[3]}")
                print(f"  地区: {reg[4] if reg[4] else '【空】'}")
                print()
        else:
            print("✅ 所有报名的机构都有地区信息")
                    
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    check_regions()
