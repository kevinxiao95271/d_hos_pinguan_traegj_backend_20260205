#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查赛事21的统计数据"""

import pymysql
from db_config import DB_CONFIG
from collections import defaultdict

# DB_CONFIG imported from db_config.py

def check_competition_21():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        competition_id = 21
        
        print("=" * 80)
        print(f"赛事 {competition_id} 的统计分析")
        print("=" * 80)
        
        # 1. 获取赛事信息
        cursor.execute("SELECT id, name, stage FROM competitions WHERE id = %s", (competition_id,))
        competition = cursor.fetchone()
        print(f"\n赛事信息:")
        print(f"  ID: {competition[0]}")
        print(f"  名称: {competition[1]}")
        print(f"  阶段: {competition[2]}")
        
        # 2. 统计报名数据
        cursor.execute("""
            SELECT COUNT(*) FROM registrations WHERE competition_id = %s
        """, (competition_id,))
        total_registrations = cursor.fetchone()[0]
        print(f"\n报名总数: {total_registrations}")
        
        # 3. 按地区统计（模拟后端逻辑）
        print(f"\n地区分布（模拟后端逻辑）:")
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
            ORDER BY r.id
        """, (competition_id,))
        
        registrations = cursor.fetchall()
        region_counts = defaultdict(int)
        
        for reg in registrations:
            region = reg[4]  # i.region
            
            # 模拟后端逻辑：如果 region 为 null 或空字符串，设置为"未知"
            if region is None or region.strip() == '':
                region = "未知"
            
            region_counts[region] += 1
        
        print(f"  统计结果:")
        for region, count in sorted(region_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"    {region}: {count} 条报名")
        
        # 4. 检查是否有地区为空的情况
        print(f"\n地区为空的报名:")
        empty_region_count = 0
        for reg in registrations:
            region = reg[4]
            if region is None or region.strip() == '':
                empty_region_count += 1
                print(f"  报名ID: {reg[0]}, 项目: {reg[1]}, 机构: {reg[3]}, 地区: {region}")
        
        if empty_region_count == 0:
            print(f"  ✅ 所有报名都有地区信息")
        else:
            print(f"  ⚠️  共 {empty_region_count} 条报名地区为空")
        
        # 5. 详细的地区分布
        print(f"\n详细地区分布:")
        cursor.execute("""
            SELECT 
                COALESCE(NULLIF(i.region, ''), '【空值】') as region_display,
                COUNT(*) as count,
                GROUP_CONCAT(r.id ORDER BY r.id SEPARATOR ', ') as registration_ids
            FROM registrations r
            LEFT JOIN institutions i ON r.institution_id = i.id
            WHERE r.competition_id = %s
            GROUP BY i.region
            ORDER BY count DESC
        """, (competition_id,))
        
        detailed_regions = cursor.fetchall()
        for region in detailed_regions:
            print(f"  {region[0]}: {region[1]} 条报名")
            print(f"    报名ID: {region[2]}")
        
        # 6. 检查机构表中的地区信息
        print(f"\n机构地区信息检查:")
        cursor.execute("""
            SELECT DISTINCT i.id, i.name, i.region
            FROM registrations r
            LEFT JOIN institutions i ON r.institution_id = i.id
            WHERE r.competition_id = %s
            ORDER BY i.id
        """, (competition_id,))
        
        institutions = cursor.fetchall()
        print(f"  涉及 {len(institutions)} 个机构:")
        for inst in institutions:
            region_display = inst[2] if inst[2] else "【空】"
            print(f"    机构ID {inst[0]}: {inst[1]} - 地区: {region_display}")
                    
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    check_competition_21()
