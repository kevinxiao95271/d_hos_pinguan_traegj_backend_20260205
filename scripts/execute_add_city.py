# -*- coding: utf-8 -*-
"""
执行添加city字段的SQL
"""
import pymysql
import time

DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

def execute_add_city():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        print("=" * 80)
        print("添加city字段")
        print("=" * 80)
        
        # 1. 添加字段
        print("\n[1/15] 添加city字段...")
        try:
            cursor.execute("""
                ALTER TABLE institutions 
                ADD COLUMN city VARCHAR(50) 
                COMMENT '所属城市（市级）' 
                AFTER region
            """)
            conn.commit()
            print("        OK")
        except Exception as e:
            if 'Duplicate' in str(e):
                print("        INFO 已存在")
            else:
                print(f"        ERROR: {e}")
        
        time.sleep(1)
        
        # 2-13. 更新各市数据
        updates = [
            ('杭州市', ['上城区', '下城区', '江干区', '拱墅区', '西湖区', '滨江区', '萧山区', '余杭区', '富阳区', '临安区', '桐庐县', '淳安县', '建德市']),
            ('宁波市', ['海曙区', '江北区', '北仑区', '镇海区', '鄞州区', '奉化区', '象山县', '宁海县', '余姚市', '慈溪市']),
            ('温州市', ['鹿城区', '龙湾区', '瓯海区', '洞头区', '永嘉县', '平阳县', '苍南县', '文成县', '泰顺县', '瑞安市', '乐清市']),
            ('嘉兴市', ['南湖区', '秀洲区', '嘉善县', '海盐县', '海宁市', '平湖市', '桐乡市']),
            ('湖州市', ['吴兴区', '南浔区', '德清县', '长兴县', '安吉县']),
            ('绍兴市', ['越城区', '柯桥区', '上虞区', '新昌县', '诸暨市', '嵊州市']),
            ('金华市', ['婺城区', '金东区', '武义县', '浦江县', '磐安县', '兰溪市', '义乌市', '东阳市', '永康市']),
            ('衢州市', ['柯城区', '衢江区', '常山县', '开化县', '龙游县', '江山市']),
            ('舟山市', ['定海区', '普陀区', '岱山县', '嵊泗县']),
            ('台州市', ['椒江区', '黄岩区', '路桥区', '三门县', '天台县', '仙居县', '温岭市', '临海市', '玉环市']),
            ('丽水市', ['莲都区', '青田县', '缙云县', '遂昌县', '松阳县', '云和县', '庆元县', '景宁畲族自治县', '龙泉市']),
        ]
        
        for i, (city, districts) in enumerate(updates, 2):
            print(f"[{i}/15] 更新{city}...")
            placeholders = ', '.join(['%s'] * len(districts))
            sql = f"UPDATE institutions SET city = %s WHERE region IN ({placeholders})"
            cursor.execute(sql, [city] + districts)
            affected = cursor.rowcount
            conn.commit()
            print(f"        OK {affected} 条")
            time.sleep(0.5)
        
        # 13. 市级直接复制
        print("[13/15] 处理市级数据...")
        cursor.execute("UPDATE institutions SET city = region WHERE city IS NULL AND region LIKE '%市'")
        affected = cursor.rowcount
        conn.commit()
        print(f"         OK {affected} 条")
        
        # 14. 添加索引
        print("[14/15] 添加索引...")
        try:
            cursor.execute("CREATE INDEX idx_city ON institutions(city)")
            conn.commit()
            print("         OK")
        except Exception as e:
            if 'Duplicate' in str(e):
                print("         INFO 已存在")
            else:
                print(f"         WARN: {e}")
        
        # 15. 统计
        print("[15/15] 统计结果...")
        cursor.execute("SELECT COUNT(*) FROM institutions")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM institutions WHERE city IS NOT NULL")
        with_city = cursor.fetchone()[0]
        print(f"         总机构: {total:,}")
        print(f"         有city: {with_city:,} ({with_city/total*100:.1f}%)")
        print(f"         无city: {total-with_city:,} ({(total-with_city)/total*100:.1f}%)")
        
        # TOP 10城市
        print("\n【TOP 10城市】")
        cursor.execute("""
            SELECT city, COUNT(*) as cnt 
            FROM institutions 
            WHERE city IS NOT NULL 
            GROUP BY city 
            ORDER BY cnt DESC 
            LIMIT 10
        """)
        for i, (city, cnt) in enumerate(cursor.fetchall(), 1):
            pct = cnt / total * 100
            print(f"{i:2d}. {city:10s} {cnt:6,} 家 ({pct:5.2f}%)")
        
        # 杭州市验证
        print("\n【杭州市验证】")
        cursor.execute("""
            SELECT COUNT(*) FROM institutions WHERE city = '杭州市'
        """)
        hangzhou_count = cursor.fetchone()[0]
        print(f"杭州市总计: {hangzhou_count:,} 家 ({hangzhou_count/total*100:.2f}%)")
        
        print("\n" + "=" * 80)
        print("OK 完成！")
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
    execute_add_city()
