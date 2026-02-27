# -*- coding: utf-8 -*-
"""
检查知名医院的city字段情况
"""
import pymysql
import sys

sys.stdout = __import__('io').TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

hospitals = [
    "浙江大学医学院附属第二医院",
    "邵逸夫",
    "浙江医院",
    "浙江省人民医院",
    "浙江省肿瘤医院",
    "李惠利"
]

print("=" * 100)
print("知名医院的city/region字段检查")
print("=" * 100)

conn = pymysql.connect(**db_config)
cursor = conn.cursor(pymysql.cursors.DictCursor)

for keyword in hospitals:
    cursor.execute("""
        SELECT name, region, city, level
        FROM const_init_institutions
        WHERE name LIKE %s
        LIMIT 3
    """, (f"%{keyword}%",))
    
    results = cursor.fetchall()
    print(f"\n[{keyword}] 找到 {len(results)} 条:")
    print("-" * 100)
    
    if results:
        for r in results:
            name = r['name'][:50]
            region = r['region'] or '[NULL]'
            city = r['city'] or '[NULL]'
            level = r['level'] or '[NULL]'
            print(f"  {name:<52} | region: {region:<12} | city: {city:<12} | level: {level}")
    else:
        print("  未找到")

cursor.close()
conn.close()

print("\n" + "=" * 100)
