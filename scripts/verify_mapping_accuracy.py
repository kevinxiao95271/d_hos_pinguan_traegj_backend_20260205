# -*- coding: utf-8 -*-
"""
验证我的映射关系是否准确
"""
import pymysql

DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

# 我定义的映射关系
MY_MAPPING = {
    "杭州市": ["上城区", "下城区", "江干区", "拱墅区", "西湖区", "滨江区",
               "萧山区", "余杭区", "富阳区", "临安区", "桐庐县", "淳安县", "建德市"],
    "宁波市": ["海曙区", "江北区", "北仑区", "镇海区", "鄞州区", "奉化区",
               "象山县", "宁海县", "余姚市", "慈溪市"],
    "金华市": ["婺城区", "金东区", "武义县", "浦江县", "磐安县", "兰溪市",
               "义乌市", "东阳市", "永康市"],
}

def verify_mapping():
    """验证映射准确性"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("验证映射关系准确性")
    print("=" * 80)
    
    # 1. 获取数据库中所有实际的region值
    cursor.execute("""
        SELECT DISTINCT region 
        FROM institutions 
        WHERE region IS NOT NULL AND region != ''
        ORDER BY region
    """)
    actual_regions = set(row[0] for row in cursor.fetchall())
    
    print(f"\n数据库中实际有 {len(actual_regions)} 个不同的region值\n")
    
    # 2. 验证每个城市的映射
    for city, districts in MY_MAPPING.items():
        print(f"\n【验证 {city}】")
        print("-" * 60)
        
        # 检查映射中的每个区县是否真实存在
        found = []
        not_found = []
        
        for district in districts:
            if district in actual_regions:
                cursor.execute("SELECT COUNT(*) FROM institutions WHERE region = %s", (district,))
                cnt = cursor.fetchone()[0]
                found.append((district, cnt))
            else:
                not_found.append(district)
        
        print(f"映射正确: {len(found)}/{len(districts)}")
        for district, cnt in found:
            print(f"  [OK] {district:15s} {cnt:6,} 家 (数据库中存在)")
        
        if not_found:
            print(f"\n映射错误: {len(not_found)} 个")
            for district in not_found:
                print(f"  [ERROR] {district} (数据库中不存在)")
        
        # 统计总数
        total = sum(cnt for _, cnt in found)
        print(f"\n  {city} 总计: {total:,} 家")
    
    # 3. 检查是否有遗漏的区县（数据库中有，但我没映射）
    print("\n" + "=" * 80)
    print("检查是否有遗漏")
    print("=" * 80)
    
    all_mapped = set()
    for districts in MY_MAPPING.values():
        all_mapped.update(districts)
    
    # 只看区、县、县级市后缀的
    unmapped = []
    for region in actual_regions:
        if region.endswith(('区', '县', '市')) and region not in all_mapped:
            cursor.execute("SELECT COUNT(*) FROM institutions WHERE region = %s", (region,))
            cnt = cursor.fetchone()[0]
            unmapped.append((region, cnt))
    
    if unmapped:
        unmapped.sort(key=lambda x: x[1], reverse=True)
        print(f"\n发现 {len(unmapped)} 个未映射的地区（TOP 20）:")
        for region, cnt in unmapped[:20]:
            print(f"  {region:20s} {cnt:6,} 家")
    
    # 4. 验证我的代码是否能正确工作
    print("\n" + "=" * 80)
    print("验证功能是否正确")
    print("=" * 80)
    
    test_cases = [
        ("杭州市", MY_MAPPING.get("杭州市", [])),
        ("宁波市", MY_MAPPING.get("宁波市", [])),
        ("金华市", MY_MAPPING.get("金华市", [])),
    ]
    
    for city, expected_districts in test_cases:
        if not expected_districts:
            continue
        
        # 模拟我的代码查询
        placeholders = ', '.join(['%s'] * len(expected_districts))
        sql = f"SELECT COUNT(*) FROM institutions WHERE region IN ({placeholders})"
        cursor.execute(sql, expected_districts)
        result_count = cursor.fetchone()[0]
        
        print(f"\n搜索'{city}':")
        print(f"  映射到: {len(expected_districts)} 个区县")
        print(f"  查询到: {result_count:,} 家机构")
        
        # 验证是否有数据
        if result_count > 0:
            print(f"  [OK] 功能正常")
        else:
            print(f"  [ERROR] 功能异常（查不到数据）")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    try:
        verify_mapping()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
