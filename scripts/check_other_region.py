#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查赛事21中地区为"其他"的数据"""

import pymysql

DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

def check_other_region():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        competition_id = 21
        
        print("=" * 100)
        print(f"检查赛事 {competition_id} 中的地区分布")
        print("=" * 100)
        
        # 1. 统计地区分布
        print("\n1. 地区分布统计:")
        print("-" * 100)
        cursor.execute("""
            SELECT 
                COALESCE(NULLIF(i.region, ''), '【空值】') as region_display,
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM registrations WHERE competition_id = %s), 2) as percentage
            FROM registrations r
            LEFT JOIN institutions i ON r.institution_id = i.id
            WHERE r.competition_id = %s
            GROUP BY i.region
            ORDER BY count DESC
        """, (competition_id, competition_id))
        
        regions = cursor.fetchall()
        total = sum(r[1] for r in regions)
        
        print(f"{'地区':<20} {'报名数':<10} {'占比':<10}")
        print("-" * 100)
        for region in regions:
            print(f"{region[0]:<20} {region[1]:<10} {region[2]:.2f}%")
        print("-" * 100)
        print(f"{'总计':<20} {total:<10} 100.00%")
        
        # 2. 检查是否有地区为空或特殊值的情况
        print("\n" + "=" * 100)
        print("2. 检查异常地区数据")
        print("=" * 100)
        
        cursor.execute("""
            SELECT 
                r.id as registration_id,
                r.project_name,
                i.id as institution_id,
                i.name as institution_name,
                i.region,
                i.code,
                r.group_type
            FROM registrations r
            LEFT JOIN institutions i ON r.institution_id = i.id
            WHERE r.competition_id = %s
            AND (i.region IS NULL OR i.region = '' OR i.region NOT IN (
                '杭州', '宁波', '温州', '绍兴', '嘉兴', '湖州', '金华', '衢州', '舟山', '台州', '丽水'
            ))
            ORDER BY r.id
        """, (competition_id,))
        
        abnormal_regions = cursor.fetchall()
        
        if abnormal_regions:
            print(f"\n⚠️  发现 {len(abnormal_regions)} 条异常地区数据:\n")
            
            for reg in abnormal_regions:
                print(f"报名ID: {reg[0]}")
                print(f"  项目名称: {reg[1]}")
                print(f"  机构ID: {reg[2]}")
                print(f"  机构名称: {reg[3]}")
                print(f"  地区: {reg[4] if reg[4] else '【空】'}")
                print(f"  机构代码: {reg[5]}")
                print(f"  组别: {reg[6]}")
                print()
        else:
            print("\n✅ 所有报名的地区都是浙江省11个地级市，没有异常数据")
        
        # 3. 详细列出所有报名的地区信息
        print("=" * 100)
        print("3. 所有报名的详细地区信息")
        print("=" * 100)
        
        cursor.execute("""
            SELECT 
                r.id,
                r.project_name,
                i.name as institution_name,
                i.region,
                r.group_type
            FROM registrations r
            LEFT JOIN institutions i ON r.institution_id = i.id
            WHERE r.competition_id = %s
            ORDER BY i.region, r.id
        """, (competition_id,))
        
        all_registrations = cursor.fetchall()
        
        print(f"\n{'报名ID':<10} {'项目名称':<40} {'机构名称':<40} {'地区':<15} {'组别':<15}")
        print("-" * 100)
        
        current_region = None
        for reg in all_registrations:
            if current_region != reg[3]:
                current_region = reg[3]
                print()
                print(f"--- {current_region} ---")
            
            project_name = reg[1][:38] + '...' if len(reg[1]) > 40 else reg[1]
            institution_name = reg[2][:38] + '...' if len(reg[2]) > 40 else reg[2]
            
            print(f"{reg[0]:<10} {project_name:<40} {institution_name:<40} {reg[3]:<15} {reg[4]:<15}")
        
        # 4. 检查机构表中是否有非标准地区名称
        print("\n" + "=" * 100)
        print("4. 检查机构表中的地区名称")
        print("=" * 100)
        
        cursor.execute("""
            SELECT DISTINCT region, COUNT(*) as count
            FROM institutions
            WHERE region IS NOT NULL AND region != ''
            GROUP BY region
            ORDER BY count DESC
        """)
        
        all_regions = cursor.fetchall()
        
        print(f"\n{'地区名称':<20} {'机构数':<10}")
        print("-" * 50)
        
        standard_regions = {'杭州', '宁波', '温州', '绍兴', '嘉兴', '湖州', '金华', '衢州', '舟山', '台州', '丽水'}
        
        for region in all_regions:
            marker = "" if region[0] in standard_regions else " ⚠️  非标准地区"
            print(f"{region[0]:<20} {region[1]:<10}{marker}")
                    
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    check_other_region()
