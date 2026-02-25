# -*- coding: utf-8 -*-
"""
分析地区数据分布情况
"""
import pymysql
import os

# 数据库配置
DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

def analyze_regions():
    """分析地区数据"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("地区数据分析")
    print("=" * 80)
    
    # 1. 总机构数
    cursor.execute("SELECT COUNT(*) FROM institutions")
    total = cursor.fetchone()[0]
    print(f"\n总机构数: {total:,}")
    
    # 2. 热门地区TOP 20
    print("\n【热门地区TOP 20】")
    cursor.execute("""
        SELECT region, COUNT(*) as cnt 
        FROM institutions 
        WHERE region IS NOT NULL 
        GROUP BY region 
        ORDER BY cnt DESC 
        LIMIT 20
    """)
    top_regions = cursor.fetchall()
    for i, (region, cnt) in enumerate(top_regions, 1):
        pct = (cnt / total) * 100
        print(f"{i:2d}. {region:20s} {cnt:6,} 家 ({pct:5.2f}%)")
    
    # 3. 统计地区粒度
    print("\n【地区粒度分析】")
    cursor.execute("""
        SELECT region FROM institutions WHERE region IS NOT NULL GROUP BY region
    """)
    all_regions = [r[0] for r in cursor.fetchall()]
    
    # 分类统计
    province_level = [r for r in all_regions if r.endswith('省') or r.endswith('市') and len(r) <= 4]
    city_level = [r for r in all_regions if r.endswith('市') and len(r) > 2 and len(r) <= 4]
    district_level = [r for r in all_regions if r.endswith('区') or r.endswith('县')]
    other = [r for r in all_regions if r not in province_level + city_level + district_level]
    
    print(f"省级（如浙江省）: {len(province_level)} 个")
    print(f"市级（如杭州市）: {len(city_level)} 个")
    print(f"区县级（如上城区）: {len(district_level)} 个")
    print(f"其他: {len(other)} 个")
    print(f"总计: {len(all_regions)} 个地区")
    
    # 4. 搜索"杭州"相关
    print("\n【杭州相关机构统计】")
    
    # 4.1 精确匹配"杭州市"
    cursor.execute("SELECT COUNT(*) FROM institutions WHERE region = '杭州市'")
    hangzhou_exact = cursor.fetchone()[0]
    print(f"region = '杭州市': {hangzhou_exact:,} 家")
    
    # 4.2 包含"杭州"
    cursor.execute("SELECT COUNT(*) FROM institutions WHERE region LIKE '%杭州%'")
    hangzhou_like = cursor.fetchone()[0]
    print(f"region LIKE '%杭州%': {hangzhou_like:,} 家")
    
    # 4.3 杭州各区县
    cursor.execute("""
        SELECT region, COUNT(*) as cnt 
        FROM institutions 
        WHERE region IN (
            '上城区', '下城区', '江干区', '拱墅区', '西湖区', '滨江区',
            '萧山区', '余杭区', '富阳区', '临安区', '桐庐县', '淳安县', '建德市'
        )
        GROUP BY region 
        ORDER BY cnt DESC
    """)
    hangzhou_districts = cursor.fetchall()
    print(f"\n杭州各区县分布:")
    hangzhou_total = 0
    for region, cnt in hangzhou_districts:
        hangzhou_total += cnt
        pct = (cnt / total) * 100
        print(f"  {region:10s} {cnt:6,} 家 ({pct:5.2f}%)")
    print(f"  {'合计':10s} {hangzhou_total:6,} 家 ({(hangzhou_total/total)*100:5.2f}%)")
    
    # 5. 名称中包含"杭州"的机构
    print("\n【机构名称包含'杭州'的统计】")
    cursor.execute("SELECT COUNT(*) FROM institutions WHERE name LIKE '%杭州%'")
    name_hangzhou = cursor.fetchone()[0]
    print(f"name LIKE '%杭州%': {name_hangzhou:,} 家")
    
    # 5.1 抽样显示几条
    cursor.execute("""
        SELECT name, region 
        FROM institutions 
        WHERE name LIKE '%杭州%' 
        LIMIT 10
    """)
    sample = cursor.fetchall()
    print(f"\n抽样显示（前10条）:")
    for name, region in sample:
        print(f"  {name[:40]:40s} -> 地区: {region}")
    
    # 6. 区县级地区TOP 10
    print("\n【区县级地区TOP 10】")
    district_regions = [r for r in top_regions if r[0].endswith('区') or r[0].endswith('县')][:10]
    for i, (region, cnt) in enumerate(district_regions, 1):
        pct = (cnt / total) * 100
        print(f"{i:2d}. {region:20s} {cnt:6,} 家 ({pct:5.2f}%)")
    
    # 7. 建议的解决方案
    print("\n" + "=" * 80)
    print("问题分析与建议")
    print("=" * 80)
    
    print("\n【问题】")
    print("1. 地区粒度不统一：同时存在省级、市级、区县级")
    print("2. 搜索'杭州市'返回0，但实际有大量杭州的机构")
    print("3. 热门地区显示的是区县级，用户体验不好")
    
    print("\n【建议方案】")
    print("方案1: 保持原数据，增强搜索功能")
    print("  - 搜索'杭州'时自动匹配所有杭州区县")
    print("  - 地区筛选器使用两级：市 -> 区县")
    print(f"  - 杭州影响范围: ~{hangzhou_total:,}家 ({(hangzhou_total/total)*100:.1f}%)")
    
    print("\n方案2: 数据规整 - 区县归并到市")
    print("  - 将区县级统一改为市级（如'上城区'->'杭州市'）")
    print("  - 优点: 搜索简单，用户体验好")
    print(f"  - 缺点: 损失区县粒度信息")
    
    print("\n方案3: 增加城市字段（推荐）")
    print("  - 保留原region字段（区县级）")
    print("  - 新增city字段（市级）")
    print("  - 优点: 保留详细信息，支持多层级查询")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    try:
        analyze_regions()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
