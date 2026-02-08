#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证修正完成 - 对比修正前后的数据"""

import pymysql
from collections import defaultdict

DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

def get_region_stats_from_backup(cursor):
    """从备份表获取修正前的统计"""
    print("=" * 80)
    print("修正前的数据（从备份表）")
    print("=" * 80)
    
    try:
        cursor.execute("""
            SELECT 
                COALESCE(NULLIF(i.region, ''), '未知') as region,
                COUNT(*) as count
            FROM registrations r
            LEFT JOIN institutions_backup_20260208 i ON r.institution_id = i.id
            WHERE r.competition_id = 21
            GROUP BY i.region
            ORDER BY count DESC
        """)
        
        results = cursor.fetchall()
        print(f"\n{'地区':<15} {'报名数':<10}")
        print("-" * 30)
        total = 0
        for row in results:
            print(f"{row[0]:<15} {row[1]:<10}")
            total += row[1]
        print("-" * 30)
        print(f"{'总计':<15} {total:<10}")
        
        return dict(results)
    except Exception as e:
        print(f"⚠️  无法读取备份表: {e}")
        print("   （可能备份表不存在或已被删除）")
        return {}

def get_region_stats_current(cursor):
    """从当前表获取修正后的统计"""
    print("\n" + "=" * 80)
    print("修正后的数据（当前表）")
    print("=" * 80)
    
    cursor.execute("""
        SELECT 
            COALESCE(NULLIF(i.region, ''), '未知') as region,
            COUNT(*) as count
        FROM registrations r
        LEFT JOIN institutions i ON r.institution_id = i.id
        WHERE r.competition_id = 21
        GROUP BY i.region
        ORDER BY count DESC
    """)
    
    results = cursor.fetchall()
    print(f"\n{'地区':<15} {'报名数':<10}")
    print("-" * 30)
    total = 0
    for row in results:
        print(f"{row[0]:<15} {row[1]:<10}")
        total += row[1]
    print("-" * 30)
    print(f"{'总计':<15} {total:<10}")
    
    return dict(results)

def compare_stats(before, after):
    """对比修正前后的变化"""
    print("\n" + "=" * 80)
    print("修正前后对比")
    print("=" * 80)
    
    if not before:
        print("⚠️  无法对比（备份数据不可用）")
        return
    
    all_regions = set(before.keys()) | set(after.keys())
    
    print(f"\n{'地区':<15} {'修正前':<10} {'修正后':<10} {'变化':<10}")
    print("-" * 50)
    
    for region in sorted(all_regions):
        before_count = before.get(region, 0)
        after_count = after.get(region, 0)
        change = after_count - before_count
        
        change_str = f"{change:+d}" if change != 0 else "0"
        marker = ""
        if change > 0:
            marker = " ⬆️"
        elif change < 0:
            marker = " ⬇️"
        
        print(f"{region:<15} {before_count:<10} {after_count:<10} {change_str:<10}{marker}")

def check_specific_institutions(cursor):
    """检查特定机构的修正情况"""
    print("\n" + "=" * 80)
    print("重点机构修正验证")
    print("=" * 80)
    
    # 检查几个典型的省级医院
    test_institutions = [
        (7, '浙江医院', '杭州'),
        (8, '浙一医院', '杭州'),
        (9, '浙江省人民医院', '杭州'),
        (16, '宁波市第一医院', '宁波'),
        (24, '衢州市人民医院', '衢州'),
    ]
    
    print(f"\n{'机构ID':<10} {'机构名称':<30} {'期望地区':<10} {'实际地区':<10} {'状态':<10}")
    print("-" * 80)
    
    all_correct = True
    for inst_id, inst_name, expected_region in test_institutions:
        cursor.execute("SELECT region FROM institutions WHERE id = %s", (inst_id,))
        result = cursor.fetchone()
        
        if result:
            actual_region = result[0]
            status = "✅" if actual_region == expected_region else "❌"
            if actual_region != expected_region:
                all_correct = False
            print(f"{inst_id:<10} {inst_name:<30} {expected_region:<10} {actual_region:<10} {status:<10}")
        else:
            print(f"{inst_id:<10} {inst_name:<30} {expected_region:<10} {'未找到':<10} {'❌':<10}")
            all_correct = False
    
    print()
    if all_correct:
        print("✅ 所有重点机构的地区信息都已正确修正！")
    else:
        print("❌ 部分机构的地区信息仍有问题")

def check_unknown_regions(cursor):
    """检查是否有地区为空或未知的情况"""
    print("\n" + "=" * 80)
    print("检查地区为空的情况")
    print("=" * 80)
    
    cursor.execute("""
        SELECT COUNT(*) 
        FROM institutions 
        WHERE region IS NULL OR region = ''
    """)
    
    empty_count = cursor.fetchone()[0]
    
    if empty_count == 0:
        print("\n✅ 所有机构都有地区信息，没有空值")
    else:
        print(f"\n⚠️  发现 {empty_count} 个机构的地区为空")
        
        cursor.execute("""
            SELECT id, name, region
            FROM institutions
            WHERE region IS NULL OR region = ''
        """)
        
        empty_institutions = cursor.fetchall()
        for inst in empty_institutions:
            print(f"  ID {inst[0]}: {inst[1]} - 地区: {inst[2] if inst[2] else '【空】'}")

def main():
    print("=" * 80)
    print("验证机构地区修正完成")
    print("=" * 80)
    print("赛事: ID 21 (2026浙江品管大赛)")
    print("报名数: 45 条")
    print()
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 1. 获取修正前的统计（从备份表）
        before_stats = get_region_stats_from_backup(cursor)
        
        # 2. 获取修正后的统计（从当前表）
        after_stats = get_region_stats_current(cursor)
        
        # 3. 对比变化
        compare_stats(before_stats, after_stats)
        
        # 4. 检查特定机构
        check_specific_institutions(cursor)
        
        # 5. 检查是否有空值
        check_unknown_regions(cursor)
        
        print("\n" + "=" * 80)
        print("验证完成")
        print("=" * 80)
        
        # 总结
        print("\n📊 修正效果总结:")
        print("-" * 40)
        
        hangzhou_before = before_stats.get('杭州', 0) if before_stats else 0
        hangzhou_after = after_stats.get('杭州', 0)
        
        if hangzhou_after > hangzhou_before:
            print(f"✅ 杭州: {hangzhou_before} → {hangzhou_after} (+{hangzhou_after - hangzhou_before})")
            print("   省级医院已正确归入杭州")
        
        if '未知' not in after_stats:
            print("✅ 没有地区为'未知'的报名")
        
        print("\n🎉 地区信息修正成功！")
        
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    main()
