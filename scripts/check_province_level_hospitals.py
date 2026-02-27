# -*- coding: utf-8 -*-
"""
检查city='省级'的三级医院，并根据实际情况修正city
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

print("=" * 100)
print("检查city='省级'的三级医院")
print("=" * 100)

conn = pymysql.connect(**db_config)
cursor = conn.cursor(pymysql.cursors.DictCursor)

# 查询city='省级'的三级医院
cursor.execute("""
    SELECT id, uscc, name, region, city, level
    FROM const_init_institutions
    WHERE level = '三级' AND city = '省级'
    ORDER BY name
""")

province_level = cursor.fetchall()

print(f"\n找到 {len(province_level)} 家city='省级'的三级医院:")
print("-" * 100)

# 根据名称关键词推断实际所在城市
city_mapping = {
    '浙江大学': '杭州市',
    '浙江医学院': '杭州市',
    '浙江医院': '杭州市',
    '浙江省': '杭州市',  # 省级单位一般在省会
    '浙江中医药大学': '杭州市',
    '温州医科大学': '温州市',
    '温州': '温州市',
}

update_list = []

for hospital in province_level:
    name = hospital['name']
    region = hospital['region']
    
    # 推断城市
    inferred_city = None
    for keyword, city in city_mapping.items():
        if keyword in name:
            inferred_city = city
            break
    
    if not inferred_city:
        inferred_city = '杭州市'  # 默认省会
    
    update_list.append({
        'id': hospital['id'],
        'name': name,
        'current_city': 'province',
        'region': region,
        'inferred_city': inferred_city
    })
    
    print(f"  {name[:60]}")
    print(f"     region: {region or '[NULL]'}")
    print(f"     推断city: {inferred_city}")
    print()

cursor.close()
conn.close()

# 输出建议
print("=" * 100)
print(f"共 {len(update_list)} 家医院需要修正city")
print("=" * 100)

杭州_count = len([h for h in update_list if h['inferred_city'] == '杭州市'])
温州_count = len([h for h in update_list if h['inferred_city'] == '温州市'])

print(f"\n城市分布:")
print(f"  杭州市: {杭州_count} 家")
print(f"  温州市: {温州_count} 家")

print("\n" + "=" * 100)
