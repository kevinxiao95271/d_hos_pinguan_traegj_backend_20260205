# -*- coding: utf-8 -*-
"""
基于真实数据生成完整的地区映射关系
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

# 浙江省行政区划（标准的地级市及其下辖区县）
# 数据来源：中华人民共和国行政区划
ZHEJIANG_ADMIN_DIVISIONS = {
    "杭州市": {
        "districts": ["上城区", "拱墅区", "西湖区", "滨江区", "萧山区", "余杭区", "临平区", "钱塘区", "富阳区", "临安区"],
        "counties": ["桐庐县", "淳安县"],
        "county_cities": ["建德市"]
    },
    "宁波市": {
        "districts": ["海曙区", "江北区", "北仑区", "镇海区", "鄞州区", "奉化区"],
        "counties": ["象山县", "宁海县"],
        "county_cities": ["余姚市", "慈溪市"]
    },
    "温州市": {
        "districts": ["鹿城区", "龙湾区", "瓯海区", "洞头区"],
        "counties": ["永嘉县", "平阳县", "苍南县", "文成县", "泰顺县"],
        "county_cities": ["瑞安市", "乐清市", "龙港市"]
    },
    "嘉兴市": {
        "districts": ["南湖区", "秀洲区"],
        "counties": ["嘉善县", "海盐县"],
        "county_cities": ["海宁市", "平湖市", "桐乡市"]
    },
    "湖州市": {
        "districts": ["吴兴区", "南浔区"],
        "counties": ["德清县", "长兴县", "安吉县"],
        "county_cities": []
    },
    "绍兴市": {
        "districts": ["越城区", "柯桥区", "上虞区"],
        "counties": ["新昌县"],
        "county_cities": ["诸暨市", "嵊州市"]
    },
    "金华市": {
        "districts": ["婺城区", "金东区"],
        "counties": ["武义县", "浦江县", "磐安县"],
        "county_cities": ["兰溪市", "义乌市", "东阳市", "永康市"]
    },
    "衢州市": {
        "districts": ["柯城区", "衢江区"],
        "counties": ["常山县", "开化县", "龙游县"],
        "county_cities": ["江山市"]
    },
    "舟山市": {
        "districts": ["定海区", "普陀区"],
        "counties": ["岱山县", "嵊泗县"],
        "county_cities": []
    },
    "台州市": {
        "districts": ["椒江区", "黄岩区", "路桥区"],
        "counties": ["三门县", "天台县", "仙居县"],
        "county_cities": ["温岭市", "临海市", "玉环市"]
    },
    "丽水市": {
        "districts": ["莲都区"],
        "counties": ["青田县", "缙云县", "遂昌县", "松阳县", "云和县", "庆元县", "景宁畲族自治县"],
        "county_cities": ["龙泉市"]
    }
}

def generate_mapping():
    """生成完整映射"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("生成完整的地区映射关系")
    print("=" * 80)
    
    # 获取数据库中实际存在的所有region
    cursor.execute("""
        SELECT region, COUNT(*) as cnt 
        FROM institutions 
        WHERE region IS NOT NULL AND region != ''
        GROUP BY region
    """)
    actual_data = {row[0]: row[1] for row in cursor.fetchall()}
    
    print(f"\n数据库中实际有 {len(actual_data)} 个不同的region值")
    print(f"共 {sum(actual_data.values()):,} 家机构\n")
    
    # 生成Java代码
    print("=" * 80)
    print("建议的完整映射（Java代码）")
    print("=" * 80)
    print("\nprivate static final Map<String, List<String>> CITY_TO_DISTRICTS = new HashMap<>();\n")
    print("static {")
    
    total_mapped = 0
    total_count = 0
    
    for city, divisions in sorted(ZHEJIANG_ADMIN_DIVISIONS.items()):
        # 合并所有下辖区划
        all_subdivisions = []
        all_subdivisions.extend(divisions["districts"])
        all_subdivisions.extend(divisions["counties"])
        all_subdivisions.extend(divisions["county_cities"])
        
        # 检查哪些在数据库中实际存在
        existing = []
        missing = []
        city_total = 0
        
        for sub in all_subdivisions:
            if sub in actual_data:
                existing.append(sub)
                city_total += actual_data[sub]
            else:
                missing.append(sub)
        
        if existing:
            total_mapped += len(existing)
            total_count += city_total
            
            print(f"    // {city} - {len(existing)}个区县, {city_total:,}家机构")
            print(f"    CITY_TO_DISTRICTS.put(\"{city}\", Arrays.asList(")
            for i, sub in enumerate(existing):
                comma = "," if i < len(existing) - 1 else ""
                print(f"        \"{sub}\"{comma}")
            print("    ));")
            print()
            
            if missing:
                print(f"    // 注意: {city}以下区划在数据库中不存在: {', '.join(missing)}")
                print()
    
    print("}")
    
    print("\n" + "=" * 80)
    print("映射统计")
    print("=" * 80)
    print(f"已映射区县数: {total_mapped} 个")
    print(f"已映射机构数: {total_count:,} 家 ({total_count/sum(actual_data.values())*100:.1f}%)")
    
    # 检查未映射的
    all_mapped_regions = set()
    for divisions in ZHEJIANG_ADMIN_DIVISIONS.values():
        all_mapped_regions.update(divisions["districts"])
        all_mapped_regions.update(divisions["counties"])
        all_mapped_regions.update(divisions["county_cities"])
    
    unmapped = []
    for region, cnt in actual_data.items():
        if region.endswith(('区', '县', '市')) and region not in all_mapped_regions:
            unmapped.append((region, cnt))
    
    if unmapped:
        unmapped.sort(key=lambda x: x[1], reverse=True)
        unmapped_count = sum(cnt for _, cnt in unmapped)
        print(f"\n未映射地区: {len(unmapped)} 个, {unmapped_count:,} 家机构 ({unmapped_count/sum(actual_data.values())*100:.1f}%)")
        print("\nTOP 20 未映射地区:")
        for region, cnt in unmapped[:20]:
            print(f"  {region:20s} {cnt:6,} 家")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    try:
        generate_mapping()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
