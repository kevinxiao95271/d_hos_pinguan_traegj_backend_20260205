# -*- coding: utf-8 -*-
"""
快速添加city字段 - 使用批量UPDATE CASE
"""
import pymysql

# 数据库配置
DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

# 区县到市的映射
DISTRICT_TO_CITY = {
    # 杭州市
    '上城区': '杭州市', '下城区': '杭州市', '江干区': '杭州市', '拱墅区': '杭州市',
    '西湖区': '杭州市', '滨江区': '杭州市', '萧山区': '杭州市', '余杭区': '杭州市',
    '富阳区': '杭州市', '临安区': '杭州市', '桐庐县': '杭州市', '淳安县': '杭州市',
    '建德市': '杭州市',
    
    # 宁波市
    '海曙区': '宁波市', '江北区': '宁波市', '北仑区': '宁波市', '镇海区': '宁波市',
    '鄞州区': '宁波市', '奉化区': '宁波市', '象山县': '宁波市', '宁海县': '宁波市',
    '余姚市': '宁波市', '慈溪市': '宁波市',
    
    # 温州市
    '鹿城区': '温州市', '龙湾区': '温州市', '瓯海区': '温州市', '洞头区': '温州市',
    '永嘉县': '温州市', '平阳县': '温州市', '苍南县': '温州市', '文成县': '温州市',
    '泰顺县': '温州市', '瑞安市': '温州市', '乐清市': '温州市',
    
    # 嘉兴市
    '南湖区': '嘉兴市', '秀洲区': '嘉兴市', '嘉善县': '嘉兴市', '海盐县': '嘉兴市',
    '海宁市': '嘉兴市', '平湖市': '嘉兴市', '桐乡市': '嘉兴市',
    
    # 湖州市
    '吴兴区': '湖州市', '南浔区': '湖州市', '德清县': '湖州市', '长兴县': '湖州市',
    '安吉县': '湖州市',
    
    # 绍兴市
    '越城区': '绍兴市', '柯桥区': '绍兴市', '上虞区': '绍兴市', '新昌县': '绍兴市',
    '诸暨市': '绍兴市', '嵊州市': '绍兴市',
    
    # 金华市
    '婺城区': '金华市', '金东区': '金华市', '武义县': '金华市', '浦江县': '金华市',
    '磐安县': '金华市', '兰溪市': '金华市', '义乌市': '金华市', '东阳市': '金华市',
    '永康市': '金华市',
    
    # 衢州市
    '柯城区': '衢州市', '衢江区': '衢州市', '常山县': '衢州市', '开化县': '衢州市',
    '龙游县': '衢州市', '江山市': '衢州市',
    
    # 舟山市
    '定海区': '舟山市', '普陀区': '舟山市', '岱山县': '舟山市', '嵊泗县': '舟山市',
    
    # 台州市
    '椒江区': '台州市', '黄岩区': '台州市', '路桥区': '台州市', '三门县': '台州市',
    '天台县': '台州市', '仙居县': '台州市', '温岭市': '台州市', '临海市': '台州市',
    '玉环市': '台州市',
    
    # 丽水市
    '莲都区': '丽水市', '青田县': '丽水市', '缙云县': '丽水市', '遂昌县': '丽水市',
    '松阳县': '丽水市', '云和县': '丽水市', '庆元县': '丽水市', '景宁畲族自治县': '丽水市',
    '龙泉市': '丽水市',
}

def add_city_field_fast():
    """快速添加city字段"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        print("=" * 80)
        print("快速添加city字段")
        print("=" * 80)
        
        # 1. 添加字段
        print("\n[1/4] 添加city字段...")
        try:
            cursor.execute("""
                ALTER TABLE institutions 
                ADD COLUMN city VARCHAR(50) 
                COMMENT '所属城市（市级）' 
                AFTER region
            """)
            conn.commit()
            print("      OK city字段添加成功")
        except Exception as e:
            if 'Duplicate' in str(e):
                print("      INFO city字段已存在")
            else:
                raise
        
        # 2. 批量更新区县 -> 市
        print("\n[2/4] 批量更新区县数据...")
        for district, city in DISTRICT_TO_CITY.items():
            cursor.execute(
                "UPDATE institutions SET city = %s WHERE region = %s",
                (city, district)
            )
        conn.commit()
        print(f"      OK 更新了 {len(DISTRICT_TO_CITY)} 个区县的映射")
        
        # 3. 对于已经是市级的region，直接复制
        print("\n[3/4] 处理市级数据...")
        cursor.execute("""
            UPDATE institutions 
            SET city = region 
            WHERE city IS NULL 
            AND region LIKE '%市' 
            AND region NOT IN (
                SELECT DISTINCT city FROM (SELECT city FROM institutions WHERE city IS NOT NULL) t
            )
        """)
        conn.commit()
        print("      OK 市级数据处理完成")
        
        # 4. 统计结果
        print("\n[4/4] 统计city分布（TOP 20）...")
        cursor.execute("""
            SELECT city, COUNT(*) as cnt 
            FROM institutions 
            WHERE city IS NOT NULL 
            GROUP BY city 
            ORDER BY cnt DESC 
            LIMIT 20
        """)
        results = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) FROM institutions")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM institutions WHERE city IS NOT NULL")
        total_with_city = cursor.fetchone()[0]
        
        print(f"\n排名  城市          机构数    占比")
        print("-" * 60)
        for i, (city, cnt) in enumerate(results, 1):
            pct = (cnt / total) * 100
            print(f"{i:2d}.  {city:12s} {cnt:6,} 家  {pct:5.2f}%")
        
        print("-" * 60)
        print(f"     {'有city数据':12s} {total_with_city:6,} 家  {(total_with_city/total)*100:5.2f}%")
        print(f"     {'无city数据':12s} {total - total_with_city:6,} 家  {((total-total_with_city)/total)*100:5.2f}%")
        
        # 5. 添加索引
        print("\n[5/5] 添加city字段索引...")
        try:
            cursor.execute("CREATE INDEX idx_city ON institutions(city)")
            conn.commit()
            print("      OK 索引创建成功")
        except Exception as e:
            if 'Duplicate' in str(e):
                print("      INFO 索引已存在")
            else:
                print(f"      WARN: {e}")
        
        # 6. 验证杭州
        print("\n【验证：杭州市】")
        cursor.execute("""
            SELECT region, COUNT(*) as cnt 
            FROM institutions 
            WHERE city = '杭州市' 
            GROUP BY region 
            ORDER BY cnt DESC
        """)
        hangzhou = cursor.fetchall()
        hangzhou_total = sum(r[1] for r in hangzhou)
        
        for region, cnt in hangzhou[:10]:
            print(f"  {region:10s} {cnt:6,} 家")
        if len(hangzhou) > 10:
            print(f"  ... 还有 {len(hangzhou)-10} 个区县")
        print(f"  {'杭州市合计':10s} {hangzhou_total:6,} 家")
        
        print("\n" + "=" * 80)
        print("OK city字段添加完成！")
        print("=" * 80)
        
    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    add_city_field_fast()
