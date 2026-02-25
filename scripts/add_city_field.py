# -*- coding: utf-8 -*-
"""
为institutions表增加city字段（市级）
保留原有region字段（区县级），支持双层级查询
"""
import pymysql
import re

# 数据库配置
DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

# 区县到市的映射（浙江省主要城市）
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

def infer_city(region):
    """
    根据region推断city
    """
    if not region or region == 'None':
        return None
    
    # 1. 如果是区县，直接映射
    if region in DISTRICT_TO_CITY:
        return DISTRICT_TO_CITY[region]
    
    # 2. 如果已经是市级（如"杭州市"、"义乌市"），直接返回
    if region.endswith('市'):
        return region
    
    # 3. 如果是省级（如"浙江省"），返回None
    if region.endswith('省'):
        return None
    
    # 4. 其他情况，尝试从名称推断（如"浙江-杭州"）
    if '-' in region:
        parts = region.split('-')
        if len(parts) >= 2:
            city_part = parts[1].strip()
            if city_part.endswith('市'):
                return city_part
            else:
                return city_part + '市'
    
    # 5. 无法推断，返回None
    return None

def add_city_field():
    """添加city字段并填充数据"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        print("=" * 80)
        print("为institutions表添加city字段（市级）")
        print("=" * 80)
        
        # 1. 检查city字段是否存在
        print("\n[1/4] 检查city字段...")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'institutions' 
            AND COLUMN_NAME = 'city'
        """)
        exists = cursor.fetchone()[0]
        
        if exists:
            print("      WARN city字段已存在，将更新数据")
        else:
            # 2. 添加city字段
            print("\n[2/4] 添加city字段...")
            cursor.execute("""
                ALTER TABLE institutions 
                ADD COLUMN city VARCHAR(50) 
                COMMENT '所属城市（市级）' 
                AFTER region
            """)
            conn.commit()
            print("      OK city字段添加成功")
        
        # 3. 获取所有机构的region
        print("\n[3/4] 分析region数据并推断city...")
        cursor.execute("SELECT id, region FROM institutions")
        institutions = cursor.fetchall()
        
        city_stats = {}
        update_count = 0
        null_count = 0
        
        # 批量更新
        for inst_id, region in institutions:
            city = infer_city(region)
            
            if city:
                city_stats[city] = city_stats.get(city, 0) + 1
                cursor.execute(
                    "UPDATE institutions SET city = %s WHERE id = %s",
                    (city, inst_id)
                )
                update_count += 1
            else:
                null_count += 1
        
        conn.commit()
        print(f"      OK 更新成功: {update_count:,} 条")
        print(f"      WARN 无法推断city: {null_count:,} 条")
        
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
        
        total_with_city = sum(r[1] for r in results)
        cursor.execute("SELECT COUNT(*) FROM institutions")
        total = cursor.fetchone()[0]
        
        print(f"\n排名  城市          机构数    占比")
        print("-" * 60)
        for i, (city, cnt) in enumerate(results, 1):
            pct = (cnt / total) * 100
            print(f"{i:2d}.  {city:12s} {cnt:6,} 家  {pct:5.2f}%")
        
        print("-" * 60)
        print(f"     {'有city数据':12s} {total_with_city:6,} 家  {(total_with_city/total)*100:5.2f}%")
        print(f"     {'无city数据':12s} {null_count:6,} 家  {(null_count/total)*100:5.2f}%")
        print(f"     {'总计':12s} {total:6,} 家  100.00%")
        
        # 5. 验证杭州数据
        print("\n【验证：杭州市数据】")
        cursor.execute("""
            SELECT region, COUNT(*) as cnt 
            FROM institutions 
            WHERE city = '杭州市' 
            GROUP BY region 
            ORDER BY cnt DESC
        """)
        hangzhou_data = cursor.fetchall()
        hangzhou_total = sum(r[1] for r in hangzhou_data)
        
        print(f"杭州市各区县分布:")
        for region, cnt in hangzhou_data:
            pct = (cnt / hangzhou_total) * 100
            print(f"  {region:10s} {cnt:6,} 家 ({pct:5.2f}%)")
        print(f"  {'合计':10s} {hangzhou_total:6,} 家")
        
        # 6. 添加索引
        print("\n[5/5] 添加city字段索引...")
        try:
            cursor.execute("CREATE INDEX idx_city ON institutions(city)")
            conn.commit()
            print("      OK 索引创建成功")
        except Exception as e:
            if 'Duplicate' in str(e) or 'already exists' in str(e):
                print("      INFO 索引已存在")
            else:
                print(f"      WARN 索引创建失败: {e}")
        
        print("\n" + "=" * 80)
        print("city字段添加完成！")
        print("=" * 80)
        print("\n现在可以：")
        print("1. 按市查询：WHERE city = '杭州市'")
        print("2. 按区县查询：WHERE region = '上城区'")
        print("3. 按市和区县联合查询：WHERE city = '杭州市' AND region = '上城区'")
        
    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    add_city_field()
