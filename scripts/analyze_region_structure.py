# -*- coding: utf-8 -*-
"""
详细分析region字段的实际数据结构
"""
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

def analyze_region_structure():
    """详细分析region字段"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("region字段详细分析")
    print("=" * 80)
    
    # 1. 获取所有唯一的region值及其数量
    cursor.execute("""
        SELECT region, COUNT(*) as cnt 
        FROM institutions 
        WHERE region IS NOT NULL AND region != ''
        GROUP BY region 
        ORDER BY cnt DESC
    """)
    all_regions = cursor.fetchall()
    
    print(f"\n总计 {len(all_regions)} 个不同的region值\n")
    
    # 2. 按后缀分类
    by_suffix = defaultdict(list)
    for region, cnt in all_regions:
        if region.endswith('市'):
            by_suffix['市'].append((region, cnt))
        elif region.endswith('区'):
            by_suffix['区'].append((region, cnt))
        elif region.endswith('县'):
            by_suffix['县'].append((region, cnt))
        elif region.endswith('省'):
            by_suffix['省'].append((region, cnt))
        else:
            by_suffix['其他'].append((region, cnt))
    
    print("【按后缀分类统计】")
    print("-" * 80)
    for suffix, items in sorted(by_suffix.items()):
        total_count = sum(cnt for _, cnt in items)
        print(f"\n{suffix}后缀: {len(items)} 个地区, 共 {total_count:,} 家机构")
        print(f"  前10个:")
        for region, cnt in items[:10]:
            print(f"    {region:20s} {cnt:6,} 家")
        if len(items) > 10:
            print(f"    ... 还有 {len(items)-10} 个")
    
    # 3. 特别分析"市"后缀的
    print("\n" + "=" * 80)
    print("【详细分析'市'后缀】")
    print("=" * 80)
    
    city_regions = by_suffix['市']
    
    # 检查是否有地级市
    prefectural_cities = []
    county_cities = []
    
    for region, cnt in city_regions:
        # 简单判断：字数<=3且常见的是地级市，>3或特定的是县级市
        # 浙江11个地级市: 杭州市、宁波市、温州市、嘉兴市、湖州市、绍兴市、金华市、衢州市、舟山市、台州市、丽水市
        known_prefectural = ['杭州市', '宁波市', '温州市', '嘉兴市', '湖州市', '绍兴市', 
                            '金华市', '衢州市', '舟山市', '台州市', '丽水市']
        
        if region in known_prefectural:
            prefectural_cities.append((region, cnt))
        else:
            county_cities.append((region, cnt))
    
    print(f"\n地级市（已知11个）:")
    for region, cnt in prefectural_cities:
        print(f"  {region:15s} {cnt:6,} 家")
    
    print(f"\n县级市（实际数据中的）:")
    for region, cnt in county_cities[:20]:
        print(f"  {region:15s} {cnt:6,} 家")
    if len(county_cities) > 20:
        print(f"  ... 还有 {len(county_cities)-20} 个")
    
    # 4. 检查义乌市、乐清市等县级市的归属
    print("\n" + "=" * 80)
    print("【检查热门县级市】")
    print("=" * 80)
    
    hot_county_cities = ['义乌市', '乐清市', '瑞安市', '慈溪市', '余姚市', '诸暨市', '温岭市', '东阳市', '永康市']
    
    for city in hot_county_cities:
        cursor.execute("SELECT COUNT(*) FROM institutions WHERE region = %s", (city,))
        cnt = cursor.fetchone()[0]
        
        # 检查该市的机构名称，看是否包含上级市名
        cursor.execute("""
            SELECT name FROM institutions 
            WHERE region = %s 
            LIMIT 10
        """, (city,))
        samples = [row[0] for row in cursor.fetchall()]
        
        # 分析名称中包含的上级市关键词
        parent_hints = defaultdict(int)
        for name in samples:
            if '金华' in name:
                parent_hints['金华市'] += 1
            elif '温州' in name:
                parent_hints['温州市'] += 1
            elif '宁波' in name:
                parent_hints['宁波市'] += 1
            elif '绍兴' in name:
                parent_hints['绍兴市'] += 1
            elif '台州' in name:
                parent_hints['台州市'] += 1
        
        likely_parent = max(parent_hints.items(), key=lambda x: x[1])[0] if parent_hints else '未知'
        
        print(f"\n{city:10s} {cnt:6,} 家  (可能属于: {likely_parent})")
        print(f"  样本机构名称:")
        for name in samples[:3]:
            print(f"    {name[:50]}")
    
    # 5. 关键发现
    print("\n" + "=" * 80)
    print("【关键发现】")
    print("=" * 80)
    
    print("\n1. region字段的实际值:")
    print(f"   - '区'后缀: {len(by_suffix['区'])} 个 (如: 上城区, 萧山区)")
    print(f"   - '县'后缀: {len(by_suffix['县'])} 个 (如: 桐庐县, 淳安县)")
    print(f"   - '市'后缀: {len(by_suffix['市'])} 个")
    print(f"     * 地级市: {len(prefectural_cities)} 个 (杭州市, 宁波市等)")
    print(f"     * 县级市: {len(county_cities)} 个 (义乌市, 乐清市等)")
    
    print("\n2. 层级关系:")
    print("   - 数据库中没有明确的层级关系字段")
    print("   - region字段混合存储了区、县、县级市")
    print("   - 地级市（如杭州市）在region中很少或没有")
    
    print("\n3. 搜索'杭州市'返回0的原因:")
    cursor.execute("SELECT COUNT(*) FROM institutions WHERE region = '杭州市'")
    hz_exact = cursor.fetchone()[0]
    print(f"   - region = '杭州市' 的记录: {hz_exact} 条")
    print("   - 杭州的机构region存储的是: 上城区, 萧山区等区县名")
    
    print("\n4. 搜索'义乌市'会返回:")
    cursor.execute("SELECT COUNT(*) FROM institutions WHERE region = '义乌市'")
    yw_exact = cursor.fetchone()[0]
    print(f"   - region = '义乌市' 的记录: {yw_exact:,} 条")
    print("   - 义乌市本身是县级市，隶属金华市")
    print("   - 但数据库中直接存储为'义乌市'，不是'金华市'")
    
    print("\n" + "=" * 80)
    print("【结论】")
    print("=" * 80)
    print("❌ 我的错误假设:")
    print("   - 假设了 city(市) -> district(区县) 的上下级关系")
    print("   - 假设搜索'杭州市'应该匹配'上城区'等")
    print("   - 假设搜索'金华市'应该匹配'义乌市'等")
    
    print("\n✅ 实际情况:")
    print("   - region字段存储的就是最具体的行政区划名称")
    print("   - '上城区'就是'上城区'，不会存储为'杭州市'")
    print("   - '义乌市'就是'义乌市'，不会存储为'金华市'")
    print("   - 数据库中没有上级地区信息")
    
    print("\n🤔 需要重新思考解决方案...")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    try:
        analyze_region_structure()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
